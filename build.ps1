<#
.SYNOPSIS
    Automated Standalone Application Compiler for VisionView (Windows).
.DESCRIPTION
    Zero-configuration build script. Automatically locates Python or creates
    a dedicated virtual environment, downloads missing dependencies from
    requirements.txt, and compiles VisionView into a standalone executable.
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

# 1. Detect Python Interpreter
$PYTHON_EXE = $null

$CONDA_CANDIDATES = @(
    "$env:USERPROFILE\miniconda3\envs\rfdetr-1.6\python.exe",
    "$env:USERPROFILE\anaconda3\envs\rfdetr-1.6\python.exe"
)

foreach ($c in $CONDA_CANDIDATES) {
    if (Test-Path $c) {
        $PYTHON_EXE = $c
        Write-Host "[+] Found Anaconda environment: $c" -ForegroundColor Green
        break
    }
}

if (-not $PYTHON_EXE) {
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        $PYTHON_EXE = (Get-Command python).Source
        Write-Host "[+] Found System Python: $PYTHON_EXE" -ForegroundColor Green
    } elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
        $PYTHON_EXE = "py"
        Write-Host "[+] Found Python Launcher: py" -ForegroundColor Green
    }
}

# 2. Attempt winget auto-install if Python is completely absent
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
    Write-Error "Python 3.10+ is required. Please install Python from https://www.python.org/downloads/"
}

# 3. Automated Virtual Environment & Dependency Installation
$isConda = $PYTHON_EXE -match "envs\\rfdetr"

if (-not $isConda) {
    $VENV_PYTHON = "$ScriptDir\.build_venv\Scripts\python.exe"
    if (-not (Test-Path $VENV_PYTHON)) {
        Write-Host "[*] Creating automated isolated virtual environment (.build_venv)..." -ForegroundColor Cyan
        & $PYTHON_EXE -m venv "$ScriptDir\.build_venv"
    }
    $PYTHON_EXE = $VENV_PYTHON
    
    Write-Host "[*] Checking and automatically downloading dependencies from requirements.txt..." -ForegroundColor Cyan
    & $PYTHON_EXE -m pip install --upgrade pip
    & $PYTHON_EXE -m pip install -r "$ScriptDir\requirements.txt"
    & $PYTHON_EXE -m pip install pyinstaller
} else {
    Write-Host "[*] Checking build tools in rfdetr-1.6 environment..." -ForegroundColor Cyan
    & $PYTHON_EXE -m pip install -q pyinstaller
}

# 4. Compile Standalone Application
$BuildArgs = @("build.py")
if ($Clean) {
    $BuildArgs += "--clean"
}

Write-Host "`n[*] Starting compilation..." -ForegroundColor Green
& $PYTHON_EXE @BuildArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Standalone Application compiled successfully!" -ForegroundColor Green
    Write-Host "Folder:  $ScriptDir\dist\VisionView" -ForegroundColor White
    Write-Host "Archive: $ScriptDir\dist\VisionView-windows-x64.zip" -ForegroundColor White
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Error "Build failed with exit code $LASTEXITCODE."
}
