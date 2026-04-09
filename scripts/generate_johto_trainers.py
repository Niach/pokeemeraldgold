#!/usr/bin/env python3

import re
from pathlib import Path

from johto_import_common import ROOT, extract_crystal_ir

POKECRYSTAL_ROOT = ROOT.parent / "pokecrystal"
TRAINER_CONSTANTS_PATH = POKECRYSTAL_ROOT / "constants" / "trainer_constants.asm"
TRAINER_POINTERS_PATH = POKECRYSTAL_ROOT / "data" / "trainers" / "party_pointers.asm"
TRAINER_PARTIES_PATH = POKECRYSTAL_ROOT / "data" / "trainers" / "parties.asm"

OUTPUT_OPPONENTS_PATH = ROOT / "include" / "constants" / "opponents_johto.h"
OUTPUT_PARTIES_PATH = ROOT / "src" / "data" / "johto_trainer_parties.h"
OUTPUT_TRAINERS_PATH = ROOT / "src" / "data" / "johto_trainers.h"

TRAINER_ID_START = 861
MAX_TRAINERS_COUNT = 1280

EXISTING_TRAINER_OVERRIDES = {
    ("RIVAL1", "1_TOTODILE"): "TRAINER_SILVER_TOTODILE",
    ("RIVAL1", "1_CHIKORITA"): "TRAINER_SILVER_CHIKORITA",
    ("RIVAL1", "1_CYNDAQUIL"): "TRAINER_SILVER_CYNDAQUIL",
    ("YOUNGSTER", "JOEY1"): "TRAINER_ROUTE30_JOEY",
    ("YOUNGSTER", "MIKEY"): "TRAINER_ROUTE30_MIKEY",
    ("BUG_CATCHER", "DON"): "TRAINER_ROUTE30_DON",
}

TRAINER_METADATA = {
    "BEAUTY": ("TRAINER_CLASS_BEAUTY", "TRAINER_PIC_BEAUTY", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "BIRD_KEEPER": ("TRAINER_CLASS_BIRD_KEEPER", "TRAINER_PIC_BIRD_KEEPER", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
    "BLACKBELT_T": ("TRAINER_CLASS_BLACK_BELT", "TRAINER_PIC_BLACK_BELT", "TRAINER_ENCOUNTER_MUSIC_HIKER", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "BOARDER": ("TRAINER_CLASS_HIKER", "TRAINER_PIC_HIKER", "TRAINER_ENCOUNTER_MUSIC_HIKER", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "BRUNO": ("TRAINER_CLASS_ELITE_FOUR", "TRAINER_PIC_ELITE_FOUR_DRAKE", "TRAINER_ENCOUNTER_MUSIC_ELITE_FOUR", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "BUGSY": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_BRAWLY", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "BUG_CATCHER": ("TRAINER_CLASS_BUG_CATCHER", "TRAINER_PIC_BUG_CATCHER", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
    "BURGLAR": ("TRAINER_CLASS_POKEMANIAC", "TRAINER_PIC_POKEMANIAC", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "CAMPER": ("TRAINER_CLASS_CAMPER", "TRAINER_PIC_CAMPER", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
    "CHAMPION": ("TRAINER_CLASS_CHAMPION", "TRAINER_PIC_CHAMPION_WALLACE", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "CHUCK": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_BRAWLY", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "CLAIR": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_JUAN", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "COOLTRAINERF": ("TRAINER_CLASS_COOLTRAINER", "TRAINER_PIC_COOLTRAINER_F", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_COOL", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "COOLTRAINERM": ("TRAINER_CLASS_COOLTRAINER", "TRAINER_PIC_COOLTRAINER_M", "TRAINER_ENCOUNTER_MUSIC_COOL", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "EXECUTIVEF": ("TRAINER_CLASS_MAGMA_ADMIN", "TRAINER_PIC_AQUA_ADMIN_F", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "EXECUTIVEM": ("TRAINER_CLASS_MAGMA_ADMIN", "TRAINER_PIC_MAGMA_ADMIN", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "FALKNER": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_WINONA", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "FIREBREATHER": ("TRAINER_CLASS_KINDLER", "TRAINER_PIC_KINDLER", "TRAINER_ENCOUNTER_MUSIC_HIKER", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "FISHER": ("TRAINER_CLASS_FISHERMAN", "TRAINER_PIC_FISHERMAN", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
    "GENTLEMAN": ("TRAINER_CLASS_GENTLEMAN", "TRAINER_PIC_GENTLEMAN", "TRAINER_ENCOUNTER_MUSIC_RICH", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "GRUNTF": ("TRAINER_CLASS_TEAM_AQUA", "TRAINER_PIC_AQUA_GRUNT_F", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "GRUNTM": ("TRAINER_CLASS_TEAM_MAGMA", "TRAINER_PIC_MAGMA_GRUNT_M", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "HIKER": ("TRAINER_CLASS_HIKER", "TRAINER_PIC_HIKER", "TRAINER_ENCOUNTER_MUSIC_HIKER", "0"),
    "JASMINE": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_ROXANNE", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "JUGGLER": ("TRAINER_CLASS_PSYCHIC", "TRAINER_PIC_PSYCHIC_M", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "KAREN": ("TRAINER_CLASS_ELITE_FOUR", "TRAINER_PIC_ELITE_FOUR_PHOEBE", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_ELITE_FOUR", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "KIMONO_GIRL": ("TRAINER_CLASS_BEAUTY", "TRAINER_PIC_BEAUTY", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "KOGA": ("TRAINER_CLASS_ELITE_FOUR", "TRAINER_PIC_ELITE_FOUR_SIDNEY", "TRAINER_ENCOUNTER_MUSIC_ELITE_FOUR", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "LASS": ("TRAINER_CLASS_LASS", "TRAINER_PIC_LASS", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "0"),
    "MEDIUM": ("TRAINER_CLASS_HEX_MANIAC", "TRAINER_PIC_HEX_MANIAC", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "MORTY": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_WATTSON", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "MYSTICALMAN": ("TRAINER_CLASS_PSYCHIC", "TRAINER_PIC_PSYCHIC_M", "TRAINER_ENCOUNTER_MUSIC_COOL", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "OFFICER": ("TRAINER_CLASS_GENTLEMAN", "TRAINER_PIC_GENTLEMAN", "TRAINER_ENCOUNTER_MUSIC_MALE", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "PICNICKER": ("TRAINER_CLASS_PICNICKER", "TRAINER_PIC_PICNICKER", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "0"),
    "POKEFANF": ("TRAINER_CLASS_POKEFAN", "TRAINER_PIC_POKEFAN_F", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "POKEFANM": ("TRAINER_CLASS_POKEFAN", "TRAINER_PIC_POKEFAN_M", "TRAINER_ENCOUNTER_MUSIC_RICH", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "POKEMANIAC": ("TRAINER_CLASS_POKEMANIAC", "TRAINER_PIC_POKEMANIAC", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "PRYCE": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_ELITE_FOUR_GLACIA", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "PSYCHIC_T": ("TRAINER_CLASS_PSYCHIC", "TRAINER_PIC_PSYCHIC_M", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "RIVAL1": ("TRAINER_CLASS_RIVAL", "TRAINER_PIC_BRENDAN", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "RIVAL2": ("TRAINER_CLASS_RIVAL", "TRAINER_PIC_BRENDAN", "TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "SAILOR": ("TRAINER_CLASS_SAILOR", "TRAINER_PIC_SAILOR", "TRAINER_ENCOUNTER_MUSIC_HIKER", "0"),
    "SAGE": ("TRAINER_CLASS_EXPERT", "TRAINER_PIC_EXPERT_M", "TRAINER_ENCOUNTER_MUSIC_HIKER", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "SCHOOLBOY": ("TRAINER_CLASS_SCHOOL_KID", "TRAINER_PIC_SCHOOL_KID_M", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
    "SCIENTIST": ("TRAINER_CLASS_POKEMANIAC", "TRAINER_PIC_POKEMANIAC", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "SKIER": ("TRAINER_CLASS_PICNICKER", "TRAINER_PIC_PICNICKER", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "SUPER_NERD": ("TRAINER_CLASS_POKEMANIAC", "TRAINER_PIC_POKEMANIAC", "TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "SWIMMERM": ("TRAINER_CLASS_SWIMMER_M", "TRAINER_PIC_SWIMMER_M", "TRAINER_ENCOUNTER_MUSIC_SWIMMER", "0"),
    "SWIMMERF": ("TRAINER_CLASS_SWIMMER_F", "TRAINER_PIC_SWIMMER_F", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_SWIMMER", "0"),
    "TEACHER": ("TRAINER_CLASS_LADY", "TRAINER_PIC_LADY", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_FEMALE", "AI_SCRIPT_CHECK_BAD_MOVE"),
    "TWINS": ("TRAINER_CLASS_TWINS", "TRAINER_PIC_TWINS", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_TWINS", "0"),
    "WHITNEY": ("TRAINER_CLASS_LEADER", "TRAINER_PIC_LEADER_NORMAN", "F_TRAINER_FEMALE | TRAINER_ENCOUNTER_MUSIC_INTENSE", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "WILL": ("TRAINER_CLASS_ELITE_FOUR", "TRAINER_PIC_ELITE_FOUR_SIDNEY", "TRAINER_ENCOUNTER_MUSIC_ELITE_FOUR", "AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT"),
    "YOUNGSTER": ("TRAINER_CLASS_YOUNGSTER", "TRAINER_PIC_YOUNGSTER", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
}

SPECIES_NAME_OVERRIDES = {
    "FARFETCH_D": "FARFETCHD",
}

LABEL_RE = re.compile(r"^([A-Za-z0-9_]+Group):$")
TRAINER_CLASS_RE = re.compile(r"^\s*trainerclass\s+([A-Z0-9_]+)")
TRAINER_CONST_RE = re.compile(r"^\s*const\s+([A-Z0-9_]+)")
TRAINER_POINTER_RE = re.compile(r"^\s*dw\s+([A-Za-z0-9_]+Group)$")
TRAINER_ENTRY_RE = re.compile(r'^\s*db\s+"([^"]*)@",\s*(TRAINERTYPE_[A-Z_]+)')
MON_ENTRY_RE = re.compile(r"^\s*db\s+([^;]+)")


def sanitize_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")


def trainer_constant_name(crystal_class: str, crystal_name: str) -> str:
    override = EXISTING_TRAINER_OVERRIDES.get((crystal_class, crystal_name))
    if override is not None:
        return override
    return f"TRAINER_{sanitize_token(crystal_class)}_{sanitize_token(crystal_name)}"


def party_symbol_name(crystal_class: str, crystal_name: str) -> str:
    return f"sPartyJohto{sanitize_token(crystal_class.title())}{sanitize_token(crystal_name.title())}"


def parse_trainer_classes():
    classes = []
    current = None
    for raw_line in TRAINER_CONSTANTS_PATH.read_text().splitlines():
        line = raw_line.split(";", 1)[0].rstrip()
        match = TRAINER_CLASS_RE.match(line)
        if match:
            class_name = match.group(1)
            current = {"class": class_name, "names": []}
            if class_name != "TRAINER_NONE":
                classes.append(current)
            continue
        if current is None:
            continue
        match = TRAINER_CONST_RE.match(line)
        if match:
            name = match.group(1)
            if name.startswith("PHONECONTACT_"):
                continue
            if current["class"] != "TRAINER_NONE":
                current["names"].append(name)
    return classes


def parse_group_order():
    return [
        match.group(1)
        for raw_line in TRAINER_POINTERS_PATH.read_text().splitlines()
        if (match := TRAINER_POINTER_RE.match(raw_line.split(";", 1)[0].rstrip()))
    ]


def parse_trainer_groups():
    groups = {}
    current_group = None
    current_entries = None
    current_entry = None

    for raw_line in TRAINER_PARTIES_PATH.read_text().splitlines():
        line = raw_line.rstrip()
        label_match = LABEL_RE.match(line)
        if label_match:
            current_group = label_match.group(1)
            current_entries = []
            groups[current_group] = current_entries
            current_entry = None
            continue

        if current_group is None:
            continue

        entry_match = TRAINER_ENTRY_RE.match(line)
        if entry_match:
            current_entry = {
                "display_name": entry_match.group(1).replace("?", "???"),
                "trainertype": entry_match.group(2),
                "mons": [],
            }
            current_entries.append(current_entry)
            continue

        if current_entry is None:
            continue

        if "db -1" in line:
            current_entry = None
            continue

        mon_match = MON_ENTRY_RE.match(line)
        if mon_match is None:
            continue

        parts = [part.strip() for part in mon_match.group(1).split(",")]
        if len(parts) < 2 or not parts[0].isdigit():
            continue

        current_entry["mons"].append(
            {
                "level": int(parts[0]),
                "species": parts[1],
            }
        )

    return groups


def build_trainer_catalog():
    class_entries = parse_trainer_classes()
    group_order = parse_group_order()
    groups = parse_trainer_groups()
    if len(class_entries) != len(group_order):
        raise RuntimeError(f"trainer class/group count mismatch: {len(class_entries)} classes vs {len(group_order)} groups")

    catalog = {}
    for class_entry, group_name in zip(class_entries, group_order):
        trainer_entries = groups.get(group_name, [])
        names = class_entry["names"]
        if len(trainer_entries) != len(names):
            raise RuntimeError(
                f"trainer entry count mismatch for {class_entry['class']}: {len(names)} constants vs {len(trainer_entries)} parties"
            )
        for name, trainer_entry in zip(names, trainer_entries):
            catalog[(class_entry["class"], name)] = trainer_entry
    return catalog


def collect_used_trainer_pairs(manifest):
    pairs = set()
    for entry in manifest:
        ir = extract_crystal_ir(entry["crystal_map"])
        for script in ir.get("scripts", {}).values():
            for command in script.get("commands", []):
                if command["command"] in {"trainer", "loadtrainer"}:
                    pairs.add((command["args"][0], command["args"][1]))
    return sorted(pairs)


def normalize_species(species: str) -> str:
    token = sanitize_token(species)
    token = SPECIES_NAME_OVERRIDES.get(token, token)
    return f"SPECIES_{token}"


def trainer_metadata_for_class(crystal_class: str):
    return TRAINER_METADATA.get(
        crystal_class,
        ("TRAINER_CLASS_YOUNGSTER", "TRAINER_PIC_YOUNGSTER", "TRAINER_ENCOUNTER_MUSIC_MALE", "0"),
    )


def write_opponents_header(new_pairs, constant_ids):
    last_id = TRAINER_ID_START - 1
    if new_pairs:
        last_id = constant_ids[new_pairs[-1]]

    lines = [
        "#ifndef GUARD_CONSTANTS_OPPONENTS_JOHTO_H",
        "#define GUARD_CONSTANTS_OPPONENTS_JOHTO_H",
        "",
    ]

    for crystal_class, crystal_name in new_pairs:
        lines.append(
            f"#define {trainer_constant_name(crystal_class, crystal_name):<48} {constant_ids[(crystal_class, crystal_name)]}"
        )

    lines.extend(
        [
            "",
            f"#define TRAINER_JOHTO_LAST {last_id}",
            "#endif  // GUARD_CONSTANTS_OPPONENTS_JOHTO_H",
            "",
        ]
    )
    OUTPUT_OPPONENTS_PATH.write_text("\n".join(lines))


def write_parties_header(new_pairs, catalog):
    lines = []
    for crystal_class, crystal_name in new_pairs:
        entry = catalog[(crystal_class, crystal_name)]
        lines.append(
            f"static const struct TrainerMonNoItemDefaultMoves {party_symbol_name(crystal_class, crystal_name)}[] = {{"
        )
        for mon in entry["mons"]:
            lines.extend(
                [
                    "    {",
                    "    .iv = 0,",
                    f"    .lvl = {mon['level']},",
                    f"    .species = {normalize_species(mon['species'])},",
                    "    },",
                ]
            )
        lines.append("};")
        lines.append("")
    OUTPUT_PARTIES_PATH.write_text("\n".join(lines).rstrip() + "\n")


def write_trainers_header(new_pairs, catalog):
    lines = []
    for crystal_class, crystal_name in new_pairs:
        trainer_class, trainer_pic, encounter_music, ai_flags = trainer_metadata_for_class(crystal_class)
        display_name = catalog[(crystal_class, crystal_name)]["display_name"]
        if display_name == "???":
            display_name = "???"
        lines.extend(
            [
                f"    [{trainer_constant_name(crystal_class, crystal_name)}] =",
                "    {",
                f"        .trainerClass = {trainer_class},",
                f"        .encounterMusic_gender = {encounter_music},",
                f"        .trainerPic = {trainer_pic},",
                f'        .trainerName = _("{display_name}"),',
                "        .items = {},",
                "        .doubleBattle = FALSE,",
                f"        .aiFlags = {ai_flags},",
                f"        .party = NO_ITEM_DEFAULT_MOVES({party_symbol_name(crystal_class, crystal_name)}),",
                "    },",
                "",
            ]
        )
    OUTPUT_TRAINERS_PATH.write_text("\n".join(lines).rstrip() + "\n")


def write_johto_trainer_files(manifest):
    catalog = build_trainer_catalog()
    used_pairs = collect_used_trainer_pairs(manifest)

    new_pairs = [pair for pair in used_pairs if pair not in EXISTING_TRAINER_OVERRIDES]
    constant_ids = {
        pair: TRAINER_ID_START + index
        for index, pair in enumerate(new_pairs)
    }

    missing = [pair for pair in used_pairs if pair not in EXISTING_TRAINER_OVERRIDES and pair not in catalog]
    if missing:
        raise RuntimeError(f"missing Crystal trainer data for pairs: {missing[:10]}")

    train_count = TRAINER_ID_START + len(new_pairs)
    if train_count > MAX_TRAINERS_COUNT:
        raise RuntimeError(f"generated {train_count} trainers, exceeding MAX_TRAINERS_COUNT {MAX_TRAINERS_COUNT}")

    OUTPUT_OPPONENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PARTIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_TRAINERS_PATH.parent.mkdir(parents=True, exist_ok=True)

    write_opponents_header(new_pairs, constant_ids)
    write_parties_header(new_pairs, catalog)
    write_trainers_header(new_pairs, catalog)

    return {
        "used_pairs": len(used_pairs),
        "generated_pairs": len(new_pairs),
        "trainers_count": train_count,
    }


if __name__ == "__main__":
    import import_johto_maps as ijm

    result = write_johto_trainer_files(ijm.load_import_manifest())
    print(
        f"generated {result['generated_pairs']} Johto trainer entries "
        f"({result['used_pairs']} used pairs, TRAINERS_COUNT={result['trainers_count']})"
    )
