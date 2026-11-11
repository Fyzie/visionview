#!/usr/bin/env bash
# ==============================================================================
# VisionView - Automated Standalone Build Script for Linux & Linux ARM
# Targets:
#   - Linux x86_64 (Ubuntu / Debian / CentOS / Fedora)
#   - Linux ARM64 (aarch64, Raspberry Pi 4/5 64-bit, NVIDIA Jetson Nano/Orin)
#   - Linux ARM32 (armv7l)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ARCH="$(uname -m)"
OS="$(uname -s)"

echo "=========================================================="
echo " VisionView Standalone Compiler for Linux & ARM"
echo " Host OS:       $OS"
echo " Architecture:  $ARCH"
echo "=========================================================="

# 1. Check Python installation
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[!] Error: Python 3 is not installed. Please install python3."
    exit 1
fi

echo "[*] Using Python: $($PYTHON_CMD --version)"

# 2. Check for optional apt package dependencies (if on Debian/Ubuntu/Raspbian)
if command -v apt-get >/dev/null 2>&1 && [ "$EUID" -eq 0 ]; then
    echo "[*] Ensuring required Qt/OpenGL system libraries are installed..."
    apt-get update -y && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libegl1 \
        libxkbcommon-x11-0 \
        libfontconfig1 \
        libdbus-1-3 \
        build-essential
fi

# 3. Create or check virtual environment if requested/needed
if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_PREFIX" ]; then
    VENV_DIR="$SCRIPT_DIR/.build_venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo "[*] Creating build virtual environment at $VENV_DIR..."
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi
    echo "[*] Activating build virtual environment..."
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python"
fi

# 4. Install dependencies
echo "[*] Verifying Python package dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

# 5. Run build.py
echo "[*] Compiling standalone executable..."
$PYTHON_CMD build.py "$@"

echo ""
echo "=========================================================="
echo "[SUCCESS] Build finished!"
echo "Distribution directory: $SCRIPT_DIR/dist/VisionView"
echo "To run the application: $SCRIPT_DIR/dist/VisionView/VisionView"
echo "=========================================================="
