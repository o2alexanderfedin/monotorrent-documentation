# Tutorial: Implementing Custom Storage in MonoTorrent

This tutorial guides you through creating a custom storage system for MonoTorrent. Instead of storing files on disk, we'll implement an in-memory storage solution that can be useful for temporary torrents, testing, or specialized applications.

## Prerequisites

- Understanding of C# and .NET
- Familiarity with MonoTorrent basics
- Knowledge of torrents and how they work

## Introduction

By default, MonoTorrent stores downloaded data directly to files on disk. However, in some scenarios, you might want to:

- Store data in memory for fast access
- Implement encrypted storage
- Store data in a database or cloud service
- Create virtual file systems
- Implement deduplication or other storage optimizations

MonoTorrent provides extension points for custom storage through interfaces like `ITorrentFileInfo` and `ITorrentStorage`. In this tutorial, we'll implement a complete in-memory storage solution.

## Step 1: Define the Custom File Implementation

First, we'll create a custom implementation of `ITorrentFileInfo` to represent a file stored in memory:

```csharp
using System;
using System.Collections.Generic;
using MonoTorrent;
using MonoTorrent.Client;

/// <summary>
/// Represents a torrent file that is stored in memory rather than on disk.
/// </summary>
public class MemoryTorrentFile : ITorrentFileInfo
{
    // Properties required by ITorrentFileInfo interface
    public string FullPath { get; }
    public long Length { get; }
    public string Path { get; }
    public Priority Priority { get; set; }
    public int StartPieceIndex { get; set; }
    public int EndPieceIndex { get; set; }
    public BitField BitField { get; }
    public double Progress => BitField.PercentComplete;
    public ReadOnlyMemory<byte> MD5 { get; }
    public ReadOnlyMemory<byte> SHA1 { get; }
    public ReadOnlyMemory<byte> ED2K { get; }

    // Additional properties for memory storage
    public byte[] Data { get; }

    public MemoryTorrentFile(TorrentFile torrentFile, string baseDirectory)
    {
        // Initialize from the original TorrentFile
        FullPath = torrentFile.FullPath;
        Path = torrentFile.Path;
        Length = torrentFile.Length;
        Priority = Priority.Normal;
        StartPieceIndex = torrentFile.StartPieceIndex;
        EndPieceIndex = torrentFile.EndPieceIndex;
        
        // Create a BitField to track which pieces of this file we have
        int pieceCount = EndPieceIndex - StartPieceIndex + 1;
        BitField = new BitField(pieceCount);
        
        // Allocate memory for the file data
        Data = new byte[Length];
        
        // Copy hash information
        MD5 = torrentFile.MD5;
        SHA1 = torrentFile.SHA1;
        ED2K = torrentFile.ED2K;
    }
}
```

## Step 2: Create a Memory Storage Manager

Next, we'll implement the `ITorrentStorage` interface to handle storing and retrieving data from memory:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

/// <summary>
/// A custom storage implementation that keeps all torrent data in memory.
/// </summary>
public class MemoryStorage : ITorrentStorage
{
    private readonly List<MemoryTorrentFile> files;
    private readonly int pieceLength;
    private readonly long totalSize;

    public MemoryStorage(IList<TorrentFile> torrentFiles, int pieceLength, string baseDirectory)
    {
        this.pieceLength = pieceLength;
        this.files = new List<MemoryTorrentFile>();
        
        foreach (var file in torrentFiles)
        {
            files.Add(new MemoryTorrentFile(file, baseDirectory));
            totalSize += file.Length;
        }
    }

    public List<ITorrentFileInfo> Files => new List<ITorrentFileInfo>(files);

    public Task CloseAsync()
    {
        // Nothing to close in memory storage
        return Task.CompletedTask;
    }

    public Task<bool> ExistsAsync()
    {
        // Memory storage always "exists"
        return Task.FromResult(true);
    }

    public Task FlushAsync()
    {
        // Nothing to flush in memory storage
        return Task.CompletedTask;
    }

    public Task MoveAsync(string newRoot)
    {
        // Memory storage doesn't support moving
        return Task.CompletedTask;
    }

    public Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        // Find the file in our list
        var memoryFile = GetMemoryFile(file);
        if (memoryFile == null)
            return Task.FromResult(0);

        // Make sure we don't read past the end of the file
        count = (int)Math.Min(count, memoryFile.Length - offset);
        if (count <= 0)
            return Task.FromResult(0);

        // Copy data from our memory buffer to the provided buffer
        Array.Copy(memoryFile.Data, offset, buffer, bufferOffset, count);
        return Task.FromResult(count);
    }

    public Task<bool> WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        // Find the file in our list
        var memoryFile = GetMemoryFile(file);
        if (memoryFile == null)
            return Task.FromResult(false);

        // Make sure we don't write past the end of the file
        count = (int)Math.Min(count, memoryFile.Length - offset);
        if (count <= 0)
            return Task.FromResult(true);

        // Copy data from the provided buffer to our memory buffer
        Array.Copy(buffer, bufferOffset, memoryFile.Data, offset, count);
        
        // Update the bitfield to mark pieces as complete
        UpdateBitfield(memoryFile, offset, count);
        
        return Task.FromResult(true);
    }

    private MemoryTorrentFile GetMemoryFile(ITorrentFileInfo file)
    {
        foreach (var memoryFile in files)
        {
            if (memoryFile.Path == file.Path && memoryFile.Length == file.Length)
                return memoryFile;
        }
        
        return null;
    }

    private void UpdateBitfield(MemoryTorrentFile file, long offset, int count)
    {
        // Calculate the piece indexes that this write affects
        int firstPiece = (int)(offset / pieceLength);
        int lastPiece = (int)((offset + count - 1) / pieceLength);
        
        // This is a simplified approach - in a real implementation,
        // you would need to track which parts of each piece are complete
        // and only mark the piece complete when all parts are written.
        for (int i = firstPiece; i <= lastPiece; i++)
        {
            int globalPieceIndex = file.StartPieceIndex + i;
            int localPieceIndex = globalPieceIndex - file.StartPieceIndex;
            
            if (localPieceIndex >= 0 && localPieceIndex < file.BitField.Length)
            {
                file.BitField[localPieceIndex] = true;
            }
        }
    }
}
```

## Step 3: Implement the Storage Factory

Now we need a factory class to create our custom storage:

```csharp
using System.Collections.Generic;
using MonoTorrent;
using MonoTorrent.Client;

/// <summary>
/// Factory for creating memory-based torrent storage.
/// </summary>
public class MemoryStorageFactory : ITorrentStorageFactory
{
    public ITorrentStorage Create(Torrent torrent, string savePath)
    {
        return new MemoryStorage(torrent.Files, torrent.PieceLength, savePath);
    }
}
```

## Step 4: Create a TorrentManager with Custom Storage

With our custom storage implementation ready, we can now create a `TorrentManager` that uses it:

```csharp
using System;
using System.IO;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

class Program
{
    static async Task Main(string[] args)
    {
        // Create engine settings
        var settings = new EngineSettings();
        
        // Create the client engine
        using var engine = new ClientEngine(settings);
        
        // Load a torrent file
        string torrentPath = "path/to/your/torrent.torrent";
        var torrent = await Torrent.LoadAsync(torrentPath);
        
        // Create our memory storage factory
        var storageFactory = new MemoryStorageFactory();
        
        // Create a TorrentManager with custom storage
        var manager = new TorrentManager(
            torrent,                   // The torrent
            "unused-download-path",    // Download path (unused with memory storage)
            new TorrentSettings(),     // Torrent settings
            storageFactory             // Our custom storage factory
        );
        
        // Register with the engine
        await engine.RegisterAsync(manager);
        
        // Start the torrent
        await manager.StartAsync();
        
        // Wait for download to complete
        while (manager.State != TorrentState.Seeding)
        {
            Console.WriteLine($"Progress: {manager.Progress:F2}%");
            Console.WriteLine($"Download Speed: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
            Console.WriteLine($"Upload Speed: {manager.Monitor.UploadRate / 1024:F2} KB/s");
            Console.WriteLine($"Peers: {manager.Peers.ConnectedPeers.Count}");
            Console.WriteLine();
            
            await Task.Delay(1000);
        }
        
        Console.WriteLine("Download complete! Data is stored in memory.");
        
        // Now we can access the data in memory
        foreach (var file in manager.Files)
        {
            if (file is ITorrentFileInfo torrentFileInfo)
            {
                // Get the memory file
                var memoryFile = ((MemoryStorage)manager.TorrentStorage).Files
                    .Find(f => f.Path == torrentFileInfo.Path);
                
                if (memoryFile is MemoryTorrentFile memory)
                {
                    Console.WriteLine($"File: {memory.Path}");
                    Console.WriteLine($"Size: {memory.Length} bytes");
                    Console.WriteLine($"First 10 bytes: {BytesToHex(memory.Data, 0, Math.Min(10, memory.Data.Length))}");
                    Console.WriteLine();
                }
            }
        }
        
        // Clean up
        await engine.UnregisterAsync(manager);
    }
    
    static string BytesToHex(byte[] bytes, int offset, int count)
    {
        return BitConverter.ToString(bytes, offset, count).Replace("-", " ");
    }
}
```

## Step 5: Enhancing the Memory Storage

Our basic implementation works, but it lacks some features that would make it more useful. Let's enhance it:

### 5.1. Add Data Persistence

Let's add the ability to save and load the memory storage to a file:

```csharp
public class MemoryStorage : ITorrentStorage
{
    // Add these methods to the MemoryStorage class

    /// <summary>
    /// Saves the current state of the in-memory storage to a file.
    /// </summary>
    public void SaveToFile(string filePath)
    {
        using var fileStream = File.Create(filePath);
        using var writer = new BinaryWriter(fileStream);
        
        // Write the number of files
        writer.Write(files.Count);
        
        // Write each file
        foreach (var file in files)
        {
            writer.Write(file.Path);
            writer.Write(file.Length);
            writer.Write(file.Data.Length);
            writer.Write(file.Data);
        }
    }
    
    /// <summary>
    /// Loads the state of the in-memory storage from a file.
    /// </summary>
    public static MemoryStorage LoadFromFile(string filePath, IList<TorrentFile> torrentFiles, int pieceLength, string baseDirectory)
    {
        var storage = new MemoryStorage(torrentFiles, pieceLength, baseDirectory);
        
        using var fileStream = File.OpenRead(filePath);
        using var reader = new BinaryReader(fileStream);
        
        // Read the number of files
        int fileCount = reader.ReadInt32();
        
        // Read each file
        for (int i = 0; i < fileCount; i++)
        {
            string path = reader.ReadString();
            long length = reader.ReadInt64();
            int dataLength = reader.ReadInt32();
            byte[] data = reader.ReadBytes(dataLength);
            
            // Find the corresponding file in our storage
            var memoryFile = storage.files.Find(f => f.Path == path && f.Length == length);
            if (memoryFile != null)
            {
                // Copy the data
                Array.Copy(data, memoryFile.Data, Math.Min(data.Length, memoryFile.Data.Length));
                
                // Update the bitfield
                for (int pieceIndex = memoryFile.StartPieceIndex; pieceIndex <= memoryFile.EndPieceIndex; pieceIndex++)
                {
                    int localPieceIndex = pieceIndex - memoryFile.StartPieceIndex;
                    memoryFile.BitField[localPieceIndex] = true;
                }
            }
        }
        
        return storage;
    }
}
```

### 5.2. Add Memory Limitations

Let's add memory usage limits to avoid out-of-memory errors:

```csharp
public class MemoryStorage : ITorrentStorage
{
    // Add these fields and properties
    private readonly long _maxMemoryUsage;
    private long _currentMemoryUsage;
    
    public long MaxMemoryUsage => _maxMemoryUsage;
    public long CurrentMemoryUsage => _currentMemoryUsage;
    
    // Update the constructor
    public MemoryStorage(IList<TorrentFile> torrentFiles, int pieceLength, string baseDirectory, long maxMemoryUsage = long.MaxValue)
    {
        this.pieceLength = pieceLength;
        this.files = new List<MemoryTorrentFile>();
        this._maxMemoryUsage = maxMemoryUsage;
        
        foreach (var file in torrentFiles)
        {
            files.Add(new MemoryTorrentFile(file, baseDirectory));
            totalSize += file.Length;
        }
        
        // Check if the total size exceeds our memory limit
        if (totalSize > maxMemoryUsage)
        {
            throw new ArgumentException($"Total torrent size ({totalSize} bytes) exceeds maximum memory usage limit ({maxMemoryUsage} bytes)");
        }
        
        _currentMemoryUsage = totalSize;
    }
    
    // Update the WriteAsync method
    public Task<bool> WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        // Find the file in our list
        var memoryFile = GetMemoryFile(file);
        if (memoryFile == null)
            return Task.FromResult(false);
        
        // Make sure we don't write past the end of the file
        count = (int)Math.Min(count, memoryFile.Length - offset);
        if (count <= 0)
            return Task.FromResult(true);
        
        // Copy data from the provided buffer to our memory buffer
        Array.Copy(buffer, bufferOffset, memoryFile.Data, offset, count);
        
        // Update the bitfield to mark pieces as complete
        UpdateBitfield(memoryFile, offset, count);
        
        return Task.FromResult(true);
    }
}
```

## Step 6: Using the Enhanced Memory Storage

Let's create a complete example showing how to use our enhanced memory storage:

```csharp
using System;
using System.IO;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

class Program
{
    static async Task Main(string[] args)
    {
        // Create engine settings
        var settings = new EngineSettings();
        
        // Create the client engine
        using var engine = new ClientEngine(settings);
        
        // Load a torrent file
        string torrentPath = "path/to/your/torrent.torrent";
        var torrent = await Torrent.LoadAsync(torrentPath);
        
        // Set a memory limit (e.g., 1 GB)
        long memoryLimit = 1L * 1024 * 1024 * 1024;
        
        try
        {
            // Create our memory storage factory with memory limits
            var storageFactory = new CustomMemoryStorageFactory(memoryLimit);
            
            // Create a TorrentManager with custom storage
            var manager = new TorrentManager(
                torrent,                   // The torrent
                "unused-download-path",    // Download path (unused with memory storage)
                new TorrentSettings(),     // Torrent settings
                storageFactory             // Our custom storage factory
            );
            
            // Register with the engine
            await engine.RegisterAsync(manager);
            
            // Subscribe to events
            manager.TorrentStateChanged += (sender, e) => {
                Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
                
                if (e.NewState == TorrentState.Seeding)
                {
                    Console.WriteLine("Download complete! Data is stored in memory.");
                    
                    // Save the memory storage to a file
                    if (manager.TorrentStorage is MemoryStorage storage)
                    {
                        string savePath = $"{torrent.Name}.memstore";
                        storage.SaveToFile(savePath);
                        Console.WriteLine($"Memory storage saved to {savePath}");
                    }
                }
            };
            
            // Start the torrent
            await manager.StartAsync();
            
            // Display progress until complete
            while (manager.State != TorrentState.Seeding)
            {
                Console.WriteLine($"Progress: {manager.Progress:F2}%");
                Console.WriteLine($"Download Speed: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
                Console.WriteLine($"Upload Speed: {manager.Monitor.UploadRate / 1024:F2} KB/s");
                Console.WriteLine($"Peers: {manager.Peers.ConnectedPeers.Count}");
                
                if (manager.TorrentStorage is MemoryStorage memStorage)
                {
                    Console.WriteLine($"Memory Usage: {FormatSize(memStorage.CurrentMemoryUsage)} / {FormatSize(memStorage.MaxMemoryUsage)}");
                }
                
                Console.WriteLine();
                
                await Task.Delay(1000);
            }
            
            // Wait for user input before exiting
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
            
            // Stop the torrent
            await manager.StopAsync();
            
            // Unregister from the engine
            await engine.UnregisterAsync(manager);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
    
    static string FormatSize(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;
        
        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len = len / 1024;
        }
        
        return $"{len:0.##} {sizes[order]}";
    }
}

// Updated storage factory
public class CustomMemoryStorageFactory : ITorrentStorageFactory
{
    private readonly long _maxMemoryUsage;
    
    public CustomMemoryStorageFactory(long maxMemoryUsage)
    {
        _maxMemoryUsage = maxMemoryUsage;
    }
    
    public ITorrentStorage Create(Torrent torrent, string savePath)
    {
        string memoryStoragePath = $"{torrent.Name}.memstore";
        
        // Check if we have a saved memory storage
        if (File.Exists(memoryStoragePath))
        {
            try
            {
                // Try to load from the file
                return MemoryStorage.LoadFromFile(memoryStoragePath, torrent.Files, torrent.PieceLength, savePath);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to load memory storage: {ex.Message}");
                // Fall back to creating a new storage
            }
        }
        
        // Create a new memory storage
        return new MemoryStorage(torrent.Files, torrent.PieceLength, savePath, _maxMemoryUsage);
    }
}
```

## Step 7: Advanced Usage - Hybrid Storage

Let's implement a hybrid storage system that keeps small files in memory but stores large files on disk:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

/// <summary>
/// A hybrid storage implementation that keeps small files in memory and large files on disk.
/// </summary>
public class HybridStorage : ITorrentStorage
{
    private readonly List<ITorrentFileInfo> files = new List<ITorrentFileInfo>();
    private readonly Dictionary<string, byte[]> memoryFiles = new Dictionary<string, byte[]>();
    private readonly string baseDirectory;
    private readonly int pieceLength;
    private readonly long memoryThreshold;

    public HybridStorage(IList<TorrentFile> torrentFiles, int pieceLength, string baseDirectory, long memoryThreshold = 10 * 1024 * 1024) // Default: 10 MB
    {
        this.pieceLength = pieceLength;
        this.baseDirectory = baseDirectory;
        this.memoryThreshold = memoryThreshold;
        
        // Process each file
        foreach (var file in torrentFiles)
        {
            if (file.Length <= memoryThreshold)
            {
                // Small file - store in memory
                var memoryFile = new MemoryTorrentFile(file, baseDirectory);
                files.Add(memoryFile);
                memoryFiles[memoryFile.Path] = memoryFile.Data;
            }
            else
            {
                // Large file - store on disk
                string fullPath = Path.Combine(baseDirectory, file.Path);
                
                // Create directory if it doesn't exist
                Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
                
                // Create file if it doesn't exist
                if (!File.Exists(fullPath))
                {
                    using var stream = File.Create(fullPath);
                    stream.SetLength(file.Length);
                }
                
                // Add the file info
                files.Add(new TorrentFileInfo(file, baseDirectory));
            }
        }
    }

    public List<ITorrentFileInfo> Files => files;

    public Task CloseAsync()
    {
        // Nothing to close
        return Task.CompletedTask;
    }

    public Task<bool> ExistsAsync()
    {
        // Check if all disk files exist
        bool allExist = true;
        
        foreach (var file in files)
        {
            if (!IsMemoryFile(file))
            {
                if (!File.Exists(file.FullPath))
                {
                    allExist = false;
                    break;
                }
            }
        }
        
        return Task.FromResult(allExist);
    }

    public Task FlushAsync()
    {
        // Nothing to flush
        return Task.CompletedTask;
    }

    public Task MoveAsync(string newRoot)
    {
        // Move disk files and update paths
        foreach (var file in files)
        {
            if (!IsMemoryFile(file))
            {
                string oldPath = file.FullPath;
                string relativePath = file.Path;
                string newPath = Path.Combine(newRoot, relativePath);
                
                // Create directory if it doesn't exist
                Directory.CreateDirectory(Path.GetDirectoryName(newPath));
                
                // Move the file
                if (File.Exists(oldPath))
                {
                    File.Move(oldPath, newPath, true);
                }
            }
        }
        
        return Task.CompletedTask;
    }

    public Task<int> ReadAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        if (IsMemoryFile(file))
        {
            // Read from memory
            byte[] data = memoryFiles[file.Path];
            
            // Make sure we don't read past the end of the file
            count = (int)Math.Min(count, file.Length - offset);
            if (count <= 0)
                return Task.FromResult(0);
            
            // Copy data from our memory buffer to the provided buffer
            Array.Copy(data, offset, buffer, bufferOffset, count);
            return Task.FromResult(count);
        }
        else
        {
            // Read from disk
            using var stream = new FileStream(file.FullPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            stream.Position = offset;
            return Task.FromResult(stream.Read(buffer, bufferOffset, count));
        }
    }

    public Task<bool> WriteAsync(ITorrentFileInfo file, long offset, byte[] buffer, int bufferOffset, int count)
    {
        if (IsMemoryFile(file))
        {
            // Write to memory
            byte[] data = memoryFiles[file.Path];
            
            // Make sure we don't write past the end of the file
            count = (int)Math.Min(count, file.Length - offset);
            if (count <= 0)
                return Task.FromResult(true);
            
            // Copy data from the provided buffer to our memory buffer
            Array.Copy(buffer, bufferOffset, data, offset, count);
            
            return Task.FromResult(true);
        }
        else
        {
            // Write to disk
            using var stream = new FileStream(file.FullPath, FileMode.Open, FileAccess.Write, FileShare.Read);
            stream.Position = offset;
            stream.Write(buffer, bufferOffset, count);
            
            return Task.FromResult(true);
        }
    }

    private bool IsMemoryFile(ITorrentFileInfo file)
    {
        return memoryFiles.ContainsKey(file.Path);
    }
}

/// <summary>
/// Factory for creating hybrid storage.
/// </summary>
public class HybridStorageFactory : ITorrentStorageFactory
{
    private readonly long _memoryThreshold;
    
    public HybridStorageFactory(long memoryThreshold = 10 * 1024 * 1024) // Default: 10 MB
    {
        _memoryThreshold = memoryThreshold;
    }
    
    public ITorrentStorage Create(Torrent torrent, string savePath)
    {
        return new HybridStorage(torrent.Files, torrent.PieceLength, savePath, _memoryThreshold);
    }
}
```

## Step 8: Working with the Downloaded Data

Once the data is downloaded, you'll want to use it. Here's how to work with the data in our custom storage:

```csharp
// Function to access downloaded data from memory storage
static async Task ProcessMemoryStorageData(TorrentManager manager)
{
    if (manager.TorrentStorage is MemoryStorage memoryStorage)
    {
        foreach (var file in manager.Files)
        {
            // Get the memory file
            var memoryFile = memoryStorage.Files
                .OfType<MemoryTorrentFile>()
                .FirstOrDefault(f => f.Path == file.Path);
            
            if (memoryFile != null)
            {
                Console.WriteLine($"Processing file: {memoryFile.Path}");
                
                // For this example, let's convert text files to uppercase
                if (Path.GetExtension(memoryFile.Path).ToLower() == ".txt")
                {
                    // Get the file data
                    byte[] data = memoryFile.Data;
                    
                    // Convert to string
                    string text = System.Text.Encoding.UTF8.GetString(data);
                    
                    // Process the text
                    string processed = text.ToUpper();
                    
                    // Convert back to bytes
                    byte[] processedData = System.Text.Encoding.UTF8.GetBytes(processed);
                    
                    // Make sure it fits in the original buffer
                    if (processedData.Length <= data.Length)
                    {
                        Array.Copy(processedData, data, processedData.Length);
                        
                        // If the new data is shorter, fill the rest with zeros
                        if (processedData.Length < data.Length)
                        {
                            Array.Fill<byte>(data, 0, processedData.Length, data.Length - processedData.Length);
                        }
                        
                        Console.WriteLine("File processed successfully.");
                    }
                    else
                    {
                        Console.WriteLine("Processed data too large for original buffer.");
                    }
                }
                // For image files, let's save them to disk
                else if (IsImageFile(memoryFile.Path))
                {
                    string outputPath = Path.Combine("output", memoryFile.Path);
                    
                    // Create directory if it doesn't exist
                    Directory.CreateDirectory(Path.GetDirectoryName(outputPath));
                    
                    // Save the image to disk
                    await File.WriteAllBytesAsync(outputPath, memoryFile.Data);
                    
                    Console.WriteLine($"Image saved to: {outputPath}");
                }
            }
        }
    }
    else if (manager.TorrentStorage is HybridStorage hybridStorage)
    {
        // Process files from hybrid storage...
    }
}

static bool IsImageFile(string path)
{
    string ext = Path.GetExtension(path).ToLower();
    return ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".gif" || ext == ".bmp";
}
```

## Conclusion

In this tutorial, you've learned how to:

1. Create a custom memory-based storage implementation for MonoTorrent
2. Implement the necessary interfaces and classes
3. Configure MonoTorrent to use your custom storage
4. Enhance the storage with features like persistence and memory limits
5. Create a hybrid storage system for optimal performance
6. Work with the downloaded data in your custom storage

Custom storage implementations allow you to tailor MonoTorrent to your specific needs, whether you're building a temporary file cache, creating a secure storage system, or implementing advanced features like deduplication or content-addressed storage.

### Next Steps

Now that you've mastered custom storage in MonoTorrent, you might want to explore:

1. **Encrypted Storage**: Add encryption to protect the stored data
2. **Database Storage**: Store torrent data in SQL or NoSQL databases
3. **Cloud Storage**: Implement storage backed by cloud providers
4. **Content-Addressed Storage**: Create a deduplication system based on content hashes
5. **Virtual File System**: Build a mountable virtual file system from torrents

Each of these extensions builds on the principles you've learned in this tutorial.