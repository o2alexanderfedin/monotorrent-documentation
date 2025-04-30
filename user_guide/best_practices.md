# Best Practices

This document outlines recommended patterns and practices when working with MonoTorrent.

## Contents

- [Memory Management](#memory-management)
- [Connection Management](#connection-management)
- [Disk I/O](#disk-io)
- [Resource Cleanup](#resource-cleanup)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)
- [Platform-Specific Considerations](#platform-specific-considerations)

## Memory Management

To ensure optimal memory usage with MonoTorrent:

1. **Limit concurrent active torrents**: Keep the number of simultaneously active torrents reasonable for your hardware.
   
   ```csharp
   // If you have many torrents, consider implementing a queue system
   int maxActiveTorrents = 5;
   var activeTorrents = new List<TorrentManager>();
   
   // Activate only a subset of torrents at a time
   foreach (var torrent in allTorrents.Take(maxActiveTorrents))
   {
       await torrent.StartAsync();
       activeTorrents.Add(torrent);
   }
   ```

2. **Use memory-efficient storage for small files**: For small files, consider using `MemoryStorage` rather than disk storage.

   ```csharp
   // For small files, use memory storage
   if (torrent.Size < 10 * 1024 * 1024) // Less than 10MB
   {
       torrentSettings.CreateCustomStorage = (torrent) => new MemoryStorage();
   }
   ```

3. **Monitor memory usage**: Implement memory monitoring and adjust settings based on available resources.

## Connection Management

Properly managing connections can significantly improve performance:

1. **Adjust connection limits based on available bandwidth**:

   ```csharp
   // For high-bandwidth connections
   engineSettings.MaximumConnections = 150;
   engineSettings.MaximumHalfOpenConnections = 15;
   
   // For lower-bandwidth connections
   engineSettings.MaximumConnections = 50;
   engineSettings.MaximumHalfOpenConnections = 5;
   ```

2. **Use encryption appropriately**:

   ```csharp
   // Balance compatibility and privacy
   engineSettings.AllowedEncryption = EncryptionTypes.RC4Full | EncryptionTypes.PlainText;
   
   // For maximum compatibility
   engineSettings.AllowedEncryption = EncryptionTypes.All;
   
   // For maximum privacy
   engineSettings.AllowedEncryption = EncryptionTypes.RC4Full;
   ```

3. **Enable DHT, PEX, and Local Peer Discovery** for better peer finding:

   ```csharp
   // Enable all peer discovery mechanisms
   engineSettings.DhtEndPoint = new IPEndPoint(IPAddress.Any, 55123);
   engineSettings.LocalPeerEndPoint = new IPEndPoint(IPAddress.Any, 55124);
   ```

## Disk I/O

Efficient disk I/O is critical for torrent performance:

1. **Adjust cache settings based on available memory**:

   ```csharp
   // For systems with ample memory
   engineSettings.MaximumOpenFiles = 40;
   
   // For more constrained systems
   engineSettings.MaximumOpenFiles = 10;
   ```

2. **Use SSD for high-performance scenarios** when possible.

3. **Consider storage location carefully**:
   - Prefer local disks over network storage
   - Ensure sufficient free space (minimum 2x the size of your largest torrent)

## Resource Cleanup

Properly clean up resources to avoid leaks:

1. **Always dispose of the engine when done**:

   ```csharp
   // Using pattern
   using (var engine = new ClientEngine(engineSettings))
   {
       // Use the engine
   }
   
   // Or with async
   await engine.DisposeAsync();
   ```

2. **Unregister event handlers** when they're no longer needed:

   ```csharp
   torrentManager.TorrentStateChanged -= HandleTorrentStateChanged;
   torrentManager.PieceHashed -= HandlePieceHashed;
   ```

## Error Handling

Robust error handling is essential for long-running torrent operations:

1. **Handle common exceptions gracefully**:

   ```csharp
   try
   {
       await torrentManager.StartAsync();
   }
   catch (InvalidOperationException)
   {
       // Handle when torrent is already started
   }
   catch (Exception ex)
   {
       // Log and handle unexpected errors
       logger.LogError(ex, "Failed to start torrent");
   }
   ```

2. **Implement retry logic for transient failures**:

   ```csharp
   int maxRetries = 3;
   int attempts = 0;
   
   while (attempts < maxRetries)
   {
       try
       {
           await engine.AddAsync(torrent, downloadPath);
           break;
       }
       catch (Exception ex) when (IsTransient(ex))
       {
           attempts++;
           if (attempts >= maxRetries)
               throw;
           
           await Task.Delay(1000 * attempts); // Exponential backoff
       }
   }
   ```

## Performance Optimization

1. **Use appropriate piece selection strategies** for your use case:

   ```csharp
   // For general downloading
   torrentSettings.PieceRequester = new StandardPicker();
   
   // For streaming use cases
   torrentSettings.PieceRequester = new StreamingPicker();
   
   // For fastest initial download with availability reporting
   torrentSettings.PieceRequester = new RarestFirstPicker();
   ```

2. **Adjust update intervals** based on UI needs:

   ```csharp
   // For data that needs frequent updates (UI display)
   engineSettings.UpdateInterval = TimeSpan.FromMilliseconds(500);
   
   // For background operations with less frequent updates
   engineSettings.UpdateInterval = TimeSpan.FromSeconds(2);
   ```

3. **Use FastResume data** to avoid hash checking on restart:

   ```csharp
   // Save when torrent completes or on shutdown
   await engine.SaveFastResumeAsync();
   ```

## Platform-Specific Considerations

1. **Mobile Platforms**:
   - Implement more aggressive connection limits
   - Check for WiFi vs. cellular connections
   - Pause downloads when on cellular if appropriate
   - Monitor battery status

2. **Desktop Applications**:
   - Consider running as a background service
   - Implement power management awareness

3. **Server Deployments**:
   - Focus on throughput and stability
   - More aggressive connection settings
   - Monitor system resource usage

For more detailed information on specific use cases, check the [Examples](../examples/README.md) section.