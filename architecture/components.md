# MonoTorrent Core Components

This document provides detailed information about the core components of MonoTorrent and their responsibilities.

## ClientEngine

The `ClientEngine` is the central coordination component of MonoTorrent. It manages all torrents and global settings.

### Responsibilities

- Managing the collection of active `TorrentManager` instances
- Handling global download/upload rate limits
- Managing the global connection manager
- Coordinating port forwarding (UPnP/NAT-PMP)
- Managing the DHT engine
- Dispatching events to interested listeners
- Providing global configuration settings

### Key Properties and Methods

- `Settings`: Global engine settings
- `RegisterTorrent(TorrentManager)`: Adds a torrent to be managed
- `UnregisterTorrent(TorrentManager)`: Removes a torrent from management
- `StartAll()`: Starts all registered torrents
- `StopAll()`: Stops all registered torrents
- `IsRunning`: Indicates if the engine is running

## TorrentManager

The `TorrentManager` handles a single torrent and coordinates all operations related to it.

### Responsibilities

- Managing the current torrent state (via Mode classes)
- Coordination of piece downloading/uploading
- Managing communication with trackers
- Handling peer discovery and connections
- Coordinating disk operations for the torrent
- Dispatching torrent-specific events

### Key Properties and Methods

- `Start()`: Starts or resumes the torrent
- `Stop()`: Stops the torrent
- `Torrent`: Access to torrent metadata
- `Bitfield`: Tracks which pieces have been downloaded
- `State`: Current state of the torrent (downloading, seeding, etc.)
- `Progress`: Download progress as a percentage

## PeerManager

The `PeerManager` handles all peer-related operations for a torrent.

### Responsibilities

- Maintaining the list of available peers
- Managing active peer connections
- Handling peer messages and requests
- Implementing peer connection policies
- Handling peer exchange (PEX)

### Key Classes

- `Peer`: Represents information about a potential peer
- `PeerId`: Represents an active connection to a peer
- `ConnectionManager`: Manages active peer connections
- `PeerExchangeManager`: Implements the peer exchange extension

## DiskManager

The `DiskManager` handles all disk I/O operations.

### Responsibilities

- Reading and writing torrent pieces
- Verifying piece hashes
- Managing file allocation
- Implementing prioritized I/O queues
- Handling read-ahead for improved performance

### Key Components

- `DiskWriter`: Writes data to disk
- `DiskReader`: Reads data from disk
- `FileAllocator`: Handles file allocation
- `ITorrentFileInfo`: Represents file information within a torrent

## PieceManager and Piece Pickers

These components decide which pieces to request from peers and handle piece validation.

### PieceManager Responsibilities

- Tracking which pieces have been downloaded
- Validating downloaded pieces
- Coordinating with piece pickers to determine what to download next

### Piece Picker Types

- `StandardPicker`: Basic sequential piece picking
- `RarestFirstPicker`: Prioritizes the rarest pieces in the swarm
- `RandomisedPicker`: Randomly selects pieces to request
- `PriorityPicker`: Downloads pieces based on file priority
- `EndGamePicker`: Special strategy used when approaching download completion
- `StreamingPicker`: Optimizes piece selection for streaming

## TrackerManager

The `TrackerManager` coordinates communication with BitTorrent trackers.

### Responsibilities

- Managing the list of trackers for a torrent
- Sending announces to trackers
- Processing tracker responses
- Handling tracker failures and retries
- Managing tracker tiers

### Key Classes

- `TrackerClient`: Base class for different tracker types
- `HttpTrackerClient`: Implementation for HTTP trackers
- `UdpTrackerClient`: Implementation for UDP trackers
- `AnnounceParameters`: Parameters for tracker announcements

## DHT Engine

The DHT (Distributed Hash Table) engine implements trackerless operation through the Kademlia protocol.

### Responsibilities

- Maintaining a routing table of DHT nodes
- Handling node lookups and routing
- Getting peer lists for torrents
- Announcing the client's status for torrents
- Implementing the DHT protocol as specified in BEP 5

### Key Components

- `DhtEngine`: Main entry point for DHT functionality
- `RoutingTable`: Maintains the list of known DHT nodes
- `Node`: Represents a node in the DHT network
- `NodeId`: Unique identifier for a DHT node
- `TokenManager`: Handles security tokens for the DHT protocol

## Connection Related Components

These components handle the low-level aspects of peer connections.

### Key Components

- `PeerConnectionFactory`: Creates appropriate connection types
- `IPeerConnection`: Interface for peer connections
- `IConnection`: Low-level connection interface
- `EncryptedConnection`: Implements protocol encryption
- `Message`: Base class for peer protocol messages

## Mode Classes

MonoTorrent uses the State pattern to manage different torrent states through Mode classes.

### Key Mode Classes

- `Mode`: Base class for all modes
- `StoppedMode`: When the torrent is not active
- `DownloadMode`: Normal downloading state
- `SeedingMode`: When the torrent is complete and uploading to peers
- `HashingMode`: When verifying downloaded data
- `MetadataMode`: When downloading torrent metadata from peers

## Rate Limiters

Components that manage bandwidth usage.

### Key Classes

- `RateLimiter`: Base class for rate limiters
- `RateLimiterGroup`: Manages multiple rate limiters
- `DiskWriterRateLimiter`: Limits disk write speed
- `RateLimitedStream`: Stream wrapper that enforces rate limits

## Port Forwarding

Components for automatic router configuration.

### Key Components

- `PortForwarder`: Base class for port forwarding
- `UPnPPortForwarder`: Implements UPnP port mapping
- `NatPmpPortForwarder`: Implements NAT-PMP port mapping