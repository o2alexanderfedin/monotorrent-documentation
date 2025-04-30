# TorrentCreator

**Namespace**: `MonoTorrent`

The `TorrentCreator` class provides functionality for creating new .torrent files.

## Overview

`TorrentCreator` allows developers to programmatically create .torrent files for distributing content via BitTorrent. It handles all the necessary steps, including scanning files, calculating piece hashes, and generating the final .torrent file structure according to the BitTorrent specification.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `Comment` | `string` | Optional comment to include in the torrent |
| `CreatedBy` | `string` | Name/version of software creating the torrent |
| `CreationDate` | `DateTime?` | When the torrent was created (null = don't include) |
| `PieceLength` | `int` | Size of each piece in bytes (must be power of 2) |
| `Private` | `bool` | Whether to mark the torrent as private |
| `Publisher` | `string` | Name of the content publisher |
| `PublisherUrl` | `string` | URL of the content publisher |
| `Source` | `string` | Source of the torrent (often used by private trackers) |
| `StoreMD5` | `bool` | Whether to calculate and store MD5 hashes for files |
| `StoreV2InfoHash` | `bool` | Whether to create a hybrid or v2 torrent |

## Events

| Event | Type | Description |
|-------|------|-------------|
| `Hashed` | `EventHandler<TorrentCreatorEventArgs>` | Fires after each piece is hashed |

## Methods

### Constructors

```csharp
public TorrentCreator()
```
Creates a new TorrentCreator instance with default settings.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `AddAnnounce(string announce)` | `void` | Adds a tracker announce URL |
| `AddAnnounces(IEnumerable<string> announces)` | `void` | Adds multiple tracker announce URLs |
| `AddAnnounces(IEnumerable<IEnumerable<string>> announces)` | `void` | Adds tracker announce URLs in tiers |
| `AddHttpSeed(string httpSeed)` | `void` | Adds an HTTP seed URL |
| `AddHttpSeeds(IEnumerable<string> httpSeeds)` | `void` | Adds multiple HTTP seed URLs |
| `AddPieceHashes(string baseDirectory, IEnumerable<FileMapping> files)` | `Task` | Calculates and adds piece hashes for the specified files |
| `AddWebSeed(string webSeed)` | `void` | Adds a GetRight-style web seed URL |
| `AddWebSeeds(IEnumerable<string> webSeeds)` | `void` | Adds multiple web seed URLs |
| `Create(ITorrentFileSource fileSource)` | `Task<Torrent>` | Creates a torrent from the specified file source |
| `Create(string path)` | `Task<Torrent>` | Creates a torrent from the file/directory at the specified path |
| `CreateAsync(ITorrentFileSource fileSource)` | `Task<Torrent>` | Asynchronously creates a torrent from the specified file source |
| `CreateAsync(string path)` | `Task<Torrent>` | Asynchronously creates a torrent from the file/directory at the specified path |
| `SetCustom(BEncodedString key, BEncodedValue value)` | `void` | Sets a custom key/value pair in the torrent metainfo |
| `SetDhtNodes(IEnumerable<Tuple<string, int>> nodes)` | `void` | Sets DHT nodes to be included in the torrent |
| `Write(Stream stream, ITorrentFileSource fileSource)` | `Task` | Writes the torrent data to the specified stream |

## Examples

### Creating a Simple Torrent

```csharp
// Create a new TorrentCreator
TorrentCreator creator = new TorrentCreator();

// Set basic properties
creator.Comment = "An example torrent";
creator.CreatedBy = "MonoTorrent Example";
creator.Publisher = "Example Publisher";
creator.PieceLength = 64 * 1024; // 64KB pieces

// Add a tracker
creator.AddAnnounce("http://example.tracker.com/announce");

// Create the torrent from a directory
Torrent torrent = await creator.CreateAsync("/path/to/content");

// Save the torrent file
await torrent.SaveAsync("/path/to/save/file.torrent");
```

### Creating a Multi-Tracker Torrent

```csharp
// Create a new TorrentCreator
TorrentCreator creator = new TorrentCreator();

// Add tracker tiers
var tier1 = new List<string>
{
    "http://primary1.tracker.com/announce",
    "http://primary2.tracker.com/announce"
};

var tier2 = new List<string>
{
    "http://backup1.tracker.com/announce",
    "http://backup2.tracker.com/announce"
};

var tiers = new List<IEnumerable<string>> { tier1, tier2 };
creator.AddAnnounces(tiers);

// Create and save the torrent
Torrent torrent = await creator.CreateAsync("/path/to/content");
await torrent.SaveAsync("/path/to/save/file.torrent");
```

### Monitoring Hashing Progress

```csharp
TorrentCreator creator = new TorrentCreator();

// Subscribe to the Hashed event
creator.Hashed += (sender, e) =>
{
    double percentComplete = (double)e.PiecesHashed / e.TotalPieces * 100;
    Console.WriteLine($"Hashed piece {e.PiecesHashed} of {e.TotalPieces} ({percentComplete:F2}%)");
};

// Create the torrent
Torrent torrent = await creator.CreateAsync("/path/to/large/content");
await torrent.SaveAsync("/path/to/save/file.torrent");
```

### Creating a Private Torrent with WebSeeds

```csharp
TorrentCreator creator = new TorrentCreator();

// Mark as private
creator.Private = true;

// Add tracker
creator.AddAnnounce("http://private.tracker.com/announce");

// Add web seeds for fallback download option
creator.AddWebSeed("http://example.com/download/file1.bin");
creator.AddWebSeed("http://mirror.example.com/download/file1.bin");

// Create and save the torrent
Torrent torrent = await creator.CreateAsync("/path/to/content");
await torrent.SaveAsync("/path/to/save/file.torrent");
```

## Remarks

- The piece length must be a power of 2 (16KB, 32KB, 64KB, 128KB, etc.)
- A smaller piece length creates larger torrent files but allows for more granular verification
- A larger piece length creates smaller torrent files but requires more data to be rehashed if verification fails
- For optimal performance, choose piece lengths based on file size:
  - Small files (<50MB): 16-32KB pieces
  - Medium files (50MB-1GB): 64-256KB pieces
  - Large files (>1GB): 512KB-1MB pieces
- Private torrents disable DHT and Peer Exchange
- When setting StoreV2InfoHash to true, the creator will generate a hybrid torrent with both v1 and v2 hash information
- The Hashed event allows monitoring of progress during the hash calculation, which can be time-consuming for large content

## Related

- [Torrent](../common/Torrent.md)
- [TorrentEditor](../common/TorrentEditor.md)
- [InfoHash](../common/InfoHash.md)
- [TorrentFile](../common/TorrentFile.md)