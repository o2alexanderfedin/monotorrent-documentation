# TorrentEditor

**Namespace**: `MonoTorrent`

The `TorrentEditor` class provides functionality for modifying existing .torrent files.

## Overview

`TorrentEditor` allows developers to modify various properties of existing torrent files without rehashing the torrent data. This is useful for changing tracker URLs, adding web seeds, or modifying other metadata in a torrent file while preserving the InfoHash (which uniquely identifies the content).

## Properties

| Name | Type | Description |
|------|------|-------------|
| `Announces` | `List<List<string>>` | Gets or sets the list of tracker announce URLs organized in tiers |
| `Comment` | `string` | Gets or sets the free-form text comment |
| `CreatedBy` | `string` | Gets or sets the name/version of software that created the torrent |
| `CreationDate` | `DateTime?` | Gets or sets when the torrent was created |
| `HttpSeeds` | `List<string>` | Gets or sets the list of HTTP seed URLs |
| `IsPrivate` | `bool?` | Gets or sets whether the torrent is private |
| `Publisher` | `string` | Gets or sets the name of the content publisher |
| `PublisherUrl` | `string` | Gets or sets the URL of the content publisher |
| `Source` | `string` | Gets or sets the source of the torrent |
| `WebSeeds` | `List<string>` | Gets or sets the list of GetRight-style web seed URLs |

## Methods

### Constructors

```csharp
public TorrentEditor(Torrent torrent)
```
Creates a new TorrentEditor for the specified torrent.

```csharp
public TorrentEditor(string path)
```
Creates a new TorrentEditor by loading the torrent at the specified path.

```csharp
public TorrentEditor(byte[] torrentData)
```
Creates a new TorrentEditor using the provided raw torrent data.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `GetCustomKeys()` | `IList<BEncodedString>` | Gets the list of custom keys in the torrent |
| `GetCustomValue(BEncodedString key)` | `BEncodedValue` | Gets the value associated with a custom key |
| `RemoveCustomKey(BEncodedString key)` | `bool` | Removes a custom key from the torrent |
| `RemoveDhtNodes()` | `void` | Removes all DHT nodes from the torrent |
| `Save()` | `byte[]` | Creates a byte array containing the modified torrent data |
| `Save(Stream stream)` | `void` | Saves the modified torrent to the specified stream |
| `Save(string path)` | `void` | Saves the modified torrent to the specified file path |
| `SetCustomValue(BEncodedString key, BEncodedValue value)` | `void` | Sets a custom key/value pair in the torrent |
| `SetDhtNodes(IEnumerable<Tuple<string, int>> nodes)` | `void` | Sets the DHT nodes for the torrent |
| `ToTorrent()` | `Torrent` | Creates a Torrent object from the current state of the editor |

## Examples

### Updating Trackers

```csharp
// Load a torrent file
TorrentEditor editor = new TorrentEditor("/path/to/original.torrent");

// Replace all trackers with a new list
var newTrackers = new List<List<string>>
{
    new List<string> { "http://primary.tracker.com/announce" },
    new List<string> { "http://backup1.tracker.com/announce", "http://backup2.tracker.com/announce" }
};

editor.Announces = newTrackers;

// Save the modified torrent
editor.Save("/path/to/modified.torrent");
```

### Adding Web Seeds

```csharp
// Load a torrent
TorrentEditor editor = new TorrentEditor("/path/to/original.torrent");

// Add web seeds
editor.WebSeeds.Add("http://mirror1.example.com/files/");
editor.WebSeeds.Add("http://mirror2.example.com/files/");

// Save the modified torrent
editor.Save("/path/to/modified.torrent");
```

### Modifying Torrent Properties

```csharp
// Load a torrent
TorrentEditor editor = new TorrentEditor("/path/to/original.torrent");

// Update various properties
editor.Comment = "Updated torrent file";
editor.CreatedBy = "MonoTorrent Editor Example";
editor.IsPrivate = true;
editor.Publisher = "New Publisher";
editor.PublisherUrl = "https://example.com";

// Save the modified torrent
editor.Save("/path/to/modified.torrent");
```

### Working with Custom Values

```csharp
// Load a torrent
TorrentEditor editor = new TorrentEditor("/path/to/original.torrent");

// Set a custom key/value pair
editor.SetCustomValue(
    new BEncodedString("custom-tag"), 
    new BEncodedString("custom-value")
);

// Get all custom keys
var keys = editor.GetCustomKeys();
foreach (var key in keys)
{
    var value = editor.GetCustomValue(key);
    Console.WriteLine($"Custom key: {key}, Value: {value}");
}

// Remove a custom key
editor.RemoveCustomKey(new BEncodedString("outdated-key"));

// Save the modified torrent
editor.Save("/path/to/modified.torrent");
```

### Converting Editor to Torrent

```csharp
// Load and modify a torrent
TorrentEditor editor = new TorrentEditor("/path/to/original.torrent");
editor.Comment = "Modified torrent";
editor.Announces.Clear();
editor.Announces.Add(new List<string> { "http://new.tracker.com/announce" });

// Convert to Torrent object
Torrent torrent = editor.ToTorrent();

// Use the Torrent object
Console.WriteLine($"Name: {torrent.Name}");
Console.WriteLine($"InfoHash: {torrent.InfoHash}");
```

## Remarks

- The `TorrentEditor` allows modifying metadata but cannot change the actual content or piece hashes
- Changes made with `TorrentEditor` do not affect the InfoHash, so the modified torrent remains compatible with the original swarm
- Properties that are not set (null) will not modify the original value in the torrent
- For bool properties like `IsPrivate`, null means "don't change the existing value"
- The `Save()` methods regenerate the entire .torrent file with the modified metadata
- To add or remove trackers individually, manipulate the `Announces` list directly
- Custom values can be used to store application-specific data in the torrent file
- The editor does not validate URLs or other content - it's the responsibility of the caller to ensure valid data

## Related

- [Torrent](../common/Torrent.md)
- [TorrentCreator](../common/TorrentCreator.md)
- [InfoHash](../common/InfoHash.md)