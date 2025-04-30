# Advanced Usage

This document covers more complex scenarios and advanced features of MonoTorrent.

## Contents

- [Custom Torrent Modes](#custom-torrent-modes)
- [Fast Resume Data](#fast-resume-data)
- [Streaming](#streaming)
- [Rate Limiting](#rate-limiting)
- [Event Handling](#event-handling)
- [Working with Metadata Mode](#working-with-metadata-mode)

## Custom Torrent Modes

MonoTorrent allows you to create custom modes to control the behavior of torrents. This provides ultimate flexibility for specialized use cases.

```csharp
public class MyCustomMode : Mode
{
    TorrentManager Manager { get; }

    public MyCustomMode(TorrentManager manager)
        : base(manager)
    {
        Manager = manager;
    }

    public override void Tick(int counter)
    {
        // Custom processing logic here
    }

    public override void HandlePeerConnected(PeerId id, Direction direction)
    {
        // Custom peer connection handling
    }

    // Override other methods as needed
}

// To use the custom mode:
torrentManager.Mode = new MyCustomMode(torrentManager);
```

## Fast Resume Data

Fast resume data allows MonoTorrent to quickly restart torrents without performing hash checks. This significantly improves startup time for large torrents.

```csharp
// Save fast resume data
await engine.SaveFastResumeAsync();

// Load fast resume data
await engine.LoadFastResumeAsync();
```

## Streaming

MonoTorrent supports streaming of torrent content while it's still downloading:

```csharp
// Create a stream provider
var streamProvider = new StreamProvider(torrentManager);

// Get a stream for a specific file
using (var stream = await streamProvider.CreateStreamAsync(torrentManager.Files[0]))
{
    // Use the stream - data will be prioritized as needed
    // The stream can be used like any other Stream object
}
```

## Rate Limiting

Control bandwidth usage with MonoTorrent's rate limiting features:

```csharp
// Set global rate limits
engineSettings.MaximumDownloadRate = 1024 * 1024; // 1 MB/s
engineSettings.MaximumUploadRate = 512 * 1024;    // 512 KB/s

// Set per-torrent rate limits
torrentSettings.MaximumDownloadRate = 512 * 1024; // 512 KB/s
torrentSettings.MaximumUploadRate = 256 * 1024;   // 256 KB/s
```

## Event Handling

MonoTorrent provides a rich event model to track progress and respond to torrent state changes:

```csharp
// Subscribe to torrent state changes
torrentManager.TorrentStateChanged += (sender, e) => {
    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
};

// Track download progress
torrentManager.PieceHashed += (sender, e) => {
    Console.WriteLine($"Piece {e.PieceIndex} hashed. Result: {e.HashPassed}");
};

// Handle peer connections
engine.PeerConnected += (sender, e) => {
    Console.WriteLine($"Connected to peer: {e.Peer.ConnectionUri}");
};
```

## Working with Metadata Mode

When dealing with magnet links, you can use Metadata Mode to download just the torrent metadata:

```csharp
// Add a magnet link
var magnetLink = new MagnetLink("magnet:?xt=urn:btih:...");
var torrentManager = await engine.AddAsync(magnetLink, "/path/to/downloads");

// Start the download
await torrentManager.StartAsync();

// Wait for metadata to be downloaded
while (!torrentManager.HasMetadata)
{
    await Task.Delay(500);
    Console.WriteLine("Waiting for metadata...");
}

Console.WriteLine("Metadata download complete!");
```

For more advanced examples, check the [Examples](../examples/README.md) section.