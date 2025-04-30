# Implementing Custom Trackers

This example demonstrates how to implement custom tracker functionality in MonoTorrent, allowing you to create specialized trackers or integrate with non-standard tracking systems.

## Contents

- [Understanding the Tracker System](#understanding-the-tracker-system)
- [The ITracker Interface](#the-itracker-interface)
- [Implementing a Custom Tracker](#implementing-a-custom-tracker)
- [Database-backed Tracker](#database-backed-tracker)
- [Specialized Tracker Implementations](#specialized-tracker-implementations)
- [Complete Example](#complete-example)

## Understanding the Tracker System

In the BitTorrent protocol, trackers are responsible for:

1. Keeping track of peers for torrents
2. Facilitating peer discovery
3. Collecting statistics about torrents

MonoTorrent allows you to implement custom trackers by implementing the `ITracker` interface.

## The ITracker Interface

The `ITracker` interface defines the contract for all tracker implementations:

```csharp
public interface ITracker
{
    // Basic properties
    bool CanAnnounce { get; }
    bool CanScrape { get; }
    TimeSpan MinUpdateInterval { get; }
    string Name { get; }
    Uri Uri { get; }
    
    // Announce and scrape methods
    Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters, CancellationToken token);
    Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters, CancellationToken token);
}
```

## Implementing a Custom Tracker

Here's a basic implementation of a custom tracker:

```csharp
public class CustomTracker : ITracker
{
    private readonly Uri _uri;
    private readonly Dictionary<InfoHash, HashSet<PeerInfo>> _peers = new Dictionary<InfoHash, HashSet<PeerInfo>>();
    private readonly Dictionary<InfoHash, int> _completedDownloads = new Dictionary<InfoHash, int>();
    
    public CustomTracker(Uri uri)
    {
        _uri = uri ?? throw new ArgumentNullException(nameof(uri));
    }
    
    // ITracker interface properties
    public bool CanAnnounce => true;
    public bool CanScrape => true;
    public TimeSpan MinUpdateInterval => TimeSpan.FromMinutes(2);
    public string Name => "Custom Tracker";
    public Uri Uri => _uri;
    
    // Announce method - called when a peer wants to register with the tracker
    public Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters, CancellationToken token)
    {
        // Create peer info
        var peer = new PeerInfo(
            parameters.ClientAddress.Address,
            parameters.ClientAddress.Port);
            
        // Update peer information
        lock (_peers)
        {
            if (!_peers.TryGetValue(parameters.InfoHash, out var peerList))
            {
                peerList = new HashSet<PeerInfo>();
                _peers[parameters.InfoHash] = peerList;
                _completedDownloads[parameters.InfoHash] = 0;
            }
            
            // Handle event
            switch (parameters.Event)
            {
                case TorrentEvent.Completed:
                    _completedDownloads[parameters.InfoHash]++;
                    break;
                    
                case TorrentEvent.Stopped:
                    peerList.RemoveWhere(p => 
                        p.ConnectionUri.EndPoint.Address.Equals(peer.ConnectionUri.EndPoint.Address) &&
                        p.ConnectionUri.EndPoint.Port == peer.ConnectionUri.EndPoint.Port);
                    return Task.FromResult(new AnnounceResponse(
                        true, null, Array.Empty<PeerInfo>(), null, null, MinUpdateInterval));
            }
            
            // Add/update this peer
            peerList.Add(peer);
            
            // Return a list of peers (excluding the requesting peer)
            var peersToReturn = peerList
                .Where(p => !p.ConnectionUri.EndPoint.Address.Equals(peer.ConnectionUri.EndPoint.Address) ||
                            p.ConnectionUri.EndPoint.Port != peer.ConnectionUri.EndPoint.Port)
                .ToArray();
                
            return Task.FromResult(new AnnounceResponse(
                true, null, peersToReturn, null, null, MinUpdateInterval));
        }
    }
    
    // Scrape method - returns statistics about torrents
    public Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters, CancellationToken token)
    {
        var results = new Dictionary<InfoHash, ScrapeInfo>();
        
        lock (_peers)
        {
            foreach (var infoHash in parameters.InfoHashes)
            {
                if (_peers.TryGetValue(infoHash, out var peerList))
                {
                    // Count seeders (have complete file) and leechers (downloading)
                    int seeders = peerList.Count(p => p.IsSeeder);
                    int leechers = peerList.Count - seeders;
                    int complete = _completedDownloads.TryGetValue(infoHash, out int completed) ? completed : 0;
                    
                    results[infoHash] = new ScrapeInfo(seeders, leechers, complete);
                }
            }
        }
        
        return Task.FromResult(new ScrapeResponse(true, null, results));
    }
}
```

## Database-backed Tracker

For a more persistent tracker implementation, you might store peers in a database:

```csharp
public class DatabaseTracker : ITracker
{
    private readonly Uri _uri;
    private readonly string _connectionString;
    
    public DatabaseTracker(Uri uri, string connectionString)
    {
        _uri = uri ?? throw new ArgumentNullException(nameof(uri));
        _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
    }
    
    // ITracker interface properties
    public bool CanAnnounce => true;
    public bool CanScrape => true;
    public TimeSpan MinUpdateInterval => TimeSpan.FromMinutes(3);
    public string Name => "Database Tracker";
    public Uri Uri => _uri;
    
    // Announce method using database
    public async Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters, CancellationToken token)
    {
        using (var connection = new SqlConnection(_connectionString))
        {
            await connection.OpenAsync(token);
            
            // Handle the peer based on the event
            switch (parameters.Event)
            {
                case TorrentEvent.Started:
                    await AddPeerAsync(connection, parameters, token);
                    break;
                    
                case TorrentEvent.Completed:
                    await CompleteTorrentAsync(connection, parameters, token);
                    break;
                    
                case TorrentEvent.Stopped:
                    await RemovePeerAsync(connection, parameters, token);
                    return new AnnounceResponse(true, null, Array.Empty<PeerInfo>(), null, null, MinUpdateInterval);
                    
                default:
                    await UpdatePeerAsync(connection, parameters, token);
                    break;
            }
            
            // Get peers to return
            var peers = await GetPeersAsync(connection, parameters, token);
            
            return new AnnounceResponse(true, null, peers, null, null, MinUpdateInterval);
        }
    }
    
    // Database operations for peer management
    private async Task AddPeerAsync(SqlConnection connection, AnnounceParameters parameters, CancellationToken token)
    {
        using (var command = new SqlCommand(@"
            INSERT INTO Peers (InfoHash, IP, Port, LastSeen, IsSeeder, BytesDownloaded, BytesUploaded)
            VALUES (@InfoHash, @IP, @Port, @LastSeen, @IsSeeder, @Downloaded, @Uploaded)
            ON DUPLICATE KEY UPDATE
                LastSeen = @LastSeen,
                IsSeeder = @IsSeeder,
                BytesDownloaded = @Downloaded,
                BytesUploaded = @Uploaded", connection))
        {
            command.Parameters.AddWithValue("@InfoHash", parameters.InfoHash.ToHex());
            command.Parameters.AddWithValue("@IP", parameters.ClientAddress.Address.ToString());
            command.Parameters.AddWithValue("@Port", parameters.ClientAddress.Port);
            command.Parameters.AddWithValue("@LastSeen", DateTime.UtcNow);
            command.Parameters.AddWithValue("@IsSeeder", parameters.BytesLeft == 0);
            command.Parameters.AddWithValue("@Downloaded", parameters.BytesDownloaded);
            command.Parameters.AddWithValue("@Uploaded", parameters.BytesUploaded);
            
            await command.ExecuteNonQueryAsync(token);
        }
    }
    
    private async Task UpdatePeerAsync(SqlConnection connection, AnnounceParameters parameters, CancellationToken token)
    {
        using (var command = new SqlCommand(@"
            UPDATE Peers
            SET LastSeen = @LastSeen,
                IsSeeder = @IsSeeder,
                BytesDownloaded = @Downloaded,
                BytesUploaded = @Uploaded
            WHERE InfoHash = @InfoHash AND IP = @IP AND Port = @Port", connection))
        {
            command.Parameters.AddWithValue("@InfoHash", parameters.InfoHash.ToHex());
            command.Parameters.AddWithValue("@IP", parameters.ClientAddress.Address.ToString());
            command.Parameters.AddWithValue("@Port", parameters.ClientAddress.Port);
            command.Parameters.AddWithValue("@LastSeen", DateTime.UtcNow);
            command.Parameters.AddWithValue("@IsSeeder", parameters.BytesLeft == 0);
            command.Parameters.AddWithValue("@Downloaded", parameters.BytesDownloaded);
            command.Parameters.AddWithValue("@Uploaded", parameters.BytesUploaded);
            
            await command.ExecuteNonQueryAsync(token);
        }
    }
    
    private async Task RemovePeerAsync(SqlConnection connection, AnnounceParameters parameters, CancellationToken token)
    {
        using (var command = new SqlCommand(@"
            DELETE FROM Peers
            WHERE InfoHash = @InfoHash AND IP = @IP AND Port = @Port", connection))
        {
            command.Parameters.AddWithValue("@InfoHash", parameters.InfoHash.ToHex());
            command.Parameters.AddWithValue("@IP", parameters.ClientAddress.Address.ToString());
            command.Parameters.AddWithValue("@Port", parameters.ClientAddress.Port);
            
            await command.ExecuteNonQueryAsync(token);
        }
    }
    
    private async Task CompleteTorrentAsync(SqlConnection connection, AnnounceParameters parameters, CancellationToken token)
    {
        // First update the peer
        await UpdatePeerAsync(connection, parameters, token);
        
        // Then increment the completed count for this torrent
        using (var command = new SqlCommand(@"
            UPDATE Torrents
            SET Completed = Completed + 1
            WHERE InfoHash = @InfoHash", connection))
        {
            command.Parameters.AddWithValue("@InfoHash", parameters.InfoHash.ToHex());
            await command.ExecuteNonQueryAsync(token);
        }
    }
    
    private async Task<PeerInfo[]> GetPeersAsync(SqlConnection connection, AnnounceParameters parameters, CancellationToken token)
    {
        var peers = new List<PeerInfo>();
        
        using (var command = new SqlCommand(@"
            SELECT IP, Port, IsSeeder
            FROM Peers
            WHERE InfoHash = @InfoHash
              AND LastSeen > @CutoffTime
              AND (IP != @ClientIP OR Port != @ClientPort)
            LIMIT 50", connection))
        {
            command.Parameters.AddWithValue("@InfoHash", parameters.InfoHash.ToHex());
            command.Parameters.AddWithValue("@CutoffTime", DateTime.UtcNow.AddMinutes(-15));
            command.Parameters.AddWithValue("@ClientIP", parameters.ClientAddress.Address.ToString());
            command.Parameters.AddWithValue("@ClientPort", parameters.ClientAddress.Port);
            
            using (var reader = await command.ExecuteReaderAsync(token))
            {
                while (await reader.ReadAsync(token))
                {
                    string ip = reader.GetString(0);
                    int port = reader.GetInt32(1);
                    bool isSeeder = reader.GetBoolean(2);
                    
                    if (IPAddress.TryParse(ip, out IPAddress ipAddress))
                    {
                        var peer = new PeerInfo(ipAddress, port);
                        if (isSeeder)
                            peer.MaybeSeeder = true;
                            
                        peers.Add(peer);
                    }
                }
            }
        }
        
        return peers.ToArray();
    }
    
    // Scrape method
    public async Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters, CancellationToken token)
    {
        using (var connection = new SqlConnection(_connectionString))
        {
            await connection.OpenAsync(token);
            
            var results = new Dictionary<InfoHash, ScrapeInfo>();
            
            foreach (var infoHash in parameters.InfoHashes)
            {
                // Get statistics for this torrent
                using (var command = new SqlCommand(@"
                    SELECT 
                        (SELECT COUNT(*) FROM Peers WHERE InfoHash = @InfoHash AND IsSeeder = 1 AND LastSeen > @CutoffTime) AS Seeders,
                        (SELECT COUNT(*) FROM Peers WHERE InfoHash = @InfoHash AND IsSeeder = 0 AND LastSeen > @CutoffTime) AS Leechers,
                        (SELECT Completed FROM Torrents WHERE InfoHash = @InfoHash) AS Completed", connection))
                {
                    command.Parameters.AddWithValue("@InfoHash", infoHash.ToHex());
                    command.Parameters.AddWithValue("@CutoffTime", DateTime.UtcNow.AddMinutes(-15));
                    
                    using (var reader = await command.ExecuteReaderAsync(token))
                    {
                        if (await reader.ReadAsync(token))
                        {
                            int seeders = reader.GetInt32(0);
                            int leechers = reader.GetInt32(1);
                            int completed = reader.IsDBNull(2) ? 0 : reader.GetInt32(2);
                            
                            results[infoHash] = new ScrapeInfo(seeders, leechers, completed);
                        }
                    }
                }
            }
            
            return new ScrapeResponse(true, null, results);
        }
    }
}
```

## Specialized Tracker Implementations

### Redis-based Tracker

For high-performance and scalability, you might implement a Redis-backed tracker:

```csharp
public class RedisTracker : ITracker
{
    private readonly Uri _uri;
    private readonly ConnectionMultiplexer _redis;
    
    public RedisTracker(Uri uri, string redisConnectionString)
    {
        _uri = uri ?? throw new ArgumentNullException(nameof(uri));
        _redis = ConnectionMultiplexer.Connect(redisConnectionString);
    }
    
    // ITracker interface properties
    public bool CanAnnounce => true;
    public bool CanScrape => true;
    public TimeSpan MinUpdateInterval => TimeSpan.FromMinutes(1);
    public string Name => "Redis Tracker";
    public Uri Uri => _uri;
    
    // Announce using Redis
    public async Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters, CancellationToken token)
    {
        var db = _redis.GetDatabase();
        string infoHashKey = $"torrent:{parameters.InfoHash.ToHex()}";
        string peerKey = $"{infoHashKey}:peers";
        string peerData = $"{parameters.ClientAddress.Address}:{parameters.ClientAddress.Port}:{parameters.BytesLeft == 0}";
        
        // Handle the event
        switch (parameters.Event)
        {
            case TorrentEvent.Started:
            case TorrentEvent.None:
                // Add/update this peer with expiration
                await db.HashSetAsync(peerKey, peerData, DateTime.UtcNow.Ticks);
                await db.KeyExpireAsync(peerKey, TimeSpan.FromMinutes(30));
                break;
                
            case TorrentEvent.Completed:
                // Add/update this peer and increment completed count
                await db.HashSetAsync(peerKey, peerData, DateTime.UtcNow.Ticks);
                await db.HashIncrementAsync(infoHashKey, "completed");
                await db.KeyExpireAsync(peerKey, TimeSpan.FromMinutes(30));
                break;
                
            case TorrentEvent.Stopped:
                // Remove this peer
                await db.HashDeleteAsync(peerKey, peerData);
                return new AnnounceResponse(true, null, Array.Empty<PeerInfo>(), null, null, MinUpdateInterval);
        }
        
        // Get peers to return
        var peerEntries = await db.HashGetAllAsync(peerKey);
        var cutoffTime = DateTime.UtcNow.AddMinutes(-15).Ticks;
        
        var peers = new List<PeerInfo>();
        foreach (var entry in peerEntries)
        {
            // Skip outdated peers
            if (long.Parse(entry.Value) < cutoffTime)
                continue;
                
            // Skip the requesting peer
            var parts = entry.Name.ToString().Split(':');
            if (parts.Length != 3)
                continue;
                
            if (IPAddress.TryParse(parts[0], out IPAddress ip) && int.TryParse(parts[1], out int port))
            {
                if (ip.Equals(parameters.ClientAddress.Address) && port == parameters.ClientAddress.Port)
                    continue;
                    
                var peer = new PeerInfo(ip, port);
                if (bool.TryParse(parts[2], out bool isSeeder) && isSeeder)
                    peer.MaybeSeeder = true;
                    
                peers.Add(peer);
            }
        }
        
        return new AnnounceResponse(true, null, peers.ToArray(), null, null, MinUpdateInterval);
    }
    
    // Scrape using Redis
    public async Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters, CancellationToken token)
    {
        var db = _redis.GetDatabase();
        var results = new Dictionary<InfoHash, ScrapeInfo>();
        
        foreach (var infoHash in parameters.InfoHashes)
        {
            string infoHashKey = $"torrent:{infoHash.ToHex()}";
            string peerKey = $"{infoHashKey}:peers";
            
            // Get completed count
            int completed = (int)(await db.HashGetAsync(infoHashKey, "completed") ?? 0);
            
            // Count seeders and leechers
            var peerEntries = await db.HashGetAllAsync(peerKey);
            var cutoffTime = DateTime.UtcNow.AddMinutes(-15).Ticks;
            
            int seeders = 0;
            int leechers = 0;
            
            foreach (var entry in peerEntries)
            {
                // Skip outdated peers
                if (long.Parse(entry.Value) < cutoffTime)
                    continue;
                    
                var parts = entry.Name.ToString().Split(':');
                if (parts.Length == 3 && bool.TryParse(parts[2], out bool isSeeder))
                {
                    if (isSeeder)
                        seeders++;
                    else
                        leechers++;
                }
            }
            
            results[infoHash] = new ScrapeInfo(seeders, leechers, completed);
        }
        
        return new ScrapeResponse(true, null, results);
    }
    
    public void Dispose()
    {
        _redis?.Dispose();
    }
}
```

### Authentication-Required Tracker

You might need a tracker that requires authentication:

```csharp
public class AuthenticatedTracker : ITracker
{
    private readonly Uri _uri;
    private readonly ICustomAuthService _authService;
    private readonly ICustomPeerStorage _peerStorage;
    
    public AuthenticatedTracker(Uri uri, ICustomAuthService authService, ICustomPeerStorage peerStorage)
    {
        _uri = uri ?? throw new ArgumentNullException(nameof(uri));
        _authService = authService ?? throw new ArgumentNullException(nameof(authService));
        _peerStorage = peerStorage ?? throw new ArgumentNullException(nameof(peerStorage));
    }
    
    // ITracker interface properties
    public bool CanAnnounce => true;
    public bool CanScrape => true;
    public TimeSpan MinUpdateInterval => TimeSpan.FromMinutes(2);
    public string Name => "Authenticated Tracker";
    public Uri Uri => _uri;
    
    // Announce with authentication
    public async Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters, CancellationToken token)
    {
        // Extract authentication info from parameters
        string passkey = ExtractPasskey(parameters);
        
        // Validate authentication
        if (!await _authService.ValidatePasskeyAsync(passkey, token))
        {
            return new AnnounceResponse(false, "Invalid passkey", Array.Empty<PeerInfo>(), null, null, TimeSpan.Zero);
        }
        
        // Check if user is authorized for this torrent
        if (!await _authService.CanAccessTorrentAsync(passkey, parameters.InfoHash, token))
        {
            return new AnnounceResponse(false, "Not authorized for this torrent", Array.Empty<PeerInfo>(), null, null, TimeSpan.Zero);
        }
        
        // Process the announce now that authentication is validated
        return await _peerStorage.ProcessAnnounceAsync(parameters, passkey, token);
    }
    
    // Extract passkey from announce parameters (typically from the URL)
    private string ExtractPasskey(AnnounceParameters parameters)
    {
        // In a real implementation, this might extract it from a custom parameter
        // or from the announce URL if using a URL format like:
        // http://tracker.example.com/PASSKEY/announce
        
        // For this example, we'll assume it's in a custom parameter
        if (parameters.CustomParameters != null && 
            parameters.CustomParameters.TryGetValue("passkey", out string passkey))
        {
            return passkey;
        }
        
        return string.Empty;
    }
    
    // Scrape with authentication
    public async Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters, CancellationToken token)
    {
        // Extract authentication info
        string passkey = ExtractPasskey(parameters);
        
        // Validate authentication
        if (!await _authService.ValidatePasskeyAsync(passkey, token))
        {
            return new ScrapeResponse(false, "Invalid passkey", new Dictionary<InfoHash, ScrapeInfo>());
        }
        
        // Process the scrape
        return await _peerStorage.ProcessScrapeAsync(parameters, passkey, token);
    }
    
    // Helper method to extract passkey from scrape parameters
    private string ExtractPasskey(ScrapeParameters parameters)
    {
        // Similar to the announce method
        if (parameters.CustomParameters != null && 
            parameters.CustomParameters.TryGetValue("passkey", out string passkey))
        {
            return passkey;
        }
        
        return string.Empty;
    }
}

// Example interfaces that would need to be implemented
public interface ICustomAuthService
{
    Task<bool> ValidatePasskeyAsync(string passkey, CancellationToken token);
    Task<bool> CanAccessTorrentAsync(string passkey, InfoHash infoHash, CancellationToken token);
}

public interface ICustomPeerStorage
{
    Task<AnnounceResponse> ProcessAnnounceAsync(AnnounceParameters parameters, string passkey, CancellationToken token);
    Task<ScrapeResponse> ProcessScrapeAsync(ScrapeParameters parameters, string passkey, CancellationToken token);
}
```

## Complete Example

Here's a complete example demonstrating how to implement and use a custom tracker:

```csharp
public class CustomTrackerExample
{
    // In-memory custom tracker demonstration
    private class InMemoryTracker : ITracker
    {
        private readonly Uri _uri;
        private readonly Dictionary<InfoHash, HashSet<PeerInfo>> _peers = new Dictionary<InfoHash, HashSet<PeerInfo>>();
        private readonly Dictionary<InfoHash, int> _completed = new Dictionary<InfoHash, int>();
        private readonly Dictionary<InfoHash, string> _torrentNames = new Dictionary<InfoHash, string>();
        
        public InMemoryTracker(Uri uri)
        {
            _uri = uri ?? throw new ArgumentNullException(nameof(uri));
        }
        
        // Register a torrent name with this tracker
        public void RegisterTorrent(InfoHash infoHash, string name)
        {
            lock (_peers)
            {
                _torrentNames[infoHash] = name;
                if (!_peers.ContainsKey(infoHash))
                {
                    _peers[infoHash] = new HashSet<PeerInfo>();
                    _completed[infoHash] = 0;
                }
            }
        }
        
        // ITracker implementation
        public bool CanAnnounce => true;
        public bool CanScrape => true;
        public TimeSpan MinUpdateInterval => TimeSpan.FromSeconds(30); // Short for demo
        public string Name => "In-Memory Tracker";
        public Uri Uri => _uri;
        
        public Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters, CancellationToken token)
        {
            Console.WriteLine($"Received announce from {parameters.ClientAddress}");
            
            // Create peer info
            var peer = new PeerInfo(parameters.ClientAddress.Address, parameters.ClientAddress.Port);
            
            // Update peer information
            lock (_peers)
            {
                if (!_peers.TryGetValue(parameters.InfoHash, out var peerList))
                {
                    peerList = new HashSet<PeerInfo>();
                    _peers[parameters.InfoHash] = peerList;
                    _completed[parameters.InfoHash] = 0;
                }
                
                // Handle event
                switch (parameters.Event)
                {
                    case TorrentEvent.Completed:
                        Console.WriteLine($"Peer completed download!");
                        _completed[parameters.InfoHash]++;
                        break;
                        
                    case TorrentEvent.Stopped:
                        Console.WriteLine($"Peer {parameters.ClientAddress} stopped");
                        peerList.RemoveWhere(p => 
                            p.ConnectionUri.EndPoint.Address.Equals(peer.ConnectionUri.EndPoint.Address) &&
                            p.ConnectionUri.EndPoint.Port == peer.ConnectionUri.EndPoint.Port);
                        return Task.FromResult(new AnnounceResponse(
                            true, null, Array.Empty<PeerInfo>(), null, null, MinUpdateInterval));
                }
                
                // Set seeder status based on bytes left
                if (parameters.BytesLeft == 0)
                {
                    peer.MaybeSeeder = true;
                    Console.WriteLine($"Peer is a seeder");
                }
                
                // Add/update this peer
                peerList.Add(peer);
                
                // Count stats
                int seeders = peerList.Count(p => p.IsSeeder);
                int leechers = peerList.Count - seeders;
                
                Console.WriteLine($"Tracker stats for {_torrentNames.TryGetValue(parameters.InfoHash, out var name) ? name : parameters.InfoHash.ToHex()}:");
                Console.WriteLine($"- Seeders: {seeders}");
                Console.WriteLine($"- Leechers: {leechers}");
                Console.WriteLine($"- Completed: {_completed[parameters.InfoHash]}");
                
                // Return a list of peers (excluding the requesting peer)
                var peersToReturn = peerList
                    .Where(p => !p.ConnectionUri.EndPoint.Address.Equals(peer.ConnectionUri.EndPoint.Address) ||
                                p.ConnectionUri.EndPoint.Port != peer.ConnectionUri.EndPoint.Port)
                    .ToArray();
                    
                Console.WriteLine($"Returning {peersToReturn.Length} peers to client");
                
                return Task.FromResult(new AnnounceResponse(
                    true, null, peersToReturn, seeders, leechers, MinUpdateInterval));
            }
        }
        
        public Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters, CancellationToken token)
        {
            Console.WriteLine("Received scrape request");
            
            var results = new Dictionary<InfoHash, ScrapeInfo>();
            
            lock (_peers)
            {
                foreach (var infoHash in parameters.InfoHashes)
                {
                    if (_peers.TryGetValue(infoHash, out var peerList))
                    {
                        int seeders = peerList.Count(p => p.IsSeeder);
                        int leechers = peerList.Count - seeders;
                        int complete = _completed.TryGetValue(infoHash, out int completed) ? completed : 0;
                        
                        results[infoHash] = new ScrapeInfo(seeders, leechers, complete);
                        
                        Console.WriteLine($"Scrape for {_torrentNames.TryGetValue(infoHash, out var name) ? name : infoHash.ToHex()}:");
                        Console.WriteLine($"- Seeders: {seeders}");
                        Console.WriteLine($"- Leechers: {leechers}");
                        Console.WriteLine($"- Completed: {complete}");
                    }
                }
            }
            
            return Task.FromResult(new ScrapeResponse(true, null, results));
        }
    }
    
    // Main example code
    public static async Task RunAsync()
    {
        // Create our custom tracker
        var customTrackerUri = new Uri("http://localhost:12345/announce");
        var customTracker = new InMemoryTracker(customTrackerUri);
        
        // Create two engine instances to demonstrate peer exchange
        Console.WriteLine("Creating two client instances to demonstrate tracker functionality");
        
        var settings1 = new EngineSettings
        {
            SavePath = Path.Combine(Path.GetTempPath(), "MonoTorrentDemo1"),
            ListenPort = 15000
        };
        
        var settings2 = new EngineSettings
        {
            SavePath = Path.Combine(Path.GetTempPath(), "MonoTorrentDemo2"),
            ListenPort = 15001
        };
        
        // Create directory if it doesn't exist
        Directory.CreateDirectory(settings1.SavePath);
        Directory.CreateDirectory(settings2.SavePath);
        
        // Create the client engines
        using var engine1 = new ClientEngine(settings1);
        using var engine2 = new ClientEngine(settings2);
        
        // Create a simple torrent for demonstration
        string demoFileName = "demo_file.txt";
        string demoFilePath = Path.Combine(settings1.SavePath, demoFileName);
        
        Console.WriteLine("Creating a demo file and torrent");
        
        // Create a demo file
        await File.WriteAllTextAsync(demoFilePath, "This is a demo file for the MonoTorrent custom tracker example.");
        
        // Create a torrent from the file
        var creator = new TorrentCreator();
        creator.AddFile(demoFilePath);
        
        // Add our custom tracker to the torrent
        creator.Announces.Add(new[] { customTrackerUri.ToString() });
        creator.Comment = "Custom tracker demo torrent";
        creator.Publisher = "MonoTorrent Example";
        creator.CreatedBy = "Custom Tracker Example";
        
        // Create the torrent file
        string torrentPath = Path.Combine(settings1.SavePath, "demo.torrent");
        await creator.CreateAsync(torrentPath);
        
        // Load the created torrent
        var torrent = await Torrent.LoadAsync(torrentPath);
        Console.WriteLine($"Created torrent: {torrent.Name}");
        
        // Register the torrent with our custom tracker
        customTracker.RegisterTorrent(torrent.InfoHash, torrent.Name);
        
        // Create torrent managers in both engines
        var manager1 = await engine1.AddAsync(torrent, settings1.SavePath);
        
        // For the second client, we'll need to copy the file to a different location
        string demoFilePath2 = Path.Combine(settings2.SavePath, demoFileName);
        File.Copy(demoFilePath, demoFilePath2, true);
        var manager2 = await engine2.AddAsync(torrent, settings2.SavePath);
        
        // Register our custom tracker implementation with both clients
        manager1.TrackerManager.Add(customTracker);
        manager2.TrackerManager.Add(customTracker);
        
        Console.WriteLine("Starting the first client as a seed");
        
        // Start the first client as a seed
        await manager1.StartAsync();
        
        // Wait a moment for the first client to announce
        await Task.Delay(1000);
        
        Console.WriteLine("Starting the second client");
        
        // Start the second client (will be a seed too since we copied the file)
        await manager2.StartAsync();
        
        // Wait for both clients to announce and exchange information via our custom tracker
        await Task.Delay(2000);
        
        // Display the connection status
        Console.WriteLine("\nClient 1 status:");
        Console.WriteLine($"- State: {manager1.State}");
        Console.WriteLine($"- Connected peers: {manager1.Peers.ConnectedPeers}");
        
        Console.WriteLine("\nClient 2 status:");
        Console.WriteLine($"- State: {manager2.State}");
        Console.WriteLine($"- Connected peers: {manager2.Peers.ConnectedPeers}");
        
        // Perform a scrape to get overall stats
        Console.WriteLine("\nPerforming scrape to get overall torrent statistics");
        var scrapeParams = new ScrapeParameters(torrent.InfoHash);
        var scrapeResult = await customTracker.ScrapeAsync(scrapeParams, CancellationToken.None);
        
        if (scrapeResult.Successful && scrapeResult.Results.TryGetValue(torrent.InfoHash, out var info))
        {
            Console.WriteLine($"Scrape results for {torrent.Name}:");
            Console.WriteLine($"- Complete (seeders): {info.Complete}");
            Console.WriteLine($"- Incomplete (leechers): {info.Incomplete}");
            Console.WriteLine($"- Downloads completed: {info.Downloaded}");
        }
        
        // Clean up
        Console.WriteLine("\nStopping clients");
        await engine1.StopAllAsync();
        await engine2.StopAllAsync();
        
        Console.WriteLine("Custom tracker example completed");
    }
}
```

This example demonstrates:

1. A basic in-memory custom tracker implementation
2. How to register a custom tracker with a torrent manager
3. How to use the custom tracker to facilitate peer exchange
4. Working with the announce and scrape functionality
5. Creating and handling a simple torrent to test the custom tracker

For production use, you would typically implement persistence, proper error handling, and more robust peer management. The code examples demonstrate the fundamental concepts to build upon for specific use cases.