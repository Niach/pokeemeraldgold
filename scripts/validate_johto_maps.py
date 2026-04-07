#!/usr/bin/env python3

import json
import struct
import sys
from pathlib import Path

from johto_import_common import (
    HEAL_LOCATIONS_PATH,
    IR_DIR,
    LAYOUTS,
    ROOT,
    block_bytes_for_ir,
    extract_crystal_ir,
    load_crystal_tilesets,
    load_import_manifest,
    load_json,
    load_parser_expectations,
    load_target_map,
    load_target_map_index,
)


CRYSTAL_TO_EMERALD_DIRECTION = {
    "north": "up",
    "south": "down",
    "west": "left",
    "east": "right",
}

MAPGRID_METATILE_ID_MASK = 0x03FF
NUM_METATILES_IN_PRIMARY = 512
METATILE_BEHAVIOR_MASK = 0x00FF
EXPECTED_GENERATED_PALETTE_SLOTS = {6, 7, 8, 9, 10, 11}
MB_NON_ANIMATED_DOOR = 0x60
PLAYERS_ROOM_RUNTIME_DIR = ROOT / "data" / "tilesets" / "secondary" / "johto_players_room"
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"


def fail(message, errors):
    errors.append(message)


def resolve_target_by_crystal_map(target_map_index, crystal_map: str):
    return target_map_index["by_crystal_map"].get(crystal_map)


def resolve_target_by_crystal_map_id(target_map_index, crystal_map_id: str):
    return target_map_index["by_crystal_map_id"].get(crystal_map_id)


def validate_saved_ir(entry, ir, errors):
    ir_path = IR_DIR / f"{entry['crystal_map']}.json"
    if not ir_path.exists():
        fail(f"{entry['id']}: missing generated IR {ir_path}", errors)
        return
    saved_ir = load_json(ir_path)
    if saved_ir != ir:
        fail(f"{entry['id']}: saved IR {ir_path} is out of date with current Crystal extraction", errors)


def validate_parser_expectations(expectations, entry, ir, errors):
    expected = expectations.get(entry["crystal_map"])
    if expected is None:
        return

    for field in ("tileset", "width_blocks", "height_blocks", "border_block", "blk_path"):
        if ir[field] != expected[field]:
            fail(
                f"{entry['id']}: parser field '{field}' value {ir[field]!r} != expected {expected[field]!r}",
                errors,
            )

    if ir["connections"] != expected["connections"]:
        fail(
            f"{entry['id']}: parser connections {ir['connections']} != expected {expected['connections']}",
            errors,
        )

    if ir["event_counts"] != expected["event_counts"]:
        fail(
            f"{entry['id']}: parser event counts {ir['event_counts']} != expected {expected['event_counts']}",
            errors,
        )


def validate_translation_coverage(entry, ir, crystal_tilesets, errors):
    if "target_map_json" not in entry:
        return

    tileset = crystal_tilesets.get(ir["tileset"])
    if tileset is None:
        fail(f"{entry['id']}: missing crystal tileset translation for {ir['tileset']}", errors)
        return

    used_blocks = set(block_bytes_for_ir(ir))
    used_blocks.add(int(ir["border_block"], 16))
    missing = sorted(block_id for block_id in used_blocks if block_id not in tileset["block_translations"])
    if missing:
        fail(
            f"{entry['id']}: missing {ir['tileset']} block translations {', '.join(f'0x{block_id:02X}' for block_id in missing)}",
            errors,
        )


def validate_layout(entry, ir, crystal_tilesets, errors):
    if "target_map_json" not in entry:
        return

    tileset = crystal_tilesets.get(ir["tileset"])
    if tileset is None:
        return

    map_data = load_target_map(entry)
    layout = LAYOUTS[map_data["layout"]]
    expected_width = ir["width_blocks"] * 2
    expected_height = ir["height_blocks"] * 2

    if layout["width"] != expected_width or layout["height"] != expected_height:
        fail(
            f"{entry['id']}: layout {map_data['layout']} dimensions {(layout['width'], layout['height'])} != exact Crystal size {(expected_width, expected_height)}",
            errors,
        )
    if layout["secondary_tileset"] != tileset["runtime_tileset"]:
        fail(
            f"{entry['id']}: layout {map_data['layout']} secondary tileset {layout['secondary_tileset']} != expected {tileset['runtime_tileset']}",
            errors,
        )

    blockdata_path = ROOT / layout["blockdata_filepath"]
    border_path = ROOT / layout["border_filepath"]
    expected_blockdata_bytes = expected_width * expected_height * 2
    if not blockdata_path.exists():
        fail(f"{entry['id']}: missing blockdata {blockdata_path}", errors)
    else:
        actual_size = len(blockdata_path.read_bytes())
        if actual_size != expected_blockdata_bytes:
            fail(
                f"{entry['id']}: blockdata size {actual_size} != expected {expected_blockdata_bytes}",
                errors,
            )

    border_block_id = int(ir["border_block"], 16)
    translation = tileset["block_translations"].get(border_block_id)
    if translation is None:
        return

    if not border_path.exists():
        fail(f"{entry['id']}: missing border {border_path}", errors)
    else:
        expected_border = tuple(translation["border_metatiles"])
        actual_border = struct.unpack("<4H", border_path.read_bytes())
        if actual_border != expected_border:
            fail(
                f"{entry['id']}: border {tuple(f'{value:04X}' for value in actual_border)} != expected {tuple(f'{value:04X}' for value in expected_border)}",
                errors,
            )


def validate_warps(entry, map_data, ir, target_map_index, errors):
    if entry.get("warp_mode") != "exact":
        return
    generated = map_data.get("warp_events", [])
    expected = ir["events"]["warp_events"]
    if len(generated) != len(expected):
        fail(f"{entry['id']}: warp count {len(generated)} != crystal {len(expected)}", errors)
        return
    for index, (event, crystal) in enumerate(zip(generated, expected)):
        target = resolve_target_by_crystal_map_id(target_map_index, crystal["dest_map"])
        if target is None:
            target = resolve_target_by_crystal_map(target_map_index, crystal["dest_map"])
        if target is None:
            continue

        if (event["x"], event["y"]) != (crystal["x"], crystal["y"]):
            fail(
                f"{entry['id']}: warp {index} at {(event['x'], event['y'])} != crystal {(crystal['x'], crystal['y'])}",
                errors,
            )

        expected_dest_warp_id = crystal["dest_warp_id"] - 1
        if expected_dest_warp_id < 0:
            fail(f"{entry['id']}: warp {index} has invalid Crystal warp id {crystal['dest_warp_id']}", errors)
            continue

        if target["warp_count"] <= expected_dest_warp_id:
            fail(
                f"{entry['id']}: warp {index} targets {target['map_id']} warp {expected_dest_warp_id}, "
                f"but only {target['warp_count']} warp(s) exist",
                errors,
            )
            continue

        actual_dest_warp_id = int(event["dest_warp_id"])
        if event["dest_map"] != target["map_id"] or actual_dest_warp_id != expected_dest_warp_id:
            fail(
                f"{entry['id']}: warp {index} destination {(event['dest_map'], actual_dest_warp_id)} "
                f"!= expected {(target['map_id'], expected_dest_warp_id)}",
                errors,
            )


def validate_bg_events(entry, map_data, ir, errors):
    if entry.get("bg_mode") != "exact":
        return
    generated = {(event["x"], event["y"]) for event in map_data.get("bg_events", [])}
    expected = {(event["x"], event["y"]) for event in ir["events"]["bg_events"]}
    if generated != expected:
        fail(f"{entry['id']}: bg coords {sorted(generated)} != crystal {sorted(expected)}", errors)


def validate_object_events(entry, map_data, ir, errors):
    mode = entry.get("object_mode")
    generated = map_data.get("object_events", [])
    crystal = ir["events"]["object_events"]

    if mode == "exact":
        expected = {(event["x"], event["y"]) for event in crystal}
        actual = {(event["x"], event["y"]) for event in generated}
        if actual != expected:
            fail(f"{entry['id']}: object coords {sorted(actual)} != crystal {sorted(expected)}", errors)
        return

    if mode == "subset":
        expected = {(crystal[index]["x"], crystal[index]["y"]) for index in entry["object_indices"]}
        actual = {(event["x"], event["y"]) for event in generated}
        if actual != expected:
            fail(f"{entry['id']}: object subset coords {sorted(actual)} != crystal {sorted(expected)}", errors)
        return

    if mode == "remap":
        indices = entry["object_indices"]
        if len(generated) != len(indices):
            fail(f"{entry['id']}: object count {len(generated)} != remap size {len(indices)}", errors)
            return
        for event, index in zip(generated, indices):
            expected_coord = (crystal[index]["x"], crystal[index]["y"])
            if (event["x"], event["y"]) != expected_coord:
                fail(
                    f"{entry['id']}: remapped object at {(event['x'], event['y'])} != crystal {expected_coord}",
                    errors,
                )


def validate_coord_events(entry, map_data, ir, errors):
    mode = entry.get("coord_mode")
    generated = map_data.get("coord_events", [])
    crystal = ir["events"]["coord_events"]

    if mode == "exact":
        if len(generated) != len(crystal):
            fail(f"{entry['id']}: coord count {len(generated)} != crystal {len(crystal)}", errors)
            return
        for index, (event, crystal_event) in enumerate(zip(generated, crystal)):
            expected_coord = (crystal_event["x"], crystal_event["y"])
            if (event["x"], event["y"]) != expected_coord:
                fail(
                    f"{entry['id']}: coord {index} at {(event['x'], event['y'])} != crystal {expected_coord}",
                    errors,
                )
        return

    if mode == "repeat_values":
        expected = {
            (event["x"], event["y"], value)
            for event in crystal
            for value in entry["coord_repeat_values"]
        }
        actual = {
            (event["x"], event["y"], str(event["var_value"]))
            for event in generated
        }
        if actual != expected:
            fail(f"{entry['id']}: repeated coord events {sorted(actual)} != crystal {sorted(expected)}", errors)


def validate_connections(entry, map_data, ir, target_map_index, errors):
    if "target_map_json" not in entry or not ir["connections"]:
        return

    expected = [
        {
            "map": resolve_target_by_crystal_map(target_map_index, connection["map"])["map_id"],
            "offset": connection["offset"],
            "direction": CRYSTAL_TO_EMERALD_DIRECTION[connection["direction"]],
        }
        for connection in ir["connections"]
        if resolve_target_by_crystal_map(target_map_index, connection["map"]) is not None
    ]
    actual = map_data.get("connections") or []
    if actual != expected:
        fail(f"{entry['id']}: connections {actual} != expected {expected}", errors)


def validate_heal_location(entry, errors):
    if "heal_location_id" not in entry or "heal_spawn_local" not in entry:
        return

    heal_locations = load_json(HEAL_LOCATIONS_PATH)["heal_locations"]
    expected = tuple(entry["heal_spawn_local"])
    for heal_location in heal_locations:
        if heal_location["id"] != entry["heal_location_id"]:
            continue
        actual = (heal_location["x"], heal_location["y"])
        if actual != expected:
            fail(f"{entry['id']}: heal location {actual} != expected {expected}", errors)
        return
    fail(f"{entry['id']}: heal location '{entry['heal_location_id']}' not found", errors)


def load_metatile_words(path: Path):
    raw = path.read_bytes()
    return struct.unpack("<" + "H" * (len(raw) // 2), raw)


def load_tileset_runtime_lookup():
    atlas = load_json(ATLAS_PATH)
    families = {family["id"]: family for family in atlas["families"]}
    lookup = {family["symbol"]: ROOT / family["runtime_dir"] for family in atlas["families"]}
    for alias in atlas.get("aliases", []):
        lookup[alias["symbol"]] = ROOT / families[alias["family"]]["runtime_dir"]
    return lookup


def validate_map_stair_warp_behavior(map_json_relpath: str, warp_index: int, runtime_lookup, errors):
    map_data = load_json(ROOT / map_json_relpath)
    layout = LAYOUTS[map_data["layout"]]
    runtime_dir = runtime_lookup[layout["secondary_tileset"]]
    metatile_attrs = struct.unpack(
        "<" + "H" * ((runtime_dir / "metatile_attributes.bin").stat().st_size // 2),
        (runtime_dir / "metatile_attributes.bin").read_bytes(),
    )
    blockdata = struct.unpack(
        "<" + "H" * ((ROOT / layout["blockdata_filepath"]).stat().st_size // 2),
        (ROOT / layout["blockdata_filepath"]).read_bytes(),
    )

    warp = map_data["warp_events"][warp_index]
    metatile_entry = blockdata[warp["y"] * layout["width"] + warp["x"]]
    metatile_id = metatile_entry & MAPGRID_METATILE_ID_MASK
    if metatile_id < NUM_METATILES_IN_PRIMARY:
        fail(f"{map_json_relpath}: warp {warp_index} does not land on a secondary metatile", errors)
        return

    attr = metatile_attrs[metatile_id - NUM_METATILES_IN_PRIMARY]
    behavior = attr & METATILE_BEHAVIOR_MASK
    if behavior != MB_NON_ANIMATED_DOOR:
        fail(
            f"{map_json_relpath}: warp {warp_index} metatile behavior {behavior:#04x} != expected {MB_NON_ANIMATED_DOOR:#04x}",
            errors,
        )


def validate_generated_room_runtime(errors):
    metatile_words = load_metatile_words(PLAYERS_ROOM_RUNTIME_DIR / "metatiles.bin")

    used_palette_slots = {
        (word >> 12) & 0xF
        for word in metatile_words
        if word
    }
    if 0 in used_palette_slots:
        fail("johto_players_room: generated metatiles still use palette slot 0 for visible tiles", errors)

    unexpected_slots = sorted(slot for slot in used_palette_slots if slot not in EXPECTED_GENERATED_PALETTE_SLOTS)
    if unexpected_slots:
        fail(
            f"johto_players_room: generated metatiles use unexpected palette slots {unexpected_slots}",
            errors,
        )

    runtime_lookup = load_tileset_runtime_lookup()
    for rel_path, warp_index in (
        ("data/maps/NewBarkTown_PlayersHouse_2F/map.json", 0),
        ("data/maps/NewBarkTown_PlayersHouse_1F/map.json", 2),
    ):
        validate_map_stair_warp_behavior(rel_path, warp_index, runtime_lookup, errors)


def validate_events(entry, ir, target_map_index, errors):
    if "target_map_json" not in entry:
        return
    map_data = load_target_map(entry)
    validate_warps(entry, map_data, ir, target_map_index, errors)
    validate_bg_events(entry, map_data, ir, errors)
    validate_object_events(entry, map_data, ir, errors)
    validate_coord_events(entry, map_data, ir, errors)
    validate_connections(entry, map_data, ir, target_map_index, errors)
    validate_heal_location(entry, errors)


def main():
    errors = []
    manifest = load_import_manifest()
    crystal_tilesets = load_crystal_tilesets()
    expectations = load_parser_expectations()
    target_map_index = load_target_map_index(manifest)

    for entry in manifest:
        ir = extract_crystal_ir(entry["crystal_map"])
        validate_saved_ir(entry, ir, errors)
        validate_parser_expectations(expectations, entry, ir, errors)
        validate_translation_coverage(entry, ir, crystal_tilesets, errors)
        validate_layout(entry, ir, crystal_tilesets, errors)
        validate_events(entry, ir, target_map_index, errors)
    validate_generated_room_runtime(errors)

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    print("Johto import validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
