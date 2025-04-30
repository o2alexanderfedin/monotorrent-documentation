# Configuring MonoTorrent

This guide covers the configuration options available in MonoTorrent and how to use them effectively.

## Engine Settings

The `EngineSettings` class controls global settings for the `ClientEngine`. These settings affect all torrents managed by the engine.

### Basic Configuration

```csharp
var settings = new EngineSettings
{
    // Set the maximum upload rate to 100 KB/s
    MaximumUploadRate = 100 * 1024,
    
    // Set the maximum download rate to 500 KB/s
    MaximumDownloadRate = 500 * 1024,
    
    // Set the maximum number of open connections
    MaximumConnections = 150,
    
    // Set the listen port for incoming connections
    ListenPort = 52138
};

// Create the engine with these settings
var engine = new ClientEngine(settings);
```

### Available Engine Settings

| Property | Description | Default Value |
|----------|-------------|---------------|
| `AllowedEncryption` | Encryption methods allowed for peer connections | `EncryptionTypes.All` |
| `AutoSaveLoadDhtCache` | Whether to automatically save/load the DHT cache | `true` |
| `AutoSaveLoadFastResume` | Whether to automatically save/load fast resume data | `true` |
| `AutoSaveLoadMagnetLinkMetadata` | Whether to save/load metadata from magnet links | `true` |
| `CacheDirectory` | Directory for caching torrent data | `Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)` |
| `DhtEndPoint` | EndPoint for DHT to listen on | `null` (uses ListenEndPoint) |
| `DiskCacheBytes` | Size of disk cache in bytes | `5 * 1024 * 1024` (5 MB) |
| `HaveSupressionEnabled` | Whether to enable have message supression | `true` |
| `ListenEndPoint` | EndPoint to listen for incoming connections | `new IPEndPoint(IPAddress.Any, 52138)` |
| `ListenPort` | Port to listen for incoming connections | `52138` |
| `MaximumConnections` | Maximum number of open connections | `150` |
| `MaximumDiskReadRate` | Maximum disk read rate in bytes/second | `0` (unlimited) |
| `MaximumDiskWriteRate` | Maximum disk write rate in bytes/second | `0` (unlimited) |
| `MaximumDownloadRate` | Maximum download rate in bytes/second | `0` (unlimited) |
| `MaximumHalfOpenConnections` | Maximum number of half-open connections | `5` |
| `MaximumOpenFiles` | Maximum number of files to keep open | `20` |
| `MaximumUploadRate` | Maximum upload rate in bytes/second | `0` (unlimited) |
| `ReportedAddress` | External address reported to peers | `null` |
| `WebSeedDelay` | Delay between WebSeed connections | `TimeSpan.FromSeconds(5)` |

## Torrent Settings

The `TorrentSettings` class controls settings for individual torrents.

### Basic Configuration

```csharp
var settings = new TorrentSettings
{
    // Maximum upload slots for this torrent
    UploadSlots = 8,
    
    // Maximum download rate for this torrent (in bytes/second)
    MaximumDownloadRate = 300 * 1024, 
    
    // Maximum upload rate for this torrent (in bytes/second)
    MaximumUploadRate = 50 * 1024,
    
    // Maximum connections for this torrent
    MaximumConnections = 60
};

// Create a TorrentManager with these settings
var manager = await engine.AddAsync(torrentPath, downloadPath, settings);
```

### Available Torrent Settings

| Property | Description | Default Value |
|----------|-------------|---------------|
| `MaximumConnections` | Maximum number of connections for this torrent | `60` |
| `MaximumDownloadRate` | Maximum download rate in bytes/second | `0` (unlimited) |
| `MaximumUploadRate` | Maximum upload rate in bytes/second | `0` (unlimited) |
| `UploadSlots` | Maximum number of upload slots | `8` |
| `AllowInitialSeeding` | Whether to allow initial seeding mode | `true` |
| `AllowDht` | Whether to use DHT for peer discovery | `true` |
| `AllowLocalPeerDiscovery` | Whether to use Local Peer Discovery | `true` |
| `AllowPeerExchange` | Whether to use Peer Exchange | `true` |

## DHT Settings

The `DhtEngineSettings` class controls the behavior of the DHT engine.

```csharp
var dhtSettings = new DhtEngineSettings
{
    // Maximum number of nodes in the routing table
    MaximumNodes = 1000,
    
    // Listen port for DHT (typically the same as the ListenPort)
    ListenPort = 52138
};

// Create a DhtEngine with these settings
var dhtEngine = new DhtEngine(dhtSettings);
```

## Tracker Settings

Configure how the torrent interacts with trackers.

```csharp
// Configure tracker settings when creating a TorrentManager
var trackerManager = new TrackerManager
{
    // Set announce interval
    AnnounceInterval = TimeSpan.FromMinutes(30),
    
    // Whether to use tracker
    UseTier = true
};
```

## File Priority Settings

You can set priorities for individual files within a torrent:

```csharp
// Get the list of files in the torrent
var files = manager.Files;

// Set priority for specific files
files[0].Priority = Priority.High;    // Download this file first
files[1].Priority = Priority.Normal;  // Normal priority
files[2].Priority = Priority.Low;     // Download this file last
files[3].Priority = Priority.DoNotDownload;  // Skip this file
```

The available priority levels are:
- `Priority.Highest`: Highest download priority
- `Priority.High`: High download priority
- `Priority.Normal`: Normal download priority
- `Priority.Low`: Low download priority
- `Priority.Lowest`: Lowest download priority
- `Priority.DoNotDownload`: Skip downloading this file

## Connection Settings

Configure behavior for peer connections:

```csharp
var connectionManager = new ConnectionManager
{
    // Max pending connections
    MaxPendingConnections = 20,
    
    // Whether to allow incoming connections
    AcceptIncomingConnections = true,
    
    // Timeout for establishing connections
    ConnectionTimeout = TimeSpan.FromSeconds(10)
};
```

## Saving and Loading Configuration

It's often useful to save configuration settings for reuse:

```csharp
// Save settings to a file
using (var file = File.Create("engine_settings.bin"))
{
    BinaryFormatter formatter = new BinaryFormatter();
    formatter.Serialize(file, settings);
}

// Load settings from a file
EngineSettings loadedSettings;
using (var file = File.OpenRead("engine_settings.bin"))
{
    BinaryFormatter formatter = new BinaryFormatter();
    loadedSettings = (EngineSettings)formatter.Deserialize(file);
}
```

## Best Practices

1. **Adjust rate limits based on your network capacity**
   - Set reasonable upload and download limits to avoid saturating your connection
   - Remember that too low upload speed can reduce your download performance

2. **Set appropriate connection limits**
   - Too many connections can degrade performance
   - A good rule of thumb is 100-200 maximum connections for the engine

3. **Configure DHT and PEX for better peer discovery**
   - Enable DHT, PEX, and Local Peer Discovery for maximum peers
   - Disable them for private trackers that prohibit these features

4. **Adjust disk cache based on available memory**
   - Larger disk cache can improve performance but uses more memory
   - For systems with limited RAM, keep the cache small

5. **Use file priorities for selective downloading**
   - Set high priority for files you want first
   - Set DoNotDownload for files you want to skip