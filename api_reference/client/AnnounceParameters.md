# AnnounceParameters

**Namespace**: `MonoTorrent.Client`

The `AnnounceParameters` class contains the parameters needed for making an announce request to a tracker.

## Overview

When a BitTorrent client needs to communicate with a tracker, it sends announce requests to report its status and get a list of peers. The `AnnounceParameters` class encapsulates all the data needed for these requests, including the torrent's InfoHash, client port, download status, and the current announce event.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `BytesDownloaded` | `long` | Total bytes downloaded for the torrent |
| `BytesLeft` | `long` | Bytes remaining to be downloaded |
| `BytesUploaded` | `long` | Total bytes uploaded for the torrent |
| `ClientEvent` | `TorrentEvent` | The event triggering this announce (started, stopped, completed, etc.) |
| `InfoHash` | `InfoHash` | The unique identifier for the torrent |
| `PeerId` | `byte[]` | The client's peer ID (20-byte identifier) |
| `Port` | `int` | The port the client is listening on for incoming connections |
| `RequiredPeers` | `int` | The number of peers the client would like to receive |
| `SupportsEncryption` | `bool` | Whether the client supports encrypted connections |
| `External` | `IPEndPoint` | Optional external endpoint the client is listening on |

## Methods

### Constructors

```csharp
public AnnounceParameters()
```
Creates a new `AnnounceParameters` instance with default values.

## Examples

### Creating Basic Announce Parameters

```csharp
// Create announce parameters for a tracker request
AnnounceParameters parameters = new AnnounceParameters
{
    // Set the torrent identifier
    InfoHash = torrent.InfoHash,
    
    // Set client's listening port
    Port = 51515,
    
    // Set client's peer ID (usually provided by ClientEngine)
    PeerId = Encoding.ASCII.GetBytes("-MT0001-123456789012"),
    
    // Set download statistics
    BytesDownloaded = 1024000,
    BytesUploaded = 512000,
    BytesLeft = 2048000,
    
    // Set the announce event (typically 'started' for first announce)
    ClientEvent = TorrentEvent.Started,
    
    // Set encryption support
    SupportsEncryption = true,
    
    // Request 50 peers
    RequiredPeers = 50
};

// Use these parameters with a tracker
ITracker tracker = /* ... */;
AnnounceResponse response = await tracker.AnnounceAsync(parameters);
```

### Implementing a Manual Tracker Announce

```csharp
// Example of how to manually trigger an announce with custom parameters
public async Task ManualAnnounceAsync(TorrentManager manager, TorrentEvent eventType)
{
    // Create announce parameters based on torrent state
    AnnounceParameters parameters = new AnnounceParameters
    {
        InfoHash = manager.InfoHash,
        PeerId = manager.Engine.PeerId,
        Port = manager.Engine.Settings.ListenPort,
        BytesDownloaded = manager.Monitor.DataBytesDownloaded,
        BytesUploaded = manager.Monitor.DataBytesUploaded,
        BytesLeft = manager.Torrent.Size - manager.Monitor.DataBytesDownloaded,
        ClientEvent = eventType,
        SupportsEncryption = true,
        RequiredPeers = 50
    };
    
    // Get the tracker manager for this torrent
    TrackerManager trackerManager = manager.TrackerManager;
    
    try
    {
        // Announce to the primary tracker
        await trackerManager.AnnounceAsync(parameters, false);
        Console.WriteLine("Announce successful");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Announce failed: {ex.Message}");
    }
}
```

### Customizing Announce Parameters for Different Scenarios

```csharp
// Create a utility class for generating announce parameters in different scenarios
public class AnnounceParametersFactory
{
    private readonly ClientEngine engine;
    
    public AnnounceParametersFactory(ClientEngine engine)
    {
        this.engine = engine;
    }
    
    // Parameters for starting a torrent
    public AnnounceParameters CreateStartParameters(TorrentManager manager)
    {
        return CreateBaseParameters(manager, TorrentEvent.Started);
    }
    
    // Parameters for stopping a torrent
    public AnnounceParameters CreateStopParameters(TorrentManager manager)
    {
        return CreateBaseParameters(manager, TorrentEvent.Stopped);
    }
    
    // Parameters for completing a torrent
    public AnnounceParameters CreateCompletedParameters(TorrentManager manager)
    {
        return CreateBaseParameters(manager, TorrentEvent.Completed);
    }
    
    // Parameters for a regular update announce
    public AnnounceParameters CreateUpdateParameters(TorrentManager manager)
    {
        return CreateBaseParameters(manager, TorrentEvent.None);
    }
    
    // Common parameter creation logic
    private AnnounceParameters CreateBaseParameters(TorrentManager manager, TorrentEvent eventType)
    {
        // Determine bytes left based on download progress
        long bytesLeft = manager.HasMetadata 
            ? manager.Torrent.Size - manager.Monitor.DataBytesDownloaded
            : 0; // For magnet links without metadata
            
        return new AnnounceParameters
        {
            InfoHash = manager.InfoHash,
            PeerId = engine.PeerId,
            Port = engine.Settings.ListenPort,
            BytesDownloaded = manager.Monitor.DataBytesDownloaded,
            BytesUploaded = manager.Monitor.DataBytesUploaded,
            BytesLeft = bytesLeft,
            ClientEvent = eventType,
            SupportsEncryption = engine.Settings.AllowedEncryption != EncryptionTypes.None,
            RequiredPeers = manager.Settings.MaxConnections,
            External = engine.ExternalAddress != null 
                ? new IPEndPoint(engine.ExternalAddress, engine.Settings.ListenPort)
                : null
        };
    }
    
    // Special parameters for scrape requests
    public ScrapeParameters CreateScrapeParameters(TorrentManager manager)
    {
        return new ScrapeParameters(manager.InfoHash);
    }
}
```

### Implementing a Tracker Protocol Tester

```csharp
// A utility class to test tracker compatibility with different announce parameters
public class TrackerCompatibilityTester
{
    private readonly ITracker tracker;
    private readonly InfoHash infoHash;
    private readonly byte[] peerId;
    private readonly int port;
    
    public TrackerCompatibilityTester(ITracker tracker, InfoHash infoHash, byte[] peerId, int port)
    {
        this.tracker = tracker;
        this.infoHash = infoHash;
        this.peerId = peerId;
        this.port = port;
    }
    
    // Test compatibility with all announce events
    public async Task TestAllEventTypes()
    {
        await TestAnnounce(TorrentEvent.Started, "Started event");
        await TestAnnounce(TorrentEvent.None, "Regular announce");
        await TestAnnounce(TorrentEvent.Completed, "Completed event");
        await TestAnnounce(TorrentEvent.Stopped, "Stopped event");
    }
    
    // Test compatibility with various BytesLeft values
    public async Task TestProgressValues()
    {
        // Test with download not started (100% left)
        await TestAnnounce(TorrentEvent.None, "Download not started", 
            1000000, 0, 1000000);
            
        // Test with download in progress (50% left)
        await TestAnnounce(TorrentEvent.None, "Download in progress", 
            500000, 100000, 500000);
            
        // Test with download completed (0% left)
        await TestAnnounce(TorrentEvent.None, "Download completed", 
            1000000, 200000, 0);
    }
    
    private async Task TestAnnounce(TorrentEvent eventType, string description,
        long downloaded = 0, long uploaded = 0, long left = 1000000)
    {
        AnnounceParameters parameters = new AnnounceParameters
        {
            InfoHash = infoHash,
            PeerId = peerId,
            Port = port,
            BytesDownloaded = downloaded,
            BytesUploaded = uploaded,
            BytesLeft = left,
            ClientEvent = eventType,
            SupportsEncryption = true,
            RequiredPeers = 50
        };
        
        Console.WriteLine($"Testing {description}...");
        
        try
        {
            AnnounceResponse response = await tracker.AnnounceAsync(parameters);
            
            Console.WriteLine($"Success! Received {response.Peers?.Count ?? 0} peers");
            Console.WriteLine($"Interval: {response.Interval}");
            
            if (!string.IsNullOrEmpty(response.WarningMessage))
                Console.WriteLine($"Warning: {response.WarningMessage}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed: {ex.Message}");
        }
        
        Console.WriteLine();
    }
}
```

## Tracker Protocol Details

The BitTorrent tracker protocol uses the following parameters in announce requests:

1. **info_hash**: The 20-byte SHA-1 hash of the 'info' section of the torrent file (encoded as the `InfoHash` property)
2. **peer_id**: A 20-byte string used as a unique identifier for the client (encoded as the `PeerId` property)
3. **port**: The port the client is listening on (encoded as the `Port` property)
4. **uploaded**: The total number of bytes uploaded (encoded as the `BytesUploaded` property)
5. **downloaded**: The total number of bytes downloaded (encoded as the `BytesDownloaded` property)
6. **left**: The number of bytes left to download (encoded as the `BytesLeft` property)
7. **event**: The event that triggered this announce (encoded as the `ClientEvent` property):
   - "started": When a download first begins
   - "completed": When the download is complete
   - "stopped": When a download is stopped
   - (blank): For regular periodic announces

These parameters are typically sent in an HTTP GET request for HTTP trackers, or encoded in a binary format for UDP trackers. MonoTorrent handles the protocol-specific details internally based on the tracker type.

## Remarks

- The `AnnounceParameters` class is used by both the `ITracker` implementations and the `TrackerManager`
- The parameters should accurately reflect the torrent's current state for proper tracker operation
- Incorrect parameter values (especially the InfoHash) can result in tracker errors or invalid responses
- The `TorrentEvent` property is particularly important as it notifies the tracker of significant status changes
- When using `TorrentEvent.Stopped`, trackers typically don't return a peer list as the client is shutting down
- Most `AnnounceParameters` instances are created internally by MonoTorrent; manual creation is only needed for custom tracker integration

## Related

- [TrackerManager](../client/TrackerManager.md)
- [ITracker](../client/ITracker.md)
- [ScrapeParameters](../client/ScrapeParameters.md)
- [InfoHash](../common/InfoHash.md)
- [TorrentEvent](../client/TorrentEvent.md)