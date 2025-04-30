# TorrentManager Class

The `TorrentManager` class manages the downloading, uploading, and seeding of a single torrent.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public class TorrentManager : IDisposable
```

## Description

The `TorrentManager` class handles all aspects of a single torrent, including:

- Coordinating peer connections for the torrent
- Managing the state (downloading, seeding, stopped, etc.)
- Handling piece selection and validation
- Coordinating disk operations
- Communicating with trackers
- Providing events for monitoring progress and status

Each `TorrentManager` instance is associated with a specific torrent and is managed by a `ClientEngine`.

## Constructors

### TorrentManager(Torrent, string, TorrentSettings)

Creates a new `TorrentManager` for the specified torrent, download directory, and settings.

```csharp
public TorrentManager(Torrent torrent, string downloadDirectory, TorrentSettings settings)
```

#### Parameters

- **torrent**: The torrent to manage.
- **downloadDirectory**: The directory to download the torrent to.
- **settings**: The settings to use for this torrent.

### TorrentManager(MagnetLink, string, TorrentSettings)

Creates a new `TorrentManager` for the specified magnet link, download directory, and settings.

```csharp
public TorrentManager(MagnetLink magnetLink, string downloadDirectory, TorrentSettings settings)
```

#### Parameters

- **magnetLink**: The magnet link to manage.
- **downloadDirectory**: The directory to download the torrent to.
- **settings**: The settings to use for this torrent.

## Properties

### Bitfield

Gets the bitfield representing which pieces have been downloaded and verified.

```csharp
public BitField Bitfield { get; }
```

### Complete

Gets a value indicating whether the download is complete.

```csharp
public bool Complete { get; }
```

### DownloadDirectory

Gets the directory where the torrent data is downloaded to.

```csharp
public string DownloadDirectory { get; }
```

### Files

Gets information about the files in the torrent.

```csharp
public IReadOnlyList<ITorrentFileInfo> Files { get; }
```

### HashChecked

Gets a value indicating whether the hash check has been completed.

```csharp
public bool HashChecked { get; }
```

### InfoHash

Gets the info hash of the torrent.

```csharp
public InfoHash InfoHash { get; }
```

### MagnetLink

Gets a `MagnetLink` for this torrent.

```csharp
public MagnetLink MagnetLink { get; }
```

### Metadata

Gets a value indicating whether the metadata has been downloaded (for magnet links).

```csharp
public bool Metadata { get; }
```

### Mode

Gets the current operating mode of the torrent.

```csharp
public Mode Mode { get; }
```

### Monitor

Gets the `TorrentMonitor` which provides statistics on download/upload speeds.

```csharp
public TorrentMonitor Monitor { get; }
```

### Peers

Gets the `PeerManager` which manages peers for this torrent.

```csharp
public PeerManager Peers { get; }
```

### Pieces

Gets information about the pieces in the torrent.

```csharp
public IReadOnlyList<Piece> Pieces { get; }
```

### PieceManager

Gets the `PieceManager` which manages piece selection and verification.

```csharp
public PieceManager PieceManager { get; }
```

### Progress

Gets the percentage of the download that has been completed.

```csharp
public double Progress { get; }
```

### Settings

Gets the settings for this torrent.

```csharp
public TorrentSettings Settings { get; }
```

### State

Gets the current state of the torrent.

```csharp
public TorrentState State { get; }
```

### Torrent

Gets the `Torrent` being managed.

```csharp
public Torrent Torrent { get; }
```

### TrackerManager

Gets the `TrackerManager` which manages communication with trackers.

```csharp
public TrackerManager TrackerManager { get; }
```

## Methods

### ChangeSettingsAsync(TorrentSettings)

Changes the settings for this torrent.

```csharp
public Task ChangeSettingsAsync(TorrentSettings settings)
```

#### Parameters

- **settings**: The new settings to use.

### Dispose()

Disposes the `TorrentManager` and all resources associated with it.

```csharp
public void Dispose()
```

### HashCheckAsync()

Performs a hash check on the files on disk.

```csharp
public Task HashCheckAsync()
```

#### Returns

A task that completes when the hash check is finished.

### LoadFastResumeAsync(byte[])

Loads fast resume data to resume a previous download session.

```csharp
public Task LoadFastResumeAsync(byte[] resumeData)
```

#### Parameters

- **resumeData**: The fast resume data.

### PauseAsync()

Pauses the torrent.

```csharp
public Task PauseAsync()
```

### SaveFastResumeAsync()

Saves fast resume data that can be used to resume the download later.

```csharp
public Task<byte[]> SaveFastResumeAsync()
```

#### Returns

The fast resume data as a byte array.

### SetFilePriorityAsync(ITorrentFileInfo, Priority)

Sets the download priority for a specific file.

```csharp
public Task SetFilePriorityAsync(ITorrentFileInfo file, Priority priority)
```

#### Parameters

- **file**: The file to set priority for.
- **priority**: The priority to set.

### StartAsync()

Starts or resumes the torrent.

```csharp
public Task StartAsync()
```

### StopAsync()

Stops the torrent.

```csharp
public Task StopAsync()
```

## Events

### ConnectionAttemptFailed

Raised when a connection attempt to a peer fails.

```csharp
public event EventHandler<ConnectionAttemptFailedEventArgs> ConnectionAttemptFailed;
```

### PeerConnected

Raised when a peer connection is established.

```csharp
public event EventHandler<PeerConnectedEventArgs> PeerConnected;
```

### PeerDisconnected

Raised when a peer connection is closed.

```csharp
public event EventHandler<PeerDisconnectedEventArgs> PeerDisconnected;
```

### PieceHashed

Raised when a piece has been hashed.

```csharp
public event EventHandler<PieceHashedEventArgs> PieceHashed;
```

### TorrentStateChanged

Raised when the state of the torrent changes.

```csharp
public event EventHandler<TorrentStateChangedEventArgs> TorrentStateChanged;
```

## Examples

### Basic Usage

```csharp
// Create a TorrentManager for a .torrent file
var torrent = await Torrent.LoadAsync("ubuntu.torrent");
var settings = new TorrentSettings();
var manager = new TorrentManager(torrent, @"C:\Downloads", settings);

// Register with the engine
await engine.AddAsync(manager);

// Start the torrent
await manager.StartAsync();

// Monitor progress
manager.TorrentStateChanged += (sender, e) => {
    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
};

manager.PieceHashed += (sender, e) => {
    Console.WriteLine($"Piece {e.PieceIndex} hashed. Valid: {e.HashPassed}");
    Console.WriteLine($"Progress: {manager.Progress:0.00}%");
};
```

### Setting File Priorities

```csharp
// Set priorities for specific files
foreach (var file in manager.Files)
{
    if (file.Path.EndsWith(".mp4"))
        await manager.SetFilePriorityAsync(file, Priority.High);
    else if (file.Path.EndsWith(".txt"))
        await manager.SetFilePriorityAsync(file, Priority.Low);
    else if (file.Path.EndsWith(".nfo"))
        await manager.SetFilePriorityAsync(file, Priority.DoNotDownload);
}
```

### Saving and Loading Fast Resume Data

```csharp
// Save fast resume data
byte[] resumeData = await manager.SaveFastResumeAsync();
File.WriteAllBytes($"{manager.InfoHash.ToHex()}.fastresume", resumeData);

// Later, load the fast resume data
if (File.Exists($"{infoHash.ToHex()}.fastresume"))
{
    byte[] loadedResumeData = File.ReadAllBytes($"{infoHash.ToHex()}.fastresume");
    await manager.LoadFastResumeAsync(loadedResumeData);
}
```

## Remarks

- Each `TorrentManager` should be registered with a `ClientEngine` using `engine.AddAsync(manager)`.
- The `TorrentManager` transitions through different states (represented by `TorrentState`) as it operates.
- The `Mode` property reflects the current operating mode, which determines the behavior of the torrent.
- File priorities can be set to control which files are downloaded and in what order.
- Fast resume data should be saved before stopping a torrent to enable quick resuming later.

## See Also

- [ClientEngine](ClientEngine.md)
- [TorrentSettings](TorrentSettings.md)
- [PeerManager](PeerManager.md)
- [TrackerManager](TrackerManager.md)
- [TorrentState](../enums/TorrentState.md)