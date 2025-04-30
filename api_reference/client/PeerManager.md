# PeerManager Class

The `PeerManager` class handles discovery, connection, and management of peers for a torrent.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public class PeerManager
```

## Description

The `PeerManager` class is responsible for:

- Managing the list of known peers for a torrent
- Establishing connections to peers
- Managing connected peers
- Handling peer exchange (PEX)
- Implementing peer connection policies

Each `TorrentManager` has its own `PeerManager` instance to handle peer-related operations for that specific torrent.

## Properties

### AvailablePeers

Gets the list of available peers that are not currently connected to.

```csharp
public IList<Peer> AvailablePeers { get; }
```

### ConnectedPeers

Gets the list of peers that are currently connected.

```csharp
public IList<PeerId> ConnectedPeers { get; }
```

### ActivePeers

Gets the list of peers that are neither choking us nor choked by us.

```csharp
public List<PeerId> ActivePeers { get; }
```

### MaxPeers

Gets or sets the maximum number of peer connections allowed.

```csharp
public int MaxPeers { get; set; }
```

### OpenConnections

Gets the number of currently open connections.

```csharp
public int OpenConnections { get; }
```

### PreferEncryption

Gets or sets whether encryption should be preferred for peer connections.

```csharp
public bool PreferEncryption { get; set; }
```

## Methods

### AddPeer(Peer, PeerAddedReason)

Adds a peer to the lists of available peers.

```csharp
public bool AddPeer(Peer peer, PeerAddedReason reason)
```

#### Parameters

- **peer**: The peer to add.
- **reason**: The reason the peer was added.

#### Returns

`true` if the peer was added, `false` otherwise.

### ClearPeers()

Clears all peer lists.

```csharp
public void ClearPeers()
```

### Contains(Peer)

Checks if a peer already exists in the available or connected peer lists.

```csharp
public bool Contains(Peer peer)
```

#### Parameters

- **peer**: The peer to check.

#### Returns

`true` if the peer exists, `false` otherwise.

### ConnectToPeer(Peer)

Attempts to establish a connection to the specified peer.

```csharp
public Task<bool> ConnectToPeer(Peer peer)
```

#### Parameters

- **peer**: The peer to connect to.

#### Returns

A task that returns `true` if the connection was successful, `false` otherwise.

### GetConnectedPeers()

Returns a list of currently connected peers.

```csharp
public List<PeerId> GetConnectedPeers()
```

#### Returns

A list of connected peers.

### GetPeerConnectionId(Peer)

Gets a peer connection ID for a specific peer if connected.

```csharp
public PeerId GetPeerConnectionId(Peer peer)
```

#### Parameters

- **peer**: The peer to check.

#### Returns

The `PeerId` for the connected peer, or `null` if not connected.

### PeerLocallyChoked(PeerId)

Updates the interested/choked state of a peer when it is locally choked.

```csharp
public void PeerLocallyChoked(PeerId id)
```

#### Parameters

- **id**: The peer ID.

### PeerRemotelyChoked(PeerId)

Updates the interested/choked state of a peer when it is remotely choked.

```csharp
public void PeerRemotelyChoked(PeerId id)
```

#### Parameters

- **id**: The peer ID.

### PeerDisconnected(PeerId)

Handles a disconnected peer, potentially adding it back to the available peers list.

```csharp
public void PeerDisconnected(PeerId id)
```

#### Parameters

- **id**: The peer ID of the disconnected peer.

### Stop()

Stops the peer manager, disconnecting from all peers.

```csharp
public void Stop()
```

## Events

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

### PeerAdded

Raised when a peer is added to the available peers list.

```csharp
public event EventHandler<PeerAddedEventArgs> PeerAdded;
```

### PeerRemoved

Raised when a peer is removed from the available peers list.

```csharp
public event EventHandler<PeerRemovedEventArgs> PeerRemoved;
```

## Examples

### Monitoring Peer Connections

```csharp
// Subscribe to peer events
torrentManager.Peers.PeerConnected += (sender, args) =>
{
    Console.WriteLine($"Peer connected: {args.Peer.ConnectionUri}");
    Console.WriteLine($"Encryption: {args.Peer.Encryption}");
    Console.WriteLine($"Client: {args.Peer.ClientApp}");
};

torrentManager.Peers.PeerDisconnected += (sender, args) =>
{
    Console.WriteLine($"Peer disconnected: {args.Peer.ConnectionUri}");
    Console.WriteLine($"Reason: {args.Reason}");
};
```

### Working with Peer Lists

```csharp
// Get a list of all available peers
var availablePeers = torrentManager.Peers.AvailablePeers;
Console.WriteLine($"Available peers: {availablePeers.Count}");

// Get a list of connected peers
var connectedPeers = torrentManager.Peers.ConnectedPeers;
Console.WriteLine($"Connected peers: {connectedPeers.Count}");

// Display information about connected peers
foreach (var peer in connectedPeers)
{
    Console.WriteLine($"Peer: {peer.ConnectionUri}");
    Console.WriteLine($"Client: {peer.ClientApp}");
    Console.WriteLine($"Download speed: {peer.Monitor.DownloadRate / 1024.0:F2} KB/s");
    Console.WriteLine($"Upload speed: {peer.Monitor.UploadRate / 1024.0:F2} KB/s");
    Console.WriteLine($"Piece availability: {peer.Bitfield.PercentComplete:F2}%");
    Console.WriteLine($"Am choking: {peer.AmChoking}");
    Console.WriteLine($"Am interested: {peer.AmInterested}");
    Console.WriteLine($"Peer choking: {peer.IsChoking}");
    Console.WriteLine($"Peer interested: {peer.IsInterested}");
    Console.WriteLine();
}
```

### Manually Connecting to a Peer

```csharp
// Create a new peer
var peer = new Peer(
    new Uri("ipv4://192.168.1.100:12345"),
    new InfoHash(new byte[20]) // Use the actual infohash
);

// Add the peer to the manager
bool added = torrentManager.Peers.AddPeer(peer, PeerAddedReason.Manual);
if (added)
{
    // Try connecting to the peer
    bool connected = await torrentManager.Peers.ConnectToPeer(peer);
    Console.WriteLine($"Connection to peer successful: {connected}");
}
```

### Limiting Peer Connections

```csharp
// Set the maximum number of peer connections
torrentManager.Peers.MaxPeers = 50;

// Get the current number of connections
int openConnections = torrentManager.Peers.OpenConnections;
Console.WriteLine($"Open connections: {openConnections} / {torrentManager.Peers.MaxPeers}");
```

## Remarks

- The `PeerManager` automatically handles most peer-related operations; manual intervention is rarely needed.
- The peer lists are automatically updated as peers connect, disconnect, or are discovered.
- Peers are discovered from multiple sources: trackers, DHT, PEX, and local peer discovery.
- Choking and unchoking of peers is handled automatically by MonoTorrent's choking algorithm.
- The `MaxPeers` property controls the maximum number of simultaneous connections.

## See Also

- [Peer](../client/Peer.md)
- [PeerId](../client/PeerId.md)
- [TorrentManager](TorrentManager.md)
- [ClientEngine](ClientEngine.md)