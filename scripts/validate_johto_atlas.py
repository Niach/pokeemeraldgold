#!/usr/bin/env python3

import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"
LAYOUTS_PATH = ROOT / "data" / "layouts" / "layouts.json"
MAPGRID_METATILE_ID_MASK = 0x03FF
NUM_METATILES_IN_PRIMARY = 512


def fail(message, errors):
    errors.append(message)


def is_hex_token(token: str):
    try:
        int(token, 16)
        return True
    except ValueError:
        return False


def load_atlas():
    return json.loads(ATLAS_PATH.read_text())


def semantic_lookup(atlas):
    return {tile["id"]: tile for tile in atlas.get("semantic_tiles", [])}


def validate_sources(atlas, errors):
    for source_id, source in atlas.get("sources", {}).items():
        root = Path(source["root"])
        if not root.exists():
            fail(f"source '{source_id}' root does not exist: {root}", errors)


def validate_families(atlas, errors):
    family_ids = set()
    family_symbols = set()

    for family in atlas.get("families", []):
        family_id = family["id"]
        symbol = family["symbol"]
        if family_id in family_ids:
            fail(f"duplicate family id: {family_id}", errors)
        family_ids.add(family_id)
        if symbol in family_symbols:
            fail(f"duplicate family symbol: {symbol}", errors)
        family_symbols.add(symbol)

    for family in atlas.get("families", []):
        runtime_tile_count = family.get("runtime_tile_count")
        if runtime_tile_count is not None and runtime_tile_count <= 0:
            fail(f"family '{family['id']}' has non-positive runtime_tile_count", errors)

        paired = family.get("paired_primary_family")
        if paired is not None and paired not in family_ids:
            fail(f"family '{family['id']}' references missing paired_primary_family '{paired}'", errors)

        candidates = {candidate["id"]: candidate for candidate in family.get("candidates", [])}
        selected = family.get("selected_candidate")
        if selected is not None and selected not in candidates:
            fail(f"family '{family['id']}' selected_candidate '{selected}' is missing", errors)

        for candidate in candidates.values():
            source = atlas["sources"].get(candidate["source"])
            if source is None:
                fail(
                    f"family '{family['id']}' candidate '{candidate['id']}' references unknown source '{candidate['source']}'",
                    errors,
                )
                continue
            source_dir = Path(source["root"]) / candidate["source_dir"]
            if not source_dir.is_dir():
                fail(f"missing tileset source directory: {source_dir}", errors)
    for alias in atlas.get("aliases", []):
        if alias["family"] not in family_ids:
            fail(f"alias '{alias['symbol']}' references missing family '{alias['family']}'", errors)

    return family_ids


def validate_semantic_tiles(atlas, family_ids, errors):
    semantic_ids = set()
    for tile in atlas.get("semantic_tiles", []):
        tile_id = tile["id"]
        if tile_id in semantic_ids:
            fail(f"duplicate semantic tile id: {tile_id}", errors)
        semantic_ids.add(tile_id)

        if tile["family"] not in family_ids:
            fail(f"semantic tile '{tile_id}' references missing family '{tile['family']}'", errors)

        try:
            entry = int(tile["entry"], 16)
        except ValueError:
            fail(f"semantic tile '{tile_id}' has invalid entry '{tile['entry']}'", errors)
            continue

        if not (0 <= entry <= 0xFFFF):
            fail(f"semantic tile '{tile_id}' entry '{tile['entry']}' does not fit u16 mapgrid data", errors)

    return semantic_ids


def validate_block_templates(atlas, semantic_ids, errors):
    templates = atlas.get("block_templates", {})
    for template_id, values in templates.items():
        if len(values) != 4:
            fail(f"block template '{template_id}' must contain 4 tokens", errors)
            continue
        for token in values:
            if token not in semantic_ids and not is_hex_token(token):
                fail(f"block template '{template_id}' references unknown token '{token}'", errors)

    return set(templates)


def validate_preview_targets(atlas, errors):
    for target in atlas.get("preview_targets", {}).get("maps", []):
        map_path = ROOT / target["map_json"]
        if not map_path.is_file():
            fail(f"preview target missing map json: {map_path}", errors)


def selected_metatile_count(atlas, family):
    if not family.get("candidates"):
        return None
    candidates = {candidate["id"]: candidate for candidate in family["candidates"]}
    selected = candidates[family["selected_candidate"]]
    source_root = Path(atlas["sources"][selected["source"]]["root"])
    metatiles_path = source_root / selected["source_dir"] / "metatiles.bin"
    if not metatiles_path.is_file():
        return None
    return len(metatiles_path.read_bytes()) // 16


def build_symbol_lookup(atlas):
    families = {family["id"]: family for family in atlas["families"]}
    lookup = {}
    for family in atlas["families"]:
        lookup[family["symbol"]] = family
    for alias in atlas.get("aliases", []):
        lookup[alias["symbol"]] = families[alias["family"]]
    return lookup


def validate_preview_target_ranges(atlas, errors):
    symbol_lookup = build_symbol_lookup(atlas)
    layouts = {layout["id"]: layout for layout in json.loads(LAYOUTS_PATH.read_text())["layouts"]}

    for target in atlas.get("preview_targets", {}).get("maps", []):
        map_path = ROOT / target["map_json"]
        if not map_path.is_file():
            continue

        map_data = json.loads(map_path.read_text())
        layout = layouts[map_data["layout"]]
        secondary_family = symbol_lookup.get(layout["secondary_tileset"])
        if secondary_family is None:
            fail(f"{map_path}: layout references unknown secondary tileset '{layout['secondary_tileset']}'", errors)
            continue

        secondary_count = selected_metatile_count(atlas, secondary_family)
        if secondary_count is None:
            continue

        blockdata_path = ROOT / layout["blockdata_filepath"]
        raw = blockdata_path.read_bytes()
        values = struct.unpack("<" + "H" * (len(raw) // 2), raw)
        for index, value in enumerate(values):
            metatile_id = value & MAPGRID_METATILE_ID_MASK
            if metatile_id >= NUM_METATILES_IN_PRIMARY and (metatile_id - NUM_METATILES_IN_PRIMARY) >= secondary_count:
                fail(
                    f"{map_path}: metatile {metatile_id:#04x} at index {index} exceeds selected secondary family '{secondary_family['id']}' count {secondary_count}",
                    errors,
                )
                break


def main():
    atlas = load_atlas()
    errors = []
    validate_sources(atlas, errors)
    family_ids = validate_families(atlas, errors)
    semantic_ids = validate_semantic_tiles(atlas, family_ids, errors)
    validate_block_templates(atlas, semantic_ids, errors)
    validate_preview_targets(atlas, errors)
    validate_preview_target_ranges(atlas, errors)

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    print("Johto atlas validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
