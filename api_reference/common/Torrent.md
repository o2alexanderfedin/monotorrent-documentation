# Torrent

**Namespace**: `MonoTorrent`

The `Torrent` class represents a BitTorrent .torrent file metadata, containing all necessary information to identify, validate, and download the torrent content.

## Overview

A `Torrent` instance contains metadata about the files to be downloaded, including file names, sizes, and the hash values used to verify downloaded data. It also contains tracker information and other optional metadata that aids in the download process.

`Torrent` instances can be created by loading a .torrent file from disk or by creating one programmatically using the `TorrentCreator` class.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `AnnounceUrls` | `IList<IList<string>>` | Lists of tracker announce URLs organized in tiers |
| `Comment` | `string` | Optional comment included in the torrent |
| `CreatedBy` | `string` | Information about the application that created the torrent |
| `CreationDate` | `DateTime` | When the torrent was created |
| `EditableFiles` | `bool` | Whether clients should allow renaming of files in the torrent |
| `Encoding` | `string` | Character encoding used for strings in the torrent |
| `Files` | `IList<ITorrentFile>` | List of files in the torrent |
| `HttpSeeds` | `IList<string>` | List of HTTP seed URLs |
| `InfoHash` | `InfoHash` | The identifier of the torrent (hash of the 'info' dictionary) |
| `InfoHashes` | `InfoHashes` | Contains both v1 and v2 InfoHashes when available |
| `IsPrivate` | `bool` | Whether the torrent is private (disallows peer exchange) |
| `Metadata` | `BEncodedDictionary` | Raw metadata dictionary of the torrent |
| `Name` | `string` | The suggested name for the torrent content |
| `PieceLength` | `int` | Size of each piece in bytes |
| `Size` | `long` | Total size of all files in bytes |
| `TorrentPath` | `string` | Path to the .torrent file (if loaded from disk) |
| `Type` | `TorrentType` | The BitTorrent version type of this torrent (V1, V2, or Hybrid) |
| `WebSeeds` | `IList<string>` | URLs for BitTorrent WebSeeding (GetRight style) |

## Methods

### Constructors

The `Torrent` class doesn't have public constructors. Instances are created using static factory methods.

### Static Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Load(string path)` | `Torrent` | Creates a Torrent instance from a .torrent file at the specified path |
| `Load(string path, InfoHash expectedInfoHash)` | `Torrent` | Loads a torrent and verifies it matches the expected InfoHash |
| `Load(byte[] data)` | `Torrent` | Creates a Torrent instance from raw byte data |
| `Load(BEncodedDictionary dictionary)` | `Torrent` | Creates a Torrent instance from a BEncodedDictionary |
| `Load(Stream stream)` | `Torrent` | Creates a Torrent instance from a Stream |
| `LoadAsync(string path, CancellationToken token = default)` | `Task<Torrent>` | Asynchronously creates a Torrent instance from a file path |

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `GetHashesV1(int pieceIndex)` | `ReadOnlyMemory<byte>?` | Gets the SHA1 hash for the specified v1 piece |
| `ToMagnetLink()` | `MagnetLink` | Creates a MagnetLink from this Torrent |
| `TryGetFile(ITorrentFileInfo file, out ITorrentFile torrentFile)` | `bool` | Tries to find a TorrentFile based on a TorrentFileInfo instance |

## Examples

### Loading a Torrent from a File

```csharp
// Load a torrent from a file path
Torrent torrent = Torrent.Load("/path/to/file.torrent");

// Access torrent properties
Console.WriteLine($"Name: {torrent.Name}");
Console.WriteLine($"Size: {torrent.Size} bytes");
Console.WriteLine($"Files: {torrent.Files.Count}");
Console.WriteLine($"Piece Length: {torrent.PieceLength} bytes");
Console.WriteLine($"Private: {torrent.IsPrivate}");
```

### Converting to a Magnet Link

```csharp
// Load a torrent
Torrent torrent = Torrent.Load("/path/to/file.torrent");

// Convert to a magnet link
MagnetLink magnet = torrent.ToMagnetLink();

// Display the magnet link
Console.WriteLine(magnet.ToString());
```

### Examining Torrent Files

```csharp
// Load a torrent
Torrent torrent = Torrent.Load("/path/to/file.torrent");

// List all files in the torrent
foreach (var file in torrent.Files)
{
    Console.WriteLine($"Path: {file.Path}");
    Console.WriteLine($"Size: {file.Length} bytes");
    Console.WriteLine($"Priority: {file.Priority}");
    Console.WriteLine("---------------------");
}
```

### Checking Trackers

```csharp
// Load a torrent
Torrent torrent = Torrent.Load("/path/to/file.torrent");

// Display all tracker tiers and URLs
for (int tierIndex = 0; tierIndex < torrent.AnnounceUrls.Count; tierIndex++)
{
    Console.WriteLine($"Tier {tierIndex}:");
    foreach (string trackerUrl in torrent.AnnounceUrls[tierIndex])
    {
        Console.WriteLine($"  {trackerUrl}");
    }
}
```

## BitTorrent .torrent File Format

A .torrent file is a bencoded dictionary with the following keys:

- `announce` - URL of the primary tracker
- `announce-list` - List of tracker tiers (optional)
- `creation date` - Unix timestamp when the torrent was created
- `comment` - Free-form text comment (optional)
- `created by` - Name/version of the program that created the file (optional)
- `info` - Dictionary containing all file information
  - `name` - Suggested name for the torrent
  - `piece length` - Size of each piece in bytes
  - `pieces` - Concatenated SHA1 hashes of all pieces
  - `private` - Whether the torrent is private (optional)
  - `length` - Size of the file (single-file torrents)
  - `files` - List of file information (multi-file torrents)
    - `length` - Size of the file in bytes
    - `path` - List of path components (directory/filename)

## Remarks

- The `Torrent` class is immutable once created
- The `InfoHash` is a SHA1 hash of the `info` dictionary
- `InfoHashes` property may contain both v1 (SHA1) and v2 (SHA256) hashes for BitTorrent v2 and hybrid torrents
- `AnnounceUrls` are organized in tiers, with MonoTorrent attempting trackers in the first tier before moving to subsequent tiers
- Private torrents disable peer exchange (PEX) and Distributed Hash Table (DHT) functionality

## Related

- [InfoHash](../common/InfoHash.md)
- [MagnetLink](../common/MagnetLink.md)
- [TorrentCreator](../common/TorrentCreator.md)
- [TorrentEditor](../common/TorrentEditor.md)
- [TorrentFile](../common/TorrentFile.md)