# Downloading Files with MonoTorrent

This tutorial provides a comprehensive guide to downloading files using MonoTorrent. You'll learn how to set up a client, add torrents, and manage downloads effectively.

## Prerequisites

Before starting this tutorial, make sure you have:

- Installed MonoTorrent via NuGet or from source
- Basic understanding of C# and async programming
- A .torrent file or magnet link to test with

## Setting Up the Client

The first step is to create a `ClientEngine` that will manage the downloads:

```csharp
using MonoTorrent;
using MonoTorrent.Client;
using System;
using System.Threading.Tasks;

// Create engine settings
var engineSettings = new EngineSettings
{
    SavePath = "/path/to/downloads",  // Where files will be saved
    ListenPort = 55123,               // Port to listen on for incoming connections
    MaximumConnections = 150,         // Maximum number of connections
    MaximumDownloadRate = 0,          // No download rate limit (in bytes/sec)
    MaximumUploadRate = 0             // No upload rate limit (in bytes/sec)
};

// Create the client engine
using var engine = new ClientEngine(engineSettings);

Console.WriteLine("Engine created and initialized");
```

## Adding a Torrent

You can add a torrent from either a .torrent file or a magnet link:

### From a .torrent File

```csharp
// Load a torrent from a file
var torrent = await Torrent.LoadAsync("path/to/your/file.torrent");

// Add the torrent to the engine
var torrentManager = await engine.AddAsync(torrent, "/path/to/downloads");

Console.WriteLine($"Added torrent: {torrent.Name}");
```

### From a Magnet Link

```csharp
// Parse a magnet link
var magnetLink = new MagnetLink("magnet:?xt=urn:btih:HASH&dn=NAME&tr=TRACKER");

// Add the magnet link to the engine
var torrentManager = await engine.AddAsync(magnetLink, "/path/to/downloads");

Console.WriteLine("Added magnet link to the engine");
```

## Starting the Download

Once you've added a torrent, you can start downloading:

```csharp
// Start the download
await torrentManager.StartAsync();

Console.WriteLine("Download started");
```

## Monitoring Download Progress

It's important to track the progress of your downloads:

```csharp
// Register event handlers
torrentManager.TorrentStateChanged += (sender, e) => {
    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
    
    if (e.NewState == TorrentState.Seeding)
    {
        Console.WriteLine("Download completed!");
    }
};

// Monitor progress in a loop
while (torrentManager.State != TorrentState.Seeding)
{
    Console.WriteLine($"Progress: {torrentManager.Progress:0.00}%");
    Console.WriteLine($"Download Speed: {torrentManager.Monitor.DownloadRate / 1024.0:0.00} KB/s");
    Console.WriteLine($"Upload Speed: {torrentManager.Monitor.UploadRate / 1024.0:0.00} KB/s");
    Console.WriteLine($"Peers: {torrentManager.Peers.ConnectedPeers}");
    
    await Task.Delay(1000);  // Update every second
    
    // Optionally, allow the user to cancel
    if (Console.KeyAvailable && Console.ReadKey(true).Key == ConsoleKey.Escape)
    {
        await torrentManager.StopAsync();
        Console.WriteLine("Download cancelled");
        break;
    }
}
```

## Managing Multiple Downloads

To manage multiple torrents at once:

```csharp
// Add multiple torrents
var torrent1 = await Torrent.LoadAsync("path/to/torrent1.torrent");
var torrent2 = await Torrent.LoadAsync("path/to/torrent2.torrent");

var manager1 = await engine.AddAsync(torrent1, "/path/to/downloads");
var manager2 = await engine.AddAsync(torrent2, "/path/to/downloads");

// Start all torrents
await manager1.StartAsync();
await manager2.StartAsync();

// Or use the engine's methods to manage all torrents
await engine.StartAllAsync();  // Start all torrents
// await engine.StopAllAsync();   // Stop all torrents
// await engine.PauseAllAsync();  // Pause all torrents

// Track overall download rates
while (manager1.State != TorrentState.Seeding || 
       manager2.State != TorrentState.Seeding)
{
    Console.WriteLine("==== Torrent Status ====");
    DisplayTorrentStatus(manager1);
    DisplayTorrentStatus(manager2);
    Console.WriteLine($"Total Download: {engine.TotalDownloadRate / 1024.0:0.00} KB/s");
    Console.WriteLine($"Total Upload: {engine.TotalUploadRate / 1024.0:0.00} KB/s");
    
    await Task.Delay(1000);
}

void DisplayTorrentStatus(TorrentManager manager)
{
    Console.WriteLine($"- {manager.Torrent.Name}:");
    Console.WriteLine($"  Progress: {manager.Progress:0.00}%");
    Console.WriteLine($"  State: {manager.State}");
    Console.WriteLine($"  Download: {manager.Monitor.DownloadRate / 1024.0:0.00} KB/s");
}
```

## Controlling Download Priority

You can prioritize certain files within a torrent:

```csharp
// Set priorities for specific files
for (int i = 0; i < torrentManager.Torrent.Files.Count; i++)
{
    var file = torrentManager.Torrent.Files[i];
    
    if (file.Path.EndsWith(".mp4") || file.Path.EndsWith(".mkv"))
    {
        // High priority for video files
        await torrentManager.SetFilePriorityAsync(file, Priority.High);
    }
    else if (file.Path.EndsWith(".txt") || file.Path.EndsWith(".nfo"))
    {
        // Low priority for text files
        await torrentManager.SetFilePriorityAsync(file, Priority.Low);
    }
    else if (file.Path.Contains("sample"))
    {
        // Skip sample files
        await torrentManager.SetFilePriorityAsync(file, Priority.DoNotDownload);
    }
}
```

## Pausing and Resuming Downloads

You can pause and resume downloads as needed:

```csharp
// Pause a download
await torrentManager.PauseAsync();
Console.WriteLine("Download paused");

// Wait a bit
await Task.Delay(5000);

// Resume the download
await torrentManager.StartAsync();
Console.WriteLine("Download resumed");
```

## Stopping Downloads

When you're done, properly stop the downloads and dispose resources:

```csharp
// Stop a specific torrent
await torrentManager.StopAsync();
Console.WriteLine("Download stopped");

// Stop all torrents and dispose the engine
await engine.StopAllAsync();
Console.WriteLine("All downloads stopped");

// The engine will be disposed by the 'using' statement
```

## Handling Errors

Handle potential errors during the download process:

```csharp
// Subscribe to the error event
torrentManager.TorrentStateChanged += (sender, e) => {
    if (e.NewState == TorrentState.Error)
    {
        var manager = (TorrentManager)sender;
        Console.WriteLine($"Error: {manager.Error.Exception.Message}");
        
        // Attempt to restart after a delay
        Task.Run(async () => {
            await Task.Delay(TimeSpan.FromSeconds(30));
            try
            {
                await manager.StartAsync();
                Console.WriteLine("Restarted after error");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to restart: {ex.Message}");
            }
        });
    }
};
```

## Complete Example

Here's a complete example that puts everything together:

```csharp
using MonoTorrent;
using MonoTorrent.Client;
using System;
using System.Linq;
using System.Threading.Tasks;

public class DownloadExample
{
    public static async Task RunAsync(string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: DownloadExample <path_to_torrent_or_magnet_link>");
            return;
        }

        string input = args[0];
        string downloadPath = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        downloadPath = System.IO.Path.Combine(downloadPath, "Downloads");
        
        // Create engine settings
        var engineSettings = new EngineSettings
        {
            SavePath = downloadPath,
            ListenPort = 55123
        };
        
        // Create the client engine
        using var engine = new ClientEngine(engineSettings);
        Console.WriteLine($"Engine created. Downloading to: {downloadPath}");
        
        // Add the torrent
        TorrentManager manager;
        
        if (input.StartsWith("magnet:"))
        {
            // From magnet link
            var magnetLink = new MagnetLink(input);
            manager = await engine.AddAsync(magnetLink, downloadPath);
            Console.WriteLine("Added magnet link. Downloading metadata...");
        }
        else
        {
            // From torrent file
            var torrent = await Torrent.LoadAsync(input);
            manager = await engine.AddAsync(torrent, downloadPath);
            Console.WriteLine($"Added torrent: {torrent.Name}");
        }
        
        // Register event handlers
        RegisterEventHandlers(manager);
        
        // Start the download
        await manager.StartAsync();
        Console.WriteLine("Download started");
        
        // Wait for metadata if it's a magnet link
        if (!manager.HasMetadata)
        {
            Console.WriteLine("Waiting for metadata...");
            while (!manager.HasMetadata)
            {
                Console.Write(".");
                await Task.Delay(500);
            }
            Console.WriteLine("\nMetadata downloaded!");
            
            // Now we can show the torrent information
            Console.WriteLine($"Torrent name: {manager.Torrent.Name}");
            Console.WriteLine($"Torrent size: {FormatSize(manager.Torrent.Size)}");
            Console.WriteLine($"File count: {manager.Torrent.Files.Count}");
        }
        
        // Main monitoring loop
        bool running = true;
        Console.WriteLine("\nPress ESC to stop, P to pause/resume, I for info");
        
        while (running)
        {
            // Display progress information
            Console.SetCursorPosition(0, Console.CursorTop);
            Console.Write($"Progress: {manager.Progress:0.00}% | State: {manager.State} | DL: {FormatSize(manager.Monitor.DownloadRate)}/s | UL: {FormatSize(manager.Monitor.UploadRate)}/s | Peers: {manager.Peers.ConnectedPeers}      ");
            
            // Check for user input
            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true);
                switch (key.Key)
                {
                    case ConsoleKey.Escape:
                        running = false;
                        break;
                    
                    case ConsoleKey.P:
                        if (manager.State == TorrentState.Downloading || manager.State == TorrentState.Seeding)
                        {
                            await manager.PauseAsync();
                            Console.WriteLine("\nDownload paused");
                        }
                        else if (manager.State == TorrentState.Paused)
                        {
                            await manager.StartAsync();
                            Console.WriteLine("\nDownload resumed");
                        }
                        break;
                    
                    case ConsoleKey.I:
                        DisplayDetailedInfo(manager);
                        break;
                }
            }
            
            // Exit if download is complete
            if (manager.State == TorrentState.Seeding)
            {
                Console.WriteLine("\nDownload completed successfully!");
                break;
            }
            
            await Task.Delay(1000);
        }
        
        // Stop the download and clean up
        await manager.StopAsync();
        await engine.StopAllAsync();
        Console.WriteLine("Download stopped. Press any key to exit.");
        Console.ReadKey();
    }
    
    private static void RegisterEventHandlers(TorrentManager manager)
    {
        // Track state changes
        manager.TorrentStateChanged += (sender, e) => {
            Console.WriteLine($"\nState changed: {e.OldState} -> {e.NewState}");
            
            if (e.NewState == TorrentState.Seeding && e.OldState == TorrentState.Downloading)
            {
                Console.WriteLine("Download completed successfully!");
            }
            else if (e.NewState == TorrentState.Error)
            {
                Console.WriteLine($"Error: {manager.Error.Exception.Message}");
            }
        };
        
        // Track tracker updates
        manager.TrackerManager.AnnounceComplete += (sender, e) => {
            if (e.Successful)
            {
                Console.WriteLine($"\nTracker update successful. Received {e.Peers.Count} peers.");
            }
            else
            {
                Console.WriteLine($"\nTracker update failed: {e.Failure}");
            }
        };
    }
    
    private static void DisplayDetailedInfo(TorrentManager manager)
    {
        Console.WriteLine("\n=== Torrent Information ===");
        Console.WriteLine($"Name: {manager.Torrent?.Name ?? "Unknown (metadata not yet available)"}");
        
        if (manager.HasMetadata)
        {
            Console.WriteLine($"Size: {FormatSize(manager.Torrent.Size)}");
            Console.WriteLine($"Files: {manager.Torrent.Files.Count}");
            Console.WriteLine($"Pieces: {manager.Torrent.Pieces.Count} ({FormatSize(manager.Torrent.PieceLength)} each)");
            Console.WriteLine($"Private: {manager.Torrent.IsPrivate}");
            
            // Display the first few files
            Console.WriteLine("\nFiles:");
            foreach (var file in manager.Torrent.Files.Take(5))
            {
                Console.WriteLine($"- {file.Path} ({FormatSize(file.Length)})");
            }
            
            if (manager.Torrent.Files.Count > 5)
            {
                Console.WriteLine($"... and {manager.Torrent.Files.Count - 5} more");
            }
        }
        
        // Connection information
        Console.WriteLine("\nConnection Information:");
        Console.WriteLine($"Download Speed: {FormatSize(manager.Monitor.DownloadRate)}/s");
        Console.WriteLine($"Upload Speed: {FormatSize(manager.Monitor.UploadRate)}/s");
        Console.WriteLine($"Data Downloaded: {FormatSize(manager.Monitor.DataBytesReceived)}");
        Console.WriteLine($"Data Uploaded: {FormatSize(manager.Monitor.DataBytesSent)}");
        Console.WriteLine($"Connected Peers: {manager.Peers.ConnectedPeers}");
        Console.WriteLine($"Seeds: {manager.Peers.Seeds}");
        Console.WriteLine($"Leechers: {manager.Peers.Leechs}");
        
        // Estimate remaining time
        if (manager.Monitor.DownloadRate > 0)
        {
            long remainingBytes = manager.Torrent.Size - manager.Monitor.DataBytesReceived;
            double secondsRemaining = remainingBytes / manager.Monitor.DownloadRate;
            var timeRemaining = TimeSpan.FromSeconds(secondsRemaining);
            
            Console.WriteLine("\nEstimated time remaining: " + 
                (timeRemaining.TotalHours >= 1 ? $"{timeRemaining.TotalHours:0.0} hours" : 
                (timeRemaining.TotalMinutes >= 1 ? $"{timeRemaining.TotalMinutes:0.0} minutes" : 
                $"{timeRemaining.TotalSeconds:0.0} seconds")));
        }
        
        Console.WriteLine("\nPress any key to continue...");
        Console.ReadKey(true);
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

## Advanced Considerations

### Rate Limiting

Control bandwidth usage with:

```csharp
// Limit global rates
engineSettings.MaximumDownloadRate = 2 * 1024 * 1024; // 2 MB/s
engineSettings.MaximumUploadRate = 1024 * 1024;       // 1 MB/s

// Or per-torrent limits
var torrentSettings = new TorrentSettings();
torrentSettings.MaximumDownloadRate = 1 * 1024 * 1024; // 1 MB/s
torrentSettings.MaximumUploadRate = 512 * 1024;        // 512 KB/s

// Apply to a specific torrent
var manager = await engine.AddAsync(torrent, "/path/to/downloads", torrentSettings);
```

### Fast Resume Data

Save and load fast resume data to quickly restart torrents without rehashing:

```csharp
// Save fast resume data when stopping
await engine.SaveFastResumeAsync();

// Load fast resume data when starting
await engine.LoadFastResumeAsync();
```

### Selective File Download

Choose which files to download from a torrent:

```csharp
// After adding the torrent but before starting it
foreach (var file in manager.Torrent.Files)
{
    if (file.Path.EndsWith(".mp4") || file.Path.EndsWith(".mkv"))
    {
        // Download video files
        await manager.SetFilePriorityAsync(file, Priority.Normal);
    }
    else
    {
        // Skip all other files
        await manager.SetFilePriorityAsync(file, Priority.DoNotDownload);
    }
}

// Now start the download
await manager.StartAsync();
```

## Conclusion

This tutorial has covered the essential aspects of downloading files with MonoTorrent. You've learned how to:

1. Set up a client engine
2. Add torrents from files and magnet links
3. Start, monitor, pause, and stop downloads
4. Manage multiple torrents
5. Control download priorities
6. Handle errors
7. Implement bandwidth limiting
8. Use fast resume data
9. Selectively download files

With these skills, you can build robust BitTorrent applications for a variety of use cases. Refer to other tutorials and the API reference for more advanced topics and examples.

## Related Resources

- [Simple Client Tutorial](simple_client_tutorial.md)
- [Custom Storage Tutorial](custom_storage_tutorial.md)
- [TorrentManager API Reference](../api_reference/client/TorrentManager.md)
- [ClientEngine API Reference](../api_reference/client/ClientEngine.md)