# Simple BitTorrent Client Example

This example demonstrates how to create a simple but functional BitTorrent client using MonoTorrent. It includes basic functionality like downloading torrents, displaying progress, and managing multiple downloads.

## Complete Console Application Example

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace SimpleMonoTorrentClient
{
    class Program
    {
        // The engine used to manage all torrents
        private static ClientEngine engine;
        
        // List of torrent managers (one per torrent)
        private static List<TorrentManager> torrents = new List<TorrentManager>();
        
        // Cancellation token source to stop the display loop
        private static CancellationTokenSource cancellation;
        
        // Path where downloaded files will be stored
        private static string downloadPath = Path.Combine(Environment.CurrentDirectory, "Downloads");
        
        static async Task Main(string[] args)
        {
            // Ensure download directory exists
            Directory.CreateDirectory(downloadPath);
            
            // Setup the engine
            await SetupEngineAsync();
            
            // Start the display loop
            cancellation = new CancellationTokenSource();
            _ = DisplayProgressAsync(cancellation.Token);
            
            // Main menu loop
            bool exit = false;
            while (!exit)
            {
                Console.WriteLine("\nMonoTorrent Simple Client");
                Console.WriteLine("--------------------------");
                Console.WriteLine("1. Add Torrent from .torrent file");
                Console.WriteLine("2. Add Torrent from magnet link");
                Console.WriteLine("3. Start All Torrents");
                Console.WriteLine("4. Pause All Torrents");
                Console.WriteLine("5. Stop All Torrents");
                Console.WriteLine("6. Remove a Torrent");
                Console.WriteLine("7. Exit");
                Console.Write("\nEnter your choice (1-7): ");
                
                string choice = Console.ReadLine();
                
                switch (choice)
                {
                    case "1":
                        await AddTorrentFromFileAsync();
                        break;
                    
                    case "2":
                        await AddTorrentFromMagnetAsync();
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
                        Console.WriteLine("Invalid choice. Please try again.");
                        break;
                }
            }
            
            // Cleanup when exiting
            await CleanupAsync();
        }
        
        private static async Task SetupEngineAsync()
        {
            Console.WriteLine("Initializing BitTorrent engine...");
            
            // Configure the engine settings
            var settings = new EngineSettings
            {
                MaximumDownloadRate = 0,            // No download limit
                MaximumUploadRate = 100 * 1024,     // 100 KB/s upload limit
                ListenPort = 55123,                 // Port to listen for incoming connections
                AllowedEncryption = EncryptionTypes.All // Allow all encryption protocols
            };
            
            // Create the engine
            engine = new ClientEngine(settings);
            
            // Load any previously saved torrents
            await LoadSavedTorrentsAsync();
            
            Console.WriteLine("Engine initialized successfully.");
        }
        
        private static async Task LoadSavedTorrentsAsync()
        {
            string fastResumePath = Path.Combine(Environment.CurrentDirectory, "FastResume");
            Directory.CreateDirectory(fastResumePath);
            
            string[] fastResumeFiles = Directory.GetFiles(fastResumePath, "*.fastresume");
            
            foreach (string file in fastResumeFiles)
            {
                try
                {
                    // Get the info hash from the filename
                    string infoHashStr = Path.GetFileNameWithoutExtension(file);
                    InfoHash infoHash = InfoHash.FromHex(infoHashStr);
                    
                    // Load the corresponding .torrent file if it exists
                    string torrentFile = Path.Combine(fastResumePath, $"{infoHashStr}.torrent");
                    
                    if (File.Exists(torrentFile))
                    {
                        // Load the torrent
                        byte[] torrentData = File.ReadAllBytes(torrentFile);
                        Torrent torrent = await Torrent.LoadAsync(torrentData);
                        
                        // Load the fast resume data
                        byte[] fastResumeData = File.ReadAllBytes(file);
                        
                        // Create and register the torrent manager
                        var manager = await engine.AddAsync(torrent, downloadPath);
                        await manager.LoadFastResumeAsync(fastResumeData);
                        
                        torrents.Add(manager);
                        
                        Console.WriteLine($"Loaded saved torrent: {torrent.Name}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading saved torrent: {ex.Message}");
                }
            }
        }
        
        private static async Task AddTorrentFromFileAsync()
        {
            Console.Write("Enter path to .torrent file: ");
            string torrentPath = Console.ReadLine().Trim('"');
            
            if (!File.Exists(torrentPath))
            {
                Console.WriteLine("File not found!");
                return;
            }
            
            try
            {
                // Add the torrent
                var manager = await engine.AddAsync(torrentPath, downloadPath);
                torrents.Add(manager);
                
                // Save a copy of the .torrent file
                string fastResumePath = Path.Combine(Environment.CurrentDirectory, "FastResume");
                Directory.CreateDirectory(fastResumePath);
                File.Copy(torrentPath, Path.Combine(fastResumePath, $"{manager.InfoHash.ToHex()}.torrent"), true);
                
                Console.WriteLine($"Added torrent: {manager.Torrent.Name}");
                
                // Ask if they want to start it
                Console.Write("Start downloading now? (y/n): ");
                if (Console.ReadLine().Trim().ToLower() == "y")
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
        
        private static async Task AddTorrentFromMagnetAsync()
        {
            Console.Write("Enter magnet link: ");
            string magnetLink = Console.ReadLine();
            
            try
            {
                // Parse and add the magnet link
                var magnet = MagnetLink.Parse(magnetLink);
                var manager = await engine.AddAsync(magnet, downloadPath);
                torrents.Add(manager);
                
                Console.WriteLine($"Added magnet link with hash: {manager.InfoHash.ToHex()}");
                
                // Ask if they want to start it
                Console.Write("Start downloading now? (y/n): ");
                if (Console.ReadLine().Trim().ToLower() == "y")
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
        
        private static async Task StartAllTorrentsAsync()
        {
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
        
        private static async Task PauseAllTorrentsAsync()
        {
            try
            {
                foreach (var torrent in torrents)
                {
                    await torrent.PauseAsync();
                }
                Console.WriteLine("All torrents paused.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error pausing torrents: {ex.Message}");
            }
        }
        
        private static async Task StopAllTorrentsAsync()
        {
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
        
        private static async Task RemoveTorrentAsync()
        {
            if (torrents.Count == 0)
            {
                Console.WriteLine("No torrents to remove.");
                return;
            }
            
            // Display list of torrents
            Console.WriteLine("\nTorrents:");
            for (int i = 0; i < torrents.Count; i++)
            {
                Console.WriteLine($"{i+1}. {torrents[i].Torrent?.Name ?? torrents[i].InfoHash.ToHex()}");
            }
            
            // Get user selection
            Console.Write("\nEnter the number of the torrent to remove: ");
            if (!int.TryParse(Console.ReadLine(), out int index) || index < 1 || index > torrents.Count)
            {
                Console.WriteLine("Invalid selection.");
                return;
            }
            
            var torrent = torrents[index - 1];
            
            // Ask if they want to delete the files
            Console.Write("Delete downloaded files? (y/n): ");
            bool deleteFiles = Console.ReadLine().Trim().ToLower() == "y";
            
            try
            {
                // Stop the torrent
                await torrent.StopAsync();
                
                // Save fast resume data
                string fastResumePath = Path.Combine(Environment.CurrentDirectory, "FastResume");
                Directory.CreateDirectory(fastResumePath);
                byte[] fastResumeData = await torrent.SaveFastResumeAsync();
                File.WriteAllBytes(Path.Combine(fastResumePath, $"{torrent.InfoHash.ToHex()}.fastresume"), fastResumeData);
                
                // Remove the torrent
                await engine.RemoveAsync(torrent);
                torrents.Remove(torrent);
                
                if (deleteFiles)
                {
                    // Delete the downloaded files
                    foreach (var file in torrent.Files)
                    {
                        string fullPath = Path.Combine(downloadPath, file.Path);
                        if (File.Exists(fullPath))
                        {
                            File.Delete(fullPath);
                        }
                    }
                    
                    // Try to delete empty directories
                    var directories = torrent.Files
                        .Select(f => Path.GetDirectoryName(Path.Combine(downloadPath, f.Path)))
                        .Distinct();
                    
                    foreach (var dir in directories)
                    {
                        if (Directory.Exists(dir) && !Directory.EnumerateFileSystemEntries(dir).Any())
                        {
                            Directory.Delete(dir);
                        }
                    }
                }
                
                Console.WriteLine("Torrent removed successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error removing torrent: {ex.Message}");
            }
        }
        
        private static async Task DisplayProgressAsync(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                // Clear the display area
                Console.Clear();
                
                Console.WriteLine("MonoTorrent Simple Client - Status");
                Console.WriteLine("-----------------------------------");
                
                // Display global stats
                Console.WriteLine($"Global Download: {engine.TotalDownloadRate / 1024:F2} KB/s");
                Console.WriteLine($"Global Upload: {engine.TotalUploadRate / 1024:F2} KB/s");
                Console.WriteLine();
                
                // Display information for each torrent
                for (int i = 0; i < torrents.Count; i++)
                {
                    var torrent = torrents[i];
                    
                    string name = torrent.Torrent?.Name ?? torrent.InfoHash.ToHex();
                    
                    Console.WriteLine($"Torrent {i+1}: {name}");
                    Console.WriteLine($"  State: {torrent.State}");
                    Console.WriteLine($"  Progress: {torrent.Progress:F2}%");
                    Console.WriteLine($"  Download: {torrent.Monitor.DownloadRate / 1024:F2} KB/s");
                    Console.WriteLine($"  Upload: {torrent.Monitor.UploadRate / 1024:F2} KB/s");
                    Console.WriteLine($"  Peers: {torrent.Peers.ConnectedPeers.Count}");
                    
                    // Calculate ETA
                    TimeSpan eta = TimeSpan.MaxValue;
                    if (torrent.Monitor.DownloadRate > 0)
                    {
                        double remainingBytes = torrent.Torrent?.Size * (100 - torrent.Progress) / 100 ?? 0;
                        eta = TimeSpan.FromSeconds(remainingBytes / torrent.Monitor.DownloadRate);
                    }
                    
                    if (eta < TimeSpan.MaxValue)
                    {
                        Console.WriteLine($"  ETA: {eta.Hours:00}:{eta.Minutes:00}:{eta.Seconds:00}");
                    }
                    else
                    {
                        Console.WriteLine("  ETA: Unknown");
                    }
                    
                    Console.WriteLine();
                }
                
                Console.WriteLine("\nPress a key to show menu...");
                
                // Update every second
                await Task.Delay(1000, token);
            }
        }
        
        private static async Task CleanupAsync()
        {
            cancellation.Cancel();
            
            Console.WriteLine("Saving torrent state and shutting down...");
            
            // Save fast resume data for all torrents
            string fastResumePath = Path.Combine(Environment.CurrentDirectory, "FastResume");
            Directory.CreateDirectory(fastResumePath);
            
            foreach (var torrent in torrents)
            {
                try
                {
                    // Save fast resume data
                    byte[] fastResumeData = await torrent.SaveFastResumeAsync();
                    File.WriteAllBytes(Path.Combine(fastResumePath, $"{torrent.InfoHash.ToHex()}.fastresume"), fastResumeData);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error saving torrent state: {ex.Message}");
                }
            }
            
            // Stop all torrents
            await engine.StopAllAsync();
            
            // Dispose the engine
            await engine.DisposeAsync();
            
            Console.WriteLine("Shutdown complete. Press any key to exit.");
            Console.ReadKey();
        }
    }
}
```

## Key Features in this Example

This example implements a simple but functional BitTorrent client with the following features:

1. **Engine Management**
   - Initializes the ClientEngine with appropriate settings
   - Proper cleanup and disposal on exit

2. **Torrent Management**
   - Adding torrents from .torrent files
   - Adding torrents from magnet links
   - Starting, pausing, and stopping torrents
   - Removing torrents with option to delete files

3. **State Persistence**
   - Saves .torrent files for future reference
   - Stores and loads FastResume data for quick resuming
   - Automatically loads previously saved torrents on startup

4. **User Interface**
   - Menu-driven interface for torrent management
   - Real-time display of download progress and statistics
   - ETA calculation for downloads

5. **Error Handling**
   - Proper exception handling throughout
   - Graceful failure when files don't exist or operations fail

## Enhancements You Might Add

This example can be extended in several ways:

1. **File Priority Management**
   - Allow users to set priorities for individual files

2. **Tracker Management**
   - Display tracker status and allow manual announces

3. **DHT Configuration**
   - Enable/disable DHT and other peer discovery methods

4. **Rate Limiting Controls**
   - Allow adjusting rate limits during runtime

5. **Torrent Creation**
   - Add functionality to create new torrents

6. **Improved UI**
   - Convert to a GUI application for better user experience

## Usage Instructions

1. Compile and run the example
2. Use the menu to add torrents
3. Monitor progress in the status display
4. Use menu options to control downloading
5. When finished, exit the application which will save all state information
6. On next run, previously added torrents will be loaded automatically

## Notes

- Downloaded files are stored in a "Downloads" folder in the current directory
- Torrent state information is stored in a "FastResume" folder
- This example does not include a GUI - it's a console application
- For real-world applications, consider adding more error handling and a proper UI