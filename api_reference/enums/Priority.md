# Priority

**Namespace**: `MonoTorrent`

The `Priority` enum defines the download priority levels for files within a torrent.

## Overview

The `Priority` enum allows users to control which files are downloaded first and which files are skipped entirely. When downloading a torrent with multiple files, setting priorities helps users get the most important files first while potentially skipping unwanted content.

## Enum Values

| Value | Description |
|-------|-------------|
| `DoNotDownload` | File will not be downloaded |
| `Lowest` | File has the lowest download priority |
| `Low` | File has low download priority |
| `Normal` | File has normal download priority (default) |
| `High` | File has high download priority |
| `Highest` | File has the highest download priority |

## Usage

### Setting File Priorities

The `Priority` enum is typically used with the `TorrentFile.Priority` property to control the download priority of individual files within a torrent:

```csharp
// Load a torrent
Torrent torrent = Torrent.Load("example.torrent");

// Set priorities for different file types
foreach (TorrentFile file in torrent.Files)
{
    // Set priority based on file extension
    if (file.Path.EndsWith(".mp4") || file.Path.EndsWith(".mkv"))
    {
        // Download video files first
        file.Priority = Priority.Highest;
    }
    else if (file.Path.EndsWith(".srt") || file.Path.EndsWith(".sub"))
    {
        // Download subtitle files second
        file.Priority = Priority.High;
    }
    else if (file.Path.EndsWith(".txt") || file.Path.EndsWith(".nfo"))
    {
        // Download documentation last
        file.Priority = Priority.Lowest;
    }
    else if (file.Path.EndsWith(".sample.mp4"))
    {
        // Skip sample videos
        file.Priority = Priority.DoNotDownload;
    }
    else
    {
        // Normal priority for everything else
        file.Priority = Priority.Normal;
    }
}
```

### Selective Downloading

To completely skip downloading certain files, set their priority to `Priority.DoNotDownload`:

```csharp
// Skip all files except video files
foreach (TorrentFile file in torrent.Files)
{
    if (file.Path.EndsWith(".mp4") || file.Path.EndsWith(".mkv"))
    {
        file.Priority = Priority.Normal;
    }
    else
    {
        file.Priority = Priority.DoNotDownload;
    }
}
```

### Changing Priorities During Download

Priorities can be changed while a download is in progress:

```csharp
// Assume we have a TorrentManager instance
TorrentManager manager = /* ... */;

// Find a specific file
TorrentFile file = manager.Torrent.Files.FirstOrDefault(f => f.Path.Contains("important.mp4"));

if (file != null)
{
    // Increase priority for this file
    file.Priority = Priority.Highest;
    
    // File priority changes take effect immediately
    Console.WriteLine($"Priority changed for {file.Path}");
}
```

## Effect on Download Behavior

The exact behavior depends on the piece picking algorithm in use, but generally:

1. Pieces from higher priority files are requested before pieces from lower priority files
2. All pieces from a `Priority.Highest` file will be requested before any pieces from a `Priority.High` file
3. Files with the same priority level are typically downloaded in the order they appear in the torrent
4. Files marked as `Priority.DoNotDownload` are completely skipped and will show 0% progress
5. If a piece contains data for files with different priorities, the highest priority determines the piece's priority

## Remarks

- The default priority for all files is `Priority.Normal`
- Setting a file to `Priority.DoNotDownload` does not delete the file if it was already downloaded
- Changing a file from `Priority.DoNotDownload` to any other priority will resume downloading that file
- Priority settings affect piece selection but do not guarantee a strict download order due to the peer-to-peer nature of BitTorrent
- Higher priority files might still download slowly if the pieces are not available from peers
- When streaming a torrent, pieces needed immediately are automatically given the highest priority regardless of file priority

## Related

- [TorrentFile](../common/TorrentFile.md)
- [TorrentManager](../client/TorrentManager.md)
- [Torrent](../common/Torrent.md)