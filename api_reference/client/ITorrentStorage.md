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

### Creating a RAM Disk Storage for Streaming

```csharp
public class RamDiskStorage : ITorrentStorage
{
    private readonly Dictionary<ITorrentFileInfo, MemoryStream> fileStreams = new Dictionary<ITorrentFileInfo, MemoryStream>();
    private readonly Dictionary<ITorrentFileInfo, bool> fileOpenState = new Dictionary<ITorrentFileInfo, bool>();
    private readonly int cacheSizeLimit; // Maximum bytes to keep in memory
    private readonly TorrentManager streamingManager;
    
    public RamDiskStorage(string path, IList<ITorrentFileInfo> files, TorrentManager manager, int cacheSizeMB = 100)
    {
        Path = path;
        Files = files;
        streamingManager = manager;
        cacheSizeLimit = cacheSizeMB * 1024 * 1024;
        
        // Add file tracking entries
        foreach (var file in files)
        {
            fileStreams[file] = null; // Will be created on first access
            fileOpenState[file] = false;
        }
        
        // Subscribe to piece completed events to prioritize caching
        manager.PieceHashed += OnPieceHashed;
    }
    
    public IList<ITorrentFileInfo> Files { get; }
    public string Path { get; }
    
    private void OnPieceHashed(object sender, PieceHashedEventArgs e)
    {
        if (e.HashPassed)
        {
            // When a piece completes successfully, update our in-memory cache
            // This might be called from another thread, so use async operations
            Task.Run(() => CachePieceAsync(e.PieceIndex));
        }
    }
    
    private async Task CachePieceAsync(int pieceIndex)
    {
        // Find all files that contain this piece
        var filesForPiece = Files.Where(f => 
            pieceIndex >= f.StartPieceIndex && 
            pieceIndex <= f.EndPieceIndex).ToList();
            
        foreach (var file in filesForPiece)
        {
            // Check if we're currently streaming this file
            if (streamingManager.StreamProvider?.CurrentStream?.File == file)
            {
                // This file is being streamed, so prioritize it for caching
                await EnsureFileInMemoryAsync(file);
            }
        }
        
        // Manage overall cache usage
        await MaintainCacheSizeAsync();
    }
    
    private async Task EnsureFileInMemoryAsync(ITorrentFileInfo file)
    {
        lock (fileStreams)
        {
            if (fileStreams[file] != null)
                return; // Already cached
        }
        
        // Create memory stream for this file
        var stream = new MemoryStream(new byte[file.Length]);
        
        // Read file data from disk into memory
        // This would use the underlying file system in a real implementation
        // For demonstration, we'll assume we have a way to get the file data:
        byte[] buffer = new byte[64 * 1024]; // 64KB chunks
        for (long offset = 0; offset < file.Length; offset += buffer.Length)
        {
            int bytesToRead = (int)Math.Min(buffer.Length, file.Length - offset);
            // In a real implementation, you would read from disk here
            // For example: await diskStorage.ReadAsync(file, offset, buffer, 0, bytesToRead);
            await stream.WriteAsync(buffer, 0, bytesToRead);
        }
        
        // Reset position to beginning
        stream.Position = 0;
        
        // Store the stream
        lock (fileStreams)
        {
            fileStreams[file] = stream;
        }
    }
    
    private async Task MaintainCacheSizeAsync()
    {
        // Calculate current cache size
        long totalCacheSize;
        List<KeyValuePair<ITorrentFileInfo, MemoryStream>> cachedFiles;
        
        lock (fileStreams)
        {
            cachedFiles = fileStreams.Where(kvp => kvp.Value != null).ToList();
            totalCacheSize = cachedFiles.Sum(kvp => kvp.Value.Length);
        }
        
        // If we're over the limit, remove least recently accessed files
        if (totalCacheSize > cacheSizeLimit)
        {
            // Sort by access time (in a real implementation, you would track this)
            // Here we'll just remove randomly until under the limit
            Random rnd = new Random();
            var shuffled = cachedFiles.OrderBy(x => rnd.Next()).ToList();
            
            foreach (var kvp in shuffled)
            {
                // Don't remove the currently streaming file
                if (streamingManager.StreamProvider?.CurrentStream?.File == kvp.Key)
                    continue;
                    
                lock (fileStreams)
                {
                    // Release the memory
                    kvp.Value.Dispose();
                    fileStreams[kvp.Key] = null;
                    
                    // Recalculate size
                    totalCacheSize = fileStreams
                        .Where(pair => pair.Value != null)
                        .Sum(pair => pair.Value.Length);
                        
                    // If we're under the limit, stop removing files
                    if (totalCacheSize <= cacheSizeLimit * 0.8) // Add some hysteresis
                        break;
                }
            }
        }
    }
    
    // ITorrentStorage implementation methods
    
    public bool Exists(ITorrentFileInfo file)
    {
        lock (fileStreams)
        {
            return fileStreams.ContainsKey(file);
        }
    }
    
    public FileInfo GetFileInfo(ITorrentFileInfo file)
    {
        // RAM disk doesn't have real files
        return null;
    }
    
    public IList<ITorrentFileInfo> GetFiles(BitField bitfield, bool includeCached)
    {
        // Include files that are fully cached or have all pieces in the bitfield
        List<ITorrentFileInfo> result = new List<ITorrentFileInfo>();
        
        foreach (var file in Files)
        {
            if (includeCached)
            {
                lock (fileStreams)
                {
                    if (fileStreams[file] != null)
                    {
                        result.Add(file);
                        continue;
                    }
                }
            }
            
            // Check if all pieces of this file are in the bitfield
            bool hasAllPieces = true;
            for (int i = file.StartPieceIndex; i <= file.EndPieceIndex; i++)
            {
                if (!bitfield[i])
                {
                    hasAllPieces = false;
                    break;
                }
            }
            
            if (hasAllPieces)
                result.Add(file);
        }
        
        return result;
    }
    
    public async Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        MemoryStream stream;
        
        lock (fileStreams)
        {
            if (!fileStreams.TryGetValue(file, out stream) || stream == null)
            {
                // If not in memory, read from disk
                // Here we would fall back to disk storage in a real implementation
                return 0;
            }
        }
        
        lock (stream)
        {
            // Position the stream
            stream.Position = offset;
            
            // Read the data
            return stream.Read(buffer, bufferOffset, count);
        }
    }
    
    // Other ITorrentStorage methods similarly implemented...
}
```

### Implementing a Database-Backed Storage

```csharp
public class DatabaseStorage : ITorrentStorage
{
    private readonly string connectionString;
    private readonly string dbTable;
    private readonly Dictionary<ITorrentFileInfo, bool> fileOpenState = new Dictionary<ITorrentFileInfo, bool>();
    private readonly int blockSize = 65536; // 64KB blocks for database storage
    
    public DatabaseStorage(string connectionString, string dbTable, string path, IList<ITorrentFileInfo> files)
    {
        this.connectionString = connectionString;
        this.dbTable = dbTable;
        Path = path;
        Files = files;
        
        // Initialize file states
        foreach (var file in files)
        {
            fileOpenState[file] = false;
        }
        
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
                        TorrentId NVARCHAR(40) NOT NULL,
                        FileId NVARCHAR(255) NOT NULL,
                        BlockIndex INT NOT NULL,
                        Data VARBINARY(MAX) NOT NULL,
                        LastAccessed DATETIME NOT NULL,
                        PRIMARY KEY (TorrentId, FileId, BlockIndex)
                    )";
                
                command.ExecuteNonQuery();
                
                // Create an index on LastAccessed for cache management
                command.CommandText = $@"
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_{dbTable}_LastAccessed')
                    CREATE INDEX IX_{dbTable}_LastAccessed ON {dbTable}(LastAccessed)";
                    
                command.ExecuteNonQuery();
            }
        }
    }
    
    public bool Exists(ITorrentFileInfo file)
    {
        string fileId = GetFileId(file);
        
        using (var connection = new SqlConnection(connectionString))
        {
            connection.Open();
            
            using (var command = connection.CreateCommand())
            {
                // Check if at least one block exists for this file
                command.CommandText = $@"
                    SELECT COUNT(1) FROM {dbTable} 
                    WHERE TorrentId = @torrentId AND FileId = @fileId";
                    
                command.Parameters.AddWithValue("@torrentId", file.TorrentManager.InfoHash.ToHex());
                command.Parameters.AddWithValue("@fileId", fileId);
                
                int blockCount = (int)command.ExecuteScalar();
                return blockCount > 0;
            }
        }
    }
    
    public async Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        string fileId = GetFileId(file);
        int startBlock = (int)(offset / blockSize);
        int endBlock = (int)((offset + count - 1) / blockSize);
        int bytesRead = 0;
        
        using (var connection = new SqlConnection(connectionString))
        {
            await connection.OpenAsync();
            
            // Read each block that contains requested data
            for (int blockIndex = startBlock; blockIndex <= endBlock; blockIndex++)
            {
                long blockOffset = blockIndex * (long)blockSize;
                int offsetInBlock = (int)(offset - blockOffset);
                if (offsetInBlock < 0) offsetInBlock = 0;
                
                int bytesToRead = (int)Math.Min(
                    blockSize - offsetInBlock,
                    count - bytesRead);
                    
                if (bytesToRead <= 0) break;
                
                using (var command = connection.CreateCommand())
                {
                    command.CommandText = $@"
                        SELECT Data FROM {dbTable}
                        WHERE TorrentId = @torrentId AND FileId = @fileId AND BlockIndex = @blockIndex";
                        
                    command.Parameters.AddWithValue("@torrentId", file.TorrentManager.InfoHash.ToHex());
                    command.Parameters.AddWithValue("@fileId", fileId);
                    command.Parameters.AddWithValue("@blockIndex", blockIndex);
                    
                    byte[] blockData = await command.ExecuteScalarAsync() as byte[];
                    
                    if (blockData != null)
                    {
                        int bytesToCopy = Math.Min(bytesToRead, blockData.Length - offsetInBlock);
                        if (bytesToCopy > 0)
                        {
                            Array.Copy(blockData, offsetInBlock, buffer, bufferOffset + bytesRead, bytesToCopy);
                            bytesRead += bytesToCopy;
                        }
                    }
                    
                    // Update LastAccessed
                    command.CommandText = $@"
                        UPDATE {dbTable} SET LastAccessed = GETUTCDATE()
                        WHERE TorrentId = @torrentId AND FileId = @fileId AND BlockIndex = @blockIndex";
                        
                    await command.ExecuteNonQueryAsync();
                }
                
                offset += bytesToRead;
            }
        }
        
        return bytesRead;
    }
    
    public async Task<int> WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        string fileId = GetFileId(file);
        int startBlock = (int)(offset / blockSize);
        int endBlock = (int)((offset + count - 1) / blockSize);
        int bytesWritten = 0;
        
        using (var connection = new SqlConnection(connectionString))
        {
            await connection.OpenAsync();
            
            using (var transaction = connection.BeginTransaction())
            {
                try
                {
                    // Write each block
                    for (int blockIndex = startBlock; blockIndex <= endBlock; blockIndex++)
                    {
                        long blockOffset = blockIndex * (long)blockSize;
                        int offsetInBlock = (int)(offset - blockOffset);
                        if (offsetInBlock < 0) offsetInBlock = 0;
                        
                        int bytesToWrite = (int)Math.Min(
                            blockSize - offsetInBlock,
                            count - bytesWritten);
                            
                        if (bytesToWrite <= 0) break;
                        
                        // First, check if block exists and get current data if it does
                        using (var command = connection.CreateCommand())
                        {
                            command.Transaction = transaction;
                            command.CommandText = $@"
                                SELECT Data FROM {dbTable}
                                WHERE TorrentId = @torrentId AND FileId = @fileId AND BlockIndex = @blockIndex";
                                
                            command.Parameters.AddWithValue("@torrentId", file.TorrentManager.InfoHash.ToHex());
                            command.Parameters.AddWithValue("@fileId", fileId);
                            command.Parameters.AddWithValue("@blockIndex", blockIndex);
                            
                            byte[] existingData = await command.ExecuteScalarAsync() as byte[];
                            byte[] newBlockData;
                            
                            if (existingData != null)
                            {
                                // Update existing block
                                newBlockData = existingData;
                                if (offsetInBlock + bytesToWrite > newBlockData.Length)
                                {
                                    // Need to resize the array
                                    Array.Resize(ref newBlockData, offsetInBlock + bytesToWrite);
                                }
                            }
                            else
                            {
                                // Create new block
                                newBlockData = new byte[offsetInBlock + bytesToWrite];
                            }
                            
                            // Copy data
                            Array.Copy(buffer, bufferOffset + bytesWritten, newBlockData, offsetInBlock, bytesToWrite);
                            
                            // Insert or update the block
                            command.Parameters.Clear();
                            command.CommandText = $@"
                                MERGE {dbTable} AS target
                                USING (SELECT @torrentId, @fileId, @blockIndex) AS source (TorrentId, FileId, BlockIndex)
                                ON (target.TorrentId = source.TorrentId AND 
                                    target.FileId = source.FileId AND 
                                    target.BlockIndex = source.BlockIndex)
                                WHEN MATCHED THEN
                                    UPDATE SET Data = @data, LastAccessed = GETUTCDATE()
                                WHEN NOT MATCHED THEN
                                    INSERT (TorrentId, FileId, BlockIndex, Data, LastAccessed)
                                    VALUES (@torrentId, @fileId, @blockIndex, @data, GETUTCDATE());";
                                    
                            command.Parameters.AddWithValue("@torrentId", file.TorrentManager.InfoHash.ToHex());
                            command.Parameters.AddWithValue("@fileId", fileId);
                            command.Parameters.AddWithValue("@blockIndex", blockIndex);
                            command.Parameters.AddWithValue("@data", newBlockData);
                            
                            await command.ExecuteNonQueryAsync();
                        }
                        
                        bytesWritten += bytesToWrite;
                        offset += bytesToWrite;
                    }
                    
                    transaction.Commit();
                }
                catch
                {
                    transaction.Rollback();
                    throw;
                }
            }
        }
        
        return bytesWritten;
    }
    
    private string GetFileId(ITorrentFileInfo file)
    {
        // Create a unique identifier for this file
        return file.Path.Replace("\\", "/").Replace("'", "''");
    }
    
    // Other ITorrentStorage methods similarly implemented...
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