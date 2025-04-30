# TorrentSettings

**Namespace**: `MonoTorrent.Client`

The `TorrentSettings` class contains configuration options that apply to individual torrents.

## Overview

`TorrentSettings` allows fine-grained control over how individual torrents behave, including upload/download rate limits, connection limits, and various BitTorrent protocol options. These settings override or complement the global settings defined in `EngineSettings`.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `AllowDht` | `bool` | Whether to use the Distributed Hash Table (DHT) to find additional peers |
| `AllowPeerExchange` | `bool` | Whether to use Peer Exchange (PEX) to find additional peers |
| `AllowedEncryption` | `EncryptionTypes` | What encryption methods are allowed for peer connections |
| `DownloadMetadata` | `bool` | Whether to download metadata if not provided (for magnet links) |
| `InitialSeedingEnabled` | `bool` | Whether to use initial seeding mode when the torrent is first seeded |
| `MaxConnections` | `int` | Maximum number of connections for this torrent |
| `MaxDownloadSpeed` | `int` | Maximum download speed in bytes/second (0 = unlimited) |
| `MaxUploadSpeed` | `int` | Maximum upload speed in bytes/second (0 = unlimited) |
| `MinimumTimeBetweenAnnounces` | `TimeSpan` | Minimum time allowed between tracker announces |
| `PreferEncryption` | `bool` | Whether to prefer encrypted connections over unencrypted ones |
| `UploadSlots` | `int` | Number of upload slots (unchoked peers) for this torrent |
| `UsePartialFiles` | `bool` | Whether to append '.!mt' to incomplete files |
| `WebSeedDelay` | `int` | Delay between connections to the same web seed in milliseconds |

## Methods

### Constructors

```csharp
public TorrentSettings()
```
Creates a new `TorrentSettings` instance with default values.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Clone()` | `TorrentSettings` | Creates a deep copy of this instance |

## Examples

### Creating and Configuring Torrent Settings

```csharp
// Create new torrent settings with defaults
TorrentSettings settings = new TorrentSettings();

// Configure connection settings
settings.MaxConnections = 60;
settings.UploadSlots = 8;

// Configure bandwidth limits
settings.MaxUploadSpeed = 50 * 1024;    // 50 KB/s upload limit
settings.MaxDownloadSpeed = 200 * 1024; // 200 KB/s download limit

// Configure features
settings.AllowDht = true;
settings.AllowPeerExchange = true;
settings.PreferEncryption = true;
settings.AllowedEncryption = EncryptionTypes.RC4Full | EncryptionTypes.PlainText;

// Configure partial files
settings.UsePartialFiles = true;

// Create a torrent manager with these settings
TorrentManager manager = new TorrentManager(torrent, downloadDirectory, settings);
```

### High-Speed Download Settings

```csharp
// Create settings optimized for fast downloading
TorrentSettings fastSettings = new TorrentSettings
{
    // Maximum connections for faster downloading
    MaxConnections = 100,
    
    // Many upload slots to encourage reciprocation
    UploadSlots = 10,
    
    // Enable all peer discovery methods
    AllowDht = true,
    AllowPeerExchange = true,
    
    // Limit upload to preserve bandwidth
    MaxUploadSpeed = 100 * 1024,  // 100 KB/s
    
    // No download limit
    MaxDownloadSpeed = 0,        // Unlimited
    
    // Allow all encryption types for more potential connections
    AllowedEncryption = EncryptionTypes.All
};

// Create a torrent manager with these settings
TorrentManager manager = new TorrentManager(torrent, downloadDirectory, fastSettings);
```

### Private Torrent Settings

```csharp
// Create settings for a private tracker
TorrentSettings privateSettings = new TorrentSettings
{
    // Disable distributed peer discovery (required for private trackers)
    AllowDht = false,
    AllowPeerExchange = false,
    
    // Private trackers often have better peers, so use fewer connections
    MaxConnections = 30,
    UploadSlots = 4,
    
    // Maintain good ratio
    MaxUploadSpeed = 75 * 1024,   // 75 KB/s
    MaxDownloadSpeed = 150 * 1024, // 150 KB/s
    
    // Required by some private trackers
    PreferEncryption = false,
    AllowedEncryption = EncryptionTypes.PlainText
};

// Create a torrent manager with these settings
TorrentManager manager = new TorrentManager(torrent, downloadDirectory, privateSettings);
```

### Low-Bandwidth Settings

```csharp
// Create settings for use on metered connections
TorrentSettings lowBandwidthSettings = new TorrentSettings
{
    // Strict bandwidth limits
    MaxDownloadSpeed = 25 * 1024,  // 25 KB/s
    MaxUploadSpeed = 5 * 1024,     // 5 KB/s
    
    // Reduce connections to minimize overhead
    MaxConnections = 15,
    UploadSlots = 2,
    
    // Slower tracker updates to reduce traffic
    MinimumTimeBetweenAnnounces = TimeSpan.FromMinutes(10),
    
    // Keep DHT active but limit encryption overhead
    AllowDht = true,
    AllowPeerExchange = true,
    PreferEncryption = false,
    AllowedEncryption = EncryptionTypes.PlainText
};

TorrentManager manager = new TorrentManager(torrent, downloadDirectory, lowBandwidthSettings);
```

### Media Streaming Optimization

```csharp
// Settings optimized for streaming media content
TorrentSettings streamingSettings = new TorrentSettings
{
    // Allow many connections to find pieces quickly
    MaxConnections = 75,
    UploadSlots = 6,
    
    // Prioritize download speed, generous upload to reciprocate
    MaxDownloadSpeed = 0,          // Unlimited
    MaxUploadSpeed = 150 * 1024,   // 150 KB/s
    
    // Enable all peer finding methods
    AllowDht = true,
    AllowPeerExchange = true,
    
    // Use all connection types to maximize piece availability
    AllowedEncryption = EncryptionTypes.All,
    
    // Critical for streaming - enables sequential piece downloading
    // (Note: In actual implementation, streaming is configured via 
    // the StreamingTorrentManager or StreamProvider class)
};

TorrentManager manager = new TorrentManager(torrent, downloadDirectory, streamingSettings);

// Example of enabling streaming mode
// StreamProvider streamProvider = new StreamProvider(manager);
// HttpStream stream = streamProvider.CreateHttpStream();
// string streamUrl = stream.Uri.ToString();
```

### Initial Seeding Configuration

```csharp
// Settings for the initial seeder of a torrent
TorrentSettings initialSeedSettings = new TorrentSettings
{
    // Enable initial seeding mode - this helps distribute pieces optimally
    // to ensure the torrent spreads efficiently with minimal uploaded data
    InitialSeedingEnabled = true,
    
    // Set generous upload limits since we're the primary seed
    MaxUploadSpeed = 500 * 1024,  // 500 KB/s
    UploadSlots = 15,
    
    // Allow many connections to distribute to as many peers as possible
    MaxConnections = 150,
    
    // Enable all peer discovery methods
    AllowDht = true,
    AllowPeerExchange = true,
    
    // Use standard announce interval since we want to advertise availability
    MinimumTimeBetweenAnnounces = TimeSpan.FromMinutes(5)
};

// Create a torrent manager with these settings
TorrentManager manager = new TorrentManager(torrent, downloadDirectory, initialSeedSettings);

// Event handler to detect when initial seeding is no longer needed
manager.TorrentStateChanged += (sender, e) => {
    if (manager.Complete && manager.Settings.InitialSeedingEnabled)
    {
        // Once we have multiple seeds, we can disable initial seeding mode
        if (manager.Peers.Seeds > 3)
        {
            var newSettings = manager.Settings.Clone();
            newSettings.InitialSeedingEnabled = false;
            manager.Settings = newSettings;
            Console.WriteLine("Switched from initial seeding to normal seeding mode");
        }
    }
};
```

### Changing Settings at Runtime

```csharp
// Get a reference to an existing TorrentManager
TorrentManager manager = /* ... */;

// Make a copy of the current settings
TorrentSettings newSettings = manager.Settings.Clone();

// Modify settings based on time of day
var currentHour = DateTime.Now.Hour;
if (currentHour >= 22 || currentHour < 8) 
{
    // Night-time settings: higher limits during off-peak hours
    Console.WriteLine("Applying night-time bandwidth settings");
    newSettings.MaxUploadSpeed = 500 * 1024;   // 500 KB/s
    newSettings.MaxDownloadSpeed = 0;          // Unlimited
    newSettings.MaxConnections = 100;
    newSettings.UploadSlots = 12;
}
else if (currentHour >= 8 && currentHour < 18)
{
    // Work-hours settings: strict limits to preserve bandwidth
    Console.WriteLine("Applying work-hours bandwidth restrictions");
    newSettings.MaxUploadSpeed = 20 * 1024;    // 20 KB/s
    newSettings.MaxDownloadSpeed = 50 * 1024;  // 50 KB/s
    newSettings.MaxConnections = 25;
    newSettings.UploadSlots = 3;
}
else
{
    // Evening settings: moderate limits
    Console.WriteLine("Applying evening bandwidth settings");
    newSettings.MaxUploadSpeed = 100 * 1024;   // 100 KB/s
    newSettings.MaxDownloadSpeed = 200 * 1024; // 200 KB/s
    newSettings.MaxConnections = 60;
    newSettings.UploadSlots = 8;
}

// Apply the new settings to the manager
manager.Settings = newSettings;
```

## Default Values

| Setting | Default Value |
|---------|---------------|
| `AllowDht` | `true` |
| `AllowPeerExchange` | `true` |
| `AllowedEncryption` | `EncryptionTypes.All` |
| `DownloadMetadata` | `true` |
| `InitialSeedingEnabled` | `false` |
| `MaxConnections` | `60` |
| `MaxDownloadSpeed` | `0` (unlimited) |
| `MaxUploadSpeed` | `0` (unlimited) |
| `MinimumTimeBetweenAnnounces` | `5 minutes` |
| `PreferEncryption` | `false` |
| `UploadSlots` | `8` |
| `UsePartialFiles` | `true` |
| `WebSeedDelay` | `250 ms` |

## Remarks

- These settings apply to a single torrent and are passed to the `TorrentManager` constructor
- For private torrents, `AllowDht` and `AllowPeerExchange` should be set to `false` to respect the privacy of the tracker
- Changing settings by assigning to `TorrentManager.Settings` takes effect immediately
- To create a good BitTorrent citizen, ensure you allow a reasonable upload speed
- The actual connection count and bandwidth usage may be further limited by the `EngineSettings`
- When setting bandwidth limits, the value 0 means "unlimited"
- For magnet links, the `DownloadMetadata` option must be true
- The `MinimumTimeBetweenAnnounces` property prevents aggressive re-announcing to trackers
- Initial seeding mode (enabled via `InitialSeedingEnabled`) optimizes upload to help torrents spread faster when first seeded

## Related

- [EngineSettings](../client/EngineSettings.md)
- [ClientEngine](../client/ClientEngine.md)
- [TorrentManager](../client/TorrentManager.md)
- [Torrent](../common/Torrent.md)