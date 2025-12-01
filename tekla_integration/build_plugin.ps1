param(
    [string]$Configuration = "Release"
)

if (-not $Env:TeklaPath) {
    Write-Host "Environment variable TeklaPath is not set. Set TeklaPath to your Tekla install directory before running this script. Example:"
    Write-Host "  $env:TeklaPath = 'C:\\Program Files\\Tekla Structures\\2021'"
    exit 2
}

$proj = Join-Path $PSScriptRoot "TeklaModelBuilder.csproj"
Write-Host "Building $proj (Configuration=$Configuration) using TeklaPath=$Env:TeklaPath"
& msbuild.exe $proj /p:Configuration=$Configuration
if ($LASTEXITCODE -ne 0) {
    Write-Host "msbuild failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}
Write-Host "Build completed. Copy the resulting DLL into Tekla plugins folder or load into a Tekla plugin project."
