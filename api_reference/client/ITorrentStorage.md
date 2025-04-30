# ITorrentStorage

**Namespace**: `MonoTorrent.Client`

The `ITorrentStorage` interface defines the contract for custom torrent storage implementations.

## Overview

The `ITorrentStorage` interface allows developers to implement custom storage strategies for torrent data. While MonoTorrent provides a default file-based storage implementation, this interface enables alternative storage approaches such as in-memory storage, database storage, or cloud-based storage.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `Files` | `IList<ITorrentFileInfo>` | Gets the list of files in the torrent |
| `Path` | `string` | Gets the base path for the torrent data |

## Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Exists(ITorrentFileInfo file)` | `bool` | Checks if the specified file exists |
| `GetFileInfo(ITorrentFileInfo file)` | `FileInfo` | Gets a FileInfo for the specified file |
| `GetFiles(BitField bitfield, bool includeCached)` | `IList<ITorrentFileInfo>` | Gets files matching the bitfield |
| `MoveFiles(string newRoot, bool overwrite)` | `Task` | Moves all files to a new root directory |
| `ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)` | `Task<int>` | Reads data from a file |
| `WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)` | `Task<int>` | Writes data to a file |
| `CloseAsync(ITorrentFileInfo file)` | `Task` | Closes the specified file |
| `FlushAsync(ITorrentFileInfo file)` | `Task` | Flushes any buffered data for the file |
| `OpenAsync(ITorrentFileInfo file)` | `Task` | Opens the specified file for reading/writing |

## Examples

### Implementing a Custom In-Memory Storage

```csharp
public class InMemoryStorage : ITorrentStorage
{
    private Dictionary<ITorrentFileInfo, byte[]> fileData = new Dictionary<ITorrentFileInfo, byte[]>();
    private string basePath;
    private IList<ITorrentFileInfo> fileList;
    
    public InMemoryStorage(string path, IList<ITorrentFileInfo> files)
    {
        Path = path;
        Files = files;
        
        // Initialize empty data for each file
        foreach (var file in files)
        {
            fileData[file] = new byte[file.Length];
        }
    }
    
    public IList<ITorrentFileInfo> Files { get; }
    
    public string Path { get; }
    
    public bool Exists(ITorrentFileInfo file)
    {
        return fileData.ContainsKey(file);
    }
    
    public FileInfo GetFileInfo(ITorrentFileInfo file)
    {
        // In-memory storage doesn't have real files, so return null or throw
        return null;
    }
    
    public IList<ITorrentFileInfo> GetFiles(BitField bitfield, bool includeCached)
    {
        // Return all files that have pieces in the specified bitfield
        List<ITorrentFileInfo> result = new List<ITorrentFileInfo>();
        foreach (var file in Files)
        {
            // Check if any of the file's pieces are in the bitfield
            bool hasCompleteData = true;
            for (int i = file.StartPieceIndex; i <= file.EndPieceIndex; i++)
            {
                if (!bitfield[i])
                {
                    hasCompleteData = false;
                    break;
                }
            }
            
            if (hasCompleteData)
                result.Add(file);
        }
        
        return result;
    }
    
    public Task MoveFiles(string newRoot, bool overwrite)
    {
        // Just update the base path - no actual file moving needed
        basePath = newRoot;
        return Task.CompletedTask;
    }
    
    public Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        if (!fileData.TryGetValue(file, out byte[] data))
            return Task.FromResult(0);
            
        int bytesToRead = (int)Math.Min(count, file.Length - offset);
        if (bytesToRead <= 0)
            return Task.FromResult(0);
            
        Array.Copy(data, offset, buffer, bufferOffset, bytesToRead);
        return Task.FromResult(bytesToRead);
    }
    
    public Task<int> WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        if (!fileData.TryGetValue(file, out byte[] data))
            return Task.FromResult(0);
            
        int bytesToWrite = (int)Math.Min(count, file.Length - offset);
        if (bytesToWrite <= 0)
            return Task.FromResult(0);
            
        Array.Copy(buffer, bufferOffset, data, offset, bytesToWrite);
        return Task.FromResult(bytesToWrite);
    }
    
    public Task CloseAsync(ITorrentFileInfo file)
    {
        // No need to do anything for in-memory storage
        return Task.CompletedTask;
    }
    
    public Task FlushAsync(ITorrentFileInfo file)
    {
        // No need to do anything for in-memory storage
        return Task.CompletedTask;
    }
    
    public Task OpenAsync(ITorrentFileInfo file)
    {
        // No need to do anything for in-memory storage
        return Task.CompletedTask;
    }
}
```

### Using a Custom Storage Implementation

```csharp
// Create the engine
ClientEngine engine = new ClientEngine();

// Load the torrent file
Torrent torrent = Torrent.Load("example.torrent");

// Create a custom storage instance
ITorrentStorage storage = new InMemoryStorage("/virtual/path", torrent.Files);

// Create a torrent manager with the custom storage
TorrentSettings settings = new TorrentSettings();
TorrentManager manager = new TorrentManager(torrent, "/virtual/path", settings, storage);

// Register with the engine
await engine.RegisterAsync(manager);

// Start the torrent
await manager.StartAsync();
```

### Implementing a Database-Backed Storage

```csharp
public class DatabaseStorage : ITorrentStorage
{
    private readonly string connectionString;
    private readonly string dbTable;
    
    public DatabaseStorage(string connectionString, string dbTable, string path, IList<ITorrentFileInfo> files)
    {
        this.connectionString = connectionString;
        this.dbTable = dbTable;
        Path = path;
        Files = files;
        
        // Initialize database table if needed
        InitializeDatabase();
    }
    
    public IList<ITorrentFileInfo> Files { get; }
    
    public string Path { get; private set; }
    
    private void InitializeDatabase()
    {
        // Create database table to store torrent data if it doesn't exist
        using (var connection = new SqlConnection(connectionString))
        {
            connection.Open();
            
            // Create table for torrent data
            using (var command = connection.CreateCommand())
            {
                command.CommandText = $@"
                    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{dbTable}')
                    CREATE TABLE {dbTable} (
                        FileId NVARCHAR(255) NOT NULL,
                        Offset BIGINT NOT NULL,
                        Data VARBINARY(8000) NOT NULL,
                        PRIMARY KEY (FileId, Offset)
                    )";
                
                command.ExecuteNonQuery();
            }
        }
    }
    
    // Implementation of ITorrentStorage methods
    // ...
}
```

## Creating a Custom Storage Implementation

To create a custom storage implementation, you need to:

1. Implement the `ITorrentStorage` interface
2. Manage data storage and retrieval according to your requirements
3. Handle the buffering and caching of data as needed for performance
4. Properly implement file operation methods like `ReadAsync`, `WriteAsync`, etc.
5. Use your custom storage when creating a `TorrentManager`

## Remarks

- Custom storage implementations are useful for streaming, virtual storage, or special content handling
- The default implementation uses regular files on the file system
- For web applications, custom storage can store content in memory or databases
- For streaming applications, storage might prioritize certain parts of files
- All methods are asynchronous to support I/O-bound operations
- The `CloseAsync` and `OpenAsync` methods are called when a file is used or no longer needed
- `GetFiles` is used to determine which files are complete and available for use
- `MoveFiles` should update the storage location while maintaining all data

## Related

- [TorrentManager](../client/TorrentManager.md)
- [TorrentFile](../common/TorrentFile.md)
- [ClientEngine](../client/ClientEngine.md)
- [ITorrentFileInfo](../client/ITorrentFileInfo.md)