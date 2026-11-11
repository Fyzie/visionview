@echo off
setlocal enabledelayedexpansion
title VisionView Automated Standalone Compiler

echo ==========================================================
echo  VisionView Automated Standalone Compiler for Windows
echo ==========================================================

REM 1. Locate any Python 3 interpreter on the host system
set PYTHON_EXE=

REM Check if python is in PATH
where python >nul 2>nul
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('where python') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
    echo [+] Detected System Python: !PYTHON_EXE!
)

REM Check Windows Python launcher (py)
if not defined PYTHON_EXE (
    where py >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py"
        echo [+] Detected Python Launcher: py
    )
)

REM Check common Python install locations
if not defined PYTHON_EXE (
    for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%d\python.exe" (
            set "PYTHON_EXE=%%d\python.exe"
            echo [+] Found Python at: !PYTHON_EXE!
        )
    )
)

REM 2. If Python is still not found, automatically install via winget
if not defined PYTHON_EXE (
    echo [!] Python was not detected on this machine.
    echo [*] Automatically installing Python 3.10 via Windows Package Manager (winget)...
    where winget >nul 2>nul
    if !errorlevel! equ 0 (
        winget install --id Python.Python.3.10 -e --accept-source-agreements --accept-package-agreements
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=python"
        )
    )
)

if not defined PYTHON_EXE (
    echo.
    echo [ERROR] Python 3.10+ is required to build VisionView.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 3. Automated Virtual Environment & Dependency Installation
if not exist ".build_venv\Scripts\python.exe" (
    echo [*] Creating isolated build virtual environment (.build_venv)...
    "%PYTHON_EXE%" -m venv .build_venv
)

set "VENV_PYTHON=.build_venv\Scripts\python.exe"

echo [*] Automatically checking and downloading required packages from requirements.txt...
"%VENV_PYTHON%" -m pip install --upgrade pip
"%VENV_PYTHON%" -m pip install -r requirements.txt
"%VENV_PYTHON%" -m pip install pyinstaller

REM 4. Execute compilation
echo.
echo [*] Compiling VisionView into standalone application...
"%VENV_PYTHON%" build.py %*

if !errorlevel! equ 0 (
    echo.
    echo ==========================================================
    echo [SUCCESS] VisionView built successfully!
    echo Application folder: dist\VisionView\
    echo Distribution ZIP:  dist\VisionView-windows-x64.zip
    echo ==========================================================
) else (
    echo.
    echo [ERROR] Build failed with exit code !errorlevel!.
)

pause
