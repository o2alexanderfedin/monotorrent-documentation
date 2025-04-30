# Basic Usage Guide for MonoTorrent

This guide covers the fundamental operations in MonoTorrent to help you get started quickly.

## Initializing the Client Engine

The `ClientEngine` is the core component of MonoTorrent. You'll need to create it first:

```csharp
using MonoTorrent;
using MonoTorrent.Client;

// Create engine settings
var settings = new EngineSettings
{
    MaximumDownloadRate = 1024 * 1024, // 1 MB/s
    MaximumUploadRate = 512 * 1024,    // 512 KB/s
    ListenPort = 55123                 // Port for incoming connections
};

// Create the client engine
var engine = new ClientEngine(settings);
```

## Loading a Torrent

You can load torrents from .torrent files or magnet links:

### From a .torrent File

```csharp
// Path to the .torrent file
string torrentPath = @"C:\Downloads\ubuntu.torrent";

// Path where files will be downloaded
string downloadPath = @"C:\Downloads\";

// Create a torrent manager for this torrent
var torrentManager = await engine.AddAsync(torrentPath, downloadPath);
```

### From a Magnet Link

```csharp
// A magnet link
string magnetLink = "magnet:?xt=urn:btih:HASH&dn=Ubuntu&tr=http://tracker.example.org/announce";

// Create a torrent manager for this magnet link
var torrentManager = await engine.AddAsync(MagnetLink.Parse(magnetLink), downloadPath);
```

## Starting and Stopping Downloads

```csharp
// Start downloading the torrent
await torrentManager.StartAsync();

// Later, pause the torrent
await torrentManager.PauseAsync();

// Resume the torrent
await torrentManager.StartAsync();

// Stop the torrent completely
await torrentManager.StopAsync();
```

## Monitoring Download Progress

You can monitor the progress of a torrent download through properties and events:

```csharp
// Check the current state
Console.WriteLine($"State: {torrentManager.State}");

// Check download progress
Console.WriteLine($"Progress: {torrentManager.Progress:0.00}%");

// Check download/upload speeds
Console.WriteLine($"Download Speed: {torrentManager.Monitor.DownloadRate / 1024.0:0.00} KB/s");
Console.WriteLine($"Upload Speed: {torrentManager.Monitor.UploadRate / 1024.0:0.00} KB/s");

// Subscribe to events
torrentManager.TorrentStateChanged += (sender, e) => 
{
    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
};

torrentManager.PieceHashed += (sender, e) => 
{
    Console.WriteLine($"Piece {e.PieceIndex} hashed. Valid: {e.HashPassed}");
};
```

## Managing Multiple Torrents

The `ClientEngine` can manage multiple torrents simultaneously:

```csharp
// Add several torrents
var torrent1 = await engine.AddAsync("file1.torrent", downloadPath);
var torrent2 = await engine.AddAsync("file2.torrent", downloadPath);
var torrent3 = await engine.AddAsync(MagnetLink.Parse(magnetLink), downloadPath);

// Start all torrents
await torrent1.StartAsync();
await torrent2.StartAsync();
await torrent3.StartAsync();

// Or use the engine to start all torrents
await engine.StartAllAsync();

// Later, stop all torrents
await engine.StopAllAsync();
```

## Working with Files in a Torrent

You can examine and control individual files within a torrent:

```csharp
// Get the list of files in the torrent
var files = torrentManager.Files;

// Display information about each file
foreach (var file in files)
{
    Console.WriteLine($"File: {file.Path}");
    Console.WriteLine($"Size: {file.Length / (1024.0 * 1024.0):0.00} MB");
    Console.WriteLine($"Priority: {file.Priority}");
    Console.WriteLine();
}

// Set priorities for specific files
files[0].Priority = Priority.High;      // Download this file first
files[1].Priority = Priority.Normal;    // Normal priority
files[2].Priority = Priority.DoNotDownload;  // Skip this file
```

## Using Trackers

MonoTorrent automatically handles tracker communication, but you can monitor and control it:

```csharp
// Get the list of trackers
var trackers = torrentManager.TrackerManager.Trackers;

// Display information about each tracker
foreach (var tracker in trackers)
{
    Console.WriteLine($"Tracker: {tracker.Uri}");
    Console.WriteLine($"Status: {tracker.Status}");
    Console.WriteLine($"Warning Message: {tracker.WarningMessage}");
    Console.WriteLine($"Failure Message: {tracker.FailureMessage}");
    Console.WriteLine();
}

// Manually update a tracker
await tracker.AnnounceAsync();
```

## Saving and Resuming Downloads

MonoTorrent supports saving and loading download progress using FastResume data:

```csharp
// Save fast resume data
byte[] resumeData = await torrentManager.SaveFastResumeAsync();
File.WriteAllBytes($"{torrentManager.InfoHash}.fastresume", resumeData);

// Later, when you want to resume the download
byte[] loadedResumeData = File.ReadAllBytes($"{infoHash}.fastresume");
await torrentManager.LoadFastResumeAsync(loadedResumeData);
```

## Shutting Down

When your application is closing, properly dispose of the engine:

```csharp
// Stop all active torrents
await engine.StopAllAsync();

// Dispose the engine
await engine.DisposeAsync();
```

## Complete Example

Here's a complete example that puts everything together:

```csharp
using System;
using System.IO;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace MonoTorrentExample
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Create settings for the engine
            var settings = new EngineSettings
            {
                MaximumDownloadRate = 1024 * 1024,  // 1 MB/s
                MaximumUploadRate = 512 * 1024,     // 512 KB/s
                ListenPort = 55123                  // Port for incoming connections
            };

            // Create the client engine
            var engine = new ClientEngine(settings);
            
            try
            {
                // The path to the .torrent file
                string torrentPath = @"C:\Downloads\ubuntu.torrent";
                
                // The path where files will be downloaded
                string downloadPath = @"C:\Downloads\";
                
                // Create a torrent manager for this torrent
                var torrentManager = await engine.AddAsync(torrentPath, downloadPath);
                
                // Subscribe to events
                torrentManager.TorrentStateChanged += (sender, e) => 
                {
                    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
                };
                
                // Start downloading the torrent
                await torrentManager.StartAsync();
                
                // Display progress in a loop
                while (torrentManager.State != TorrentState.Seeding)
                {
                    // Display current status
                    Console.WriteLine($"Progress: {torrentManager.Progress:0.00}%");
                    Console.WriteLine($"Download Speed: {torrentManager.Monitor.DownloadRate / 1024.0:0.00} KB/s");
                    Console.WriteLine($"Upload Speed: {torrentManager.Monitor.UploadRate / 1024.0:0.00} KB/s");
                    Console.WriteLine($"Peers: {torrentManager.Peers.AvailablePeers.Count}");
                    
                    // Wait a second before updating again
                    await Task.Delay(1000);
                }
                
                Console.WriteLine("Download complete! Seeding...");
                
                // Wait for user input to stop
                Console.WriteLine("Press Enter to stop seeding and exit");
                Console.ReadLine();
                
                // Stop the torrent and dispose the engine
                await torrentManager.StopAsync();
                await engine.DisposeAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                await engine.DisposeAsync();
            }
        }
    }
}
```

This basic example should help you get started with MonoTorrent. For more advanced features like DHT, streaming, and custom piece pickers, refer to the Advanced Usage guide.