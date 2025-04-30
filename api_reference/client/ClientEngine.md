# ClientEngine Class

`ClientEngine` is the central coordinator in MonoTorrent. It manages all active torrents and provides global settings and services.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public class ClientEngine : IDisposable
```

## Description

The `ClientEngine` class is responsible for:

- Managing all active torrent downloads and uploads
- Coordinating global rate limiting
- Managing connection resources
- Handling DHT operations (if enabled)
- Coordinating port forwarding
- Providing central event dispatching

The `ClientEngine` is typically the first object created when using MonoTorrent and is designed to be a singleton in most applications.

## Constructors

### ClientEngine()

Creates a new `ClientEngine` with default settings.

```csharp
public ClientEngine()
```

### ClientEngine(EngineSettings)

Creates a new `ClientEngine` with the specified settings.

```csharp
public ClientEngine(EngineSettings settings)
```

#### Parameters

- **settings**: The settings to use with the engine.

### ClientEngine(EngineSettings, IDhtEngine)

Creates a new `ClientEngine` with the specified settings and DHT engine.

```csharp
public ClientEngine(EngineSettings settings, IDhtEngine dhtEngine)
```

#### Parameters

- **settings**: The settings to use with the engine.
- **dhtEngine**: The DHT engine to use, or `null` to disable DHT.

## Properties

### ConnectionManager

Gets the connection manager which handles all connections to peers.

```csharp
public ConnectionManager ConnectionManager { get; }
```

### DhtEngine

Gets the DHT engine used by the client engine.

```csharp
public IDhtEngine DhtEngine { get; }
```

### DiskManager

Gets the disk manager used by the client engine.

```csharp
public DiskManager DiskManager { get; }
```

### IsRunning

Gets a value indicating whether the engine is running.

```csharp
public bool IsRunning { get; }
```

### Settings

Gets the settings for the engine.

```csharp
public EngineSettings Settings { get; }
```

### Torrents

Gets the collection of torrents registered with the engine.

```csharp
public IEnumerable<TorrentManager> Torrents { get; }
```

### TotalDownloadRate

Gets the current download rate across all torrents in bytes per second.

```csharp
public long TotalDownloadRate { get; }
```

### TotalUploadRate

Gets the current upload rate across all torrents in bytes per second.

```csharp
public long TotalUploadRate { get; }
```

## Methods

### AddAsync(Torrent, string)

Registers a torrent with the engine using the specified Torrent object and download directory.

```csharp
public Task<TorrentManager> AddAsync(Torrent torrent, string downloadDirectory)
```

#### Parameters

- **torrent**: The torrent to register with the engine.
- **downloadDirectory**: The directory to download the torrent to.

#### Returns

A `TorrentManager` instance for the torrent.

### AddAsync(MagnetLink, string)

Registers a magnet link with the engine.

```csharp
public Task<TorrentManager> AddAsync(MagnetLink magnetLink, string downloadDirectory)
```

#### Parameters

- **magnetLink**: The magnet link to register with the engine.
- **downloadDirectory**: The directory to download the torrent to.

#### Returns

A `TorrentManager` instance for the magnet link.

### AddAsync(string, string)

Registers a torrent with the engine using the specified .torrent file path and download directory.

```csharp
public Task<TorrentManager> AddAsync(string torrentPath, string downloadDirectory)
```

#### Parameters

- **torrentPath**: The path to the .torrent file to load.
- **downloadDirectory**: The directory to download the torrent to.

#### Returns

A `TorrentManager` instance for the torrent.

### ChangeSettingsAsync(EngineSettings)

Changes the engine settings.

```csharp
public Task ChangeSettingsAsync(EngineSettings settings)
```

#### Parameters

- **settings**: The new settings to use.

### Dispose()

Disposes the engine and all resources associated with it.

```csharp
public void Dispose()
```

### RemoveAsync(TorrentManager)

Unregisters a torrent from the engine.

```csharp
public Task RemoveAsync(TorrentManager manager)
```

#### Parameters

- **manager**: The `TorrentManager` to unregister.

### StartAllAsync()

Starts all torrents registered with the engine.

```csharp
public Task StartAllAsync()
```

### StopAllAsync()

Stops all torrents registered with the engine.

```csharp
public Task StopAllAsync()
```

## Events

### CriticalException

Raised when a critical exception occurs in the engine.

```csharp
public event EventHandler<CriticalExceptionEventArgs> CriticalException;
```

### StatsUpdate

Raised periodically to provide updated statistics.

```csharp
public event EventHandler<StatsUpdateEventArgs> StatsUpdate;
```

### TorrentRegistered

Raised when a torrent is registered with the engine.

```csharp
public event EventHandler<TorrentEventArgs> TorrentRegistered;
```

### TorrentRemoved

Raised when a torrent is removed from the engine.

```csharp
public event EventHandler<TorrentEventArgs> TorrentRemoved;
```

## Examples

### Basic Usage

```csharp
// Create the engine with default settings
var engine = new ClientEngine();

// Add a torrent
var manager = await engine.AddAsync("ubuntu.torrent", @"C:\Downloads");

// Start the torrent
await manager.StartAsync();

// Eventually, stop the torrent and dispose the engine
await manager.StopAsync();
await engine.DisposeAsync();
```

### Custom Engine Settings

```csharp
// Create custom settings
var settings = new EngineSettings
{
    MaximumDownloadRate = 1024 * 1024, // 1 MB/s
    MaximumUploadRate = 512 * 1024,    // 512 KB/s
    ListenPort = 55123                 // Port for incoming connections
};

// Create the engine with custom settings
var engine = new ClientEngine(settings);
```

### Managing Multiple Torrents

```csharp
// Create the engine
var engine = new ClientEngine();

// Add several torrents
var torrent1 = await engine.AddAsync("file1.torrent", downloadPath);
var torrent2 = await engine.AddAsync("file2.torrent", downloadPath);
var torrent3 = await engine.AddAsync(MagnetLink.Parse(magnetLink), downloadPath);

// Start all torrents at once
await engine.StartAllAsync();

// Later, stop all torrents
await engine.StopAllAsync();
```

## Remarks

- The `ClientEngine` class is thread-safe.
- Only one instance of `ClientEngine` should be created per application.
- The engine should be properly disposed when no longer needed to release resources.
- The `ClientEngine` maintains a persistent connection manager, disk manager, and other shared resources to optimize performance across multiple torrents.

## See Also

- [EngineSettings](EngineSettings.md)
- [TorrentManager](TorrentManager.md)
- [ConnectionManager](ConnectionManager.md)
- [DiskManager](DiskManager.md)