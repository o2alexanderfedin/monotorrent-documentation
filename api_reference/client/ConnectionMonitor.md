# ConnectionMonitor

**Namespace**: `MonoTorrent.Client`

The `ConnectionMonitor` class tracks data transfer statistics for a peer connection.

## Overview

`ConnectionMonitor` provides detailed statistics about data transfer rates and total bytes transferred with a specific peer. It's used by the `PeerId` class to monitor upload and download activity, helping the choking algorithm and providing useful metrics for the user interface.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `DataBytesDownloaded` | `long` | Total data bytes downloaded from the peer |
| `DataBytesUploaded` | `long` | Total data bytes uploaded to the peer |
| `DownloadSpeed` | `int` | Current download speed in bytes/second |
| `ProtocolBytesDownloaded` | `long` | Total protocol bytes downloaded (messages, etc.) |
| `ProtocolBytesUploaded` | `long` | Total protocol bytes uploaded (messages, etc.) |
| `TotalBytesDownloaded` | `long` | Total bytes downloaded (data + protocol) |
| `TotalBytesUploaded` | `long` | Total bytes uploaded (data + protocol) |
| `UploadSpeed` | `int` | Current upload speed in bytes/second |

## Methods

### Constructors

```csharp
public ConnectionMonitor()
```
Creates a new connection monitor instance.

### Instance Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Reset()` | `void` | Resets all statistics to zero |
| `ToString()` | `string` | Returns a string representation of the statistics |
| `UploadRate(int bytesUploaded, bool transferType)` | `void` | Records bytes uploaded (true = data, false = protocol) |
| `DownloadRate(int bytesDownloaded, bool transferType)` | `void` | Records bytes downloaded (true = data, false = protocol) |
| `BytesTransferred(long bytesUploaded, long bytesDownloaded, bool transferType)` | `void` | Records bytes transferred in both directions |
| `Tick()` | `void` | Updates transfer rates (called approximately once per second) |

## Examples

### Monitoring Peer Performance

```csharp
// Get a connected peer from a torrent manager
TorrentManager manager = /* ... */;
PeerId peer = manager.Peers.ConnectedPeers.FirstOrDefault();

if (peer != null)
{
    ConnectionMonitor monitor = peer.Monitor;
    
    // Display current transfer rates
    Console.WriteLine($"Download speed: {monitor.DownloadSpeed / 1024.0:F2} KB/s");
    Console.WriteLine($"Upload speed: {monitor.UploadSpeed / 1024.0:F2} KB/s");
    
    // Display total data transferred
    Console.WriteLine($"Total downloaded: {monitor.DataBytesDownloaded / (1024.0 * 1024.0):F2} MB");
    Console.WriteLine($"Total uploaded: {monitor.DataBytesUploaded / (1024.0 * 1024.0):F2} MB");
    
    // Display ratio
    double ratio = monitor.DataBytesUploaded > 0 
        ? (double)monitor.DataBytesUploaded / monitor.DataBytesDownloaded 
        : 0;
    Console.WriteLine($"Share ratio: {ratio:F3}");
}
```

### Implementing a Connection Monitoring UI

```csharp
// Implementation of a UI component that updates peer statistics every second
public class PeerMonitoringUI
{
    private readonly ListView peerListView;
    private readonly TorrentManager manager;
    private readonly Timer updateTimer;
    
    public PeerMonitoringUI(ListView peerListView, TorrentManager manager)
    {
        this.peerListView = peerListView;
        this.manager = manager;
        
        // Update every second
        updateTimer = new Timer(1000);
        updateTimer.Elapsed += UpdatePeerStats;
        updateTimer.Start();
    }
    
    private void UpdatePeerStats(object sender, ElapsedEventArgs e)
    {
        // Get the list of connected peers
        var peers = manager.Peers.ConnectedPeers.ToList();
        
        // Update UI on UI thread
        peerListView.Invoke((MethodInvoker)(() =>
        {
            peerListView.Items.Clear();
            
            foreach (var peer in peers)
            {
                ConnectionMonitor monitor = peer.Monitor;
                
                // Create a list view item for this peer
                ListViewItem item = new ListViewItem(peer.Peer.Peer.ToString());
                
                // Add sub-items for the statistics
                item.SubItems.Add($"{monitor.DownloadSpeed / 1024.0:F1} KB/s");
                item.SubItems.Add($"{monitor.UploadSpeed / 1024.0:F1} KB/s");
                item.SubItems.Add($"{monitor.DataBytesDownloaded / (1024 * 1024.0):F2} MB");
                item.SubItems.Add($"{monitor.DataBytesUploaded / (1024 * 1024.0):F2} MB");
                
                // Add to the list view
                peerListView.Items.Add(item);
            }
        }));
    }
    
    public void Dispose()
    {
        updateTimer.Stop();
        updateTimer.Dispose();
    }
}
```

### Creating a Custom Choking Algorithm Based on Peer Performance

```csharp
// Example of a choking algorithm that favors fast peers and maintains reciprocation
public class SpeedBasedChokingAlgorithm
{
    private readonly TorrentManager manager;
    private readonly int maxUnchoked;
    private readonly Timer chokeTimer;
    private readonly Random random = new Random();
    
    public SpeedBasedChokingAlgorithm(TorrentManager manager, int maxUnchoked = 4)
    {
        this.manager = manager;
        this.maxUnchoked = maxUnchoked;
        
        // Run the choking algorithm every 30 seconds
        chokeTimer = new Timer(30000);
        chokeTimer.Elapsed += RunChokeUnchokeRound;
        chokeTimer.Start();
    }
    
    private void RunChokeUnchokeRound(object sender, ElapsedEventArgs e)
    {
        // Get all connected peers
        List<PeerId> connectedPeers = manager.Peers.ConnectedPeers
            .Where(p => p.IsInterested)  // Only consider peers interested in our data
            .ToList();
            
        if (connectedPeers.Count == 0)
            return;
            
        // Sort peers by download rate (reciprocation - reward peers that send us data)
        List<PeerId> sortedPeers = connectedPeers
            .OrderByDescending(p => p.Monitor.DownloadSpeed)
            .ToList();
            
        // Reserve one slot for optimistic unchoking
        int slotsToAssign = maxUnchoked - 1;
        
        // Unchoke the best downloaders
        for (int i = 0; i < sortedPeers.Count; i++)
        {
            PeerId peer = sortedPeers[i];
            
            if (i < slotsToAssign)
            {
                // Unchoke this peer (if currently choked)
                if (peer.AmChoking)
                {
                    peer.EnqueueMessage(new UnchokeMessage());
                    Console.WriteLine($"Unchoking peer {peer.Peer.Peer} (Download: {peer.Monitor.DownloadSpeed / 1024} KB/s)");
                }
            }
            else
            {
                // Choke this peer (if currently unchoked)
                if (!peer.AmChoking)
                {
                    peer.EnqueueMessage(new ChokeMessage());
                    Console.WriteLine($"Choking peer {peer.Peer.Peer}");
                }
            }
        }
        
        // Optimistic unchoke - randomly select one choked peer to unchoke
        var chokedPeers = connectedPeers
            .Where(p => p.AmChoking && p.IsInterested)
            .ToList();
            
        if (chokedPeers.Count > 0)
        {
            int randomIndex = random.Next(chokedPeers.Count);
            PeerId luckyPeer = chokedPeers[randomIndex];
            
            // Unchoke the lucky peer
            luckyPeer.EnqueueMessage(new UnchokeMessage());
            Console.WriteLine($"Optimistically unchoking peer {luckyPeer.Peer.Peer}");
        }
    }
    
    public void Dispose()
    {
        chokeTimer.Stop();
        chokeTimer.Dispose();
    }
}
```

### Bandwidth Monitoring for Multiple Peers

```csharp
// Create a class that monitors overall bandwidth across peers
public class BandwidthMonitor
{
    private readonly TorrentManager manager;
    private readonly Timer updateTimer;
    private readonly Queue<long> downloadSamples = new Queue<long>();
    private readonly Queue<long> uploadSamples = new Queue<long>();
    private readonly int maxSamples = 10; // Average over 10 seconds
    
    private long lastTotalDownload;
    private long lastTotalUpload;
    
    public double AverageDownloadSpeed { get; private set; }
    public double AverageUploadSpeed { get; private set; }
    
    public BandwidthMonitor(TorrentManager manager)
    {
        this.manager = manager;
        
        // Get initial values
        lastTotalDownload = GetTotalDownload();
        lastTotalUpload = GetTotalUpload();
        
        // Update every second
        updateTimer = new Timer(1000);
        updateTimer.Elapsed += UpdateBandwidthStats;
        updateTimer.Start();
    }
    
    private long GetTotalDownload()
    {
        return manager.Peers.ConnectedPeers.Sum(p => p.Monitor.DataBytesDownloaded);
    }
    
    private long GetTotalUpload()
    {
        return manager.Peers.ConnectedPeers.Sum(p => p.Monitor.DataBytesUploaded);
    }
    
    private void UpdateBandwidthStats(object sender, ElapsedEventArgs e)
    {
        // Get current totals
        long currentTotalDownload = GetTotalDownload();
        long currentTotalUpload = GetTotalUpload();
        
        // Calculate differences since last update
        long downloadDelta = currentTotalDownload - lastTotalDownload;
        long uploadDelta = currentTotalUpload - lastTotalUpload;
        
        // Store for next update
        lastTotalDownload = currentTotalDownload;
        lastTotalUpload = currentTotalUpload;
        
        // Add to samples, removing old ones if needed
        downloadSamples.Enqueue(downloadDelta);
        uploadSamples.Enqueue(uploadDelta);
        
        if (downloadSamples.Count > maxSamples)
            downloadSamples.Dequeue();
            
        if (uploadSamples.Count > maxSamples)
            uploadSamples.Dequeue();
            
        // Calculate averages
        AverageDownloadSpeed = downloadSamples.Average();
        AverageUploadSpeed = uploadSamples.Average();
        
        // Output current stats
        Console.WriteLine($"Download: {AverageDownloadSpeed / 1024:F2} KB/s, Upload: {AverageUploadSpeed / 1024:F2} KB/s");
        Console.WriteLine($"Connected Peers: {manager.Peers.ConnectedPeers.Count}");
    }
    
    public void Dispose()
    {
        updateTimer.Stop();
        updateTimer.Dispose();
    }
}
```

## Implementation Details

The `ConnectionMonitor` uses a sliding window approach to calculate transfer rates:

1. Each call to `Tick()` updates the sliding window:
   - The oldest measurement is removed
   - The current measurement is added
   - The average is recalculated

2. Transfer rates are calculated as the moving average over the last several seconds
   - This smooths out temporary fluctuations for a more stable reading
   - The window size is typically 4-5 seconds

3. Transfer type distinction:
   - Data bytes: Actual torrent content (pieces)
   - Protocol bytes: BitTorrent protocol overhead (messages, headers)
   - Total bytes: Sum of data and protocol bytes

## Remarks

- `ConnectionMonitor` instances are typically created and managed by the `PeerId` class
- The monitor is updated automatically by internal torrent engine mechanisms
- Transfer speeds are recalculated approximately once per second
- These statistics are used by the choking algorithm to decide which peers to unchoke
- The `DownloadSpeed` and `UploadSpeed` properties return instantaneous rates, not averages
- For more stable readings, applications may want to average these values over time

## Related

- [PeerId](../client/PeerId.md)
- [Peer](../client/Peer.md)
- [PeerManager](../client/PeerManager.md)
- [TorrentManager](../client/TorrentManager.md)