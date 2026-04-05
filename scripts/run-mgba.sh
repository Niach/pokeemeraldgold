#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROM_PATH="$ROOT_DIR/pokeemerald_modern.gba"

if [[ ! -f "$ROM_PATH" ]]; then
  echo "ROM not found: $ROM_PATH" >&2
  echo "Build it first with: make modern -j2" >&2
  exit 1
fi

open -a mGBA "$ROM_PATH"
