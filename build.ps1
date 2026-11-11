<#
.SYNOPSIS
    Automated Standalone Application Compiler for VisionView (Windows).
.DESCRIPTION
    Zero-configuration, self-provisioning build script. Automatically locates
    Python or installs it via winget, creates an isolated virtual environment
    (.build_venv), downloads all dependencies from requirements.txt, and
    compiles VisionView into a standalone executable.
.USAGE
    .\build.ps1
    .\build.ps1 -Clean
#>

[CmdletBinding()]
param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " VisionView Automated Standalone Compiler for Windows" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Locate Python Interpreter
$PYTHON_EXE = $null

if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PYTHON_EXE = (Get-Command python).Source
    Write-Host "[+] Found System Python: $PYTHON_EXE" -ForegroundColor Green
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PYTHON_EXE = "py"
    Write-Host "[+] Found Python Launcher: py" -ForegroundColor Green
} else {
    $commonPaths = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*" -ErrorAction SilentlyContinue
    foreach ($p in $commonPaths) {
        $candidate = Join-Path $p.FullName "python.exe"
        if (Test-Path $candidate) {
            $PYTHON_EXE = $candidate
            Write-Host "[+] Found Python at: $PYTHON_EXE" -ForegroundColor Green
            break
        }
    }
}

# 2. Automatically install Python via winget if absent
if (-not $PYTHON_EXE) {
    Write-Host "[!] Python was not detected on this machine." -ForegroundColor Yellow
    if (Get-Command "winget" -ErrorAction SilentlyContinue) {
        Write-Host "[*] Automatically installing Python 3.10 via winget..." -ForegroundColor Cyan
        winget install --id Python.Python.3.10 -e --accept-source-agreements --accept-package-agreements
        if (Get-Command "python" -ErrorAction SilentlyContinue) {
            $PYTHON_EXE = (Get-Command python).Source
        }
    }
}

if (-not $PYTHON_EXE) {
    Write-Error "Python 3.10+ is required to build VisionView. Please install Python from https://www.python.org/downloads/"
}

# 3. Automated Virtual Environment & Dependency Installation
$VENV_PYTHON = "$ScriptDir\.build_venv\Scripts\python.exe"

if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "[*] Creating isolated automated build environment (.build_venv)..." -ForegroundColor Cyan
    & $PYTHON_EXE -m venv "$ScriptDir\.build_venv"
}

Write-Host "[*] Checking and automatically downloading dependencies from requirements.txt..." -ForegroundColor Cyan
& $VENV_PYTHON -m pip install --upgrade pip
& $VENV_PYTHON -m pip install -r "$ScriptDir\requirements.txt"
& $VENV_PYTHON -m pip install pyinstaller

# 4. Compile Standalone Application
$BuildArgs = @("build.py")
if ($Clean) {
    $BuildArgs += "--clean"
}

Write-Host "`n[*] Starting compilation..." -ForegroundColor Green
& $VENV_PYTHON @BuildArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Standalone Application compiled successfully!" -ForegroundColor Green
    Write-Host "Folder:  $ScriptDir\dist\VisionView" -ForegroundColor White
    Write-Host "Archive: $ScriptDir\dist\VisionView-windows-x64.zip" -ForegroundColor White
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Error "Build failed with exit code $LASTEXITCODE."
}
