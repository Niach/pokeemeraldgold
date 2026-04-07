#!/usr/bin/env python3

import json
import re
from pathlib import Path

try:
    from crystal_room_tilesets import build_generated_block_translations
except ModuleNotFoundError:
    from scripts.crystal_room_tilesets import build_generated_block_translations

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"
IMPORT_DIR = ROOT / "data" / "johto_import"
CRYSTAL_TILESETS_PATH = IMPORT_DIR / "crystal_tilesets.json"
MAPS_PATH = IMPORT_DIR / "maps.json"
PARSER_EXPECTATIONS_PATH = IMPORT_DIR / "parser_expectations.json"
IR_DIR = IMPORT_DIR / "crystal_ir"
LAYOUTS_PATH = ROOT / "data" / "layouts" / "layouts.json"
MAP_GROUPS_PATH = ROOT / "data" / "maps" / "map_groups.json"
REGION_MAP_SECTIONS_PATH = ROOT / "src" / "data" / "region_map" / "region_map_sections.json"
AUTO_JOHTO_SCRIPTS_PATH = ROOT / "data" / "maps" / "johto_auto_scripts.inc"
HEAL_LOCATIONS_PATH = ROOT / "src" / "data" / "heal_locations.json"

SECTION_MARKERS = {
    "warp_events": (
        "def_warp_events",
        "def_coord_events",
        re.compile(r"warp_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*(\d+)"),
    ),
    "coord_events": (
        "def_coord_events",
        "def_bg_events",
        re.compile(r"coord_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*([A-Za-z0-9_]+)"),
    ),
    "bg_events": (
        "def_bg_events",
        "def_object_events",
        re.compile(r"bg_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*([A-Za-z0-9_]+)"),
    ),
    "object_events": (
        "def_object_events",
        None,
        re.compile(
            r"object_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*([A-Z0-9_]+),\s*(-?\d+),\s*(-?\d+),.*,\s*([A-Za-z0-9_]+),\s*(-?\d+)"
        ),
    ),
}

BLOCK_LABEL_RE = re.compile(r"^([A-Za-z0-9_]+)_Blocks:$")
INCBIN_RE = re.compile(r'^INCBIN\s+"([^"]+\.blk)"$')
NEWGROUP_RE = re.compile(r"^newgroup\s+([A-Z0-9_]+)$")
ENDGROUP_RE = re.compile(r"^endgroup$")
MAP_CONST_RE = re.compile(r"^map_const\s+([A-Z0-9_]+),\s*(\d+),\s*(\d+)$")
LANDMARK_ENTRY_RE = re.compile(r"^landmark\s+(-?\d+),\s*(-?\d+),\s*([A-Za-z0-9_]+)$")
LANDMARK_NAME_RE = re.compile(r'^([A-Za-z0-9_]+):\s+db\s+"([^"]*)@"$')


def load_json(path: Path):
    return json.loads(path.read_text())


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def strip_asm_comment(raw_line: str) -> str:
    return raw_line.split(";", 1)[0].strip()


ATLAS = load_json(ATLAS_PATH)
CRYSTAL_ROOT = Path(ATLAS["sources"]["pokecrystal"]["root"])
LAYOUTS = {layout["id"]: layout for layout in load_json(LAYOUTS_PATH)["layouts"]}


def load_semantic_tiles(atlas):
    semantic_tiles = {}
    for tile in atlas.get("semantic_tiles", []):
        semantic_tiles[tile["id"]] = int(tile["entry"], 16)
    return semantic_tiles


def load_block_templates(atlas):
    block_templates = {}
    for template_id, tokens in atlas.get("block_templates", {}).items():
        if len(tokens) != 4:
            raise ValueError(f"{ATLAS_PATH}: block template '{template_id}' must contain 4 metatile tokens")
        block_templates[template_id] = tokens
    return block_templates


SEMANTIC_TILES = load_semantic_tiles(ATLAS)
BLOCK_TEMPLATES = load_block_templates(ATLAS)


def is_hex_token(token: str) -> bool:
    try:
        int(token, 16)
        return True
    except ValueError:
        return False


def parse_metatile_token(token: str) -> int:
    if token in SEMANTIC_TILES:
        return SEMANTIC_TILES[token]
    if is_hex_token(token):
        return int(token, 16)
    raise ValueError(f"unknown semantic tile '{token}'")


def normalize_chunk_tokens(chunk) -> list[str]:
    if isinstance(chunk, str):
        if chunk in BLOCK_TEMPLATES:
            return list(BLOCK_TEMPLATES[chunk])
        values = chunk.split()
    elif isinstance(chunk, list):
        values = list(chunk)
    else:
        raise ValueError(f"unsupported chunk format: {chunk!r}")

    if len(values) != 4:
        raise ValueError(f"chunk '{chunk}' does not contain 4 metatile tokens")
    return values


def parse_chunk_tokens(chunk) -> list[int]:
    return [parse_metatile_token(token) for token in normalize_chunk_tokens(chunk)]


def split_asm_args(line: str, prefix: str, expected_count: int):
    if not line.startswith(prefix):
        raise ValueError(f"expected '{prefix}' line, found '{line}'")
    body = line[len(prefix):].strip()
    parts = [part.strip() for part in body.split(",")]
    if len(parts) != expected_count:
        raise ValueError(f"expected {expected_count} arguments for '{line}', found {len(parts)}")
    return parts


def resolve_crystal_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return CRYSTAL_ROOT / path


def parse_blocks_index():
    blocks_asm = CRYSTAL_ROOT / "data" / "maps" / "blocks.asm"
    pending_labels = []
    mapping = {}
    for raw_line in blocks_asm.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue
        label_match = BLOCK_LABEL_RE.match(line)
        if label_match:
            pending_labels.append(label_match.group(1))
            continue
        incbin_match = INCBIN_RE.match(line)
        if incbin_match:
            for label in pending_labels:
                mapping[label] = incbin_match.group(1)
            pending_labels.clear()
            continue
        pending_labels.clear()
    return mapping


def parse_map_constants():
    path = CRYSTAL_ROOT / "constants" / "map_constants.asm"
    current_group = None
    group_index = 0
    map_index = 0
    by_id = {}

    for raw_line in path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue

        match = NEWGROUP_RE.match(line)
        if match:
            current_group = match.group(1)
            group_index += 1
            map_index = 0
            continue

        if ENDGROUP_RE.match(line):
            current_group = None
            continue

        match = MAP_CONST_RE.match(line)
        if not match:
            continue
        if current_group is None:
            raise ValueError(f"map_const outside newgroup in {path}: {line}")

        map_index += 1
        map_id = match.group(1)
        by_id[map_id] = {
            "map_id": map_id,
            "group": current_group,
            "group_index": group_index,
            "map_index": map_index,
            "width_blocks": int(match.group(2)),
            "height_blocks": int(match.group(3)),
        }
    return by_id


def parse_map_table():
    path = CRYSTAL_ROOT / "data" / "maps" / "maps.asm"
    current_group = None
    by_name = {}

    for raw_line in path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue
        if line.endswith(":") and line.startswith("MapGroup_"):
            current_group = line[:-1]
            continue
        if not line.startswith("map "):
            continue
        parts = split_asm_args(line, "map ", 8)
        name = parts[0]
        by_name[name] = {
            "crystal_map": name,
            "group_label": current_group,
            "tileset": parts[1],
            "environment": parts[2],
            "landmark": parts[3],
            "music": parts[4],
            "phone_service_flag": parts[5],
            "time_of_day": parts[6],
            "fishgroup": parts[7],
        }
    return by_name


def parse_map_attributes():
    path = CRYSTAL_ROOT / "data" / "maps" / "attributes.asm"
    by_name = {}
    current_name = None

    for raw_line in path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue
        if line.startswith("map_attributes "):
            name, map_id, border_block, _connections = split_asm_args(line, "map_attributes ", 4)
            current_name = name
            by_name[name] = {
                "map_id": map_id,
                "border_block": border_block.removeprefix("$").upper(),
                "connections": [],
            }
            continue
        if line.startswith("connection "):
            if current_name is None:
                continue
            direction, target_name, target_map_id, offset = split_asm_args(line, "connection ", 4)
            by_name[current_name]["connections"].append(
                {
                    "direction": direction,
                    "map": target_name,
                    "target_map_id": target_map_id,
                    "offset": int(offset),
                }
            )
            continue
        current_name = None
    return by_name


CRYSTAL_BLOCKS_INDEX = parse_blocks_index()
CRYSTAL_MAP_CONSTANTS = parse_map_constants()
CRYSTAL_MAP_TABLE = parse_map_table()
CRYSTAL_MAP_ATTRIBUTES = parse_map_attributes()


def build_crystal_map_database():
    database = {}
    for crystal_map, map_info in CRYSTAL_MAP_TABLE.items():
        attributes = CRYSTAL_MAP_ATTRIBUTES.get(crystal_map)
        if attributes is None:
            continue
        constants = CRYSTAL_MAP_CONSTANTS.get(attributes["map_id"])
        if constants is None:
            raise ValueError(
                f"{crystal_map}: missing map_constants entry for map id '{attributes['map_id']}'"
            )

        database[crystal_map] = {
            "crystal_map": crystal_map,
            "map_id": attributes["map_id"],
            "group": constants["group"],
            "group_index": constants["group_index"],
            "map_index": constants["map_index"],
            "tileset": map_info["tileset"],
            "environment": map_info["environment"],
            "landmark": map_info["landmark"],
            "music": map_info["music"],
            "phone_service_flag": map_info["phone_service_flag"],
            "time_of_day": map_info["time_of_day"],
            "fishgroup": map_info["fishgroup"],
            "width_blocks": constants["width_blocks"],
            "height_blocks": constants["height_blocks"],
            "border_block": attributes["border_block"],
            "blk_path": CRYSTAL_BLOCKS_INDEX.get(crystal_map),
            "source_asm": f"maps/{crystal_map}.asm",
            "connections": attributes["connections"],
        }
    return database


CRYSTAL_MAP_DB = build_crystal_map_database()


def parse_landmark_data():
    constants_path = CRYSTAL_ROOT / "constants" / "landmark_constants.asm"
    johto_landmarks = set()
    all_landmarks = []
    in_johto = False
    reading_landmarks = False

    for raw_line in constants_path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue
        if line == "const_def":
            reading_landmarks = True
            continue
        if line.startswith("DEF NUM_LANDMARKS"):
            break
        if not reading_landmarks:
            continue
        if line == "DEF JOHTO_LANDMARK EQU const_value":
            in_johto = True
            continue
        if line.startswith("DEF JOHTO_LANDMARK_LAST"):
            in_johto = False
            continue
        match = re.match(r"^const\s+([A-Z0-9_]+)$", line)
        if not match:
            continue
        landmark_id = match.group(1)
        if not landmark_id.startswith("LANDMARK_"):
            continue
        all_landmarks.append(landmark_id)
        if in_johto:
            johto_landmarks.add(landmark_id)

    landmarks_path = CRYSTAL_ROOT / "data" / "maps" / "landmarks.asm"
    entries = []
    names = {}
    reading_entries = False
    for raw_line in landmarks_path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue
        if line == "Landmarks:":
            reading_entries = True
            continue
        if reading_entries:
            if line.startswith("assert_table_length NUM_LANDMARKS"):
                reading_entries = False
                continue
            match = LANDMARK_ENTRY_RE.match(line)
            if match:
                x, y, label = match.groups()
                entries.append(
                    {
                        "x": int(x),
                        "y": int(y),
                        "name_label": label,
                    }
                )
            continue

        match = LANDMARK_NAME_RE.match(line)
        if match:
            label, raw_name = match.groups()
            names[label] = raw_name.replace("<BSP>", " ")

    if len(all_landmarks) != len(entries):
        raise ValueError(
            f"{landmarks_path}: landmark count {len(entries)} does not match constants count {len(all_landmarks)}"
        )

    landmarks = {}
    for landmark_id, entry in zip(all_landmarks, entries):
        landmarks[landmark_id] = {
            "id": landmark_id,
            "x": entry["x"],
            "y": entry["y"],
            "name": names.get(entry["name_label"], entry["name_label"]),
        }
    return johto_landmarks, landmarks


JOHTO_LANDMARKS, CRYSTAL_LANDMARKS = parse_landmark_data()


def parse_section(lines, start_marker, end_marker, pattern):
    collecting = False
    events = []
    for raw_line in lines:
        line = raw_line.strip()
        if not collecting:
            if line == start_marker:
                collecting = True
            continue
        if end_marker is not None and line == end_marker:
            break
        if not line or line.startswith(";"):
            continue
        match = pattern.search(line)
        if match:
            events.append(match.groups())
    return events


def parse_crystal_events(source_path: Path):
    lines = source_path.read_text().splitlines()
    warp_events = []
    for x, y, dest_map, warp_id in parse_section(lines, *SECTION_MARKERS["warp_events"]):
        warp_events.append(
            {
                "x": int(x),
                "y": int(y),
                "dest_map": dest_map,
                "dest_warp_id": int(warp_id),
            }
        )

    coord_events = []
    for x, y, scene, script in parse_section(lines, *SECTION_MARKERS["coord_events"]):
        coord_events.append(
            {
                "x": int(x),
                "y": int(y),
                "scene": scene,
                "script": script,
            }
        )

    bg_events = []
    for x, y, kind, script in parse_section(lines, *SECTION_MARKERS["bg_events"]):
        bg_events.append(
            {
                "x": int(x),
                "y": int(y),
                "kind": kind,
                "script": script,
            }
        )

    object_events = []
    for x, y, sprite, movement, range_x, range_y, script, flag in parse_section(lines, *SECTION_MARKERS["object_events"]):
        object_events.append(
            {
                "x": int(x),
                "y": int(y),
                "sprite": sprite,
                "movement": movement,
                "movement_range_x": int(range_x),
                "movement_range_y": int(range_y),
                "script": script,
                "flag": int(flag),
            }
        )

    return {
        "warp_events": warp_events,
        "coord_events": coord_events,
        "bg_events": bg_events,
        "object_events": object_events,
    }


def load_import_manifest():
    data = load_json(MAPS_PATH)
    return [normalize_manifest_entry(entry) for entry in data["maps"]]


def load_parser_expectations():
    if not PARSER_EXPECTATIONS_PATH.exists():
        return {}
    data = load_json(PARSER_EXPECTATIONS_PATH)
    return {entry["crystal_map"]: entry for entry in data.get("maps", [])}


def load_crystal_tilesets():
    data = load_json(CRYSTAL_TILESETS_PATH)
    tilesets = {}
    for entry in data.get("tilesets", []):
        crystal_tileset = entry["crystal_tileset"]
        block_translations = {}
        for block_id, translation in entry.get("block_translations", {}).items():
            try:
                normalized_id = int(block_id, 16)
            except ValueError as exc:
                raise ValueError(f"{CRYSTAL_TILESETS_PATH}: invalid block id '{block_id}'") from exc
            if translation["provenance"] not in {"emerald", "firered", "custom_gba"}:
                raise ValueError(
                    f"{CRYSTAL_TILESETS_PATH}: block {block_id} in {crystal_tileset} has invalid provenance '{translation['provenance']}'"
                )
            metatile_tokens = normalize_chunk_tokens(translation["metatiles"])
            border_tokens = normalize_chunk_tokens(translation.get("border_metatiles", metatile_tokens))
            block_translations[normalized_id] = {
                "provenance": translation["provenance"],
                "metatile_tokens": metatile_tokens,
                "metatiles": [parse_metatile_token(token) for token in metatile_tokens],
                "border_tokens": border_tokens,
                "border_metatiles": [parse_metatile_token(token) for token in border_tokens],
            }

        generated_spec = entry.get("generated")
        if generated_spec is not None:
            for normalized_id, translation in build_generated_block_translations(generated_spec).items():
                if normalized_id in block_translations:
                    raise ValueError(
                        f"{CRYSTAL_TILESETS_PATH}: duplicate block translation 0x{normalized_id:02X} in {crystal_tileset}"
                    )
                block_translations[normalized_id] = translation

        tilesets[crystal_tileset] = {
            "runtime_tileset": entry["runtime_tileset"],
            "block_translations": block_translations,
        }
    return tilesets


def extract_crystal_ir(crystal_map: str):
    metadata = CRYSTAL_MAP_DB.get(crystal_map)
    if metadata is None:
        raise ValueError(f"unknown Crystal map '{crystal_map}'")
    if metadata["blk_path"] is None:
        raise ValueError(f"{crystal_map}: no block source found in blocks.asm")

    source_asm = resolve_crystal_path(metadata["source_asm"])
    ir = dict(metadata)
    ir["events"] = parse_crystal_events(source_asm)
    ir["event_counts"] = {
        key: len(values)
        for key, values in ir["events"].items()
    }
    return ir


def block_bytes_for_ir(ir) -> bytes:
    return resolve_crystal_path(ir["blk_path"]).read_bytes()


def target_name_from_entry(entry):
    if "target_name" in entry:
        return entry["target_name"]
    if "target_map_json" in entry:
        return Path(entry["target_map_json"]).parent.name
    return entry["crystal_map"]


def target_name_constant_suffix(target_name: str) -> str:
    parts = []
    for chunk in target_name.split("_"):
        chunk = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", chunk)
        parts.append(chunk.upper())
    return "_".join(parts)


def region_map_section_from_landmark(landmark: str) -> str:
    if landmark == "LANDMARK_SPECIAL":
        return "MAPSEC_DYNAMIC"
    if landmark.startswith("LANDMARK_"):
        return "MAPSEC_" + landmark.removeprefix("LANDMARK_")
    return "MAPSEC_DYNAMIC"


def normalize_manifest_entry(entry):
    normalized = dict(entry)
    target_name = target_name_from_entry(normalized)
    normalized["target_name"] = target_name
    normalized.setdefault("target_map_json", f"data/maps/{target_name}/map.json")
    normalized.setdefault("target_scripts_path", f"data/maps/{target_name}/scripts.inc")
    normalized.setdefault("target_layout_dir", f"data/layouts/{target_name}")
    normalized.setdefault("layout_id", f"LAYOUT_{target_name_constant_suffix(target_name)}")
    normalized.setdefault("map_id", f"MAP_{target_name_constant_suffix(target_name)}")
    normalized.setdefault("region_map_section", region_map_section_from_landmark(CRYSTAL_MAP_DB[normalized["crystal_map"]]["landmark"]))
    normalized.setdefault("target_group", "gMapGroup_JohtoTowns" if CRYSTAL_MAP_DB[normalized["crystal_map"]]["environment"] in {"TOWN", "ROUTE"} else "gMapGroup_JohtoIndoors")
    normalized.setdefault("warp_mode", "exact")
    normalized.setdefault("bg_mode", "skip")
    normalized.setdefault("object_mode", "skip")
    normalized.setdefault("coord_mode", "skip")
    return normalized


def manifest_by_crystal_map(manifest):
    return {entry["crystal_map"]: entry for entry in manifest}


def load_target_map(entry):
    path = ROOT / entry["target_map_json"]
    if not path.exists():
        return None
    return load_json(path)


def load_target_map_index(manifest):
    by_crystal_map = {}
    by_crystal_map_id = {}
    by_map_id = {}
    for entry in manifest:
        map_path = ROOT / entry["target_map_json"]
        if not map_path.exists():
            continue
        map_data = load_json(map_path)
        crystal_metadata = CRYSTAL_MAP_DB[entry["crystal_map"]]
        index_entry = {
            "target_map_json": entry["target_map_json"],
            "crystal_map": entry["crystal_map"],
            "crystal_map_id": crystal_metadata["map_id"],
            "map_id": map_data["id"],
            "layout_id": map_data["layout"],
            "warp_count": len(map_data.get("warp_events", [])),
        }
        by_crystal_map[entry["crystal_map"]] = index_entry
        by_crystal_map_id[crystal_metadata["map_id"]] = index_entry
        by_map_id[map_data["id"]] = index_entry
    return {
        "by_crystal_map": by_crystal_map,
        "by_crystal_map_id": by_crystal_map_id,
        "by_map_id": by_map_id,
    }
