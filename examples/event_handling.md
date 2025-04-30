# Handling MonoTorrent Events

This example demonstrates how to effectively handle the various events provided by MonoTorrent to monitor and respond to torrent activity.

## Contents

- [Understanding MonoTorrent Events](#understanding-monotorrent-events)
- [Engine-Level Events](#engine-level-events)
- [TorrentManager Events](#torrentmanager-events)
- [TrackerManager Events](#trackermanager-events)
- [Error Handling](#error-handling)
- [Event-Based UI Updates](#event-based-ui-updates)
- [Complete Example](#complete-example)

## Understanding MonoTorrent Events

MonoTorrent provides a comprehensive event system that lets you monitor and respond to various aspects of the torrenting process. Events are raised at different levels:

1. **ClientEngine events**: Global events that affect all torrents
2. **TorrentManager events**: Events specific to individual torrents
3. **TrackerManager events**: Events related to tracker communication
4. **PeerManager events**: Events related to peer interactions

By subscribing to these events, you can build responsive applications that react to changes in the torrenting process.

## Engine-Level Events

The `ClientEngine` class provides several important events:

```csharp
// Configure the engine
var engineSettings = new EngineSettings
{
    SavePath = "/path/to/downloads"
};
using var engine = new ClientEngine(engineSettings);

// Subscribe to engine-level events

// Fires when a new peer connects
engine.PeerConnected += (sender, e) => {
    Console.WriteLine($"Connected to peer: {e.Peer.ConnectionUri}");
    Console.WriteLine($"For torrent: {e.TorrentManager.Torrent?.Name ?? "Unknown"}");
    Console.WriteLine($"Client: {e.Peer.ClientApp}");
};

// Fires when a peer disconnects
engine.PeerDisconnected += (sender, e) => {
    Console.WriteLine($"Disconnected from peer: {e.Peer.ConnectionUri}");
    Console.WriteLine($"Reason: {e.Reason}");
};

// Fires when a connection to a peer fails
engine.ConnectionAttemptFailed += (sender, e) => {
    if (e.Reason != ConnectionFailureReason.NoError)
    {
        Console.WriteLine($"Connection failed: {e.Reason}");
    }
};

// Fires when a torrent state changes
engine.TorrentStateChanged += (sender, e) => {
    Console.WriteLine($"Torrent state changed from {e.OldState} to {e.NewState}");
    Console.WriteLine($"Torrent: {((TorrentManager)sender).Torrent?.Name ?? "Unknown"}");
    
    // Handle specific state transitions
    if (e.OldState == TorrentState.Downloading && e.NewState == TorrentState.Seeding)
    {
        Console.WriteLine("Download completed, now seeding");
    }
};
```

## TorrentManager Events

Each `TorrentManager` instance provides events specific to that torrent:

```csharp
// Load a torrent
var torrent = await Torrent.LoadAsync("example.torrent");
var manager = await engine.AddAsync(torrent, "/path/to/downloads");

// Subscribe to TorrentManager events

// Fires when a piece is successfully hashed
manager.PieceHashed += (sender, e) => {
    Console.WriteLine($"Piece {e.PieceIndex} was hashed. Success: {e.HashPassed}");
    if (!e.HashPassed)
    {
        Console.WriteLine("Hash check failed. The piece will be re-downloaded.");
    }
};

// Fires when torrent metadata is received (useful for magnet links)
manager.MetadataReceived += (sender, e) => {
    var torrentManager = (TorrentManager)sender;
    Console.WriteLine($"Received metadata for {torrentManager.Torrent.Name}");
    Console.WriteLine($"File count: {torrentManager.Torrent.Files.Count}");
};

// Fires when the torrent state changes
manager.TorrentStateChanged += (sender, e) => {
    Console.WriteLine($"State changed: {e.OldState} -> {e.NewState}");
    
    // Perform actions based on state change
    if (e.NewState == TorrentState.Seeding)
    {
        Console.WriteLine("Download complete!");
        // Maybe show a notification or update UI
    }
    else if (e.NewState == TorrentState.Error)
    {
        Console.WriteLine($"Error: {manager.Error.Exception.Message}");
    }
};
```

## TrackerManager Events

The `TrackerManager` provides events for monitoring tracker communication:

```csharp
// Access the TrackerManager for a torrent
var trackerManager = manager.TrackerManager;

// Fires when an announce to the tracker is about to start
trackerManager.AnnounceStarting += (sender, e) => {
    Console.WriteLine($"Starting announce to tracker: {e.Tracker.Uri}");
};

// Fires when an announce completes successfully
trackerManager.AnnounceComplete += (sender, e) => {
    if (e.Successful)
    {
        Console.WriteLine($"Announce successful. Peers: {e.Peers.Count}");
    }
    else
    {
        Console.WriteLine($"Announce failed: {e.Failure}");
    }
};

// Fires when an announce fails
trackerManager.AnnounceFailed += (sender, e) => {
    Console.WriteLine($"Announce failed: {e.Failure}");
};

// Fires when a scrape operation completes
trackerManager.ScrapeComplete += (sender, e) => {
    if (e.Successful)
    {
        Console.WriteLine($"Scrape successful. Seeders: {e.Complete}, Leechers: {e.Incomplete}");
    }
    else
    {
        Console.WriteLine($"Scrape failed: {e.Failure}");
    }
};
```

## Error Handling

Proper error handling with events is important for a robust application:

```csharp
// Set up error handling for key events
public void RegisterErrorHandlingEvents(ClientEngine engine, TorrentManager manager)
{
    // Safely subscribe to events with error handling
    manager.TorrentStateChanged += SafeEventHandler<TorrentStateChangedEventArgs>((sender, e) => {
        if (e.NewState == TorrentState.Error)
        {
            var torrentManager = (TorrentManager)sender;
            LogError($"Torrent error: {torrentManager.Error?.Exception?.Message}");
            
            // Attempt recovery
            Task.Run(async () => {
                try
                {
                    await Task.Delay(TimeSpan.FromMinutes(1));
                    await torrentManager.StartAsync();
                }
                catch (Exception ex)
                {
                    LogError($"Failed to restart torrent: {ex.Message}");
                }
            });
        }
    });
    
    // Handle tracker failures
    manager.TrackerManager.AnnounceFailed += SafeEventHandler<AnnounceFailedEventArgs>((sender, e) => {
        LogWarning($"Tracker announce failed: {e.Failure}");
    });
    
    // Handle peer disconnections that might indicate problems
    engine.PeerDisconnected += SafeEventHandler<PeerDisconnectedEventArgs>((sender, e) => {
        if (e.Reason == ConnectionFailureReason.IOError || 
            e.Reason == ConnectionFailureReason.ConnectionCancelled)
        {
            LogWarning($"Peer disconnected abnormally: {e.Reason}");
        }
    });
}

// Helper method to wrap event handlers with error handling
private EventHandler<T> SafeEventHandler<T>(EventHandler<T> handler) where T : EventArgs
{
    return (sender, args) => {
        try
        {
            handler(sender, args);
        }
        catch (Exception ex)
        {
            LogError($"Error in event handler: {ex.Message}");
        }
    };
}

private void LogError(string message)
{
    Console.WriteLine($"ERROR: {message}");
    // In a real app, log to file, database, etc.
}

private void LogWarning(string message)
{
    Console.WriteLine($"WARNING: {message}");
    // In a real app, log to file, database, etc.
}
```

## Event-Based UI Updates

Here's an example of using events to update a user interface:

```csharp
// Set up UI update events
public void SetupUIUpdateEvents(TorrentManager manager)
{
    // Update UI when state changes
    manager.TorrentStateChanged += (sender, e) => {
        // Use dispatcher or invoke if in a UI framework
        UpdateUI(() => {
            statusLabel.Text = e.NewState.ToString();
            
            // Enable/disable buttons based on state
            startButton.Enabled = e.NewState == TorrentState.Stopped || 
                                 e.NewState == TorrentState.Paused;
            pauseButton.Enabled = e.NewState == TorrentState.Downloading || 
                                 e.NewState == TorrentState.Seeding;
            stopButton.Enabled = e.NewState != TorrentState.Stopped;
        });
    };
    
    // Update progress display
    manager.PieceHashed += (sender, e) => {
        if (e.HashPassed && updateCounter++ % 5 == 0) // Update every 5 pieces
        {
            UpdateUI(() => {
                progressBar.Value = (int)manager.Progress;
                progressLabel.Text = $"{manager.Progress:0.00}%";
                downloadSpeedLabel.Text = $"{FormatSize(manager.Monitor.DownloadRate)}/s";
                uploadSpeedLabel.Text = $"{FormatSize(manager.Monitor.UploadRate)}/s";
                etaLabel.Text = CalculateETA(manager);
            });
        }
    };
    
    // Update peer count
    System.Timers.Timer peerUpdateTimer = new System.Timers.Timer(1000);
    peerUpdateTimer.Elapsed += (sender, e) => {
        UpdateUI(() => {
            peersLabel.Text = $"{manager.Peers.ConnectedPeers} peers connected";
            seedsLabel.Text = $"{manager.Peers.Seeds} seeds";
            leechesLabel.Text = $"{manager.Peers.Leechs} leechers";
        });
    };
    peerUpdateTimer.Start();
    
    // Update trackers status
    manager.TrackerManager.AnnounceComplete += (sender, e) => {
        UpdateUI(() => {
            string status = e.Successful ? "OK" : $"Failed: {e.Failure}";
            AddToTrackersList($"{e.Tracker.Uri}: {status}");
        });
    };
}

// Helper method for UI thread synchronization (implementation depends on UI framework)
private void UpdateUI(Action action)
{
    // For WinForms
    if (statusLabel.InvokeRequired)
    {
        statusLabel.Invoke(action);
    }
    else
    {
        action();
    }
    
    // For WPF, you'd use the Dispatcher
    // Dispatcher.Invoke(action);
}

private string CalculateETA(TorrentManager manager)
{
    if (manager.Monitor.DownloadRate <= 0)
        return "∞";
        
    var remainingBytes = manager.Torrent.Size - manager.Monitor.DataBytesReceived;
    var seconds = remainingBytes / manager.Monitor.DownloadRate;
    
    TimeSpan time = TimeSpan.FromSeconds(seconds);
    if (time.TotalDays > 1)
        return $"{time.TotalDays:0.0} days";
    else if (time.TotalHours > 1)
        return $"{time.TotalHours:0.0} hours";
    else if (time.TotalMinutes > 1)
        return $"{time.TotalMinutes:0.0} min";
    else
        return $"{time.TotalSeconds:0.0} sec";
}
```

## Complete Example

Here's a complete console application demonstrating event handling:

```csharp
public class EventHandlingExample
{
    private static object ConsoleLock = new object();
    
    public static async Task RunAsync()
    {
        // Set up the engine
        var engineSettings = new EngineSettings
        {
            SavePath = "/path/to/downloads",
            ReportedAddress = new System.Net.IPAddress(new byte[] { 127, 0, 0, 1 })
        };
        
        using var engine = new ClientEngine(engineSettings);
        
        // Register engine events
        RegisterEngineEvents(engine);
        
        // Ask user for a torrent file
        Console.WriteLine("Enter path to .torrent file or a magnet link:");
        string input = Console.ReadLine().Trim();
        
        TorrentManager manager = null;
        
        try
        {
            // Add the torrent to the engine
            if (input.StartsWith("magnet:"))
            {
                var magnetLink = new MagnetLink(input);
                manager = await engine.AddAsync(magnetLink, "/path/to/downloads");
                LogInfo($"Added magnet link for '{magnetLink.Name ?? "Unnamed torrent"}'");
            }
            else
            {
                var torrent = await Torrent.LoadAsync(input);
                manager = await engine.AddAsync(torrent, "/path/to/downloads");
                LogInfo($"Added torrent: {torrent.Name}");
            }
            
            // Register torrent-specific events
            RegisterTorrentEvents(manager);
            
            // Start the torrent
            await manager.StartAsync();
            LogInfo("Torrent started");
            
            // Main loop to keep application running and show periodic updates
            bool running = true;
            Console.WriteLine("\nCommands: (p)ause, (r)esume, (s)top, (q)uit");
            
            while (running)
            {
                DisplayTorrentStats(manager);
                
                // Check for user input
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true);
                    switch (key.KeyChar)
                    {
                        case 'p':
                            await manager.PauseAsync();
                            LogInfo("Torrent paused");
                            break;
                            
                        case 'r':
                            await manager.StartAsync();
                            LogInfo("Torrent resumed");
                            break;
                            
                        case 's':
                            await manager.StopAsync();
                            LogInfo("Torrent stopped");
                            break;
                            
                        case 'q':
                            running = false;
                            break;
                    }
                }
                
                await Task.Delay(1000);
            }
            
            // Clean up
            await engine.StopAllAsync();
            LogInfo("All torrents stopped");
        }
        catch (Exception ex)
        {
            LogError($"Error: {ex.Message}");
        }
    }
    
    private static void RegisterEngineEvents(ClientEngine engine)
    {
        // Listen for peer connections
        engine.PeerConnected += (sender, e) => {
            LogPeer($"Connected to peer: {e.Peer.ConnectionUri}");
        };
        
        // Listen for peer disconnections
        engine.PeerDisconnected += (sender, e) => {
            LogPeer($"Disconnected from peer: {e.Peer.ConnectionUri}, Reason: {e.Reason}");
        };
        
        // Listen for connection failures
        engine.ConnectionAttemptFailed += (sender, e) => {
            if (e.Reason != ConnectionFailureReason.NoError)
            {
                LogWarning($"Connection attempt failed: {e.Reason}");
            }
        };
    }
    
    private static void RegisterTorrentEvents(TorrentManager manager)
    {
        // Track torrent state changes
        manager.TorrentStateChanged += (sender, e) => {
            LogEvent($"State changed: {e.OldState} -> {e.NewState}");
            
            if (e.NewState == TorrentState.Seeding && e.OldState == TorrentState.Downloading)
            {
                LogInfo("Download completed successfully!");
            }
            else if (e.NewState == TorrentState.Error)
            {
                LogError($"Error: {manager.Error?.Exception?.Message}");
            }
        };
        
        // Track piece hash results
        manager.PieceHashed += (sender, e) => {
            if (!e.HashPassed)
            {
                LogWarning($"Piece {e.PieceIndex} failed hash check. It will be redownloaded.");
            }
        };
        
        // Track metadata download for magnet links
        manager.MetadataReceived += (sender, e) => {
            LogInfo($"Metadata downloaded for: {manager.Torrent.Name}");
            LogInfo($"Files in torrent ({manager.Torrent.Files.Count}):");
            
            foreach (var file in manager.Torrent.Files.OrderByDescending(f => f.Length).Take(5))
            {
                LogInfo($"- {file.Path} ({FormatSize(file.Length)})");
            }
            
            if (manager.Torrent.Files.Count > 5)
            {
                LogInfo($"... and {manager.Torrent.Files.Count - 5} more files");
            }
        };
        
        // Register tracker events
        RegisterTrackerEvents(manager.TrackerManager);
    }
    
    private static void RegisterTrackerEvents(TrackerManager trackerManager)
    {
        trackerManager.AnnounceStarting += (sender, e) => {
            LogTracker($"Announcing to: {e.Tracker.Uri}");
        };
        
        trackerManager.AnnounceComplete += (sender, e) => {
            if (e.Successful)
            {
                LogTracker($"Announce successful. Peers: {e.Peers.Count}");
            }
            else
            {
                LogTracker($"Announce failed: {e.Failure}");
            }
        };
        
        trackerManager.ScrapeComplete += (sender, e) => {
            if (e.Successful)
            {
                LogTracker($"Scrape successful. Complete: {e.Complete}, Incomplete: {e.Incomplete}, Downloaded: {e.Downloaded}");
            }
        };
    }
    
    private static void DisplayTorrentStats(TorrentManager manager)
    {
        lock (ConsoleLock)
        {
            // Save cursor position
            int left = Console.CursorLeft;
            int top = Console.CursorTop;
            
            // Clear space for stats
            Console.SetCursorPosition(0, Console.WindowHeight - 5);
            for (int i = 0; i < 5; i++)
            {
                Console.Write(new string(' ', Console.WindowWidth - 1));
                Console.CursorTop++;
                Console.CursorLeft = 0;
            }
            
            // Print stats
            Console.SetCursorPosition(0, Console.WindowHeight - 5);
            Console.WriteLine($"State: {manager.State} | Progress: {manager.Progress:0.00}%");
            Console.WriteLine($"Down: {FormatSize(manager.Monitor.DownloadRate)}/s | Up: {FormatSize(manager.Monitor.UploadRate)}/s");
            Console.WriteLine($"Peers: {manager.Peers.ConnectedPeers} | Seeds: {manager.Peers.Seeds} | Leeches: {manager.Peers.Leechs}");
            Console.WriteLine($"Downloaded: {FormatSize(manager.Monitor.DataBytesReceived)} | Uploaded: {FormatSize(manager.Monitor.DataBytesSent)}");
            
            // Restore cursor position
            Console.SetCursorPosition(left, top);
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
    
    // Logging methods with categories
    private static void LogInfo(string message)
    {
        WriteColoredLine(ConsoleColor.White, $"[INFO] {message}");
    }
    
    private static void LogWarning(string message)
    {
        WriteColoredLine(ConsoleColor.Yellow, $"[WARN] {message}");
    }
    
    private static void LogError(string message)
    {
        WriteColoredLine(ConsoleColor.Red, $"[ERROR] {message}");
    }
    
    private static void LogEvent(string message)
    {
        WriteColoredLine(ConsoleColor.Cyan, $"[EVENT] {message}");
    }
    
    private static void LogPeer(string message)
    {
        WriteColoredLine(ConsoleColor.Green, $"[PEER] {message}");
    }
    
    private static void LogTracker(string message)
    {
        WriteColoredLine(ConsoleColor.Magenta, $"[TRACKER] {message}");
    }
    
    private static void WriteColoredLine(ConsoleColor color, string message)
    {
        lock (ConsoleLock)
        {
            var oldColor = Console.ForegroundColor;
            Console.ForegroundColor = color;
            Console.WriteLine(message);
            Console.ForegroundColor = oldColor;
        }
    }
}
```

This example demonstrates a comprehensive approach to handling MonoTorrent events, including:

1. Engine-level events (peer connections, disconnections)
2. Torrent-specific events (state changes, piece hashing)
3. Tracker communication events
4. Error handling
5. User interface updates
6. Console-based stats display with color-coded logging

By properly handling these events, you can create robust torrent applications that provide meaningful feedback to users and respond appropriately to changing conditions.