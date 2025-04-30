# Piece Picking Strategies in MonoTorrent

This document describes the piece picking strategies available in MonoTorrent. Piece pickers determine which pieces of a torrent to request from peers and in what order.

## IPiecePicker Interface

The `IPiecePicker` interface is the foundation for all piece picking strategies in MonoTorrent.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

### Interface Definition

```csharp
public interface IPiecePicker
{
    void Initialise(BitField bitfield, TorrentFile[] files, IReadOnlyList<Piece> pieces);
    int PickPiece(PeerId id, BitField peerBitfield, List<PeerId> otherPeers);
    void CancelRequest(PeerId peer, int piece, int startOffset, int length);
    void RequestRejected(PeerId peer, int piece, int startOffset, int length);
    void ValidatePiece(PeerId peer, int pieceIndex, bool validationPassed);
    bool IsInteresting(BitField bitfield);
}
```

### Key Methods

- **Initialise**: Sets up the piece picker with the torrent's bitfield, files, and pieces
- **PickPiece**: Selects a piece to request from a peer
- **CancelRequest**: Cancels a piece request
- **RequestRejected**: Handles a rejected piece request
- **ValidatePiece**: Updates internal state when a piece is validated
- **IsInteresting**: Determines if a peer has pieces that are interesting to download

## StandardPicker

The `StandardPicker` is the base implementation used by most other strategies.

**Namespace**: `MonoTorrent.PiecePicking`

**Assembly**: `MonoTorrent.Client.dll`

### Class Definition

```csharp
public class StandardPicker : IPiecePicker
```

### Description

The `StandardPicker` provides the basic functionality for piece picking. It:

- Maintains a list of available pieces
- Tracks which pieces have been requested but not yet received
- Ensures pieces are requested in a sequential manner (within a piece)
- Handles request cancellation and rejection
- Supports continuing partial downloads

This picker doesn't specify any particular order for selecting pieces - it defers that decision to derived classes. However, it does ensure that once a piece is started, blocks within that piece are requested sequentially.

### Example

```csharp
// Create a standard picker (typically you'd use a derived class instead)
var picker = new StandardPicker();

// The picker would be initialized by the TorrentManager
picker.Initialise(torrentManager.Bitfield, torrentManager.Torrent.Files, torrentManager.Pieces);

// The TorrentManager uses the picker to select pieces to request
int pieceIndex = picker.PickPiece(peerId, peerId.BitField, torrentManager.Peers.ConnectedPeers);
if (pieceIndex != -1)
{
    // Request the selected piece
    var request = new RequestMessage(pieceIndex, 0, Piece.BlockSize);
    peerId.Enqueue(request);
}
```

## RarestFirstPicker

The `RarestFirstPicker` selects the rarest pieces first to improve piece distribution in the swarm.

**Namespace**: `MonoTorrent.PiecePicking`

**Assembly**: `MonoTorrent.Client.dll`

### Class Definition

```csharp
public class RarestFirstPicker : IPiecePicker
```

### Description

The `RarestFirstPicker` implements the "rarest first" piece picking strategy, which:

- Prioritizes pieces that are least common among peers
- Maintains a list of pieces sorted by rarity
- Updates rarity calculations as peers connect and disconnect
- Helps ensure rare pieces get distributed more quickly
- Is the default strategy used by MonoTorrent

This strategy is particularly effective for ensuring good distribution of pieces across the swarm and preventing the "last piece problem" where rare pieces can be difficult to find.

### Example

```csharp
// Create a rarest first picker
var rarestPicker = new RarestFirstPicker();

// Initialize the picker
rarestPicker.Initialise(torrentManager.Bitfield, torrentManager.Torrent.Files, torrentManager.Pieces);

// When a new peer connects, the picker updates its rarity calculations
peer.BitfieldUpdated += (sender, args) => 
{
    // The picker will automatically update rarity calculations
    bool isInteresting = rarestPicker.IsInteresting(peer.BitField);
    Console.WriteLine($"Peer has {(isInteresting ? "interesting" : "no interesting")} pieces");
};
```

## RandomisedPicker

The `RandomisedPicker` selects pieces in a random order, which is useful for the initial pieces of a download.

**Namespace**: `MonoTorrent.PiecePicking`

**Assembly**: `MonoTorrent.Client.dll`

### Class Definition

```csharp
public class RandomisedPicker : IPiecePicker
```

### Description

The `RandomisedPicker` chooses pieces randomly, which:

- Helps to quickly get different pieces from different parts of the torrent
- Allows the client to start sharing unique pieces sooner
- Is often used for the first few pieces, before switching to a more strategic picker

This picker is typically used at the beginning of a download to quickly get some pieces that can be shared with other peers, after which a strategy like rarest first is used.

### Example

```csharp
// Create a randomized picker for the first few pieces
var randomPicker = new RandomisedPicker();

// Initialize the picker
randomPicker.Initialise(torrentManager.Bitfield, torrentManager.Torrent.Files, torrentManager.Pieces);

// After downloading some pieces (e.g., 4 pieces), switch to rarest first
if (torrentManager.Bitfield.TrueCount >= 4)
{
    // Switch to rarest first picker
    // (In practice, this would be handled automatically by MonoTorrent)
}
```

## PriorityPicker

The `PriorityPicker` selects pieces based on file priorities set by the user.

**Namespace**: `MonoTorrent.PiecePicking`

**Assembly**: `MonoTorrent.Client.dll`

### Class Definition

```csharp
public class PriorityPicker : IPiecePicker
```

### Description

The `PriorityPicker` allows selective downloading by prioritizing pieces based on file priorities:

- Files can be set to `High`, `Normal`, `Low`, or `DoNotDownload` priority
- Pieces belonging to higher priority files are downloaded first
- Respects the underlying picking strategy for pieces of the same priority
- Allows users to download specific files before others

This picker is essential for implementing selective downloading and is typically used as a wrapper around another picker like `RarestFirstPicker`.

### Example

```csharp
// Set file priorities
foreach (var file in torrentManager.Files)
{
    // Skip .nfo files
    if (file.Path.EndsWith(".nfo", StringComparison.OrdinalIgnoreCase))
    {
        file.Priority = Priority.DoNotDownload;
    }
    // Prioritize video files
    else if (file.Path.EndsWith(".mp4", StringComparison.OrdinalIgnoreCase) ||
             file.Path.EndsWith(".mkv", StringComparison.OrdinalIgnoreCase))
    {
        file.Priority = Priority.Highest;
    }
    // Other files get normal priority
    else
    {
        file.Priority = Priority.Normal;
    }
}

// MonoTorrent automatically uses a PriorityPicker when file priorities are set
// But if you were creating one manually, it would look like:
var basePicker = new RarestFirstPicker();
var priorityPicker = new PriorityPicker(basePicker);
priorityPicker.Initialise(torrentManager.Bitfield, torrentManager.Torrent.Files, torrentManager.Pieces);
```

## EndGamePicker

The `EndGamePicker` is used when a torrent is nearly complete to speed up completion.

**Namespace**: `MonoTorrent.PiecePicking`

**Assembly**: `MonoTorrent.Client.dll`

### Class Definition

```csharp
public class EndGamePicker : IPiecePicker
```

### Description

The `EndGamePicker` implements a special strategy for the end of a download:

- Activates when only a few pieces remain to be downloaded
- Requests the same pieces from multiple peers simultaneously
- Cancels redundant requests when a piece is received
- Helps overcome issues with peers that are slow or unresponsive

This picker is crucial for preventing the "last piece problem" where a download can stall when waiting for the final few pieces.

### Example

```csharp
// In practice, MonoTorrent automatically switches to EndGamePicker
// when appropriate, but if implementing manually:

// Check if we should switch to endgame mode
int remainingPieces = torrentManager.Bitfield.Length - torrentManager.Bitfield.TrueCount;
if (remainingPieces <= 5) // Example threshold
{
    // Switch to endgame mode
    var basePicker = new RarestFirstPicker();
    var endGamePicker = new EndGamePicker(basePicker);
    endGamePicker.Initialise(torrentManager.Bitfield, torrentManager.Torrent.Files, torrentManager.Pieces);
    
    Console.WriteLine("Entered endgame mode with " + remainingPieces + " pieces remaining");
}
```

## FastResumePicker

The `FastResumePicker` restores the download state after a restart.

**Namespace**: `MonoTorrent.PiecePicking`

**Assembly**: `MonoTorrent.Client.dll`

### Class Definition

```csharp
public class FastResumePicker : IPiecePicker
```

### Description

The `FastResumePicker` is a special picker used when resuming a previously started download:

- Restores the state of partially downloaded pieces
- Ensures that pieces that were in progress before shutdown are prioritized
- Helps continue downloads efficiently after a client restart
- Is automatically used when fast resume data is loaded

This picker is essential for implementing the fast resume feature, which allows downloads to continue efficiently after a client restart.

### Example

```csharp
// In practice, this is handled automatically when loading fast resume data:
byte[] resumeData = File.ReadAllBytes("fastresume.data");
await torrentManager.LoadFastResumeAsync(resumeData);

// MonoTorrent will automatically use a FastResumePicker to restore the download state
```

## StreamingPicker

The `StreamingPicker` prioritizes pieces in sequential order for streaming media.

**Namespace**: `MonoTorrent.Streaming`

**Assembly**: `MonoTorrent.Streaming.dll`

### Class Definition

```csharp
public class StreamingPicker : IPiecePicker
```

### Description

The `StreamingPicker` implements a strategy optimized for streaming media:

- Downloads pieces sequentially from a specified starting position
- Maintains a buffer of pieces ahead of the playback position
- Dynamically adjusts when the read position changes (seeking)
- Balances sequential downloading with maintaining good swarm health

This picker is crucial for implementing streaming functionality where media playback can begin before the entire file is downloaded.

### Example

```csharp
// Create a streaming manager
var manager = await engine.AddStreamingAsync(torrentPath, downloadPath);

// The StreamingPicker is automatically set up when creating a streaming torrent
// Get a stream for a specific file
using var stream = await manager.StreamProvider.CreateStreamAsync(manager.Files[0]);

// As you read from the stream, the StreamingPicker ensures that
// pieces are downloaded in the appropriate order
byte[] buffer = new byte[4096];
int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);

// If you seek in the stream, the picker adjusts its priorities
stream.Position = 1000000; // Example seek
bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
```

## Implementing a Custom Picker

You can implement custom picking strategies by implementing the `IPiecePicker` interface or by extending existing pickers.

### Example: Implementing a Simple Sequential Picker

```csharp
public class SequentialPicker : IPiecePicker
{
    private BitField bitfield;
    private IReadOnlyList<Piece> pieces;
    private readonly StandardPicker standardPicker;
    
    public SequentialPicker()
    {
        standardPicker = new StandardPicker();
    }
    
    public void Initialise(BitField bitfield, TorrentFile[] files, IReadOnlyList<Piece> pieces)
    {
        this.bitfield = bitfield;
        this.pieces = pieces;
        standardPicker.Initialise(bitfield, files, pieces);
    }
    
    public int PickPiece(PeerId id, BitField peerBitfield, List<PeerId> otherPeers)
    {
        // Check if there's a piece we're already downloading
        int piece = standardPicker.PickPiece(id, peerBitfield, otherPeers);
        if (piece >= 0)
            return piece;
        
        // Otherwise, pick the first piece we need that the peer has
        for (int i = 0; i < bitfield.Length; i++)
        {
            if (!bitfield[i] && peerBitfield[i])
                return i;
        }
        
        return -1;
    }
    
    public void CancelRequest(PeerId peer, int piece, int startOffset, int length)
    {
        standardPicker.CancelRequest(peer, piece, startOffset, length);
    }
    
    public void RequestRejected(PeerId peer, int piece, int startOffset, int length)
    {
        standardPicker.RequestRejected(peer, piece, startOffset, length);
    }
    
    public void ValidatePiece(PeerId peer, int pieceIndex, bool validationPassed)
    {
        standardPicker.ValidatePiece(peer, pieceIndex, validationPassed);
    }
    
    public bool IsInteresting(BitField bitfield)
    {
        return !this.bitfield.AllTrue && (bitfield & ~this.bitfield).Length > 0;
    }
}
```

### Example: Using a Chain of Pickers

```csharp
// Create a chain of pickers for a sophisticated strategy
public IPiecePicker CreateAdvancedPicker(BitField bitfield, TorrentFile[] files, IReadOnlyList<Piece> pieces)
{
    // Base picker - implements core functionality
    var basePicker = new StandardPicker();
    
    // Add rarest first strategy
    var rarestPicker = new RarestFirstPicker(basePicker);
    
    // Add file priority support
    var priorityPicker = new PriorityPicker(rarestPicker);
    
    // Initialize the picker chain
    priorityPicker.Initialise(bitfield, files, pieces);
    
    return priorityPicker;
}
```

## Conclusion

Piece picking strategies are a crucial part of BitTorrent clients that significantly impact download performance, media streaming capability, and user experience. MonoTorrent provides a comprehensive set of picking strategies through a flexible, extensible interface system that can be customized for various use cases.

In most cases, MonoTorrent automatically selects and configures the appropriate pickers based on the current state of the download and user settings, but understanding the different strategies can help when implementing custom behavior or optimizing for specific scenarios.