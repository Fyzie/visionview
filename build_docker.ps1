<#
.SYNOPSIS
    Builds Linux (x86_64) and Linux ARM64 packages using Docker Buildx from Windows.
.USAGE
    .\build_docker.ps1 -Platform linux/amd64
    .\build_docker.ps1 -Platform linux/arm64
    .\build_docker.ps1 -All
#>

param(
    [string]$Platform = "linux/amd64",
    [switch]$All
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required to cross-compile Linux/ARM packages from Windows. Please install Docker Desktop."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if ($All) {
    $Platforms = @("linux/amd64", "linux/arm64")
} else {
    $Platforms = @($Platform)
}

foreach ($p in $Platforms) {
    $tag = if ($p -eq "linux/arm64") { "arm64" } else { "x86_64" }
    $OutDir = "$ScriptDir\dist\docker-$tag"
    Write-Host "`n[*] Compiling VisionView for $p -> $OutDir..." -ForegroundColor Cyan
    docker buildx build --platform $p -f Dockerfile.build -o $OutDir .
    Write-Host "[+] Finished build for $p" -ForegroundColor Green
}
