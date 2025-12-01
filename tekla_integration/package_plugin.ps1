param(
    [string]$Configuration = "Release",
    [string]$OutputZip = "./TeklaPlugin.zip"
)

# Simple packaging script: build project and zip DLL
$proj = "TeklaModelBuilder.csproj"
if (-not (Test-Path $proj)) {
    Write-Error "Project file $proj not found in current directory"
    exit 2
}

Write-Output "Building $proj (Configuration=$Configuration)"
# Prefer msbuild if present
if (Get-Command msbuild -ErrorAction SilentlyContinue) {
    msbuild $proj /p:Configuration=$Configuration | Write-Output
} elseif (Get-Command dotnet -ErrorAction SilentlyContinue) {
    dotnet build $proj -c $Configuration | Write-Output
} else {
    Write-Error "Neither msbuild nor dotnet found in PATH. Install Visual Studio/MSBuild or dotnet SDK."
    exit 3
}

# Find output DLL
$bin = Join-Path -Path (Get-Location) -ChildPath "bin\$Configuration"
$dll = Get-ChildItem -Path $bin -Filter "*.dll" -Recurse | Select-Object -First 1
if (-not $dll) {
    Write-Error "Built DLL not found under $bin"
    exit 4
}

Write-Output "Packaging $($dll.FullName) -> $OutputZip"
if (Test-Path $OutputZip) { Remove-Item $OutputZip }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory((Split-Path $dll.FullName -Parent), $OutputZip)
Write-Output "Packaged plugin zip: $OutputZip"
