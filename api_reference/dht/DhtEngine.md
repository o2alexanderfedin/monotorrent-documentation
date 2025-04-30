# DhtEngine Class

The `DhtEngine` class implements the BitTorrent Distributed Hash Table (DHT) protocol as specified in BEP 5.

**Namespace**: `MonoTorrent.Dht`

**Assembly**: `MonoTorrent.Dht.dll`

## Syntax

```csharp
public class DhtEngine : IDisposable
```

## Description

The `DhtEngine` class provides a way to participate in the BitTorrent DHT network, which enables trackerless operation by allowing peers to find each other without contacting a centralized tracker. The DHT is a Kademlia-based distributed system where each node maintains a routing table of other nodes and can perform lookups to find peers for a specific torrent.

Key responsibilities of the `DhtEngine` include:

- Maintaining a routing table of DHT nodes
- Performing lookups to find peers for torrents
- Responding to requests from other DHT nodes
- Bootstrapping into the DHT network
- Announcing the local client's torrents to the DHT network

## Properties

### IsRunning

Gets a value indicating whether the DHT engine is running.

```csharp
public bool IsRunning { get; }
```

### Listener

Gets the listener used by the DHT engine.

```csharp
public IDhtListener Listener { get; }
```

### NodeId

Gets the ID of the local DHT node.

```csharp
public NodeId LocalNodeId { get; }
```

### RoutingTable

Gets the routing table used by the DHT engine.

```csharp
public RoutingTable RoutingTable { get; }
```

### State

Gets the current state of the DHT engine.

```csharp
public DhtState State { get; }
```

### TokenManager

Gets the token manager used by the DHT engine.

```csharp
public TokenManager TokenManager { get; }
```

## Events

### PeersFound

Raised when peers are found for a torrent.

```csharp
public event EventHandler<PeersFoundEventArgs> PeersFound;
```

### StateChanged

Raised when the state of the DHT engine changes.

```csharp
public event EventHandler<StateChangedEventArgs> StateChanged;
```

## Methods

### Add(BEncodedDictionary)

Adds a node to the routing table from its encoded representation.

```csharp
public void Add(BEncodedDictionary dict)
```

#### Parameters

- **dict**: The encoded node information.

### Add(Node)

Adds a node to the routing table.

```csharp
public void Add(Node node)
```

#### Parameters

- **node**: The node to add.

### AddNode(IPEndPoint)

Adds a node to the routing table based on its endpoint.

```csharp
public void AddNode(IPEndPoint endpoint)
```

#### Parameters

- **endpoint**: The endpoint of the node to add.

### Add(IEnumerable<Node>)

Adds multiple nodes to the routing table.

```csharp
public void Add(IEnumerable<Node> nodes)
```

#### Parameters

- **nodes**: The nodes to add.

### AnnounceAsync(InfoHash, int)

Announces that the local client has the torrent with the specified info hash.

```csharp
public Task AnnounceAsync(InfoHash infoHash, int port)
```

#### Parameters

- **infoHash**: The info hash of the torrent.
- **port**: The port the client is listening on.

#### Returns

A task representing the asynchronous operation.

### Dispose()

Disposes the DHT engine and releases all resources.

```csharp
public void Dispose()
```

### GetNodes()

Gets a list of all nodes in the routing table.

```csharp
public IEnumerable<Node> GetNodes()
```

#### Returns

A list of all nodes in the routing table.

### GetNodesAsync(NodeId)

Gets nodes that are close to the specified node ID.

```csharp
public Task<IList<Node>> GetNodesAsync(NodeId target)
```

#### Parameters

- **target**: The target node ID.

#### Returns

A task that returns a list of nodes that are close to the specified node ID.

### GetPeersAsync(InfoHash)

Gets peers for the torrent with the specified info hash.

```csharp
public Task<IList<Peer>> GetPeersAsync(InfoHash infoHash)
```

#### Parameters

- **infoHash**: The info hash of the torrent.

#### Returns

A task that returns a list of peers for the specified torrent.

### SaveNodes()

Saves the nodes in the routing table to a BEncoded dictionary.

```csharp
public BEncodedDictionary SaveNodes()
```

#### Returns

A BEncoded dictionary containing the nodes.

### SendQueryAsync(Message, IPEndPoint)

Sends a query message to the specified endpoint.

```csharp
public Task<SendQueryEventArgs> SendQueryAsync(Message query, IPEndPoint endpoint)
```

#### Parameters

- **query**: The query message to send.
- **endpoint**: The endpoint to send the query to.

#### Returns

A task that returns the response to the query.

### Start()

Starts the DHT engine.

```csharp
public void Start()
```

### Stop()

Stops the DHT engine.

```csharp
public void Stop()
```

### WaitForState(DhtState, TimeSpan)

Waits for the DHT engine to reach the specified state.

```csharp
public bool WaitForState(DhtState state, TimeSpan timeout)
```

#### Parameters

- **state**: The state to wait for.
- **timeout**: The maximum time to wait.

#### Returns

`true` if the specified state was reached within the timeout period, `false` otherwise.

## Examples

### Setting Up the DHT Engine

```csharp
// Create a listener for the DHT engine
IPEndPoint endpoint = new IPEndPoint(IPAddress.Any, 55123);
var listener = new DhtListener(endpoint);

// Create the DHT engine
var engine = new DhtEngine(listener);

// Add bootstrap nodes to help join the DHT network
engine.Add(new Node(NodeId.Create(), new IPEndPoint(IPAddress.Parse("router.bittorrent.com"), 6881)));
engine.Add(new Node(NodeId.Create(), new IPEndPoint(IPAddress.Parse("dht.transmissionbt.com"), 6881)));

// Start the DHT engine
engine.Start();

// Wait for the DHT to initialize
bool initialized = engine.WaitForState(DhtState.Ready, TimeSpan.FromMinutes(1));
if (initialized)
{
    Console.WriteLine("DHT engine initialized successfully");
}
else
{
    Console.WriteLine("DHT engine initialization timed out");
}
```

### Finding Peers for a Torrent

```csharp
// Create an info hash for the torrent
byte[] hashData = new byte[20]; // Replace with actual hash data
var infoHash = new InfoHash(hashData);

// Subscribe to the PeersFound event
engine.PeersFound += (sender, e) => 
{
    if (e.InfoHash.Equals(infoHash))
    {
        Console.WriteLine($"Found {e.Peers.Count} peers for torrent {e.InfoHash.ToHex()}");
        
        foreach (var peer in e.Peers)
        {
            Console.WriteLine($"Peer: {peer.ConnectionUri}");
        }
    }
};

// Search for peers
try
{
    var peers = await engine.GetPeersAsync(infoHash);
    Console.WriteLine($"GetPeersAsync returned {peers.Count} peers");
}
catch (Exception ex)
{
    Console.WriteLine($"Error getting peers: {ex.Message}");
}
```

### Announcing a Torrent to the DHT

```csharp
// Announce that we're sharing a torrent
int listeningPort = 55123; // The port your client is listening on
await engine.AnnounceAsync(infoHash, listeningPort);
Console.WriteLine($"Announced torrent {infoHash.ToHex()} to the DHT");
```

### Saving and Loading DHT State

```csharp
// Save the DHT state to a file
void SaveDhtState(DhtEngine engine, string filePath)
{
    var state = engine.SaveNodes();
    using var fileStream = File.Create(filePath);
    using var writer = new BinaryWriter(fileStream);
    var bytes = state.Encode();
    writer.Write(bytes.Length);
    writer.Write(bytes);
}

// Load the DHT state from a file
void LoadDhtState(DhtEngine engine, string filePath)
{
    try
    {
        using var fileStream = File.OpenRead(filePath);
        using var reader = new BinaryReader(fileStream);
        int length = reader.ReadInt32();
        byte[] buffer = reader.ReadBytes(length);
        var dict = (BEncodedDictionary)BEncodedValue.Decode(buffer);
        engine.Add(dict);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error loading DHT state: {ex.Message}");
        // Add default bootstrap nodes as fallback
        engine.Add(new Node(NodeId.Create(), new IPEndPoint(IPAddress.Parse("router.bittorrent.com"), 6881)));
    }
}

// Example usage
string statePath = "dht_state.dat";

// Save on shutdown
SaveDhtState(engine, statePath);

// Load on startup
LoadDhtState(engine, statePath);
```

### Monitoring DHT State

```csharp
// Subscribe to state changes
engine.StateChanged += (sender, e) => 
{
    Console.WriteLine($"DHT state changed: {e.OldState} -> {e.NewState}");
    
    if (e.NewState == DhtState.Ready)
    {
        Console.WriteLine("DHT is now ready to use");
        Console.WriteLine($"Nodes in routing table: {engine.RoutingTable.Count}");
    }
};
```

### Querying Specific Nodes

```csharp
// Send a ping message to a specific node
async Task PingNodeAsync(DhtEngine engine, IPEndPoint endpoint)
{
    try
    {
        var ping = new PingQuery(engine.LocalNodeId);
        var response = await engine.SendQueryAsync(ping, endpoint);
        
        if (response.ResponseMessage != null)
        {
            Console.WriteLine($"Received response from {endpoint}");
            
            // Add the node to our routing table
            var nodeId = response.ResponseMessage.Id;
            engine.Add(new Node(nodeId, endpoint));
        }
        else
        {
            Console.WriteLine($"No response from {endpoint}");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error pinging node: {ex.Message}");
    }
}

// Example usage
var endpoint = new IPEndPoint(IPAddress.Parse("1.2.3.4"), 6881);
await PingNodeAsync(engine, endpoint);
```

## Remarks

- The DHT implementation follows BEP 5 (DHT Protocol) and BEP 32 (IPv6 support).
- The DHT engine needs bootstrap nodes to join the network initially.
- It automatically maintains the routing table based on node interactions.
- The DHT provides a backup mechanism for finding peers when trackers are unavailable.
- It uses UDP for communication, so port forwarding may be required for full participation.
- The `State` property indicates the current state of the DHT:
  - `NotReady`: The DHT is not initialized.
  - `Initializing`: The DHT is bootstrapping into the network.
  - `Ready`: The DHT is operational and can find peers.
  - `Error`: The DHT encountered an error.
- The routing table is a Kademlia-based structure with buckets of nodes organized by their distance to the local node.
- For private torrents, the DHT is typically disabled to prevent unauthorized access.
- The DHT engine uses a token system to prevent unauthorized peer announcements.

## See Also

- [Node](Node.md)
- [NodeId](NodeId.md)
- [RoutingTable](RoutingTable.md)
- [DhtListener](DhtListener.md)
- [InfoHash](../client/InfoHash.md)
- [BEP 5: DHT Protocol](http://www.bittorrent.org/beps/bep_0005.html)