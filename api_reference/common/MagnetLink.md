# MagnetLink

**Namespace**: `MonoTorrent`

The `MagnetLink` class represents a BitTorrent Magnet URI, which is a link that identifies content using cryptographic hash values instead of a location.

## Overview

Magnet links allow users to share references to torrent content without the need to distribute a .torrent file. A magnet link contains an InfoHash (unique identifier) and can optionally include tracker URLs, display names, and other metadata.

MonoTorrent's `MagnetLink` class provides functionality to parse and create magnet links, which can then be used to start downloads without having access to a .torrent file.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `InfoHash` | `InfoHash` | The unique identifier of the torrent |
| `Name` | `string` | The suggested name for the torrent (can be null) |
| `Size` | `long` | The size of the torrent content in bytes (0 if unknown) |
| `Trackers` | `IList<string>` | List of tracker URLs specified in the magnet link |
| `WebSeeds` | `IList<string>` | List of HTTP seeds specified in the magnet link |
| `PeerSources` | `IList<string>` | List of peer sources (like "dht", "pex", etc.) |

## Methods

### Constructors

```csharp
// Create a MagnetLink with just an InfoHash
public MagnetLink(InfoHash infoHash)

// Create a MagnetLink with InfoHash and name
public MagnetLink(InfoHash infoHash, string name, IEnumerable<string> trackers)
```

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `ToV1String()` | `string` | Returns the magnet link in URN BitTorrent v1 format |
| `ToString()` | `string` | Returns the string representation of the magnet link |

### Static Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Parse(string magnetLink)` | `MagnetLink` | Parses a magnet link string and returns a MagnetLink object |
| `TryParse(string magnetLink, out MagnetLink result)` | `bool` | Tries to parse a magnet link string, returns true if successful |
| `FromUri(Uri uri)` | `MagnetLink` | Creates a MagnetLink from a Uri object |

## Examples

### Parsing a Magnet Link

```csharp
// Parse a magnet link
string magnetLinkStr = "magnet:?xt=urn:btih:6a9759bffd5c0af65319979fb7832189f4f3c35d&dn=sintel.mp4";
MagnetLink magnetLink = MagnetLink.Parse(magnetLinkStr);

// Access properties
Console.WriteLine($"InfoHash: {magnetLink.InfoHash}");
Console.WriteLine($"Name: {magnetLink.Name}");

// Handle parsing errors with TryParse
if (MagnetLink.TryParse(inputString, out MagnetLink result))
{
    // Successfully parsed
    engine.AddAsync(result);
}
else
{
    Console.WriteLine("Invalid magnet link format");
}
```

### Creating a Magnet Link

```csharp
// Create a MagnetLink with minimal information
InfoHash hash = new InfoHash("6a9759bffd5c0af65319979fb7832189f4f3c35d");
MagnetLink magnetLink = new MagnetLink(hash);

// Create a MagnetLink with name and trackers
List<string> trackers = new List<string>
{
    "udp://tracker.example.org:6969/announce",
    "http://tracker.example.com:8080/announce"
};
MagnetLink magnetLink = new MagnetLink(hash, "Example Torrent", trackers);

// Get the magnet link as a string
string magnetLinkStr = magnetLink.ToString();
```

### Using a MagnetLink to Start a Download

```csharp
// Create a client engine
ClientEngine engine = new ClientEngine(new EngineSettings());

// Add a magnet link to start downloading
MagnetLink magnetLink = MagnetLink.Parse("magnet:?xt=urn:btih:6a9759bffd5c0af65319979fb7832189f4f3c35d");
await engine.AddAsync(magnetLink);
```

## Magnet Link Format

A typical magnet link follows this format:
```
magnet:?xt=urn:btih:<info-hash>&dn=<name>&tr=<tracker-url>&tr=<tracker-url>
```

Where:
- `xt=urn:btih:<info-hash>` - The exact topic (InfoHash) in hexadecimal
- `dn=<name>` - Display name (optional)
- `tr=<tracker-url>` - Tracker URL (can appear multiple times)
- `ws=<webseed-url>` - HTTP seed (can appear multiple times)
- `x.pe=<peer-address>` - Known peer address (can appear multiple times)
- `kt=<keyword>` - Keyword topic (can appear multiple times)
- `xl=<size>` - Exact length in bytes

## Remarks

- The InfoHash is the only mandatory parameter in a magnet link
- Magnet links don't contain file structures or piece hashes that are in .torrent files
- When downloading from a magnet link, this metadata must be fetched from peers
- Magnet links are less reliable than .torrent files but more convenient for sharing

## Related

- [InfoHash](../common/InfoHash.md)
- [Torrent](../common/Torrent.md)
- [ClientEngine](../client/ClientEngine.md)