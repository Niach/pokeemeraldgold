#!/usr/bin/env python3

import json
import re
from pathlib import Path
from typing import Optional, Tuple

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
    "scene_scripts": ("def_scene_scripts", "def_callbacks"),
    "callbacks": ("def_callbacks", "def_warp_events"),
    "warp_events": ("def_warp_events", "def_coord_events"),
    "coord_events": ("def_coord_events", "def_bg_events"),
    "bg_events": ("def_bg_events", "def_object_events"),
    "object_events": ("def_object_events", None),
}

BLOCK_LABEL_RE = re.compile(r"^([A-Za-z0-9_]+)_Blocks:$")
INCBIN_RE = re.compile(r'^INCBIN\s+"([^"]+\.blk)"$')
NEWGROUP_RE = re.compile(r"^newgroup\s+([A-Z0-9_]+)$")
ENDGROUP_RE = re.compile(r"^endgroup$")
MAP_CONST_RE = re.compile(r"^map_const\s+([A-Z0-9_]+),\s*(\d+),\s*(\d+)$")
LANDMARK_ENTRY_RE = re.compile(r"^landmark\s+(-?\d+),\s*(-?\d+),\s*([A-Za-z0-9_]+)$")
LANDMARK_NAME_RE = re.compile(r'^([A-Za-z0-9_]+):\s+db\s+"([^"]*)@"$')
LABEL_RE = re.compile(r"^([A-Za-z0-9_.]+)::?$|^(\.[A-Za-z0-9_]+)$")
OBJECT_CONST_RE = re.compile(r"^const\s+([A-Z0-9_]+)$")
STRING_COMMAND_RE = re.compile(r'^([A-Za-z0-9_]+)\s+"(.*)"$')

TEXT_BLOCK_COMMANDS = {
    "text",
    "line",
    "cont",
    "para",
    "page",
    "prompt",
    "done",
    "text_ram",
    "text_decimal",
    "text_start",
}

MOVEMENT_COMMANDS = {
    "step",
    "slow_step",
    "big_step",
    "turn_head",
    "fix_facing",
    "remove_fixed_facing",
    "step_sleep",
    "jump_step",
    "step_end",
}

TEXT_REF_COMMANDS = {
    "writetext",
    "farwritetext",
    "jumptext",
    "jumptextfaceplayer",
}

MOVEMENT_REF_COMMANDS = {
    "applymovement",
}

STD_CALL_COMMANDS = {
    "jumpstd",
    "callstd",
}

BRANCH_COMMANDS = {
    "jump",
    "sjump",
    "goto",
    "call",
    "scall",
    "iftrue",
    "iffalse",
    "ifequal",
    "ifnotequal",
    "ifgreater",
    "ifless",
}

SCRIPT_TERMINATOR_COMMANDS = {
    "end",
    "endall",
    "endcallback",
    "farjump",
    "farjumptext",
    "goto",
    "jump",
    "jumpopenedtext",
    "jumpstd",
    "jumptext",
    "jumptextfaceplayer",
    "return",
    "sjump",
}

SCENE_REF_COMMANDS = {
    "setscene",
    "setmapscene",
}


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
    return split_asm_args_range(line, prefix, expected_count, expected_count)


def split_asm_args_range(line: str, prefix: str, min_count: int, max_count: int):
    if not line.startswith(prefix):
        raise ValueError(f"expected '{prefix}' line, found '{line}'")
    body = line[len(prefix):].strip()
    parts = [part.strip() for part in body.split(",")]
    if len(parts) < min_count or len(parts) > max_count:
        if min_count == max_count:
            expected_message = str(min_count)
        else:
            expected_message = f"{min_count}-{max_count}"
        raise ValueError(f"expected {expected_message} arguments for '{line}', found {len(parts)}")
    return parts


def parse_asm_value(token: str):
    token = token.strip()
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    return token


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


def iter_section_lines(lines, start_marker, end_marker):
    collecting = False
    for raw_line in lines:
        line = strip_asm_comment(raw_line)
        if not collecting:
            if line == start_marker:
                collecting = True
            continue
        if end_marker is not None and line == end_marker:
            break
        if not line:
            continue
        yield line


def parse_crystal_events(source_path: Path):
    lines = source_path.read_text().splitlines()

    scene_scripts = []
    for line in iter_section_lines(lines, *SECTION_MARKERS["scene_scripts"]):
        if line.startswith("scene_script "):
            parts = split_asm_args_range(line, "scene_script ", 1, 2)
            scene_scripts.append(
                {
                    "script": parts[0],
                    "scene_id": parts[1] if len(parts) == 2 else None,
                }
            )
        elif line.startswith("scene_const "):
            parts = split_asm_args(line, "scene_const ", 1)
            scene_scripts.append(
                {
                    "script": None,
                    "scene_id": parts[0],
                }
            )

    callbacks = []
    for line in iter_section_lines(lines, *SECTION_MARKERS["callbacks"]):
        if not line.startswith("callback "):
            continue
        callback_type, script = split_asm_args(line, "callback ", 2)
        callbacks.append(
            {
                "type": callback_type,
                "script": script,
            }
        )

    warp_events = []
    for line in iter_section_lines(lines, *SECTION_MARKERS["warp_events"]):
        if not line.startswith("warp_event "):
            continue
        x, y, dest_map, warp_id = split_asm_args(line, "warp_event ", 4)
        warp_events.append(
            {
                "x": int(x),
                "y": int(y),
                "dest_map": dest_map,
                "dest_warp_id": int(warp_id),
            }
        )

    coord_events = []
    for line in iter_section_lines(lines, *SECTION_MARKERS["coord_events"]):
        if not line.startswith("coord_event "):
            continue
        x, y, scene, script = split_asm_args(line, "coord_event ", 4)
        coord_events.append(
            {
                "x": int(x),
                "y": int(y),
                "scene": scene,
                "script": script,
            }
        )

    bg_events = []
    for line in iter_section_lines(lines, *SECTION_MARKERS["bg_events"]):
        if not line.startswith("bg_event "):
            continue
        x, y, kind, script = split_asm_args(line, "bg_event ", 4)
        bg_events.append(
            {
                "x": int(x),
                "y": int(y),
                "kind": kind,
                "script": script,
            }
        )

    object_events = []
    for line in iter_section_lines(lines, *SECTION_MARKERS["object_events"]):
        if not line.startswith("object_event "):
            continue
        (
            x,
            y,
            sprite,
            movement,
            range_x,
            range_y,
            time_start,
            time_end,
            palette,
            object_type,
            sight_range,
            script,
            flag,
        ) = split_asm_args(line, "object_event ", 13)
        object_events.append(
            {
                "x": int(x),
                "y": int(y),
                "sprite": sprite,
                "movement": movement,
                "movement_range_x": int(range_x),
                "movement_range_y": int(range_y),
                "time_range_start": parse_asm_value(time_start),
                "time_range_end": parse_asm_value(time_end),
                "palette": parse_asm_value(palette),
                "object_type": object_type,
                "trainer_sight_range": parse_asm_value(sight_range),
                "script": script,
                "flag": parse_asm_value(flag),
            }
        )

    return {
        "scene_scripts": scene_scripts,
        "callbacks": callbacks,
        "warp_events": warp_events,
        "coord_events": coord_events,
        "bg_events": bg_events,
        "object_events": object_events,
    }


def parse_object_constants(source_path: Path):
    object_consts = []
    collecting = False

    for raw_line in source_path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue
        if line == "object_const_def":
            collecting = True
            continue
        if not collecting:
            continue

        match = OBJECT_CONST_RE.match(line)
        if match:
            object_consts.append(match.group(1))
            continue
        break

    return object_consts


def scope_crystal_label(raw_label: str, current_global_label: Optional[str]) -> Tuple[str, Optional[str]]:
    if raw_label.startswith("."):
        if current_global_label is None:
            return raw_label, current_global_label
        return f"{current_global_label}{raw_label}", current_global_label
    return raw_label, raw_label


def parse_label_blocks(source_path: Path):
    blocks = {}
    scopes = {}
    order = []
    current_label = None
    current_lines = []
    current_scope = None
    current_global_label = None

    for raw_line in source_path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue

        label_match = LABEL_RE.match(line)
        if label_match:
            if current_label is not None:
                blocks[current_label] = current_lines
                scopes[current_label] = current_scope
                order.append(current_label)
            label_name = label_match.group(1) or label_match.group(2)
            current_label, current_global_label = scope_crystal_label(label_name, current_global_label)
            current_scope = current_global_label
            current_lines = []
            continue

        if current_label is not None:
            current_lines.append(line)

    if current_label is not None:
        blocks[current_label] = current_lines
        scopes[current_label] = current_scope
        order.append(current_label)

    return blocks, scopes, order


def classify_label_block(lines):
    if not lines:
        return "empty"

    first_command = lines[0].split()[0]
    if first_command in TEXT_BLOCK_COMMANDS:
        return "text"
    if first_command in MOVEMENT_COMMANDS:
        return "movement"
    return "script"


def parse_text_block(lines):
    commands = []
    for line in lines:
        command = line.split()[0]
        value = line[len(command):].strip()
        string_match = STRING_COMMAND_RE.match(line)
        commands.append(
            {
                "command": command,
                "value": string_match.group(2) if string_match else value,
            }
        )

    return {
        "raw_lines": lines,
        "commands": commands,
    }


def parse_movement_block(lines):
    steps = []
    for line in lines:
        command = line.split()[0]
        args = line[len(command):].strip().split()
        steps.append(
            {
                "command": command,
                "args": args,
            }
        )

    return {
        "raw_lines": lines,
        "steps": steps,
    }


def normalize_script_arg(arg: str, current_scope: Optional[str]) -> str:
    if current_scope is not None and arg.startswith("."):
        return f"{current_scope}{arg}"
    return arg


def parse_script_block(lines, current_scope=None):
    commands = []
    for line in lines:
        command = line.split()[0]
        arg_text = line[len(command):].strip()
        args = [normalize_script_arg(part.strip(), current_scope) for part in arg_text.split(",")] if arg_text else []
        commands.append(
            {
                "command": command,
                "args": args,
                "raw": line,
            }
        )

    return {
        "raw_lines": lines,
        "commands": commands,
        "first_command": commands[0]["command"] if commands else None,
    }


def extract_script_dependencies(script_block, known_labels):
    label_refs = set()
    text_refs = set()
    movement_refs = set()
    scene_refs = set()
    std_calls = set()

    for command in script_block["commands"]:
        name = command["command"]
        args = command["args"]

        if name in TEXT_REF_COMMANDS and args and args[0] in known_labels:
            text_refs.add(args[0])

        if name == "trainer" and len(args) >= 5:
            if args[3] in known_labels:
                text_refs.add(args[3])
            if args[4] in known_labels:
                text_refs.add(args[4])
            if len(args) >= 7 and args[6] in known_labels:
                label_refs.add(args[6])

        if name in MOVEMENT_REF_COMMANDS and len(args) > 1 and args[1] in known_labels:
            movement_refs.add(args[1])

        if name in STD_CALL_COMMANDS and args:
            std_calls.add(args[0])

        if name in BRANCH_COMMANDS and args and args[-1] in known_labels:
            label_refs.add(args[-1])

        if name == "setscene" and args:
            scene_refs.add(args[0])
        elif name == "setmapscene" and len(args) > 1:
            scene_refs.add(args[1])

    return {
        "label_refs": sorted(label_refs),
        "text_refs": sorted(text_refs),
        "movement_refs": sorted(movement_refs),
        "scene_refs": sorted(scene_refs),
        "std_calls": sorted(std_calls),
    }


def parse_crystal_script_assets(source_path: Path, events: dict):
    blocks, scopes, order = parse_label_blocks(source_path)
    scripts = {}
    texts = {}
    movements = {}
    dependencies = {}
    std_calls = set()
    known_labels = set(blocks)

    for label, lines in blocks.items():
        block_kind = classify_label_block(lines)
        if block_kind == "text":
            texts[label] = parse_text_block(lines)
        elif block_kind == "movement":
            movements[label] = parse_movement_block(lines)
        elif block_kind == "script":
            scripts[label] = parse_script_block(lines, scopes.get(label))

    script_labels_in_order = [label for label in order if label in scripts]
    for index, label in enumerate(script_labels_in_order[:-1]):
        script_block = scripts[label]
        commands = script_block["commands"]
        if commands and commands[-1]["command"] not in SCRIPT_TERMINATOR_COMMANDS:
            script_block["fallthrough_label"] = script_labels_in_order[index + 1]

    for label, script_block in scripts.items():
        refs = extract_script_dependencies(script_block, known_labels)
        if script_block.get("fallthrough_label") is not None:
            refs["label_refs"] = sorted(set(refs["label_refs"]) | {script_block["fallthrough_label"]})
        script_block.update(refs)
        dependencies[label] = refs
        std_calls.update(refs["std_calls"])

    scene_ids = []
    for scene in events["scene_scripts"]:
        if scene["scene_id"] is not None:
            scene_ids.append(scene["scene_id"])
    for callback in events["callbacks"]:
        if callback["script"] in scripts:
            scene_ids.extend(scripts[callback["script"]]["scene_refs"])
    for script in scripts.values():
        scene_ids.extend(script["scene_refs"])

    return {
        "object_consts": parse_object_constants(source_path),
        "scene_ids": sorted(set(scene_ids)),
        "scripts": scripts,
        "texts": texts,
        "movements": movements,
        "std_calls": sorted(std_calls),
        "dependencies": dependencies,
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


SUBSTITUTE_TAGS = {
    "pokegear": ("#GEAR", "Pokegear", "PHONE_", "addcellnum", "checkcellnum", "specialphonecall"),
    "radio": ("Radio", "radio", "MUSIC_POKEMON_TALK", "Radio1Script", "PokemonTalk"),
    "decorations": ("describedecoration", "ToggleDecorationsVisibility", "ToggleMaptileDecorations", "DECODESC_"),
    "day_time": ("VAR_WEEKDAY", "checktime", "SetDayOfWeek", "DST", "InitialSetDSTFlag", "InitialClearDSTFlag"),
}


def detect_substitute_tags(source_text: str):
    tags = []
    for tag, needles in SUBSTITUTE_TAGS.items():
        if any(needle in source_text for needle in needles):
            tags.append(tag)
    return tags


def extract_crystal_ir(crystal_map: str):
    metadata = CRYSTAL_MAP_DB.get(crystal_map)
    if metadata is None:
        raise ValueError(f"unknown Crystal map '{crystal_map}'")
    if metadata["blk_path"] is None:
        raise ValueError(f"{crystal_map}: no block source found in blocks.asm")

    source_asm = resolve_crystal_path(metadata["source_asm"])
    source_text = source_asm.read_text()
    ir = dict(metadata)
    ir["events"] = parse_crystal_events(source_asm)
    ir.update(parse_crystal_script_assets(source_asm, ir["events"]))
    ir["substitute_tags"] = detect_substitute_tags(source_text)
    ir["event_counts"] = {
        key: len(values)
        for key, values in ir["events"].items()
    }
    return ir


def block_bytes_for_ir(ir) -> bytes:
    return resolve_crystal_path(ir["blk_path"]).read_bytes()


def crystal_connection_offset_to_emerald(offset: int) -> int:
    return offset * 2


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
    landmark_overrides = {
        "LANDMARK_BURNED_TOWER": "MAPSEC_ECRUTEAK_CITY",
        "LANDMARK_LIGHTHOUSE": "MAPSEC_OLIVINE_CITY",
        "LANDMARK_MT_MORTAR": "MAPSEC_ROUTE_42",
        "LANDMARK_TIN_TOWER": "MAPSEC_ECRUTEAK_CITY",
        "LANDMARK_WHIRL_ISLANDS": "MAPSEC_ROUTE_41",
    }
    overridden = landmark_overrides.get(landmark)
    if overridden is not None:
        return overridden
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
