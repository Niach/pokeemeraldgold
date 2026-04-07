#!/usr/bin/env python3

import json
import re
import struct
from functools import lru_cache
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow is required by the tileset generator.
    Image = None


ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"
ATLAS = json.loads(ATLAS_PATH.read_text())
CRYSTAL_ROOT = Path(ATLAS["sources"]["pokecrystal"]["root"])

NUM_METATILES_IN_PRIMARY = 512
MAPGRID_COLLISION_SHIFT = 10
MAPGRID_ELEVATION_SHIFT = 12
METATILE_ATTR_BEHAVIOR_SHIFT = 0
METATILE_ATTR_LAYER_SHIFT = 12

METATILE_LAYER_NORMAL = 0
METATILE_LAYER_COVERED = 1

MB_NORMAL = 0x00
MB_TALL_GRASS = 0x02
MB_CAVE = 0x08
MB_POND_WATER = 0x10
MB_OCEAN_WATER = 0x15
MB_JUMP_EAST = 0x3D
MB_JUMP_WEST = 0x3E
MB_JUMP_SOUTH = 0x40
MB_JUMP_SOUTHEAST = 0x43
MB_JUMP_SOUTHWEST = 0x44
MB_NON_ANIMATED_DOOR = 0x60
MB_LADDER = 0x61
MB_EAST_ARROW_WARP = 0x62
MB_WEST_ARROW_WARP = 0x63
MB_SOUTH_ARROW_WARP = 0x65
MB_ANIMATED_DOOR = 0x69
MB_UP_ESCALATOR = 0x6A
MB_DOWN_ESCALATOR = 0x6B
MB_COUNTER = 0x80
MB_PC = 0x85
MB_REGION_MAP = 0x87
MB_TELEVISION = 0x88
MB_BOOKSHELF = 0xE1

PLAYERS_ROOM_GENERATED_KIND = "crystal_players_room"
CRYSTAL_TILESET_GENERATED_KIND = "crystal_tileset"

PLAYERS_ROOM_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_players_room"
PLAYERS_HOUSE_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_players_house"
HOUSE_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_house"
LAB_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_lab"
JOHTO_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_town_early"
GATE_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_gate"
POKECENTER_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_pokecenter"
MART_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_mart"

BUILDING_PRIMARY_PALETTES_DIR = ROOT / "data" / "tilesets" / "primary" / "building" / "palettes"
GENERAL_PRIMARY_PALETTES_DIR = ROOT / "data" / "tilesets" / "primary" / "general" / "palettes"

COLLISION_LINE_RE = re.compile(
    r"tilecoll\s+([A-Z_0-9]+),\s*([A-Z_0-9]+),\s*([A-Z_0-9]+),\s*([A-Z_0-9]+)\s*;\s*([0-9A-Fa-f]{2})"
)
TILEPAL_LINE_RE = re.compile(r"tilepal\s+([01])\s*,\s*(.+)$")
REPT_LINE_RE = re.compile(r"rept\s+(\d+)$")
DB_LINE_RE = re.compile(r"db\s+(.+)$")

BASE_GRAYSCALE_PALETTE = [
    (0, 0, 0),
    (248, 243, 236),
    (238, 233, 226),
    (224, 220, 212),
    (210, 205, 198),
    (197, 192, 185),
    (182, 178, 171),
    (169, 164, 157),
    (155, 150, 143),
    (135, 130, 123),
    (120, 116, 109),
    (107, 102, 95),
    (93, 88, 81),
    (80, 75, 68),
    (65, 61, 53),
    (40, 35, 28),
]

BORDER_PALETTE = [(0, 0, 0)] * 16

LUMINANCE_TO_INDEX = {
    255: 1,
    170: 5,
    85: 10,
    0: 15,
}

QUADRANT_TILE_OFFSETS = (
    (0, 1, 4, 5),
    (2, 3, 6, 7),
    (8, 9, 12, 13),
    (10, 11, 14, 15),
)

PALETTE_CLASS_SLOTS = {
    "GRAY": 6,
    "BROWN": 7,
    "RED": 8,
    "GREEN": 9,
    "WATER": 10,
    "YELLOW": 11,
    "ROOF": 12,
    "TEXT": 13,
}

BORDER_PALETTE_SLOT = 14

PALETTE_PROFILES = {
    "building_primary": {
        "base_palettes_dir": BUILDING_PRIMARY_PALETTES_DIR,
        "tints": {
            "GRAY": ((204, 205, 210), 0.08),
            "BROWN": ((214, 188, 148), 0.22),
            "RED": ((206, 150, 154), 0.26),
            "GREEN": ((160, 194, 156), 0.22),
            "WATER": ((150, 192, 222), 0.24),
            "YELLOW": ((220, 198, 120), 0.28),
            "ROOF": ((186, 132, 126), 0.32),
            "TEXT": ((150, 154, 170), 0.12),
        },
    },
    "general_primary": {
        "base_palettes_dir": GENERAL_PRIMARY_PALETTES_DIR,
        "tints": {
            "GRAY": ((196, 206, 208), 0.08),
            "BROWN": ((186, 156, 118), 0.26),
            "RED": ((192, 120, 116), 0.30),
            "GREEN": ((126, 182, 118), 0.34),
            "WATER": ((114, 180, 216), 0.34),
            "YELLOW": ((216, 190, 108), 0.30),
            "ROOF": ((176, 112, 108), 0.34),
            "TEXT": ((148, 152, 168), 0.14),
        },
    },
}

CRYSTAL_TO_GBA_COLLISION = {
    "01": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_NORMAL},
    "BOOKSHELF": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_BOOKSHELF},
    "BUOY": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "CAVE": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_CAVE},
    "COUNTER": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_COUNTER},
    "CUT_TREE": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "DOOR": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_ANIMATED_DOOR},
    "FF": {"collision": 1, "elevation": 0, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "FLOOR": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_NORMAL},
    "HEADBUTT_TREE": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "HOP_DOWN": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_JUMP_SOUTH},
    "HOP_DOWN_LEFT": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_JUMP_SOUTHWEST},
    "HOP_DOWN_RIGHT": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_JUMP_SOUTHEAST},
    "HOP_LEFT": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_JUMP_WEST},
    "HOP_RIGHT": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_JUMP_EAST},
    "LADDER": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_NON_ANIMATED_DOOR},
    "PC": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_PC},
    "RADIO": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_TELEVISION},
    "STAIRCASE": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_NON_ANIMATED_DOOR},
    "TALL_GRASS": {"collision": 0, "elevation": 3, "layer": METATILE_LAYER_NORMAL, "behavior": MB_TALL_GRASS},
    "TOWN_MAP": {"collision": 1, "elevation": 0, "layer": METATILE_LAYER_COVERED, "behavior": MB_REGION_MAP},
    "TV": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_TELEVISION},
    "UP_WALL": {"collision": 1, "elevation": 0, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "VIRTUAL_BOY": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_TELEVISION},
    "WALL": {"collision": 1, "elevation": 0, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "WARP_CARPET_DOWN": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_SOUTH_ARROW_WARP},
    "WARP_CARPET_LEFT": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_WEST_ARROW_WARP},
    "WARP_CARPET_RIGHT": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_EAST_ARROW_WARP},
    "WARP_PANEL": {"collision": 0, "elevation": 0, "layer": METATILE_LAYER_NORMAL, "behavior": MB_NON_ANIMATED_DOOR},
    "WATER": {"collision": 0, "elevation": 1, "layer": METATILE_LAYER_NORMAL, "behavior": MB_POND_WATER},
    "WHIRLPOOL": {"collision": 0, "elevation": 1, "layer": METATILE_LAYER_NORMAL, "behavior": MB_OCEAN_WATER},
    "WINDOW": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL},
    "MART_SHELF": {"collision": 1, "elevation": 3, "layer": METATILE_LAYER_COVERED, "behavior": MB_BOOKSHELF},
}

GENERATED_RUNTIME_TILESETS = [
    {
        "family_id": "johto_players_room",
        "runtime_dir": PLAYERS_ROOM_RUNTIME_DIR,
        "generated": PLAYERS_ROOM_GENERATED_KIND,
    },
    {
        "family_id": "johto_players_house",
        "runtime_dir": PLAYERS_HOUSE_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "players_house",
            "palette_profile": "building_primary",
            "border_mode": "dark",
        },
    },
    {
        "family_id": "johto_house",
        "runtime_dir": HOUSE_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "house",
            "palette_profile": "building_primary",
            "border_mode": "dark",
        },
    },
    {
        "family_id": "johto_lab",
        "runtime_dir": LAB_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "lab",
            "palette_profile": "building_primary",
            "border_mode": "dark",
        },
    },
    {
        "family_id": "johto_town_early",
        "runtime_dir": JOHTO_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "johto",
            "palette_profile": "general_primary",
            "border_mode": "exact",
        },
    },
    {
        "family_id": "johto_gate",
        "runtime_dir": GATE_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "gate",
            "palette_profile": "building_primary",
            "border_mode": "dark",
        },
    },
    {
        "family_id": "johto_pokecenter",
        "runtime_dir": POKECENTER_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "pokecenter",
            "palette_profile": "building_primary",
            "border_mode": "dark",
        },
    },
    {
        "family_id": "johto_mart",
        "runtime_dir": MART_RUNTIME_DIR,
        "generated": {
            "kind": CRYSTAL_TILESET_GENERATED_KIND,
            "source_tileset": "mart",
            "palette_profile": "building_primary",
            "border_mode": "dark",
        },
    },
]


def _ensure_pillow():
    if Image is None:
        raise RuntimeError("Pillow is required to generate Crystal-derived tilesets")


def _write_jasc_pal(path: Path, colors):
    lines = ["JASC-PAL", "0100", "16"]
    lines.extend(f"{r} {g} {b}" for r, g, b in colors)
    path.write_text("\n".join(lines) + "\n")


def _write_gbapal(path: Path, colors):
    encoded = bytearray()
    for r, g, b in colors:
        value = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)
        encoded.extend(struct.pack("<H", value))
    path.write_bytes(encoded)


def _read_jasc_pal(path: Path):
    lines = path.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "16"]:
        raise ValueError(f"Unsupported palette format in {path}")
    return [tuple(int(part) for part in line.split()) for line in lines[3:19]]


def _parse_collision_rows(path: Path):
    rows_by_index = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.split(";", 1)[0] + (";" + raw_line.split(";", 1)[1] if ";" in raw_line else "")
        match = COLLISION_LINE_RE.search(line)
        if not match:
            continue
        tl, tr, bl, br, block_hex = match.groups()
        rows_by_index[int(block_hex, 16)] = [tl, tr, bl, br]

    if not rows_by_index:
        raise ValueError(f"{path}: no collision rows found")

    rows = [None] * (max(rows_by_index) + 1)
    for index, row in rows_by_index.items():
        rows[index] = row

    missing = [index for index, row in enumerate(rows) if row is None]
    if missing:
        missing_ids = ", ".join(f"0x{index:02X}" for index in missing)
        raise ValueError(f"{path}: missing collision rows for {missing_ids}")
    return rows


def _load_crystal_block_tiles(path: Path):
    raw = path.read_bytes()
    if len(raw) % 16 != 0:
        raise ValueError(f"{path}: expected Crystal metatiles.bin to be a multiple of 16 bytes")
    return [list(raw[index:index + 16]) for index in range(0, len(raw), 16)]


def _pack_map_entry(local_metatile_index: int, collision: int, elevation: int) -> int:
    return (
        (NUM_METATILES_IN_PRIMARY + local_metatile_index)
        | (collision << MAPGRID_COLLISION_SHIFT)
        | (elevation << MAPGRID_ELEVATION_SHIFT)
    )


def _pack_bg_tile(local_tile_index: int, palette_slot: int) -> int:
    return (NUM_METATILES_IN_PRIMARY + local_tile_index) | (palette_slot << 12)


def _pack_metatile_attr(layer: int, behavior: int) -> int:
    return (behavior << METATILE_ATTR_BEHAVIOR_SHIFT) | (layer << METATILE_ATTR_LAYER_SHIFT)


def _blend_color(base, tint, strength: float):
    return tuple(
        max(0, min(255, round((channel * (1.0 - strength)) + (target * strength))))
        for channel, target in zip(base, tint)
    )


def _tint_palette(colors, tint, strength: float):
    tinted = [colors[0]]
    tinted.extend(_blend_color(color, tint, strength) for color in colors[1:])
    return tinted


def _map_luminance_to_index(value: int) -> int:
    mapped = LUMINANCE_TO_INDEX.get(value)
    if mapped is not None:
        return mapped
    if value < 43:
        return 15
    if value < 128:
        return 10
    if value < 213:
        return 5
    return 1


def _generated_spec_key(spec):
    if isinstance(spec, str):
        return spec
    if isinstance(spec, dict):
        return json.dumps(spec, sort_keys=True)
    raise ValueError(f"unsupported generated tileset spec {spec!r}")


def normalize_generated_spec(spec):
    if isinstance(spec, str):
        return {"kind": spec}
    if isinstance(spec, dict):
        normalized = dict(spec)
        normalized.setdefault("kind", CRYSTAL_TILESET_GENERATED_KIND)
        return normalized
    raise ValueError(f"unsupported generated tileset spec {spec!r}")


def _resolve_collision_info(token: str):
    collision_info = CRYSTAL_TO_GBA_COLLISION.get(token)
    if collision_info is None:
        return {"collision": 1, "elevation": 0, "layer": METATILE_LAYER_COVERED, "behavior": MB_NORMAL}
    return collision_info


def _source_paths(source_tileset: str):
    base = CRYSTAL_ROOT
    return {
        "source_png": base / "gfx" / "tilesets" / f"{source_tileset}.png",
        "source_metatiles": base / "data" / "tilesets" / f"{source_tileset}_metatiles.bin",
        "source_collisions": base / "data" / "tilesets" / f"{source_tileset}_collision.asm",
        "source_palette_map": base / "gfx" / "tilesets" / f"{source_tileset}_palette_map.asm",
    }


@lru_cache(maxsize=None)
def _load_quantized_source_tiles(source_png: str):
    _ensure_pillow()

    with Image.open(source_png) as image:
        grayscale = image.convert("L")
        width, height = grayscale.size
        if width % 8 != 0 or height % 8 != 0:
            raise ValueError(f"{source_png}: expected source image dimensions to be 8x8 aligned")
        tiles_per_row = width // 8
        tiles = []
        for tile_y in range(0, height, 8):
            for tile_x in range(0, width, 8):
                crop = grayscale.crop((tile_x, tile_y, tile_x + 8, tile_y + 8))
                tiles.append(tuple(_map_luminance_to_index(value) for value in crop.getdata()))
        return {
            "tiles": tuple(tiles),
            "tiles_per_row": tiles_per_row,
        }


def _parse_db_entries(body: str):
    entries = []
    for part in body.split(","):
        token = part.strip()
        if token.startswith("$"):
            value = int(token[1:], 16)
        else:
            value = int(token, 0)
        entries.append(None if (value & 0xF) == 0xF else value & 0xF)
        entries.append(None if ((value >> 4) & 0xF) == 0xF else (value >> 4) & 0xF)
    return entries


@lru_cache(maxsize=None)
def _parse_palette_map(path_str: str):
    entries = []
    lines = Path(path_str).read_text().splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].split(";", 1)[0].strip()
        index += 1
        if not line:
            continue

        match = TILEPAL_LINE_RE.match(line)
        if match:
            _bank = int(match.group(1))
            names = [part.strip() for part in match.group(2).split(",")]
            entries.extend(names)
            continue

        match = REPT_LINE_RE.match(line)
        if match:
            count = int(match.group(1))
            block_entries = []
            while index < len(lines):
                repeat_line = lines[index].split(";", 1)[0].strip()
                index += 1
                if not repeat_line:
                    continue
                if repeat_line == "endr":
                    break
                db_match = DB_LINE_RE.match(repeat_line)
                if db_match is None:
                    raise ValueError(f"{path_str}: unsupported palette map repeat body '{repeat_line}'")
                block_entries.extend(_parse_db_entries(db_match.group(1)))
            entries.extend(block_entries * count)
            continue

        db_match = DB_LINE_RE.match(line)
        if db_match is not None:
            entries.extend(_parse_db_entries(db_match.group(1)))
            continue

    if len(entries) < 256:
        entries.extend([None] * (256 - len(entries)))
    return tuple(entries[:256])


def _resolve_source_tile_index(raw_tile_index: int, source_tile_count: int) -> int:
    # Crystal 192-tile tilesets are split across two 96-tile VRAM banks:
    # 0x00-0x5F address the first bank and 0x80-0xDF address the second.
    # The gaps are unused, and some tilesets use 0xF0+/0xFF as blank filler.
    if source_tile_count == 192:
        if raw_tile_index < 0x60:
            return raw_tile_index
        if 0x80 <= raw_tile_index < 0xE0:
            return 96 + (raw_tile_index - 0x80)
        if raw_tile_index >= 0xF0:
            return 0
    if raw_tile_index < source_tile_count:
        return raw_tile_index
    masked = raw_tile_index & 0x7F
    if masked < source_tile_count:
        return masked
    raise ValueError(
        f"raw Crystal tile 0x{raw_tile_index:02X} cannot be resolved against source tile count {source_tile_count}"
    )


def _runtime_palette_bank(profile_name: str):
    profile = PALETTE_PROFILES[profile_name]
    palette_bank = [
        _read_jasc_pal(profile["base_palettes_dir"] / f"{palette_index:02d}.pal")
        for palette_index in range(16)
    ]
    for palette_class, palette_slot in PALETTE_CLASS_SLOTS.items():
        tint, strength = profile["tints"][palette_class]
        palette_bank[palette_slot] = _tint_palette(BASE_GRAYSCALE_PALETTE, tint, strength)
    palette_bank[BORDER_PALETTE_SLOT] = list(BORDER_PALETTE)
    return palette_bank


def _render_tiles_png(source_tiles, tiles_per_row: int):
    _ensure_pillow()

    output_tiles = 1 + len(source_tiles)
    output_rows = (output_tiles + tiles_per_row - 1) // tiles_per_row
    output = Image.new("P", (tiles_per_row * 8, output_rows * 8), 0)

    palette_bytes = []
    for r, g, b in BASE_GRAYSCALE_PALETTE:
        palette_bytes.extend((r, g, b))
    palette_bytes.extend([0] * (768 - len(palette_bytes)))
    output.putpalette(palette_bytes)

    border_tile = Image.new("P", (8, 8), 15)
    border_tile.putpalette(palette_bytes)
    output.paste(border_tile, (0, 0))

    for tile_index, tile_data in enumerate(source_tiles, start=1):
        tile = Image.new("P", (8, 8), 0)
        tile.putpalette(palette_bytes)
        tile.putdata(tile_data)
        out_x = (tile_index % tiles_per_row) * 8
        out_y = (tile_index // tiles_per_row) * 8
        output.paste(tile, (out_x, out_y))

    return output


@lru_cache(maxsize=None)
def _load_generic_spec_data(generated_key: str):
    spec = json.loads(generated_key) if generated_key.startswith("{") else generated_key
    spec = normalize_generated_spec(spec)
    source_tileset = spec["source_tileset"]
    paths = _source_paths(source_tileset)
    block_tiles = _load_crystal_block_tiles(paths["source_metatiles"])
    collisions = _parse_collision_rows(paths["source_collisions"])
    quantized_tiles = _load_quantized_source_tiles(str(paths["source_png"]))
    palette_map = _parse_palette_map(str(paths["source_palette_map"]))
    return {
        "spec": spec,
        "paths": paths,
        "block_tiles": block_tiles,
        "collisions": collisions,
        "source_tiles": quantized_tiles["tiles"],
        "tiles_per_row": quantized_tiles["tiles_per_row"],
        "palette_map": palette_map,
    }


def _generic_local_metatile(block_id: int, quadrant: int) -> int:
    return 1 + (block_id * 4) + quadrant


def _generic_local_tile(source_tile_index: int) -> int:
    return 1 + source_tile_index


def _generic_metatile_words(spec):
    data = _load_generic_spec_data(_generated_spec_key(spec))
    source_tile_count = len(data["source_tiles"])
    words = []
    border_word = _pack_bg_tile(0, BORDER_PALETTE_SLOT)
    words.append([border_word, border_word, border_word, border_word, 0, 0, 0, 0])

    for block in data["block_tiles"]:
        for offsets in QUADRANT_TILE_OFFSETS:
            tile_words = []
            for offset in offsets:
                raw_tile_index = block[offset]
                source_tile_index = _resolve_source_tile_index(raw_tile_index, source_tile_count)
                palette_class = data["palette_map"][raw_tile_index]
                if palette_class is None and source_tile_index < len(data["palette_map"]):
                    palette_class = data["palette_map"][source_tile_index]
                if palette_class is None:
                    palette_class = "GRAY"
                palette_slot = PALETTE_CLASS_SLOTS.get(palette_class)
                if palette_slot is None:
                    raise ValueError(f"unsupported Crystal palette class '{palette_class}'")
                tile_words.append(_pack_bg_tile(_generic_local_tile(source_tile_index), palette_slot))
            words.append(tile_words + [0, 0, 0, 0])

    return words


def _generic_metatile_attributes(spec):
    data = _load_generic_spec_data(_generated_spec_key(spec))
    attributes = [_pack_metatile_attr(METATILE_LAYER_COVERED, MB_NORMAL)]
    for block_tokens in data["collisions"]:
        for token in block_tokens:
            collision_info = _resolve_collision_info(token)
            attributes.append(_pack_metatile_attr(collision_info["layer"], collision_info["behavior"]))
    return attributes


def _generic_block_translations(spec):
    data = _load_generic_spec_data(_generated_spec_key(spec))
    border_entry = _pack_map_entry(0, 1, 0)
    translations = {}

    for block_id, collision_tokens in enumerate(data["collisions"]):
        metatiles = []
        for quadrant, token in enumerate(collision_tokens):
            collision_info = _resolve_collision_info(token)
            metatiles.append(
                _pack_map_entry(
                    _generic_local_metatile(block_id, quadrant),
                    collision_info["collision"],
                    collision_info["elevation"],
                )
            )

        border_mode = data["spec"].get("border_mode", "exact")
        border_metatiles = [border_entry] * 4 if border_mode == "dark" and block_id == 0 else list(metatiles)
        translations[block_id] = {
            "provenance": "custom_gba",
            "metatile_tokens": [f"{value:04X}" for value in metatiles],
            "metatiles": metatiles,
            "border_tokens": [f"{value:04X}" for value in border_metatiles],
            "border_metatiles": border_metatiles,
            "source_collision_tokens": collision_tokens,
            "source_block_tiles": data["block_tiles"][block_id],
        }

    return translations


def _players_room_paths():
    return _source_paths("players_room")


def build_players_room_palette_bank():
    palette_bank = [
        _read_jasc_pal(BUILDING_PRIMARY_PALETTES_DIR / f"{palette_index:02d}.pal")
        for palette_index in range(16)
    ]
    palette_bank[6] = list(BASE_GRAYSCALE_PALETTE)
    palette_bank[7] = _tint_palette(BASE_GRAYSCALE_PALETTE, (214, 188, 148), 0.22)
    palette_bank[8] = _tint_palette(BASE_GRAYSCALE_PALETTE, (150, 192, 222), 0.22)
    palette_bank[9] = _tint_palette(BASE_GRAYSCALE_PALETTE, (220, 198, 120), 0.28)
    palette_bank[10] = _tint_palette(BASE_GRAYSCALE_PALETTE, (222, 182, 196), 0.20)
    palette_bank[11] = list(BORDER_PALETTE)
    return palette_bank


def build_players_room_block_translations():
    paths = _players_room_paths()
    block_tiles = _load_crystal_block_tiles(paths["source_metatiles"])
    collisions = _parse_collision_rows(paths["source_collisions"])
    translations = {}
    border_entry = _pack_map_entry(0, 1, 0)

    for block_id, collision_tokens in enumerate(collisions):
        metatiles = []
        for quadrant, token in enumerate(collision_tokens):
            collision_info = _resolve_collision_info(token)
            metatiles.append(
                _pack_map_entry(
                    _generic_local_metatile(block_id, quadrant),
                    collision_info["collision"],
                    collision_info["elevation"],
                )
            )

        border_metatiles = [border_entry] * 4 if block_id == 0 else list(metatiles)
        translations[block_id] = {
            "provenance": "custom_gba",
            "metatile_tokens": [f"{value:04X}" for value in metatiles],
            "metatiles": metatiles,
            "border_tokens": [f"{value:04X}" for value in border_metatiles],
            "border_metatiles": border_metatiles,
            "source_collision_tokens": collision_tokens,
            "source_block_tiles": block_tiles[block_id],
        }

    return translations


def build_generated_block_translations(spec):
    normalized = normalize_generated_spec(spec)
    if normalized["kind"] == PLAYERS_ROOM_GENERATED_KIND:
        return build_players_room_block_translations()
    if normalized["kind"] == CRYSTAL_TILESET_GENERATED_KIND:
        return _generic_block_translations(normalized)
    raise ValueError(f"unsupported generated tileset kind '{normalized['kind']}'")


def _players_room_metatile_words():
    paths = _players_room_paths()
    block_tiles = _load_crystal_block_tiles(paths["source_metatiles"])
    collisions = _parse_collision_rows(paths["source_collisions"])
    words = []

    border_tile_word = _pack_bg_tile(0, 11)
    words.append([border_tile_word, border_tile_word, border_tile_word, border_tile_word, 0, 0, 0, 0])

    for block_id, block in enumerate(block_tiles):
        collision_tokens = collisions[block_id]
        for quadrant, offsets in enumerate(QUADRANT_TILE_OFFSETS):
            if collision_tokens[quadrant] == "FF":
                palette_slot = 11
            elif collision_tokens[quadrant] in {"FLOOR", "STAIRCASE"}:
                palette_slot = 9
            elif collision_tokens[quadrant] == "TOWN_MAP":
                palette_slot = 10
            elif collision_tokens[quadrant] == "TV":
                palette_slot = 8
            elif collision_tokens[quadrant] == "BOOKSHELF":
                palette_slot = 7
            else:
                palette_slot = 6

            words.append(
                [
                    _pack_bg_tile(_generic_local_tile(block[offsets[0]]), palette_slot),
                    _pack_bg_tile(_generic_local_tile(block[offsets[1]]), palette_slot),
                    _pack_bg_tile(_generic_local_tile(block[offsets[2]]), palette_slot),
                    _pack_bg_tile(_generic_local_tile(block[offsets[3]]), palette_slot),
                    0,
                    0,
                    0,
                    0,
                ]
            )

    return words


def _players_room_metatile_attributes():
    collisions = _parse_collision_rows(_players_room_paths()["source_collisions"])
    attributes = [_pack_metatile_attr(METATILE_LAYER_COVERED, MB_NORMAL)]
    for block_tokens in collisions:
        for token in block_tokens:
            collision_info = _resolve_collision_info(token)
            attributes.append(_pack_metatile_attr(collision_info["layer"], collision_info["behavior"]))
    return attributes


def _quantize_players_room_image():
    data = _load_quantized_source_tiles(str(_players_room_paths()["source_png"]))
    return _render_tiles_png(data["tiles"], data["tiles_per_row"])


def generate_players_room_tileset(output_dir: Path = PLAYERS_ROOM_RUNTIME_DIR):
    _ensure_pillow()

    output_dir.mkdir(parents=True, exist_ok=True)
    palettes_dir = output_dir / "palettes"
    palettes_dir.mkdir(parents=True, exist_ok=True)

    tiles_png = _quantize_players_room_image()
    tiles_path = output_dir / "tiles.png"
    tiles_png.save(tiles_path)

    palette_bank = build_players_room_palette_bank()
    for palette_index, colors in enumerate(palette_bank):
        palette_name = f"{palette_index:02d}"
        _write_jasc_pal(palettes_dir / f"{palette_name}.pal", colors)
        _write_gbapal(palettes_dir / f"{palette_name}.gbapal", colors)

    metatile_words = _players_room_metatile_words()
    metatile_attributes = _players_room_metatile_attributes()

    if len(metatile_words) != len(metatile_attributes):
        raise ValueError("players room metatile word count does not match attribute count")

    (output_dir / "metatiles.bin").write_bytes(
        b"".join(struct.pack("<8H", *tile_words) for tile_words in metatile_words)
    )
    (output_dir / "metatile_attributes.bin").write_bytes(
        b"".join(struct.pack("<H", value) for value in metatile_attributes)
    )

    for filename in ("tiles.4bpp", "tiles.4bpp.lz"):
        path = output_dir / filename
        if path.exists():
            path.unlink()

    return {
        "runtime_dir": str(output_dir),
        "tile_count": ((tiles_png.width // 8) * (tiles_png.height // 8)),
        "metatile_count": len(metatile_words),
    }


def generate_crystal_tileset(output_dir: Path, spec):
    normalized = normalize_generated_spec(spec)
    if normalized["kind"] == PLAYERS_ROOM_GENERATED_KIND:
        return generate_players_room_tileset(output_dir)

    if normalized["kind"] != CRYSTAL_TILESET_GENERATED_KIND:
        raise ValueError(f"unsupported generated tileset kind '{normalized['kind']}'")

    output_dir.mkdir(parents=True, exist_ok=True)
    palettes_dir = output_dir / "palettes"
    palettes_dir.mkdir(parents=True, exist_ok=True)

    data = _load_generic_spec_data(_generated_spec_key(normalized))
    tiles_png = _render_tiles_png(data["source_tiles"], data["tiles_per_row"])
    tiles_png.save(output_dir / "tiles.png")

    palette_bank = _runtime_palette_bank(normalized["palette_profile"])
    for palette_index, colors in enumerate(palette_bank):
        palette_name = f"{palette_index:02d}"
        _write_jasc_pal(palettes_dir / f"{palette_name}.pal", colors)
        _write_gbapal(palettes_dir / f"{palette_name}.gbapal", colors)

    metatile_words = _generic_metatile_words(normalized)
    metatile_attributes = _generic_metatile_attributes(normalized)
    if len(metatile_words) != len(metatile_attributes):
        raise ValueError(f"{normalized['source_tileset']}: metatile word count does not match attribute count")

    (output_dir / "metatiles.bin").write_bytes(
        b"".join(struct.pack("<8H", *tile_words) for tile_words in metatile_words)
    )
    (output_dir / "metatile_attributes.bin").write_bytes(
        b"".join(struct.pack("<H", value) for value in metatile_attributes)
    )

    for filename in ("tiles.4bpp", "tiles.4bpp.lz"):
        path = output_dir / filename
        if path.exists():
            path.unlink()

    return {
        "runtime_dir": str(output_dir),
        "tile_count": ((tiles_png.width // 8) * (tiles_png.height // 8)),
        "metatile_count": len(metatile_words),
        "source_tileset": normalized["source_tileset"],
    }


def generate_exact_runtime_tilesets():
    reports = []
    for entry in GENERATED_RUNTIME_TILESETS:
        report = generate_crystal_tileset(entry["runtime_dir"], entry["generated"])
        report["family_id"] = entry["family_id"]
        reports.append(report)
    return reports
