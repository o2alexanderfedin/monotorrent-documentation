# MonoTorrent Core Component Diagrams

This document contains UML diagrams representing the core architecture of MonoTorrent.

## Client Engine and Torrent Manager Relationship

The following diagram shows the relationship between the main components of MonoTorrent:

```mermaid
classDiagram
    class ClientEngine {
        -EngineSettings Settings
        -ConnectionManager ConnectionManager
        -DhtEngine DhtEngine
        -DiskManager DiskManager
        -List~TorrentManager~ Torrents
        +AddAsync(Torrent, string) Task~TorrentManager~
        +AddAsync(MagnetLink, string) Task~TorrentManager~
        +StartAllAsync() Task
        +StopAllAsync() Task
        +RegisterAsync(TorrentManager) Task
        +UnregisterAsync(TorrentManager) Task
    }
    
    class TorrentManager {
        -Torrent Torrent
        -PeerManager Peers
        -TrackerManager TrackerManager
        -DiskManager DiskManager
        -PieceManager PieceManager
        -Mode Mode
        +Progress double
        +State TorrentState
        +StartAsync() Task
        +StopAsync() Task
        +PauseAsync() Task
        +HashCheckAsync() Task
    }
    
    class PeerManager {
        -List~Peer~ AvailablePeers
        -List~PeerId~ ConnectedPeers
        +MaxPeers int
        +AddPeer(Peer, PeerAddedReason) bool
        +ConnectToPeer(Peer) Task~bool~
        +GetConnectedPeers() List~PeerId~
    }
    
    class TrackerManager {
        -List~ITracker~ Trackers
        +AnnounceInterval TimeSpan
        +CurrentTracker ITracker
        +Add(Uri) bool
        +AnnounceAsync() Task~bool~
        +ScrapeAsync(ITracker) Task~ScrapeResponse~
    }
    
    class DiskManager {
        +MaximumOpenFiles int
        +OpenFiles int
        +ReadRate long
        +WriteRate long
        +ReadAsync(...) Task~ReadResult~
        +WriteAsync(...) Task~bool~
        +GetHashAsync(...) Task~ReadResult~
        +MoveFilesAsync(...) Task
    }
    
    class Mode {
        #TorrentManager Manager
        +CanAcceptConnections bool
        +CanHandleMessages bool
        +State TorrentState
        +Tick() void
        +HandlePeerConnected(PeerId) void
        +HandlePeerDisconnected(PeerId) void
    }
    
    class PieceManager {
        -BitField BitField
        -List~Piece~ Pieces
        +UnhashedPieces int
        +ValidateHash(int, byte[], long) bool
        +PieceComplete(int) void
        +AddRequested(PeerId, int) void
    }
    
    class Torrent {
        +InfoHash InfoHash
        +Name string
        +Files List~TorrentFile~
        +Size long
        +PieceLength int
        +PieceCount int
        +Comment string
        +IsPrivate bool
    }
    
    ClientEngine "1" -- "many" TorrentManager : manages
    TorrentManager "1" -- "1" PeerManager : has
    TorrentManager "1" -- "1" TrackerManager : has
    TorrentManager "1" -- "1" PieceManager : has
    TorrentManager "1" -- "1" Mode : has
    TorrentManager "1" -- "1" Torrent : has
    ClientEngine "1" -- "1" DiskManager : has
    TorrentManager -- DiskManager : uses
```

## Torrent States and Modes

This diagram illustrates the relationship between the `TorrentState` enum and the various `Mode` implementations:

```mermaid
classDiagram
    class TorrentState {
        <<enumeration>>
        Stopped
        Stopping
        Downloading
        DownloadingMetadata
        Seeding
        Hashing
        Error
        Metadata
        Paused
    }
    
    class Mode {
        <<abstract>>
        #TorrentManager Manager
        +CanAcceptConnections bool
        +CanHandleMessages bool
        +State TorrentState
        +Tick() void*
        +HandlePeerConnected(PeerId) void*
        +HandlePeerDisconnected(PeerId) void*
    }
    
    class StoppedMode {
        +State = TorrentState.Stopped
        +Tick() override
        +HandlePeerConnected() override
    }
    
    class DownloadMode {
        +State = TorrentState.Downloading
        +Tick() override
        +HandlePeerConnected() override
    }
    
    class SeedingMode {
        +State = TorrentState.Seeding
        +Tick() override
        +HandlePeerConnected() override
    }
    
    class HashingMode {
        +State = TorrentState.Hashing
        +Tick() override
        +HandlePeerConnected() override
    }
    
    class MetadataMode {
        +State = TorrentState.Metadata
        +Tick() override
        +HandlePeerConnected() override
    }
    
    class ErrorMode {
        +State = TorrentState.Error
        +Tick() override
        +HandlePeerConnected() override
    }
    
    class PausedMode {
        +State = TorrentState.Paused
        +Tick() override
        +HandlePeerConnected() override
    }
    
    Mode <|-- StoppedMode
    Mode <|-- DownloadMode
    Mode <|-- SeedingMode
    Mode <|-- HashingMode
    Mode <|-- MetadataMode
    Mode <|-- ErrorMode
    Mode <|-- PausedMode
    
    Mode -- TorrentState : returns
```

## Peer Communication Classes

This diagram shows the classes involved in peer communication:

```mermaid
classDiagram
    class PeerId {
        +IPeerConnection Connection
        +BitField BitField
        +bool AmChoking
        +bool AmInterested
        +bool IsChoking
        +bool IsInterested
        +PeerExchangeManager PeerExchangeManager
        +ProcessMessage(Message) void
        +EnqueueMessage(Message) void
    }
    
    class Peer {
        +Uri ConnectionUri
        +InfoHash InfoHash
        +int RepeatedFailures
        +PeerStatus Status
        +string PeerId
        +bool IsSeeder
    }
    
    class IPeerConnection {
        <<interface>>
        +ReadOnlyMemory~byte~ AddressBytes
        +bool CanReconnect
        +bool IsIncoming
        +EndPoint RemoteEndPoint
        +ConnectAsync() Task
        +ReceiveAsync(ByteBuffer) Task~int~
        +SendAsync(ByteBuffer) Task~int~
    }
    
    class Message {
        <<abstract>>
        +int ByteLength
        +Decode(ReadOnlySpan~byte~) void*
        +Encode(Span~byte~) int*
    }
    
    class HandshakeMessage {
        +InfoHash InfoHash
        +string ProtocolString
        +ReadOnlyMemory~byte~ PeerId
    }
    
    class PieceMessage {
        +int PieceIndex
        +int StartOffset
        +ReadOnlyMemory~byte~ Data
    }
    
    class RequestMessage {
        +int PieceIndex
        +int StartOffset
        +int RequestLength
    }
    
    class HaveMessage {
        +int PieceIndex
    }
    
    class BitfieldMessage {
        +BitField BitField
    }
    
    class ConnectionManager {
        +int HalfOpenConnections
        +int OpenConnections
        +int MaxConnections
        +AddPendingConnection(PendingConnection) void
        +CleanupPeerConnections() void
    }
    
    PeerId "1" -- "1" Peer : references
    PeerId "1" -- "1" IPeerConnection : has
    PeerId -- Message : sends/receives
    ConnectionManager -- PeerId : manages
    Message <|-- HandshakeMessage
    Message <|-- PieceMessage
    Message <|-- RequestMessage
    Message <|-- HaveMessage
    Message <|-- BitfieldMessage
```

## Piece Picking and Storage Hierarchy

This diagram shows the piece picking strategies and storage interfaces:

```mermaid
classDiagram
    class IPiecePicker {
        <<interface>>
        +Initialise(BitField, TorrentFile[], Piece[]) void
        +PickPiece(PeerId, BitField, List~PeerId~) int
        +CancelRequest(PeerId, int, int, int) void
        +ValidatePiece(PeerId, int, bool) void
    }
    
    class StandardPicker {
        -BitField BitField
        -List~TorrentFile~ Files
        -List~Piece~ Pieces
        +PickPiece(...) override
        +CancelRequest(...) override
    }
    
    class RarestFirstPicker {
        -StandardPicker BasePicker
        -List~int~ RarestPieces
        +PickPiece(...) override
    }
    
    class RandomisedPicker {
        -StandardPicker BasePicker
        +PickPiece(...) override
    }
    
    class PriorityPicker {
        -StandardPicker BasePicker
        -List~TorrentFile~ Files
        +PickPiece(...) override
    }
    
    class EndGamePicker {
        -StandardPicker BasePicker
        -List~PendingRequest~ PendingRequests
        +PickPiece(...) override
        +CancelRequest(...) override
    }
    
    class ITorrentStorage {
        <<interface>>
        +List~ITorrentFileInfo~ Files
        +CloseAsync() Task
        +ExistsAsync() Task~bool~
        +FlushAsync() Task
        +MoveAsync(string) Task
        +ReadAsync(...) Task~int~
        +WriteAsync(...) Task~bool~
    }
    
    class ITorrentFileInfo {
        <<interface>>
        +string FullPath
        +long Length
        +string Path
        +Priority Priority
        +int StartPieceIndex
        +int EndPieceIndex
        +BitField BitField
        +double Progress
    }
    
    class DiskManager {
        +MaximumOpenFiles int
        +ReadRate long
        +WriteRate long
        +ReadAsync(...) Task~ReadResult~
        +WriteAsync(...) Task~bool~
    }
    
    IPiecePicker <|-- StandardPicker
    IPiecePicker <|-- RarestFirstPicker
    IPiecePicker <|-- RandomisedPicker
    IPiecePicker <|-- PriorityPicker
    IPiecePicker <|-- EndGamePicker
    
    RarestFirstPicker --> StandardPicker : uses
    RandomisedPicker --> StandardPicker : uses
    PriorityPicker --> StandardPicker : uses
    EndGamePicker --> StandardPicker : uses
    
    DiskManager -- ITorrentStorage : uses
    ITorrentStorage -- ITorrentFileInfo : contains
```

## Tracker and DHT Classes

This diagram shows the tracker and DHT components:

```mermaid
classDiagram
    class TrackerManager {
        -List~ITracker~ Trackers
        +AnnounceInterval TimeSpan
        +CurrentTracker ITracker
        +Add(Uri) bool
        +AnnounceAsync() Task~bool~
        +ScrapeAsync(ITracker) Task~ScrapeResponse~
    }
    
    class ITracker {
        <<interface>>
        +Uri Uri
        +bool CanAnnounce
        +bool CanScrape
        +Uri ScrapeUri
        +string FailureMessage
        +string WarningMessage
        +AnnounceAsync(AnnounceParameters) Task~AnnounceResponse~
        +ScrapeAsync(ScrapeParameters) Task~ScrapeResponse~
    }
    
    class HttpTracker {
        -Uri Uri
        +AnnounceAsync(...) override
        +ScrapeAsync(...) override
    }
    
    class UdpTracker {
        -Uri Uri
        -Socket Socket
        +AnnounceAsync(...) override
        +ScrapeAsync(...) override
    }
    
    class DhtTracker {
        -DhtEngine Engine
        +AnnounceAsync(...) override
        +ScrapeAsync(...) override
    }
    
    class DhtEngine {
        -Node LocalNode
        -RoutingTable RoutingTable
        -DhtListener Listener
        +AddNode(Node) void
        +GetPeersAsync(InfoHash) Task~List~Peer~~
        +AnnounceAsync(InfoHash, int) Task
    }
    
    class Node {
        +NodeId Id
        +IPEndPoint EndPoint
        +NodeState State
        +LastSeen DateTime
    }
    
    class RoutingTable {
        -List~Bucket~ Buckets
        -Node LocalNode
        +Add(Node) bool
        +FindClosest(NodeId) List~Node~
    }
    
    TrackerManager "1" -- "many" ITracker : manages
    ITracker <|-- HttpTracker
    ITracker <|-- UdpTracker
    ITracker <|-- DhtTracker
    DhtTracker -- DhtEngine : uses
    DhtEngine "1" -- "many" Node : manages
    DhtEngine "1" -- "1" RoutingTable : has
    RoutingTable "1" -- "many" Node : contains
```

## Extension Points Diagram

This diagram illustrates the main extension points in MonoTorrent:

```mermaid
classDiagram
    class ClientEngine {
        +RegisterDhtEndPoint(IPEndPoint) void
        +RegisterLocalPeerDiscovery() void
    }
    
    class ITorrentStorageFactory {
        <<interface>>
        +Create(Torrent, string) ITorrentStorage
    }
    
    class DefaultTorrentStorageFactory {
        +Create(Torrent, string) ITorrentStorage
    }
    
    class IPiecePicker {
        <<interface>>
        +Initialise(BitField, TorrentFile[], Piece[]) void
        +PickPiece(PeerId, BitField, List~PeerId~) int
    }
    
    class IPeerConnection {
        <<interface>>
        +ConnectAsync() Task
        +ReceiveAsync(ByteBuffer) Task~int~
        +SendAsync(ByteBuffer) Task~int~
    }
    
    class ConnectionFactory {
        <<abstract>>
        +CreateOutboundConnection(EndPoint) IPeerConnection
        +CreateInboundConnection(buffer, EndPoint) IPeerConnection
    }
    
    class TcpConnectionFactory {
        +CreateOutboundConnection(EndPoint) override
        +CreateInboundConnection(buffer, EndPoint) override
    }
    
    class ITorrentStorage {
        <<interface>>
        +ReadAsync(...) Task~int~
        +WriteAsync(...) Task~bool~
    }
    
    class TorrentStorage {
        -string BasePath
        -List~TorrentFileInfo~ Files
        +ReadAsync(...) override
        +WriteAsync(...) override
    }
    
    class ITracker {
        <<interface>>
        +AnnounceAsync(AnnounceParameters) Task~AnnounceResponse~
        +ScrapeAsync(ScrapeParameters) Task~ScrapeResponse~
    }
    
    ITorrentStorageFactory <|-- DefaultTorrentStorageFactory
    ConnectionFactory <|-- TcpConnectionFactory
    ITorrentStorage <|-- TorrentStorage
    
    ClientEngine -- ITorrentStorageFactory : uses
    ClientEngine -- ConnectionFactory : uses
    ClientEngine -- IPiecePicker : uses
    TorrentManager -- ITorrentStorage : uses
    TrackerManager -- ITracker : uses
```

These diagrams provide a comprehensive view of MonoTorrent's architecture and component relationships.