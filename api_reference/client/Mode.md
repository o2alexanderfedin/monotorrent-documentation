# Mode Class

The `Mode` class is an abstract base class that represents a torrent's operational state and defines how it behaves in that state.

**Namespace**: `MonoTorrent.Client`

**Assembly**: `MonoTorrent.Client.dll`

## Syntax

```csharp
public abstract class Mode
```

## Description

The `Mode` class implements the State pattern in MonoTorrent. Each torrent (represented by a `TorrentManager`) is always in exactly one mode, and that mode determines how the torrent behaves. For example:

- When in `DownloadMode`, the torrent actively requests pieces from peers
- When in `SeedingMode`, the torrent only uploads pieces to peers
- When in `StoppedMode`, the torrent does not transfer data

The `Mode` class provides the base functionality for all states, and specific mode classes implement behavior for each state.

## Properties

### CanAcceptConnections

Gets a value indicating whether the torrent can accept new peer connections in this mode.

```csharp
public virtual bool CanAcceptConnections { get; }
```

### CanHandleMessages

Gets a value indicating whether the torrent can process peer messages in this mode.

```csharp
public virtual bool CanHandleMessages { get; }
```

### Manager

Gets the `TorrentManager` associated with this mode.

```csharp
protected TorrentManager Manager { get; }
```

### State

Gets the `TorrentState` enum value corresponding to this mode.

```csharp
public abstract TorrentState State { get; }
```

## Methods

### HandlePeerConnected(PeerId)

Called when a peer connection is established.

```csharp
public virtual void HandlePeerConnected(PeerId id)
```

#### Parameters

- **id**: The peer that connected.

### HandlePeerDisconnected(PeerId)

Called when a peer disconnects.

```csharp
public virtual void HandlePeerDisconnected(PeerId id)
```

#### Parameters

- **id**: The peer that disconnected.

### Tick()

Called periodically to perform regular processing for this mode.

```csharp
public abstract void Tick();
```

## Derived Classes

MonoTorrent implements several mode classes, each corresponding to a specific torrent state:

### DownloadMode

Represents a torrent that is actively downloading. In this mode, the torrent requests pieces from peers and processes incoming messages.

```csharp
public class DownloadMode : Mode
{
    public override TorrentState State => TorrentState.Downloading;
}
```

### ErrorMode

Represents a torrent that has encountered an error and cannot continue normal operation.

```csharp
public class ErrorMode : Mode
{
    public override TorrentState State => TorrentState.Error;
}
```

### HashingMode

Represents a torrent that is verifying the integrity of downloaded data by hashing pieces.

```csharp
public class HashingMode : Mode
{
    public override TorrentState State => TorrentState.Hashing;
}
```

### InitialSeedingMode

Represents a torrent that is in initial seeding mode, which prioritizes uploading rare pieces to help distribute the torrent quickly.

```csharp
public class InitialSeedingMode : Mode
{
    public override TorrentState State => TorrentState.Seeding;
}
```

### MetadataMode

Represents a torrent that is downloading metadata (typically from a magnet link).

```csharp
public class MetadataMode : Mode
{
    public override TorrentState State => TorrentState.Metadata;
}
```

### PausedMode

Represents a torrent that is paused. In this mode, the torrent maintains connections but does not transfer data.

```csharp
public class PausedMode : Mode
{
    public override TorrentState State => TorrentState.Paused;
}
```

### SeedingMode

Represents a torrent that has completed downloading and is only uploading to peers.

```csharp
public class SeedingMode : Mode
{
    public override TorrentState State => TorrentState.Seeding;
}
```

### StoppedMode

Represents a torrent that is stopped. In this mode, the torrent is not active and does not transfer data.

```csharp
public class StoppedMode : Mode
{
    public override TorrentState State => TorrentState.Stopped;
}
```

### StoppingMode

Represents a torrent that is in the process of stopping.

```csharp
public class StoppingMode : Mode
{
    public override TorrentState State => TorrentState.Stopping;
}
```

## Examples

### Using Mode to Determine Torrent State

```csharp
// Check the current state of a torrent
TorrentState state = torrentManager.State;

// Perform actions based on the state
switch (state)
{
    case TorrentState.Downloading:
        Console.WriteLine("Torrent is downloading");
        break;
        
    case TorrentState.Seeding:
        Console.WriteLine("Torrent is seeding");
        break;
        
    case TorrentState.Stopped:
        Console.WriteLine("Torrent is stopped");
        break;
        
    case TorrentState.Hashing:
        Console.WriteLine("Torrent is verifying data");
        break;
        
    // Handle other states...
}
```

### Mode Transitions

```csharp
// The TorrentManager automatically transitions between modes
// based on the actions you take:

// Start a stopped torrent - transitions to Downloading or Seeding mode
await torrentManager.StartAsync();

// Pause a running torrent - transitions to Paused mode
await torrentManager.PauseAsync();

// Stop a torrent - transitions to Stopped mode
await torrentManager.StopAsync();

// HashCheck a torrent - transitions to Hashing mode
await torrentManager.HashCheckAsync();
```

### Creating a Custom Mode

```csharp
// Custom mode implementation for specialized behavior
public class CustomMode : Mode
{
    public CustomMode(TorrentManager manager)
        : base(manager)
    {
    }
    
    public override TorrentState State => TorrentState.Downloading;
    
    public override bool CanAcceptConnections => true;
    
    public override bool CanHandleMessages => true;
    
    public override void Tick()
    {
        // Custom processing logic that runs periodically
        Console.WriteLine("Custom mode tick");
        
        // Request specific pieces based on custom logic
        foreach (var peer in Manager.Peers.ConnectedPeers)
        {
            if (!peer.IsChoking)
            {
                // Custom piece selection logic
                // ...
            }
        }
    }
    
    public override void HandlePeerConnected(PeerId id)
    {
        // Custom peer connection handling
        Console.WriteLine($"Peer connected in custom mode: {id.Uri}");
        base.HandlePeerConnected(id);
    }
}

// Using the custom mode
void ApplyCustomMode(TorrentManager manager)
{
    // Note: Directly setting the Mode property is not recommended
    // in normal operation, as it can disrupt the internal state.
    // This is just for demonstration.
    var customMode = new CustomMode(manager);
    
    // Use reflection to set the mode (for demonstration only)
    typeof(TorrentManager)
        .GetProperty("Mode")
        .SetValue(manager, customMode);
}
```

## Remarks

- The `Mode` class is a key part of MonoTorrent's architecture and implements the State pattern.
- Modes encapsulate state-specific behavior, making the code more maintainable.
- Each mode is responsible for implementing the appropriate behavior for its state.
- The `TorrentManager` handles transitions between modes based on user actions and internal events.
- Typically, you don't directly interact with mode classes - you use the `TorrentManager` methods like `StartAsync()`, `StopAsync()`, etc.
- The `State` property of a `TorrentManager` reflects the current mode's state.

## See Also

- [TorrentManager](TorrentManager.md)
- [TorrentState](../enums/TorrentState.md)
- [DownloadMode](DownloadMode.md)
- [SeedingMode](SeedingMode.md)
- [StoppedMode](StoppedMode.md)