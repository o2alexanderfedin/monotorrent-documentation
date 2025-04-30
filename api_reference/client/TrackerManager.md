# TrackerManager Class

The `TrackerManager` class coordinates communication with BitTorrent trackers for a torrent.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public class TrackerManager
```

## Description

The `TrackerManager` class is responsible for:

- Managing the list of trackers for a torrent
- Sending announces to trackers
- Processing tracker responses
- Handling tracker failures and retries
- Managing tracker tiers

Each `TorrentManager` has its own `TrackerManager` instance to handle tracker-related operations for that specific torrent.

## Properties

### AnnounceInterval

Gets or sets the interval between tracker announces in seconds.

```csharp
public TimeSpan AnnounceInterval { get; set; }
```

### CurrentTracker

Gets the tracker that was most recently announced to.

```csharp
public ITracker CurrentTracker { get; }
```

### LastAnnounceTimes

Gets a dictionary containing the last announce time for each tracker.

```csharp
public ReadOnlyDictionary<ITracker, DateTime> LastAnnounceTimes { get; }
```

### Trackers

Gets the list of all trackers.

```csharp
public IList<ITracker> Trackers { get; }
```

### SupportsFastResume

Gets a value indicating whether fast resume is supported.

```csharp
public bool SupportsFastResume { get; }
```

## Methods

### Add(Uri)

Adds a tracker with the specified URI.

```csharp
public bool Add(Uri uri)
```

#### Parameters

- **uri**: The URI of the tracker to add.

#### Returns

`true` if the tracker was added, `false` otherwise.

### Add(ITracker)

Adds the specified tracker.

```csharp
public bool Add(ITracker tracker)
```

#### Parameters

- **tracker**: The tracker to add.

#### Returns

`true` if the tracker was added, `false` otherwise.

### AddTracker(Uri)

Adds a tracker with the specified URI.

```csharp
public bool AddTracker(Uri uri)
```

#### Parameters

- **uri**: The URI of the tracker to add.

#### Returns

`true` if the tracker was added, `false` otherwise.

### AnnounceAsync()

Sends an announce to the next available tracker.

```csharp
public Task<bool> AnnounceAsync()
```

#### Returns

A task that returns `true` if the announce was successful, `false` otherwise.

### AnnounceAsync(ITracker)

Sends an announce to the specified tracker.

```csharp
public Task<bool> AnnounceAsync(ITracker tracker)
```

#### Parameters

- **tracker**: The tracker to announce to.

#### Returns

A task that returns `true` if the announce was successful, `false` otherwise.

### Remove(ITracker)

Removes the specified tracker.

```csharp
public bool Remove(ITracker tracker)
```

#### Parameters

- **tracker**: The tracker to remove.

#### Returns

`true` if the tracker was removed, `false` otherwise.

### Remove(Uri)

Removes the tracker with the specified URI.

```csharp
public bool Remove(Uri uri)
```

#### Parameters

- **uri**: The URI of the tracker to remove.

#### Returns

`true` if the tracker was removed, `false` otherwise.

### ScrapeAsync(ITracker)

Scrapes the specified tracker to get statistics about the torrent.

```csharp
public Task<ScrapeResponse> ScrapeAsync(ITracker tracker)
```

#### Parameters

- **tracker**: The tracker to scrape.

#### Returns

A task that returns a `ScrapeResponse` with the tracker statistics.

## Events

### AnnounceComplete

Raised when a tracker announce completes successfully.

```csharp
public event EventHandler<AnnounceResponseEventArgs> AnnounceComplete;
```

### AnnounceFailed

Raised when a tracker announce fails.

```csharp
public event EventHandler<AnnounceResponseEventArgs> AnnounceFailed;
```

### AnnounceStarting

Raised when a tracker announce is about to start.

```csharp
public event EventHandler<AnnounceResponseEventArgs> AnnounceStarting;
```

### ScrapeComplete

Raised when a tracker scrape completes successfully.

```csharp
public event EventHandler<ScrapeResponseEventArgs> ScrapeComplete;
```

### ScrapeFailed

Raised when a tracker scrape fails.

```csharp
public event EventHandler<ScrapeResponseEventArgs> ScrapeFailed;
```

## Examples

### Basic Tracker Management

```csharp
// Get the TrackerManager from a TorrentManager
var trackerManager = torrentManager.TrackerManager;

// Add a new tracker
bool added = trackerManager.Add(new Uri("http://tracker.example.com:6969/announce"));
if (added)
{
    Console.WriteLine("Tracker added successfully");
}

// List all trackers
foreach (var tracker in trackerManager.Trackers)
{
    Console.WriteLine($"Tracker: {tracker.Uri}");
    Console.WriteLine($"Status: {tracker.Status}");
    Console.WriteLine($"Failure Message: {tracker.FailureMessage}");
    Console.WriteLine($"Warning Message: {tracker.WarningMessage}");
    Console.WriteLine();
}
```

### Manually Announcing to a Tracker

```csharp
// Announce to the next tracker in the rotation
bool success = await torrentManager.TrackerManager.AnnounceAsync();
Console.WriteLine($"Announce successful: {success}");

// Announce to a specific tracker
var specificTracker = torrentManager.TrackerManager.Trackers.FirstOrDefault();
if (specificTracker != null)
{
    success = await torrentManager.TrackerManager.AnnounceAsync(specificTracker);
    Console.WriteLine($"Announce to {specificTracker.Uri} successful: {success}");
}
```

### Scraping a Tracker for Statistics

```csharp
// Scrape a tracker to get statistics
var tracker = torrentManager.TrackerManager.Trackers.FirstOrDefault(t => t.CanScrape);
if (tracker != null)
{
    var response = await torrentManager.TrackerManager.ScrapeAsync(tracker);
    if (response.Successful)
    {
        Console.WriteLine($"Complete (seeders): {response.Complete}");
        Console.WriteLine($"Incomplete (leechers): {response.Incomplete}");
        Console.WriteLine($"Downloaded: {response.Downloaded}");
    }
    else
    {
        Console.WriteLine($"Scrape failed: {response.FailureMessage}");
    }
}
```

### Handling Tracker Events

```csharp
// Subscribe to tracker events
trackerManager.AnnounceComplete += (sender, e) => 
{
    Console.WriteLine($"Announce to {e.Tracker.Uri} completed successfully");
    Console.WriteLine($"Peers received: {e.Peers.Count}");
    Console.WriteLine($"Complete (seeders): {e.Complete}");
    Console.WriteLine($"Incomplete (leechers): {e.Incomplete}");
    Console.WriteLine($"Warning message: {e.WarningMessage}");
};

trackerManager.AnnounceFailed += (sender, e) => 
{
    Console.WriteLine($"Announce to {e.Tracker.Uri} failed");
    Console.WriteLine($"Failure message: {e.FailureMessage}");
};

trackerManager.AnnounceStarting += (sender, e) => 
{
    Console.WriteLine($"Starting announce to {e.Tracker.Uri}");
};

trackerManager.ScrapeComplete += (sender, e) => 
{
    Console.WriteLine($"Scrape of {e.Tracker.Uri} completed successfully");
    Console.WriteLine($"Complete (seeders): {e.Complete}");
    Console.WriteLine($"Incomplete (leechers): {e.Incomplete}");
};

trackerManager.ScrapeFailed += (sender, e) => 
{
    Console.WriteLine($"Scrape of {e.Tracker.Uri} failed");
    Console.WriteLine($"Failure message: {e.FailureMessage}");
};
```

### Working with Tracker Tiers

```csharp
// Add trackers to specific tiers
var tier1 = new[]
{
    new Uri("http://tracker1.example.com/announce"),
    new Uri("http://tracker2.example.com/announce")
};

var tier2 = new[]
{
    new Uri("http://backup1.example.com/announce"),
    new Uri("http://backup2.example.com/announce")
};

// Create a new torrent with specific tracker tiers
var creator = new TorrentCreator();
creator.Announces.Add(new RawTrackerTier(tier1));
creator.Announces.Add(new RawTrackerTier(tier2));

// Later, when the torrent is loaded, the TrackerManager will handle the tiers
// The trackers in tier1 will be tried before any in tier2
```

## Remarks

- The `TrackerManager` automatically handles most tracker-related operations.
- Trackers are organized in tiers, with trackers in the first tier tried before the second tier, and so on.
- Within a tier, trackers are tried in a round-robin fashion.
- Failed trackers are retried after a delay, typically with an exponential backoff.
- Announces are automatically sent when a torrent starts, completes, or stops.
- Additional announces are sent periodically based on the `AnnounceInterval` property and tracker responses.
- The announce URLs and interval are typically specified in the .torrent file.

## See Also

- [ITracker](../client/ITracker.md)
- [AnnounceParameters](../client/AnnounceParameters.md)
- [ScrapeParameters](../client/ScrapeParameters.md)
- [TorrentManager](TorrentManager.md)
- [ClientEngine](ClientEngine.md)