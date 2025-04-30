# Tutorial: Creating a Simple BitTorrent Client

This tutorial will guide you through creating a basic BitTorrent client application using MonoTorrent. We'll build a simple console application that can download torrents, display progress information, and manage multiple downloads.

## Prerequisites

- Basic knowledge of C# and .NET
- .NET 6.0 SDK or later installed
- Visual Studio, Visual Studio Code, or another .NET IDE

## Step 1: Create a New Project

First, let's create a new console application:

```bash
dotnet new console -n SimpleTorrentClient
cd SimpleTorrentClient
```

## Step 2: Add MonoTorrent Package Reference

Add the MonoTorrent NuGet package to your project:

```bash
dotnet add package MonoTorrent
```

## Step 3: Set Up the Basic Structure

Create the basic structure for your application by editing `Program.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace SimpleTorrentClient
{
    class Program
    {
        // The engine used to manage all torrents
        private static ClientEngine engine;
        
        // List of torrent managers (one per torrent)
        private static List<TorrentManager> torrents = new List<TorrentManager>();
        
        // Path where downloaded files will be stored
        private static string downloadDirectory;
        
        // Cancellation token source for the main loop
        private static CancellationTokenSource cancellation;
        
        static async Task Main(string[] args)
        {
            // Initialize the client
            await InitializeClientAsync();
            
            // Start the main program loop
            await RunClientAsync();
            
            // Clean up resources when exiting
            await ShutdownClientAsync();
        }
        
        static async Task InitializeClientAsync()
        {
            Console.WriteLine("Initializing BitTorrent client...");
            
            // TODO: Initialize the engine and settings
        }
        
        static async Task RunClientAsync()
        {
            Console.WriteLine("BitTorrent client is running.");
            
            // TODO: Implement the main program loop
        }
        
        static async Task ShutdownClientAsync()
        {
            Console.WriteLine("Shutting down...");
            
            // TODO: Clean up resources
        }
    }
}
```

## Step 4: Initialize the BitTorrent Engine

Now, let's implement the `InitializeClientAsync` method to set up the MonoTorrent engine:

```csharp
static async Task InitializeClientAsync()
{
    Console.WriteLine("Initializing BitTorrent client...");
    
    // Create the downloads directory if it doesn't exist
    downloadDirectory = Path.Combine(Environment.CurrentDirectory, "Downloads");
    Directory.CreateDirectory(downloadDirectory);
    
    // Configure the engine settings
    var engineSettings = new EngineSettings
    {
        MaximumDownloadRate = 0,            // No download rate limit
        MaximumUploadRate = 250 * 1024,     // 250 KB/s upload limit
        ListenPort = 55123,                 // Port for incoming connections
        AllowedEncryption = EncryptionTypes.All
    };
    
    // Create the engine
    engine = new ClientEngine(engineSettings);
    
    Console.WriteLine("BitTorrent engine initialized.");
    Console.WriteLine($"Listening on port: {engineSettings.ListenPort}");
    Console.WriteLine($"Download directory: {downloadDirectory}");
    Console.WriteLine();
}
```

## Step 5: Implement the Main Program Loop

Next, let's implement the main program loop that displays a menu and handles user input:

```csharp
static async Task RunClientAsync()
{
    Console.WriteLine("BitTorrent client is running.");
    
    // Create cancellation token for the display task
    cancellation = new CancellationTokenSource();
    
    // Start a background task to display progress
    _ = DisplayProgressAsync(cancellation.Token);
    
    bool exit = false;
    while (!exit)
    {
        Console.WriteLine("\nCommands:");
        Console.WriteLine("1. Add Torrent");
        Console.WriteLine("2. Add Magnet Link");
        Console.WriteLine("3. Start All");
        Console.WriteLine("4. Pause All");
        Console.WriteLine("5. Stop All");
        Console.WriteLine("6. Remove Torrent");
        Console.WriteLine("7. Exit");
        Console.Write("\nEnter command (1-7): ");
        
        string input = Console.ReadLine();
        Console.WriteLine();
        
        switch (input)
        {
            case "1":
                await AddTorrentAsync();
                break;
                
            case "2":
                await AddMagnetLinkAsync();
                break;
                
            case "3":
                await StartAllTorrentsAsync();
                break;
                
            case "4":
                await PauseAllTorrentsAsync();
                break;
                
            case "5":
                await StopAllTorrentsAsync();
                break;
                
            case "6":
                await RemoveTorrentAsync();
                break;
                
            case "7":
                exit = true;
                break;
                
            default:
                Console.WriteLine("Invalid command. Please try again.");
                break;
        }
    }
    
    // Signal the display task to stop
    cancellation.Cancel();
}
```

## Step 6: Implement the Display Task

Now, let's implement the task that displays download progress:

```csharp
static async Task DisplayProgressAsync(CancellationToken token)
{
    while (!token.IsCancellationRequested)
    {
        if (torrents.Count > 0)
        {
            Console.Clear();
            Console.WriteLine("=== Torrent Status ===");
            Console.WriteLine();
            
            // Display global stats
            Console.WriteLine($"Global Download: {engine.TotalDownloadRate / 1024:F2} KB/s");
            Console.WriteLine($"Global Upload: {engine.TotalUploadRate / 1024:F2} KB/s");
            Console.WriteLine();
            
            // Display stats for each torrent
            for (int i = 0; i < torrents.Count; i++)
            {
                var manager = torrents[i];
                string name = manager.Torrent?.Name ?? manager.InfoHash.ToHex();
                
                Console.WriteLine($"[{i + 1}] {name}");
                Console.WriteLine($"    State: {manager.State}");
                Console.WriteLine($"    Progress: {manager.Progress:F2}%");
                Console.WriteLine($"    Download: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
                Console.WriteLine($"    Upload: {manager.Monitor.UploadRate / 1024:F2} KB/s");
                
                // Calculate and display ETA if downloading
                if (manager.State == TorrentState.Downloading && manager.Monitor.DownloadRate > 0)
                {
                    double remainingBytes = manager.Torrent?.Size * (100 - manager.Progress) / 100 ?? 0;
                    TimeSpan eta = TimeSpan.FromSeconds(remainingBytes / manager.Monitor.DownloadRate);
                    Console.WriteLine($"    ETA: {eta.Hours:D2}:{eta.Minutes:D2}:{eta.Seconds:D2}");
                }
                
                Console.WriteLine($"    Peers: {manager.Peers.ConnectedPeers.Count}");
                Console.WriteLine();
            }
            
            Console.WriteLine("Press any key to show menu...");
        }
        
        // Update every second
        await Task.Delay(1000, token);
    }
}
```

## Step 7: Implement Torrent Operations

Now, let's implement the methods for adding, starting, pausing, and removing torrents:

```csharp
static async Task AddTorrentAsync()
{
    Console.Write("Enter path to .torrent file: ");
    string path = Console.ReadLine().Trim('"'); // Remove quotes if user copied a path with quotes
    
    try
    {
        if (!File.Exists(path))
        {
            Console.WriteLine("Error: File not found.");
            return;
        }
        
        // Add the torrent to the engine
        var manager = await engine.AddAsync(path, downloadDirectory);
        torrents.Add(manager);
        
        Console.WriteLine($"Added torrent: {manager.Torrent.Name}");
        
        // Ask if the user wants to start the torrent immediately
        Console.Write("Start downloading now? (y/n): ");
        string response = Console.ReadLine().ToLower();
        
        if (response == "y" || response == "yes")
        {
            await manager.StartAsync();
            Console.WriteLine("Torrent started.");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error adding torrent: {ex.Message}");
    }
}

static async Task AddMagnetLinkAsync()
{
    Console.Write("Enter magnet link: ");
    string link = Console.ReadLine();
    
    try
    {
        // Parse and validate the magnet link
        var magnetLink = MagnetLink.Parse(link);
        
        // Add the magnet link to the engine
        var manager = await engine.AddAsync(magnetLink, downloadDirectory);
        torrents.Add(manager);
        
        Console.WriteLine($"Added magnet link with hash: {manager.InfoHash.ToHex()}");
        
        // Ask if the user wants to start the torrent immediately
        Console.Write("Start downloading now? (y/n): ");
        string response = Console.ReadLine().ToLower();
        
        if (response == "y" || response == "yes")
        {
            await manager.StartAsync();
            Console.WriteLine("Torrent started.");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error adding magnet link: {ex.Message}");
    }
}

static async Task StartAllTorrentsAsync()
{
    if (torrents.Count == 0)
    {
        Console.WriteLine("No torrents to start.");
        return;
    }
    
    try
    {
        await engine.StartAllAsync();
        Console.WriteLine("All torrents started.");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error starting torrents: {ex.Message}");
    }
}

static async Task PauseAllTorrentsAsync()
{
    if (torrents.Count == 0)
    {
        Console.WriteLine("No torrents to pause.");
        return;
    }
    
    try
    {
        foreach (var manager in torrents)
        {
            await manager.PauseAsync();
        }
        Console.WriteLine("All torrents paused.");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error pausing torrents: {ex.Message}");
    }
}

static async Task StopAllTorrentsAsync()
{
    if (torrents.Count == 0)
    {
        Console.WriteLine("No torrents to stop.");
        return;
    }
    
    try
    {
        await engine.StopAllAsync();
        Console.WriteLine("All torrents stopped.");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error stopping torrents: {ex.Message}");
    }
}

static async Task RemoveTorrentAsync()
{
    if (torrents.Count == 0)
    {
        Console.WriteLine("No torrents to remove.");
        return;
    }
    
    Console.WriteLine("Select a torrent to remove:");
    
    for (int i = 0; i < torrents.Count; i++)
    {
        var manager = torrents[i];
        string name = manager.Torrent?.Name ?? manager.InfoHash.ToHex();
        Console.WriteLine($"[{i + 1}] {name}");
    }
    
    Console.Write("\nEnter torrent number: ");
    if (!int.TryParse(Console.ReadLine(), out int index) || index < 1 || index > torrents.Count)
    {
        Console.WriteLine("Invalid selection.");
        return;
    }
    
    var torrentManager = torrents[index - 1];
    
    Console.Write("Delete downloaded files? (y/n): ");
    bool deleteFiles = Console.ReadLine().ToLower() == "y";
    
    try
    {
        // Stop the torrent first
        await torrentManager.StopAsync();
        
        // Remove from the engine
        await engine.RemoveAsync(torrentManager);
        
        // Remove from our list
        torrents.Remove(torrentManager);
        
        // Optionally delete files
        if (deleteFiles)
        {
            foreach (var file in torrentManager.Files)
            {
                string fullPath = Path.Combine(downloadDirectory, file.Path);
                if (File.Exists(fullPath))
                {
                    File.Delete(fullPath);
                }
            }
            
            // Try to clean up empty directories
            CleanEmptyDirectories(downloadDirectory);
        }
        
        Console.WriteLine("Torrent removed successfully.");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error removing torrent: {ex.Message}");
    }
}

static void CleanEmptyDirectories(string directory)
{
    try
    {
        foreach (var dir in Directory.GetDirectories(directory))
        {
            CleanEmptyDirectories(dir);
            
            if (Directory.GetFiles(dir).Length == 0 && 
                Directory.GetDirectories(dir).Length == 0)
            {
                Directory.Delete(dir);
            }
        }
    }
    catch (Exception)
    {
        // Ignore errors in directory cleanup
    }
}
```

## Step 8: Implement Cleanup

Finally, let's implement the shutdown method to clean up resources:

```csharp
static async Task ShutdownClientAsync()
{
    Console.WriteLine("Shutting down...");
    
    try
    {
        // Stop all active torrents
        if (engine != null)
        {
            await engine.StopAllAsync();
            
            // Save fast resume data for each torrent
            string resumeDataPath = Path.Combine(Environment.CurrentDirectory, "ResumeData");
            Directory.CreateDirectory(resumeDataPath);
            
            foreach (var manager in torrents)
            {
                try
                {
                    // Save the fast resume data
                    byte[] resumeData = await manager.SaveFastResumeAsync();
                    File.WriteAllBytes(
                        Path.Combine(resumeDataPath, $"{manager.InfoHash.ToHex()}.fresume"),
                        resumeData);
                    
                    // If this is a magnet link that has metadata now, save the .torrent file
                    if (manager.HasMetadata && !manager.HasTorrent)
                    {
                        byte[] metadata = await manager.GetMetadataAsync();
                        File.WriteAllBytes(
                            Path.Combine(resumeDataPath, $"{manager.InfoHash.ToHex()}.torrent"),
                            metadata);
                    }
                }
                catch
                {
                    // Ignore errors saving individual torrent data
                }
            }
            
            // Dispose the engine
            await engine.DisposeAsync();
        }
        
        Console.WriteLine("Shutdown complete.");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error during shutdown: {ex.Message}");
    }
}
```

## Step 9: Add Support for Resuming Downloads

Let's enhance the initialization method to load previously saved torrents:

```csharp
static async Task InitializeClientAsync()
{
    Console.WriteLine("Initializing BitTorrent client...");
    
    // Create the downloads directory if it doesn't exist
    downloadDirectory = Path.Combine(Environment.CurrentDirectory, "Downloads");
    Directory.CreateDirectory(downloadDirectory);
    
    // Configure the engine settings
    var engineSettings = new EngineSettings
    {
        MaximumDownloadRate = 0,            // No download rate limit
        MaximumUploadRate = 250 * 1024,     // 250 KB/s upload limit
        ListenPort = 55123,                 // Port for incoming connections
        AllowedEncryption = EncryptionTypes.All
    };
    
    // Create the engine
    engine = new ClientEngine(engineSettings);
    
    // Check for saved torrents and resume data
    string resumeDataPath = Path.Combine(Environment.CurrentDirectory, "ResumeData");
    if (Directory.Exists(resumeDataPath))
    {
        Console.WriteLine("Loading saved torrents...");
        
        // Look for .torrent files
        foreach (string torrentFile in Directory.GetFiles(resumeDataPath, "*.torrent"))
        {
            try
            {
                // Extract the info hash from the filename
                string infoHashHex = Path.GetFileNameWithoutExtension(torrentFile);
                
                // Load the torrent
                var torrent = await Torrent.LoadAsync(torrentFile);
                var manager = await engine.AddAsync(torrent, downloadDirectory);
                torrents.Add(manager);
                
                // Check for fast resume data
                string resumeFile = Path.Combine(resumeDataPath, $"{infoHashHex}.fresume");
                if (File.Exists(resumeFile))
                {
                    byte[] resumeData = File.ReadAllBytes(resumeFile);
                    await manager.LoadFastResumeAsync(resumeData);
                }
                
                Console.WriteLine($"Loaded torrent: {torrent.Name}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading torrent: {ex.Message}");
            }
        }
    }
    
    Console.WriteLine("BitTorrent engine initialized.");
    Console.WriteLine($"Listening on port: {engineSettings.ListenPort}");
    Console.WriteLine($"Download directory: {downloadDirectory}");
    Console.WriteLine();
}
```

## Step 10: Enhancing the Client with Events

Let's add event handling to track torrent state changes and completed downloads:

```csharp
static void RegisterTorrentEvents(TorrentManager manager)
{
    // Track state changes
    manager.TorrentStateChanged += (s, e) => 
    {
        Console.WriteLine($"\nTorrent '{manager.Torrent?.Name ?? manager.InfoHash.ToHex()}' changed state:");
        Console.WriteLine($"Old State: {e.OldState}, New State: {e.NewState}");
        
        // If the torrent just completed, show a notification
        if (e.NewState == TorrentState.Seeding && e.OldState != TorrentState.Seeding)
        {
            Console.WriteLine($"\n*** Download Complete: {manager.Torrent?.Name ?? manager.InfoHash.ToHex()} ***\n");
        }
    };
    
    // Track piece hashing for detailed progress
    manager.PieceHashed += (s, e) => 
    {
        if (!e.HashPassed)
        {
            Console.WriteLine($"\nPiece hash failed for torrent '{manager.Torrent?.Name ?? manager.InfoHash.ToHex()}'");
            Console.WriteLine($"Piece index: {e.PieceIndex}");
        }
    };
}
```

Now, we need to call this method whenever we add a torrent. Add this to both the `AddTorrentAsync` and `AddMagnetLinkAsync` methods after adding the torrent:

```csharp
RegisterTorrentEvents(manager);
```

Also add it to the loading of saved torrents in `InitializeClientAsync`:

```csharp
RegisterTorrentEvents(manager);
```

## Step 11: Build and Run the Application

Build and run your application:

```bash
dotnet build
dotnet run
```

You should now have a functional BitTorrent client capable of:
- Adding and downloading torrents from .torrent files and magnet links
- Displaying download progress and statistics
- Pausing, resuming, and stopping torrents
- Removing torrents and optionally deleting downloaded files
- Saving state between sessions for resuming downloads

## Complete Code

Here's the complete code for the application:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace SimpleTorrentClient
{
    class Program
    {
        // The engine used to manage all torrents
        private static ClientEngine engine;
        
        // List of torrent managers (one per torrent)
        private static List<TorrentManager> torrents = new List<TorrentManager>();
        
        // Path where downloaded files will be stored
        private static string downloadDirectory;
        
        // Cancellation token source for the main loop
        private static CancellationTokenSource cancellation;
        
        static async Task Main(string[] args)
        {
            // Initialize the client
            await InitializeClientAsync();
            
            // Start the main program loop
            await RunClientAsync();
            
            // Clean up resources when exiting
            await ShutdownClientAsync();
        }
        
        static async Task InitializeClientAsync()
        {
            Console.WriteLine("Initializing BitTorrent client...");
            
            // Create the downloads directory if it doesn't exist
            downloadDirectory = Path.Combine(Environment.CurrentDirectory, "Downloads");
            Directory.CreateDirectory(downloadDirectory);
            
            // Configure the engine settings
            var engineSettings = new EngineSettings
            {
                MaximumDownloadRate = 0,            // No download rate limit
                MaximumUploadRate = 250 * 1024,     // 250 KB/s upload limit
                ListenPort = 55123,                 // Port for incoming connections
                AllowedEncryption = EncryptionTypes.All
            };
            
            // Create the engine
            engine = new ClientEngine(engineSettings);
            
            // Check for saved torrents and resume data
            string resumeDataPath = Path.Combine(Environment.CurrentDirectory, "ResumeData");
            if (Directory.Exists(resumeDataPath))
            {
                Console.WriteLine("Loading saved torrents...");
                
                // Look for .torrent files
                foreach (string torrentFile in Directory.GetFiles(resumeDataPath, "*.torrent"))
                {
                    try
                    {
                        // Extract the info hash from the filename
                        string infoHashHex = Path.GetFileNameWithoutExtension(torrentFile);
                        
                        // Load the torrent
                        var torrent = await Torrent.LoadAsync(torrentFile);
                        var manager = await engine.AddAsync(torrent, downloadDirectory);
                        torrents.Add(manager);
                        
                        // Check for fast resume data
                        string resumeFile = Path.Combine(resumeDataPath, $"{infoHashHex}.fresume");
                        if (File.Exists(resumeFile))
                        {
                            byte[] resumeData = File.ReadAllBytes(resumeFile);
                            await manager.LoadFastResumeAsync(resumeData);
                        }
                        
                        RegisterTorrentEvents(manager);
                        Console.WriteLine($"Loaded torrent: {torrent.Name}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error loading torrent: {ex.Message}");
                    }
                }
            }
            
            Console.WriteLine("BitTorrent engine initialized.");
            Console.WriteLine($"Listening on port: {engineSettings.ListenPort}");
            Console.WriteLine($"Download directory: {downloadDirectory}");
            Console.WriteLine();
        }
        
        static async Task RunClientAsync()
        {
            Console.WriteLine("BitTorrent client is running.");
            
            // Create cancellation token for the display task
            cancellation = new CancellationTokenSource();
            
            // Start a background task to display progress
            _ = DisplayProgressAsync(cancellation.Token);
            
            bool exit = false;
            while (!exit)
            {
                Console.WriteLine("\nCommands:");
                Console.WriteLine("1. Add Torrent");
                Console.WriteLine("2. Add Magnet Link");
                Console.WriteLine("3. Start All");
                Console.WriteLine("4. Pause All");
                Console.WriteLine("5. Stop All");
                Console.WriteLine("6. Remove Torrent");
                Console.WriteLine("7. Exit");
                Console.Write("\nEnter command (1-7): ");
                
                string input = Console.ReadLine();
                Console.WriteLine();
                
                switch (input)
                {
                    case "1":
                        await AddTorrentAsync();
                        break;
                        
                    case "2":
                        await AddMagnetLinkAsync();
                        break;
                        
                    case "3":
                        await StartAllTorrentsAsync();
                        break;
                        
                    case "4":
                        await PauseAllTorrentsAsync();
                        break;
                        
                    case "5":
                        await StopAllTorrentsAsync();
                        break;
                        
                    case "6":
                        await RemoveTorrentAsync();
                        break;
                        
                    case "7":
                        exit = true;
                        break;
                        
                    default:
                        Console.WriteLine("Invalid command. Please try again.");
                        break;
                }
            }
            
            // Signal the display task to stop
            cancellation.Cancel();
        }
        
        static async Task DisplayProgressAsync(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                if (torrents.Count > 0)
                {
                    Console.Clear();
                    Console.WriteLine("=== Torrent Status ===");
                    Console.WriteLine();
                    
                    // Display global stats
                    Console.WriteLine($"Global Download: {engine.TotalDownloadRate / 1024:F2} KB/s");
                    Console.WriteLine($"Global Upload: {engine.TotalUploadRate / 1024:F2} KB/s");
                    Console.WriteLine();
                    
                    // Display stats for each torrent
                    for (int i = 0; i < torrents.Count; i++)
                    {
                        var manager = torrents[i];
                        string name = manager.Torrent?.Name ?? manager.InfoHash.ToHex();
                        
                        Console.WriteLine($"[{i + 1}] {name}");
                        Console.WriteLine($"    State: {manager.State}");
                        Console.WriteLine($"    Progress: {manager.Progress:F2}%");
                        Console.WriteLine($"    Download: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
                        Console.WriteLine($"    Upload: {manager.Monitor.UploadRate / 1024:F2} KB/s");
                        
                        // Calculate and display ETA if downloading
                        if (manager.State == TorrentState.Downloading && manager.Monitor.DownloadRate > 0)
                        {
                            double remainingBytes = manager.Torrent?.Size * (100 - manager.Progress) / 100 ?? 0;
                            TimeSpan eta = TimeSpan.FromSeconds(remainingBytes / manager.Monitor.DownloadRate);
                            Console.WriteLine($"    ETA: {eta.Hours:D2}:{eta.Minutes:D2}:{eta.Seconds:D2}");
                        }
                        
                        Console.WriteLine($"    Peers: {manager.Peers.ConnectedPeers.Count}");
                        Console.WriteLine();
                    }
                    
                    Console.WriteLine("Press any key to show menu...");
                }
                
                // Update every second
                await Task.Delay(1000, token);
            }
        }
        
        static async Task AddTorrentAsync()
        {
            Console.Write("Enter path to .torrent file: ");
            string path = Console.ReadLine().Trim('"'); // Remove quotes if user copied a path with quotes
            
            try
            {
                if (!File.Exists(path))
                {
                    Console.WriteLine("Error: File not found.");
                    return;
                }
                
                // Add the torrent to the engine
                var manager = await engine.AddAsync(path, downloadDirectory);
                torrents.Add(manager);
                
                // Register event handlers
                RegisterTorrentEvents(manager);
                
                Console.WriteLine($"Added torrent: {manager.Torrent.Name}");
                
                // Ask if the user wants to start the torrent immediately
                Console.Write("Start downloading now? (y/n): ");
                string response = Console.ReadLine().ToLower();
                
                if (response == "y" || response == "yes")
                {
                    await manager.StartAsync();
                    Console.WriteLine("Torrent started.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error adding torrent: {ex.Message}");
            }
        }
        
        static async Task AddMagnetLinkAsync()
        {
            Console.Write("Enter magnet link: ");
            string link = Console.ReadLine();
            
            try
            {
                // Parse and validate the magnet link
                var magnetLink = MagnetLink.Parse(link);
                
                // Add the magnet link to the engine
                var manager = await engine.AddAsync(magnetLink, downloadDirectory);
                torrents.Add(manager);
                
                // Register event handlers
                RegisterTorrentEvents(manager);
                
                Console.WriteLine($"Added magnet link with hash: {manager.InfoHash.ToHex()}");
                
                // Ask if the user wants to start the torrent immediately
                Console.Write("Start downloading now? (y/n): ");
                string response = Console.ReadLine().ToLower();
                
                if (response == "y" || response == "yes")
                {
                    await manager.StartAsync();
                    Console.WriteLine("Torrent started.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error adding magnet link: {ex.Message}");
            }
        }
        
        static async Task StartAllTorrentsAsync()
        {
            if (torrents.Count == 0)
            {
                Console.WriteLine("No torrents to start.");
                return;
            }
            
            try
            {
                await engine.StartAllAsync();
                Console.WriteLine("All torrents started.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error starting torrents: {ex.Message}");
            }
        }
        
        static async Task PauseAllTorrentsAsync()
        {
            if (torrents.Count == 0)
            {
                Console.WriteLine("No torrents to pause.");
                return;
            }
            
            try
            {
                foreach (var manager in torrents)
                {
                    await manager.PauseAsync();
                }
                Console.WriteLine("All torrents paused.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error pausing torrents: {ex.Message}");
            }
        }
        
        static async Task StopAllTorrentsAsync()
        {
            if (torrents.Count == 0)
            {
                Console.WriteLine("No torrents to stop.");
                return;
            }
            
            try
            {
                await engine.StopAllAsync();
                Console.WriteLine("All torrents stopped.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error stopping torrents: {ex.Message}");
            }
        }
        
        static async Task RemoveTorrentAsync()
        {
            if (torrents.Count == 0)
            {
                Console.WriteLine("No torrents to remove.");
                return;
            }
            
            Console.WriteLine("Select a torrent to remove:");
            
            for (int i = 0; i < torrents.Count; i++)
            {
                var manager = torrents[i];
                string name = manager.Torrent?.Name ?? manager.InfoHash.ToHex();
                Console.WriteLine($"[{i + 1}] {name}");
            }
            
            Console.Write("\nEnter torrent number: ");
            if (!int.TryParse(Console.ReadLine(), out int index) || index < 1 || index > torrents.Count)
            {
                Console.WriteLine("Invalid selection.");
                return;
            }
            
            var torrentManager = torrents[index - 1];
            
            Console.Write("Delete downloaded files? (y/n): ");
            bool deleteFiles = Console.ReadLine().ToLower() == "y";
            
            try
            {
                // Stop the torrent first
                await torrentManager.StopAsync();
                
                // Remove from the engine
                await engine.RemoveAsync(torrentManager);
                
                // Remove from our list
                torrents.Remove(torrentManager);
                
                // Optionally delete files
                if (deleteFiles)
                {
                    foreach (var file in torrentManager.Files)
                    {
                        string fullPath = Path.Combine(downloadDirectory, file.Path);
                        if (File.Exists(fullPath))
                        {
                            File.Delete(fullPath);
                        }
                    }
                    
                    // Try to clean up empty directories
                    CleanEmptyDirectories(downloadDirectory);
                }
                
                Console.WriteLine("Torrent removed successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error removing torrent: {ex.Message}");
            }
        }
        
        static void CleanEmptyDirectories(string directory)
        {
            try
            {
                foreach (var dir in Directory.GetDirectories(directory))
                {
                    CleanEmptyDirectories(dir);
                    
                    if (Directory.GetFiles(dir).Length == 0 && 
                        Directory.GetDirectories(dir).Length == 0)
                    {
                        Directory.Delete(dir);
                    }
                }
            }
            catch (Exception)
            {
                // Ignore errors in directory cleanup
            }
        }
        
        static void RegisterTorrentEvents(TorrentManager manager)
        {
            // Track state changes
            manager.TorrentStateChanged += (s, e) => 
            {
                Console.WriteLine($"\nTorrent '{manager.Torrent?.Name ?? manager.InfoHash.ToHex()}' changed state:");
                Console.WriteLine($"Old State: {e.OldState}, New State: {e.NewState}");
                
                // If the torrent just completed, show a notification
                if (e.NewState == TorrentState.Seeding && e.OldState != TorrentState.Seeding)
                {
                    Console.WriteLine($"\n*** Download Complete: {manager.Torrent?.Name ?? manager.InfoHash.ToHex()} ***\n");
                }
            };
            
            // Track piece hashing for detailed progress
            manager.PieceHashed += (s, e) => 
            {
                if (!e.HashPassed)
                {
                    Console.WriteLine($"\nPiece hash failed for torrent '{manager.Torrent?.Name ?? manager.InfoHash.ToHex()}'");
                    Console.WriteLine($"Piece index: {e.PieceIndex}");
                }
            };
        }
        
        static async Task ShutdownClientAsync()
        {
            Console.WriteLine("Shutting down...");
            
            try
            {
                // Stop all active torrents
                if (engine != null)
                {
                    await engine.StopAllAsync();
                    
                    // Save fast resume data for each torrent
                    string resumeDataPath = Path.Combine(Environment.CurrentDirectory, "ResumeData");
                    Directory.CreateDirectory(resumeDataPath);
                    
                    foreach (var manager in torrents)
                    {
                        try
                        {
                            // Save the fast resume data
                            byte[] resumeData = await manager.SaveFastResumeAsync();
                            File.WriteAllBytes(
                                Path.Combine(resumeDataPath, $"{manager.InfoHash.ToHex()}.fresume"),
                                resumeData);
                            
                            // If this is a magnet link that has metadata now, save the .torrent file
                            if (manager.HasMetadata && !manager.HasTorrent)
                            {
                                byte[] metadata = await manager.GetMetadataAsync();
                                File.WriteAllBytes(
                                    Path.Combine(resumeDataPath, $"{manager.InfoHash.ToHex()}.torrent"),
                                    metadata);
                            }
                        }
                        catch
                        {
                            // Ignore errors saving individual torrent data
                        }
                    }
                    
                    // Dispose the engine
                    await engine.DisposeAsync();
                }
                
                Console.WriteLine("Shutdown complete.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during shutdown: {ex.Message}");
            }
        }
    }
}
```

## Next Steps

Now that you have a working BitTorrent client, you could enhance it further:

1. Add support for file priorities to selectively download files
2. Create a graphical user interface using Windows Forms, WPF, or Avalonia
3. Implement more detailed torrent information displays
4. Add support for RSS feeds to automatically download torrents
5. Implement bandwidth scheduling to limit speeds at certain times of day
6. Add support for UPnP/NAT-PMP port forwarding

This tutorial has provided a foundation that you can build upon to create a more sophisticated BitTorrent client.