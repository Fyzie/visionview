@echo off
setlocal enabledelayedexpansion
title VisionView Automated Standalone Compiler

echo ==========================================================
echo  VisionView Standalone Compiler for Windows
echo ==========================================================

REM 1. Locate Python interpreter
set PYTHON_EXE=

REM Check Conda environments (rfdetr-1.6)
if exist "%USERPROFILE%\miniconda3\envs\rfdetr-1.6\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\miniconda3\envs\rfdetr-1.6\python.exe"
    echo [+] Detected Anaconda environment: rfdetr-1.6
) else if exist "%USERPROFILE%\anaconda3\envs\rfdetr-1.6\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\anaconda3\envs\rfdetr-1.6\python.exe"
    echo [+] Detected Anaconda environment: rfdetr-1.6
) else (
    REM Check system PATH python
    where python >nul 2>nul
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('where python') do (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
        )
        echo [+] Detected System Python: !PYTHON_EXE!
    ) else (
        REM Check Windows Python launcher (py)
        where py >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=py"
            echo [+] Detected Python Launcher: py
        )
    )
)

REM 2. If Python is still not found, attempt auto-install via winget
if not defined PYTHON_EXE (
    echo [!] Python is not installed or not in PATH.
    echo [*] Attempting automated installation via Windows Package Manager (winget)...
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
    echo [ERROR] Python 3.10+ is required to compile VisionView.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 3. Automated Dependency Download & Environment Setup
set IS_CONDA=0
echo !PYTHON_EXE! | findstr /i "envs\rfdetr" >nul
if !errorlevel! equ 0 set IS_CONDA=1

if "!IS_CONDA!"=="0" (
    if not exist ".build_venv\Scripts\python.exe" (
        echo [*] Setting up isolated automated build environment (.build_venv)...
        "%PYTHON_EXE%" -m venv .build_venv
    )
    set "PYTHON_EXE=.build_venv\Scripts\python.exe"
    echo [*] Checking and automatically downloading required packages from requirements.txt...
    "%PYTHON_EXE%" -m pip install --upgrade pip
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    "%PYTHON_EXE%" -m pip install pyinstaller
) else (
    echo [*] Verifying PyInstaller in rfdetr-1.6...
    "%PYTHON_EXE%" -m pip install -q pyinstaller
)

REM 4. Execute compilation
echo.
echo [*] Compiling VisionView into standalone application...
"%PYTHON_EXE%" build.py %*

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
