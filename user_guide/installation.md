# Installing MonoTorrent

This guide covers how to install MonoTorrent in your .NET projects.

## Prerequisites

- .NET 6.0 or later
- NuGet package manager

## Installation Methods

### Using NuGet Package Manager Console

The easiest way to install MonoTorrent is through the NuGet Package Manager console:

```powershell
Install-Package MonoTorrent
```

### Using .NET CLI

You can also install MonoTorrent using the .NET CLI:

```bash
dotnet add package MonoTorrent
```

### Using PackageReference in .csproj

Add a reference to MonoTorrent in your project file:

```xml
<ItemGroup>
    <PackageReference Include="MonoTorrent" Version="2.0.x" />
</ItemGroup>
```

Replace `2.0.x` with the latest version or a specific version you want to use.

## Verifying Installation

To verify that MonoTorrent has been installed correctly, you can add a simple reference to the library in your code:

```csharp
using MonoTorrent;
using MonoTorrent.Client;

// If this compiles, MonoTorrent is installed correctly
ClientEngine engine = new ClientEngine(new EngineSettings());
```

## Additional Packages

MonoTorrent is modular and has several packages for different functionalities:

- **MonoTorrent.Client**: Core BitTorrent client functionality
- **MonoTorrent.Dht**: DHT implementation for trackerless torrents
- **MonoTorrent.PieceWriter**: Provides different strategies for writing pieces to disk
- **MonoTorrent.Trackers**: Support for different tracker protocols

While the main MonoTorrent package includes all these components, you can install them individually if you only need specific functionality.

## Building from Source

If you need the latest features or want to contribute to MonoTorrent, you can build it from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/alanmcgovern/monotorrent.git
   ```

2. Navigate to the repository directory:
   ```bash
   cd monotorrent
   ```

3. Build the solution:
   ```bash
   dotnet build
   ```

4. Run the tests to ensure everything is working correctly:
   ```bash
   dotnet test
   ```

## Compatibility

MonoTorrent is compatible with:

- .NET 6.0+
- .NET Framework 4.6.2+ (older versions)
- Mono 5.0+
- Unity 2018.1+ (with .NET 4.x scripting runtime)

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Ensure you have the correct .NET version installed.
2. **Firewall issues**: MonoTorrent requires network access, so ensure your firewall allows it.
3. **Version conflicts**: If you're using other libraries that depend on different versions of MonoTorrent's dependencies, you may need to add binding redirects.

### Getting Help

If you encounter issues installing MonoTorrent, you can:

- Check the [GitHub issues](https://github.com/alanmcgovern/monotorrent/issues) for similar problems
- Open a new issue if your problem hasn't been reported
- Reach out to the community through GitHub discussions