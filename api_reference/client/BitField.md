# BitField Class

The `BitField` class represents a collection of bits that can be set, cleared, and checked. In MonoTorrent, it's primarily used to track which pieces of a torrent have been downloaded.

**Namespace**: `MonoTorrent`

**Assembly**: `MonoTorrent.dll`

## Syntax

```csharp
public class BitField
```

## Description

The `BitField` class provides an efficient way to store and manipulate a collection of boolean values (bits). In the context of BitTorrent, `BitField` is used to:

- Track which pieces a client has downloaded (in `TorrentManager.Bitfield`)
- Represent which pieces a peer has available (in `PeerId.BitField`)
- Efficiently communicate piece availability between peers (via `BitfieldMessage`)

A `BitField` is backed by an array of bytes, where each bit represents a boolean value. This provides a compact representation that can be easily sent over the network.

## Constructors

### BitField(int)

Creates a new `BitField` with the specified length.

```csharp
public BitField(int length)
```

#### Parameters

- **length**: The number of bits in the `BitField`.

### BitField(bool[])

Creates a new `BitField` from an array of boolean values.

```csharp
public BitField(bool[] array)
```

#### Parameters

- **array**: An array of boolean values to initialize the `BitField` with.

### BitField(BitField)

Creates a new `BitField` that is a copy of the specified `BitField`.

```csharp
public BitField(BitField bitfield)
```

#### Parameters

- **bitfield**: The `BitField` to copy.

### BitField(ReadOnlySpan<byte>, int)

Creates a new `BitField` from a span of bytes.

```csharp
public BitField(ReadOnlySpan<byte> array, int length)
```

#### Parameters

- **array**: The span of bytes containing the bit data.
- **length**: The number of bits in the `BitField`.

## Properties

### AllFalse

Gets a value indicating whether all bits in the `BitField` are `false`.

```csharp
public bool AllFalse { get; }
```

### AllTrue

Gets a value indicating whether all bits in the `BitField` are `true`.

```csharp
public bool AllTrue { get; }
```

### Length

Gets the number of bits in the `BitField`.

```csharp
public int Length { get; }
```

### TrueCount

Gets the number of bits that are `true`.

```csharp
public int TrueCount { get; }
```

### PercentComplete

Gets the percentage of bits that are `true`.

```csharp
public double PercentComplete { get; }
```

### this[int]

Gets or sets the value of the bit at the specified index.

```csharp
public bool this[int index] { get; set; }
```

#### Parameters

- **index**: The zero-based index of the bit to get or set.

## Methods

### And(BitField)

Performs a bitwise AND operation with the specified `BitField`.

```csharp
public void And(BitField value)
```

#### Parameters

- **value**: The `BitField` to AND with.

### Clear()

Sets all bits to `false`.

```csharp
public void Clear()
```

### Clear(int, int)

Sets a range of bits to `false`.

```csharp
public void Clear(int startIndex, int count)
```

#### Parameters

- **startIndex**: The index of the first bit to clear.
- **count**: The number of bits to clear.

### Clone()

Creates a copy of this `BitField`.

```csharp
public BitField Clone()
```

#### Returns

A new `BitField` that is a copy of this `BitField`.

### FirstTrue()

Gets the index of the first bit that is `true`.

```csharp
public int FirstTrue()
```

#### Returns

The index of the first bit that is `true`, or -1 if all bits are `false`.

### FirstFalse()

Gets the index of the first bit that is `false`.

```csharp
public int FirstFalse()
```

#### Returns

The index of the first bit that is `false`, or -1 if all bits are `true`.

### From(bool[])

Creates a new `BitField` from an array of boolean values.

```csharp
public static BitField From(bool[] array)
```

#### Parameters

- **array**: An array of boolean values.

#### Returns

A new `BitField` initialized with the specified values.

### From(BitField)

Creates a new `BitField` from another `BitField`.

```csharp
public static BitField From(BitField bitfield)
```

#### Parameters

- **bitfield**: The `BitField` to copy.

#### Returns

A new `BitField` that is a copy of the specified `BitField`.

### Not()

Inverts all bits in the `BitField`.

```csharp
public void Not()
```

### Or(BitField)

Performs a bitwise OR operation with the specified `BitField`.

```csharp
public void Or(BitField value)
```

#### Parameters

- **value**: The `BitField` to OR with.

### Set(int)

Sets the bit at the specified index to `true`.

```csharp
public void Set(int index)
```

#### Parameters

- **index**: The index of the bit to set.

### Set(int, bool)

Sets the bit at the specified index to the specified value.

```csharp
public void Set(int index, bool value)
```

#### Parameters

- **index**: The index of the bit to set.
- **value**: The value to set the bit to.

### SetAll(bool)

Sets all bits to the specified value.

```csharp
public void SetAll(bool value)
```

#### Parameters

- **value**: The value to set all bits to.

### SetTrue()

Sets all bits to `true`.

```csharp
public void SetTrue()
```

### ToBytes()

Gets the byte array representing the `BitField`.

```csharp
public byte[] ToBytes()
```

#### Returns

A byte array containing the `BitField` data.

### Xor(BitField)

Performs a bitwise XOR operation with the specified `BitField`.

```csharp
public void Xor(BitField value)
```

#### Parameters

- **value**: The `BitField` to XOR with.

## Examples

### Basic BitField Usage

```csharp
// Create a BitField with 10 bits
var bitField = new BitField(10);

// Set some bits
bitField[0] = true;
bitField[3] = true;
bitField[7] = true;

// Check the state of bits
bool hasPieceZero = bitField[0];  // true
bool hasPieceTwo = bitField[2];   // false

// Get the percentage of bits set to true
double percent = bitField.PercentComplete;  // 30.0

// Count how many bits are true
int count = bitField.TrueCount;  // 3

// Find the first true and false bits
int firstTrue = bitField.FirstTrue();   // 0
int firstFalse = bitField.FirstFalse(); // 1
```

### BitField Operations

```csharp
// Create two BitFields
var fieldA = new BitField(8);
var fieldB = new BitField(8);

// Set bits in each field
fieldA[0] = true;
fieldA[1] = true;
fieldA[2] = true;
fieldA[3] = true;

fieldB[2] = true;
fieldB[3] = true;
fieldB[4] = true;
fieldB[5] = true;

// Perform operations
var resultAnd = fieldA.Clone();
resultAnd.And(fieldB);
// resultAnd has bits 2,3 set

var resultOr = fieldA.Clone();
resultOr.Or(fieldB);
// resultOr has bits 0,1,2,3,4,5 set

var resultXor = fieldA.Clone();
resultXor.Xor(fieldB);
// resultXor has bits 0,1,4,5 set

var resultNot = fieldA.Clone();
resultNot.Not();
// resultNot has bits 4,5,6,7 set
```

### Using BitField with Torrent Pieces

```csharp
// BitField that represents which pieces we have downloaded
var bitField = torrentManager.Bitfield;

// Check if we have a specific piece
int pieceIndex = 42;
bool havePiece = bitField[pieceIndex];

// Display download progress
double progress = bitField.PercentComplete;
Console.WriteLine($"Download progress: {progress:F2}%");

// Find the first piece we don't have
int nextPieceToDownload = bitField.FirstFalse();

// Find common pieces with a peer
var peerBitField = peerConnection.BitField;
var commonPieces = bitField.Clone();
commonPieces.And(peerBitField);

// Count how many pieces we share with the peer
int sharedPieces = commonPieces.TrueCount;
```

### Creating a BitField from Bytes

```csharp
// Incoming bitfield message from a peer
byte[] bitfieldData = /* received from peer */;
int pieceCount = torrent.PieceCount;

// Create a BitField from the received data
var peerBitfield = new BitField(bitfieldData, pieceCount);

// Now we can check which pieces the peer has
bool peerHasPieceZero = peerBitfield[0];
int piecesAvailable = peerBitfield.TrueCount;
```

## Remarks

- `BitField` is an essential component in BitTorrent for tracking piece availability.
- It provides an efficient representation of boolean values, using just one bit per value.
- The class includes various bitwise operations (AND, OR, XOR, NOT) that are useful for comparing piece availability between peers.
- When used in `TorrentManager.Bitfield`, it represents the pieces that have been successfully downloaded and verified.
- When used in `PeerId.BitField`, it represents the pieces that a peer has available.
- The `BitField` is sent between peers via the `BitfieldMessage` to communicate which pieces are available.
- Performance is important for `BitField` operations since they are frequently performed during piece selection.

## See Also

- [TorrentManager](TorrentManager.md)
- [PeerId](PeerId.md)
- [BitfieldMessage](../messages/BitfieldMessage.md)