# Creating a Torrent Creator

This tutorial will guide you through building a tool to create torrent files using MonoTorrent's `TorrentCreator` class. You'll learn how to create torrents from files and directories, customize torrent properties, and optimize the creation process.

## Prerequisites

Before starting this tutorial, make sure you have:

- Installed MonoTorrent via NuGet or from source
- Basic understanding of C# and async programming
- Files or directories that you want to create torrents from

## Understanding Torrent Creation

Creating a torrent file involves these steps:

1. Specifying files or directories to include
2. Setting metadata like comments, creation date, and publisher info
3. Configuring trackers and DHT settings
4. Calculating piece hashes (the most time-consuming part)
5. Saving the resulting torrent file

MonoTorrent's `TorrentCreator` class handles these steps for you.

## Basic Torrent Creation

Let's start with creating a simple torrent from a single file:

```csharp
using MonoTorrent;
using System;
using System.IO;
using System.Threading.Tasks;

// Create a new TorrentCreator instance
var creator = new TorrentCreator();

// Add a file to the torrent
string filePath = "path/to/your/file.mp4";
creator.AddFile(filePath);

// Add tracker URLs
creator.Announces.Add(new[] {
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://tracker.openbittorrent.com:6969/announce"
});

// Set metadata
creator.Comment = "My first torrent created with MonoTorrent";
creator.Publisher = "Your Name";
creator.CreatedBy = "Torrent Creator Tutorial";

// Create and save the torrent file
string torrentPath = Path.Combine(Path.GetDirectoryName(filePath), 
                                 Path.GetFileNameWithoutExtension(filePath) + ".torrent");
await creator.CreateAsync(torrentPath);

Console.WriteLine($"Torrent created successfully: {torrentPath}");
```

## Creating a Torrent from Multiple Files

To create a torrent from multiple files:

```csharp
// Create a new TorrentCreator instance
var creator = new TorrentCreator();

// Add multiple files to the torrent
creator.AddFile("path/to/file1.mp4");
creator.AddFile("path/to/file2.mp3");
creator.AddFile("path/to/file3.txt");

// Set the torrent name (folder name in the torrent)
creator.Name = "My Collection";

// Add tracker URLs and other metadata...

// Create and save the torrent file
await creator.CreateAsync("path/to/output/MyCollection.torrent");
```

## Creating a Torrent from a Directory

To create a torrent from an entire directory:

```csharp
// Create a new TorrentCreator instance
var creator = new TorrentCreator();

// Add a directory to the torrent
string directoryPath = "path/to/your/directory";
creator.AddDirectory(directoryPath);

// The torrent name will default to the directory name, but you can override it
creator.Name = Path.GetFileName(directoryPath);

// Add tracker URLs and other metadata...

// Create and save the torrent file
string torrentPath = Path.Combine(Path.GetDirectoryName(directoryPath), 
                                 Path.GetFileName(directoryPath) + ".torrent");
await creator.CreateAsync(torrentPath);
```

## Optimizing Piece Length

The piece length affects torrent performance. Smaller pieces provide more granular download verification but increase torrent file size. Larger pieces reduce overhead but may cause more data to be re-downloaded if errors occur.

Here's how to set an optimal piece length based on the total content size:

```csharp
// Calculate optimal piece length based on total size
long CalculateOptimalPieceLength(long totalSize)
{
    if (totalSize < 50 * 1024 * 1024)        // Less than 50 MB
        return 16 * 1024;                     // 16 KB pieces
    else if (totalSize < 500 * 1024 * 1024)   // Less than 500 MB
        return 64 * 1024;                     // 64 KB pieces
    else if (totalSize < 1024 * 1024 * 1024)  // Less than 1 GB
        return 256 * 1024;                    // 256 KB pieces
    else if (totalSize < 4 * 1024 * 1024 * 1024L) // Less than 4 GB
        return 1 * 1024 * 1024;               // 1 MB pieces
    else
        return 4 * 1024 * 1024;               // 4 MB pieces for very large torrents
}

// Usage
var creator = new TorrentCreator();
creator.AddDirectory("path/to/directory");

// Calculate total size
long totalSize = CalculateTotalSize("path/to/directory");
creator.PieceLength = CalculateOptimalPieceLength(totalSize);

// Helper method to calculate total size
long CalculateTotalSize(string directoryPath)
{
    long size = 0;
    foreach (var file in Directory.GetFiles(directoryPath, "*", SearchOption.AllDirectories))
    {
        size += new FileInfo(file).Length;
    }
    return size;
}
```

## Creating Private Torrents

Private torrents are restricted to specific trackers and disable DHT, PEX, and LPD:

```csharp
// Create a private torrent
var creator = new TorrentCreator();
creator.AddDirectory("path/to/directory");

// Set it as private
creator.Private = true;

// For private torrents, make sure to include tracker URLs
creator.Announces.Add(new[] { 
    "https://private-tracker.example.com/announce" 
});

// Create and save
await creator.CreateAsync("path/to/output/PrivateTorrent.torrent");
```

## Adding WebSeeds

WebSeeds provide direct HTTP/HTTPS sources for downloading content:

```csharp
// Create a new TorrentCreator
var creator = new TorrentCreator();
creator.AddDirectory("path/to/directory");

// Add trackers
creator.Announces.Add(new[] { "udp://tracker.example.com:6969/announce" });

// Add WebSeeds (direct download URLs)
creator.WebSeeds.Add("https://example.com/downloads/mycontent.zip");
creator.WebSeeds.Add("https://mirror.example.net/mycontent.zip");

// Create and save
await creator.CreateAsync("path/to/output/WebSeedTorrent.torrent");
```

## Handling Progress Updates

For large torrents, calculating piece hashes can take time. You can track progress:

```csharp
// Create a new TorrentCreator
var creator = new TorrentCreator();
creator.AddDirectory("path/to/large/directory");

// Subscribe to the hashing progress event
creator.Hashed += (sender, e) => {
    double percentComplete = (double)e.PiecesHashed / e.TotalPieces * 100;
    Console.WriteLine($"Hashing progress: {percentComplete:0.00}% ({e.PiecesHashed}/{e.TotalPieces})");
};

// Create and save the torrent
await creator.CreateAsync("path/to/output/LargeTorrent.torrent");
```

## Building a Complete Torrent Creator Application

Let's create a complete console application for creating torrents:

```csharp
using MonoTorrent;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

public class TorrentCreatorApp
{
    public static async Task Main(string[] args)
    {
        Console.WriteLine("MonoTorrent - Torrent Creator");
        Console.WriteLine("=============================\n");
        
        try
        {
            // Get the path to create a torrent from
            string sourcePath = GetSourcePath();
            
            // Get output torrent path
            string outputPath = GetOutputPath(sourcePath);
            
            // Create the torrent creator
            var creator = new TorrentCreator();
            
            // Add files or directory
            if (File.Exists(sourcePath))
            {
                Console.WriteLine($"Adding file: {sourcePath}");
                creator.AddFile(sourcePath);
                
                // Default name to the file name
                creator.Name = Path.GetFileNameWithoutExtension(sourcePath);
            }
            else if (Directory.Exists(sourcePath))
            {
                Console.WriteLine($"Adding directory: {sourcePath}");
                creator.AddDirectory(sourcePath);
                
                // Default name to the directory name
                creator.Name = Path.GetFileName(sourcePath);
            }
            else
            {
                Console.WriteLine("Error: Source path does not exist");
                return;
            }
            
            // Get torrent metadata
            GetTorrentMetadata(creator);
            
            // Calculate optimal piece length
            long totalSize = CalculateTotalSize(sourcePath);
            creator.PieceLength = CalculateOptimalPieceLength(totalSize);
            Console.WriteLine($"Using piece length: {FormatSize(creator.PieceLength)}");
            
            // Subscribe to hashing progress
            Console.WriteLine("\nCalculating piece hashes. This may take a while...");
            
            creator.Hashed += (sender, e) => {
                int percent = (int)((double)e.PiecesHashed / e.TotalPieces * 100);
                
                // Update progress on the same line
                Console.Write($"\rHashing: {percent}% complete ({e.PiecesHashed}/{e.TotalPieces})");
            };
            
            // Create the torrent
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            await creator.CreateAsync(outputPath);
            stopwatch.Stop();
            
            Console.WriteLine($"\n\nTorrent created successfully: {outputPath}");
            Console.WriteLine($"Creation time: {stopwatch.Elapsed.TotalSeconds:0.00} seconds");
            
            // Display the torrent info
            DisplayTorrentInfo(outputPath);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
    
    private static string GetSourcePath()
    {
        while (true)
        {
            Console.Write("Enter the path to the file or directory to create a torrent from: ");
            string path = Console.ReadLine().Trim('"');  // Remove quotes if user copied from explorer
            
            if (File.Exists(path) || Directory.Exists(path))
                return path;
                
            Console.WriteLine("Error: Invalid path. Please enter a valid file or directory path.");
        }
    }
    
    private static string GetOutputPath(string sourcePath)
    {
        string defaultName;
        
        if (File.Exists(sourcePath))
            defaultName = Path.GetFileNameWithoutExtension(sourcePath) + ".torrent";
        else
            defaultName = Path.GetFileName(sourcePath) + ".torrent";
            
        string defaultPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), defaultName);
        
        Console.Write($"Enter the output torrent path (default: {defaultPath}): ");
        string outputPath = Console.ReadLine();
        
        if (string.IsNullOrWhiteSpace(outputPath))
            return defaultPath;
            
        return outputPath.Trim('"');
    }
    
    private static void GetTorrentMetadata(TorrentCreator creator)
    {
        // Get torrent name
        Console.Write($"Enter torrent name (default: {creator.Name}): ");
        string name = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(name))
            creator.Name = name;
            
        // Add trackers
        List<string> trackers = new List<string>();
        Console.WriteLine("\nEnter tracker URLs (empty line to finish):");
        
        while (true)
        {
            Console.Write("Tracker URL: ");
            string tracker = Console.ReadLine();
            
            if (string.IsNullOrWhiteSpace(tracker))
                break;
                
            trackers.Add(tracker);
        }
        
        if (trackers.Count == 0)
        {
            // Add some common public trackers
            Console.WriteLine("No trackers specified. Adding common public trackers.");
            trackers.AddRange(new[] {
                "udp://tracker.opentrackr.org:1337/announce",
                "udp://tracker.openbittorrent.com:6969/announce",
                "udp://tracker.internetwarriors.net:1337/announce"
            });
        }
        
        // Add trackers to creator
        creator.Announces.Add(trackers.ToArray());
        
        // Get comment
        Console.Write("Enter torrent comment: ");
        string comment = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(comment))
            creator.Comment = comment;
            
        // Get publisher
        Console.Write("Enter publisher name: ");
        string publisher = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(publisher))
            creator.Publisher = publisher;
            
        // Get publisher URL
        Console.Write("Enter publisher URL: ");
        string publisherUrl = Console.ReadLine();
        if (!string.IsNullOrWhiteSpace(publisherUrl))
            creator.PublisherUrl = publisherUrl;
            
        // Set created by
        creator.CreatedBy = "MonoTorrent Creator App";
        
        // Check if it should be private
        Console.Write("Create private torrent? (y/n, default: n): ");
        string privateInput = Console.ReadLine();
        creator.Private = privateInput.Trim().ToLower() == "y";
        
        // Add WebSeeds if any
        Console.WriteLine("\nEnter WebSeed URLs (direct HTTP/HTTPS download links) (empty line to finish):");
        
        while (true)
        {
            Console.Write("WebSeed URL: ");
            string webSeed = Console.ReadLine();
            
            if (string.IsNullOrWhiteSpace(webSeed))
                break;
                
            creator.WebSeeds.Add(webSeed);
        }
    }
    
    private static long CalculateTotalSize(string path)
    {
        if (File.Exists(path))
            return new FileInfo(path).Length;
            
        long size = 0;
        foreach (var file in Directory.GetFiles(path, "*", SearchOption.AllDirectories))
        {
            size += new FileInfo(file).Length;
        }
        
        Console.WriteLine($"Total content size: {FormatSize(size)}");
        return size;
    }
    
    private static long CalculateOptimalPieceLength(long totalSize)
    {
        if (totalSize < 50 * 1024 * 1024)         // Less than 50 MB
            return 16 * 1024;                      // 16 KB pieces
        else if (totalSize < 500 * 1024 * 1024)    // Less than 500 MB
            return 64 * 1024;                      // 64 KB pieces
        else if (totalSize < 1024 * 1024 * 1024)   // Less than 1 GB
            return 256 * 1024;                     // 256 KB pieces
        else if (totalSize < 4 * 1024 * 1024 * 1024L) // Less than 4 GB
            return 1 * 1024 * 1024;                // 1 MB pieces
        else
            return 4 * 1024 * 1024;                // 4 MB pieces
    }
    
    private static void DisplayTorrentInfo(string torrentPath)
    {
        try
        {
            var torrent = Torrent.Load(torrentPath);
            
            Console.WriteLine("\nTorrent Information:");
            Console.WriteLine($"Name: {torrent.Name}");
            Console.WriteLine($"Size: {FormatSize(torrent.Size)}");
            Console.WriteLine($"Piece Length: {FormatSize(torrent.PieceLength)}");
            Console.WriteLine($"Piece Count: {torrent.Pieces.Count}");
            Console.WriteLine($"InfoHash: {torrent.InfoHash.ToHex()}");
            Console.WriteLine($"Created: {torrent.CreationDate}");
            Console.WriteLine($"Created By: {torrent.CreatedBy}");
            Console.WriteLine($"Comment: {torrent.Comment}");
            Console.WriteLine($"Private: {torrent.IsPrivate}");
            
            // Display trackers
            Console.WriteLine("\nTrackers:");
            foreach (var tier in torrent.AnnounceUrls)
            {
                foreach (var tracker in tier)
                {
                    Console.WriteLine($"- {tracker}");
                }
            }
            
            // Display WebSeeds if any
            if (torrent.WebSeeds.Count > 0)
            {
                Console.WriteLine("\nWebSeeds:");
                foreach (var webSeed in torrent.WebSeeds)
                {
                    Console.WriteLine($"- {webSeed}");
                }
            }
            
            // Display files
            Console.WriteLine("\nFiles:");
            int fileCount = torrent.Files.Count;
            int displayCount = Math.Min(fileCount, 10); // Show at most 10 files
            
            for (int i = 0; i < displayCount; i++)
            {
                var file = torrent.Files[i];
                Console.WriteLine($"- {file.Path} ({FormatSize(file.Length)})");
            }
            
            if (fileCount > displayCount)
            {
                Console.WriteLine($"... and {fileCount - displayCount} more files");
            }
            
            // Create magnet link
            string magnetLink = $"magnet:?xt=urn:btih:{torrent.InfoHash.ToHex()}&dn={Uri.EscapeDataString(torrent.Name)}";
            
            foreach (var tier in torrent.AnnounceUrls)
            {
                foreach (var tracker in tier)
                {
                    magnetLink += $"&tr={Uri.EscapeDataString(tracker)}";
                }
            }
            
            Console.WriteLine("\nMagnet Link:");
            Console.WriteLine(magnetLink);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error reading torrent: {ex.Message}");
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

## Creating a Batch Torrent Creator

For creating multiple torrents at once, you can extend the application:

```csharp
// Add a method to process a batch of files or directories
private static async Task ProcessBatchAsync(string batchFile)
{
    if (!File.Exists(batchFile))
    {
        Console.WriteLine($"Batch file not found: {batchFile}");
        return;
    }
    
    string[] lines = await File.ReadAllLinesAsync(batchFile);
    int total = lines.Length;
    int successful = 0;
    
    Console.WriteLine($"Processing {total} items from batch file...\n");
    
    for (int i = 0; i < total; i++)
    {
        string line = lines[i].Trim();
        if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#"))
            continue;
            
        Console.WriteLine($"Processing item {i+1}/{total}: {line}");
        
        try
        {
            if (File.Exists(line) || Directory.Exists(line))
            {
                var creator = new TorrentCreator();
                
                // Add the file or directory
                if (File.Exists(line))
                {
                    creator.AddFile(line);
                    creator.Name = Path.GetFileNameWithoutExtension(line);
                }
                else
                {
                    creator.AddDirectory(line);
                    creator.Name = Path.GetFileName(line);
                }
                
                // Add default trackers
                creator.Announces.Add(new[] {
                    "udp://tracker.opentrackr.org:1337/announce",
                    "udp://tracker.openbittorrent.com:6969/announce"
                });
                
                // Set created by
                creator.CreatedBy = "MonoTorrent Batch Creator";
                
                // Set optimal piece length
                long totalSize = CalculateTotalSize(line);
                creator.PieceLength = CalculateOptimalPieceLength(totalSize);
                
                // Generate output path
                string outputDir = Path.GetDirectoryName(batchFile);
                string outputFile = Path.Combine(outputDir, creator.Name + ".torrent");
                
                // Create the torrent
                await creator.CreateAsync(outputFile);
                Console.WriteLine($"Created: {outputFile}");
                successful++;
            }
            else
            {
                Console.WriteLine($"Error: Path not found: {line}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error creating torrent: {ex.Message}");
        }
        
        Console.WriteLine();
    }
    
    Console.WriteLine($"Batch processing complete. Created {successful}/{total} torrents successfully.");
}
```

## Advanced Topics

### Implementing a Cross-Platform GUI

To create a more user-friendly application, consider implementing a GUI. Here's a sketch of a cross-platform GUI using Avalonia UI:

```csharp
// Avalonia UI XAML
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Torrent Creator" Width="600" Height="700">
    <Grid RowDefinitions="Auto,*,Auto" Margin="10">
        <!-- Source Selection -->
        <StackPanel Grid.Row="0" Spacing="10">
            <TextBlock Text="Source Files or Directory" FontWeight="Bold"/>
            <Grid ColumnDefinitions="*,Auto">
                <TextBox Grid.Column="0" Text="{Binding SourcePath}" Watermark="Select files or directory"/>
                <Button Grid.Column="1" Content="Browse..." Command="{Binding BrowseCommand}" Margin="5,0,0,0"/>
            </Grid>
            
            <!-- Torrent Metadata -->
            <TextBlock Text="Torrent Information" FontWeight="Bold" Margin="0,10,0,0"/>
            <Grid RowDefinitions="Auto,Auto,Auto,Auto" ColumnDefinitions="Auto,*">
                <TextBlock Grid.Row="0" Grid.Column="0" Text="Name:" VerticalAlignment="Center" Margin="0,0,10,0"/>
                <TextBox Grid.Row="0" Grid.Column="1" Text="{Binding TorrentName}"/>
                
                <TextBlock Grid.Row="1" Grid.Column="0" Text="Comment:" VerticalAlignment="Center" Margin="0,0,10,0"/>
                <TextBox Grid.Row="1" Grid.Column="1" Text="{Binding Comment}"/>
                
                <TextBlock Grid.Row="2" Grid.Column="0" Text="Publisher:" VerticalAlignment="Center" Margin="0,0,10,0"/>
                <TextBox Grid.Row="2" Grid.Column="1" Text="{Binding Publisher}"/>
                
                <TextBlock Grid.Row="3" Grid.Column="0" Text="Private:" VerticalAlignment="Center" Margin="0,0,10,0"/>
                <CheckBox Grid.Row="3" Grid.Column="1" IsChecked="{Binding IsPrivate}"/>
            </Grid>
        </StackPanel>
        
        <!-- Main Content -->
        <TabControl Grid.Row="1" Margin="0,10">
            <TabItem Header="Trackers">
                <Grid RowDefinitions="*,Auto">
                    <ListBox Grid.Row="0" Items="{Binding Trackers}"/>
                    <Grid Grid.Row="1" ColumnDefinitions="*,Auto,Auto" Margin="0,5,0,0">
                        <TextBox Grid.Column="0" Text="{Binding NewTracker}" Watermark="Enter tracker URL"/>
                        <Button Grid.Column="1" Content="Add" Command="{Binding AddTrackerCommand}" Margin="5,0,0,0"/>
                        <Button Grid.Column="2" Content="Remove" Command="{Binding RemoveTrackerCommand}" Margin="5,0,0,0"/>
                    </Grid>
                </Grid>
            </TabItem>
            <TabItem Header="WebSeeds">
                <Grid RowDefinitions="*,Auto">
                    <ListBox Grid.Row="0" Items="{Binding WebSeeds}"/>
                    <Grid Grid.Row="1" ColumnDefinitions="*,Auto,Auto" Margin="0,5,0,0">
                        <TextBox Grid.Column="0" Text="{Binding NewWebSeed}" Watermark="Enter WebSeed URL"/>
                        <Button Grid.Column="1" Content="Add" Command="{Binding AddWebSeedCommand}" Margin="5,0,0,0"/>
                        <Button Grid.Column="2" Content="Remove" Command="{Binding RemoveWebSeedCommand}" Margin="5,0,0,0"/>
                    </Grid>
                </Grid>
            </TabItem>
            <TabItem Header="Advanced Settings">
                <StackPanel Spacing="10" Margin="0,10,0,0">
                    <Grid ColumnDefinitions="Auto,*">
                        <TextBlock Grid.Column="0" Text="Piece Size:" VerticalAlignment="Center" Margin="0,0,10,0"/>
                        <ComboBox Grid.Column="1" Items="{Binding PieceSizes}" SelectedItem="{Binding SelectedPieceSize}" Width="200" HorizontalAlignment="Left"/>
                    </Grid>
                    <CheckBox Content="Auto-optimize piece size based on content" IsChecked="{Binding AutoOptimizePieceSize}"/>
                    <TextBlock Text="Creation Date:" Margin="0,10,0,0"/>
                    <DatePicker SelectedDate="{Binding CreationDate}"/>
                </StackPanel>
            </TabItem>
            <TabItem Header="Files">
                <ListBox Items="{Binding IncludedFiles}">
                    <ListBox.ItemTemplate>
                        <DataTemplate>
                            <Grid ColumnDefinitions="*,Auto">
                                <TextBlock Grid.Column="0" Text="{Binding Path}"/>
                                <TextBlock Grid.Column="1" Text="{Binding Size}" Margin="10,0,0,0"/>
                            </Grid>
                        </DataTemplate>
                    </ListBox.ItemTemplate>
                </ListBox>
            </TabItem>
        </TabControl>
        
        <!-- Status and Controls -->
        <Grid Grid.Row="2" RowDefinitions="Auto,Auto">
            <ProgressBar Grid.Row="0" Value="{Binding Progress}" IsVisible="{Binding IsCreating}" Height="20" Margin="0,0,0,10"/>
            <TextBlock Grid.Row="0" Text="{Binding Status}" HorizontalAlignment="Center" VerticalAlignment="Center" IsVisible="{Binding IsCreating}"/>
            
            <Grid Grid.Row="1" ColumnDefinitions="*,Auto">
                <Button Grid.Column="1" Content="Create Torrent" Command="{Binding CreateCommand}" IsEnabled="{Binding !IsCreating}"/>
            </Grid>
        </Grid>
    </Grid>
</Window>
```

### Creating v2 Torrents

BitTorrent v2 (BEP 52) improves security with SHA-256 hashing and other enhancements. While MonoTorrent doesn't fully support v2 torrents yet, you can prepare your application for future compatibility.

## Conclusion

This tutorial has covered creating a comprehensive torrent creator using MonoTorrent. You've learned how to:

1. Create torrents from single files and directories
2. Set metadata and tracker information
3. Optimize piece length for different content sizes
4. Create private torrents
5. Add WebSeeds for direct downloads
6. Handle progress updates during creation
7. Build a complete torrent creator application
8. Implement a batch torrent creator

With these skills, you can create a fully functional torrent creator that meets your specific needs.

## Related Resources

- [TorrentCreator API Reference](../api_reference/common/TorrentCreator.md)
- [Torrent API Reference](../api_reference/common/Torrent.md)
- [Simple Client Tutorial](simple_client_tutorial.md)
- [Building a Tracker Tutorial](tracker_tutorial.md)