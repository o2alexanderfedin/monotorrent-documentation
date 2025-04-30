# EngineSettings

**Namespace**: `MonoTorrent.Client`

The `EngineSettings` class contains configuration options that apply to the entire BitTorrent engine and all torrents it manages.

## Overview

`EngineSettings` controls global behaviors of the BitTorrent engine, including connection limits, port settings, disk cache configuration, and other performance-related parameters. These settings affect all torrents managed by the `ClientEngine`.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `AllowHaveSuppression` | `bool` | Whether to suppress sending "Have" messages to peers that already have a piece |
| `AllowLocalPeerDiscovery` | `bool` | Whether to enable Local Peer Discovery (LPD) |
| `AllowPortForwarding` | `bool` | Whether to attempt automatic port forwarding via UPnP/NAT-PMP |
| `AutoSaveLoadDhtCache` | `bool` | Whether to automatically save and load the DHT cache |
| `CacheDirectory` | `string` | Directory where cache data is stored |
| `DhtEndPoint` | `IPEndPoint` | The endpoint the DHT will listen on |
| `DiskCacheBytes` | `int` | The maximum size of the disk cache in bytes |
| `HaveSuppressionEnabled` | `bool` | Whether "Have" message suppression is enabled |
| `ListenPort` | `int` | The port to listen for incoming connections on |
| `MaxConnections` | `int` | Maximum number of open connections for the entire engine |
| `MaxDiskReadRate` | `int` | Maximum disk read rate in bytes/second (0 = unlimited) |
| `MaxDiskWriteRate` | `int` | Maximum disk write rate in bytes/second (0 = unlimited) |
| `MaxOpenFiles` | `int` | Maximum number of open files |
| `MaxUploadSpeed` | `int` | Maximum global upload speed in bytes/second (0 = unlimited) |
| `MaxDownloadSpeed` | `int` | Maximum global download speed in bytes/second (0 = unlimited) |
| `ReportedAddress` | `IPAddress` | External IP address reported to trackers and peers |
| `WebSeedDelay` | `int` | Delay between connections to the same web seed in milliseconds |

## Methods

### Constructors

```csharp
public EngineSettings()
```
Creates a new `EngineSettings` instance with default values.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Clone()` | `EngineSettings` | Creates a deep copy of this instance |

## Examples

### Creating and Configuring Engine Settings

```csharp
// Create new engine settings with defaults
EngineSettings settings = new EngineSettings();

// Configure connection settings
settings.ListenPort = 52138;
settings.MaxConnections = 150;

// Configure bandwidth limits
settings.MaxUploadSpeed = 100 * 1024;    // 100 KB/s upload limit
settings.MaxDownloadSpeed = 500 * 1024;  // 500 KB/s download limit

// Configure disk cache
settings.DiskCacheBytes = 50 * 1024 * 1024;  // 50 MB disk cache
settings.MaxOpenFiles = 40;

// Configure features
settings.AllowPortForwarding = true;
settings.AllowLocalPeerDiscovery = true;
settings.AutoSaveLoadDhtCache = true;

// Create a ClientEngine with these settings
ClientEngine engine = new ClientEngine(settings);
```

### Adjusting Engine Settings at Runtime

```csharp
// Get a reference to an existing ClientEngine
ClientEngine engine = /* ... */;

// Clone the current settings
EngineSettings newSettings = engine.Settings.Clone();

// Modify the settings
newSettings.MaxConnections = 200;
newSettings.MaxUploadSpeed = 200 * 1024;  // 200 KB/s upload limit

// Apply the new settings to the engine
engine.Settings = newSettings;

// Engine will now use the new settings
Console.WriteLine($"Engine now allows {engine.Settings.MaxConnections} connections");
```

### Setting Up for a Home Server

```csharp
// Create settings optimized for a home server
EngineSettings serverSettings = new EngineSettings
{
    // Use a specific listen port
    ListenPort = 51515,
    
    // Allow high connection counts
    MaxConnections = 300,
    
    // Use a large disk cache for better performance
    DiskCacheBytes = 256 * 1024 * 1024,  // 256 MB
    
    // Enable all discovery methods
    AllowPortForwarding = true,
    AllowLocalPeerDiscovery = true,
    
    // Specify cache location
    CacheDirectory = "/var/cache/torrents",
    
    // No throttling
    MaxUploadSpeed = 0,    // Unlimited
    MaxDownloadSpeed = 0   // Unlimited
};

// Create engine with these settings
ClientEngine engine = new ClientEngine(serverSettings);
```

## Default Values

| Setting | Default Value |
|---------|---------------|
| `AllowHaveSuppression` | `true` |
| `AllowLocalPeerDiscovery` | `true` |
| `AllowPortForwarding` | `true` |
| `AutoSaveLoadDhtCache` | `true` |
| `CacheDirectory` | User's application data directory |
| `DiskCacheBytes` | 5 MB |
| `ListenPort` | 52138 |
| `MaxConnections` | 150 |
| `MaxDiskReadRate` | 0 (unlimited) |
| `MaxDiskWriteRate` | 0 (unlimited) |
| `MaxOpenFiles` | 20 |
| `MaxUploadSpeed` | 0 (unlimited) |
| `MaxDownloadSpeed` | 0 (unlimited) |
| `WebSeedDelay` | 250 ms |

## Remarks

- The `ClientEngine` uses these settings as global defaults and limits
- Individual torrent limits (set via `TorrentSettings`) cannot exceed the global limits set in `EngineSettings`
- Changes to `EngineSettings` take effect immediately after assigning to `ClientEngine.Settings`
- When setting bandwidth limits, the value 0 means "unlimited"
- The `DiskCacheBytes` setting directly impacts memory usage, so set it according to available system memory
- Port forwarding requires UPnP or NAT-PMP support in the network router
- Local Peer Discovery uses multicast to find peers on the local network
- To disable DHT, set `DhtEndPoint` to null

## Related

- [ClientEngine](../client/ClientEngine.md)
- [TorrentSettings](../client/TorrentSettings.md)
- [TorrentManager](../client/TorrentManager.md)