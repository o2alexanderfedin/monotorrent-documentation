# ConnectionManager Class

The `ConnectionManager` class manages connections to peers in MonoTorrent.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public class ConnectionManager
```

## Description

The `ConnectionManager` class is responsible for:

- Managing connections to peers across all torrents
- Limiting the total number of connections
- Handling the connection and disconnection of peers
- Managing open and half-open connection counts
- Ensuring connections don't exceed configured limits

Each `ClientEngine` has a single `ConnectionManager` instance that is shared across all torrents.

## Properties

### CriticalException

Gets or sets a callback that will be invoked when a critical exception is encountered.

```csharp
public ActionBlock<Exception> CriticalException { get; set; }
```

### HalfOpenConnections

Gets the current number of half-open connections.

```csharp
public int HalfOpenConnections { get; }
```

### MaxConnections

Gets or sets the maximum number of open connections allowed.

```csharp
public int MaxConnections { get; set; }
```

### MaxHalfOpenConnections

Gets or sets the maximum number of half-open connections allowed.

```csharp
public int MaxHalfOpenConnections { get; set; }
```

### OpenConnections

Gets the current number of open connections.

```csharp
public int OpenConnections { get; }
```

### Settings

Gets the settings used by the connection manager.

```csharp
public ConnectionManagerSettings Settings { get; }
```

## Methods

### BanPeer(PeerId)

Bans a peer from reconnecting.

```csharp
public void BanPeer(PeerId peer)
```

#### Parameters

- **peer**: The peer to ban.

### CleanupPeerConnections()

Cleans up peer connections by removing disconnected peers.

```csharp
public void CleanupPeerConnections()
```

### Contains(Uri)

Checks if a peer with the specified URI is already connected.

```csharp
public bool Contains(Uri uri)
```

#### Parameters

- **uri**: The URI to check.

#### Returns

`true` if a peer with the specified URI is connected, `false` otherwise.

### ConnectToPeer(PeerId)

Connects to a peer.

```csharp
public async Task<bool> ConnectToPeer(PeerId id)
```

#### Parameters

- **id**: The peer to connect to.

#### Returns

A task that returns `true` if the connection was successful, `false` otherwise.

### Dispose()

Disposes the connection manager and releases all resources.

```csharp
public void Dispose()
```

### GetOpenConnections()

Gets a list of all open connections.

```csharp
public List<PeerId> GetOpenConnections()
```

#### Returns

A list of all open connections.

### GetPeerConnections(InfoHash)

Gets a list of peer connections for the specified torrent.

```csharp
public List<PeerId> GetPeerConnections(InfoHash infoHash)
```

#### Parameters

- **infoHash**: The info hash of the torrent.

#### Returns

A list of peer connections for the specified torrent.

### IsConnected(Uri)

Checks if a peer with the specified URI is connected.

```csharp
public bool IsConnected(Uri uri)
```

#### Parameters

- **uri**: The URI to check.

#### Returns

`true` if a peer with the specified URI is connected, `false` otherwise.

### NewConnection(Direction, Uri)

Creates a new connection to a peer.

```csharp
public Task<PeerId> NewConnection(Direction direction, Uri uri)
```

#### Parameters

- **direction**: The direction of the connection (incoming or outgoing).
- **uri**: The URI of the peer to connect to.

#### Returns

A task that returns the new peer connection, or `null` if the connection could not be established.

### ProcessFreshConnection(PeerId)

Processes a newly established connection.

```csharp
public async Task<bool> ProcessFreshConnection(PeerId id)
```

#### Parameters

- **id**: The newly connected peer.

#### Returns

A task that returns `true` if the connection was processed successfully, `false` otherwise.

### TryConnect(IList<Peer>, TorrentManager)

Attempts to connect to a list of peers for a specific torrent.

```csharp
public async Task<int> TryConnect(IList<Peer> peers, TorrentManager manager)
```

#### Parameters

- **peers**: The list of peers to try to connect to.
- **manager**: The torrent manager for which to establish connections.

#### Returns

A task that returns the number of successful connections.

## Events

### ConnectionAttemptFailed

Raised when a connection attempt fails.

```csharp
public event EventHandler<ConnectionAttemptFailedEventArgs> ConnectionAttemptFailed;
```

### PeerConnected

Raised when a peer connection is established.

```csharp
public event EventHandler<PeerConnectedEventArgs> PeerConnected;
```

### PeerDisconnected

Raised when a peer connection is closed.

```csharp
public event EventHandler<PeerDisconnectedEventArgs> PeerDisconnected;
```

## Examples

### Basic Connection Management

```csharp
// Create client engine with connection settings
var settings = new EngineSettings
{
    MaximumConnections = 150,         // Total connections across all torrents
    MaximumHalfOpenConnections = 8    // Maximum connection attempts at once
};

var engine = new ClientEngine(settings);

// Access the connection manager
var connectionManager = engine.ConnectionManager;

// Monitor the connection counts
Console.WriteLine($"Open connections: {connectionManager.OpenConnections}");
Console.WriteLine($"Half-open connections: {connectionManager.HalfOpenConnections}");
Console.WriteLine($"Maximum connections allowed: {connectionManager.MaxConnections}");
```

### Connecting to a Peer

```csharp
// Create a peer
var peer = new Peer(
    new Uri("ipv4://192.168.1.100:12345"),
    new InfoHash(new byte[20]) // Use the actual infohash
);

// Create a PeerId for the peer
var peerId = new PeerId(peer, connectionManager);

// Connect to the peer
bool connected = await connectionManager.ConnectToPeer(peerId);
if (connected)
{
    Console.WriteLine("Successfully connected to peer");
}
else
{
    Console.WriteLine("Failed to connect to peer");
}
```

### Monitoring Connections

```csharp
// Subscribe to connection events
connectionManager.PeerConnected += (sender, e) => 
{
    Console.WriteLine($"Peer connected: {e.Peer.Uri}");
    Console.WriteLine($"Total connections: {connectionManager.OpenConnections}");
};

connectionManager.PeerDisconnected += (sender, e) => 
{
    Console.WriteLine($"Peer disconnected: {e.Peer.Uri}");
    Console.WriteLine($"Reason: {e.Reason}");
    Console.WriteLine($"Total connections: {connectionManager.OpenConnections}");
};

connectionManager.ConnectionAttemptFailed += (sender, e) => 
{
    Console.WriteLine($"Connection attempt failed: {e.Peer.Uri}");
    Console.WriteLine($"Reason: {e.Reason}");
};
```

### Listing All Open Connections

```csharp
// Get all open connections
var openConnections = connectionManager.GetOpenConnections();

Console.WriteLine($"Total open connections: {openConnections.Count}");
foreach (var peer in openConnections)
{
    Console.WriteLine($"- Peer: {peer.Uri}");
    Console.WriteLine($"  Client: {peer.ClientApp}");
    Console.WriteLine($"  Torrent: {peer.TorrentManager.Torrent.Name}");
    Console.WriteLine($"  Download rate: {peer.Monitor.DownloadRate / 1024:F2} KB/s");
    Console.WriteLine($"  Upload rate: {peer.Monitor.UploadRate / 1024:F2} KB/s");
}
```

### Getting Connections for a Specific Torrent

```csharp
// Get connections for a specific torrent
var connections = connectionManager.GetPeerConnections(torrentManager.InfoHash);

Console.WriteLine($"Connections for {torrentManager.Torrent.Name}: {connections.Count}");
foreach (var peer in connections)
{
    Console.WriteLine($"- Peer: {peer.Uri}");
}
```

### Banning a Problematic Peer

```csharp
// Ban a peer that is causing problems
void BanProblematicPeer(PeerId peer)
{
    Console.WriteLine($"Banning peer: {peer.Uri}");
    connectionManager.BanPeer(peer);
}

// Example usage - ban a peer that sends corrupt data
torrentManager.PieceHashed += (sender, e) => 
{
    if (!e.HashPassed)
    {
        // Find the peer that sent us this piece
        var peer = torrentManager.Peers.ConnectedPeers
            .FirstOrDefault(p => p.AmRequestingPiecesCount > 0);
        
        if (peer != null)
        {
            Console.WriteLine($"Received corrupt piece from {peer.Uri}");
            BanProblematicPeer(peer);
        }
    }
};
```

### Implementing Custom Connection Limits

```csharp
// Create a class that adjusts connection limits based on system resources
class AdaptiveConnectionManager
{
    private readonly ConnectionManager connectionManager;
    private readonly Timer updateTimer;
    
    public AdaptiveConnectionManager(ConnectionManager connectionManager)
    {
        this.connectionManager = connectionManager;
        
        // Update limits every 30 seconds
        updateTimer = new Timer(UpdateLimits, null, TimeSpan.Zero, TimeSpan.FromSeconds(30));
    }
    
    private void UpdateLimits(object state)
    {
        // Get available memory
        long availableMemoryMB = GetAvailableMemoryMB();
        
        // Adjust connection limits based on available memory
        if (availableMemoryMB < 100)
        {
            // Low memory - reduce connections
            connectionManager.MaxConnections = 50;
            connectionManager.MaxHalfOpenConnections = 5;
        }
        else if (availableMemoryMB < 500)
        {
            // Medium memory
            connectionManager.MaxConnections = 100;
            connectionManager.MaxHalfOpenConnections = 8;
        }
        else
        {
            // High memory
            connectionManager.MaxConnections = 200;
            connectionManager.MaxHalfOpenConnections = 12;
        }
        
        Console.WriteLine($"Adjusted connection limits: Max={connectionManager.MaxConnections}, " +
                         $"HalfOpen={connectionManager.MaxHalfOpenConnections}");
    }
    
    private long GetAvailableMemoryMB()
    {
        // This is a placeholder - implement based on your platform
        // For Windows, you might use PerformanceCounter
        // For Linux, you might read from /proc/meminfo
        return 500; // Example return value
    }
    
    public void Dispose()
    {
        updateTimer.Dispose();
    }
}

// Usage
var adaptiveManager = new AdaptiveConnectionManager(connectionManager);
```

## Remarks

- The `ConnectionManager` is shared across all torrents managed by a `ClientEngine`.
- It enforces global connection limits to prevent resource exhaustion.
- Half-open connections are connection attempts that haven't completed the handshake process.
- The connection manager automatically attempts to maintain connections up to the configured limits.
- It handles both incoming and outgoing connections.
- When the maximum connection limit is reached, new connection attempts will be rejected.
- The connection manager implements connection throttling to prevent overloading the system with connection attempts.
- Connections are typically established based on peer priority, with peers offering rare pieces given higher priority.

## See Also

- [ClientEngine](ClientEngine.md)
- [PeerId](PeerId.md)
- [Peer](Peer.md)
- [TorrentManager](TorrentManager.md)
- [EngineSettings](EngineSettings.md)