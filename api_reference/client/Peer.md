# Peer

**Namespace**: `MonoTorrent.Client`

The `Peer` class represents a remote BitTorrent peer, containing its connection information and available pieces.

## Overview

In BitTorrent networking, a peer is another client that is downloading or seeding the same torrent. The `Peer` class contains the information needed to connect to and communicate with a remote peer, including its endpoint (IP address and port), peer ID, and information about which pieces of the torrent it has available.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `AllowedEncryption` | `EncryptionTypes` | The encryption types allowed when connecting to this peer |
| `ConnectionUri` | `Uri` | The URI used to connect to this peer (for HTTP peers) |
| `EncryptionType` | `EncryptionType` | The encryption method being used with this peer |
| `IsSeeder` | `bool` | Whether this peer has all pieces of the torrent |
| `PeerId` | `BEncodedString` | The peer's unique identifier |
| `PeerSource` | `PeerSource` | How this peer was discovered (DHT, Tracker, etc.) |
| `Peer` | `IPEndPoint` | The endpoint (IP address and port) of this peer |
| `SupportsEncryption` | `bool` | Whether this peer supports encryption |
| `CleanedUpConnection` | `bool` | Whether the connection to this peer has been properly closed |
| `ConnectionAttempts` | `int` | Number of times a connection has been attempted to this peer |
| `DhtPort` | `int` | The port this peer is listening on for DHT messages |
| `IsChoking` | `bool` | Whether we are choking this peer |
| `IsInterested` | `bool` | Whether we are interested in pieces from this peer |
| `IsSeeder` | `bool` | Whether this peer has all pieces of the torrent |
| `LastConnectionAttempt` | `DateTime` | When the last connection attempt was made |
| `LastMessageReceived` | `DateTime` | When the last message was received from this peer |
| `LastMessageSent` | `DateTime` | When the last message was sent to this peer |
| `LocalPort` | `int` | Our local port used for the connection to this peer |
| `MaxPendingRequests` | `int` | Maximum number of piece requests that can be pending |
| `Monitor` | `ConnectionMonitor` | Tracks data transfer statistics for this peer |
| `PiecesReceived` | `int` | Number of pieces received from this peer |
| `AmChoking` | `bool` | Whether we are choking this peer |
| `AmInterested` | `bool` | Whether we are interested in pieces from this peer |
| `IsChoking` | `bool` | Whether the peer is choking us |
| `IsInterested` | `bool` | Whether the peer is interested in our pieces |
| `SupportsFastPeer` | `bool` | Whether this peer supports the Fast Peer extensions |
| `SupportsLTMessages` | `bool` | Whether this peer supports libtorrent extension messages |

## Methods

### Constructors

```csharp
public Peer(string peerId, Uri connectionUri)
```
Creates a new Peer with the specified peer ID and connection URI.

```csharp
public Peer(string peerId, IPEndPoint endpoint)
```
Creates a new Peer with the specified peer ID and endpoint.

```csharp
public Peer(IPEndPoint endpoint)
```
Creates a new Peer with the specified endpoint and a randomly generated peer ID.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `BitfieldLength` | `int` | Gets the length of the bitfield needed for this peer |
| `HasPiece(int pieceIndex)` | `bool` | Checks if the peer has the specified piece |
| `HasPieces(int startIndex, int endIndex)` | `bool` | Checks if the peer has all the pieces in the specified range |
| `Equals(object obj)` | `bool` | Determines whether this peer equals another object |
| `GetHashCode()` | `int` | Gets the hash code for this peer |
| `ToURI()` | `Uri` | Converts the peer to a URI |
| `ToString()` | `string` | Returns a string representation of this peer |

## Examples

### Creating and Inspecting Peers

```csharp
// Create a peer from an endpoint
IPEndPoint endpoint = new IPEndPoint(IPAddress.Parse("192.168.1.100"), 6881);
Peer peer = new Peer(endpoint);

// Display peer information
Console.WriteLine($"Peer: {peer}");
Console.WriteLine($"Endpoint: {peer.Peer}");
Console.WriteLine($"Peer ID: {peer.PeerId}");
Console.WriteLine($"Is Seeder: {peer.IsSeeder}");
```

### Checking for Available Pieces

```csharp
// Create a peer
Peer peer = new Peer(new IPEndPoint(IPAddress.Parse("192.168.1.100"), 6881));

// Check if the peer has specific pieces
bool hasPiece5 = peer.HasPiece(5);
Console.WriteLine($"Peer has piece 5: {hasPiece5}");

// Check if the peer has a range of pieces
bool hasRange = peer.HasPieces(10, 15);
Console.WriteLine($"Peer has pieces 10-15: {hasRange}");
```

### Working with Peer Connection Statistics

```csharp
// Get a peer from a torrent manager's peers
TorrentManager manager = /* ... */;
Peer peer = manager.Peers.ConnectedPeers.First();

// Display connection information
Console.WriteLine($"Last message received: {peer.LastMessageReceived}");
Console.WriteLine($"Connection attempts: {peer.ConnectionAttempts}");

// Show data transfer statistics
Console.WriteLine($"Download speed: {peer.Monitor.DownloadSpeed / 1024} KB/s");
Console.WriteLine($"Upload speed: {peer.Monitor.UploadSpeed / 1024} KB/s");
Console.WriteLine($"Data downloaded: {peer.Monitor.DataBytesDownloaded / (1024 * 1024)} MB");
Console.WriteLine($"Data uploaded: {peer.Monitor.DataBytesUploaded / (1024 * 1024)} MB");
```

### Understanding Peer State

```csharp
// Get a peer from a torrent manager
Peer peer = /* ... */;

// Check choking and interest state
if (peer.AmChoking && !peer.AmInterested)
{
    Console.WriteLine("We're choking this peer and not interested in their pieces");
}
else if (!peer.AmChoking && peer.AmInterested)
{
    Console.WriteLine("We're not choking this peer and interested in their pieces");
}

if (peer.IsChoking && !peer.IsInterested)
{
    Console.WriteLine("Peer is choking us and not interested in our pieces");
}
else if (!peer.IsChoking && peer.IsInterested)
{
    Console.WriteLine("Peer is not choking us and interested in our pieces");
}
```

## BitTorrent Peer Protocol

The BitTorrent peer protocol defines how clients communicate with each other to exchange pieces. Key concepts include:

1. **Choking**: A peer is "choking" another when it temporarily refuses to upload data
2. **Interest**: A peer is "interested" in another when the other peer has pieces it needs
3. **Peer ID**: A 20-byte string that uniquely identifies a peer (usually includes client name/version)
4. **Bitfield**: A bitmap indicating which pieces the peer has
5. **Have**: Messages sent when a peer completes a piece

The peer connection states (choking/interested) control the flow of data between peers. The "tit-for-tat" algorithm used by BitTorrent ensures peers that contribute more get better download rates.

## Remarks

- The `Peer` class primarily contains peer metadata and state
- Actual connection handling is managed by `PeerId` (despite the confusing name)
- `Peer` objects are typically created when peers are discovered from trackers, DHT, or PEX
- `PeerSource` indicates how the peer was discovered (tracker, DHT, PEX, web seeds, etc.)
- The choking algorithm periodically updates which peers are choked to optimize bandwidth
- Fast Peers extensions allow for more efficient piece requests
- libtorrent extension messages enable additional features like metadata exchange

## Related

- [PeerId](../client/PeerId.md)
- [TorrentManager](../client/TorrentManager.md)
- [ClientEngine](../client/ClientEngine.md)
- [ConnectionMonitor](../client/ConnectionMonitor.md)