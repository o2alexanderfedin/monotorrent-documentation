# TorrentFile

**Namespace**: `MonoTorrent`

The `TorrentFile` class represents a single file within a torrent, containing information about the file's location, size, and download properties.

## Overview

In BitTorrent, a torrent can contain one or more files. The `TorrentFile` class provides detailed information about each individual file, including its path relative to the download directory, its length, download priority, and progress information. It implements the `ITorrentFile` interface, which is part of the core API for accessing file information within torrents.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `DownloadCompleted` | `bool` | Whether the file has been completely downloaded |
| `FullPath` | `string` | The absolute path where the file will be saved |
| `Length` | `long` | Size of the file in bytes |
| `Padding` | `bool` | Whether this is a padding file (BitTorrent v2) |
| `Path` | `string` | The relative path of the file within the torrent |
| `Priority` | `Priority` | The download priority for this file |
| `StartPieceIndex` | `int` | The index of the first piece that contains data for this file |
| `EndPieceIndex` | `int` | The index of the last piece that contains data for this file |
| `BitField` | `BitField` | BitField representing which pieces of this file have been downloaded |
| `BytesDownloaded` | `long` | The number of bytes downloaded for this file |
| `MD5` | `byte[]` | MD5 hash of the file (if available in the torrent metadata) |
| `Sha1` | `byte[]` | SHA1 hash of the file (BitTorrent v2, if available) |
| `Sha256` | `byte[]` | SHA256 hash of the file (BitTorrent v2, if available) |

## Methods

### Constructors

`TorrentFile` instances are typically created by the `Torrent` class when loading a .torrent file and are not usually instantiated directly by application code.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `GetBytesCompleted(BitField bitfield)` | `long` | Calculates the number of bytes completed for this file based on the provided BitField |
| `GetSelector()` | `RangeCollection` | Gets a RangeCollection representing the pieces that contain this file |

## Examples

### Listing Files in a Torrent

```csharp
// Load a torrent
Torrent torrent = Torrent.Load("example.torrent");

// List all files
foreach (TorrentFile file in torrent.Files)
{
    Console.WriteLine($"Path: {file.Path}");
    Console.WriteLine($"Size: {file.Length} bytes");
    Console.WriteLine($"Priority: {file.Priority}");
    Console.WriteLine($"Piece Range: {file.StartPieceIndex} to {file.EndPieceIndex}");
    Console.WriteLine();
}
```

### Setting File Download Priorities

```csharp
// Load a torrent
Torrent torrent = Torrent.Load("example.torrent");

// Find a specific file
TorrentFile videoFile = torrent.Files.FirstOrDefault(f => f.Path.EndsWith(".mp4"));
if (videoFile != null)
{
    // Set high priority for video file
    videoFile.Priority = Priority.Highest;
}

// Set low priority for all other files
foreach (TorrentFile file in torrent.Files.Where(f => f != videoFile))
{
    file.Priority = Priority.Lowest;
}

// Create a torrent manager with the prioritized files
ClientEngine engine = new ClientEngine();
TorrentManager manager = new TorrentManager(torrent, downloadDirectory, torrentSettings);
await engine.RegisterAsync(manager);
```

### Checking Download Progress for Individual Files

```csharp
// Assume we have a TorrentManager instance
TorrentManager manager = /* ... */;

// Get progress information for each file
foreach (TorrentFile file in manager.Torrent.Files)
{
    double percentComplete = (double)file.BytesDownloaded / file.Length * 100;
    Console.WriteLine($"{file.Path}: {percentComplete:F2}% complete");
    
    if (file.DownloadCompleted)
    {
        Console.WriteLine("  Download complete!");
    }
    else
    {
        Console.WriteLine($"  Downloaded: {file.BytesDownloaded} / {file.Length} bytes");
    }
}
```

## File Mapping in BitTorrent

In a BitTorrent torrent, files are split into fixed-size pieces for downloading. A single piece may contain data from multiple files, and a file may span multiple pieces. The `StartPieceIndex` and `EndPieceIndex` properties help identify which pieces contain data for a particular file.

For example, in a torrent with a piece length of 256KB:
- A 512KB file may span exactly 2 pieces
- A 300KB file may span 2 pieces, but only partially fill the second piece
- Multiple small files may be contained within a single piece

This mapping is crucial for translating between piece-based download progress and file-based download progress.

## Remarks

- The `Priority` property affects the order in which pieces of the file are requested
- Setting a file's `Priority` to `Priority.DoNotDownload` will exclude it from the download
- Files with higher priority will have their pieces requested before files with lower priority
- The `BitField` property represents which pieces of the file have been downloaded and verified
- For multi-file torrents, changing file priorities can help users download specific files first
- The `FullPath` property combines the download directory path with the file's relative path

## Related

- [Torrent](../common/Torrent.md)
- [BitField](../client/BitField.md)
- [Priority](../enums/Priority.md)
- [TorrentManager](../client/TorrentManager.md)
- [TorrentCreator](../common/TorrentCreator.md)