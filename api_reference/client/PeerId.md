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

### Implementing a Peer Selection Strategy

```csharp
// Get all connected peers from a torrent manager
TorrentManager manager = /* ... */;
List<PeerId> connectedPeers = manager.Peers.ConnectedPeers.ToList();

// Sort peers by download speed
var fastestPeers = connectedPeers
    .OrderByDescending(p => p.Monitor.DownloadSpeed)
    .ToList();

Console.WriteLine("Top 5 fastest peers:");
foreach (var peer in fastestPeers.Take(5))
{
    Console.WriteLine($"- {peer.Peer.Peer}: {peer.Monitor.DownloadSpeed / 1024} KB/s");
}

// Find peers that are unchoked and interested in our data (potential uploaders)
var uploadingPeers = connectedPeers
    .Where(p => !p.AmChoking && p.IsInterested)
    .ToList();

Console.WriteLine($"Currently uploading to {uploadingPeers.Count} peers");

// Find peers that are not choking us and have pieces we need (potential downloaders)
var downloadingPeers = connectedPeers
    .Where(p => !p.IsChoking && p.AmInterested)
    .ToList();

Console.WriteLine($"Currently downloading from {downloadingPeers.Count} peers");

// Calculate the overall health of the swarm
double averageAvailability = 0;
if (manager.Bitfield.Length > 0)
{
    int[] pieceCounts = new int[manager.Bitfield.Length];
    
    // Count availability of each piece
    foreach (var peer in connectedPeers)
    {
        for (int i = 0; i < manager.Bitfield.Length; i++)
        {
            if (peer.HasPiece(i))
                pieceCounts[i]++;
        }
    }
    
    // Calculate average piece availability
    averageAvailability = pieceCounts.Average();
}

Console.WriteLine($"Average piece availability: {averageAvailability:F2} copies");
```

### Implementing a Custom Choke/Unchoke Algorithm

```csharp
// This example shows how you might implement a custom choke/unchoke algorithm
// Note: In actual MonoTorrent code, this is handled internally

// Get the torrent manager and its connected peers
TorrentManager manager = /* ... */;
List<PeerId> connectedPeers = manager.Peers.ConnectedPeers.ToList();

// Step 1: Sort peers by their upload rate to us (to implement tit-for-tat)
var sortedPeers = connectedPeers
    .OrderByDescending(p => p.Monitor.DownloadSpeed)
    .ToList();

// Step 2: Determine how many upload slots we have available
int uploadSlots = manager.Settings.UploadSlots;
Console.WriteLine($"We have {uploadSlots} upload slots available");

// Step 3: Unchoke the best uploaders (tit-for-tat)
int unchokedCount = 0;
foreach (var peer in sortedPeers)
{
    bool shouldUnchoke = unchokedCount < uploadSlots;
    
    // If we're changing the peer's choke state, send the appropriate message
    if (peer.AmChoking && shouldUnchoke)
    {
        // Unchoke this peer
        Console.WriteLine($"Unchoking peer {peer.Peer.Peer} (upload: {peer.Monitor.DownloadSpeed / 1024} KB/s)");
        peer.EnqueueMessage(new UnchokeMessage());
        unchokedCount++;
    }
    else if (!peer.AmChoking && !shouldUnchoke)
    {
        // Choke this peer
        Console.WriteLine($"Choking peer {peer.Peer.Peer}");
        peer.EnqueueMessage(new ChokeMessage());
    }
}

// Step 4: Optimistic unchoke - randomly unchoke one more peer
// This helps discover faster peers and prevent swarm deadlock
if (sortedPeers.Count > uploadSlots)
{
    // Get list of choked peers that are interested in our data
    var chokedInterestedPeers = sortedPeers
        .Skip(uploadSlots)
        .Where(p => p.AmChoking && p.IsInterested)
        .ToList();
    
    if (chokedInterestedPeers.Count > 0)
    {
        // Randomly choose one for optimistic unchoking
        Random random = new Random();
        int index = random.Next(chokedInterestedPeers.Count);
        PeerId luckyPeer = chokedInterestedPeers[index];
        
        Console.WriteLine($"Optimistically unchoking peer {luckyPeer.Peer.Peer}");
        luckyPeer.EnqueueMessage(new UnchokeMessage());
    }
}
```

### Handling Metadata Exchange with a Peer

```csharp
// This example demonstrates how you might handle metadata exchange with a peer
// that supports the extension protocol (for magnet links)

// Get a PeerId from a torrent manager
PeerId peerId = /* ... */;
TorrentManager manager = peerId.TorrentManager;

// Check if we need metadata and the peer supports the metadata exchange extension
if (manager.MetadataComplete == false && 
    peerId.SupportsLTMessages && 
    peerId.ExtensionSupports.Supports(MetadataMessage.Support))
{
    Console.WriteLine("Peer supports metadata exchange! Requesting metadata...");
    
    // In a real implementation, MonoTorrent handles this automatically
    // This is just a demonstration of the concept
    
    // 1. First, determine the size of the metadata
    int metadataSize = 0; // This would be obtained from the handshake
    
    // 2. Calculate how many pieces the metadata has
    int pieceLength = 16384; // Standard metadata piece length
    int pieceCount = (metadataSize + pieceLength - 1) / pieceLength;
    
    // 3. Request each piece of the metadata
    for (int i = 0; i < pieceCount; i++)
    {
        Console.WriteLine($"Requesting metadata piece {i}/{pieceCount-1}");
        
        // In a real implementation, you'd use the extension message system
        // to send a proper metadata request
        //peerId.EnqueueMessage(new MetadataMessage(i));
    }
    
    // 4. When all pieces are received, they would be assembled and
    // used to create a Torrent object
    
    Console.WriteLine("In actual MonoTorrent implementation, metadata exchange is automatic");
}
else if (manager.MetadataComplete == false)
{
    Console.WriteLine("Peer does not support metadata exchange, cannot download via magnet link");
}
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