Tekla Model Builder
===================

How to build and test `TeklaModelBuilder.cs` inside a Tekla/Windows environment.

Prerequisites
- Windows machine with Tekla Structures installed (compatible version).
- Visual Studio 2019/2022 with .NET Framework 4.8 development tools.

Build steps
1. Open a Developer Command Prompt for Visual Studio.
2. Set the environment variable `TeklaPath` to your Tekla install directory, e.g.:
   ```powershell
   setx TeklaPath "C:\Program Files\Tekla Structures\2021\"
   ```
3. From the `tekla_integration` folder run:
   ```powershell
   msbuild TeklaModelBuilder.csproj /p:Configuration=Release
   ```

Notes
- The project references Tekla assemblies via `$(TeklaPath)\bin\...`. Adjust the `HintPath` in the `.csproj` if your Tekla installation is elsewhere.
- Once built, copy the compiled DLL into Tekla's plugins folder or create a Tekla plugin/extension that calls `TeklaModelBuilder.ImportMembers("path_to_json")`.

Packaging
- After a successful build you can package the DLL for distribution using the provided PowerShell helper. From `tekla_integration` run:
   ```powershell
   .\package_plugin.ps1 -Configuration Release -OutputZip .\TeklaPlugin.zip
   ```

- The script will build the project using `msbuild` (or `dotnet` when available), collect the compiled DLL and create a ZIP suitable for deployment into a Tekla plugin folder. This step requires Windows and Visual Studio/MSBuild.

VS Solution
- A minimal Visual Studio solution file `TeklaModelBuilder.sln` is included as a convenience for opening the project in Visual Studio. Use `File -> Open -> Project/Solution` and select the `.sln` file.
