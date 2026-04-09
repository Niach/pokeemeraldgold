#!/usr/bin/env python3

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data" / "johto_events" / "pre_league_event_matrix.json"
MANIFEST_PATH = ROOT / "data" / "johto_import" / "maps.json"


def load_json(path: Path):
    with path.open() as handle:
        return json.load(handle)


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def manifest_id_for_crystal_map(crystal_map: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", crystal_map)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"([a-z])([0-9])", r"\1_\2", value).lower()
    value = re.sub(r"_([0-9])_f\b", r"_\1f", value)
    value = re.sub(r"_b_?([0-9])_f\b", r"_b\1f", value)
    return value


def default_manifest_entry(crystal_map: str):
    return {
        "id": manifest_id_for_crystal_map(crystal_map),
        "crystal_map": crystal_map,
        "bg_mode": "exact",
        "object_mode": "exact",
        "coord_mode": "exact",
    }


def main():
    matrix = load_json(MATRIX_PATH)["maps"]
    manifest_data = load_json(MANIFEST_PATH)
    manifest = manifest_data["maps"]
    existing = {entry["crystal_map"] for entry in manifest}

    added = []
    for map_entry in matrix:
        crystal_map = map_entry["crystal_map"]
        if crystal_map in existing:
            continue
        manifest.append(default_manifest_entry(crystal_map))
        existing.add(crystal_map)
        added.append(crystal_map)

    save_json(MANIFEST_PATH, manifest_data)
    print(f"added {len(added)} manifest entries")
    for crystal_map in added:
        print(crystal_map)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
