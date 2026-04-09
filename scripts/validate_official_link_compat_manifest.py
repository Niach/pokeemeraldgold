#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "johto_events" / "official_link_compatibility_manifest.json"

REQUIRED_TOP_LEVEL_KEYS = {
    "compatibility_target",
    "supported_titles",
    "unsupported_targets",
    "wire_contract",
    "subsystems",
}

REQUIRED_WIRE_CONTRACT_KEYS = {
    "game_version",
    "pokemon_struct_layout",
    "link_player_layout",
    "trade_payload_layout",
    "battle_flow",
}

REQUIRED_SUBSYSTEM_KEYS = {
    "id",
    "classification",
    "status",
    "notes",
}

VALID_CLASSIFICATIONS = {
    "save_only",
    "local_battle_story",
    "link_visible",
}

VALID_STATUSES = {
    "retail_safe",
    "link_blocked_until_retail_safe",
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())

    missing = REQUIRED_TOP_LEVEL_KEYS - manifest.keys()
    if missing:
        fail(f"manifest is missing top-level keys: {sorted(missing)}")

    wire_contract = manifest["wire_contract"]
    missing_wire_keys = REQUIRED_WIRE_CONTRACT_KEYS - wire_contract.keys()
    if missing_wire_keys:
        fail(f"wire_contract is missing keys: {sorted(missing_wire_keys)}")

    subsystems = manifest["subsystems"]
    if not isinstance(subsystems, list) or not subsystems:
        fail("subsystems must be a non-empty list")

    ids = set()
    for index, subsystem in enumerate(subsystems):
        missing_subsystem_keys = REQUIRED_SUBSYSTEM_KEYS - subsystem.keys()
        if missing_subsystem_keys:
            fail(f"subsystem #{index} is missing keys: {sorted(missing_subsystem_keys)}")

        subsystem_id = subsystem["id"]
        if subsystem_id in ids:
            fail(f"subsystem id '{subsystem_id}' is duplicated")
        ids.add(subsystem_id)

        if subsystem["classification"] not in VALID_CLASSIFICATIONS:
            fail(
                f"subsystem '{subsystem_id}' has invalid classification "
                f"'{subsystem['classification']}'"
            )

        if subsystem["status"] not in VALID_STATUSES:
            fail(f"subsystem '{subsystem_id}' has invalid status '{subsystem['status']}'")

    print("official link compatibility manifest is valid")


if __name__ == "__main__":
    main()
