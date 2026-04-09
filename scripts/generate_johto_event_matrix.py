#!/usr/bin/env python3

import json
import re
from collections import Counter
from pathlib import Path

from johto_import_common import (
    CRYSTAL_MAP_DB,
    JOHTO_LANDMARKS,
    ROOT,
    extract_crystal_ir,
    load_import_manifest,
    manifest_by_crystal_map,
    resolve_crystal_path,
    save_json,
    strip_asm_comment,
)

OUTPUT_PATH = ROOT / "data" / "johto_events" / "pre_league_event_matrix.json"

PRE_LEAGUE_EXCLUDED_LANDMARKS = {
    "LANDMARK_BATTLE_TOWER",
    "LANDMARK_SILVER_CAVE",
}

PRE_LEAGUE_EXTRA_LANDMARKS = {
    "LANDMARK_ROUTE_26",
    "LANDMARK_ROUTE_27",
    "LANDMARK_TOHJO_FALLS",
    "LANDMARK_VICTORY_ROAD",
    "LANDMARK_INDIGO_PLATEAU",
}

PRE_LEAGUE_SPECIAL_MAPS = {
    "Pokecenter2F",
}

FLAG_REF_RE = re.compile(r"\b(?:ENGINE|EVENT|FLAG)_[A-Z0-9_]+\b")
VAR_REF_RE = re.compile(r"\bVAR_[A-Z0-9_]+\b")
LABEL_RE = re.compile(r"^([A-Za-z0-9_.]+)::?$")

EARLY_BADGE_PATH_LANDMARKS = {
    "LANDMARK_AZALEA_TOWN",
    "LANDMARK_GOLDENROD_CITY",
    "LANDMARK_ILEX_FOREST",
    "LANDMARK_ROUTE_32",
    "LANDMARK_ROUTE_33",
    "LANDMARK_ROUTE_34",
    "LANDMARK_SLOWPOKE_WELL",
    "LANDMARK_SPROUT_TOWER",
    "LANDMARK_UNION_CAVE",
    "LANDMARK_VIOLET_CITY",
}

MIDGAME_LANDMARKS = {
    "LANDMARK_BURNED_TOWER",
    "LANDMARK_CIANWOOD_CITY",
    "LANDMARK_ECRUTEAK_CITY",
    "LANDMARK_LIGHTHOUSE",
    "LANDMARK_MT_MORTAR",
    "LANDMARK_NATIONAL_PARK",
    "LANDMARK_OLIVINE_CITY",
    "LANDMARK_ROUTE_35",
    "LANDMARK_ROUTE_36",
    "LANDMARK_ROUTE_37",
    "LANDMARK_ROUTE_38",
    "LANDMARK_ROUTE_39",
    "LANDMARK_ROUTE_40",
    "LANDMARK_ROUTE_41",
    "LANDMARK_ROUTE_42",
    "LANDMARK_TIN_TOWER",
    "LANDMARK_WHIRL_ISLANDS",
}

LATE_JOHTO_TO_LEAGUE_LANDMARKS = {
    "LANDMARK_BLACKTHORN_CITY",
    "LANDMARK_DARK_CAVE",
    "LANDMARK_DRAGONS_DEN",
    "LANDMARK_ICE_PATH",
    "LANDMARK_INDIGO_PLATEAU",
    "LANDMARK_LAKE_OF_RAGE",
    "LANDMARK_MAHOGANY_TOWN",
    "LANDMARK_RADIO_TOWER",
    "LANDMARK_ROCKET_BASE",
    "LANDMARK_ROUTE_26",
    "LANDMARK_ROUTE_27",
    "LANDMARK_ROUTE_43",
    "LANDMARK_ROUTE_44",
    "LANDMARK_ROUTE_45",
    "LANDMARK_TOHJO_FALLS",
    "LANDMARK_VICTORY_ROAD",
}

MAP_NAME_ARC_OVERRIDES = {
    "DayOfWeekSiblingsHouse": "LATE_JOHTO_TO_LEAGUE",
    "GoldenrodUndergroundWarehouse": "LATE_JOHTO_TO_LEAGUE",
    "HallOfFame": "LATE_JOHTO_TO_LEAGUE",
    "Route29Route46Gate": "NEW_BARK_BOOTSTRAP",
}

SUBSTITUTE_POLICIES = [
    (
        "Pokegear phone -> Emerald Match Call / PokeNav",
        ("#GEAR", "Pokegear", "PHONE_", "addcellnum", "checkcellnum", "specialphonecall"),
    ),
    (
        "Radio interactions -> Emerald TV or scripted broadcast text",
        ("Radio", "radio", "MUSIC_POKEMON_TALK", "Radio1Script", "PokemonTalk"),
    ),
    (
        "Bedroom decorations -> Emerald decorations or fixed room state",
        ("describedecoration", "ToggleDecorationsVisibility", "ToggleMaptileDecorations", "DECODESC_"),
    ),
    (
        "Day/time prompts -> Emerald RTC with simplified Crystal parity",
        ("VAR_WEEKDAY", "checktime", "SetDayOfWeek", "DST", "InitialSetDSTFlag", "InitialClearDSTFlag"),
    ),
]

SUPPORTED_CRYSTAL_COMMANDS = {
    "addcellnum",
    "appear",
    "applymovement",
    "call",
    "callstd",
    "catchtutorial",
    "checkevent",
    "checkflag",
    "checkscene",
    "checktime",
    "closepokepic",
    "closetext",
    "cry",
    "disappear",
    "dontrestartmapmusic",
    "end",
    "endcallback",
    "faceplayer",
    "follow",
    "farwritetext",
    "fruittree",
    "givepoke",
    "ifnotequal",
    "ifequal",
    "iffalse",
    "iftrue",
    "itemball",
    "jumpstd",
    "jumptext",
    "jumptextfaceplayer",
    "loadtrainer",
    "loadvar",
    "loadwildmon",
    "moveobject",
    "musicfadeout",
    "opentext",
    "pause",
    "playsound",
    "playmusic",
    "pokepic",
    "promptbutton",
    "reanchormap",
    "readvar",
    "reloadmap",
    "scall",
    "sdefer",
    "setevent",
    "setflag",
    "setlasttalked",
    "setmapscene",
    "setscene",
    "setval",
    "sjump",
    "special",
    "startbattle",
    "stopfollow",
    "turnobject",
    "verbosegiveitem",
    "waitbutton",
    "waitsfx",
    "writetext",
    "yesorno",
}

MECHANIC_PATTERNS = {
    "applymovement": "applymovement",
    "trainer": "trainer ",
    "itemball": "itemball",
    "hiddenitem": "hiddenitem",
    "setscene": "setscene",
    "appear": "appear ",
    "disappear": "disappear ",
    "follow": "follow ",
    "stopfollow": "stopfollow",
    "changeblock": "changeblock",
    "specialphonecall": "specialphonecall",
}


def is_pre_league_map(crystal_map: str, metadata: dict, manifest_lookup: dict) -> bool:
    landmark = metadata["landmark"]
    if crystal_map in PRE_LEAGUE_SPECIAL_MAPS:
        return True
    if crystal_map in manifest_lookup:
        return True
    if landmark in PRE_LEAGUE_EXTRA_LANDMARKS:
        return True
    if landmark not in JOHTO_LANDMARKS:
        return False
    return landmark not in PRE_LEAGUE_EXCLUDED_LANDMARKS


def classify_story_arc(crystal_map: str, metadata: dict) -> str:
    if crystal_map in MAP_NAME_ARC_OVERRIDES:
        return MAP_NAME_ARC_OVERRIDES[crystal_map]

    landmark = metadata["landmark"]
    if landmark == "LANDMARK_NEW_BARK_TOWN" or landmark == "LANDMARK_CHERRYGROVE_CITY":
        return "NEW_BARK_BOOTSTRAP"
    if landmark in {"LANDMARK_ROUTE_29", "LANDMARK_ROUTE_30", "LANDMARK_ROUTE_31", "LANDMARK_ROUTE_46"}:
        return "NEW_BARK_BOOTSTRAP"
    if landmark in EARLY_BADGE_PATH_LANDMARKS:
        return "EARLY_BADGE_PATH"
    if landmark in MIDGAME_LANDMARKS:
        return "MIDGAME"
    if landmark in LATE_JOHTO_TO_LEAGUE_LANDMARKS:
        return "LATE_JOHTO_TO_LEAGUE"

    if crystal_map.startswith(("NewBark", "Cherrygrove", "PlayersHouse", "Elms", "GuideGentsHouse", "Route29", "Route30", "Route31", "Route46")):
        return "NEW_BARK_BOOTSTRAP"
    if crystal_map.startswith(("Violet", "SproutTower", "Route32", "Route33", "UnionCave", "Azalea", "SlowpokeWell", "IlexForest", "Goldenrod", "BugCatchingContest", "Route34")):
        return "EARLY_BADGE_PATH"
    if crystal_map.startswith(("Ecruteak", "BurnedTower", "Olivine", "OlivineLighthouse", "Lighthouse", "Cianwood", "WhirlIslands", "Route35", "Route36", "Route37", "Route38", "Route39", "Route40", "Route41", "Route42", "MtMortar")):
        return "MIDGAME"
    return "LATE_JOHTO_TO_LEAGUE"


def parse_label_commands(source_path: Path) -> dict:
    commands = {}
    pending_labels = []
    for raw_line in source_path.read_text().splitlines():
        line = strip_asm_comment(raw_line)
        if not line:
            continue

        label_match = LABEL_RE.match(line)
        if label_match:
            pending_labels.append(label_match.group(1))
            continue

        if not pending_labels:
            continue
        command = line.split()[0]
        for label in pending_labels:
            commands[label] = command
        pending_labels.clear()
    return commands


def build_command_coverage(ir: dict) -> tuple[dict, list[str]]:
    command_counts = Counter()
    for script in ir.get("scripts", {}).values():
        for command in script.get("commands", []):
            command_counts[command["command"]] += 1

    unsupported = sorted(
        command
        for command in command_counts
        if command not in SUPPORTED_CRYSTAL_COMMANDS
    )
    supported_total = sum(
        count for command, count in command_counts.items() if command in SUPPORTED_CRYSTAL_COMMANDS
    )
    unsupported_total = sum(
        count for command, count in command_counts.items() if command not in SUPPORTED_CRYSTAL_COMMANDS
    )
    coverage = {
        "total_commands": sum(command_counts.values()),
        "supported_commands": supported_total,
        "unsupported_commands": unsupported_total,
        "counts_by_command": dict(sorted(command_counts.items())),
    }
    return coverage, unsupported


def count_by(entries: list[dict], key: str) -> dict[str, int]:
    counts = Counter()
    for entry in entries:
        counts[str(entry[key])] += 1
    return dict(sorted(counts.items()))


def sorted_unique(pattern: re.Pattern, text: str) -> list[str]:
    return sorted(set(pattern.findall(text)))


def detect_substitute_policies(source_text: str) -> list[str]:
    policies = []
    for policy, needles in SUBSTITUTE_POLICIES:
        if any(needle in source_text for needle in needles):
            policies.append(policy)
    return policies


def detect_acceptance_scenarios(entry: dict, source_text: str) -> list[str]:
    scenarios = []
    if entry["scene_scripts"]:
        scenarios.append("scene sequencing and scene-id progression")
    if entry["callbacks"]:
        scenarios.append("callback-driven map load and resume behavior")
    if entry["coord_events"]:
        scenarios.append("coord trigger first-run, repeat entry, and reload behavior")
    if entry["bg_event_counts_by_kind"].get("BGEVENT_ITEM", 0):
        scenarios.append("hidden item single-use parity")
    if any(event["interaction_kind"] == "trainer" for event in entry["object_events"]):
        scenarios.append("trainer battle setup and after-battle state")
    if any(event["interaction_kind"] == "itemball" for event in entry["object_events"]):
        scenarios.append("item ball single-use parity")
    if any(event["interaction_kind"] == "fruit_tree" for event in entry["object_events"]):
        scenarios.append("fruit tree or daily pickup behavior")
    if any(event["interaction_kind"] == "script" for event in entry["object_events"]):
        scenarios.append("NPC facing and talk prologue behavior")
    if entry["visibility_time_gates"]:
        scenarios.append("time/day or event-flag visibility gates")
    if "follow " in source_text or "stopfollow" in source_text:
        scenarios.append("follow and stopfollow cutscene behavior")
    if "changeblock" in source_text:
        scenarios.append("changeblock redraw and persistent tile state")
    return scenarios


def classify_object_interaction(object_event: dict, label_commands: dict) -> str:
    script_command = label_commands.get(object_event["script"])
    object_type = object_event["object_type"]
    if object_type == "OBJECTTYPE_TRAINER" or script_command == "trainer":
        return "trainer"
    if object_type == "OBJECTTYPE_ITEMBALL" or script_command == "itemball":
        return "itemball"
    if script_command == "fruittree":
        return "fruit_tree"
    return "script"


def classify_bg_interaction(bg_event: dict, label_commands: dict) -> str:
    if bg_event["kind"] == "BGEVENT_ITEM":
        return "hidden_item"
    if label_commands.get(bg_event["script"]) == "hiddenitem":
        return "hidden_item"
    return "sign_or_trigger"


def build_map_entry(crystal_map: str, metadata: dict, manifest_lookup: dict) -> tuple[dict, dict]:
    source_path = resolve_crystal_path(metadata["source_asm"])
    source_text = source_path.read_text()
    ir = extract_crystal_ir(crystal_map)
    label_commands = parse_label_commands(source_path)
    manifest_entry = manifest_lookup.get(crystal_map)
    target_exists = manifest_entry is not None and (ROOT / manifest_entry["target_map_json"]).exists()
    known_labels = set(ir.get("scripts", {})) | set(ir.get("texts", {})) | set(ir.get("movements", {}))

    scene_scripts = ir["events"]["scene_scripts"]
    callbacks = ir["events"]["callbacks"]
    warp_events = ir["events"]["warp_events"]
    coord_events = ir["events"]["coord_events"]

    bg_events = []
    for event in ir["events"]["bg_events"]:
        event_entry = dict(event)
        event_entry["interaction_kind"] = classify_bg_interaction(event, label_commands)
        event_entry["script_command"] = label_commands.get(event["script"])
        bg_events.append(event_entry)

    object_events = []
    for event in ir["events"]["object_events"]:
        event_entry = dict(event)
        event_entry["interaction_kind"] = classify_object_interaction(event, label_commands)
        event_entry["script_command"] = label_commands.get(event["script"])
        object_events.append(event_entry)

    visibility_time_gates = []
    for event in object_events:
        if event["time_range_start"] != -1 or event["time_range_end"] != -1 or event["flag"] != -1:
            visibility_time_gates.append(
                {
                    "script": event["script"],
                    "object_type": event["object_type"],
                    "time_range_start": event["time_range_start"],
                    "time_range_end": event["time_range_end"],
                    "flag": event["flag"],
                }
            )

    script_refs = []
    for event in scene_scripts:
        if event["script"] is not None:
            script_refs.append(event["script"])
    for callback in callbacks:
        script_refs.append(callback["script"])
    for event in coord_events + bg_events + object_events:
        script_refs.append(event["script"])

    command_coverage, unsupported_commands = build_command_coverage(ir)
    unresolved_script_refs = sorted(ref for ref in set(script_refs) if ref not in known_labels)
    runtime_requirements = []
    if unsupported_commands:
        runtime_requirements.append("unsupported Crystal commands need runtime or transpiler support")
    if unresolved_script_refs:
        runtime_requirements.append("unresolved script refs need parser or generator support")
    if ir.get("substitute_tags"):
        runtime_requirements.append("approved substitute systems required")

    entry = {
        "crystal_map": crystal_map,
        "crystal_map_id": metadata["map_id"],
        "story_arc": classify_story_arc(crystal_map, metadata),
        "source_asm": metadata["source_asm"],
        "import_status": (
            "pilot_imported"
            if target_exists
            else "pilot_manifest_only"
            if manifest_entry is not None
            else "not_in_manifest"
        ),
        "target": None
        if manifest_entry is None
        else {
            "target_name": manifest_entry["target_name"],
            "map_id": manifest_entry["map_id"],
            "target_map_json": manifest_entry["target_map_json"],
            "target_scripts_path": manifest_entry["target_scripts_path"],
        },
        "scene_scripts": scene_scripts,
        "callbacks": callbacks,
        "warp_events": warp_events,
        "coord_events": coord_events,
        "bg_events": bg_events,
        "bg_event_counts_by_kind": count_by(bg_events, "kind"),
        "object_events": object_events,
        "object_event_counts_by_type": count_by(object_events, "object_type"),
        "visibility_time_gates": visibility_time_gates,
        "referenced_flags": sorted_unique(FLAG_REF_RE, source_text),
        "referenced_vars": sorted_unique(VAR_REF_RE, source_text),
        "script_refs": sorted(set(script_refs)),
        "unresolved_script_refs": unresolved_script_refs,
        "command_coverage": command_coverage,
        "unsupported_commands": unsupported_commands,
        "text_policy": "crystal_exact_with_minimal_substitutions" if ir.get("texts") else "no_text_blocks",
        "generated_status": (
            "ready_for_generation"
            if not unsupported_commands and not unresolved_script_refs
            else "needs_runtime_support"
        ),
        "runtime_requirements": runtime_requirements,
        "script_asset_counts": {
            "scripts": len(ir.get("scripts", {})),
            "texts": len(ir.get("texts", {})),
            "movements": len(ir.get("movements", {})),
        },
        "scene_ids": ir.get("scene_ids", []),
        "object_consts": ir.get("object_consts", []),
        "std_calls": ir.get("std_calls", []),
        "substitute_tags": ir.get("substitute_tags", []),
        "substitute_system_policy": detect_substitute_policies(source_text),
        "acceptance_scenarios": [],
    }
    entry["acceptance_scenarios"] = detect_acceptance_scenarios(entry, source_text)
    return entry, {"source_text": source_text}


def generate_matrix():
    manifest = load_import_manifest()
    manifest_lookup = manifest_by_crystal_map(manifest)
    maps = []
    mechanic_counts = Counter()
    total_bg_kinds = Counter()
    total_object_types = Counter()

    for crystal_map, metadata in sorted(CRYSTAL_MAP_DB.items()):
        if not is_pre_league_map(crystal_map, metadata, manifest_lookup):
            continue

        entry, context = build_map_entry(crystal_map, metadata, manifest_lookup)
        maps.append(entry)

        for mechanic, needle in MECHANIC_PATTERNS.items():
            if needle in context["source_text"]:
                mechanic_counts[mechanic] += 1
        total_bg_kinds.update(entry["bg_event_counts_by_kind"])
        total_object_types.update(entry["object_event_counts_by_type"])

    maps.sort(key=lambda item: (item["story_arc"], item["crystal_map"]))
    return {
        "schema_version": 1,
        "scope": {
            "description": "Pokemon Crystal pre-League Johto plus Indigo Plateau, excluding Kanto and postgame-only landmarks.",
            "excluded_landmarks": sorted(PRE_LEAGUE_EXCLUDED_LANDMARKS),
            "extra_landmarks": sorted(PRE_LEAGUE_EXTRA_LANDMARKS),
            "special_maps": sorted(PRE_LEAGUE_SPECIAL_MAPS),
        },
        "summary": {
            "map_count": len(maps),
            "story_arc_counts": dict(sorted(Counter(entry["story_arc"] for entry in maps).items())),
            "import_status_counts": dict(sorted(Counter(entry["import_status"] for entry in maps).items())),
            "mechanic_map_counts": dict(sorted(mechanic_counts.items())),
            "bg_event_counts_by_kind": dict(sorted(total_bg_kinds.items())),
            "object_event_counts_by_type": dict(sorted(total_object_types.items())),
        },
        "maps": maps,
    }


def main():
    matrix = generate_matrix()
    save_json(OUTPUT_PATH, matrix)
    print(f"updated {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
