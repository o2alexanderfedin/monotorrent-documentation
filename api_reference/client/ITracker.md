# ITracker

**Namespace**: `MonoTorrent.Client`

The `ITracker` interface defines the contract for implementing BitTorrent trackers.

## Overview

Trackers are servers that help BitTorrent peers find each other. The `ITracker` interface enables developers to implement custom tracker types beyond the built-in HTTP, UDP, and DHT trackers. Each implementation handles the specific protocol details while providing a consistent interface to the `TrackerManager`.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `CanAnnounce` | `bool` | Whether the tracker is able to announce |
| `CanScrape` | `bool` | Whether the tracker supports scrape requests |
| `FailureMessage` | `string` | The last failure message, or null if no failure |
| `MinUpdateInterval` | `TimeSpan` | Minimum time between announce requests |
| `Status` | `TrackerState` | The current status of the tracker |
| `UpdateInterval` | `TimeSpan` | Suggested time between announce requests |
| `WarningMessage` | `string` | The last warning message, or null if no warning |
| `Uri` | `Uri` | The URI for this tracker |

## Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `AnnounceAsync(AnnounceParameters parameters)` | `Task<AnnounceResponse>` | Sends an announce request to the tracker |
| `ScrapeAsync(ScrapeParameters parameters)` | `Task<ScrapeResponse>` | Sends a scrape request to the tracker |

## Examples

### Implementing a Custom Tracker

```csharp
public class CustomWebSocketTracker : ITracker
{
    private ClientWebSocket socket;
    private Uri trackerUri;
    private bool isConnected;
    private TaskCompletionSource<AnnounceResponse> announceCompletionSource;
    private TaskCompletionSource<ScrapeResponse> scrapeCompletionSource;
    
    public CustomWebSocketTracker(Uri uri)
    {
        this.trackerUri = uri;
        socket = new ClientWebSocket();
        Status = TrackerState.NotContacted;
    }
    
    // ITracker properties
    public bool CanAnnounce => true;
    public bool CanScrape => true;
    public string FailureMessage { get; private set; }
    public TimeSpan MinUpdateInterval { get; private set; } = TimeSpan.FromMinutes(3);
    public TrackerState Status { get; private set; }
    public TimeSpan UpdateInterval { get; private set; } = TimeSpan.FromMinutes(5);
    public string WarningMessage { get; private set; }
    public Uri Uri => trackerUri;
    
    private async Task EnsureConnectedAsync()
    {
        if (!isConnected)
        {
            try
            {
                await socket.ConnectAsync(trackerUri, CancellationToken.None);
                isConnected = true;
                Status = TrackerState.Ok;
                
                // Start a background task to receive messages
                _ = Task.Run(ReceiveMessagesAsync);
            }
            catch (Exception ex)
            {
                FailureMessage = ex.Message;
                Status = TrackerState.Offline;
                throw;
            }
        }
    }
    
    private async Task ReceiveMessagesAsync()
    {
        var buffer = new byte[4096];
        var receiveBuffer = new ArraySegment<byte>(buffer);
        
        try
        {
            while (socket.State == WebSocketState.Open)
            {
                var result = await socket.ReceiveAsync(receiveBuffer, CancellationToken.None);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
                    isConnected = false;
                    Status = TrackerState.NotContacted;
                    break;
                }
                
                // Process the received message based on message type
                string message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                ProcessMessage(message);
            }
        }
        catch (Exception ex)
        {
            FailureMessage = ex.Message;
            Status = TrackerState.Offline;
            isConnected = false;
        }
    }
    
    private void ProcessMessage(string message)
    {
        // Parse the JSON message
        var json = System.Text.Json.JsonDocument.Parse(message).RootElement;
        
        // Check message type
        if (json.TryGetProperty("type", out var typeElement))
        {
            string type = typeElement.GetString();
            
            if (type == "announce_response")
            {
                // Parse announce response
                var response = ParseAnnounceResponse(json);
                announceCompletionSource?.TrySetResult(response);
            }
            else if (type == "scrape_response")
            {
                // Parse scrape response
                var response = ParseScrapeResponse(json);
                scrapeCompletionSource?.TrySetResult(response);
            }
        }
    }
    
    private AnnounceResponse ParseAnnounceResponse(JsonElement json)
    {
        // Extract data from the JSON response
        var response = new AnnounceResponse();
        
        if (json.TryGetProperty("interval", out var intervalElement))
            UpdateInterval = TimeSpan.FromSeconds(intervalElement.GetInt32());
            
        if (json.TryGetProperty("min_interval", out var minIntervalElement))
            MinUpdateInterval = TimeSpan.FromSeconds(minIntervalElement.GetInt32());
            
        if (json.TryGetProperty("peers", out var peersElement) && peersElement.ValueKind == JsonValueKind.Array)
        {
            var peers = new List<Peer>();
            foreach (var peerElement in peersElement.EnumerateArray())
            {
                string ip = peerElement.GetProperty("ip").GetString();
                int port = peerElement.GetProperty("port").GetInt32();
                peers.Add(new Peer(new IPEndPoint(IPAddress.Parse(ip), port)));
            }
            response.Peers = peers;
        }
        
        return response;
    }
    
    private ScrapeResponse ParseScrapeResponse(JsonElement json)
    {
        // Extract data from the JSON response
        var response = new ScrapeResponse();
        
        if (json.TryGetProperty("files", out var filesElement) && filesElement.ValueKind == JsonValueKind.Object)
        {
            foreach (var property in filesElement.EnumerateObject())
            {
                string infoHash = property.Name;
                var fileElement = property.Value;
                
                int complete = fileElement.GetProperty("complete").GetInt32();
                int downloaded = fileElement.GetProperty("downloaded").GetInt32();
                int incomplete = fileElement.GetProperty("incomplete").GetInt32();
                
                response.Add(InfoHash.FromHex(infoHash), new ScrapeInfo(complete, downloaded, incomplete));
            }
        }
        
        return response;
    }
    
    public async Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters)
    {
        try
        {
            await EnsureConnectedAsync();
            
            // Create the announce request message
            var request = new
            {
                type = "announce",
                info_hash = parameters.InfoHash.ToHex(),
                peer_id = System.Text.Encoding.UTF8.GetString(parameters.PeerId),
                port = parameters.Port,
                uploaded = parameters.BytesUploaded,
                downloaded = parameters.BytesDownloaded,
                left = parameters.BytesLeft,
                compact = 1,
                event_type = parameters.ClientEvent.ToString().ToLowerInvariant()
            };
            
            string requestJson = System.Text.Json.JsonSerializer.Serialize(request);
            var buffer = System.Text.Encoding.UTF8.GetBytes(requestJson);
            
            // Set up completion source for the response
            announceCompletionSource = new TaskCompletionSource<AnnounceResponse>();
            
            // Send the request
            await socket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
            
            // Wait for response with timeout
            var response = await announceCompletionSource.Task.TimeoutAfter(TimeSpan.FromSeconds(30));
            Status = TrackerState.Ok;
            return response;
        }
        catch (Exception ex)
        {
            FailureMessage = ex.Message;
            Status = TrackerState.Offline;
            return new AnnounceResponse
            {
                Failure = FailureMessage
            };
        }
    }
    
    public async Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters)
    {
        if (!CanScrape)
            return new ScrapeResponse();
            
        try
        {
            await EnsureConnectedAsync();
            
            // Create the scrape request message
            var request = new
            {
                type = "scrape",
                info_hashes = parameters.InfoHashes.Select(ih => ih.ToHex()).ToList()
            };
            
            string requestJson = System.Text.Json.JsonSerializer.Serialize(request);
            var buffer = System.Text.Encoding.UTF8.GetBytes(requestJson);
            
            // Set up completion source for the response
            scrapeCompletionSource = new TaskCompletionSource<ScrapeResponse>();
            
            // Send the request
            await socket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
            
            // Wait for response with timeout
            var response = await scrapeCompletionSource.Task.TimeoutAfter(TimeSpan.FromSeconds(30));
            Status = TrackerState.Ok;
            return response;
        }
        catch (Exception ex)
        {
            FailureMessage = ex.Message;
            Status = TrackerState.Offline;
            return new ScrapeResponse
            {
                Failure = FailureMessage
            };
        }
    }
}
```

### Using a Custom Tracker

```csharp
// Create a custom tracker
ITracker customTracker = new CustomWebSocketTracker(new Uri("ws://example.tracker.com/announce"));

// Create torrent manager
TorrentManager manager = /* ... */;

// Add the custom tracker to the torrent
manager.TrackerManager.Add(customTracker);

// Start the torrent
await manager.StartAsync();
```

### Implementing a Simple HTTP Tracker

```csharp
public class SimpleHttpTracker : ITracker
{
    private readonly HttpClient client;
    private readonly Uri trackerUri;
    
    public SimpleHttpTracker(Uri uri)
    {
        this.trackerUri = uri;
        this.client = new HttpClient();
        Status = TrackerState.NotContacted;
    }
    
    public bool CanAnnounce => true;
    public bool CanScrape => trackerUri.AbsolutePath.EndsWith("/announce");
    public string FailureMessage { get; private set; }
    public TimeSpan MinUpdateInterval { get; private set; } = TimeSpan.FromMinutes(3);
    public TrackerState Status { get; private set; }
    public TimeSpan UpdateInterval { get; private set; } = TimeSpan.FromMinutes(30);
    public string WarningMessage { get; private set; }
    public Uri Uri => trackerUri;
    
    public async Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters)
    {
        try
        {
            // Construct the announce URL with query parameters
            var uriBuilder = new UriBuilder(trackerUri);
            var query = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            
            // Add required parameters
            query["info_hash"] = Uri.EscapeDataString(parameters.InfoHash.ToHex());
            query["peer_id"] = Uri.EscapeDataString(System.Text.Encoding.UTF8.GetString(parameters.PeerId));
            query["port"] = parameters.Port.ToString();
            query["uploaded"] = parameters.BytesUploaded.ToString();
            query["downloaded"] = parameters.BytesDownloaded.ToString();
            query["left"] = parameters.BytesLeft.ToString();
            query["compact"] = "1";
            query["event"] = parameters.ClientEvent.ToString().ToLowerInvariant();
            
            uriBuilder.Query = query.ToString();
            
            // Send the HTTP request
            var response = await client.GetByteArrayAsync(uriBuilder.Uri);
            
            // Parse the response using BEncode
            var dict = BEncodedValue.Decode<BEncodedDictionary>(response);
            var announceResponse = new AnnounceResponse();
            
            if (dict.TryGetValue("interval", out BEncodedValue value))
                UpdateInterval = TimeSpan.FromSeconds(((BEncodedNumber)value).Number);
                
            if (dict.TryGetValue("min interval", out value))
                MinUpdateInterval = TimeSpan.FromSeconds(((BEncodedNumber)value).Number);
                
            if (dict.TryGetValue("peers", out value))
            {
                if (value is BEncodedString compact)
                {
                    // Parse compact peer format
                    announceResponse.Peers = ParseCompactPeers(compact.TextBytes);
                }
                else if (value is BEncodedList peerList)
                {
                    // Parse dictionary peer format
                    announceResponse.Peers = ParseDictionaryPeers(peerList);
                }
            }
            
            Status = TrackerState.Ok;
            return announceResponse;
        }
        catch (Exception ex)
        {
            FailureMessage = ex.Message;
            Status = TrackerState.Offline;
            return new AnnounceResponse
            {
                Failure = FailureMessage
            };
        }
    }
    
    public async Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters)
    {
        if (!CanScrape)
            return new ScrapeResponse();
            
        try
        {
            // Convert /announce to /scrape
            var scrapeUri = trackerUri.AbsoluteUri.Replace("/announce", "/scrape");
            var uriBuilder = new UriBuilder(scrapeUri);
            var query = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            
            // Add info_hash parameters
            for (int i = 0; i < parameters.InfoHashes.Count; i++)
            {
                query.Add("info_hash", Uri.EscapeDataString(parameters.InfoHashes[i].ToHex()));
            }
            
            uriBuilder.Query = query.ToString();
            
            // Send the HTTP request
            var response = await client.GetByteArrayAsync(uriBuilder.Uri);
            
            // Parse the response using BEncode
            var dict = BEncodedValue.Decode<BEncodedDictionary>(response);
            var scrapeResponse = new ScrapeResponse();
            
            if (dict.TryGetValue("files", out BEncodedValue value) && value is BEncodedDictionary files)
            {
                foreach (KeyValuePair<BEncodedString, BEncodedValue> file in files)
                {
                    var infoHash = InfoHash.FromHex(file.Key.Text);
                    var fileDict = (BEncodedDictionary)file.Value;
                    
                    int complete = fileDict.ContainsKey("complete") ? (int)((BEncodedNumber)fileDict["complete"]).Number : 0;
                    int downloaded = fileDict.ContainsKey("downloaded") ? (int)((BEncodedNumber)fileDict["downloaded"]).Number : 0;
                    int incomplete = fileDict.ContainsKey("incomplete") ? (int)((BEncodedNumber)fileDict["incomplete"]).Number : 0;
                    
                    scrapeResponse.Add(infoHash, new ScrapeInfo(complete, downloaded, incomplete));
                }
            }
            
            Status = TrackerState.Ok;
            return scrapeResponse;
        }
        catch (Exception ex)
        {
            FailureMessage = ex.Message;
            Status = TrackerState.Offline;
            return new ScrapeResponse
            {
                Failure = FailureMessage
            };
        }
    }
    
    private List<Peer> ParseCompactPeers(byte[] compactPeers)
    {
        var peers = new List<Peer>();
        
        // Each peer is 6 bytes: 4 for IP, 2 for port
        for (int i = 0; i < compactPeers.Length; i += 6)
        {
            if (i + 6 > compactPeers.Length)
                break;
                
            var ipBytes = new byte[4];
            Array.Copy(compactPeers, i, ipBytes, 0, 4);
            
            int port = (compactPeers[i + 4] << 8) | compactPeers[i + 5];
            var endpoint = new IPEndPoint(new IPAddress(ipBytes), port);
            
            peers.Add(new Peer(endpoint));
        }
        
        return peers;
    }
    
    private List<Peer> ParseDictionaryPeers(BEncodedList peerList)
    {
        var peers = new List<Peer>();
        
        foreach (BEncodedDictionary dict in peerList)
        {
            string ip = ((BEncodedString)dict["ip"]).Text;
            int port = (int)((BEncodedNumber)dict["port"]).Number;
            
            var endpoint = new IPEndPoint(IPAddress.Parse(ip), port);
            peers.Add(new Peer(endpoint));
        }
        
        return peers;
    }
}
```

## BitTorrent Tracker Protocol

The BitTorrent tracker protocol consists of two main request types:

1. **Announce**:
   - Informs the tracker about a peer's status
   - Requests peers that are also downloading/seeding the torrent
   - Includes information such as bytes downloaded, uploaded, and remaining
   - Specifies events like "started", "stopped", or "completed"

2. **Scrape**:
   - Requests statistics about torrents
   - Returns information such as number of seeders, leechers, and downloads
   - Usually optional and not supported by all trackers

Trackers can use different transport protocols:
- **HTTP**: The original tracker protocol using HTTP GET requests
- **UDP**: A more efficient binary protocol for high-load trackers
- **WebSocket**: Allows real-time communication and updates
- **DHT**: Distributed Hash Table for trackerless operation

## Remarks

- The `ITracker` interface abstracts away the specific tracker protocol
- Built-in implementations include HTTP trackers, UDP trackers, and DHT
- Custom implementations can support private trackers or specialized protocols
- The `TrackerManager` coordinates announces across multiple trackers in tiers
- Tracker status helps determine tracker reliability
- Failure and warning messages provide diagnostic information
- `UpdateInterval` and `MinUpdateInterval` control announce frequency
- All operations are asynchronous to avoid blocking the main thread

## Related

- [TrackerManager](../client/TrackerManager.md)
- [Peer](../client/Peer.md)
- [AnnounceParameters](../client/AnnounceParameters.md)
- [ScrapeParameters](../client/ScrapeParameters.md)
- [InfoHash](../common/InfoHash.md)