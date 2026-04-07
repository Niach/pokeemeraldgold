#!/usr/bin/env python3

import argparse
import struct
import sys
from typing import Optional

from johto_import_common import (
    AUTO_JOHTO_SCRIPTS_PATH,
    HEAL_LOCATIONS_PATH,
    IR_DIR,
    LAYOUTS_PATH,
    MAP_GROUPS_PATH,
    REGION_MAP_SECTIONS_PATH,
    ROOT,
    CRYSTAL_LANDMARKS,
    block_bytes_for_ir,
    extract_crystal_ir,
    load_crystal_tilesets,
    load_import_manifest,
    load_json,
    load_target_map,
    load_target_map_index,
    save_json,
)


CRYSTAL_TO_EMERALD_DIRECTION = {
    "north": "up",
    "south": "down",
    "west": "left",
    "east": "right",
}


def resolve_target_by_crystal_map(target_map_index, crystal_map: str):
    return target_map_index["by_crystal_map"].get(crystal_map)


def resolve_target_by_crystal_map_id(target_map_index, crystal_map_id: str):
    return target_map_index["by_crystal_map_id"].get(crystal_map_id)


def write_ir_files(manifest):
    IR_DIR.mkdir(parents=True, exist_ok=True)
    ir_index = {}
    for entry in manifest:
        ir = extract_crystal_ir(entry["crystal_map"])
        ir_path = IR_DIR / f"{entry['crystal_map']}.json"
        save_json(ir_path, ir)
        print(f"updated {ir_path.relative_to(ROOT)} from {entry['crystal_map']}")
        ir_index[entry["crystal_map"]] = ir
    return ir_index


def extract_ir_index(manifest):
    return {
        entry["crystal_map"]: extract_crystal_ir(entry["crystal_map"])
        for entry in manifest
    }


def choose_primary_tileset(environment: str) -> str:
    if environment in {"INDOOR", "GATE"}:
        return "gTileset_Building"
    return "gTileset_General"


def choose_map_type(environment: str) -> str:
    return {
        "TOWN": "MAP_TYPE_TOWN",
        "ROUTE": "MAP_TYPE_ROUTE",
        "INDOOR": "MAP_TYPE_INDOOR",
        "GATE": "MAP_TYPE_INDOOR",
        "CAVE": "MAP_TYPE_UNDERGROUND",
        "DUNGEON": "MAP_TYPE_UNDERGROUND",
    }[environment]


def choose_music(ir, entry) -> str:
    if "music" in entry:
        return entry["music"]
    environment = ir["environment"]
    if environment == "ROUTE":
        return "MUS_ROUTE101"
    if environment in {"CAVE", "DUNGEON"}:
        return "MUS_CAVE_OF_ORIGIN"
    return "MUS_LITTLEROOT"


def choose_weather(environment: str) -> str:
    return "WEATHER_SUNNY" if environment in {"TOWN", "ROUTE"} else "WEATHER_NONE"


def placeholder_warp_events(ir):
    return [
        {
            "x": 0,
            "y": 0,
            "elevation": 0,
            "dest_map": "MAP_DYNAMIC",
            "dest_warp_id": "0",
        }
        for _ in ir["events"]["warp_events"]
    ]


def region_section_from_landmark(ir, entry) -> Optional[dict]:
    if entry["region_map_section"] == "MAPSEC_DYNAMIC":
        return None
    landmark = CRYSTAL_LANDMARKS.get(ir["landmark"])
    if landmark is None:
        return None
    return {
        "id": entry["region_map_section"],
        "name": landmark["name"].replace("<BSP>", " "),
        "x": max(0, (landmark["x"] - 20) // 8),
        "y": max(0, (landmark["y"] - 20) // 8),
        "width": 1,
        "height": 1,
    }


def ensure_region_sections(manifest, ir_index):
    data = load_json(REGION_MAP_SECTIONS_PATH)
    sections = data["map_sections"]
    by_id = {section["id"]: section for section in sections}
    changed = False

    for entry in manifest:
        section = region_section_from_landmark(ir_index[entry["crystal_map"]], entry)
        if section is None or section["id"] in by_id:
            continue
        sections.append(section)
        by_id[section["id"]] = section
        changed = True

    if changed:
        save_json(REGION_MAP_SECTIONS_PATH, data)
        print(f"updated {REGION_MAP_SECTIONS_PATH.relative_to(ROOT)}")


def ensure_map_groups(manifest, ir_index):
    data = load_json(MAP_GROUPS_PATH)
    changed = False
    for entry in manifest:
        group_name = entry["target_group"]
        maps = data[group_name]
        if entry["target_name"] not in maps:
            maps.append(entry["target_name"])
            changed = True

    if changed:
        save_json(MAP_GROUPS_PATH, data)
        print(f"updated {MAP_GROUPS_PATH.relative_to(ROOT)}")


def ensure_layouts(manifest, ir_index, crystal_tilesets):
    data = load_json(LAYOUTS_PATH)
    layouts = data["layouts"]
    by_id = {layout["id"]: layout for layout in layouts}
    changed = False

    for entry in manifest:
        ir = ir_index[entry["crystal_map"]]
        tileset = crystal_tilesets[ir["tileset"]]
        layout = by_id.get(entry["layout_id"])
        desired = {
            "id": entry["layout_id"],
            "name": f"{entry['target_name']}_Layout",
            "width": ir["width_blocks"] * 2,
            "height": ir["height_blocks"] * 2,
            "primary_tileset": choose_primary_tileset(ir["environment"]),
            "secondary_tileset": tileset["runtime_tileset"],
            "border_filepath": f"{entry['target_layout_dir']}/border.bin",
            "blockdata_filepath": f"{entry['target_layout_dir']}/map.bin",
        }
        if layout is None:
            layouts.append(desired)
            by_id[entry["layout_id"]] = desired
            changed = True
        elif any(layout.get(key) != value for key, value in desired.items()):
            layout.update(desired)
            changed = True

        layout_dir = ROOT / entry["target_layout_dir"]
        layout_dir.mkdir(parents=True, exist_ok=True)
        for filename in ("map.bin", "border.bin"):
            path = layout_dir / filename
            if not path.exists():
                path.write_bytes(b"")

    if changed:
        save_json(LAYOUTS_PATH, data)
        print(f"updated {LAYOUTS_PATH.relative_to(ROOT)}")


def scaffold_map_json(entry, ir):
    map_path = ROOT / entry["target_map_json"]
    existed = map_path.exists()
    map_data = load_json(map_path) if existed else {
        "id": entry["map_id"],
        "name": entry["target_name"],
        "layout": entry["layout_id"],
        "music": choose_music(ir, entry),
        "region_map_section": entry["region_map_section"],
        "requires_flash": False,
        "weather": choose_weather(ir["environment"]),
        "map_type": choose_map_type(ir["environment"]),
        "allow_cycling": ir["environment"] in {"TOWN", "ROUTE"},
        "allow_escaping": False,
        "allow_running": ir["environment"] in {"TOWN", "ROUTE"},
        "show_map_name": ir["environment"] in {"TOWN", "ROUTE"},
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [],
        "warp_events": placeholder_warp_events(ir),
        "coord_events": [],
        "bg_events": [],
    }

    map_data["id"] = entry["map_id"]
    map_data["name"] = entry["target_name"]
    map_data["layout"] = entry["layout_id"]
    map_data["region_map_section"] = entry["region_map_section"]
    map_data["map_type"] = choose_map_type(ir["environment"])
    map_data["weather"] = choose_weather(ir["environment"])

    if not existed:
        save_json(map_path, map_data)
        print(f"created {map_path.relative_to(ROOT)}")
    elif entry.get("warp_mode") == "exact" and "warp_events" not in map_data:
        map_data["warp_events"] = placeholder_warp_events(ir)
        save_json(map_path, map_data)
        print(f"updated {map_path.relative_to(ROOT)}")


def ensure_scripts_placeholder(entry):
    scripts_path = ROOT / entry["target_scripts_path"]
    if scripts_path.exists():
        return
    scripts_path.parent.mkdir(parents=True, exist_ok=True)
    scripts_path.write_text(f"{entry['target_name']}_MapScripts::\n\t.byte 0\n")
    print(f"created {scripts_path.relative_to(ROOT)}")


def write_auto_script_includes(manifest):
    event_scripts_path = ROOT / "data" / "event_scripts.s"
    manual_includes = set()
    for raw_line in event_scripts_path.read_text().splitlines():
        marker = '.include "data/maps/'
        if marker not in raw_line:
            continue
        fragment = raw_line.split(marker, 1)[1]
        manual_includes.add(fragment.split("/scripts.inc", 1)[0])

    lines = []
    for entry in manifest:
        if entry["target_name"] in manual_includes:
            continue
        scripts_path = ROOT / entry["target_scripts_path"]
        if not scripts_path.exists():
            continue
        lines.append(f'\t.include "data/maps/{entry["target_name"]}/scripts.inc"')

    AUTO_JOHTO_SCRIPTS_PATH.write_text("\n".join(lines) + ("\n" if lines else ""))
    print(f"updated {AUTO_JOHTO_SCRIPTS_PATH.relative_to(ROOT)}")


def scaffold_targets(manifest, ir_index, crystal_tilesets):
    ensure_region_sections(manifest, ir_index)
    ensure_map_groups(manifest, ir_index)
    ensure_layouts(manifest, ir_index, crystal_tilesets)
    for entry in manifest:
        ir = ir_index[entry["crystal_map"]]
        scaffold_map_json(entry, ir)
        ensure_scripts_placeholder(entry)
    write_auto_script_includes(manifest)


def compile_layout(entry, ir, crystal_tilesets):
    if "target_map_json" not in entry:
        return

    map_data = load_target_map(entry)
    layouts = {layout["id"]: layout for layout in load_json(LAYOUTS_PATH)["layouts"]}
    layout = layouts[map_data["layout"]]
    tileset = crystal_tilesets[ir["tileset"]]
    expected_width = ir["width_blocks"] * 2
    expected_height = ir["height_blocks"] * 2

    if layout["width"] != expected_width or layout["height"] != expected_height:
        raise ValueError(
            f"{entry['id']}: layout {map_data['layout']} dimensions {(layout['width'], layout['height'])} "
            f"do not match exact Crystal size {(expected_width, expected_height)}"
        )
    if layout["secondary_tileset"] != tileset["runtime_tileset"]:
        raise ValueError(
            f"{entry['id']}: layout {map_data['layout']} secondary tileset {layout['secondary_tileset']} "
            f"!= expected {tileset['runtime_tileset']}"
        )

    block_bytes = block_bytes_for_ir(ir)
    expected_block_count = ir["width_blocks"] * ir["height_blocks"]
    if len(block_bytes) != expected_block_count:
        raise ValueError(
            f"{entry['id']}: expected {expected_block_count} blocks in {ir['blk_path']}, found {len(block_bytes)}"
        )

    metatile_rows = []
    for row_index in range(ir["height_blocks"]):
        top_row = []
        bottom_row = []
        for column_index in range(ir["width_blocks"]):
            block_id = block_bytes[row_index * ir["width_blocks"] + column_index]
            translation = tileset["block_translations"].get(block_id)
            if translation is None:
                raise ValueError(
                    f"{entry['id']}: missing translation for {ir['tileset']} block 0x{block_id:02X}"
                )
            tl, tr, bl, br = translation["metatiles"]
            top_row.extend((tl, tr))
            bottom_row.extend((bl, br))
        metatile_rows.append(top_row)
        metatile_rows.append(bottom_row)

    border_block_id = int(ir["border_block"], 16)
    border_translation = tileset["block_translations"].get(border_block_id)
    if border_translation is None:
        raise ValueError(
            f"{entry['id']}: missing border translation for {ir['tileset']} block 0x{border_block_id:02X}"
        )

    blockdata_path = ROOT / layout["blockdata_filepath"]
    border_path = ROOT / layout["border_filepath"]
    map_bytes = b"".join(struct.pack("<H", value) for row in metatile_rows for value in row)
    border_bytes = b"".join(struct.pack("<H", value) for value in border_translation["border_metatiles"])

    blockdata_path.write_bytes(map_bytes)
    border_path.write_bytes(border_bytes)
    print(f"updated {blockdata_path.relative_to(ROOT)} from {entry['crystal_map']}")
    print(f"updated {border_path.relative_to(ROOT)} from {entry['crystal_map']}")


def apply_exact_warps(map_data, ir, target_map_index):
    generated = map_data.get("warp_events", [])
    expected = ir["events"]["warp_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{map_data['name']}: warp count {len(generated)} != crystal {len(expected)}")
    unresolved = []
    for index, (event, crystal) in enumerate(zip(generated, expected)):
        target = resolve_target_by_crystal_map_id(target_map_index, crystal["dest_map"])
        if target is None:
            target = resolve_target_by_crystal_map(target_map_index, crystal["dest_map"])
        if target is None:
            unresolved.append((index, crystal["dest_map"]))
            continue

        dest_warp_id = crystal["dest_warp_id"] - 1
        if dest_warp_id < 0:
            raise ValueError(
                f"{map_data['name']}: warp {index} has invalid Crystal warp id {crystal['dest_warp_id']}"
            )
        if dest_warp_id >= target["warp_count"]:
            raise ValueError(
                f"{map_data['name']}: warp {index} targets {target['map_id']} warp {dest_warp_id}, "
                f"but only {target['warp_count']} warp(s) exist"
            )

        event["x"] = crystal["x"]
        event["y"] = crystal["y"]
        event["dest_map"] = target["map_id"]
        event["dest_warp_id"] = str(dest_warp_id)

    if unresolved:
        fragments = ", ".join(f"{index}:{target}" for index, target in unresolved)
        print(
            f"partially imported warps for {map_data['name']}: unresolved Crystal targets {fragments}",
            file=sys.stderr,
        )


def apply_exact_bg(map_data, ir):
    generated = map_data.get("bg_events", [])
    expected = ir["events"]["bg_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{map_data['name']}: bg count {len(generated)} != crystal {len(expected)}")
    for event, crystal in zip(generated, expected):
        event["x"] = crystal["x"]
        event["y"] = crystal["y"]


def apply_exact_objects(map_data, ir):
    generated = map_data.get("object_events", [])
    expected = ir["events"]["object_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{map_data['name']}: object count {len(generated)} != crystal {len(expected)}")
    for event, crystal in zip(generated, expected):
        event["x"] = crystal["x"]
        event["y"] = crystal["y"]
        event["movement_range_x"] = crystal["movement_range_x"]
        event["movement_range_y"] = crystal["movement_range_y"]


def apply_subset_objects(entry, map_data, ir):
    generated = map_data.get("object_events", [])
    expected = ir["events"]["object_events"]
    indices = entry["object_indices"]
    if len(generated) != len(indices):
        raise ValueError(f"{map_data['name']}: object count {len(generated)} != subset size {len(indices)}")
    for event, index in zip(generated, indices):
        crystal = expected[index]
        event["x"] = crystal["x"]
        event["y"] = crystal["y"]
        event["movement_range_x"] = crystal["movement_range_x"]
        event["movement_range_y"] = crystal["movement_range_y"]


def apply_remapped_objects(entry, map_data, ir):
    generated = map_data.get("object_events", [])
    expected = ir["events"]["object_events"]
    indices = entry["object_indices"]
    if len(generated) != len(indices):
        raise ValueError(f"{map_data['name']}: object count {len(generated)} != remap size {len(indices)}")
    for event, index in zip(generated, indices):
        crystal = expected[index]
        event["x"] = crystal["x"]
        event["y"] = crystal["y"]
        event["movement_range_x"] = crystal["movement_range_x"]
        event["movement_range_y"] = crystal["movement_range_y"]


def apply_exact_coords(map_data, ir):
    generated = map_data.get("coord_events", [])
    expected = ir["events"]["coord_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{map_data['name']}: coord count {len(generated)} != crystal {len(expected)}")
    for event, crystal in zip(generated, expected):
        event["x"] = crystal["x"]
        event["y"] = crystal["y"]


def apply_repeat_coords(entry, map_data, ir):
    generated = map_data.get("coord_events", [])
    expected = ir["events"]["coord_events"]
    repeat_values = entry["coord_repeat_values"]
    required_count = len(expected) * len(repeat_values)
    if len(generated) != required_count:
        raise ValueError(f"{map_data['name']}: coord count {len(generated)} != repeated crystal count {required_count}")

    cursor = 0
    for crystal in expected:
        for value in repeat_values:
            event = generated[cursor]
            event["x"] = crystal["x"]
            event["y"] = crystal["y"]
            event["var"] = entry["coord_repeat_var"]
            event["var_value"] = value
            cursor += 1


def apply_connections(map_data, ir, target_map_index):
    if not ir["connections"]:
        return

    generated = []
    unresolved = []
    for connection in ir["connections"]:
        target = resolve_target_by_crystal_map(target_map_index, connection["map"])
        if target is None:
            unresolved.append(connection["map"])
            continue
        generated.append(
            {
                "map": target["map_id"],
                "offset": connection["offset"],
                "direction": CRYSTAL_TO_EMERALD_DIRECTION[connection["direction"]],
            }
        )

    if unresolved and not generated:
        print(
            f"skipped connection import for {map_data['name']}: unresolved Crystal targets {', '.join(unresolved)}",
            file=sys.stderr,
        )
        return

    if unresolved:
        print(
            f"partially imported connections for {map_data['name']}: unresolved Crystal targets {', '.join(unresolved)}",
            file=sys.stderr,
        )

    map_data["connections"] = generated


def apply_heal_location(entry):
    if "heal_location_id" not in entry or "heal_spawn_local" not in entry:
        return

    heal_data = load_json(HEAL_LOCATIONS_PATH)
    spawn_x, spawn_y = entry["heal_spawn_local"]
    for heal_location in heal_data["heal_locations"]:
        if heal_location["id"] != entry["heal_location_id"]:
            continue
        heal_location["x"] = int(spawn_x)
        heal_location["y"] = int(spawn_y)
        save_json(HEAL_LOCATIONS_PATH, heal_data)
        print(f"updated {HEAL_LOCATIONS_PATH.relative_to(ROOT)} from {entry['crystal_map']}")
        return
    raise ValueError(f"{entry['id']}: heal location '{entry['heal_location_id']}' not found")


def compile_events(entry, ir, target_map_index):
    if "target_map_json" not in entry:
        return

    map_path = ROOT / entry["target_map_json"]
    map_data = load_target_map(entry)

    if entry.get("warp_mode") == "exact":
        apply_exact_warps(map_data, ir, target_map_index)

    if entry.get("bg_mode") == "exact":
        apply_exact_bg(map_data, ir)

    object_mode = entry.get("object_mode")
    if object_mode == "exact":
        apply_exact_objects(map_data, ir)
    elif object_mode == "subset":
        apply_subset_objects(entry, map_data, ir)
    elif object_mode == "remap":
        apply_remapped_objects(entry, map_data, ir)

    coord_mode = entry.get("coord_mode")
    if coord_mode == "exact":
        apply_exact_coords(map_data, ir)
    elif coord_mode == "repeat_values":
        apply_repeat_coords(entry, map_data, ir)

    apply_connections(map_data, ir, target_map_index)
    save_json(map_path, map_data)
    print(f"updated {map_path.relative_to(ROOT)} from {entry['crystal_map']}")
    apply_heal_location(entry)


def run_all(manifest):
    crystal_tilesets = load_crystal_tilesets()
    ir_index = write_ir_files(manifest)
    scaffold_targets(manifest, ir_index, crystal_tilesets)
    target_map_index = load_target_map_index(manifest)

    for entry in manifest:
        compile_layout(entry, ir_index[entry["crystal_map"]], crystal_tilesets)
    for entry in manifest:
        compile_events(entry, ir_index[entry["crystal_map"]], target_map_index)


def run_extract(manifest):
    write_ir_files(manifest)


def run_scaffold(manifest):
    crystal_tilesets = load_crystal_tilesets()
    ir_index = extract_ir_index(manifest)
    scaffold_targets(manifest, ir_index, crystal_tilesets)


def run_compile_layouts(manifest):
    crystal_tilesets = load_crystal_tilesets()
    ir_index = extract_ir_index(manifest)
    scaffold_targets(manifest, ir_index, crystal_tilesets)
    for entry in manifest:
        compile_layout(entry, ir_index[entry["crystal_map"]], crystal_tilesets)


def run_compile_events(manifest):
    ir_index = extract_ir_index(manifest)
    scaffold_targets(manifest, ir_index, load_crystal_tilesets())
    target_map_index = load_target_map_index(manifest)
    for entry in manifest:
        compile_events(entry, ir_index[entry["crystal_map"]], target_map_index)


def parse_args():
    parser = argparse.ArgumentParser(description="Import Crystal-authored Johto maps into pokeemerald.")
    parser.add_argument(
        "stage",
        nargs="?",
        default="all",
        choices=("all", "extract", "scaffold", "compile-layouts", "compile-events"),
        help="Importer stage to run. Default: all",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manifest = load_import_manifest()

    if args.stage == "all":
        run_all(manifest)
    elif args.stage == "extract":
        run_extract(manifest)
    elif args.stage == "scaffold":
        run_scaffold(manifest)
    elif args.stage == "compile-layouts":
        run_compile_layouts(manifest)
    elif args.stage == "compile-events":
        run_compile_events(manifest)
    else:
        raise AssertionError(f"unhandled stage {args.stage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
