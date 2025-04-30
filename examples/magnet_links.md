# Working with Magnet Links

This example demonstrates how to work with magnet links in MonoTorrent. Magnet links provide a convenient way to share torrents without distributing the .torrent file itself.

## Contents

- [Understanding Magnet Links](#understanding-magnet-links)
- [Parsing Magnet Links](#parsing-magnet-links)
- [Adding a Magnet Link](#adding-a-magnet-link)
- [Handling Metadata Download](#handling-metadata-download)
- [Creating Magnet Links](#creating-magnet-links)
- [Complete Example](#complete-example)

## Understanding Magnet Links

A magnet link is a URI scheme that includes the necessary information to find and download a torrent without having the .torrent file. At minimum, it contains the InfoHash of the torrent, but it can also include tracker URLs, display names, and more.

Example magnet link:
```
magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10&dn=Example+Torrent&tr=udp%3A%2F%2Ftracker.example.com%3A80
```

## Parsing Magnet Links

MonoTorrent provides the `MagnetLink` class to parse and work with magnet links:

```csharp
// Parse a magnet link
string magnetLinkStr = "magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10&dn=Example+Torrent";
var magnetLink = new MagnetLink(magnetLinkStr);

// Access properties of the magnet link
Console.WriteLine($"InfoHash: {magnetLink.InfoHash.ToHex()}");
Console.WriteLine($"Name: {magnetLink.Name}");

// Examine trackers
foreach (var tracker in magnetLink.AnnounceUrls)
{
    Console.WriteLine($"Tracker: {tracker}");
}
```

## Adding a Magnet Link

To download a torrent from a magnet link:

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

// Start downloading
await manager.StartAsync();

// Note: When starting from a magnet link, the torrent enters "metadata mode" first
// to download the torrent metadata before downloading the actual content
```

## Handling Metadata Download

When downloading from a magnet link, MonoTorrent must first download the torrent metadata:

```csharp
// Add event handlers to monitor the metadata download
manager.TorrentStateChanged += (sender, e) => {
    if (e.OldState == TorrentState.Metadata && e.NewState == TorrentState.Downloading)
    {
        Console.WriteLine("Metadata download complete, starting content download");
        
        // Now we can access torrent information
        Console.WriteLine($"Torrent name: {manager.Torrent.Name}");
        Console.WriteLine($"Torrent size: {manager.Torrent.Size} bytes");
        Console.WriteLine($"File count: {manager.Torrent.Files.Count}");
    }
};

// Start the metadata download
await manager.StartAsync();

// Wait for metadata to download
while (!manager.HasMetadata)
{
    Console.WriteLine("Waiting for metadata...");
    await Task.Delay(1000);
}

Console.WriteLine("Metadata download complete!");

// Display torrent information
Console.WriteLine($"Torrent name: {manager.Torrent.Name}");
foreach (var file in manager.Torrent.Files)
{
    Console.WriteLine($"File: {file.Path} ({file.Length} bytes)");
}
```

## Creating Magnet Links

You can generate magnet links from existing torrents:

```csharp
// Load a torrent
var torrent = await Torrent.LoadAsync("example.torrent");

// Generate a basic magnet link with just the infohash
string basicMagnet = $"magnet:?xt=urn:btih:{torrent.InfoHash.ToHex()}";
Console.WriteLine($"Basic magnet link: {basicMagnet}");

// Generate a more comprehensive magnet link
var magnetBuilder = new StringBuilder($"magnet:?xt=urn:btih:{torrent.InfoHash.ToHex()}");

// Add display name
if (!string.IsNullOrEmpty(torrent.Name))
{
    magnetBuilder.Append($"&dn={Uri.EscapeDataString(torrent.Name)}");
}

// Add trackers
foreach (var tier in torrent.AnnounceUrls)
{
    foreach (var tracker in tier)
    {
        magnetBuilder.Append($"&tr={Uri.EscapeDataString(tracker)}");
    }
}

// Add web seeds if available
foreach (var webSeed in torrent.WebSeeds)
{
    magnetBuilder.Append($"&ws={Uri.EscapeDataString(webSeed)}");
}

string fullMagnet = magnetBuilder.ToString();
Console.WriteLine($"Full magnet link: {fullMagnet}");
```

## Complete Example

Here's a complete example demonstrating magnet link handling:

```csharp
public class MagnetLinkExample
{
    public static async Task RunAsync()
    {
        // Initialize engine with DHT enabled for better metadata downloads
        var engineSettings = new EngineSettings
        {
            SavePath = "/path/to/downloads",
            DhtEndPoint = new IPEndPoint(IPAddress.Any, 55123)
        };
        
        using var engine = new ClientEngine(engineSettings);
        
        // Start DHT to improve peer finding
        await engine.DhtEngine.StartAsync();
        
        Console.WriteLine("Enter a magnet link:");
        string magnetLinkStr = Console.ReadLine();
        
        try
        {
            // Parse the magnet link
            var magnetLink = new MagnetLink(magnetLinkStr);
            Console.WriteLine($"Parsed magnet link for: {magnetLink.Name ?? "Unnamed torrent"}");
            
            // Add the torrent
            var manager = await engine.AddAsync(magnetLink, "/path/to/downloads");
            
            // Subscribe to events
            manager.TorrentStateChanged += (s, e) => {
                Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
                
                if (e.OldState == TorrentState.Metadata && e.NewState == TorrentState.Downloading)
                {
                    DisplayTorrentInfo(manager);
                }
            };
            
            // Start the download
            await manager.StartAsync();
            
            // Wait for metadata
            Console.WriteLine("Waiting for metadata to download...");
            int retryCount = 0;
            while (!manager.HasMetadata && retryCount < 60) // Wait up to 60 seconds
            {
                await Task.Delay(1000);
                Console.Write(".");
                retryCount++;
            }
            Console.WriteLine();
            
            if (!manager.HasMetadata)
            {
                Console.WriteLine("Failed to download metadata within timeout period.");
                
                // Try adding additional trackers to help find peers
                var additionalTrackers = new[] {
                    "udp://tracker.opentrackr.org:1337/announce",
                    "udp://tracker.openbittorrent.com:6969/announce",
                    "udp://tracker.internetwarriors.net:1337/announce"
                };
                
                foreach (var tracker in additionalTrackers)
                {
                    Console.WriteLine($"Adding tracker: {tracker}");
                    manager.TrackerManager.Add(new Uri(tracker));
                }
                
                Console.WriteLine("Press Enter to continue waiting for metadata...");
                Console.ReadLine();
                
                // Continue waiting
                while (!manager.HasMetadata)
                {
                    await Task.Delay(2000);
                    Console.Write(".");
                }
                Console.WriteLine();
            }
            
            if (manager.HasMetadata)
            {
                Console.WriteLine("Metadata download complete!");
                DisplayTorrentInfo(manager);
                
                // Continue downloading
                Console.WriteLine("Press Enter to stop downloading...");
                Console.ReadLine();
            }
            
            // Stop the download
            await manager.StopAsync();
            
            // Generate a new magnet link from the torrent
            if (manager.HasMetadata)
            {
                string newMagnetLink = GenerateMagnetLink(manager.Torrent);
                Console.WriteLine($"Regenerated magnet link: {newMagnetLink}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
        
        // Clean up
        await engine.StopAllAsync();
    }
    
    private static void DisplayTorrentInfo(TorrentManager manager)
    {
        Console.WriteLine($"Torrent name: {manager.Torrent.Name}");
        Console.WriteLine($"Torrent size: {FormatSize(manager.Torrent.Size)}");
        Console.WriteLine($"Piece length: {FormatSize(manager.Torrent.PieceLength)}");
        Console.WriteLine($"Piece count: {manager.Torrent.Pieces.Count}");
        Console.WriteLine($"File count: {manager.Torrent.Files.Count}");
        
        Console.WriteLine("\nFiles:");
        foreach (var file in manager.Torrent.Files)
        {
            Console.WriteLine($"- {file.Path} ({FormatSize(file.Length)})");
        }
        
        Console.WriteLine("\nTrackers:");
        foreach (var tier in manager.Torrent.AnnounceUrls)
        {
            foreach (var tracker in tier)
            {
                Console.WriteLine($"- {tracker}");
            }
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
    
    private static string GenerateMagnetLink(Torrent torrent)
    {
        var sb = new StringBuilder($"magnet:?xt=urn:btih:{torrent.InfoHash.ToHex()}");
        
        if (!string.IsNullOrEmpty(torrent.Name))
        {
            sb.Append($"&dn={Uri.EscapeDataString(torrent.Name)}");
        }
        
        foreach (var tier in torrent.AnnounceUrls)
        {
            foreach (var tracker in tier)
            {
                sb.Append($"&tr={Uri.EscapeDataString(tracker)}");
            }
        }
        
        return sb.ToString();
    }
}
```

This example shows how to work with magnet links, including parsing, adding to the client engine, handling metadata download, and creating new magnet links from existing torrents.