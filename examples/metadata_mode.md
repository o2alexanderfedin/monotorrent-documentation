# Downloading Metadata Only

This example demonstrates how to use Metadata Mode in MonoTorrent to download only the metadata (torrent structure) without downloading the actual content.

## Contents

- [Understanding Metadata Mode](#understanding-metadata-mode)
- [Using Metadata Mode](#using-metadata-mode)
- [Saving Downloaded Metadata](#saving-downloaded-metadata)
- [Monitoring Metadata Progress](#monitoring-metadata-progress)
- [Working with Retrieved Metadata](#working-with-retrieved-metadata)
- [Complete Example](#complete-example)

## Understanding Metadata Mode

When adding a magnet link to MonoTorrent, the client must first download the torrent metadata before it can begin downloading the actual content. This initial phase is called "Metadata Mode."

Key points about Metadata Mode:

1. It allows downloading just the .torrent information from peers without getting the content
2. After metadata is retrieved, you can examine file structure before deciding to download
3. You can save the retrieved metadata as a .torrent file for later use
4. Metadata download relies on finding peers who have the complete torrent

## Using Metadata Mode

To use Metadata Mode with a magnet link:

```csharp
// Configure the client engine
var engineSettings = new EngineSettings
{
    SavePath = "/path/to/downloads"
};
using var engine = new ClientEngine(engineSettings);

// Parse the magnet link
var magnetLink = new MagnetLink("magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10");

// Add the magnet link to the engine
var manager = await engine.AddAsync(magnetLink, "/path/to/downloads");

// Start the metadata download
await manager.StartAsync();

// Wait for metadata to download
while (!manager.HasMetadata)
{
    Console.WriteLine("Waiting for metadata...");
    await Task.Delay(1000);
}

// Stop after metadata is downloaded (don't proceed to content download)
await manager.StopAsync();

// Now you can work with the metadata
Console.WriteLine($"Metadata downloaded successfully: {manager.Torrent.Name}");
```

## Saving Downloaded Metadata

After downloading metadata, you might want to save it as a .torrent file:

```csharp
// Save the downloaded metadata as a .torrent file
public async Task SaveTorrentFileAsync(TorrentManager manager, string savePath)
{
    if (!manager.HasMetadata)
    {
        throw new InvalidOperationException("Metadata has not been downloaded yet");
    }

    // Create the directory if it doesn't exist
    Directory.CreateDirectory(Path.GetDirectoryName(savePath));

    // Save the torrent
    await manager.Torrent.SaveAsync(savePath);
    Console.WriteLine($"Torrent file saved to: {savePath}");
}

// Usage:
await SaveTorrentFileAsync(manager, "/path/to/save/file.torrent");
```

## Monitoring Metadata Progress

You can monitor the metadata download progress:

```csharp
// Track state changes to monitor metadata download
manager.TorrentStateChanged += (sender, e) => {
    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
    
    if (e.OldState == TorrentState.Metadata && e.NewState == TorrentState.Stopped)
    {
        Console.WriteLine("Metadata download completed and torrent stopped");
    }
};

// Monitor peers to help diagnose metadata download issues
engine.PeerConnected += (sender, e) => {
    if (e.TorrentManager.State == TorrentState.Metadata)
    {
        Console.WriteLine($"Connected to peer while in metadata mode: {e.Peer.ConnectionUri}");
    }
};

engine.PeerDisconnected += (sender, e) => {
    if (e.TorrentManager.State == TorrentState.Metadata)
    {
        Console.WriteLine($"Disconnected from peer while in metadata mode: {e.Peer.ConnectionUri}");
    }
};
```

## Working with Retrieved Metadata

Once metadata is downloaded, you can examine it to make decisions:

```csharp
public void AnalyzeMetadata(TorrentManager manager)
{
    if (!manager.HasMetadata)
    {
        Console.WriteLine("Metadata not available");
        return;
    }

    var torrent = manager.Torrent;
    
    // Basic torrent information
    Console.WriteLine($"Name: {torrent.Name}");
    Console.WriteLine($"Size: {FormatSize(torrent.Size)}");
    Console.WriteLine($"Creation Date: {torrent.CreationDate}");
    Console.WriteLine($"Created By: {torrent.CreatedBy}");
    Console.WriteLine($"Comment: {torrent.Comment}");
    Console.WriteLine($"Private: {torrent.IsPrivate}");
    
    // File information
    Console.WriteLine("\nFiles:");
    foreach (var file in torrent.Files)
    {
        Console.WriteLine($"- {file.Path} ({FormatSize(file.Length)})");
    }
    
    // Check for media files
    bool hasVideo = torrent.Files.Any(f => {
        var ext = Path.GetExtension(f.Path).ToLowerInvariant();
        return new[] { ".mp4", ".mkv", ".avi", ".mov" }.Contains(ext);
    });
    
    Console.WriteLine($"\nContains video files: {hasVideo}");
    
    // Tracker information
    Console.WriteLine("\nTrackers:");
    foreach (var tier in torrent.AnnounceUrls)
    {
        foreach (var tracker in tier)
        {
            Console.WriteLine($"- {tracker}");
        }
    }
    
    // WebSeeds
    if (torrent.WebSeeds.Count > 0)
    {
        Console.WriteLine("\nWebSeeds:");
        foreach (var webSeed in torrent.WebSeeds)
        {
            Console.WriteLine($"- {webSeed}");
        }
    }
}

private string FormatSize(long bytes)
{
    string[] suffixes = { "B", "KB", "MB", "GB", "TB" };
    int i = 0;
    double size = bytes;
    
    while (size >= 1024 && i < suffixes.Length - 1)
    {
        size /= 1024;
        i++;
    }
    
    return $"{size:0.##} {suffixes[i]}";
}
```

## Complete Example

Here's a complete example demonstrating how to use Metadata Mode:

```csharp
public class MetadataModeExample
{
    public static async Task RunAsync()
    {
        // Initialize the engine with DHT enabled for better peer finding
        var engineSettings = new EngineSettings
        {
            SavePath = "/path/to/downloads",
            DhtEndPoint = new IPEndPoint(IPAddress.Any, 55123)
        };
        
        using var engine = new ClientEngine(engineSettings);
        
        // Start DHT to improve peer finding for metadata download
        await engine.DhtEngine.StartAsync();
        Console.WriteLine("DHT started");
        
        // Get a magnet link from the user
        Console.WriteLine("Enter a magnet link:");
        string magnetLinkStr = Console.ReadLine();
        
        try
        {
            // Parse the magnet link
            var magnetLink = new MagnetLink(magnetLinkStr);
            Console.WriteLine($"Processing magnet link: {magnetLink.InfoHash.ToHex()}");
            
            if (!string.IsNullOrEmpty(magnetLink.Name))
            {
                Console.WriteLine($"Name from magnet link: {magnetLink.Name}");
            }
            
            // Register event handlers
            RegisterEventHandlers(engine);
            
            // Add the magnet link
            var manager = await engine.AddAsync(magnetLink, "/path/to/downloads");
            Console.WriteLine("Magnet link added to engine");
            
            // Start the metadata download
            await manager.StartAsync();
            Console.WriteLine("Started metadata download");
            
            // Monitor the metadata download progress
            var timeout = TimeSpan.FromMinutes(2);
            var watch = System.Diagnostics.Stopwatch.StartNew();
            
            while (!manager.HasMetadata && watch.Elapsed < timeout)
            {
                // Display status
                Console.WriteLine($"Metadata download: Connected to {manager.Peers.ConnectedPeers} peers");
                
                // Wait a bit
                await Task.Delay(2000);
            }
            
            // Check if metadata was downloaded
            if (manager.HasMetadata)
            {
                Console.WriteLine("Metadata download complete!");
                
                // Stop the torrent (we only wanted metadata)
                await manager.StopAsync();
                
                // Analyze the metadata
                AnalyzeMetadata(manager);
                
                // Ask if user wants to save the torrent file
                Console.WriteLine("\nDo you want to save the .torrent file? (y/n)");
                if (Console.ReadLine().Trim().ToLower() == "y")
                {
                    string torrentPath = Path.Combine(
                        Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
                        $"{manager.Torrent.Name}.torrent");
                    
                    await manager.Torrent.SaveAsync(torrentPath);
                    Console.WriteLine($"Torrent file saved to: {torrentPath}");
                }
                
                // Ask if user wants to continue downloading
                Console.WriteLine("\nDo you want to begin downloading the content? (y/n)");
                if (Console.ReadLine().Trim().ToLower() == "y")
                {
                    // Start the actual download
                    await manager.StartAsync();
                    Console.WriteLine("Download started");
                    
                    // Monitor progress
                    while (manager.Progress < 100)
                    {
                        Console.WriteLine($"Download progress: {manager.Progress:0.00}%");
                        Console.WriteLine($"Download speed: {FormatSize(manager.Monitor.DownloadRate)}/s");
                        
                        await Task.Delay(1000);
                        
                        // Allow user to cancel
                        if (Console.KeyAvailable && Console.ReadKey(true).Key == ConsoleKey.Escape)
                        {
                            Console.WriteLine("Download cancelled");
                            break;
                        }
                    }
                    
                    // Stop the download
                    await manager.StopAsync();
                }
            }
            else
            {
                Console.WriteLine("Failed to download metadata within the timeout period.");
                Console.WriteLine("Possible reasons:");
                Console.WriteLine("- No peers have this torrent");
                Console.WriteLine("- Network issues");
                Console.WriteLine("- Incorrect InfoHash in magnet link");
            }
            
            // Remove the torrent
            await engine.RemoveAsync(manager);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
        
        // Shutdown the engine
        await engine.StopAllAsync();
        await engine.DhtEngine.StopAsync();
        Console.WriteLine("Engine stopped");
    }
    
    private static void RegisterEventHandlers(ClientEngine engine)
    {
        // Listen for state changes
        engine.TorrentStateChanged += (sender, e) => {
            Console.WriteLine($"State changed: {e.OldState} -> {e.NewState}");
        };
        
        // Listen for peer connections
        engine.PeerConnected += (sender, e) => {
            Console.WriteLine($"Connected to peer: {e.Peer.ConnectionUri}");
        };
        
        // Listen for connection failures
        engine.ConnectionAttemptFailed += (sender, e) => {
            if (e.Reason != ConnectionFailureReason.NoError)
            {
                Console.WriteLine($"Connection failed: {e.Reason}");
            }
        };
    }
    
    private static void AnalyzeMetadata(TorrentManager manager)
    {
        var torrent = manager.Torrent;
        
        Console.WriteLine("\n--- Torrent Metadata Analysis ---");
        Console.WriteLine($"Name: {torrent.Name}");
        Console.WriteLine($"Size: {FormatSize(torrent.Size)}");
        
        if (torrent.CreationDate.HasValue)
        {
            Console.WriteLine($"Creation Date: {torrent.CreationDate.Value}");
        }
        
        if (!string.IsNullOrEmpty(torrent.CreatedBy))
        {
            Console.WriteLine($"Created By: {torrent.CreatedBy}");
        }
        
        if (!string.IsNullOrEmpty(torrent.Comment))
        {
            Console.WriteLine($"Comment: {torrent.Comment}");
        }
        
        Console.WriteLine($"Private Torrent: {torrent.IsPrivate}");
        Console.WriteLine($"Piece Count: {torrent.Pieces.Count}");
        Console.WriteLine($"Piece Length: {FormatSize(torrent.PieceLength)}");
        
        // File analysis
        Console.WriteLine($"\nContains {torrent.Files.Count} files:");
        
        var fileTypes = torrent.Files
            .Select(f => Path.GetExtension(f.Path).ToLowerInvariant())
            .Where(ext => !string.IsNullOrEmpty(ext))
            .GroupBy(ext => ext)
            .OrderByDescending(g => g.Count())
            .Take(5)
            .ToList();
        
        Console.WriteLine("Top file extensions:");
        foreach (var type in fileTypes)
        {
            Console.WriteLine($"- {type.Key}: {type.Count()} files");
        }
        
        // List largest files
        var largestFiles = torrent.Files
            .OrderByDescending(f => f.Length)
            .Take(5)
            .ToList();
        
        Console.WriteLine("\nLargest files:");
        foreach (var file in largestFiles)
        {
            Console.WriteLine($"- {file.Path} ({FormatSize(file.Length)})");
        }
        
        // Tracker information
        Console.WriteLine($"\nTracker Count: {torrent.AnnounceUrls.SelectMany(t => t).Count()}");
        
        var trackerTypes = torrent.AnnounceUrls
            .SelectMany(t => t)
            .Select(url => new Uri(url).Scheme)
            .GroupBy(scheme => scheme)
            .ToDictionary(g => g.Key, g => g.Count());
        
        foreach (var type in trackerTypes)
        {
            Console.WriteLine($"- {type.Key} trackers: {type.Value}");
        }
        
        // WebSeed information
        if (torrent.WebSeeds.Count > 0)
        {
            Console.WriteLine($"\nWebSeeds: {torrent.WebSeeds.Count}");
        }
    }
    
    private static string FormatSize(long bytes)
    {
        string[] suffixes = { "B", "KB", "MB", "GB", "TB" };
        int i = 0;
        double size = bytes;
        
        while (size >= 1024 && i < suffixes.Length - 1)
        {
            size /= 1024;
            i++;
        }
        
        return $"{size:0.##} {suffixes[i]}";
    }
}
```

This example demonstrates a complete workflow for downloading and analyzing torrent metadata, with options to save the .torrent file or continue downloading the content.