#!/usr/bin/env python3

try:
    from crystal_room_tilesets import generate_exact_runtime_tilesets
except ModuleNotFoundError:
    from scripts.crystal_room_tilesets import generate_exact_runtime_tilesets


def main():
    for report in generate_exact_runtime_tilesets():
        family_id = report["family_id"]
        runtime_dir = report["runtime_dir"]
        tile_count = report["tile_count"]
        metatile_count = report["metatile_count"]
        source_tileset = report.get("source_tileset", family_id)
        print(
            "generated "
            f"{family_id} "
            f"from {source_tileset} "
            f"at {runtime_dir} "
            f"({tile_count} tiles, {metatile_count} metatiles)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
