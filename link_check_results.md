# Dangling References Report

## Missing Files Referenced in Documentation

### Source: user_guide/README.md

Missing target: `advanced_usage.md`

Link text: "Advanced Usage"

Context:
```
    - [Basic Usage](basic_usage.md): Getting started with basic operations
    - [Advanced Usage](advanced_usage.md): More complex scenarios and features
    - [Best Practices](best_practices.md): Recommended patterns and practices

```

### Source: user_guide/README.md

Missing target: `best_practices.md`

Link text: "Best Practices"

Context:
```
    - [Advanced Usage](advanced_usage.md): More complex scenarios and features
    - [Best Practices](best_practices.md): Recommended patterns and practices
    - [Troubleshooting](troubleshooting.md): Common issues and solutions
```

### Source: user_guide/README.md

Missing target: `troubleshooting.md`

Link text: "Troubleshooting"

Context:
```
    - [Best Practices](best_practices.md): Recommended patterns and practices
    - [Troubleshooting](troubleshooting.md): Common issues and solutions
```

### Source: api_reference/client/TrackerManager.md

Missing target: `../client/ITracker.md`

Link text: "ITracker"

Context:
```
    
    - [ITracker](../client/ITracker.md)
    - [AnnounceParameters](../client/AnnounceParameters.md)

```

### Source: api_reference/client/TrackerManager.md

Missing target: `../client/AnnounceParameters.md`

Link text: "AnnounceParameters"

Context:
```
    - [ITracker](../client/ITracker.md)
    - [AnnounceParameters](../client/AnnounceParameters.md)
    - [ScrapeParameters](../client/ScrapeParameters.md)

```

### Source: api_reference/client/TrackerManager.md

Missing target: `../client/ScrapeParameters.md`

Link text: "ScrapeParameters"

Context:
```
    - [AnnounceParameters](../client/AnnounceParameters.md)
    - [ScrapeParameters](../client/ScrapeParameters.md)
    - [TorrentManager](TorrentManager.md)

```

### Source: api_reference/client/TorrentManager.md

Missing target: `TorrentSettings.md`

Link text: "TorrentSettings"

Context:
```
    - [ClientEngine](ClientEngine.md)
    - [TorrentSettings](TorrentSettings.md)
    - [PeerManager](PeerManager.md)

```

### Source: api_reference/client/PeerManager.md

Missing target: `../client/Peer.md`

Link text: "Peer"

Context:
```
    
    - [Peer](../client/Peer.md)
    - [PeerId](../client/PeerId.md)

```

### Source: api_reference/client/PeerManager.md

Missing target: `../client/PeerId.md`

Link text: "PeerId"

Context:
```
    - [Peer](../client/Peer.md)
    - [PeerId](../client/PeerId.md)
    - [TorrentManager](TorrentManager.md)

```

### Source: examples/README.md

Missing target: `custom_storage.md`

Link text: "Custom Storage"

Context:
```
    - [Creating Torrents](creating_torrents.md): How to create torrent files
    - [Custom Storage](custom_storage.md): Implementing custom storage solutions
    

```

### Source: examples/README.md

Missing target: `magnet_links.md`

Link text: "Magnet Links"

Context:
```
    
    - [Magnet Links](magnet_links.md): Working with magnet links
    - [Metadata Mode](metadata_mode.md): Downloading metadata only

```

### Source: examples/README.md

Missing target: `metadata_mode.md`

Link text: "Metadata Mode"

Context:
```
    - [Magnet Links](magnet_links.md): Working with magnet links
    - [Metadata Mode](metadata_mode.md): Downloading metadata only
    - [Event Handling](event_handling.md): Handling MonoTorrent events

```

### Source: examples/README.md

Missing target: `event_handling.md`

Link text: "Event Handling"

Context:
```
    - [Metadata Mode](metadata_mode.md): Downloading metadata only
    - [Event Handling](event_handling.md): Handling MonoTorrent events
    - [Custom Trackers](custom_trackers.md): Implementing custom trackers
```

### Source: examples/README.md

Missing target: `custom_trackers.md`

Link text: "Custom Trackers"

Context:
```
    - [Event Handling](event_handling.md): Handling MonoTorrent events
    - [Custom Trackers](custom_trackers.md): Implementing custom trackers
```

### Source: tutorials/README.md

Missing target: `downloading_files_tutorial.md`

Link text: "Downloading Files"

Context:
```
    - [Creating a Simple Torrent Client](simple_client_tutorial.md): Step-by-step guide to create a basic torrent client
    - [Downloading Files](downloading_files_tutorial.md): Complete guide to downloading files
    

```

### Source: tutorials/README.md

Missing target: `torrent_creator_tutorial.md`

Link text: "Creating a Torrent Creator"

Context:
```
    
    - [Creating a Torrent Creator](torrent_creator_tutorial.md): Building a tool to create torrents
    - [Building a Tracker](tracker_tutorial.md): Implementing a basic tracker

```

### Source: tutorials/README.md

Missing target: `tracker_tutorial.md`

Link text: "Building a Tracker"

Context:
```
    - [Creating a Torrent Creator](torrent_creator_tutorial.md): Building a tool to create torrents
    - [Building a Tracker](tracker_tutorial.md): Implementing a basic tracker
    

```

### Source: tutorials/README.md

Missing target: `custom_piece_picker_tutorial.md`

Link text: "Implementing a Custom Piece Picker"

Context:
```
    
    - [Implementing a Custom Piece Picker](custom_piece_picker_tutorial.md): Creating specialized download strategies
    - [Building a Web-based Client](web_client_tutorial.md): Integrating MonoTorrent with web technologies
```

### Source: tutorials/README.md

Missing target: `web_client_tutorial.md`

Link text: "Building a Web-based Client"

Context:
```
    - [Implementing a Custom Piece Picker](custom_piece_picker_tutorial.md): Creating specialized download strategies
    - [Building a Web-based Client](web_client_tutorial.md): Integrating MonoTorrent with web technologies
```

### Source: api_reference/client/ConnectionManager.md

Missing target: `PeerId.md`

Link text: "PeerId"

Context:
```
    - [ClientEngine](ClientEngine.md)
    - [PeerId](PeerId.md)
    - [Peer](Peer.md)

```

### Source: api_reference/client/ConnectionManager.md

Missing target: `Peer.md`

Link text: "Peer"

Context:
```
    - [PeerId](PeerId.md)
    - [Peer](Peer.md)
    - [TorrentManager](TorrentManager.md)

```

### Source: api_reference/client/ConnectionManager.md

Missing target: `EngineSettings.md`

Link text: "EngineSettings"

Context:
```
    - [TorrentManager](TorrentManager.md)
    - [EngineSettings](EngineSettings.md)
```

### Source: api_reference/enums/TorrentState.md

Missing target: `../client/TorrentStateChangedEventArgs.md`

Link text: "TorrentStateChangedEventArgs"

Context:
```
    - [TorrentManager](../client/TorrentManager.md)
    - [TorrentStateChangedEventArgs](../client/TorrentStateChangedEventArgs.md)
    - [Mode](../client/Mode.md)
```

### Source: api_reference/dht/DhtEngine.md

Missing target: `Node.md`

Link text: "Node"

Context:
```
    
    - [Node](Node.md)
    - [NodeId](NodeId.md)

```

### Source: api_reference/dht/DhtEngine.md

Missing target: `NodeId.md`

Link text: "NodeId"

Context:
```
    - [Node](Node.md)
    - [NodeId](NodeId.md)
    - [RoutingTable](RoutingTable.md)

```

### Source: api_reference/dht/DhtEngine.md

Missing target: `RoutingTable.md`

Link text: "RoutingTable"

Context:
```
    - [NodeId](NodeId.md)
    - [RoutingTable](RoutingTable.md)
    - [DhtListener](DhtListener.md)

```

### Source: api_reference/dht/DhtEngine.md

Missing target: `DhtListener.md`

Link text: "DhtListener"

Context:
```
    - [RoutingTable](RoutingTable.md)
    - [DhtListener](DhtListener.md)
    - [InfoHash](../client/InfoHash.md)

```

### Source: api_reference/dht/DhtEngine.md

Missing target: `../client/InfoHash.md`

Link text: "InfoHash"

Context:
```
    - [DhtListener](DhtListener.md)
    - [InfoHash](../client/InfoHash.md)
    - [BEP 5: DHT Protocol](http://www.bittorrent.org/beps/bep_0005.html)
```

### Source: api_reference/client/DiskManager.md

Missing target: `EngineSettings.md`

Link text: "EngineSettings"

Context:
```
    - [TorrentManager](TorrentManager.md)
    - [EngineSettings](EngineSettings.md)
    - [ITorrentStorage](../client/ITorrentStorage.md)

```

### Source: api_reference/client/DiskManager.md

Missing target: `../client/ITorrentStorage.md`

Link text: "ITorrentStorage"

Context:
```
    - [EngineSettings](EngineSettings.md)
    - [ITorrentStorage](../client/ITorrentStorage.md)
    - [ReadResult](../client/ReadResult.md)
```

### Source: api_reference/client/DiskManager.md

Missing target: `../client/ReadResult.md`

Link text: "ReadResult"

Context:
```
    - [ITorrentStorage](../client/ITorrentStorage.md)
    - [ReadResult](../client/ReadResult.md)
```

### Source: api_reference/client/Mode.md

Missing target: `DownloadMode.md`

Link text: "DownloadMode"

Context:
```
    - [TorrentState](../enums/TorrentState.md)
    - [DownloadMode](DownloadMode.md)
    - [SeedingMode](SeedingMode.md)

```

### Source: api_reference/client/Mode.md

Missing target: `SeedingMode.md`

Link text: "SeedingMode"

Context:
```
    - [DownloadMode](DownloadMode.md)
    - [SeedingMode](SeedingMode.md)
    - [StoppedMode](StoppedMode.md)
```

### Source: api_reference/client/Mode.md

Missing target: `StoppedMode.md`

Link text: "StoppedMode"

Context:
```
    - [SeedingMode](SeedingMode.md)
    - [StoppedMode](StoppedMode.md)
```

### Source: api_reference/client/ClientEngine.md

Missing target: `EngineSettings.md`

Link text: "EngineSettings"

Context:
```
    
    - [EngineSettings](EngineSettings.md)
    - [TorrentManager](TorrentManager.md)

```

### Source: api_reference/client/BitField.md

Missing target: `PeerId.md`

Link text: "PeerId"

Context:
```
    - [TorrentManager](TorrentManager.md)
    - [PeerId](PeerId.md)
    - [BitfieldMessage](../messages/BitfieldMessage.md)
```

### Source: api_reference/client/BitField.md

Missing target: `../messages/BitfieldMessage.md`

Link text: "BitfieldMessage"

Context:
```
    - [PeerId](PeerId.md)
    - [BitfieldMessage](../messages/BitfieldMessage.md)
```

### Source: api_reference/README.md

Missing target: `client/README.md`

Link text: "MonoTorrent.Client"

Context:
```
    
    - [MonoTorrent.Client](client/README.md): Client-side torrent implementation
    - [MonoTorrent.Dht](dht/README.md): Distributed Hash Table implementation

```

### Source: api_reference/README.md

Missing target: `dht/README.md`

Link text: "MonoTorrent.Dht"

Context:
```
    - [MonoTorrent.Client](client/README.md): Client-side torrent implementation
    - [MonoTorrent.Dht](dht/README.md): Distributed Hash Table implementation
    - [MonoTorrent.Tracker](tracker/README.md): Tracker functionality

```

### Source: api_reference/README.md

Missing target: `tracker/README.md`

Link text: "MonoTorrent.Tracker"

Context:
```
    - [MonoTorrent.Dht](dht/README.md): Distributed Hash Table implementation
    - [MonoTorrent.Tracker](tracker/README.md): Tracker functionality
    - [MonoTorrent.Common](common/README.md): Shared utilities and data structures

```

### Source: api_reference/README.md

Missing target: `common/README.md`

Link text: "MonoTorrent.Common"

Context:
```
    - [MonoTorrent.Tracker](tracker/README.md): Tracker functionality
    - [MonoTorrent.Common](common/README.md): Shared utilities and data structures
    

```

## Potential Missing API Documentation

Classes mentioned but without dedicated documentation files:

- **Console** (mentioned 530 times)
- **WriteLine** (mentioned 468 times)
- **Task** (mentioned 226 times)
- **Create** (mentioned 138 times)
- **Path** (mentioned 135 times)
- **Add** (mentioned 125 times)
- **DHT** (mentioned 101 times)
- **State** (mentioned 96 times)
- **Length** (mentioned 95 times)
- **Gets** (mentioned 92 times)
- **File** (mentioned 81 times)
- **System** (mentioned 81 times)
- **List** (mentioned 80 times)
- **Peer** (mentioned 79 times)
- **Files** (mentioned 76 times)
- **PeerId** (mentioned 72 times)
- **AppendLine** (mentioned 71 times)
- **Parameters** (mentioned 70 times)
- **Client** (mentioned 64 times)
- **Message** (mentioned 61 times)
- **Error** (mentioned 58 times)
- **Name** (mentioned 54 times)
- **Download** (mentioned 54 times)
- **Progress** (mentioned 53 times)
- **Piece** (mentioned 53 times)
- **Count** (mentioned 52 times)
- **Uri** (mentioned 51 times)
- **Returns** (mentioned 51 times)
- **Peers** (mentioned 45 times)
- **Monitor** (mentioned 45 times)
- **Tracker** (mentioned 44 times)
- **Load** (mentioned 44 times)
- **Set** (mentioned 44 times)
- **Write** (mentioned 43 times)
- **Example** (mentioned 42 times)
- **Exception** (mentioned 42 times)
- **Directory** (mentioned 41 times)
- **EngineSettings** (mentioned 39 times)
- **Start** (mentioned 39 times)
- **Description** (mentioned 38 times)
- **Creating** (mentioned 37 times)
- **ToHex** (mentioned 36 times)
- **ITorrentFileInfo** (mentioned 35 times)
- **Custom** (mentioned 35 times)
- **Combine** (mentioned 35 times)
- **AddAsync** (mentioned 34 times)
- **Data** (mentioned 34 times)
- **Protocol** (mentioned 34 times)
- **Downloading** (mentioned 33 times)
- **All** (mentioned 33 times)
- **StartAsync** (mentioned 32 times)
- **When** (mentioned 32 times)
- **Seeding** (mentioned 31 times)
- **BEP** (mentioned 31 times)
- **Examples** (mentioned 30 times)
- **Use** (mentioned 30 times)
- **Save** (mentioned 30 times)
- **Complete** (mentioned 30 times)
- **Creates** (mentioned 30 times)
- **Response** (mentioned 30 times)
- **ITorrentStorage** (mentioned 29 times)
- **Methods** (mentioned 29 times)
- **Basic** (mentioned 28 times)
- **Key** (mentioned 27 times)
- **ITracker** (mentioned 26 times)
- **Implement** (mentioned 26 times)
- **Managing** (mentioned 26 times)
- **Display** (mentioned 26 times)
- **ReadLine** (mentioned 26 times)
- **Torrents** (mentioned 25 times)
- **TimeSpan** (mentioned 25 times)
- **Size** (mentioned 25 times)
- **PieceLength** (mentioned 25 times)
- **Usage** (mentioned 25 times)
- **Namespace** (mentioned 25 times)
- **Step** (mentioned 25 times)
- **IPiecePicker** (mentioned 24 times)
- **Get** (mentioned 24 times)
- **EventHandler** (mentioned 24 times)
- **DownloadRate** (mentioned 23 times)
- **Raised** (mentioned 23 times)
- **WebSeeds** (mentioned 23 times)
- **Parse** (mentioned 23 times)
- **Trackers** (mentioned 22 times)
- **Storage** (mentioned 22 times)
- **Node** (mentioned 22 times)
- **Stop** (mentioned 22 times)
- **Handling** (mentioned 22 times)
- **Check** (mentioned 22 times)
- **Bitfield** (mentioned 22 times)
- **Streaming** (mentioned 22 times)
- **AnnounceAsync** (mentioned 21 times)
- **Extension** (mentioned 21 times)
- **For** (mentioned 21 times)
- **Implementing** (mentioned 21 times)
- **Maximum** (mentioned 21 times)
- **Dispose** (mentioned 21 times)
- **Request** (mentioned 21 times)
- **Exists** (mentioned 21 times)
- **StandardPicker** (mentioned 20 times)
- **Properties** (mentioned 20 times)
- **EndsWith** (mentioned 20 times)
- **Upload** (mentioned 20 times)
- **IList** (mentioned 20 times)
- **URLs** (mentioned 20 times)
- **Settings** (mentioned 19 times)
- **Metadata** (mentioned 19 times)
- **Whether** (mentioned 19 times)
- **Management** (mentioned 19 times)
- **Threading** (mentioned 19 times)
- **Publisher** (mentioned 19 times)
- **StopAsync** (mentioned 18 times)
- **WriteAsync** (mentioned 18 times)
- **Connection** (mentioned 18 times)
- **Integration** (mentioned 18 times)
- **NET** (mentioned 18 times)
- **Class** (mentioned 18 times)
- **ListenPort** (mentioned 18 times)
- **Assembly** (mentioned 18 times)
- **Remove** (mentioned 18 times)
- **Downloads** (mentioned 18 times)
- **Magnet** (mentioned 18 times)
- **FormatSize** (mentioned 18 times)
- **FromResult** (mentioned 18 times)
- **PieceManager** (mentioned 17 times)
- **ConnectedPeers** (mentioned 17 times)
- **ReadAsync** (mentioned 17 times)
- **ReadOnlyMemory** (mentioned 17 times)
- **Type** (mentioned 17 times)
- **Remarks** (mentioned 17 times)
- **Copy** (mentioned 17 times)
- **MaximumDownloadRate** (mentioned 17 times)
- **MaximumUploadRate** (mentioned 17 times)
- **CreateDirectory** (mentioned 17 times)
- **Announces** (mentioned 17 times)
- **Enter** (mentioned 17 times)
- **Status** (mentioned 16 times)
- **StartPieceIndex** (mentioned 16 times)
- **Find** (mentioned 16 times)
- **Simple** (mentioned 16 times)
- **NewState** (mentioned 16 times)
- **UploadRate** (mentioned 16 times)
- **Main** (mentioned 16 times)
- **Adds** (mentioned 16 times)
- **URI** (mentioned 16 times)
- **Sets** (mentioned 16 times)
- **Private** (mentioned 16 times)
- **Engine** (mentioned 15 times)
- **Tick** (mentioned 15 times)
- **Pieces** (mentioned 15 times)
- **Comment** (mentioned 15 times)
- **FullPath** (mentioned 15 times)
- **DoNotDownload** (mentioned 15 times)
- **Math** (mentioned 15 times)
- **Events** (mentioned 15 times)
- **Update** (mentioned 15 times)
- **Program** (mentioned 15 times)
- **Normal** (mentioned 15 times)
- **Represents** (mentioned 15 times)
- **MemoryStorage** (mentioned 15 times)
- **EndPoint** (mentioned 14 times)
- **Initialise** (mentioned 14 times)
- **PickPiece** (mentioned 14 times)
- **RarestFirstPicker** (mentioned 14 times)
- **IPEndPoint** (mentioned 14 times)
- **Guide** (mentioned 14 times)
- **Advanced** (mentioned 14 times)
- **Architecture** (mentioned 14 times)
- **Dictionary** (mentioned 14 times)
- **TorrentStateChanged** (mentioned 14 times)
- **Each** (mentioned 14 times)
- **Stream** (mentioned 14 times)
- **Delay** (mentioned 14 times)
- **Tasks** (mentioned 14 times)
- **Environment** (mentioned 14 times)
- **Port** (mentioned 14 times)
- **TorrentSettings** (mentioned 14 times)
- **IEnumerable** (mentioned 14 times)
- **StopAllAsync** (mentioned 13 times)
- **HandlePeerConnected** (mentioned 13 times)
- **Stopped** (mentioned 13 times)
- **Paused** (mentioned 13 times)
- **Min** (mentioned 13 times)
- **OldState** (mentioned 13 times)
- **Configure** (mentioned 13 times)
- **Announce** (mentioned 13 times)
- **High** (mentioned 13 times)
- **Using** (mentioned 13 times)
- **CreateAsync** (mentioned 13 times)
- **ReadResult** (mentioned 12 times)
- **IPeerConnection** (mentioned 12 times)
- **PriorityPicker** (mentioned 12 times)
- **EndGamePicker** (mentioned 12 times)
- **EndPieceIndex** (mentioned 12 times)
- **RoutingTable** (mentioned 12 times)
- **NodeId** (mentioned 12 times)
- **Memory** (mentioned 12 times)
- **Connections** (mentioned 12 times)
- **PeerDisconnected** (mentioned 12 times)
- **Subscribe** (mentioned 12 times)
- **Handle** (mentioned 12 times)
- **Considerations** (mentioned 12 times)
- **LoadAsync** (mentioned 12 times)
- **See** (mentioned 12 times)
- **PEX** (mentioned 12 times)
- **Position** (mentioned 12 times)
- **Clear** (mentioned 12 times)
- **CreatedBy** (mentioned 12 times)
- **Speed** (mentioned 12 times)
- **ToLower** (mentioned 12 times)
- **CurrentDirectory** (mentioned 12 times)
- **Delete** (mentioned 12 times)
- **MemoryTorrentFile** (mentioned 12 times)
- **PauseAsync** (mentioned 11 times)
- **ScrapeAsync** (mentioned 11 times)
- **Best** (mentioned 11 times)
- **Common** (mentioned 11 times)
- **Method** (mentioned 11 times)
- **Now** (mentioned 11 times)
- **Disk** (mentioned 11 times)
- **Also** (mentioned 11 times)
- **Tutorials** (mentioned 11 times)
- **Hash** (mentioned 11 times)
- **URL** (mentioned 11 times)
- **Selection** (mentioned 11 times)
- **Read** (mentioned 11 times)
- **GetInput** (mentioned 11 times)
- **Ask** (mentioned 11 times)
- **Core** (mentioned 10 times)
- **Manager** (mentioned 10 times)
- **Hashing** (mentioned 10 times)
- **StoppedMode** (mentioned 10 times)
- **SeedingMode** (mentioned 10 times)
- **Classes** (mentioned 10 times)
- **Practices** (mentioned 10 times)
- **Return** (mentioned 10 times)
- **Array** (mentioned 10 times)
- **PieceHashed** (mentioned 10 times)
- **PeerConnected** (mentioned 10 times)
- **Calculate** (mentioned 10 times)
- **You** (mentioned 10 times)
- **Background** (mentioned 10 times)
- **Grid** (mentioned 10 times)
- **ToString** (mentioned 10 times)
- **Contains** (mentioned 10 times)
- **Syntax** (mentioned 10 times)
- **RawTrackerTier** (mentioned 10 times)
- **Total** (mentioned 10 times)
- **From** (mentioned 10 times)
- **Press** (mentioned 10 times)
- **Make** (mentioned 10 times)
- **ITorrentManagerInfo** (mentioned 10 times)
- **MaximumOpenFiles** (mentioned 9 times)
- **DownloadMode** (mentioned 9 times)
- **ReadOnlySpan** (mentioned 9 times)
- **OpenConnections** (mentioned 9 times)
- **RandomisedPicker** (mentioned 9 times)
- **User** (mentioned 9 times)
- **SHA1** (mentioned 9 times)
- **Constructors** (mentioned 9 times)
- **IReadOnlyList** (mentioned 9 times)
- **Adding** (mentioned 9 times)
- **Resource** (mentioned 9 times)
- **Updates** (mentioned 9 times)
- **TorrentService** (mentioned 9 times)
- **Initialize** (mentioned 9 times)
- **Monitoring** (mentioned 9 times)
- **MaximumConnections** (mentioned 9 times)
- **Failed** (mentioned 9 times)
- **Verification** (mentioned 9 times)
- **Local** (mentioned 9 times)
- **Discovery** (mentioned 9 times)
- **Low** (mentioned 9 times)
- **Global** (mentioned 9 times)
- **Rate** (mentioned 9 times)
- **SHA** (mentioned 9 times)
- **Wait** (mentioned 9 times)
- **Media** (mentioned 9 times)
- **Collections** (mentioned 9 times)
- **Generic** (mentioned 9 times)
- **TryParse** (mentioned 9 times)
- **Invalid** (mentioned 9 times)
- **StartAllAsync** (mentioned 8 times)
- **MaxConnections** (mentioned 8 times)
- **CancelRequest** (mentioned 8 times)
- **AnnounceParameters** (mentioned 8 times)
- **DateTime** (mentioned 8 times)
- **Recommended** (mentioned 8 times)
- **Highest** (mentioned 8 times)
- **IDisposable** (mentioned 8 times)
- **Implementation** (mentioned 8 times)
- **Register** (mentioned 8 times)
- **Performance** (mentioned 8 times)
- **Conclusion** (mentioned 8 times)
- **Service** (mentioned 8 times)
- **Application** (mentioned 8 times)
- **AddTorrentAsync** (mentioned 8 times)
- **CancellationToken** (mentioned 8 times)
- **CompletedTask** (mentioned 8 times)
- **GetFiles** (mentioned 8 times)
- **New** (mentioned 8 times)
- **AllowedEncryption** (mentioned 8 times)
- **EncryptionTypes** (mentioned 8 times)
- **Handles** (mentioned 8 times)
- **Completed** (mentioned 8 times)
- **Reference** (mentioned 8 times)
- **Flow** (mentioned 8 times)
- **Includes** (mentioned 8 times)
- **Loading** (mentioned 8 times)
- **Definition** (mentioned 8 times)
- **LoadFastResumeAsync** (mentioned 8 times)
- **Clone** (mentioned 8 times)
- **Open** (mentioned 8 times)
- **SaveFastResumeAsync** (mentioned 8 times)
- **WriteAllBytes** (mentioned 8 times)
- **Trim** (mentioned 8 times)
- **ETA** (mentioned 8 times)
- **BEncodedString** (mentioned 8 times)
- **Let** (mentioned 8 times)
- **InitializeClientAsync** (mentioned 8 times)
- **ConnectToPeer** (mentioned 7 times)
- **ScrapeResponse** (mentioned 7 times)
- **IsPrivate** (mentioned 7 times)
- **PieceIndex** (mentioned 7 times)
- **Points** (mentioned 7 times)
- **TorrentStorage** (mentioned 7 times)
- **These** (mentioned 7 times)
- **How** (mentioned 7 times)
- **MD5** (mentioned 7 times)
- **Instance** (mentioned 7 times)
- **Other** (mentioned 7 times)
- **ConnectionAttemptFailed** (mentioned 7 times)
- **Web** (mentioned 7 times)
- **Operations** (mentioned 7 times)
- **Text** (mentioned 7 times)
- **Value** (mentioned 7 times)
- **FromSeconds** (mentioned 7 times)
- **OpenRead** (mentioned 7 times)
- **Process** (mentioned 7 times)
- **Provides** (mentioned 7 times)
- **Exchange** (mentioned 7 times)
- **Allows** (mentioned 7 times)
- **TrueCount** (mentioned 7 times)
- **ReadAllBytes** (mentioned 7 times)
- **StreamingPicker** (mentioned 7 times)
- **AddStreamingAsync** (mentioned 7 times)
- **StreamProvider** (mentioned 7 times)
- **UPnP** (mentioned 7 times)
- **Distributed** (mentioned 7 times)
- **Responsibilities** (mentioned 7 times)
- **Coordinating** (mentioned 7 times)
- **AnnounceUrls** (mentioned 7 times)
- **Optional** (mentioned 7 times)
- **BEncodedDictionary** (mentioned 7 times)
- **Hybrid** (mentioned 7 times)
- **Link** (mentioned 7 times)
- **Not** (mentioned 7 times)
- **Initializing** (mentioned 7 times)
- **FastResume** (mentioned 7 times)
- **DisposeAsync** (mentioned 7 times)
- **RegisterTorrentEvents** (mentioned 7 times)
- **Component** (mentioned 6 times)
- **MaxPeers** (mentioned 6 times)
- **AnnounceInterval** (mentioned 6 times)
- **Stopping** (mentioned 6 times)
- **HashingMode** (mentioned 6 times)
- **MetadataMode** (mentioned 6 times)
- **ByteBuffer** (mentioned 6 times)
- **StartOffset** (mentioned 6 times)
- **BitfieldMessage** (mentioned 6 times)
- **FailureMessage** (mentioned 6 times)
- **ITorrentStorageFactory** (mentioned 6 times)
- **ConnectionFactory** (mentioned 6 times)
- **Setting** (mentioned 6 times)
- **FirstOrDefault** (mentioned 6 times)
- **Cases** (mentioned 6 times)
- **NAT** (mentioned 6 times)
- **BEPs** (mentioned 6 times)
- **Event** (mentioned 6 times)
- **HashPassed** (mentioned 6 times)
- **Ensure** (mentioned 6 times)
- **Patterns** (mentioned 6 times)
- **Xamarin** (mentioned 6 times)
- **Timer** (mentioned 6 times)
- **Binding** (mentioned 6 times)
- **Content** (mentioned 6 times)
- **Build** (mentioned 6 times)
- **Run** (mentioned 6 times)
- **Incomplete** (mentioned 6 times)
- **Working** (mentioned 6 times)
- **Later** (mentioned 6 times)
- **Source** (mentioned 6 times)
- **Code** (mentioned 6 times)
- **Documents** (mentioned 6 times)
- **Next** (mentioned 6 times)
- **IPAddress** (mentioned 6 times)
- **Skip** (mentioned 6 times)
- **Saving** (mentioned 6 times)
- **PiecePicking** (mentioned 6 times)
- **Helps** (mentioned 6 times)
- **Base** (mentioned 6 times)
- **Table** (mentioned 6 times)
- **Stops** (mentioned 6 times)
- **Implements** (mentioned 6 times)
- **Encoding** (mentioned 6 times)
- **Disposes** (mentioned 6 times)
- **Saves** (mentioned 6 times)
- **Block** (mentioned 6 times)
- **First** (mentioned 6 times)
- **Reason** (mentioned 6 times)
- **PercentComplete** (mentioned 6 times)
- **Try** (mentioned 6 times)
- **IsNullOrEmpty** (mentioned 6 times)
- **MaxHalfOpenConnections** (mentioned 6 times)
- **BlockInfo** (mentioned 6 times)
- **CancellationTokenSource** (mentioned 6 times)
- **DisplayProgressAsync** (mentioned 6 times)
- **StartAllTorrentsAsync** (mentioned 6 times)
- **PauseAllTorrentsAsync** (mentioned 6 times)
- **StopAllTorrentsAsync** (mentioned 6 times)
- **RemoveTorrentAsync** (mentioned 6 times)
- **Added** (mentioned 6 times)
- **Clean** (mentioned 6 times)
- **Track** (mentioned 6 times)
- **HasMetadata** (mentioned 6 times)
- **ToLowerInvariant** (mentioned 6 times)
- **Close** (mentioned 6 times)
- **HttpListenerContext** (mentioned 6 times)
- **StatusCode** (mentioned 6 times)
- **ContentLength64** (mentioned 6 times)
- **CleanEmptyDirectories** (mentioned 6 times)
- **AvailablePeers** (mentioned 5 times)
- **ReadRate** (mentioned 5 times)
- **WriteRate** (mentioned 5 times)
- **CanAcceptConnections** (mentioned 5 times)
- **CanHandleMessages** (mentioned 5 times)
- **ConnectionUri** (mentioned 5 times)
- **Decode** (mentioned 5 times)
- **Encode** (mentioned 5 times)
- **ValidatePiece** (mentioned 5 times)
- **ScrapeParameters** (mentioned 5 times)
- **GetPeersAsync** (mentioned 5 times)
- **Getting** (mentioned 5 times)
- **Priorities** (mentioned 5 times)
- **Lowest** (mentioned 5 times)
- **Checking** (mentioned 5 times)
- **Downloaded** (mentioned 5 times)
- **Multiple** (mentioned 5 times)
- **Replace** (mentioned 5 times)
- **Picker** (mentioned 5 times)
- **Extensions** (mentioned 5 times)
- **Based** (mentioned 5 times)
- **AnnounceComplete** (mentioned 5 times)
- **Building** (mentioned 5 times)
- **FromMinutes** (mentioned 5 times)
- **Document** (mentioned 5 times)
- **Windows** (mentioned 5 times)
- **Pattern** (mentioned 5 times)
- **Width** (mentioned 5 times)
- **Asynchronous** (mentioned 5 times)
- **Limitations** (mentioned 5 times)
- **GetValue** (mentioned 5 times)
- **TorrentWorker** (mentioned 5 times)
- **LogInformation** (mentioned 5 times)
- **AddTorrentFromFileAsync** (mentioned 5 times)
- **Keep** (mentioned 5 times)
- **Pause** (mentioned 5 times)
- **Adjust** (mentioned 5 times)
- **Removes** (mentioned 5 times)
- **Announcing** (mentioned 5 times)
- **Tutorial** (mentioned 5 times)
- **Developers** (mentioned 5 times)
- **Default** (mentioned 5 times)
- **Encryption** (mentioned 5 times)
- **Any** (mentioned 5 times)
- **Interface** (mentioned 5 times)
- **Determines** (mentioned 5 times)
- **Maintains** (mentioned 5 times)
- **StringComparison** (mentioned 5 times)
- **OrdinalIgnoreCase** (mentioned 5 times)
- **FastResumePicker** (mentioned 5 times)
- **UDP** (mentioned 5 times)
- **PMP** (mentioned 5 times)
- **Manages** (mentioned 5 times)
- **Kademlia** (mentioned 5 times)
- **Fast** (mentioned 5 times)
- **Changes** (mentioned 5 times)
- **Starts** (mentioned 5 times)
- **IsRunning** (mentioned 5 times)
- **Access** (mentioned 5 times)
- **Format** (mentioned 5 times)
- **InfoHashes** (mentioned 5 times)
- **Convert** (mentioned 5 times)
- **SetFilePriorityAsync** (mentioned 5 times)
- **Handshake** (mentioned 5 times)
- **Cancel** (mentioned 5 times)
- **Connected** (mentioned 5 times)
- **Here** (mentioned 5 times)
- **Linq** (mentioned 5 times)
- **Move** (mentioned 5 times)
- **Optionally** (mentioned 5 times)
- **GetDirectoryName** (mentioned 5 times)
- **Select** (mentioned 5 times)
- **CriticalException** (mentioned 5 times)
- **DhtState** (mentioned 5 times)
- **RemoveAsync** (mentioned 5 times)
- **TotalDownloadRate** (mentioned 5 times)
- **TotalUploadRate** (mentioned 5 times)
- **Hashed** (mentioned 5 times)
- **IsMemoryFile** (mentioned 5 times)
- **GetExtension** (mentioned 5 times)
- **UTF8** (mentioned 5 times)
- **Ignore** (mentioned 5 times)
- **RunClientAsync** (mentioned 5 times)
- **ShutdownClientAsync** (mentioned 5 times)
- **AddMagnetLinkAsync** (mentioned 5 times)
- **RegisterAsync** (mentioned 4 times)
- **HashCheckAsync** (mentioned 4 times)
- **AddPeer** (mentioned 4 times)
- **PeerAddedReason** (mentioned 4 times)
- **CurrentTracker** (mentioned 4 times)
- **OpenFiles** (mentioned 4 times)
- **MoveFilesAsync** (mentioned 4 times)
- **HandlePeerDisconnected** (mentioned 4 times)
- **Modes** (mentioned 4 times)
- **ErrorMode** (mentioned 4 times)
- **PausedMode** (mentioned 4 times)
- **Communication** (mentioned 4 times)
- **SendAsync** (mentioned 4 times)
- **ByteLength** (mentioned 4 times)
- **HalfOpenConnections** (mentioned 4 times)
- **BasePicker** (mentioned 4 times)
- **ExistsAsync** (mentioned 4 times)
- **MoveAsync** (mentioned 4 times)
- **WarningMessage** (mentioned 4 times)
- **AnnounceResponse** (mentioned 4 times)
- **DhtTracker** (mentioned 4 times)
- **DhtListener** (mentioned 4 times)
- **Listener** (mentioned 4 times)
- **CreateOutboundConnection** (mentioned 4 times)
- **Range** (mentioned 4 times)
- **Strategies** (mentioned 4 times)
- **ED2K** (mentioned 4 times)
- **TryGetValue** (mentioned 4 times)
- **Factory** (mentioned 4 times)
- **Enhancement** (mentioned 4 times)
- **Proposals** (mentioned 4 times)
- **TorrentProgress** (mentioned 4 times)
- **CustomDiskManager** (mentioned 4 times)
- **Consider** (mentioned 4 times)
- **MAUI** (mentioned 4 times)
- **Mobile** (mentioned 4 times)
- **Allow** (mentioned 4 times)
- **Persistence** (mentioned 4 times)
- **TorrentStateChangedEventArgs** (mentioned 4 times)
- **ListView** (mentioned 4 times)
- **ColumnDefinition** (mentioned 4 times)
- **Column** (mentioned 4 times)
- **Processing** (mentioned 4 times)
- **CPU** (mentioned 4 times)
- **ILogger** (mentioned 4 times)
- **IsCancellationRequested** (mentioned 4 times)
- **LogError** (mentioned 4 times)
- **WiFi** (mentioned 4 times)
- **Limited** (mentioned 4 times)
- **Operation** (mentioned 4 times)
- **NetworkAccess** (mentioned 4 times)
- **Values** (mentioned 4 times)
- **Perform** (mentioned 4 times)
- **Extract** (mentioned 4 times)
- **Shutdown** (mentioned 4 times)
- **Limits** (mentioned 4 times)
- **Verify** (mentioned 4 times)
- **Choose** (mentioned 4 times)
- **AnnounceFailed** (mentioned 4 times)
- **Failure** (mentioned 4 times)
- **Scrape** (mentioned 4 times)
- **Project** (mentioned 4 times)
- **Information** (mentioned 4 times)
- **Completion** (mentioned 4 times)
- **Covers** (mentioned 4 times)
- **Steps** (mentioned 4 times)
- **Available** (mentioned 4 times)
- **WebSeed** (mentioned 4 times)
- **BinaryFormatter** (mentioned 4 times)
- **RequestRejected** (mentioned 4 times)
- **IsInteresting** (mentioned 4 times)
- **Prioritizes** (mentioned 4 times)
- **CreateStreamAsync** (mentioned 4 times)
- **PortForwarder** (mentioned 4 times)
- **Maintaining** (mentioned 4 times)
- **Reading** (mentioned 4 times)
- **Regular** (mentioned 4 times)
- **Support** (mentioned 4 times)
- **Verifying** (mentioned 4 times)
- **TokenManager** (mentioned 4 times)
- **NuGet** (mentioned 4 times)
- **Package** (mentioned 4 times)
- **Version** (mentioned 4 times)
- **Dht** (mentioned 4 times)
- **Planned** (mentioned 4 times)
- **Lists** (mentioned 4 times)
- **ChangeSettingsAsync** (mentioned 4 times)
- **Performs** (mentioned 4 times)
- **Links** (mentioned 4 times)
- **Seconds** (mentioned 4 times)
- **Unchoke** (mentioned 4 times)
- **Limiting** (mentioned 4 times)
- **Shutting** (mentioned 4 times)
- **Creator** (mentioned 4 times)
- **PeersFound** (mentioned 4 times)
- **Equals** (mentioned 4 times)
- **BEncodedValue** (mentioned 4 times)
- **ITorrentManager** (mentioned 4 times)
- **SetReadRateLimit** (mentioned 4 times)
- **SetWriteRateLimit** (mentioned 4 times)
- **Unlimited** (mentioned 4 times)
- **Token** (mentioned 4 times)
- **Please** (mentioned 4 times)
- **SaveAsync** (mentioned 4 times)
- **Nothing** (mentioned 4 times)
- **GetMemoryFile** (mentioned 4 times)
- **HybridStorage** (mentioned 4 times)
- **GetBytes** (mentioned 4 times)
- **And** (mentioned 4 times)
- **FirstFalse** (mentioned 4 times)
- **StartsWith** (mentioned 4 times)
- **GetMimeType** (mentioned 4 times)
- **OutputStream** (mentioned 4 times)
- **SimpleTorrentClient** (mentioned 4 times)
- **GetDirectories** (mentioned 4 times)
- **ResumeData** (mentioned 4 times)
- **UnregisterAsync** (mentioned 3 times)
- **GetConnectedPeers** (mentioned 3 times)
- **GetHashAsync** (mentioned 3 times)
- **PieceCount** (mentioned 3 times)
- **IsChoking** (mentioned 3 times)
- **PeerExchangeManager** (mentioned 3 times)
- **ConnectAsync** (mentioned 3 times)
- **ReceiveAsync** (mentioned 3 times)
- **Span** (mentioned 3 times)
- **RequestMessage** (mentioned 3 times)
- **RequestLength** (mentioned 3 times)
- **CleanupPeerConnections** (mentioned 3 times)
- **Picking** (mentioned 3 times)
- **CloseAsync** (mentioned 3 times)
- **FlushAsync** (mentioned 3 times)
- **CanScrape** (mentioned 3 times)
- **HttpTracker** (mentioned 3 times)
- **UdpTracker** (mentioned 3 times)
- **Socket** (mentioned 3 times)
- **AddNode** (mentioned 3 times)
- **CreateInboundConnection** (mentioned 3 times)
- **TorrentFileInfo** (mentioned 3 times)
- **Troubleshooting** (mentioned 3 times)
- **ITorrentFile** (mentioned 3 times)
- **BytesDownloaded** (mentioned 3 times)
- **IDiskWriter** (mentioned 3 times)
- **TrackerClient** (mentioned 3 times)
- **Authentication** (mentioned 3 times)
- **StartTime** (mentioned 3 times)
- **VerifiedBytes** (mentioned 3 times)
- **MyCustomMode** (mentioned 3 times)
- **Override** (mentioned 3 times)
- **Apply** (mentioned 3 times)
- **MyEngineSettings** (mentioned 3 times)
- **EnableMyFeature** (mentioned 3 times)
- **Desktop** (mentioned 3 times)
- **Applications** (mentioned 3 times)
- **Services** (mentioned 3 times)
- **Embedded** (mentioned 3 times)
- **Forms** (mentioned 3 times)
- **WPF** (mentioned 3 times)
- **Provide** (mentioned 3 times)
- **Always** (mentioned 3 times)
- **Cleanup** (mentioned 3 times)
- **Singleton** (mentioned 3 times)
- **StartTorrentAsync** (mentioned 3 times)
- **TorrentStatus** (mentioned 3 times)
- **GetTorrentStatus** (mentioned 3 times)
- **IActionResult** (mentioned 3 times)
- **TorrentHub** (mentioned 3 times)
- **Clients** (mentioned 3 times)
- **Logging** (mentioned 3 times)
- **Comprehensive** (mentioned 3 times)
- **Worker** (mentioned 3 times)
- **IConfiguration** (mentioned 3 times)
- **DownloadDirectory** (mentioned 3 times)
- **Recovery** (mentioned 3 times)
- **Resume** (mentioned 3 times)
- **TorrentUpdateWorker** (mentioned 3 times)
- **Optimization** (mentioned 3 times)
- **Network** (mentioned 3 times)
- **Very** (mentioned 3 times)
- **Sends** (mentioned 3 times)
- **AnnounceResponseEventArgs** (mentioned 3 times)
- **AnnounceStarting** (mentioned 3 times)
- **ScrapeComplete** (mentioned 3 times)
- **ScrapeFailed** (mentioned 3 times)
- **Warning** (mentioned 3 times)
- **Manually** (mentioned 3 times)
- **Successful** (mentioned 3 times)
- **Starting** (mentioned 3 times)
- **Additional** (mentioned 3 times)
- **Coverage** (mentioned 3 times)
- **While** (mentioned 3 times)
- **Date** (mentioned 3 times)
- **Initial** (mentioned 3 times)
- **Notes** (mentioned 3 times)
- **Current** (mentioned 3 times)
- **Good** (mentioned 3 times)
- **Property** (mentioned 3 times)
- **Enable** (mentioned 3 times)
- **Requests** (mentioned 3 times)
- **AllTrue** (mentioned 3 times)
- **Coordinates** (mentioned 3 times)
- **IPv6** (mentioned 3 times)
- **Design** (mentioned 3 times)
- **Providing** (mentioned 3 times)
- **Writes** (mentioned 3 times)
- **Reads** (mentioned 3 times)
- **Prerequisites** (mentioned 3 times)
- **Missing** (mentioned 3 times)
- **Security** (mentioned 3 times)
- **Structure** (mentioned 3 times)
- **Can** (mentioned 3 times)
- **Uses** (mentioned 3 times)
- **CreationDate** (mentioned 3 times)
- **GetRight** (mentioned 3 times)
- **Static** (mentioned 3 times)
- **Loads** (mentioned 3 times)
- **Asynchronously** (mentioned 3 times)
- **Suggested** (mentioned 3 times)
- **PeerConnectedEventArgs** (mentioned 3 times)
- **PeerDisconnectedEventArgs** (mentioned 3 times)
- **Valid** (mentioned 3 times)
- **Info** (mentioned 3 times)
- **BEncoding** (mentioned 3 times)
- **Ubuntu** (mentioned 3 times)
- **BEncoded** (mentioned 3 times)
- **Standard** (mentioned 3 times)
- **Interested** (mentioned 3 times)
- **Have** (mentioned 3 times)
- **Send** (mentioned 3 times)
- **Efficient** (mentioned 3 times)
- **Once** (mentioned 3 times)
- **Choking** (mentioned 3 times)
- **Every** (mentioned 3 times)
- **Only** (mentioned 3 times)
- **Critical** (mentioned 3 times)
- **Checks** (mentioned 3 times)
- **ClientApp** (mentioned 3 times)
- **Connecting** (mentioned 3 times)
- **Creation** (mentioned 3 times)
- **Substring** (mentioned 3 times)
- **TorrentVersion** (mentioned 3 times)
- **InfoHashV2** (mentioned 3 times)
- **CalculateOptimalPieceLength** (mentioned 3 times)
- **Small** (mentioned 3 times)
- **Medium** (mentioned 3 times)
- **Large** (mentioned 3 times)
- **Utility** (mentioned 3 times)
- **BanPeer** (mentioned 3 times)
- **GetOpenConnections** (mentioned 3 times)
- **GetPeerConnections** (mentioned 3 times)
- **Connect** (mentioned 3 times)
- **Received** (mentioned 3 times)
- **AdaptiveConnectionManager** (mentioned 3 times)
- **Displaying** (mentioned 3 times)
- **StateChanged** (mentioned 3 times)
- **SaveNodes** (mentioned 3 times)
- **SendQueryAsync** (mentioned 3 times)
- **WaitForState** (mentioned 3 times)
- **Ready** (mentioned 3 times)
- **Found** (mentioned 3 times)
- **ReadInt32** (mentioned 3 times)
- **PendingReads** (mentioned 3 times)
- **PendingWrites** (mentioned 3 times)
- **Cancellation** (mentioned 3 times)
- **Exit** (mentioned 3 times)
- **GetFileNameWithoutExtension** (mentioned 3 times)
- **FromHex** (mentioned 3 times)
- **Loaded** (mentioned 3 times)
- **MaxValue** (mentioned 3 times)
- **Hours** (mentioned 3 times)
- **Minutes** (mentioned 3 times)
- **Unknown** (mentioned 3 times)
- **ReadKey** (mentioned 3 times)
- **Called** (mentioned 3 times)
- **CustomMode** (mentioned 3 times)
- **PublisherUrl** (mentioned 3 times)
- **AddAnnounce** (mentioned 3 times)
- **AddAnnounces** (mentioned 3 times)
- **AddWebSeed** (mentioned 3 times)
- **ITorrentFileSource** (mentioned 3 times)
- **IDhtEngine** (mentioned 3 times)
- **Registers** (mentioned 3 times)
- **StatsUpdate** (mentioned 3 times)
- **Initialization** (mentioned 3 times)
- **Buffer** (mentioned 3 times)
- **Failures** (mentioned 3 times)
- **Store** (mentioned 3 times)
- **UpdateBitfield** (mentioned 3 times)
- **Our** (mentioned 3 times)
- **CustomMemoryStorageFactory** (mentioned 3 times)
- **AND** (mentioned 3 times)
- **FirstTrue** (mentioned 3 times)
- **Xor** (mentioned 3 times)
- **XOR** (mentioned 3 times)
- **Ctrl** (mentioned 3 times)
- **IsMediaFile** (mentioned 3 times)
- **Send404** (mentioned 3 times)
- **ContentType** (mentioned 3 times)
- **GetFileProgress** (mentioned 3 times)
- **IsVideoFile** (mentioned 3 times)
- **IsAudioFile** (mentioned 3 times)
- **Server** (mentioned 3 times)
- **Listening** (mentioned 3 times)
