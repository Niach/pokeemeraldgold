#!/usr/bin/env python3

try:
    from generate_crystal_tilesets import main
except ModuleNotFoundError:
    from scripts.generate_crystal_tilesets import main


if __name__ == "__main__":
    raise SystemExit(main())
