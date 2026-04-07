#!/usr/bin/env python3

import json
import math
import struct
from functools import lru_cache
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit("Pillow is required for Johto preview rendering") from exc


ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"
LAYOUTS_PATH = ROOT / "data" / "layouts" / "layouts.json"
PREVIEW_ROOT = ROOT / "data" / "johto_tilesets" / "previews"

MAPGRID_METATILE_ID_MASK = 0x03FF
NUM_METATILES_IN_PRIMARY = 512
SECONDARY_PALETTE_START = 6
RUNTIME_VIEW_WIDTH = 15
RUNTIME_VIEW_HEIGHT = 10

COLOR_OBJECT = (255, 72, 72, 220)
COLOR_WARP = (80, 148, 255, 220)
COLOR_BG = (255, 210, 72, 220)


def load_json(path: Path):
    return json.loads(path.read_text())


def build_family_lookup(atlas):
    families = {family["id"]: family for family in atlas["families"]}
    by_symbol = {}
    for family in atlas["families"]:
        by_symbol[family["symbol"]] = family
    for alias in atlas.get("aliases", []):
        by_symbol[alias["symbol"]] = families[alias["family"]]
    return families, by_symbol


def parse_jasc_pal(path: Path):
    lines = path.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "16"]:
        raise ValueError(f"Unsupported palette format in {path}")
    colors = []
    for line in lines[3:19]:
        colors.append(tuple(int(part) for part in line.split()))
    return tuple(colors)


@lru_cache(maxsize=None)
def load_tile_bank(tiles_png: str):
    path = Path(tiles_png)
    with Image.open(path) as image:
        if image.mode != "P":
            image = image.convert("P")
        width, height = image.size
        tiles = []
        for tile_y in range(0, height, 8):
            for tile_x in range(0, width, 8):
                crop = image.crop((tile_x, tile_y, tile_x + 8, tile_y + 8))
                tiles.append(tuple(crop.getdata()))
        return tuple(tiles)


@lru_cache(maxsize=None)
def load_metatile_table(metatiles_path: str):
    raw = Path(metatiles_path).read_bytes()
    if len(raw) % 16 != 0:
        raise ValueError(f"{metatiles_path}: expected metatiles.bin to be a multiple of 16 bytes")
    words = struct.unpack("<" + "H" * (len(raw) // 2), raw)
    return tuple(tuple(words[index:index + 8]) for index in range(0, len(words), 8))


@lru_cache(maxsize=None)
def load_palette_bank(palettes_dir: str):
    path = Path(palettes_dir)
    palettes = []
    for pal_path in sorted(path.glob("*.pal")):
        palettes.append(parse_jasc_pal(pal_path))
    return tuple(palettes)


def decode_bg_tile(word: int):
    return {
        "tile_index": word & 0x03FF,
        "hflip": bool(word & 0x0400),
        "vflip": bool(word & 0x0800),
        "palette": (word >> 12) & 0xF,
    }


def placeholder_tile():
    tile = Image.new("RGBA", (8, 8), (255, 0, 255, 255))
    draw = ImageDraw.Draw(tile)
    draw.line((0, 0, 7, 7), fill=(0, 0, 0, 255))
    draw.line((0, 7, 7, 0), fill=(0, 0, 0, 255))
    return tile


PLACEHOLDER_TILE = placeholder_tile()


@lru_cache(maxsize=None)
def render_index_tile(tiles_png: str, local_tile_index: int, palette: tuple[tuple[int, int, int], ...], hflip: bool, vflip: bool):
    tiles = load_tile_bank(tiles_png)
    if local_tile_index >= len(tiles):
        return PLACEHOLDER_TILE

    rgba = Image.new("RGBA", (8, 8))
    rgba.putdata([
        (0, 0, 0, 0) if value == 0 else (*palette[min(value, len(palette) - 1)], 255)
        for value in tiles[local_tile_index]
    ])

    if hflip:
        rgba = rgba.transpose(Image.FLIP_LEFT_RIGHT)
    if vflip:
        rgba = rgba.transpose(Image.FLIP_TOP_BOTTOM)
    return rgba


def resolve_bg_palette(primary_assets, secondary_assets, palette_index: int):
    primary_palettes = primary_assets["palettes"]
    secondary_palettes = secondary_assets["palettes"] if secondary_assets is not None else ()

    if secondary_assets is not None and palette_index >= SECONDARY_PALETTE_START and palette_index < len(secondary_palettes):
        return secondary_palettes[palette_index]
    if palette_index < len(primary_palettes):
        return primary_palettes[palette_index]
    if secondary_assets is not None and palette_index < len(secondary_palettes):
        return secondary_palettes[palette_index]
    if primary_palettes:
        return primary_palettes[min(palette_index, len(primary_palettes) - 1)]
    if secondary_palettes:
        return secondary_palettes[min(palette_index, len(secondary_palettes) - 1)]
    return ((255, 0, 255),) * 16


def runtime_backdrop(primary_assets, secondary_assets):
    palette = resolve_bg_palette(primary_assets, secondary_assets, 0)
    return (*palette[0], 255)


def compose_metatile(tile_words, primary_assets, secondary_assets=None):
    image = Image.new("RGBA", (16, 16), runtime_backdrop(primary_assets, secondary_assets))
    positions = (
        (0, 0), (8, 0), (0, 8), (8, 8),
        (0, 0), (8, 0), (0, 8), (8, 8),
    )
    for index, word in enumerate(tile_words):
        tile_info = decode_bg_tile(word)
        assets = primary_assets
        local_tile_index = tile_info["tile_index"]
        if secondary_assets is not None and tile_info["tile_index"] >= NUM_METATILES_IN_PRIMARY:
            assets = secondary_assets
            local_tile_index = tile_info["tile_index"] - NUM_METATILES_IN_PRIMARY
        tile_image = render_index_tile(
            assets["tiles_png"],
            local_tile_index,
            resolve_bg_palette(primary_assets, secondary_assets, tile_info["palette"]),
            tile_info["hflip"],
            tile_info["vflip"],
        )
        image.alpha_composite(tile_image, positions[index])
    return image


def family_runtime_dir(family):
    return ROOT / family["runtime_dir"]


def family_tileset_assets(family):
    runtime_dir = family_runtime_dir(family)
    return {
        "tiles_png": str(runtime_dir / "tiles.png"),
        "palettes": load_palette_bank(str(runtime_dir / "palettes")),
        "metatiles": load_metatile_table(str(runtime_dir / "metatiles.bin")),
    }


def family_metatile_sheet(family, families):
    paired_primary = families.get(family.get("paired_primary_family"), family)
    primary_assets = family_tileset_assets(paired_primary)
    secondary_assets = family_tileset_assets(family) if family["id"] != paired_primary["id"] else None
    metatiles = family_tileset_assets(family)["metatiles"]
    return render_metatile_sheet(
        [compose_metatile(tile_words, primary_assets, secondary_assets) for tile_words in metatiles],
        title=family["id"],
    )


def render_metatile_sheet(images, title):
    font = ImageFont.load_default()
    columns = 8
    rows = max(1, math.ceil(len(images) / columns))
    cell_width = 60
    cell_height = 38
    sheet = Image.new("RGBA", (columns * cell_width, rows * cell_height + 18), (244, 246, 242, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((4, 4), title, fill=(28, 32, 28, 255), font=font)

    for index, image in enumerate(images):
        column = index % columns
        row = index // columns
        x = column * cell_width + 4
        y = row * cell_height + 18
        sheet.alpha_composite(image, (x, y))
        draw.text((x + 20, y + 2), f"{index:03X}", fill=(46, 54, 46, 255), font=font)

    return sheet


def semantic_tile_sheet(atlas, families):
    rendered = []
    labels = []
    for tile in sorted(atlas["semantic_tiles"], key=lambda item: item["id"]):
        family = families[tile["family"]]
        paired_primary = families.get(family.get("paired_primary_family"), family)
        primary_assets = family_tileset_assets(paired_primary)
        secondary_assets = family_tileset_assets(family) if family["id"] != paired_primary["id"] else None
        metatiles = family_tileset_assets(family)["metatiles"]
        entry = int(tile["entry"], 16) & MAPGRID_METATILE_ID_MASK
        if entry < NUM_METATILES_IN_PRIMARY:
            metatile_index = entry
            primary_metatiles = primary_assets["metatiles"]
            tile_words = primary_metatiles[metatile_index]
        else:
            metatile_index = entry - NUM_METATILES_IN_PRIMARY
            if metatile_index >= len(metatiles):
                tile_words = None
            else:
                tile_words = metatiles[metatile_index]

        if tile_words is None:
            rendered.append(Image.new("RGBA", (16, 16), (255, 0, 255, 255)))
        else:
            rendered.append(compose_metatile(tile_words, primary_assets, secondary_assets))
        labels.append(tile["id"])

    font = ImageFont.load_default()
    columns = 4
    cell_width = 190
    cell_height = 26
    rows = max(1, math.ceil(len(rendered) / columns))
    sheet = Image.new("RGBA", (columns * cell_width, rows * cell_height + 18), (244, 246, 242, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((4, 4), "semantic_tiles", fill=(28, 32, 28, 255), font=font)

    for index, image in enumerate(rendered):
        column = index % columns
        row = index // columns
        x = column * cell_width + 4
        y = row * cell_height + 18
        sheet.alpha_composite(image, (x, y))
        draw.text((24, y + 2), labels[index], fill=(40, 44, 40, 255), font=font)

    return sheet


def resolve_layout_lookup():
    layouts = load_json(LAYOUTS_PATH)["layouts"]
    return {layout["id"]: layout for layout in layouts}


def render_map_preview(map_path: Path, layout_lookup, symbol_lookup, overlay_objects: bool):
    map_data = load_json(map_path)
    layout = layout_lookup[map_data["layout"]]
    primary_family = symbol_lookup[layout["primary_tileset"]]
    secondary_family = symbol_lookup[layout["secondary_tileset"]]
    primary_assets = family_tileset_assets(primary_family)
    secondary_assets = family_tileset_assets(secondary_family)
    primary_metatiles = primary_assets["metatiles"]
    secondary_metatiles = secondary_assets["metatiles"]

    blockdata_path = ROOT / layout["blockdata_filepath"]
    raw = blockdata_path.read_bytes()
    values = struct.unpack("<" + "H" * (len(raw) // 2), raw)
    width = layout["width"]
    height = layout["height"]

    preview = Image.new("RGBA", (width * 16, height * 16), runtime_backdrop(primary_assets, secondary_assets))
    for y in range(height):
        for x in range(width):
            entry = values[y * width + x]
            metatile_id = entry & MAPGRID_METATILE_ID_MASK
            if metatile_id < NUM_METATILES_IN_PRIMARY:
                tile_words = primary_metatiles[metatile_id]
            else:
                tile_words = secondary_metatiles[metatile_id - NUM_METATILES_IN_PRIMARY]
            preview.alpha_composite(compose_metatile(tile_words, primary_assets, secondary_assets), (x * 16, y * 16))

    draw = ImageDraw.Draw(preview)
    for event in map_data.get("warp_events", []):
        draw.rectangle((event["x"] * 16 + 3, event["y"] * 16 + 3, event["x"] * 16 + 12, event["y"] * 16 + 12), outline=COLOR_WARP, width=2)
    for event in map_data.get("bg_events", []):
        draw.rectangle((event["x"] * 16 + 5, event["y"] * 16 + 5, event["x"] * 16 + 10, event["y"] * 16 + 10), outline=COLOR_BG, width=1)
    if overlay_objects:
        for event in map_data.get("object_events", []):
            cx = event["x"] * 16 + 8
            cy = event["y"] * 16 + 8
            draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=COLOR_OBJECT, width=2)

    return preview


def render_runtime_preview(map_path: Path, layout_lookup, symbol_lookup, overlay_objects: bool):
    map_data = load_json(map_path)
    layout = layout_lookup[map_data["layout"]]
    primary_family = symbol_lookup[layout["primary_tileset"]]
    secondary_family = symbol_lookup[layout["secondary_tileset"]]
    primary_assets = family_tileset_assets(primary_family)
    secondary_assets = family_tileset_assets(secondary_family)
    primary_metatiles = primary_assets["metatiles"]
    secondary_metatiles = secondary_assets["metatiles"]

    blockdata_path = ROOT / layout["blockdata_filepath"]
    border_path = ROOT / layout["border_filepath"]
    raw = blockdata_path.read_bytes()
    values = struct.unpack("<" + "H" * (len(raw) // 2), raw)
    border_values = struct.unpack("<4H", border_path.read_bytes())
    width = layout["width"]
    height = layout["height"]
    canvas_width = max(width, RUNTIME_VIEW_WIDTH)
    canvas_height = max(height, RUNTIME_VIEW_HEIGHT)
    offset_x = (canvas_width - width) // 2
    offset_y = (canvas_height - height) // 2

    preview = Image.new("RGBA", (canvas_width * 16, canvas_height * 16), runtime_backdrop(primary_assets, secondary_assets))

    for y in range(canvas_height):
        for x in range(canvas_width):
            entry = border_values[(x & 1) + ((y & 1) * 2)]
            metatile_id = entry & MAPGRID_METATILE_ID_MASK
            if metatile_id < NUM_METATILES_IN_PRIMARY:
                tile_words = primary_metatiles[metatile_id]
            else:
                tile_words = secondary_metatiles[metatile_id - NUM_METATILES_IN_PRIMARY]
            preview.alpha_composite(compose_metatile(tile_words, primary_assets, secondary_assets), (x * 16, y * 16))

    for y in range(height):
        for x in range(width):
            entry = values[y * width + x]
            metatile_id = entry & MAPGRID_METATILE_ID_MASK
            if metatile_id < NUM_METATILES_IN_PRIMARY:
                tile_words = primary_metatiles[metatile_id]
            else:
                tile_words = secondary_metatiles[metatile_id - NUM_METATILES_IN_PRIMARY]
            preview.alpha_composite(
                compose_metatile(tile_words, primary_assets, secondary_assets),
                ((x + offset_x) * 16, (y + offset_y) * 16),
            )

    draw = ImageDraw.Draw(preview)
    for event in map_data.get("warp_events", []):
        x = (event["x"] + offset_x) * 16
        y = (event["y"] + offset_y) * 16
        draw.rectangle((x + 3, y + 3, x + 12, y + 12), outline=COLOR_WARP, width=2)
    for event in map_data.get("bg_events", []):
        x = (event["x"] + offset_x) * 16
        y = (event["y"] + offset_y) * 16
        draw.rectangle((x + 5, y + 5, x + 10, y + 10), outline=COLOR_BG, width=1)
    if overlay_objects:
        for event in map_data.get("object_events", []):
            cx = (event["x"] + offset_x) * 16 + 8
            cy = (event["y"] + offset_y) * 16 + 8
            draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=COLOR_OBJECT, width=2)

    return preview


def save_image(image, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def main():
    atlas = load_json(ATLAS_PATH)
    families, symbol_lookup = build_family_lookup(atlas)
    layout_lookup = resolve_layout_lookup()

    for family in atlas["families"]:
        output_path = PREVIEW_ROOT / "families" / f"{family['id']}.png"
        save_image(family_metatile_sheet(family, families), output_path)
        print(f"rendered {output_path.relative_to(ROOT)}")

    semantic_output = PREVIEW_ROOT / "semantic_tiles.png"
    save_image(semantic_tile_sheet(atlas, families), semantic_output)
    print(f"rendered {semantic_output.relative_to(ROOT)}")

    for target in atlas.get("preview_targets", {}).get("maps", []):
        map_path = ROOT / target["map_json"]
        output_path = ROOT / target["output"]
        preview = render_map_preview(map_path, layout_lookup, symbol_lookup, target.get("overlay_objects", False))
        save_image(preview, output_path)
        print(f"rendered {output_path.relative_to(ROOT)}")
        runtime_output = PREVIEW_ROOT / "runtime" / output_path.name
        runtime_preview = render_runtime_preview(map_path, layout_lookup, symbol_lookup, target.get("overlay_objects", False))
        save_image(runtime_preview, runtime_output)
        print(f"rendered {runtime_output.relative_to(ROOT)}")


if __name__ == "__main__":
    raise SystemExit(main())
