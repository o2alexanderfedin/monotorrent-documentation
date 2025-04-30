# Creating Torrents with MonoTorrent

This example demonstrates how to create torrent files using MonoTorrent's `TorrentCreator` class.

## Creating a Simple Torrent

The following example shows how to create a basic .torrent file from a directory or file:

```csharp
using System;
using System.IO;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace TorrentCreatorExample
{
    class Program
    {
        static async Task Main(string[] args)
        {
            await CreateSingleFileTorrentAsync();
            await CreateMultiFileTorrentAsync();
        }

        static async Task CreateSingleFileTorrentAsync()
        {
            Console.WriteLine("Creating single file torrent...");

            // Path to the file you want to create a torrent for
            string filePath = @"C:\Media\ubuntu-20.04.iso";
            
            // Path where you want to save the .torrent file
            string torrentPath = @"C:\Torrents\ubuntu-20.04.torrent";
            
            // Create a new TorrentCreator
            var creator = new TorrentCreator();
            
            // Set basic properties
            creator.Comment = "Ubuntu 20.04 ISO";
            creator.CreatedBy = "MonoTorrent Example";
            creator.Publisher = "Example Publisher";
            creator.PieceLength = 256 * 1024; // 256 KB pieces
            
            // Add a tracker
            creator.Announces.Add(new RawTrackerTier { 
                "http://tracker.ubuntu.com:6969/announce", 
                "udp://tracker.opentrackr.org:1337/announce" 
            });
            
            // Create the torrent
            await creator.CreateAsync(filePath, torrentPath);
            
            Console.WriteLine($"Torrent created and saved to {torrentPath}");
        }

        static async Task CreateMultiFileTorrentAsync()
        {
            Console.WriteLine("Creating multi-file torrent...");

            // Path to the directory containing files you want to include
            string directoryPath = @"C:\Media\MyAlbum";
            
            // Path where you want to save the .torrent file
            string torrentPath = @"C:\Torrents\my-album.torrent";
            
            // Create a new TorrentCreator
            var creator = new TorrentCreator();
            
            // Set basic properties
            creator.Comment = "My Music Album";
            creator.CreatedBy = "MonoTorrent Example";
            creator.Publisher = "Example Publisher";
            creator.PieceLength = 64 * 1024; // 64 KB pieces (smaller for smaller files)
            
            // Add trackers (in tiers)
            creator.Announces.Add(new RawTrackerTier { 
                "http://tracker1.example.com/announce", 
                "http://tracker2.example.com/announce" 
            });
            
            // Add a second tier of trackers (used as backup)
            creator.Announces.Add(new RawTrackerTier { 
                "http://backup1.example.com/announce", 
                "http://backup2.example.com/announce" 
            });
            
            // Create the torrent
            await creator.CreateAsync(directoryPath, torrentPath);
            
            Console.WriteLine($"Torrent created and saved to {torrentPath}");
        }
    }
}
```

## Advanced Torrent Creation

This example demonstrates more advanced options when creating torrents:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace AdvancedTorrentCreatorExample
{
    class Program
    {
        static async Task Main(string[] args)
        {
            await CreatePrivateTorrentAsync();
            await CreateTorrentWithCustomOptionsAsync();
        }

        static async Task CreatePrivateTorrentAsync()
        {
            Console.WriteLine("Creating private torrent...");

            // Path to the directory you want to create a torrent for
            string directoryPath = @"C:\Media\PrivateContent";
            
            // Path where you want to save the .torrent file
            string torrentPath = @"C:\Torrents\private-content.torrent";
            
            // Create a new TorrentCreator
            var creator = new TorrentCreator();
            
            // Basic properties
            creator.Comment = "Private content - DO NOT REDISTRIBUTE";
            creator.CreatedBy = "MonoTorrent Example";
            creator.Publisher = "Private Publisher";
            creator.PieceLength = 128 * 1024; // 128 KB pieces
            
            // Make the torrent private (disables DHT, PEX, etc.)
            creator.Private = true;
            
            // Add tracker for a private tracker
            creator.Announces.Add(new RawTrackerTier { 
                "https://private-tracker.example.com/announce" 
            });
            
            // Create the torrent
            await creator.CreateAsync(directoryPath, torrentPath);
            
            Console.WriteLine($"Private torrent created and saved to {torrentPath}");
        }

        static async Task CreateTorrentWithCustomOptionsAsync()
        {
            Console.WriteLine("Creating torrent with custom options...");

            // Path to the directory you want to create a torrent for
            string directoryPath = @"C:\Media\CustomContent";
            
            // Path where you want to save the .torrent file
            string torrentPath = @"C:\Torrents\custom-content.torrent";
            
            // Create a new TorrentCreator
            var creator = new TorrentCreator();
            
            // Basic properties
            creator.Comment = "Custom torrent example";
            creator.CreatedBy = "MonoTorrent Advanced Example";
            creator.Publisher = "Custom Publisher";
            
            // Use a larger piece size for better performance with large files
            creator.PieceLength = 1024 * 1024; // 1 MB pieces
            
            // Add trackers
            creator.Announces.Add(new RawTrackerTier { 
                "http://tracker1.example.com/announce",
                "http://tracker2.example.com/announce" 
            });
            
            // Add DHT nodes for trackerless operation
            creator.DhtNodes.Add(new KeyValuePair<string, int>("router.bittorrent.com", 6881));
            creator.DhtNodes.Add(new KeyValuePair<string, int>("dht.transmissionbt.com", 6881));
            
            // Add a source field (useful for private trackers to identify source)
            creator.Source = "CustomGroup";
            
            // Create the torrent with a specific directory name inside the torrent
            // This affects the path that will be created when the torrent is downloaded
            string torrentName = "Custom Content Collection";
            
            // Override default behavior and include specific files with custom paths
            string[] filesToInclude = Directory.GetFiles(directoryPath, "*.*", SearchOption.AllDirectories);
            
            // Create a dictionary mapping real paths to paths inside the torrent
            var fileMapping = new Dictionary<string, string>();
            foreach (string file in filesToInclude)
            {
                // Get the relative path within the directory
                string relativePath = file.Substring(directoryPath.Length).TrimStart(Path.DirectorySeparatorChar);
                
                // Create a custom path inside the torrent
                // For example, move all .txt files to a "Documents" subdirectory
                if (file.EndsWith(".txt"))
                {
                    fileMapping[file] = Path.Combine(torrentName, "Documents", relativePath);
                }
                // Move all media files to a "Media" subdirectory
                else if (file.EndsWith(".mp3") || file.EndsWith(".mp4") || file.EndsWith(".avi"))
                {
                    fileMapping[file] = Path.Combine(torrentName, "Media", Path.GetFileName(file));
                }
                // Keep other files in the root
                else
                {
                    fileMapping[file] = Path.Combine(torrentName, relativePath);
                }
            }
            
            // Create the torrent with custom file mappings
            await creator.CreateAsync(fileMapping, torrentPath);
            
            Console.WriteLine($"Custom torrent created and saved to {torrentPath}");
            
            // Optionally, calculate info hash and display it
            using (var fileStream = File.OpenRead(torrentPath))
            {
                var torrent = await Torrent.LoadAsync(fileStream);
                Console.WriteLine($"Torrent info hash: {torrent.InfoHash.ToHex()}");
            }
        }
    }
}
```

## Creating a Torrent with WebSeeds

WebSeeds provide direct HTTP download links for torrent content, which can help with initial seeding or as a fallback when peers are scarce.

```csharp
static async Task CreateTorrentWithWebSeedsAsync()
{
    Console.WriteLine("Creating torrent with WebSeeds...");

    // Path to the directory you want to create a torrent for
    string directoryPath = @"C:\Media\WebSeedContent";
    
    // Path where you want to save the .torrent file
    string torrentPath = @"C:\Torrents\webseed-content.torrent";
    
    // Create a new TorrentCreator
    var creator = new TorrentCreator();
    
    // Basic properties
    creator.Comment = "Torrent with WebSeeds";
    creator.CreatedBy = "MonoTorrent Example";
    creator.Publisher = "WebSeed Publisher";
    creator.PieceLength = 256 * 1024; // 256 KB pieces
    
    // Add regular trackers
    creator.Announces.Add(new RawTrackerTier { 
        "http://tracker.example.com/announce"
    });
    
    // Add WebSeeds (direct HTTP sources for the files)
    creator.WebSeeds.Add("http://mirror1.example.com/content/");
    creator.WebSeeds.Add("http://mirror2.example.com/content/");
    
    // Create the torrent
    await creator.CreateAsync(directoryPath, torrentPath);
    
    Console.WriteLine($"Torrent with WebSeeds created and saved to {torrentPath}");
}
```

## Creating a Hybrid BitTorrent v1/v2 Torrent

MonoTorrent supports creating hybrid v1/v2 torrents, which are compatible with both older and newer BitTorrent clients.

```csharp
static async Task CreateHybridTorrentAsync()
{
    Console.WriteLine("Creating hybrid BitTorrent v1/v2 torrent...");

    // Path to the directory you want to create a torrent for
    string directoryPath = @"C:\Media\HybridContent";
    
    // Path where you want to save the .torrent file
    string torrentPath = @"C:\Torrents\hybrid-content.torrent";
    
    // Create a new TorrentCreator with v1/v2 hybrid support
    var creator = new TorrentCreator();
    
    // Basic properties
    creator.Comment = "Hybrid v1/v2 Torrent";
    creator.CreatedBy = "MonoTorrent Example";
    creator.Publisher = "Hybrid Publisher";
    creator.PieceLength = 256 * 1024; // 256 KB pieces
    
    // Set to create a hybrid v1/v2 torrent
    creator.Version = TorrentVersion.V1V2;
    
    // Add trackers
    creator.Announces.Add(new RawTrackerTier { 
        "http://tracker.example.com/announce"
    });
    
    // Create the torrent
    await creator.CreateAsync(directoryPath, torrentPath);
    
    Console.WriteLine($"Hybrid v1/v2 torrent created and saved to {torrentPath}");
    
    // Load the torrent to verify it's hybrid
    using (var fileStream = File.OpenRead(torrentPath))
    {
        var torrent = await Torrent.LoadAsync(fileStream);
        Console.WriteLine($"Torrent v1 info hash: {torrent.InfoHash.ToHex()}");
        Console.WriteLine($"Torrent v2 info hash: {torrent.InfoHashV2?.ToHex() ?? "Not available"}");
    }
}
```

## Customizing Piece Length Selection

The piece length is an important consideration when creating torrents. Here's a helper method to automatically select an appropriate piece length based on torrent size:

```csharp
static int CalculateOptimalPieceLength(long totalSize)
{
    // Recommended piece counts are between 1000 and 2000 pieces
    // Minimum piece size is typically 16 KB, maximum 8 MB
    
    // Start with smallest standard piece size
    int pieceLength = 16 * 1024; // 16 KB
    
    // Standard piece lengths (powers of 2)
    int[] standardSizes = {
        16 * 1024,       // 16 KB
        32 * 1024,       // 32 KB
        64 * 1024,       // 64 KB
        128 * 1024,      // 128 KB
        256 * 1024,      // 256 KB
        512 * 1024,      // 512 KB
        1024 * 1024,     // 1 MB
        2 * 1024 * 1024, // 2 MB
        4 * 1024 * 1024, // 4 MB
        8 * 1024 * 1024  // 8 MB
    };
    
    // Find the smallest piece size that gives us less than 2000 pieces
    foreach (int size in standardSizes)
    {
        int pieceCount = (int)Math.Ceiling((double)totalSize / size);
        if (pieceCount < 2000)
        {
            pieceLength = size;
            break;
        }
    }
    
    // Make sure we have at least 1000 pieces for very large torrents
    int minPieceCount = 1000;
    int maxPieceLength = (int)(totalSize / minPieceCount);
    
    // Round down to nearest standard size
    for (int i = standardSizes.Length - 1; i >= 0; i--)
    {
        if (standardSizes[i] <= maxPieceLength)
        {
            return Math.Min(pieceLength, standardSizes[i]);
        }
    }
    
    return pieceLength;
}
```

## Best Practices for Creating Torrents

1. **Choose the right piece size**: Smaller pieces provide better download granularity but increase .torrent file size and verification overhead.
   - Small files (< 100 MB): 32 KB or 64 KB pieces
   - Medium files (100 MB - 1 GB): 256 KB pieces
   - Large files (1 GB - 10 GB): 1 MB pieces
   - Very large files (> 10 GB): 4 MB or 8 MB pieces

2. **Use multiple trackers**: Include several trackers organized in tiers for redundancy.

3. **Consider WebSeeds**: Adding WebSeeds can ensure content availability even when peers are scarce.

4. **Private flag**: Set the private flag only for private trackers that require it.

5. **Hybrid torrents**: Create v1/v2 hybrid torrents for maximum compatibility.

6. **Comment and source fields**: Add descriptive comments and source information to help users identify your torrents.

7. **Testing**: Always test your created torrents by loading them in MonoTorrent or another BitTorrent client to verify they work as expected.

## Complete Torrent Creator Utility

Here's a complete console application that serves as a torrent creation utility:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;

namespace TorrentCreatorUtility
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("MonoTorrent Creator Utility");
            Console.WriteLine("==========================");
            
            if (args.Length > 0 && (args[0] == "-h" || args[0] == "--help"))
            {
                ShowHelp();
                return;
            }
            
            try
            {
                string inputPath = GetInput("Enter the path to the file or directory to create a torrent for: ");
                
                if (!File.Exists(inputPath) && !Directory.Exists(inputPath))
                {
                    Console.WriteLine("Error: The specified path does not exist.");
                    return;
                }
                
                string outputPath = GetInput("Enter the path where the .torrent file should be saved: ");
                
                // Create directory for output path if it doesn't exist
                Directory.CreateDirectory(Path.GetDirectoryName(outputPath));
                
                // Create a new TorrentCreator
                var creator = new TorrentCreator();
                
                // Set basic properties
                creator.Comment = GetInput("Enter a comment for the torrent (optional): ");
                creator.CreatedBy = GetInput("Enter the creator name (optional): ", "MonoTorrent Creator Utility");
                creator.Publisher = GetInput("Enter the publisher name (optional): ");
                
                // Calculate total size to determine optimal piece length
                long totalSize = CalculateTotalSize(inputPath);
                int optimalPieceLength = CalculateOptimalPieceLength(totalSize);
                
                Console.WriteLine($"Suggested piece length for {FormatSize(totalSize)}: {FormatSize(optimalPieceLength)}");
                
                string pieceLengthInput = GetInput($"Enter piece length in KB (default: {optimalPieceLength / 1024}): ");
                if (!string.IsNullOrEmpty(pieceLengthInput) && int.TryParse(pieceLengthInput, out int customPieceLength))
                {
                    creator.PieceLength = customPieceLength * 1024;
                }
                else
                {
                    creator.PieceLength = optimalPieceLength;
                }
                
                // Ask for tracker URLs
                List<string> trackers = new List<string>();
                while (true)
                {
                    string tracker = GetInput("Enter a tracker URL (leave empty to finish adding trackers): ");
                    if (string.IsNullOrEmpty(tracker))
                        break;
                    
                    trackers.Add(tracker);
                }
                
                if (trackers.Any())
                {
                    creator.Announces.Add(new RawTrackerTier(trackers));
                }
                
                // Ask for WebSeeds
                List<string> webSeeds = new List<string>();
                while (true)
                {
                    string webSeed = GetInput("Enter a WebSeed URL (leave empty to finish adding WebSeeds): ");
                    if (string.IsNullOrEmpty(webSeed))
                        break;
                    
                    webSeeds.Add(webSeed);
                }
                
                foreach (string webSeed in webSeeds)
                {
                    creator.WebSeeds.Add(webSeed);
                }
                
                // Ask if the torrent should be private
                string privateInput = GetInput("Make this a private torrent? (y/n): ", "n");
                creator.Private = privateInput.ToLower() == "y";
                
                // Ask for torrent version
                string versionInput = GetInput("Select torrent version (1=v1 only, 2=hybrid v1/v2): ", "1");
                creator.Version = versionInput == "2" ? TorrentVersion.V1V2 : TorrentVersion.V1;
                
                Console.WriteLine("\nCreating torrent...");
                
                // Create the torrent
                await creator.CreateAsync(inputPath, outputPath);
                
                // Load the torrent to display info
                using (var fileStream = File.OpenRead(outputPath))
                {
                    var torrent = await Torrent.LoadAsync(fileStream);
                    
                    Console.WriteLine("\nTorrent created successfully!");
                    Console.WriteLine($"Output path: {outputPath}");
                    Console.WriteLine($"Torrent name: {torrent.Name}");
                    Console.WriteLine($"Info hash: {torrent.InfoHash.ToHex()}");
                    
                    if (torrent.InfoHashV2 != null)
                    {
                        Console.WriteLine($"Info hash v2: {torrent.InfoHashV2.ToHex()}");
                    }
                    
                    Console.WriteLine($"Piece length: {FormatSize(torrent.PieceLength)}");
                    Console.WriteLine($"Piece count: {torrent.PieceCount}");
                    Console.WriteLine($"Total size: {FormatSize(torrent.Size)}");
                    Console.WriteLine($"File count: {torrent.Files.Count}");
                    Console.WriteLine($"Private: {torrent.IsPrivate}");
                    
                    if (torrent.AnnounceUrls.Count > 0)
                    {
                        Console.WriteLine("Trackers:");
                        for (int tierIndex = 0; tierIndex < torrent.AnnounceUrls.Count; tierIndex++)
                        {
                            Console.WriteLine($"  Tier {tierIndex + 1}:");
                            foreach (string announceUrl in torrent.AnnounceUrls[tierIndex])
                            {
                                Console.WriteLine($"    {announceUrl}");
                            }
                        }
                    }
                    
                    if (torrent.WebSeeds.Count > 0)
                    {
                        Console.WriteLine("WebSeeds:");
                        foreach (string webSeed in torrent.WebSeeds)
                        {
                            Console.WriteLine($"  {webSeed}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                if (ex.InnerException != null)
                {
                    Console.WriteLine($"Inner error: {ex.InnerException.Message}");
                }
            }
        }
        
        static void ShowHelp()
        {
            Console.WriteLine("Usage: TorrentCreatorUtility [options]");
            Console.WriteLine();
            Console.WriteLine("Options:");
            Console.WriteLine("  -h, --help    Show this help message");
            Console.WriteLine();
            Console.WriteLine("When run without options, the utility will guide you through creating a torrent interactively.");
        }
        
        static string GetInput(string prompt, string defaultValue = "")
        {
            Console.Write(prompt);
            string input = Console.ReadLine();
            return string.IsNullOrEmpty(input) ? defaultValue : input;
        }
        
        static long CalculateTotalSize(string path)
        {
            if (File.Exists(path))
            {
                return new FileInfo(path).Length;
            }
            else if (Directory.Exists(path))
            {
                return Directory.GetFiles(path, "*", SearchOption.AllDirectories).Sum(f => new FileInfo(f).Length);
            }
            
            return 0;
        }
        
        static int CalculateOptimalPieceLength(long totalSize)
        {
            // Recommended piece counts are between 1000 and 2000 pieces
            // Minimum piece size is typically 16 KB, maximum 8 MB
            
            // Start with smallest standard piece size
            int pieceLength = 16 * 1024; // 16 KB
            
            // Standard piece lengths (powers of 2)
            int[] standardSizes = {
                16 * 1024,       // 16 KB
                32 * 1024,       // 32 KB
                64 * 1024,       // 64 KB
                128 * 1024,      // 128 KB
                256 * 1024,      // 256 KB
                512 * 1024,      // 512 KB
                1024 * 1024,     // 1 MB
                2 * 1024 * 1024, // 2 MB
                4 * 1024 * 1024, // 4 MB
                8 * 1024 * 1024  // 8 MB
            };
            
            // Find the smallest piece size that gives us less than 2000 pieces
            foreach (int size in standardSizes)
            {
                int pieceCount = (int)Math.Ceiling((double)totalSize / size);
                if (pieceCount < 2000)
                {
                    pieceLength = size;
                    break;
                }
            }
            
            // Make sure we have at least 50 pieces for very small torrents
            int minPieceCount = 50;
            int maxPieceLength = (int)(totalSize / minPieceCount);
            
            // Round down to nearest standard size
            for (int i = standardSizes.Length - 1; i >= 0; i--)
            {
                if (standardSizes[i] <= maxPieceLength)
                {
                    return Math.Min(pieceLength, standardSizes[i]);
                }
            }
            
            return pieceLength;
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
}
```

This utility provides a comprehensive interface for creating torrents with custom settings and shows all relevant information about the created torrent.