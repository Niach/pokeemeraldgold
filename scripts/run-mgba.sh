#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROM_PATH="$ROOT_DIR/pokeemerald_modern.gba"

echo "Building ROM with make modern -j2..."
make -C "$ROOT_DIR" modern -j2

open -a mGBA "$ROM_PATH"
