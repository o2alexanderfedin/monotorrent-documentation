# InfoHash

**Namespace**: `MonoTorrent`

The `InfoHash` struct represents the unique identifier for a torrent, which is a SHA-1 hash of the "info" section of a .torrent file. This hash is used to identify torrents in the BitTorrent network.

## Overview

An InfoHash is a 20-byte (160-bit) SHA-1 hash used to uniquely identify torrents. It's a critical component in the BitTorrent protocol, used for:

- Identifying torrents in tracker communications
- Connecting to peers in the swarm
- Indexing torrents in the DHT network
- Creating magnet links

## Properties

| Name | Type | Description |
|------|------|-------------|
| `Value` | `ReadOnlySpan<byte>` | Gets the raw 20-byte hash value |

## Methods

### Constructors

```csharp
// Create an InfoHash from a 20-byte array
public InfoHash(byte[] infoHash)

// Create an InfoHash from a span of bytes
public InfoHash(ReadOnlySpan<byte> infoHash)

// Create an InfoHash from a hexadecimal string
public InfoHash(string hexString)
```

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Equals(object obj)` | `bool` | Determines whether the specified object is equal to the current InfoHash |
| `Equals(InfoHash other)` | `bool` | Determines whether the specified InfoHash is equal to the current InfoHash |
| `GetHashCode()` | `int` | Serves as the hash function for the InfoHash type |
| `ToHex()` | `string` | Returns the hexadecimal string representation of the InfoHash |
| `ToString()` | `string` | Returns the hexadecimal string representation of the InfoHash |

### Static Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `FromHex(string hex)` | `InfoHash` | Creates an InfoHash from a hexadecimal string |
| `FromMemory(ReadOnlyMemory<byte> memory)` | `InfoHash` | Creates an InfoHash from a ReadOnlyMemory<byte> |

### Operators

| Operator | Description |
|----------|-------------|
| `==` | Determines whether two InfoHash instances are equal |
| `!=` | Determines whether two InfoHash instances are not equal |
| `implicit operator ReadOnlySpan<byte>` | Implicitly converts an InfoHash to a ReadOnlySpan<byte> |

## Examples

### Creating an InfoHash

```csharp
// Create from a byte array
byte[] hashBytes = new byte[20]; // This would normally contain hash data
InfoHash hash1 = new InfoHash(hashBytes);

// Create from a hexadecimal string
InfoHash hash2 = new InfoHash("0123456789ABCDEF0123456789ABCDEF01234567");

// Create using static method
InfoHash hash3 = InfoHash.FromHex("0123456789ABCDEF0123456789ABCDEF01234567");
```

### Using an InfoHash

```csharp
// Compare two InfoHashes
if (torrent1.InfoHash.Equals(torrent2.InfoHash))
{
    Console.WriteLine("These torrents are the same!");
}

// Get the hexadecimal representation
string hexString = torrent.InfoHash.ToHex();
Console.WriteLine($"Torrent hash: {hexString}");

// Use in dictionary
var torrentDictionary = new Dictionary<InfoHash, Torrent>();
torrentDictionary.Add(torrent.InfoHash, torrent);
```

### Using with Magnet Links

```csharp
// Create a magnet link using an InfoHash
string magnetLink = $"magnet:?xt=urn:btih:{torrent.InfoHash.ToHex()}";

// Parse a magnet link to get the InfoHash
MagnetLink magnet = MagnetLink.Parse(magnetLinkString);
InfoHash hash = magnet.InfoHash;
```

## Remarks

- InfoHash values are immutable
- Always 20 bytes (SHA-1 hash length)
- Case-insensitive in hexadecimal form
- Critical for torrent identification in the BitTorrent protocol

## Related

- [Torrent](../common/Torrent.md)
- [MagnetLink](../common/MagnetLink.md)
- [TorrentManager](../client/TorrentManager.md)