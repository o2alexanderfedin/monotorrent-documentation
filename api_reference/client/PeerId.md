# PeerId

**Namespace**: `MonoTorrent.Client`

The `PeerId` class represents an active connection to a remote BitTorrent peer, managing all communication and state.

## Overview

Despite its name, the `PeerId` class represents much more than just an identifier - it manages an active connection to a peer, including the message processing, data transfer, and protocol state. While the `Peer` class contains static information about a peer, the `PeerId` class handles the dynamic connection and communication with that peer.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `AmChoking` | `bool` | Whether we are choking the peer |
| `AmInterested` | `bool` | Whether we are interested in pieces from the peer |
| `AmRequestingPiecesCount` | `int` | The number of pieces we are currently requesting |
| `BitField` | `BitField` | The pieces the peer has |
| `ClientApp` | `Software` | The client software the peer is using |
| `Connection` | `IPeerConnection` | The connection to the peer |
| `ConnectionManager` | `ConnectionManager` | The connection manager for this connection |
| `Dequeue` | `bool` | Whether message dequeueing is allowed |
| `EncryptionType` | `EncryptionType` | The encryption type used with this peer |
| `ExtensionSupports` | `ExtensionSupports` | The protocol extensions this peer supports |
| `HashedPiece` | `bool` | Whether we have a piece hash to send to the peer |
| `IsChoking` | `bool` | Whether the peer is choking us |
| `IsInterested` | `bool` | Whether the peer is interested in our pieces |
| `IsSeeder` | `bool` | Whether the peer has all pieces |
| `MessageQueue` | `MessageQueue` | Queue of messages to send to the peer |
| `Monitor` | `ConnectionMonitor` | Monitors data transfer with this peer |
| `Peer` | `Peer` | The peer this connection is established with |
| `PiecesSent` | `int` | Number of pieces sent to the peer |
| `SupportsFastPeer` | `bool` | Whether the peer supports the Fast Peer extensions |
| `SupportsLTMessages` | `bool` | Whether the peer supports libtorrent extension messages |
| `TorrentManager` | `TorrentManager` | The torrent manager for this connection |

## Methods

### Constructors

The `PeerId` class has internal constructors and is typically instantiated by the MonoTorrent engine, not directly by users.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `AddConnection(IConnection connection)` | `void` | Adds a connection to this peer |
| `AmAllowedFastPieces()` | `IList<int>` | Gets the pieces we're allowed to request while choked |
| `CloseConnection()` | `void` | Closes the connection to the peer |
| `EnqueueAt(PeerMessage message, int index)` | `void` | Enqueues a message at the specified index |
| `EnqueueMessage(PeerMessage message)` | `void` | Enqueues a message to be sent to the peer |
| `Equals(object obj)` | `bool` | Determines if this PeerId equals another object |
| `GetHashCode()` | `int` | Gets the hash code for this peer |
| `HasPiece(int pieceIndex)` | `bool` | Checks if the peer has the specified piece |
| `HasPieces(int startIndex, int endIndex)` | `bool` | Checks if the peer has all pieces in the range |
| `ReceivedBlock()` | `void` | Called when a block is received from this peer |
| `TorrentManager.PieceManager.ReceivedRejectedRequest()` | `void` | Called when a request is rejected by this peer |
| `SendHaveMessageIfNeeded()` | `void` | Sends "Have" messages for completed pieces if needed |
| `SentBlock()` | `void` | Called when a block is sent to this peer |
| `SentCancelMessage()` | `void` | Called when a cancel message is sent to this peer |
| `SentRequestMessage()` | `void` | Called when a request message is sent to this peer |
| `StartEncryption()` | `void` | Starts the encryption handshake with this peer |
| `ToString()` | `string` | Returns a string representation of this peer |
| `UpdateAmInterested()` | `bool` | Updates whether we're interested in this peer based on available pieces |

## Examples

### Working with Active Peer Connections

```csharp
// Get a PeerId from a torrent manager's active connections
TorrentManager manager = /* ... */;
PeerId peerId = manager.Peers.ConnectedPeers.FirstOrDefault();

if (peerId != null)
{
    // Display connection information
    Console.WriteLine($"Connected to peer: {peerId.Peer.Peer}");
    Console.WriteLine($"Client: {peerId.ClientApp.Client}");
    Console.WriteLine($"Protocol: {peerId.ClientApp.Protocol}");
    
    // Check connection state
    Console.WriteLine($"Am Choking: {peerId.AmChoking}");
    Console.WriteLine($"Am Interested: {peerId.AmInterested}");
    Console.WriteLine($"Is Choking: {peerId.IsChoking}");
    Console.WriteLine($"Is Interested: {peerId.IsInterested}");
    
    // Check data transfer stats
    Console.WriteLine($"Download speed: {peerId.Monitor.DownloadSpeed / 1024} KB/s");
    Console.WriteLine($"Upload speed: {peerId.Monitor.UploadSpeed / 1024} KB/s");
}
```

### Sending Messages to a Peer

```csharp
// Get a PeerId from a torrent manager
PeerId peerId = /* ... */;

// Send an "Interested" message to the peer
peerId.EnqueueMessage(new InterestedMessage());

// Request a piece if the peer is not choking us and has the piece we want
int pieceIndex = 42;
if (!peerId.IsChoking && peerId.HasPiece(pieceIndex))
{
    // Request three blocks from the piece (each 16KB)
    peerId.EnqueueMessage(new RequestMessage(pieceIndex, 0, 16384));
    peerId.EnqueueMessage(new RequestMessage(pieceIndex, 16384, 16384));
    peerId.EnqueueMessage(new RequestMessage(pieceIndex, 32768, 16384));
}
```

### Examining Peer Capabilities

```csharp
// Get a PeerId from a torrent manager
PeerId peerId = /* ... */;

// Check supported extensions
if (peerId.SupportsFastPeer)
{
    Console.WriteLine("Peer supports Fast Peer extensions");
    
    // Get pieces we can request even when choked
    var allowedFastPieces = peerId.AmAllowedFastPieces();
    Console.WriteLine($"We can request {allowedFastPieces.Count} pieces when choked");
}

if (peerId.SupportsLTMessages)
{
    Console.WriteLine("Peer supports libtorrent extension messages");
    
    // Check for specific extensions
    if (peerId.ExtensionSupports.Supports(PeerExchangeMessage.Support))
    {
        Console.WriteLine("Peer supports Peer Exchange (PEX)");
    }
    
    if (peerId.ExtensionSupports.Supports(MetadataMessage.Support))
    {
        Console.WriteLine("Peer supports Metadata Exchange");
    }
}
```

### Monitoring Piece Availability

```csharp
// Get a PeerId from a torrent manager
PeerId peerId = /* ... */;
TorrentManager manager = peerId.TorrentManager;

// Count how many pieces this peer has that we need
int neededPieces = 0;
for (int i = 0; i < manager.Torrent.Pieces.Count; i++)
{
    if (peerId.HasPiece(i) && !manager.Bitfield[i])
    {
        neededPieces++;
    }
}

Console.WriteLine($"Peer has {neededPieces} pieces that we need");

// Check if peer has a specific range we need
int startPiece = 50;
int endPiece = 60;
bool hasRange = peerId.HasPieces(startPiece, endPiece);
Console.WriteLine($"Peer has pieces {startPiece}-{endPiece}: {hasRange}");
```

## BitTorrent Protocol State

Each peer connection maintains state to handle the BitTorrent protocol:

1. **Choking State**:
   - `AmChoking`: Whether we are refusing to upload to the peer (default: true)
   - `IsChoking`: Whether the peer is refusing to upload to us (default: true)

2. **Interest State**:
   - `AmInterested`: Whether we want pieces from the peer (default: false)
   - `IsInterested`: Whether the peer wants pieces from us (default: false)

3. **Message Flow**:
   - The `MessageQueue` handles outgoing messages
   - `EnqueueMessage` adds messages to the queue
   - MonoTorrent automatically processes and sends these messages

4. **Piece Management**:
   - `BitField` tracks which pieces the peer has
   - `HasPiece` checks if the peer has a specific piece
   - `UpdateAmInterested` recalculates interest based on peer pieces

## Remarks

- The `PeerId` class is the core of peer communication in MonoTorrent
- It is managed by the `TorrentManager` and should not be created directly
- The unusual name comes from early BitTorrent specifications
- Despite the name confusion, `PeerId` objects represent connections, while `Peer` objects represent connection metadata
- When a peer completes a piece, we notify them with a "Have" message via `SendHaveMessageIfNeeded()`
- The choking algorithm periodically cycles through peers, updating `AmChoking` to optimize bandwidth allocation
- Fast Peer extensions allow for optimized piece requests and transfers

## Related

- [Peer](../client/Peer.md)
- [ConnectionManager](../client/ConnectionManager.md)
- [TorrentManager](../client/TorrentManager.md)
- [BitField](../client/BitField.md)