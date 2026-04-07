#!/usr/bin/env python3

import colorsys
import math
import json
import shutil
import struct
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow is optional for the source PNG preview refresh.
    Image = None


ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"
MISSING_REPORT_PATH = ROOT / "data" / "johto_tilesets" / "missing_tiles_report.json"
BUILD_REPORT_PATH = ROOT / "data" / "johto_tilesets" / "atlas_build_report.json"

FIRERED_METATILE_ATTR_MASKS = {
    "behavior": 0x000001FF,
    "layer_type": 0x60000000,
}
FIRERED_METATILE_ATTR_SHIFTS = {
    "behavior": 0,
    "layer_type": 29,
}


def clamp_byte(value: float) -> int:
    return max(0, min(255, int(round(value))))


def transform_rgb(rgb, transform):
    r, g, b = rgb
    if (r, g, b) in ((255, 0, 255), (0, 0, 0)):
        return r, g, b

    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    h = (h + (transform["hue_shift"] / 360.0)) % 1.0
    l = max(0.0, min(1.0, l * transform["lightness_mult"]))
    s = max(0.0, min(1.0, s * transform["saturation_mult"]))
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)

    tint = transform["tint"]
    strength = transform["tint_strength"]
    r3 = r2 * 255.0 * (1.0 - strength) + tint[0] * strength
    g3 = g2 * 255.0 * (1.0 - strength) + tint[1] * strength
    b3 = b2 * 255.0 * (1.0 - strength) + tint[2] * strength
    return clamp_byte(r3), clamp_byte(g3), clamp_byte(b3)


def parse_jasc_pal(path: Path):
    lines = path.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "16"]:
        raise ValueError(f"Unsupported palette format in {path}")
    colors = []
    for line in lines[3:19]:
        parts = [int(part) for part in line.split()]
        if len(parts) != 3:
            raise ValueError(f"Malformed palette row in {path}: {line}")
        colors.append(tuple(parts))
    return colors


def write_jasc_pal(path: Path, colors):
    lines = ["JASC-PAL", "0100", "16"]
    lines.extend(f"{r} {g} {b}" for r, g, b in colors)
    path.write_text("\n".join(lines) + "\n")


def write_gbapal(path: Path, colors):
    encoded = bytearray()
    for r, g, b in colors:
        value = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)
        encoded.extend(struct.pack("<H", value))
    path.write_bytes(encoded)


def transform_palette_file(pal_path: Path, transform):
    colors = parse_jasc_pal(pal_path)
    transformed = [transform_rgb(color, transform) for color in colors]
    write_jasc_pal(pal_path, transformed)
    write_gbapal(pal_path.with_suffix(".gbapal"), transformed)


def refresh_tiles_png(source_png: Path, output_png: Path, transform):
    if Image is None:
        shutil.copy(source_png, output_png)
        return

    with Image.open(source_png) as image:
        if image.mode != "P":
            shutil.copy(source_png, output_png)
            return

        palette = image.getpalette()
        if palette is None:
            shutil.copy(source_png, output_png)
            return

        if transform is None:
            image.copy().save(output_png)
            return

        new_palette = palette[:]
        for index in range(0, len(palette), 3):
            rgb = tuple(palette[index:index + 3])
            if len(rgb) < 3:
                break
            r, g, b = transform_rgb(rgb, transform)
            new_palette[index:index + 3] = [r, g, b]

        recolored = image.copy()
        recolored.putpalette(new_palette)
        recolored.save(output_png)


def resolve_source_root(atlas, source_id: str) -> Path:
    source = atlas["sources"][source_id]
    return Path(source["root"])


def convert_firered_metatile_attributes(input_path: Path, output_path: Path):
    raw = input_path.read_bytes()
    if len(raw) % 4 != 0:
        raise ValueError(f"{input_path}: expected 32-bit FireRed metatile attributes")

    converted = bytearray()
    for (value,) in struct.iter_unpack("<I", raw):
        behavior = (value & FIRERED_METATILE_ATTR_MASKS["behavior"]) >> FIRERED_METATILE_ATTR_SHIFTS["behavior"]
        layer_type = (value & FIRERED_METATILE_ATTR_MASKS["layer_type"]) >> FIRERED_METATILE_ATTR_SHIFTS["layer_type"]
        if behavior > 0xFF:
            raise ValueError(f"{input_path}: behavior {behavior:#x} does not fit Emerald attribute format")
        converted_value = behavior | (layer_type << 12)
        converted.extend(struct.pack("<H", converted_value))

    output_path.write_bytes(converted)


def ensure_gbapals(output_dir: Path):
    for pal_path in sorted((output_dir / "palettes").glob("*.pal")):
        colors = parse_jasc_pal(pal_path)
        write_gbapal(pal_path.with_suffix(".gbapal"), colors)


def expected_tile_count(family, candidate):
    return family.get("runtime_tile_count", candidate["tile_count"])


def remove_prebuilt_tile_binaries(output_dir: Path):
    for filename in ("tiles.4bpp", "tiles.4bpp.lz"):
        path = output_dir / filename
        if path.exists():
            path.unlink()


def pad_tiles_png(output_png: Path, expected_count: int):
    if Image is None:
        raise RuntimeError(
            f"Pillow is required to pad {output_png} to {expected_count} tiles for mixed-source tilesets"
        )

    with Image.open(output_png) as image:
        if image.mode != "P":
            raise ValueError(f"{output_png}: expected paletted PNG tileset")

        width, height = image.size
        if width % 8 != 0 or height % 8 != 0:
            raise ValueError(f"{output_png}: expected 8x8-aligned tileset image")

        tiles_per_row = width // 8
        current_count = tiles_per_row * (height // 8)
        if current_count >= expected_count:
            return current_count

        new_rows = math.ceil(expected_count / tiles_per_row)
        padded = Image.new("P", (width, new_rows * 8), 0)
        palette = image.getpalette()
        if palette is not None:
            padded.putpalette(palette)
        padded.paste(image, (0, 0))
        padded.save(output_png)
        return expected_count


def copy_family(family, candidate, atlas, output_dir: Path):
    source_root = resolve_source_root(atlas, candidate["source"])
    source_dir = source_root / candidate["source_dir"]
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Missing source tileset directory: {source_dir}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(source_dir, output_dir)

    if candidate["attribute_mode"] == "firered":
        convert_firered_metatile_attributes(
            source_dir / "metatile_attributes.bin",
            output_dir / "metatile_attributes.bin",
        )

    transform = candidate.get("transform")
    if transform is not None:
        for pal_path in sorted((output_dir / "palettes").glob("*.pal")):
            transform_palette_file(pal_path, transform)
    else:
        ensure_gbapals(output_dir)

    refresh_tiles_png(source_dir / "tiles.png", output_dir / "tiles.png", transform)
    actual_count = pad_tiles_png(output_dir / "tiles.png", expected_tile_count(family, candidate))
    remove_prebuilt_tile_binaries(output_dir)
    return actual_count


def build_family(family, atlas):
    if not family.get("managed", True):
        return None

    candidates = {candidate["id"]: candidate for candidate in family["candidates"]}
    selected = candidates[family["selected_candidate"]]
    output_dir = ROOT / family["runtime_dir"]
    tile_count = copy_family(family, selected, atlas, output_dir)
    return {
        "family": family["id"],
        "symbol": family["symbol"],
        "selected_candidate": selected["id"],
        "runtime_dir": family["runtime_dir"],
        "source": selected["source"],
        "source_dir": selected["source_dir"],
        "paired_primary_family": family.get("paired_primary_family"),
        "runtime_tile_count": expected_tile_count(family, selected),
        "output_tile_count": tile_count,
    }


def write_reports(atlas, build_report):
    missing_semantic_tiles = [
        {
            "id": tile["id"],
            "family": tile["family"],
            "status": tile["status"],
        }
        for tile in atlas["semantic_tiles"]
        if tile["status"] != "mapped"
    ]
    MISSING_REPORT_PATH.write_text(json.dumps({
        "missing_semantic_tiles": missing_semantic_tiles,
        "missing_count": len(missing_semantic_tiles),
    }, indent=2) + "\n")

    BUILD_REPORT_PATH.write_text(json.dumps({
        "managed_families": build_report,
        "managed_family_count": len(build_report),
    }, indent=2) + "\n")


def main():
    atlas = json.loads(ATLAS_PATH.read_text())
    build_report = []
    for family in atlas["families"]:
        result = build_family(family, atlas)
        if result is not None:
            build_report.append(result)
            print(f"updated {result['runtime_dir']} from {result['source']}:{result['source_dir']}")

    write_reports(atlas, build_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
