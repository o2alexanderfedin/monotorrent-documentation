# Extension Points in MonoTorrent

MonoTorrent is designed with extensibility in mind. This document outlines the key extension points that allow developers to customize and extend the library's functionality.

## Overview of Extension Architecture

MonoTorrent uses a combination of interfaces, abstract classes, and event handlers to provide extension points. These allow you to:

1. Replace core components with custom implementations
2. Add new functionality to existing components
3. React to internal events without modifying library code
4. Extend the BitTorrent protocol with custom extensions

## Key Extension Points

### 1. Piece Picking Strategies

MonoTorrent allows you to implement custom piece selection strategies by implementing the `IPiecePicker` interface.

```csharp
public interface IPiecePicker
{
    void Initialise(BitField bitfield, TorrentFile[] files, IReadOnlyList<Piece> pieces);
    int PickPiece(PeerId id, BitField peerBitfield, List<PeerId> otherPeers);
    void CancelRequest(PeerId peer, int piece, int startOffset, int length);
    // Other methods...
}
```

**Common Use Cases:**
- Implementing prioritized downloading for media files
- Creating custom streaming strategies
- Developing specialized piece pickers for specific use cases

**Example: Simple Sequential Piece Picker**

```csharp
public class SequentialPiecePicker : IPiecePicker
{
    private BitField bitfield;
    private IReadOnlyList<Piece> pieces;
    
    public void Initialise(BitField bitfield, TorrentFile[] files, IReadOnlyList<Piece> pieces)
    {
        this.bitfield = bitfield;
        this.pieces = pieces;
    }
    
    public int PickPiece(PeerId id, BitField peerBitfield, List<PeerId> otherPeers)
    {
        // Simply pick the first piece we don't have that the peer has
        for (int i = 0; i < bitfield.Length; i++)
        {
            if (!bitfield[i] && peerBitfield[i])
                return i;
        }
        return -1;
    }
    
    // Implement other required methods...
}
```

### 2. Custom Storage Solutions

MonoTorrent allows custom storage implementations through the `ITorrentFileInfo` and `IDiskWriter` interfaces.

```csharp
public interface ITorrentFileInfo
{
    string FullPath { get; }
    long Length { get; }
    string Path { get; }
    Priority Priority { get; set; }
    ReadOnlyMemory<byte>[] MD5 { get; }
    ReadOnlyMemory<byte>[] SHA1 { get; }
    ReadOnlyMemory<byte>[] ED2K { get; }
    // Other properties...
}

public interface IDiskWriter : IDisposable
{
    Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count);
    Task WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count);
    Task<bool> ExistsAsync(ITorrentFileInfo file);
    Task MoveAsync(ITorrentFileInfo file, string newPath);
    // Other methods...
}
```

**Common Use Cases:**
- Storing torrent data in memory for small torrents
- Implementing encrypted storage
- Creating virtual file systems
- Storing torrents in databases or cloud storage

**Example: In-Memory Storage Implementation**

```csharp
public class MemoryWriter : IDiskWriter
{
    private Dictionary<string, byte[]> storage = new Dictionary<string, byte[]>();
    
    public async Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        if (!storage.TryGetValue(file.FullPath, out byte[] data))
            return 0;
            
        int bytesToRead = (int)Math.Min(count, data.Length - offset);
        if (bytesToRead <= 0)
            return 0;
            
        Array.Copy(data, offset, buffer, bufferOffset, bytesToRead);
        return bytesToRead;
    }
    
    public async Task WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        if (!storage.TryGetValue(file.FullPath, out byte[] data))
        {
            data = new byte[file.Length];
            storage[file.FullPath] = data;
        }
        
        int bytesToWrite = (int)Math.Min(count, data.Length - offset);
        if (bytesToWrite > 0)
            Array.Copy(buffer, bufferOffset, data, offset, bytesToWrite);
    }
    
    // Implement other required methods...
}
```

### 3. Custom Tracker Implementations

MonoTorrent supports custom tracker protocols by extending the `TrackerClient` abstract class.

```csharp
public abstract class TrackerClient
{
    public abstract bool CanScrape { get; }
    public abstract Uri ScrapeUri { get; }
    public abstract Uri Uri { get; }
    
    public abstract Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters);
    public abstract Task<ScrapeResponse> ScrapeAsync(ScrapeParameters parameters);
}
```

**Common Use Cases:**
- Implementing private tracker protocols
- Creating custom tracker authentication mechanisms
- Supporting new tracker protocols
- Adding WebSocket-based trackers

**Example: Custom HTTP Tracker with Authentication**

```csharp
public class AuthenticatedHttpTracker : HttpTrackerClient
{
    private readonly string username;
    private readonly string password;
    
    public AuthenticatedHttpTracker(Uri uri, string username, string password)
        : base(uri)
    {
        this.username = username;
        this.password = password;
    }
    
    public override async Task<AnnounceResponse> AnnounceAsync(AnnounceParameters parameters)
    {
        // Add authentication to the announce request
        var customParameters = new AnnounceParameters(parameters);
        customParameters.AddCustomParameter("username", username);
        customParameters.AddCustomParameter("password", password);
        
        return await base.AnnounceAsync(customParameters);
    }
}
```

### 4. Custom Peer Connections

MonoTorrent allows customizing peer connections through the `IPeerConnection` interface and the `ConnectionFactory`.

```csharp
public interface IPeerConnection : IDisposable
{
    ReadOnlyMemory<byte> AddressBytes { get; }
    bool CanReconnect { get; }
    bool IsIncoming { get; }
    EndPoint RemoteEndPoint { get; }
    
    Task ConnectAsync();
    Task<int> ReceiveAsync(ByteBuffer buffer);
    Task<int> SendAsync(ByteBuffer buffer);
}

public abstract class ConnectionFactory
{
    public abstract IPeerConnection CreateInboundConnection(ReadOnlyMemory<byte> buffer, EndPoint endPoint);
    public abstract IPeerConnection CreateOutboundConnection(EndPoint endPoint);
}
```

**Common Use Cases:**
- Implementing custom encryption protocols
- Adding support for WebRTC or WebSocket connections
- Creating proxy-based connections
- Implementing NAT traversal techniques

**Example: Proxy Connection Factory**

```csharp
public class ProxyConnectionFactory : ConnectionFactory
{
    private readonly EndPoint proxyEndPoint;
    
    public ProxyConnectionFactory(EndPoint proxyEndPoint)
    {
        this.proxyEndPoint = proxyEndPoint;
    }
    
    public override IPeerConnection CreateOutboundConnection(EndPoint endPoint)
    {
        return new ProxyConnection(proxyEndPoint, endPoint);
    }
    
    // Implement other required methods...
}
```

### 5. Protocol Message Extensions

MonoTorrent supports BitTorrent protocol extensions through the `ExtensionSupports` and custom message implementations.

```csharp
public class ExtensionSupports
{
    public bool SupportsExtended { get; set; }
    public bool SupportsFastPeer { get; set; }
    public bool SupportsLTMessages { get; set; }
    // Other properties...
}

public abstract class PeerMessage
{
    public abstract void Decode(ReadOnlySpan<byte> buffer);
    public abstract int Encode(Span<byte> buffer);
    public abstract int ByteLength { get; }
}
```

**Common Use Cases:**
- Implementing custom BitTorrent extension protocols
- Adding support for new BEPs (BitTorrent Enhancement Proposals)
- Creating private extensions for specific clients

**Example: Custom Protocol Extension Message**

```csharp
[MessageId(100)]  // Use a custom ID
public class MyCustomExtensionMessage : PeerMessage
{
    public override int ByteLength => 5;  // Message length in bytes
    
    public string CustomData { get; private set; }
    
    public MyCustomExtensionMessage(string data)
    {
        CustomData = data;
    }
    
    public override void Decode(ReadOnlySpan<byte> buffer)
    {
        // Decode the message from the buffer
        // ...
    }
    
    public override int Encode(Span<byte> buffer)
    {
        // Encode the message to the buffer
        // ...
        return ByteLength;
    }
}
```

### 6. Event-Based Extensions

MonoTorrent provides numerous events that allow you to react to internal state changes without modifying library code.

**Key Events:**
- `TorrentManager.TorrentStateChanged`
- `TorrentManager.PieceHashed`
- `ClientEngine.ConnectionAttemptFailed`
- `PeerManager.PeerConnected`
- `PeerManager.PeerDisconnected`
- `TrackerManager.AnnounceComplete`

**Common Use Cases:**
- Implementing custom logging
- Adding analytics
- Creating notification systems
- Building user interfaces
- Custom bandwidth management

**Example: Custom Download Progress Tracker**

```csharp
public class DownloadProgressTracker
{
    private readonly Dictionary<InfoHash, TorrentProgress> progress = new Dictionary<InfoHash, TorrentProgress>();
    
    public void Register(TorrentManager manager)
    {
        progress[manager.InfoHash] = new TorrentProgress { StartTime = DateTime.Now };
        
        manager.PieceHashed += (sender, e) => {
            if (e.HashPassed)
            {
                var torrentProgress = progress[manager.InfoHash];
                torrentProgress.VerifiedPieces++;
                torrentProgress.VerifiedBytes += manager.Torrent.PieceLength;
                
                // Calculate and log the speed
                var elapsed = DateTime.Now - torrentProgress.StartTime;
                var bytesPerSecond = torrentProgress.VerifiedBytes / elapsed.TotalSeconds;
                Console.WriteLine($"Download speed: {bytesPerSecond / 1024:F2} KB/s");
            }
        };
    }
    
    private class TorrentProgress
    {
        public DateTime StartTime { get; set; }
        public int VerifiedPieces { get; set; }
        public long VerifiedBytes { get; set; }
    }
}
```

## Advanced Extension Techniques

### Dependency Injection

MonoTorrent components can be extended and customized through dependency injection:

```csharp
// Create custom components
var diskManager = new CustomDiskManager();
var connectionManager = new CustomConnectionManager();
var piecePicker = new CustomPiecePicker();

// Inject them into the TorrentManager
var manager = new TorrentManager(
    torrent,
    downloadFolder,
    torrentSettings,
    downloadFolder,
    piecePicker,
    diskManager,
    connectionManager
);
```

### Custom Modes

You can implement custom torrent modes by extending the `Mode` class:

```csharp
public class MyCustomMode : Mode
{
    public MyCustomMode(TorrentManager manager)
        : base(manager)
    {
    }
    
    public override void Tick()
    {
        // Custom behavior for each tick
    }
    
    // Override other methods as needed
}

// Apply your custom mode
torrentManager.Mode = new MyCustomMode(torrentManager);
```

### Custom Settings Classes

Extend the settings classes to add your own configuration options:

```csharp
public class MyEngineSettings : EngineSettings
{
    public bool EnableMyFeature { get; set; }
    public TimeSpan CustomTimeout { get; set; }
    
    public MyEngineSettings()
    {
        EnableMyFeature = false;
        CustomTimeout = TimeSpan.FromMinutes(5);
    }
}

// Use your custom settings
var engine = new ClientEngine(new MyEngineSettings { EnableMyFeature = true });
```

## Best Practices for Extending MonoTorrent

1. **Use Interfaces**: Prefer implementing interfaces rather than inheriting from concrete classes when possible
2. **Subscribe to Events**: Use events to react to state changes rather than modifying core code
3. **Test Thoroughly**: Extension points may interact with complex BitTorrent protocol behaviors
4. **Consider Performance**: Extensions can impact performance, especially in hot paths
5. **Maintain Protocol Compatibility**: Ensure custom protocol extensions don't break compatibility with other clients
6. **Handle Errors Properly**: Implement proper error handling in your extensions
7. **Document Extensions**: Document how your extensions modify or extend the standard behavior

## Conclusion

MonoTorrent's extension points provide flexibility for customizing almost every aspect of the BitTorrent implementation. By following the patterns described in this document, you can create powerful extensions while maintaining compatibility with the core library.