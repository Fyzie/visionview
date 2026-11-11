#!/usr/bin/env bash
# ==============================================================================
# Cross-compile VisionView for Linux x86_64 and ARM64 using Docker Buildx
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker is not installed or not in PATH."
    exit 1
fi

TARGET="${1:-all}"

build_target() {
    local platform="$1"
    local tag="$2"
    local out_dir="$SCRIPT_DIR/dist/docker-$tag"
    echo "=========================================================="
    echo " Building VisionView for $platform -> $out_dir"
    echo "=========================================================="
    docker buildx build --platform "$platform" -f Dockerfile.build -o "$out_dir" .
    echo "[SUCCESS] Finished build for $platform"
}

if [ "$TARGET" = "arm64" ] || [ "$TARGET" = "linux/arm64" ]; then
    build_target "linux/arm64" "arm64"
elif [ "$TARGET" = "amd64" ] || [ "$TARGET" = "x86_64" ] || [ "$TARGET" = "linux/amd64" ]; then
    build_target "linux/amd64" "x86_64"
else
    build_target "linux/amd64" "x86_64"
    build_target "linux/arm64" "arm64"
fi
