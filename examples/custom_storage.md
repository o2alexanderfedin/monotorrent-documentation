# Custom Storage

This example demonstrates how to implement custom storage solutions for MonoTorrent, allowing you to control exactly how and where downloaded data is stored.

## Contents

- [Understanding Storage in MonoTorrent](#understanding-storage-in-monotorrent)
- [Implementing Custom Storage](#implementing-custom-storage)
- [Memory-Based Storage](#memory-based-storage)
- [Hybrid Storage](#hybrid-storage)
- [Database Storage](#database-storage)
- [Complete Example](#complete-example)

## Understanding Storage in MonoTorrent

MonoTorrent uses the `ITorrentStorage` interface to abstract storage operations. By implementing this interface, you can customize how files are read from and written to storage.

The key methods in the interface are:

```csharp
public interface ITorrentStorage : IDisposable
{
    Task<bool> ExistsAsync(ITorrentFileInfo file);
    Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count);
    Task WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count);
    Task MoveAsync(ITorrentFileInfo file, string fullPath);
    Task CloseAsync(ITorrentFileInfo file);
    // Other methods...
}
```

## Implementing Custom Storage

### Basic Implementation

Here's a simplified example of a custom storage implementation:

```csharp
public class CustomStorage : ITorrentStorage
{
    private readonly Dictionary<ITorrentFileInfo, Stream> openStreams = new Dictionary<ITorrentFileInfo, Stream>();
    private readonly string basePath;

    public CustomStorage(string basePath)
    {
        this.basePath = basePath;
    }

    private async Task<Stream> GetStreamAsync(ITorrentFileInfo file)
    {
        if (openStreams.TryGetValue(file, out Stream stream))
            return stream;

        string fullPath = Path.Combine(basePath, file.Path);
        Directory.CreateDirectory(Path.GetDirectoryName(fullPath));

        stream = new FileStream(fullPath, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.Read);
        openStreams.Add(file, stream);
        return stream;
    }

    public async Task<bool> ExistsAsync(ITorrentFileInfo file)
    {
        string fullPath = Path.Combine(basePath, file.Path);
        return File.Exists(fullPath);
    }

    public async Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        Stream stream = await GetStreamAsync(file);
        stream.Position = offset;
        return await stream.ReadAsync(buffer, bufferOffset, count);
    }

    public async Task WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        Stream stream = await GetStreamAsync(file);
        stream.Position = offset;
        await stream.WriteAsync(buffer, bufferOffset, count);
    }

    public async Task MoveAsync(ITorrentFileInfo file, string fullPath)
    {
        await CloseAsync(file);
        string currentPath = Path.Combine(basePath, file.Path);
        Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
        File.Move(currentPath, fullPath);
    }

    public async Task CloseAsync(ITorrentFileInfo file)
    {
        if (openStreams.TryGetValue(file, out Stream stream))
        {
            await stream.FlushAsync();
            stream.Dispose();
            openStreams.Remove(file);
        }
    }

    public void Dispose()
    {
        foreach (var stream in openStreams.Values)
            stream.Dispose();
        
        openStreams.Clear();
    }
}
```

## Memory-Based Storage

For scenarios where you want to keep the data in memory (like small files or testing):

```csharp
public class MemoryStorage : ITorrentStorage
{
    private readonly Dictionary<ITorrentFileInfo, MemoryStream> fileData = 
        new Dictionary<ITorrentFileInfo, MemoryStream>();

    public async Task<bool> ExistsAsync(ITorrentFileInfo file)
    {
        return fileData.ContainsKey(file);
    }

    private MemoryStream GetStream(ITorrentFileInfo file)
    {
        if (!fileData.TryGetValue(file, out var stream))
        {
            stream = new MemoryStream(new byte[file.Length]);
            fileData[file] = stream;
        }
        return stream;
    }

    public async Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        var stream = GetStream(file);
        stream.Position = offset;
        return await stream.ReadAsync(buffer, bufferOffset, count);
    }

    public async Task WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        var stream = GetStream(file);
        stream.Position = offset;
        await stream.WriteAsync(buffer, bufferOffset, count);
    }

    public async Task MoveAsync(ITorrentFileInfo file, string fullPath)
    {
        if (fileData.TryGetValue(file, out var stream))
        {
            // Write memory data to disk
            Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
            using (var fileStream = new FileStream(fullPath, FileMode.Create))
            {
                stream.Position = 0;
                await stream.CopyToAsync(fileStream);
            }
        }
    }

    public async Task CloseAsync(ITorrentFileInfo file)
    {
        // In memory implementation doesn't need explicit close
    }

    public void Dispose()
    {
        foreach (var stream in fileData.Values)
            stream.Dispose();
        
        fileData.Clear();
    }
}
```

## Hybrid Storage

A hybrid approach can store smaller files in memory and larger files on disk:

```csharp
public class HybridStorage : ITorrentStorage
{
    private readonly Dictionary<ITorrentFileInfo, Stream> openStreams = 
        new Dictionary<ITorrentFileInfo, Stream>();
    private readonly string basePath;
    private readonly long memoryThreshold;

    public HybridStorage(string basePath, long memoryThreshold = 1024 * 1024) // Default 1MB
    {
        this.basePath = basePath;
        this.memoryThreshold = memoryThreshold;
    }

    private bool ShouldBeInMemory(ITorrentFileInfo file)
    {
        return file.Length <= memoryThreshold;
    }

    private async Task<Stream> GetStreamAsync(ITorrentFileInfo file)
    {
        if (openStreams.TryGetValue(file, out Stream stream))
            return stream;

        if (ShouldBeInMemory(file))
        {
            stream = new MemoryStream(new byte[file.Length]);
        }
        else
        {
            string fullPath = Path.Combine(basePath, file.Path);
            Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
            stream = new FileStream(fullPath, FileMode.OpenOrCreate, FileAccess.ReadWrite);
        }

        openStreams.Add(file, stream);
        return stream;
    }

    // Implement other ITorrentStorage methods similar to previous examples
    // but check if it's a memory stream or file stream before operations
}
```

## Database Storage

For more advanced scenarios, you could store torrent data in a database:

```csharp
public class DatabaseStorage : ITorrentStorage
{
    private readonly string connectionString;
    
    public DatabaseStorage(string connectionString)
    {
        this.connectionString = connectionString;
    }
    
    public async Task<bool> ExistsAsync(ITorrentFileInfo file)
    {
        using (var connection = new SqlConnection(connectionString))
        {
            await connection.OpenAsync();
            var cmd = new SqlCommand(
                "SELECT COUNT(*) FROM TorrentBlocks WHERE FileId = @FileId", 
                connection);
            cmd.Parameters.AddWithValue("@FileId", GetFileId(file));
            return (int)await cmd.ExecuteScalarAsync() > 0;
        }
    }
    
    public async Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        // Implement database read logic
        // This would typically involve reading blocks from a BLOB column
    }
    
    public async Task WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        // Implement database write logic
        // This would typically involve writing blocks to a BLOB column
    }
    
    // Implement other methods...
    
    private string GetFileId(ITorrentFileInfo file)
    {
        // Create a unique ID for the file based on the torrent and file path
        return $"{file.Torrent.InfoHash.ToHex()}_{file.Path}";
    }
}
```

## Complete Example

Here's a complete example showing how to use custom storage:

```csharp
public class CustomStorageExample
{
    public static async Task RunAsync()
    {
        // Create custom storage factory
        var storageFactory = new CustomStorageFactory();

        // Create engine settings with custom storage
        var engineSettings = new EngineSettings
        {
            SavePath = "/path/to/downloads",
            CreateTorrentStorage = storageFactory.CreateStorage
        };

        // Create the client engine
        using var engine = new ClientEngine(engineSettings);

        // Load torrent
        var torrent = await Torrent.LoadAsync("example.torrent");
        
        // Add torrent with custom storage
        var manager = await engine.AddAsync(torrent, "/path/to/downloads");
        
        // Start downloading
        await manager.StartAsync();
        
        // Wait for download to complete
        while (manager.State != TorrentState.Seeding)
        {
            Console.WriteLine($"Progress: {manager.Progress:0.00}%");
            await Task.Delay(1000);
        }
        
        // Clean up
        await engine.StopAllAsync();
    }
}

// Custom storage factory
public class CustomStorageFactory
{
    public ITorrentStorage CreateStorage(ITorrentManagerInfo manager)
    {
        // Based on torrent characteristics, select appropriate storage
        if (manager.Files.All(f => f.Length < 10 * 1024 * 1024)) // All files < 10MB
        {
            Console.WriteLine("Using memory storage");
            return new MemoryStorage();
        }
        else if (manager.Files.Any(f => IsMediaFile(f.Path)))
        {
            Console.WriteLine("Using hybrid storage for media torrent");
            return new HybridStorage(manager.SavePath);
        }
        else
        {
            Console.WriteLine("Using standard storage");
            return new CustomStorage(manager.SavePath);
        }
    }
    
    private bool IsMediaFile(string path)
    {
        var ext = Path.GetExtension(path).ToLowerInvariant();
        return new[] { ".mp4", ".mkv", ".mp3", ".avi" }.Contains(ext);
    }
}
```

This example demonstrates different storage strategies and how to select the appropriate one based on the torrent characteristics.