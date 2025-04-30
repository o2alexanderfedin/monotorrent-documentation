# DiskManager Class

The `DiskManager` class handles all disk I/O operations for torrents in MonoTorrent.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public class DiskManager : IDisposable
```

## Description

The `DiskManager` class is responsible for:

- Reading and writing piece data to disk
- Managing disk I/O queue
- Handling file allocation
- Implementing rate limiting for disk operations
- Managing open file handles

The `DiskManager` is typically shared across all torrents managed by a `ClientEngine` to provide centralized disk I/O management.

## Properties

### MaximumOpenFiles

Gets or sets the maximum number of files that can be open simultaneously.

```csharp
public int MaximumOpenFiles { get; set; }
```

### OpenFiles

Gets the number of currently open files.

```csharp
public int OpenFiles { get; }
```

### PendingReads

Gets the number of pending read operations.

```csharp
public int PendingReads { get; }
```

### PendingWrites

Gets the number of pending write operations.

```csharp
public int PendingWrites { get; }
```

### ReadRate

Gets the current read rate in bytes per second.

```csharp
public long ReadRate { get; }
```

### TotalRead

Gets the total number of bytes read from disk.

```csharp
public long TotalRead { get; }
```

### TotalWritten

Gets the total number of bytes written to disk.

```csharp
public long TotalWritten { get; }
```

### WriteRate

Gets the current write rate in bytes per second.

```csharp
public long WriteRate { get; }
```

## Methods

### CloseFilesAsync(ITorrentManager)

Closes all files associated with the specified torrent manager.

```csharp
public Task CloseFilesAsync(ITorrentManager manager)
```

#### Parameters

- **manager**: The torrent manager whose files should be closed.

#### Returns

A task representing the asynchronous operation.

### Dispose()

Disposes the `DiskManager` and releases all resources.

```csharp
public void Dispose()
```

### Dispose(bool)

Disposes the `DiskManager` and optionally releases unmanaged resources.

```csharp
protected virtual void Dispose(bool disposing)
```

#### Parameters

- **disposing**: `true` to release both managed and unmanaged resources; `false` to release only unmanaged resources.

### GetHashAsync(ITorrentStorage, ITorrentManagerInfo, int)

Gets the hash of the specified piece from disk.

```csharp
public Task<ReadResult> GetHashAsync(ITorrentStorage storage, ITorrentManagerInfo info, int pieceIndex)
```

#### Parameters

- **storage**: The torrent storage to use.
- **info**: The torrent manager information.
- **pieceIndex**: The index of the piece to hash.

#### Returns

A task that returns a `ReadResult` containing the hash of the piece.

### MoveFilesAsync(ITorrentManager, string)

Moves all files for the specified torrent to the specified destination path.

```csharp
public Task MoveFilesAsync(ITorrentManager manager, string newRoot)
```

#### Parameters

- **manager**: The torrent manager whose files should be moved.
- **newRoot**: The new root directory for the files.

#### Returns

A task representing the asynchronous operation.

### ReadAsync(ITorrentStorage, ITorrentManagerInfo, int, BlockInfo)

Reads a block of data from disk.

```csharp
public Task<ReadResult> ReadAsync(ITorrentStorage storage, ITorrentManagerInfo info, int pieceIndex, BlockInfo blockInfo)
```

#### Parameters

- **storage**: The torrent storage to use.
- **info**: The torrent manager information.
- **pieceIndex**: The index of the piece to read from.
- **blockInfo**: Information about the block to read.

#### Returns

A task that returns a `ReadResult` containing the read data.

### ReadPieceAsync(ITorrentStorage, ITorrentManagerInfo, int)

Reads an entire piece from disk.

```csharp
public Task<ReadResult> ReadPieceAsync(ITorrentStorage storage, ITorrentManagerInfo info, int pieceIndex)
```

#### Parameters

- **storage**: The torrent storage to use.
- **info**: The torrent manager information.
- **pieceIndex**: The index of the piece to read.

#### Returns

A task that returns a `ReadResult` containing the piece data.

### SetMaximumOpenFiles(int)

Sets the maximum number of files that can be open simultaneously.

```csharp
public void SetMaximumOpenFiles(int value)
```

#### Parameters

- **value**: The maximum number of open files.

### SetReadRateLimit(int)

Sets the maximum read rate in bytes per second.

```csharp
public void SetReadRateLimit(int rate)
```

#### Parameters

- **rate**: The maximum read rate in bytes per second.

### SetWriteRateLimit(int)

Sets the maximum write rate in bytes per second.

```csharp
public void SetWriteRateLimit(int rate)
```

#### Parameters

- **rate**: The maximum write rate in bytes per second.

### Tick()

Updates internal state, such as rate limiting calculations.

```csharp
public void Tick()
```

### WriteAsync(ITorrentStorage, ITorrentManagerInfo, int, BlockInfo, ReadOnlyMemory<byte>)

Writes a block of data to disk.

```csharp
public Task<bool> WriteAsync(ITorrentStorage storage, ITorrentManagerInfo info, int pieceIndex, BlockInfo blockInfo, ReadOnlyMemory<byte> data)
```

#### Parameters

- **storage**: The torrent storage to use.
- **info**: The torrent manager information.
- **pieceIndex**: The index of the piece to write to.
- **blockInfo**: Information about the block to write.
- **data**: The data to write.

#### Returns

A task that returns `true` if the write was successful, `false` otherwise.

## Examples

### Basic DiskManager Configuration

```csharp
// Create an engine settings object with disk manager settings
var settings = new EngineSettings
{
    // Set the maximum number of open files
    MaximumOpenFiles = 40,
    
    // Set rate limits (in bytes per second)
    MaximumDiskReadRate = 10 * 1024 * 1024,  // 10 MB/s
    MaximumDiskWriteRate = 5 * 1024 * 1024   // 5 MB/s
};

// Create the client engine with these settings
var engine = new ClientEngine(settings);

// Access the disk manager
var diskManager = engine.DiskManager;

// Monitor disk activity
Console.WriteLine($"Read rate: {diskManager.ReadRate / 1024.0 / 1024.0:F2} MB/s");
Console.WriteLine($"Write rate: {diskManager.WriteRate / 1024.0 / 1024.0:F2} MB/s");
Console.WriteLine($"Open files: {diskManager.OpenFiles} / {diskManager.MaximumOpenFiles}");
Console.WriteLine($"Pending reads: {diskManager.PendingReads}");
Console.WriteLine($"Pending writes: {diskManager.PendingWrites}");
```

### Moving Files to a New Location

```csharp
// Move all files for a torrent to a new location
string newLocation = @"D:\NewDownloads";
await torrentManager.Engine.DiskManager.MoveFilesAsync(torrentManager, newLocation);

// Torrent will continue from the new location
```

### Customizing Rate Limits

```csharp
// Adjust rate limits after engine creation
diskManager.SetReadRateLimit(20 * 1024 * 1024);  // 20 MB/s
diskManager.SetWriteRateLimit(10 * 1024 * 1024); // 10 MB/s

// Or set unlimited rates
diskManager.SetReadRateLimit(0);  // Unlimited
diskManager.SetWriteRateLimit(0); // Unlimited
```

### Creating a Custom DiskManager

```csharp
// Create a custom disk manager implementation
public class CustomDiskManager : DiskManager
{
    public CustomDiskManager(int maxOpenFiles) : base(maxOpenFiles)
    {
    }
    
    // Override methods to add custom behavior
    public override Task<ReadResult> ReadAsync(ITorrentStorage storage, ITorrentManagerInfo info, int pieceIndex, BlockInfo blockInfo)
    {
        // Add custom logging
        Console.WriteLine($"Reading piece {pieceIndex}, block {blockInfo.StartOffset}-{blockInfo.StartOffset + blockInfo.RequestLength}");
        
        // Call the base implementation
        return base.ReadAsync(storage, info, pieceIndex, blockInfo);
    }
    
    public override Task<bool> WriteAsync(ITorrentStorage storage, ITorrentManagerInfo info, int pieceIndex, BlockInfo blockInfo, ReadOnlyMemory<byte> data)
    {
        // Add custom validation
        if (data.Length == 0)
        {
            return Task.FromResult(false);
        }
        
        // Add custom logging
        Console.WriteLine($"Writing piece {pieceIndex}, block {blockInfo.StartOffset}-{blockInfo.StartOffset + blockInfo.RequestLength}");
        
        // Call the base implementation
        return base.WriteAsync(storage, info, pieceIndex, blockInfo, data);
    }
}

// Use the custom disk manager with the client engine
var customDiskManager = new CustomDiskManager(40);
var engineSettings = new EngineSettings();
var engine = new ClientEngine(engineSettings, diskManager: customDiskManager);
```

## Remarks

- The `DiskManager` is shared across all torrents in a `ClientEngine` to efficiently manage disk resources.
- It implements rate limiting to prevent overloading the disk with I/O operations.
- It manages a queue of pending reads and writes to prioritize important operations.
- It limits the number of open file handles to prevent exceeding system limits.
- Disk operations are performed asynchronously to avoid blocking the main thread.
- The DiskManager automatically closes unused files when the number of open files exceeds `MaximumOpenFiles`.
- Rate limits of 0 mean unlimited rates.

## See Also

- [ClientEngine](ClientEngine.md)
- [TorrentManager](TorrentManager.md)
- [EngineSettings](EngineSettings.md)
- [ITorrentStorage](../client/ITorrentStorage.md)
- [ReadResult](../client/ReadResult.md)