# Streaming Torrents with MonoTorrent

This example demonstrates how to set up and use MonoTorrent's streaming capabilities to stream content while downloading.

## Overview

Torrent streaming allows users to start playing media files before they've been completely downloaded. MonoTorrent supports streaming by prioritizing the download of pieces in sequential order, starting from the current playback position.

## Streaming Implementation

### Basic Streaming Setup

```csharp
using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;
using MonoTorrent.Streaming;

namespace MonoTorrentStreaming
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Create temporary directory for downloaded data
            string downloadPath = Path.Combine(Path.GetTempPath(), "MonoTorrentStreaming");
            Directory.CreateDirectory(downloadPath);
            
            try
            {
                // Create engine settings
                var settings = new EngineSettings
                {
                    AllowedEncryption = EncryptionTypes.All,
                    MaximumConnections = 60,
                    MaximumDownloadRate = 0, // Unlimited
                    MaximumUploadRate = 100 * 1024, // 100 KB/s
                    ListenPort = 55123
                };
                
                // Create the client engine
                using var engine = new ClientEngine(settings);
                
                // Load the torrent or magnet link
                Console.Write("Enter path to .torrent file or magnet link: ");
                string input = Console.ReadLine().Trim();
                
                TorrentManager manager;
                
                if (input.StartsWith("magnet:", StringComparison.OrdinalIgnoreCase))
                {
                    var magnetLink = MagnetLink.Parse(input);
                    manager = await engine.AddStreamingAsync(magnetLink, downloadPath);
                }
                else
                {
                    manager = await engine.AddStreamingAsync(input, downloadPath);
                }
                
                // Start the torrent
                await manager.StartAsync();
                
                // Wait for metadata if this is a magnet link
                if (!manager.HasMetadata)
                {
                    Console.WriteLine("Downloading torrent metadata...");
                    while (!manager.HasMetadata)
                    {
                        await Task.Delay(500);
                    }
                    Console.WriteLine("Metadata download complete.");
                }
                
                // Display available files
                Console.WriteLine("\nAvailable files:");
                for (int i = 0; i < manager.Files.Count; i++)
                {
                    Console.WriteLine($"{i + 1}. {manager.Files[i].Path} ({FormatSize(manager.Files[i].Length)})");
                }
                
                // Let user select a file to stream
                Console.Write("\nEnter the number of the file to stream: ");
                if (!int.TryParse(Console.ReadLine(), out int fileIndex) || fileIndex < 1 || fileIndex > manager.Files.Count)
                {
                    Console.WriteLine("Invalid selection. Exiting.");
                    return;
                }
                
                var selectedFile = manager.Files[fileIndex - 1];
                
                // Create a stream for the selected file
                Console.WriteLine($"\nStreaming: {selectedFile.Path}");
                using var stream = await manager.StreamProvider.CreateStreamAsync(selectedFile);
                
                // Display stream information
                Console.WriteLine($"Stream length: {FormatSize(stream.Length)}");
                Console.WriteLine($"Stream can seek: {stream.CanSeek}");
                
                // Track stream progress in a separate task
                _ = Task.Run(async () => await TrackStreamProgressAsync(manager, stream, selectedFile));
                
                // Main streaming simulation
                await SimulateStreamingAsync(stream);
                
                // Clean up
                Console.WriteLine("\nStreaming complete. Press any key to exit...");
                Console.ReadKey();
                
                await manager.StopAsync();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            finally
            {
                // Optionally clean up the temporary directory
                // Directory.Delete(downloadPath, true);
            }
        }
        
        static async Task TrackStreamProgressAsync(TorrentManager manager, Stream stream, ITorrentFileInfo file)
        {
            long prevStreamPosition = 0;
            
            while (true)
            {
                // Calculate streaming progress
                double downloadProgress = manager.Progress;
                double streamProgress = (double)stream.Position / stream.Length * 100;
                
                // Calculate streaming rate
                long bytesRead = stream.Position - prevStreamPosition;
                prevStreamPosition = stream.Position;
                double streamRate = bytesRead / 1024.0; // KB/s
                
                // Calculate buffer size (how much ahead we've downloaded)
                long streamPosition = stream.Position;
                long fileOffset = file.StartPieceIndex * manager.Torrent.PieceLength + 
                                  (streamPosition / manager.Torrent.PieceLength) * manager.Torrent.PieceLength;
                long bufferBytes = 0;
                
                for (int i = file.StartPieceIndex; i <= file.EndPieceIndex; i++)
                {
                    if (manager.Bitfield[i] && i * manager.Torrent.PieceLength >= fileOffset)
                    {
                        bufferBytes += manager.Torrent.PieceLength;
                    }
                    else if (i * manager.Torrent.PieceLength >= fileOffset)
                    {
                        break;
                    }
                }
                
                // Display progress information
                Console.Clear();
                Console.WriteLine($"File: {file.Path}");
                Console.WriteLine($"Total Download Progress: {downloadProgress:F2}%");
                Console.WriteLine($"Stream Position: {FormatSize(stream.Position)} / {FormatSize(stream.Length)} ({streamProgress:F2}%)");
                Console.WriteLine($"Download Speed: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
                Console.WriteLine($"Stream Rate: {streamRate:F2} KB/s");
                Console.WriteLine($"Buffer Size: {FormatSize(bufferBytes)}");
                Console.WriteLine($"Connected Peers: {manager.Peers.ConnectedPeers.Count}");
                Console.WriteLine();
                Console.WriteLine("Streaming simulation in progress...");
                Console.WriteLine("Press Ctrl+C to exit");
                
                await Task.Delay(1000);
            }
        }
        
        static async Task SimulateStreamingAsync(Stream stream)
        {
            // This method simulates reading from the stream as a video player would
            byte[] buffer = new byte[16 * 1024]; // 16 KB buffer
            long totalBytesRead = 0;
            
            try
            {
                while (totalBytesRead < stream.Length)
                {
                    // Read a chunk of data
                    int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                    if (bytesRead == 0)
                    {
                        // If we can't read more data yet, wait a bit
                        await Task.Delay(500);
                        continue;
                    }
                    
                    totalBytesRead += bytesRead;
                    
                    // Simulate processing time for a video player
                    await Task.Delay(100);
                    
                    // Every 50 MB, simulate a seek operation (like skipping ahead in a video)
                    if (totalBytesRead % (50 * 1024 * 1024) < buffer.Length && totalBytesRead > buffer.Length)
                    {
                        long newPosition = Math.Min(stream.Position + 10 * 1024 * 1024, stream.Length - 1);
                        stream.Position = newPosition;
                        Console.WriteLine($"\nSimulating seek to position {FormatSize(newPosition)}");
                    }
                }
            }
            catch (EndOfStreamException)
            {
                Console.WriteLine("Reached end of stream");
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine("Streaming operation canceled");
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
}
```

## Advanced Streaming Example

This example extends the basic streaming functionality to include a simple HTTP server to stream content to external media players.

```csharp
using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using MonoTorrent;
using MonoTorrent.Client;
using MonoTorrent.Streaming;

namespace MonoTorrentHttpStreaming
{
    class Program
    {
        private static readonly ManualResetEvent waitHandle = new ManualResetEvent(false);
        private static HttpListener httpListener;
        private static TorrentManager streamingManager;
        private static string downloadPath;
        
        static async Task Main(string[] args)
        {
            // Create temporary directory for downloaded data
            downloadPath = Path.Combine(Path.GetTempPath(), "MonoTorrentHttpStreaming");
            Directory.CreateDirectory(downloadPath);
            
            try
            {
                // Create engine settings
                var settings = new EngineSettings
                {
                    AllowedEncryption = EncryptionTypes.All,
                    MaximumConnections = 60,
                    MaximumDownloadRate = 0, // Unlimited
                    MaximumUploadRate = 100 * 1024, // 100 KB/s
                    ListenPort = 55123
                };
                
                // Create the client engine
                using var engine = new ClientEngine(settings);
                
                // Load the torrent or magnet link
                Console.Write("Enter path to .torrent file or magnet link: ");
                string input = Console.ReadLine().Trim();
                
                if (input.StartsWith("magnet:", StringComparison.OrdinalIgnoreCase))
                {
                    var magnetLink = MagnetLink.Parse(input);
                    streamingManager = await engine.AddStreamingAsync(magnetLink, downloadPath);
                }
                else
                {
                    streamingManager = await engine.AddStreamingAsync(input, downloadPath);
                }
                
                // Start the torrent
                await streamingManager.StartAsync();
                
                // Wait for metadata if this is a magnet link
                if (!streamingManager.HasMetadata)
                {
                    Console.WriteLine("Downloading torrent metadata...");
                    while (!streamingManager.HasMetadata)
                    {
                        await Task.Delay(500);
                    }
                    Console.WriteLine("Metadata download complete.");
                }
                
                // Display available files
                Console.WriteLine("\nAvailable files:");
                for (int i = 0; i < streamingManager.Files.Count; i++)
                {
                    var file = streamingManager.Files[i];
                    Console.WriteLine($"{i + 1}. {file.Path} ({FormatSize(file.Length)})");
                }
                
                // Start the HTTP streaming server
                int httpPort = 8080;
                StartHttpServer(httpPort);
                
                // Output streaming URLs
                Console.WriteLine("\nStreaming URLs:");
                
                for (int i = 0; i < streamingManager.Files.Count; i++)
                {
                    var file = streamingManager.Files[i];
                    string extension = Path.GetExtension(file.Path).ToLowerInvariant();
                    
                    if (IsMediaFile(extension))
                    {
                        string streamUrl = $"http://localhost:{httpPort}/stream/{i}";
                        Console.WriteLine($"{file.Path}: {streamUrl}");
                    }
                }
                
                Console.WriteLine("\nStreaming server started. Press Ctrl+C to exit.");
                
                // Monitor the torrent in a separate task
                _ = Task.Run(() => MonitorTorrentAsync(streamingManager));
                
                // Wait for exit signal
                Console.CancelKeyPress += (sender, e) => {
                    e.Cancel = true;
                    waitHandle.Set();
                };
                
                waitHandle.WaitOne();
                
                // Clean up
                StopHttpServer();
                await streamingManager.StopAsync();
                
                Console.WriteLine("Streaming service stopped.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            finally
            {
                // Optionally clean up the temporary directory
                // Directory.Delete(downloadPath, true);
            }
        }
        
        static void StartHttpServer(int port)
        {
            httpListener = new HttpListener();
            httpListener.Prefixes.Add($"http://localhost:{port}/");
            httpListener.Start();
            
            Task.Run(async () => {
                while (httpListener.IsListening)
                {
                    try
                    {
                        var context = await httpListener.GetContextAsync();
                        _ = HandleRequestAsync(context);
                    }
                    catch (HttpListenerException)
                    {
                        break; // Listener was stopped
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"HTTP server error: {ex.Message}");
                    }
                }
            });
        }
        
        static void StopHttpServer()
        {
            if (httpListener != null && httpListener.IsListening)
            {
                httpListener.Stop();
                httpListener.Close();
            }
        }
        
        static async Task HandleRequestAsync(HttpListenerContext context)
        {
            string path = context.Request.Url.AbsolutePath;
            string query = context.Request.Url.Query;
            
            try
            {
                if (path.StartsWith("/stream/"))
                {
                    // Extract file index from path
                    string indexStr = path.Substring("/stream/".Length);
                    if (int.TryParse(indexStr, out int fileIndex) && 
                        fileIndex >= 0 && 
                        fileIndex < streamingManager.Files.Count)
                    {
                        await StreamFileAsync(context, fileIndex);
                    }
                    else
                    {
                        Send404(context);
                    }
                }
                else if (path == "/status")
                {
                    await SendStatusAsync(context);
                }
                else if (path == "/")
                {
                    await SendIndexPageAsync(context);
                }
                else
                {
                    Send404(context);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error handling request: {ex.Message}");
                try
                {
                    Send500(context, ex.Message);
                }
                catch
                {
                    // Ignore errors when sending error responses
                }
            }
        }
        
        static async Task StreamFileAsync(HttpListenerContext context, int fileIndex)
        {
            var file = streamingManager.Files[fileIndex];
            string fileName = Path.GetFileName(file.Path);
            string extension = Path.GetExtension(fileName).ToLowerInvariant();
            
            // Get MIME type
            string contentType = GetMimeType(extension);
            
            // Handle range requests for seeking
            long startByte = 0;
            long endByte = file.Length - 1;
            bool isRangeRequest = false;
            
            if (context.Request.Headers["Range"] != null)
            {
                string rangeHeader = context.Request.Headers["Range"];
                if (rangeHeader.StartsWith("bytes="))
                {
                    isRangeRequest = true;
                    string[] range = rangeHeader.Substring("bytes=".Length).Split('-');
                    if (range.Length == 2)
                    {
                        if (!string.IsNullOrEmpty(range[0]))
                            startByte = long.Parse(range[0]);
                        
                        if (!string.IsNullOrEmpty(range[1]))
                            endByte = long.Parse(range[1]);
                    }
                }
            }
            
            // Create a stream for the file
            using var stream = await streamingManager.StreamProvider.CreateStreamAsync(file);
            
            try
            {
                // Set the response headers
                context.Response.ContentType = contentType;
                context.Response.AddHeader("Accept-Ranges", "bytes");
                
                if (isRangeRequest)
                {
                    context.Response.StatusCode = 206; // Partial content
                    context.Response.AddHeader("Content-Range", $"bytes {startByte}-{endByte}/{file.Length}");
                    context.Response.ContentLength64 = endByte - startByte + 1;
                }
                else
                {
                    context.Response.StatusCode = 200; // OK
                    context.Response.ContentLength64 = file.Length;
                }
                
                // Set position for range requests
                if (startByte > 0)
                {
                    stream.Position = startByte;
                }
                
                // Stream the file
                byte[] buffer = new byte[64 * 1024]; // 64 KB buffer
                long remaining = context.Response.ContentLength64;
                
                while (remaining > 0)
                {
                    int read = await stream.ReadAsync(buffer, 0, (int)Math.Min(buffer.Length, remaining));
                    if (read == 0)
                    {
                        // Wait for more data to become available
                        await Task.Delay(100);
                        continue;
                    }
                    
                    await context.Response.OutputStream.WriteAsync(buffer, 0, read);
                    remaining -= read;
                }
            }
            catch (HttpListenerException)
            {
                // Client disconnected
            }
            finally
            {
                context.Response.Close();
            }
        }
        
        static async Task SendStatusAsync(HttpListenerContext context)
        {
            var statusInfo = new
            {
                TorrentName = streamingManager.Torrent?.Name ?? "Unknown",
                State = streamingManager.State.ToString(),
                Progress = streamingManager.Progress,
                DownloadRate = streamingManager.Monitor.DownloadRate,
                UploadRate = streamingManager.Monitor.UploadRate,
                ConnectedPeers = streamingManager.Peers.ConnectedPeers.Count,
                Files = streamingManager.Files.Select(f => new
                {
                    Path = f.Path,
                    Length = f.Length,
                    Progress = GetFileProgress(f)
                }).ToArray()
            };
            
            string json = System.Text.Json.JsonSerializer.Serialize(statusInfo, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
            
            context.Response.ContentType = "application/json";
            context.Response.StatusCode = 200;
            
            byte[] buffer = Encoding.UTF8.GetBytes(json);
            context.Response.ContentLength64 = buffer.Length;
            await context.Response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
            context.Response.Close();
        }
        
        static async Task SendIndexPageAsync(HttpListenerContext context)
        {
            StringBuilder html = new StringBuilder();
            html.AppendLine("<!DOCTYPE html>");
            html.AppendLine("<html>");
            html.AppendLine("<head>");
            html.AppendLine("  <title>MonoTorrent HTTP Streaming</title>");
            html.AppendLine("  <style>");
            html.AppendLine("    body { font-family: Arial, sans-serif; margin: 20px; }");
            html.AppendLine("    h1 { color: #333; }");
            html.AppendLine("    .file { margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }");
            html.AppendLine("    .progress { height: 20px; background-color: #f0f0f0; border-radius: 5px; margin-top: 5px; }");
            html.AppendLine("    .progress-bar { height: 100%; background-color: #4CAF50; border-radius: 5px; }");
            html.AppendLine("    .player { margin-top: 10px; }");
            html.AppendLine("  </style>");
            html.AppendLine("  <script>");
            html.AppendLine("    function updateStatus() {");
            html.AppendLine("      fetch('/status')");
            html.AppendLine("        .then(response => response.json())");
            html.AppendLine("        .then(data => {");
            html.AppendLine("          document.getElementById('torrent-name').textContent = data.TorrentName;");
            html.AppendLine("          document.getElementById('torrent-state').textContent = data.State;");
            html.AppendLine("          document.getElementById('torrent-progress').textContent = data.Progress.toFixed(2) + '%';");
            html.AppendLine("          document.getElementById('download-rate').textContent = (data.DownloadRate / 1024).toFixed(2) + ' KB/s';");
            html.AppendLine("          document.getElementById('upload-rate').textContent = (data.UploadRate / 1024).toFixed(2) + ' KB/s';");
            html.AppendLine("          document.getElementById('connected-peers').textContent = data.ConnectedPeers;");
            html.AppendLine("          ");
            html.AppendLine("          // Update file progress");
            html.AppendLine("          data.Files.forEach((file, index) => {");
            html.AppendLine("            const progressBar = document.getElementById(`progress-${index}`);");
            html.AppendLine("            if (progressBar) {");
            html.AppendLine("              progressBar.style.width = file.Progress.toFixed(2) + '%';");
            html.AppendLine("            }");
            html.AppendLine("          });");
            html.AppendLine("        });");
            html.AppendLine("      setTimeout(updateStatus, 1000);");
            html.AppendLine("    }");
            html.AppendLine("    window.onload = updateStatus;");
            html.AppendLine("  </script>");
            html.AppendLine("</head>");
            html.AppendLine("<body>");
            html.AppendLine("  <h1>MonoTorrent HTTP Streaming</h1>");
            html.AppendLine("  <div>");
            html.AppendLine("    <strong>Torrent Name:</strong> <span id=\"torrent-name\"></span><br>");
            html.AppendLine("    <strong>State:</strong> <span id=\"torrent-state\"></span><br>");
            html.AppendLine("    <strong>Progress:</strong> <span id=\"torrent-progress\"></span><br>");
            html.AppendLine("    <strong>Download Rate:</strong> <span id=\"download-rate\"></span><br>");
            html.AppendLine("    <strong>Upload Rate:</strong> <span id=\"upload-rate\"></span><br>");
            html.AppendLine("    <strong>Connected Peers:</strong> <span id=\"connected-peers\"></span>");
            html.AppendLine("  </div>");
            html.AppendLine("  <h2>Available Files</h2>");
            
            for (int i = 0; i < streamingManager.Files.Count; i++)
            {
                var file = streamingManager.Files[i];
                string extension = Path.GetExtension(file.Path).ToLowerInvariant();
                bool isMediaFile = IsMediaFile(extension);
                string streamUrl = $"/stream/{i}";
                
                html.AppendLine($"  <div class=\"file\">");
                html.AppendLine($"    <strong>{file.Path}</strong> ({FormatSize(file.Length)})<br>");
                html.AppendLine($"    <div class=\"progress\">");
                html.AppendLine($"      <div id=\"progress-{i}\" class=\"progress-bar\" style=\"width: {GetFileProgress(file)}%\"></div>");
                html.AppendLine($"    </div>");
                
                if (isMediaFile)
                {
                    if (IsVideoFile(extension))
                    {
                        html.AppendLine($"    <div class=\"player\">");
                        html.AppendLine($"      <video controls width=\"640\" height=\"360\">");
                        html.AppendLine($"        <source src=\"{streamUrl}\" type=\"{GetMimeType(extension)}\">");
                        html.AppendLine($"        Your browser does not support the video tag.");
                        html.AppendLine($"      </video>");
                        html.AppendLine($"    </div>");
                    }
                    else if (IsAudioFile(extension))
                    {
                        html.AppendLine($"    <div class=\"player\">");
                        html.AppendLine($"      <audio controls>");
                        html.AppendLine($"        <source src=\"{streamUrl}\" type=\"{GetMimeType(extension)}\">");
                        html.AppendLine($"        Your browser does not support the audio tag.");
                        html.AppendLine($"      </audio>");
                        html.AppendLine($"    </div>");
                    }
                    
                    html.AppendLine($"    <div>");
                    html.AppendLine($"      <a href=\"{streamUrl}\" target=\"_blank\">Download/Open in external player</a>");
                    html.AppendLine($"    </div>");
                }
                
                html.AppendLine($"  </div>");
            }
            
            html.AppendLine("</body>");
            html.AppendLine("</html>");
            
            context.Response.ContentType = "text/html";
            context.Response.StatusCode = 200;
            
            byte[] buffer = Encoding.UTF8.GetBytes(html.ToString());
            context.Response.ContentLength64 = buffer.Length;
            await context.Response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
            context.Response.Close();
        }
        
        static void Send404(HttpListenerContext context)
        {
            context.Response.StatusCode = 404;
            context.Response.StatusDescription = "Not Found";
            context.Response.Close();
        }
        
        static void Send500(HttpListenerContext context, string message)
        {
            context.Response.StatusCode = 500;
            context.Response.StatusDescription = "Internal Server Error";
            
            byte[] buffer = Encoding.UTF8.GetBytes(message);
            context.Response.ContentLength64 = buffer.Length;
            context.Response.OutputStream.Write(buffer, 0, buffer.Length);
            
            context.Response.Close();
        }
        
        static string GetMimeType(string extension)
        {
            switch (extension.ToLowerInvariant())
            {
                case ".mp4": return "video/mp4";
                case ".mkv": return "video/x-matroska";
                case ".avi": return "video/x-msvideo";
                case ".mov": return "video/quicktime";
                case ".wmv": return "video/x-ms-wmv";
                case ".flv": return "video/x-flv";
                case ".webm": return "video/webm";
                
                case ".mp3": return "audio/mpeg";
                case ".wav": return "audio/wav";
                case ".ogg": return "audio/ogg";
                case ".flac": return "audio/flac";
                case ".aac": return "audio/aac";
                
                case ".srt": return "application/x-subrip";
                case ".vtt": return "text/vtt";
                
                default: return "application/octet-stream";
            }
        }
        
        static bool IsMediaFile(string extension)
        {
            return IsVideoFile(extension) || IsAudioFile(extension);
        }
        
        static bool IsVideoFile(string extension)
        {
            string[] videoExtensions = { ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm" };
            return videoExtensions.Contains(extension.ToLowerInvariant());
        }
        
        static bool IsAudioFile(string extension)
        {
            string[] audioExtensions = { ".mp3", ".wav", ".ogg", ".flac", ".aac" };
            return audioExtensions.Contains(extension.ToLowerInvariant());
        }
        
        static double GetFileProgress(ITorrentFileInfo file)
        {
            // Calculate file progress based on downloaded pieces
            int piecesCompleted = 0;
            int totalPieces = file.EndPieceIndex - file.StartPieceIndex + 1;
            
            for (int i = file.StartPieceIndex; i <= file.EndPieceIndex; i++)
            {
                if (streamingManager.Bitfield[i])
                {
                    piecesCompleted++;
                }
            }
            
            return (double)piecesCompleted / totalPieces * 100;
        }
        
        static async Task MonitorTorrentAsync(TorrentManager manager)
        {
            while (!waitHandle.WaitOne(1000))
            {
                Console.Clear();
                Console.WriteLine($"Torrent: {manager.Torrent?.Name ?? "Unknown"}");
                Console.WriteLine($"State: {manager.State}");
                Console.WriteLine($"Progress: {manager.Progress:F2}%");
                Console.WriteLine($"Download Speed: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
                Console.WriteLine($"Upload Speed: {manager.Monitor.UploadRate / 1024:F2} KB/s");
                Console.WriteLine($"Connected Peers: {manager.Peers.ConnectedPeers.Count}");
                Console.WriteLine();
                Console.WriteLine("HTTP Streaming Server running at http://localhost:8080/");
                Console.WriteLine("Press Ctrl+C to exit");
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
}
```

## How Streaming Works in MonoTorrent

MonoTorrent's streaming capabilities are built around the following concepts:

### StreamProvider

The `StreamProvider` class is the main entry point for streaming functionality. It can be accessed through a streaming-enabled `TorrentManager` instance's `StreamProvider` property.

### Creating Streaming TorrentManagers

To enable streaming for a torrent, use the streaming extension methods for `ClientEngine`:

```csharp
// From a torrent file
TorrentManager manager = await engine.AddStreamingAsync(torrentPath, downloadPath);

// From a magnet link
TorrentManager manager = await engine.AddStreamingAsync(magnetLink, downloadPath);
```

### Creating Streams

Once you have a streaming-enabled TorrentManager, you can create streams for individual files:

```csharp
// Create a stream for a specific file
Stream stream = await manager.StreamProvider.CreateStreamAsync(fileInfo);
```

### Piece Selection Strategy

When streaming, MonoTorrent uses a specialized piece picking strategy that:

1. Prioritizes pieces near the current read position
2. Downloads pieces sequentially from the current position
3. Maintains a buffer of pieces ahead of the current position
4. Dynamically adjusts priorities when seeking to a new position

This ensures smooth playback while still participating in the BitTorrent swarm.

## Best Practices for Streaming

1. **Buffer Management**: Ensure sufficient buffer ahead of the playback position
2. **Bandwidth Control**: Allocate enough bandwidth for streaming to maintain playback
3. **File Selection**: Only stream one file at a time for best performance
4. **Error Handling**: Be prepared for temporary unavailability of pieces
5. **Piece Size Considerations**: Larger piece sizes can affect seeking responsiveness
6. **Cache Management**: Implement proper caching for better performance

## Limitations

1. **Not All Files Are Suitable**: Very large files or files with small pieces may have issues
2. **Network Conditions**: Poor swarm health can affect streaming quality
3. **Seeking Performance**: Seeking to unwatched portions requires downloading new pieces
4. **Memory Usage**: Streaming can require more memory than regular downloading

## Using with Media Players

To use MonoTorrent streaming with external media players:

1. **HTTP Streaming Server**: Implement an HTTP server (as shown in the advanced example)
2. **DLNA/UPnP**: Expose the stream via DLNA for smart TVs and media players
3. **File Proxying**: Create a virtual file that forwards to the torrent stream
4. **Socket Communication**: Use inter-process communication for local media players

## Conclusion

MonoTorrent's streaming capabilities make it possible to start consuming content before it's fully downloaded. This can significantly improve the user experience for media applications like video players, while still maintaining the advantages of BitTorrent's distributed download model.