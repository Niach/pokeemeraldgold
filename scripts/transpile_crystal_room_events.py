#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "johto_room_transpilers"
HEAL_LOCATIONS_PATH = ROOT / "src" / "data" / "heal_locations.json"


SECTION_MARKERS = {
    "warp_events": ("def_warp_events", "def_coord_events", re.compile(r"warp_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*(\d+)")),
    "coord_events": ("def_coord_events", "def_bg_events", re.compile(r"coord_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*([A-Za-z0-9_]+)")),
    "bg_events": ("def_bg_events", "def_object_events", re.compile(r"bg_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*([A-Za-z0-9_]+)")),
    "object_events": ("def_object_events", None, re.compile(r"object_event\s+(\d+),\s+(\d+),\s*([A-Z0-9_]+),\s*([A-Z0-9_]+),\s*(-?\d+),\s*(-?\d+),.*,\s*([A-Za-z0-9_]+),\s*(-?\d+)")),
}


def load_json(path: Path):
    return json.loads(path.read_text())


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


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
    return {
        key: parse_section(lines, start, end, pattern)
        for key, (start, end, pattern) in SECTION_MARKERS.items()
    }


def resolve_source_path(source: str) -> Path:
    path = Path(source)
    if path.is_absolute():
        return path
    candidates = [ROOT / path, ROOT.parent / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return ROOT / path


def derive_offset(spec):
    if "offset_x" in spec or "offset_y" in spec:
        return spec.get("offset_x", 0), spec.get("offset_y", 0)

    layout_spec_path = spec.get("layout_spec")
    if layout_spec_path is None:
        return 0, 0

    layout_spec = load_json(ROOT / layout_spec_path)
    return layout_spec.get("anchor_chunk_x", 0) * 2, layout_spec.get("anchor_chunk_y", 0) * 2


def apply_exact_warps(spec, data, crystal_events, offset_x, offset_y):
    generated = data.get("warp_events", [])
    expected = crystal_events["warp_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{spec['name']}: warp count {len(generated)} != crystal {len(expected)}")
    for event, (x, y, _dest, _warp) in zip(generated, expected):
        event["x"] = int(x) + offset_x
        event["y"] = int(y) + offset_y


def apply_exact_bg(spec, data, crystal_events, offset_x, offset_y):
    generated = data.get("bg_events", [])
    expected = crystal_events["bg_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{spec['name']}: bg count {len(generated)} != crystal {len(expected)}")
    for event, (x, y, _kind, _script) in zip(generated, expected):
        event["x"] = int(x) + offset_x
        event["y"] = int(y) + offset_y


def apply_exact_objects(spec, data, crystal_events, offset_x, offset_y):
    generated = data.get("object_events", [])
    expected = crystal_events["object_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{spec['name']}: object count {len(generated)} != crystal {len(expected)}")
    for event, (x, y, _sprite, _move, range_x, range_y, _script, _flag) in zip(generated, expected):
        event["x"] = int(x) + offset_x
        event["y"] = int(y) + offset_y
        event["movement_range_x"] = int(range_x)
        event["movement_range_y"] = int(range_y)


def apply_subset_objects(spec, data, crystal_events, offset_x, offset_y):
    generated = data.get("object_events", [])
    expected = crystal_events["object_events"]
    indices = spec.get("object_indices")
    if indices is None:
        raise ValueError(f"{spec['name']}: object_mode 'subset' requires object_indices")
    if len(generated) != len(indices):
        raise ValueError(f"{spec['name']}: object count {len(generated)} != configured subset size {len(indices)}")

    for event, index in zip(generated, indices):
        if index < 0 or index >= len(expected):
            raise ValueError(f"{spec['name']}: object index {index} is out of range for {len(expected)} crystal objects")
        x, y, _sprite, _move, range_x, range_y, _script, _flag = expected[index]
        event["x"] = int(x) + offset_x
        event["y"] = int(y) + offset_y
        event["movement_range_x"] = int(range_x)
        event["movement_range_y"] = int(range_y)


def apply_exact_coords(spec, data, crystal_events, offset_x, offset_y):
    generated = data.get("coord_events", [])
    expected = crystal_events["coord_events"]
    if len(generated) != len(expected):
        raise ValueError(f"{spec['name']}: coord count {len(generated)} != crystal {len(expected)}")
    for event, (x, y, _scene, _script) in zip(generated, expected):
        event["x"] = int(x) + offset_x
        event["y"] = int(y) + offset_y


def apply_heal_location(spec, offset_x, offset_y):
    if "heal_location_id" not in spec or "heal_spawn_local" not in spec:
        return

    heal_data = load_json(HEAL_LOCATIONS_PATH)
    target_id = spec["heal_location_id"]
    spawn_x, spawn_y = spec["heal_spawn_local"]
    for entry in heal_data["heal_locations"]:
        if entry["id"] == target_id:
            entry["x"] = int(spawn_x) + offset_x
            entry["y"] = int(spawn_y) + offset_y
            save_json(HEAL_LOCATIONS_PATH, heal_data)
            return
    raise ValueError(f"{spec['name']}: heal location '{target_id}' not found in {HEAL_LOCATIONS_PATH}")


def transpile_spec(spec_path: Path) -> None:
    spec = load_json(spec_path)
    map_path = ROOT / spec["target_map_json"]
    map_data = load_json(map_path)
    crystal_events = parse_crystal_events(resolve_source_path(spec["source_asm"]))
    offset_x, offset_y = derive_offset(spec)

    mode = spec.get("warp_mode", "skip")
    if mode == "exact":
        apply_exact_warps(spec, map_data, crystal_events, offset_x, offset_y)

    mode = spec.get("bg_mode", "skip")
    if mode == "exact":
        apply_exact_bg(spec, map_data, crystal_events, offset_x, offset_y)

    mode = spec.get("object_mode", "skip")
    if mode == "exact":
        apply_exact_objects(spec, map_data, crystal_events, offset_x, offset_y)
    elif mode == "subset":
        apply_subset_objects(spec, map_data, crystal_events, offset_x, offset_y)

    mode = spec.get("coord_mode", "skip")
    if mode == "exact":
        apply_exact_coords(spec, map_data, crystal_events, offset_x, offset_y)

    save_json(map_path, map_data)
    print(f"updated {map_path.relative_to(ROOT)} from {spec_path.relative_to(ROOT)}")

    if "heal_location_id" in spec:
        apply_heal_location(spec, offset_x, offset_y)
        print(f"updated {HEAL_LOCATIONS_PATH.relative_to(ROOT)} from {spec_path.relative_to(ROOT)}")


def main() -> int:
    if not SOURCE_DIR.is_dir():
        print(f"missing source directory: {SOURCE_DIR}", file=sys.stderr)
        return 1

    for spec_path in sorted(SOURCE_DIR.glob("*.json")):
        transpile_spec(spec_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
