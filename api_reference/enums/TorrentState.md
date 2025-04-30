# TorrentState Enum

The `TorrentState` enum represents the various states a torrent can be in.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public enum TorrentState
```

## Members

| Name | Value | Description |
|------|-------|-------------|
| Stopped | 0 | The torrent is not active. No data is being transferred. |
| Stopping | 1 | The torrent is in the process of stopping. |
| Downloading | 2 | The torrent is downloading. Data is being received from peers. |
| Downloading | 3 | The torrent is downloading metadata. This occurs when a magnet link is used. |
| Seeding | 4 | The torrent has finished downloading and is now uploading to peers. |
| Hashing | 5 | The torrent is checking the integrity of downloaded data. |
| Error | 6 | The torrent encountered an error. |
| Metadata | 7 | The torrent is downloading metadata (from a magnet link). |
| Paused | 8 | The torrent is paused. No data is being transferred, but connections are maintained. |

## Description

The `TorrentState` enum is used to represent the current state of a torrent in MonoTorrent. This state is accessible through the `State` property of a `TorrentManager` object and changes as the torrent progresses through its lifecycle.

The torrent state is useful for displaying the status of torrents to users and for determining what operations are valid on a torrent at a given time.

## Usage

The torrent state can be accessed through the `State` property of a `TorrentManager` instance:

```csharp
TorrentState currentState = torrentManager.State;
```

## State Transitions

Torrents typically transition through several states during their lifecycle:

1. **Stopped** - Initial state when a torrent is added but not started
2. **Downloading Metadata** (if using a magnet link) - Downloading torrent metadata
3. **Hashing** - Verifying any existing data on disk
4. **Downloading** - Downloading missing pieces
5. **Seeding** - Uploading to other peers after download is complete
6. **Stopped** - When explicitly stopped by the user

A torrent can also be **Paused** temporarily or enter an **Error** state if issues occur.

## Examples

### Displaying the Current State

```csharp
// Display the current state of a torrent
Console.WriteLine($"Torrent state: {torrentManager.State}");

// Format the state for display
string stateText = GetStateText(torrentManager.State);
Console.WriteLine($"Status: {stateText}");

// Helper method to convert state to a user-friendly string
string GetStateText(TorrentState state)
{
    switch (state)
    {
        case TorrentState.Stopped:
            return "Stopped";
        case TorrentState.Stopping:
            return "Stopping...";
        case TorrentState.Downloading:
            return "Downloading";
        case TorrentState.DownloadingMetadata:
            return "Downloading Metadata";
        case TorrentState.Seeding:
            return "Seeding";
        case TorrentState.Hashing:
            return "Checking Files...";
        case TorrentState.Error:
            return "Error";
        case TorrentState.Metadata:
            return "Downloading Metadata";
        case TorrentState.Paused:
            return "Paused";
        default:
            return state.ToString();
    }
}
```

### Monitoring State Changes

```csharp
// Subscribe to the torrent state changed event
torrentManager.TorrentStateChanged += (sender, e) =>
{
    Console.WriteLine($"State changed from {e.OldState} to {e.NewState}");
    
    // Handle specific state transitions
    if (e.NewState == TorrentState.Seeding && e.OldState == TorrentState.Downloading)
    {
        Console.WriteLine("Download completed!");
        
        // Perform actions when download completes
        NotifyDownloadComplete(torrentManager.Torrent.Name);
    }
    else if (e.NewState == TorrentState.Error)
    {
        Console.WriteLine("An error occurred with the torrent!");
        
        // Handle the error
        LogTorrentError(torrentManager);
    }
};
```

### Performing Actions Based on State

```csharp
// Check if a specific action is valid in the current state
bool CanPause(TorrentManager manager)
{
    // Can only pause if downloading or seeding
    return manager.State == TorrentState.Downloading || 
           manager.State == TorrentState.Seeding;
}

bool CanResume(TorrentManager manager)
{
    // Can only resume if paused or stopped
    return manager.State == TorrentState.Paused || 
           manager.State == TorrentState.Stopped;
}

// Example usage
async Task TogglePauseResumeAsync(TorrentManager manager)
{
    if (manager.State == TorrentState.Paused || manager.State == TorrentState.Stopped)
    {
        await manager.StartAsync();
        Console.WriteLine("Torrent resumed");
    }
    else if (manager.State == TorrentState.Downloading || manager.State == TorrentState.Seeding)
    {
        await manager.PauseAsync();
        Console.WriteLine("Torrent paused");
    }
    else
    {
        Console.WriteLine($"Cannot toggle pause/resume in state: {manager.State}");
    }
}
```

### Displaying Progress Indicators Based on State

```csharp
// Display appropriate progress information based on state
void DisplayProgress(TorrentManager manager)
{
    switch (manager.State)
    {
        case TorrentState.Stopped:
            Console.WriteLine("Torrent is stopped. Press Start to begin downloading.");
            break;
            
        case TorrentState.Downloading:
            Console.WriteLine($"Downloading: {manager.Progress:F2}%");
            Console.WriteLine($"Speed: {manager.Monitor.DownloadRate / 1024:F2} KB/s");
            break;
            
        case TorrentState.Seeding:
            Console.WriteLine("Download complete. Seeding to other peers.");
            Console.WriteLine($"Upload speed: {manager.Monitor.UploadRate / 1024:F2} KB/s");
            break;
            
        case TorrentState.Hashing:
            Console.WriteLine($"Verifying downloaded data: {manager.Progress:F2}%");
            break;
            
        case TorrentState.Metadata:
            Console.WriteLine("Downloading torrent metadata...");
            break;
            
        case TorrentState.Paused:
            Console.WriteLine($"Paused at {manager.Progress:F2}%");
            break;
            
        case TorrentState.Error:
            Console.WriteLine("Error occurred. Try restarting the torrent.");
            break;
    }
}
```

## Remarks

- The `TorrentState` is primarily controlled by the `Mode` that the `TorrentManager` is currently using.
- State transitions typically occur in response to user actions (e.g., StartAsync, StopAsync, PauseAsync) or due to internal events (e.g., download completion).
- The `TorrentStateChanged` event is raised whenever the torrent state changes, providing the old and new states.
- Some operations are only valid in certain states. For example, you cannot pause a torrent that is already stopped.
- The `Error` state indicates that something went wrong with the torrent. To recover, you typically need to stop and restart the torrent.

## See Also

- [TorrentManager](../client/TorrentManager.md)
- [TorrentStateChangedEventArgs](../client/TorrentStateChangedEventArgs.md)
- [Mode](../client/Mode.md)