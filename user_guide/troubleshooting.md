# Troubleshooting

This document provides solutions for common issues you might encounter when using MonoTorrent.

## Contents

- [Connection Issues](#connection-issues)
- [Download Performance](#download-performance)
- [Upload Issues](#upload-issues)
- [Errors and Exceptions](#errors-and-exceptions)
- [DHT Problems](#dht-problems)
- [File Corruption](#file-corruption)
- [Resource Usage](#resource-usage)
- [Metadata Download Issues](#metadata-download-issues)

## Connection Issues

### Cannot Connect to Peers

If your client cannot connect to peers:

1. **Check network connectivity**:
   ```csharp
   // Use this to check basic network connectivity
   if (!await IsNetworkAvailable())
   {
       Console.WriteLine("Network is unavailable");
       return;
   }
   ```

2. **Verify port forwarding**:
   ```csharp
   // Port forwarding might be needed if behind NAT
   var portForwarder = new PortForwarding.Upnp();
   var mapping = await portForwarder.CreateAsync(Protocol.Tcp, 
                                               engineSettings.ListenPort, 
                                               engineSettings.ListenPort);
   if (mapping == null)
   {
       Console.WriteLine("Port forwarding failed - may need manual router configuration");
   }
   ```

3. **Try alternative encryption settings**:
   ```csharp
   // Try allowing all encryption types if having connection issues
   engineSettings.AllowedEncryption = EncryptionTypes.All;
   ```

### Low Peer Count

If you're not finding enough peers:

1. **Enable all peer discovery mechanisms**:
   ```csharp
   // Ensure DHT is enabled
   engineSettings.DhtEndPoint = new IPEndPoint(IPAddress.Any, 55123);
   
   // Enable Local Peer Discovery
   engineSettings.LocalPeerEndPoint = new IPEndPoint(IPAddress.Any, 55124);
   
   // Use PEX (enabled by default)
   ```

2. **Check tracker status**:
   ```csharp
   // Monitor tracker issues
   torrentManager.TrackerManager.AnnounceComplete += (sender, e) => {
       if (e.Successful)
           Console.WriteLine($"Tracker update succeeded: {e.Peers.Count} peers");
       else
           Console.WriteLine($"Tracker update failed: {e.Failure}");
   };
   ```

## Download Performance

### Slow Downloads

1. **Check piece picker strategy**:
   ```csharp
   // For general downloading
   torrentSettings.PieceRequester = new StandardPicker();
   
   // For rarest-first strategy (better in swarms)
   torrentSettings.PieceRequester = new RarestFirstPicker();
   ```

2. **Optimize connection settings**:
   ```csharp
   // Increase maximum connections for better parallelism
   engineSettings.MaximumConnections = 150;
   
   // Adjust half-open connection limit
   engineSettings.MaximumHalfOpenConnections = 15;
   ```

3. **Check for rate limiting**:
   ```csharp
   // Ensure no unintended rate limits are applied
   if (engineSettings.MaximumDownloadRate < 1_000_000)
   {
       Console.WriteLine("Download rate is limited to less than 1 MB/s");
   }
   ```

### Stalled Downloads

If downloads stall:

1. **Check torrent health**:
   ```csharp
   // Monitor availability
   bool hasCompleteSource = torrentManager.Peers.Any(p => p.BitField.AllTrue);
   if (!hasCompleteSource)
   {
       Console.WriteLine("No peer has all pieces - torrent may be unhealthy");
   }
   ```

2. **Restart problematic torrents**:
   ```csharp
   await torrentManager.StopAsync();
   await Task.Delay(1000);
   await torrentManager.StartAsync();
   ```

## Upload Issues

### No Uploading

If your client isn't uploading:

1. **Check upload rate settings**:
   ```csharp
   // Ensure upload isn't disabled
   if (engineSettings.MaximumUploadRate == 0)
   {
       Console.WriteLine("Upload is disabled");
       engineSettings.MaximumUploadRate = -1; // Unlimited
   }
   ```

2. **Verify port forwarding**:
   ```csharp
   // Check if listening port is accessible
   bool portForwarded = await IsPortAccessible(engineSettings.ListenPort);
   if (!portForwarded)
   {
       Console.WriteLine("Port not accessible - incoming connections will fail");
   }
   ```

## Errors and Exceptions

### Common Exceptions

1. **Invalid Operation Exceptions**:
   ```csharp
   try
   {
       await torrentManager.StartAsync();
   }
   catch (InvalidOperationException ex) when (ex.Message.Contains("already started"))
   {
       // Handle torrent already started
       Console.WriteLine("Torrent is already running");
   }
   ```

2. **Disk I/O Errors**:
   ```csharp
   try
   {
       await torrentManager.MoveFilesAsync("/new/location");
   }
   catch (IOException ex)
   {
       Console.WriteLine($"Disk error: {ex.Message}");
       // Check disk space, permissions, etc.
   }
   ```

### Error Mode

If a torrent enters Error mode:

```csharp
torrentManager.TorrentStateChanged += (sender, e) => {
    if (e.NewState == TorrentState.Error)
    {
        var manager = (TorrentManager)sender;
        Console.WriteLine($"Torrent error: {manager.Error.Exception.Message}");
        
        // Attempt recovery after delay
        Task.Delay(TimeSpan.FromMinutes(1))
            .ContinueWith(t => manager.StartAsync());
    }
};
```

## DHT Problems

### DHT Not Working

If DHT peer discovery isn't functioning:

1. **Check DHT state**:
   ```csharp
   if (engine.DhtEngine.State != DhtState.Ready)
   {
       Console.WriteLine($"DHT is not ready: {engine.DhtEngine.State}");
   }
   ```

2. **Check node count**:
   ```csharp
   int nodeCount = engine.DhtEngine.RoutingTable.CountNodes();
   if (nodeCount < 10)
   {
       Console.WriteLine("DHT has very few nodes - may need time to populate");
   }
   ```

3. **Reinitialize DHT if needed**:
   ```csharp
   await engine.StopAllAsync();
   await engine.DhtEngine.StopAsync();
   await engine.DhtEngine.StartAsync();
   await engine.StartAllAsync();
   ```

## File Corruption

### Corrupted Downloads

If you encounter file corruption:

1. **Force rehash**:
   ```csharp
   await torrentManager.HashCheckAsync(true);
   ```

2. **Check for disk issues**:
   ```csharp
   // Verify disk space
   string downloadPath = torrentManager.SavePath;
   long availableSpace = new DriveInfo(Path.GetPathRoot(downloadPath)).AvailableFreeSpace;
   
   if (availableSpace < torrentManager.Torrent.Size)
   {
       Console.WriteLine("Insufficient disk space - may cause corruption");
   }
   ```

## Resource Usage

### High CPU Usage

If MonoTorrent is consuming too much CPU:

1. **Reduce update frequency**:
   ```csharp
   // Increase the time between internal updates
   engineSettings.UpdateInterval = TimeSpan.FromSeconds(2);
   ```

2. **Limit active torrents**:
   ```csharp
   // Implement a queue system for many torrents
   int maxActive = Environment.ProcessorCount;
   ```

### High Memory Usage

To address high memory consumption:

1. **Limit open files**:
   ```csharp
   engineSettings.MaximumOpenFiles = 10;
   ```

2. **Adjust buffer allocation**:
   ```csharp
   // Customize buffer management (if implemented)
   CustomBufferPool.MaxBufferSize = 1024 * 1024; // 1 MB
   ```

## Metadata Download Issues

### Magnet Links Not Downloading Metadata

If you're having trouble downloading metadata from magnet links:

1. **Check for DHT**:
   ```csharp
   if (engine.DhtEngine == null || engine.DhtEngine.State != DhtState.Ready)
   {
       Console.WriteLine("DHT not ready - metadata download may be slow or fail");
   }
   ```

2. **Add known trackers**:
   ```csharp
   // Add public trackers to help find peers
   var trackers = new[] {
       "udp://tracker.opentrackr.org:1337/announce",
       "udp://tracker.openbittorrent.com:6969/announce"
   };
   
   foreach (var tracker in trackers)
   {
       torrentManager.TrackerManager.Add(new Uri(tracker));
   }
   ```

3. **Monitor metadata progress**:
   ```csharp
   // Add logging for metadata progress
   if (torrentManager.State == TorrentState.Metadata)
   {
       Console.WriteLine("Downloading metadata...");
       // Implement timeout logic if needed
   }
   ```

For more complex issues, consider checking the [GitHub repository](https://github.com/alanmcgovern/monotorrent) for known issues or submitting a new one.