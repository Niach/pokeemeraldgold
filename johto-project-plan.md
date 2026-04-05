# Pokémon Emerald — Johto Region Expansion: Execution Plan

## Project Goal
Add the Johto region to a vanilla `pret/pokeemerald` build as a second playable region, while maintaining **full link/trade compatibility** with retail Pokémon Ruby, Sapphire, FireRed, LeafGreen, and Emerald cartridges.

---

## Critical Constraint: Link Compatibility Rules

Everything in this plan is designed around one rule: **the 100-byte Pokémon data structure and the link protocol must remain byte-identical to vanilla Emerald.** Here is exactly what you can and cannot touch.

### SAFE — Modify Freely
These never cross the link cable and have zero effect on compatibility:

- Maps, tilesets, tile palettes, metatiles, map connections
- Wild encounter tables (as long as species IDs are ≤411)
- Trainer teams, AI, and battle scripts
- Overworld event scripts, NPC dialogue, cutscenes
- Music and sound effects
- Overworld sprites and tileset graphics
- Story progression, badge logic, flag systems
- Region map / Town Map / Fly destinations
- Movement permissions, warp points, map headers
- HM usage rules, Repel behavior, text speed, QoL tweaks
- Adding new maps (entire regions worth)

### NEVER TOUCH — Will Break Linking
- Species table: do NOT add species beyond index 411 (Deoxys = 410 + 1 egg = 411)
- Move table: do NOT add moves beyond ID 354 (Psycho Boost)
- Ability table: do NOT add abilities beyond ID 77 (Air Lock)
- Item table: do NOT add items beyond ID 376 (Enigma Berry)
- Pokémon data structure (`struct Pokemon`, 100 bytes / 80 bytes in PC)
- The 48-byte encrypted data substructures (Growth, Attacks, EVs, Misc)
- Encryption scheme (personality XOR OT ID)
- Checksum algorithm (16-bit sum of unencrypted data)
- `src/link.c`, `src/link_rfu.c` — link protocol code
- `src/trade.c` — trade sequence and validation
- The "GameFreak inc." magic handshake string
- `gGameVersion` / ROM header game code (`BPEE` for Emerald)
- `struct LinkPlayer` and `LinkPlayerBlock` formats
- Save block structure layout (EWRAM offsets the link code reads)

### CAUTION — Modify With Care
- Base stats: safe to change, but traded Pokémon will have their stats recalculated by the receiving game using *its own* base stat table, so stats will shift
- Learnsets: safe if all move IDs are valid vanilla Gen 3
- Evolution methods: safe to change triggers (e.g. level, happiness), but evolved species must be valid vanilla IDs
- Type table: do NOT add new types (the type matchup table is referenced during link battles)
- National Dex trade gate: you can remove the Celio/Champion check to allow earlier trading — this is a flag/script change, not a protocol change

---

## Architecture Overview

```
pokeemerald (your fork)
├── data/
│   ├── maps/                    ← Hoenn maps (existing)
│   │   ├── PetalburgCity/
│   │   └── ...
│   ├── maps_johto/              ← NEW: all Johto maps
│   │   ├── NewBarkTown/
│   │   ├── CherrygroveCity/
│   │   ├── VioletCity/
│   │   └── ...
│   ├── layouts/                 ← Hoenn layouts (existing)
│   ├── layouts_johto/           ← NEW: Johto layouts
│   └── tilesets/
│       ├── primary/             ← existing Hoenn tilesets
│       ├── secondary/           ← existing Hoenn tilesets
│       ├── primary_johto/       ← NEW: Johto primary tilesets
│       └── secondary_johto/     ← NEW: Johto secondary tilesets
├── graphics/
│   └── tilesets_johto/          ← NEW: Johto tileset PNGs
├── src/
│   ├── region_switch.c          ← NEW: region transition logic
│   ├── johto_fly_map.c          ← NEW: Johto fly/town map
│   └── ...
└── include/
    └── constants/
        ├── map_groups.h         ← add Johto map groups
        └── region.h             ← NEW: region ID constants
```

---

## Phase 0: Setup & Reference Repos (Day 1-2)

### 0.1 — Fork & verify your base builds clean
```bash
cd ~/pokeemerald
make clean
make -j$(nproc)
# Verify output: pokeemerald.gba with sha1 f3ae088181bf583e55daf962a92bb46f4f1d07b7
```

### 0.2 — Clone reference repos side by side
```bash
cd ~
git clone https://github.com/pret/pokecrystal.git
git clone https://github.com/eonlynx/pokecrossroads.git
git clone https://github.com/StrangeQuark/pokeemerald.git strangequark-emerald
```

**What each reference gives you:**
- `pokecrystal` — Original Johto map layouts (`.blk` files), event scripts, wild encounter data, NPC positions, warp coordinates, trainer teams. This is your **content blueprint**.
- `pokecrossroads` — A working multi-region pokeemerald hack (Hoenn+Kanto+Johto). Study their `data/maps/` structure for how they added Kanto maps, their region-switching code, and their multi-region fly map. This is your **architecture reference**.
- `strangequark-emerald` — The base fork that Crossroads built on. A simpler, cleaner version of the 3-region merge without the expansion features. May be easier to study.

### 0.3 — Install Porymap
Download Porymap 6.x from https://github.com/huderlem/porymap/releases. Point it at your pokeemerald directory. Verify it opens and shows Hoenn maps correctly. You'll use this for ALL map creation.

### 0.4 — Set up link testing
Install mGBA (latest). Configure two instances for link cable testing:
- Instance 1: your hack ROM
- Instance 2: vanilla Emerald ROM (or Ruby/Sapphire/FRLG)
- Test trading after every major milestone

---

## Phase 1: Johto Tilesets (Weeks 1-3)

This is the hardest and most time-consuming phase. Crystal's tilesets are Game Boy Color quality (4 colors, 8x8 tiles in 32x32 metatile blocks). You need GBA-quality equivalents (16 colors per palette, 8x8 tiles in 16x16 metatiles with two layers).

### 1.1 — Inventory Crystal's tilesets
Open `pokecrystal/gfx/tilesets/` and catalog them:
```
johto_modern.png     → cities like Goldenrod, Violet, etc.
johto_traditional.png → Ecruteak, etc.
kanto.png            → Kanto areas
cave.png             → caves/tunnels
house.png            → generic interiors
pokecenter.png       → Pokémon Centers
mart.png             → Poké Marts
gate.png             → route gates
radio_tower.png      → Radio Tower interior
...
```

### 1.2 — Strategy: Reuse + Redraw
You have three tiers of tilesets to deal with:

**Tier 1 — Reuse Emerald tilesets directly** (saves massive time):
- Pokémon Centers (identical layout across games)
- Poké Marts
- Generic house interiors
- Caves (Emerald's cave tileset works for Johto caves)
- Generic indoor tilesets

**Tier 2 — Adapt existing Emerald tilesets** (moderate work):
- Route tilesets: Emerald's route tiles can be recolored/tweaked for Johto routes
- Water/ocean tiles: reuse directly
- Forest tiles: reuse Petalburg Woods style

**Tier 3 — Draw new tilesets** (significant work):
- Johto city tilesets (Goldenrod's urban look, Ecruteak's traditional style)
- Johto-specific landmarks (Tin Tower, Burned Tower, Radio Tower)
- Johto-style houses and rooftops

**Shortcut:** Study what Heart & Soul and Crossroads used. Some community-made Johto GBA tilesets exist on DeviantArt and PokéCommunity's resource threads. Many are free to use with credit.

### 1.3 — Create tileset files in pokeemerald format
Each tileset needs:
```
graphics/tilesets_johto/primary/johto_general/
    ├── tiles.png          (the 8x8 tile sheet, 128px wide)
    ├── palettes/
    │   ├── 00.pal         (up to 13 palettes for primary)
    │   ├── 01.pal
    │   └── ...
    └── metatiles/
        ├── metatiles.bin  (metatile definitions)
        └── metatile_attributes.bin

data/tilesets/primary_johto/johto_general/
    └── header.inc         (tileset header referencing the above)
```

Use Porymap's tileset editor to create and preview metatiles.

---

## Phase 2: Map Layouts (Weeks 3-6)

### 2.1 — Plan the Johto map list
From pokecrystal, the full Johto region has approximately:

**Outdoor maps (~30):**
New Bark Town, Cherrygrove City, Violet City, Azalea Town, Goldenrod City, Ecruteak City, Olivine City, Cianwood City, Mahogany Town, Blackthorn City, plus Routes 29-46, National Park, Lake of Rage, etc.

**Indoor maps (~80-100):**
Gyms (8), Pokémon Centers (10+), Marts, houses, caves (Union Cave, Slowpoke Well, Ice Path, Mt. Mortar, Dark Cave, Whirl Islands, Dragon's Den), towers (Sprout Tower, Tin Tower, Burned Tower, Radio Tower), Ruins of Alph, Safari Zone, etc.

**Total: ~110-130 maps**

### 2.2 — Define map groups and constants

Edit `include/constants/map_groups.h`:
```c
// After existing Hoenn map groups, add:
#define MAP_GROUP_JOHTO_TOWNS      (LAST_HOENN_GROUP + 1)
#define MAP_GROUP_JOHTO_ROUTES     (LAST_HOENN_GROUP + 2)
#define MAP_GROUP_JOHTO_DUNGEONS   (LAST_HOENN_GROUP + 3)
#define MAP_GROUP_JOHTO_INTERIORS  (LAST_HOENN_GROUP + 4)
```

### 2.3 — Build maps in Porymap
For each Crystal map, the workflow is:

1. **Open Crystal's `.blk` in Polished Map** (or just look at screenshots/references) to understand the layout dimensions and structure
2. **In Porymap: File → New Map** — set dimensions, choose your Johto tileset
3. **Paint the layout** matching Crystal's design but at GBA quality
4. **Set metatile behaviors** (walkable, surfable, ledge, warp, etc.)
5. **Add events**: NPC object events, warps, triggers, sign scripts
6. **Set map connections** to adjacent maps (e.g., New Bark Town connects to Route 29 east)
7. **Save** — Porymap auto-generates all JSON and layout files

### 2.4 — Dimension reference (Crystal → Emerald)
Crystal measures in 32x32 blocks; Emerald in 16x16 metatiles. Scale factor is roughly 2:1.

| Crystal Map | Crystal Size (blocks) | Emerald Size (metatiles) | Notes |
|---|---|---|---|
| New Bark Town | 10×9 | 20×18 | Small starter town |
| Cherrygrove City | 15×10 | 30×20 | |
| Violet City | 20×18 | 40×36 | Has Sprout Tower |
| Goldenrod City | 20×30 | 40×54+ | Largest Johto city, may need splitting |
| Route 29 | 30×9 | 60×18 | Long horizontal route |

Note: GBA maps can be much larger than GB maps. You don't need to split most maps. However, very large cities like Goldenrod may benefit from being split into sections for performance (like Emerald does with Lilycove).

---

## Phase 3: Region Switching System (Week 4-5)

### 3.1 — Region ID system
Create `include/constants/region.h`:
```c
#ifndef GUARD_CONSTANTS_REGION_H
#define GUARD_CONSTANTS_REGION_H

#define REGION_HOENN  0
#define REGION_JOHTO  1

#endif
```

### 3.2 — Track current region
Add a variable to track which region the player is in. Store it in a save-safe location (a flag or var):
```c
// Use one of the unused VAR slots
#define VAR_CURRENT_REGION  VAR_UNUSED_0x40F  // pick an unused var
```

### 3.3 — Region transition trigger
Create a warp/script event that transitions between regions. For example, a boat from Olivine City to Vermilion/Littleroot, or the S.S. Aqua:

```
// In a map script (Poryscript syntax):
script OlivinePort_SailToHoenn {
    lock
    msgbox("Board the S.S. Aqua to Hoenn?", MSGBOX_YESNO)
    if (var(VAR_RESULT) == YES) {
        setvar(VAR_CURRENT_REGION, REGION_HOENN)
        // fade, play ship animation
        warp(MAP_LILYCOVE_CITY_HARBOR, 5, 3)
    }
    release
}
```

### 3.4 — Fly map per region
The Fly/Town Map system needs to show different maps per region. Study how Crossroads handles this in `src/region_map.c`. The approach is:

1. Create a second region map image (`graphics/pokenav/johto_region_map.png`)
2. Define Johto landmark coordinates in a new data table
3. Modify `src/region_map.c` to check `VAR_CURRENT_REGION` and load the appropriate map image and landmark table
4. Filter the Fly destination list to only show locations in the current region

This is one of the more complex code changes. Reference Crossroads' implementation closely.

---

## Phase 4: Scripts & Events (Weeks 5-8)

### 4.1 — Port NPC dialogue
For each map, read Crystal's script file (e.g., `maps/NewBarkTown.asm`) and rewrite the dialogue in pokeemerald's scripting format.

**Crystal script (Z80 asm):**
```asm
ElmsLabElmScript:
    faceplayer
    opentext
    writetext ElmText_Pokemon
    waitbutton
    closetext
    end
```

**Emerald equivalent (Poryscript):**
```
script ElmsLab_Elm {
    lock
    faceplayer
    msgbox("Ah, {PLAYER}! I've been waiting!\n"
           "I have a favor to ask of you...", MSGBOX_DEFAULT)
    release
}
```

### 4.2 — Gym leader battles
Define trainer data in `src/data/trainers.h`. Each Johto gym leader needs:
- Party definition (species, level, moves, held items — all vanilla IDs only!)
- Pre-battle and post-battle scripts
- Badge reward logic (use available flag slots)

### 4.3 — Wild encounters
Edit `src/data/wild_encounters.json` to add entries for each Johto map:
```json
{
    "map": "MAP_ROUTE29",
    "base_label": "gRoute29_LandMons",
    "land_mons": {
        "encounter_rate": 25,
        "mons": [
            { "min_level": 2, "max_level": 4, "species": "SPECIES_PIDGEY" },
            { "min_level": 2, "max_level": 4, "species": "SPECIES_SENTRET" },
            ...
        ]
    }
}
```

Use Crystal's `data/wild/` as your reference for which Pokémon appear where. All species must use vanilla Emerald species constants (they're all Gen 1-3, which is perfect for Johto).

### 4.4 — Item locations
Place items using Porymap's event editor (hidden items, Poké Ball items on the ground). Reference Crystal's item placement but adjust for GBA conventions.

---

## Phase 5: Progression & Story Integration (Weeks 7-10)

### 5.1 — Decide your game flow
Key design decision: How does the player reach Johto?

**Option A — Post-game unlock:** Player beats Hoenn Elite Four, then unlocks a boat/ticket to Johto (like FRLG's Sevii Islands). Simplest to implement, minimal Hoenn changes.

**Option B — Mid-game branch:** Player can travel to Johto at some story point and go back and forth. More complex flag management.

**Option C — Johto first:** Player starts in Johto, travels to Hoenn later. Requires reworking the intro sequence.

**Recommendation for link compat: Option A.** It minimizes changes to the Hoenn story flow, keeping the vanilla progression gates for trading intact (the player still beats the E4, gets National Dex, and can trade normally).

### 5.2 — Flag management
pokeemerald has system flags and trainer flags. You'll need flags for:
- Johto gym badges (8 flags)
- Johto story progression events (~20-40 flags)
- Johto trainer defeated flags (~100-200 flags)
- Item pickup flags (~50-100 flags)

There are plenty of unused flag slots in vanilla Emerald. Audit `include/constants/flags.h` for available ranges. Flags are save-local and never transmitted over link cable.

### 5.3 — Badge system
You'll need to handle having two sets of badges. The simplest approach: Johto badges are tracked via flags but don't affect the vanilla badge-check system (which gates HM usage and obedience). Instead, implement Johto HM/obedience checks via script conditions.

---

## Phase 6: Link Compatibility Testing (Ongoing)

### 6.1 — Test matrix
After each major phase, test ALL of these in mGBA with link cable emulation:

| Test | Your Hack → Vanilla | Vanilla → Your Hack |
|---|---|---|
| Link to Emerald | ☐ | ☐ |
| Link to Ruby | ☐ | ☐ |
| Link to Sapphire | ☐ | ☐ |
| Link to FireRed | ☐ | ☐ |
| Link to LeafGreen | ☐ | ☐ |
| Trade Pokémon | ☐ | ☐ |
| Trade holds item | ☐ | ☐ |
| Link battle (singles) | ☐ | ☐ |
| Link battle (doubles) | ☐ | ☐ |
| Pokémon received shows correct data | ☐ | ☐ |
| No Bad Eggs generated | ☐ | ☐ |

### 6.2 — Automated sanity checks
Create a script that verifies your build hasn't accidentally modified critical tables:

```bash
#!/bin/bash
# verify_link_compat.sh — run after every build

VANILLA_ROM="pokeemerald_vanilla.gba"
HACK_ROM="pokeemerald.gba"

# Compare species table size
echo "Checking species count..."
# The species table should have the same number of entries

# Compare ROM header game code
echo "Checking game code..."
# Bytes at 0xAC-0xAF should be "BPEE"
xxd -s 0xAC -l 4 "$HACK_ROM" | grep -q "4250 4545" && echo "PASS: Game code BPEE" || echo "FAIL: Game code changed!"

# Check GameFreak magic string exists
echo "Checking GameFreak magic..."
strings "$HACK_ROM" | grep -q "GameFreak inc." && echo "PASS: Magic string present" || echo "FAIL: Magic string missing!"
```

### 6.3 — PKHeX validation
Open your hack's save file in PKHeX periodically. Verify that Pokémon caught in Johto maps appear with valid data (legal species, moves, met location). Met-location data is stored in the Pokémon struct — vanilla games will just show "met in a trade" or display the location ID. As long as you don't exceed the vanilla location ID range, this is fine. Pokémon met in your custom Johto maps will show unfamiliar location names on vanilla games (or "faraway place"), but the data will be structurally valid.

---

## Phase 7: Polish & Region Map (Weeks 9-12)

### 7.1 — Johto region map graphic
Create `graphics/pokenav/johto_map.png` — a top-down region map image for the PokéNav/Fly screen. Can be drawn pixel art or traced from Crystal's town map.

### 7.2 — Music
Johto has iconic music. Your options:
- **Port Crystal's music to GBA format:** The tracks need to be converted from Game Boy sound to GBA's mixer format. Some community members have already done MIDI conversions of GSC music. Check PokéCommunity's music resources.
- **Reuse Emerald's music:** Simpler but loses Johto flavor.
- **Use HGSS-inspired arrangements:** Some exist as community resources.

Music is stored in `sound/songs/` and never affects link compatibility.

### 7.3 — Pokédex area display
If you want the Pokédex's "Area" feature to show Johto locations, you'll need to extend the area map system. This is optional — it won't break linking if skipped.

---

## Key Reference Projects

| Project | URL | What to Study |
|---|---|---|
| pret/pokecrystal | github.com/pret/pokecrystal | Map layouts, scripts, wild data, trainer teams |
| pret/pokeemerald | github.com/pret/pokeemerald | Your base — map format, build system, link code |
| eonlynx/pokecrossroads | github.com/eonlynx/pokecrossroads | Multi-region architecture, fly map, region switching |
| StrangeQuark/pokeemerald | github.com/StrangeQuark/pokeemerald | Cleaner 3-region merge base |
| Pokémon Heart & Soul | pokecommunity.com thread | Completed Johto GBA hack, tileset reference |
| FRLG+ by Deokishisu | pokecommunity.com thread | Link-compatible hack design philosophy |

---

## Estimated Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| 0. Setup | 2 days | Build verified, references cloned, Porymap working |
| 1. Tilesets | 2-3 weeks | All Johto tilesets created and loadable |
| 2. Map layouts | 3-4 weeks | All ~120 Johto maps painted in Porymap |
| 3. Region switching | 1-2 weeks | Player can warp between Hoenn and Johto |
| 4. Scripts & events | 3-4 weeks | NPCs, gyms, trainers, wild encounters functional |
| 5. Story integration | 2-3 weeks | Full Johto story playable |
| 6. Testing | Ongoing | Link compatibility verified at each milestone |
| 7. Polish | 2-3 weeks | Music, region map, UI polish |
| **Total** | **~14-20 weeks** | **Playable Johto region with vanilla link compat** |

---

## Quick-Start Checklist

- [ ] Fork `pret/pokeemerald`, verify clean build
- [ ] Clone `pret/pokecrystal` as reference
- [ ] Clone `eonlynx/pokecrossroads` as architecture reference
- [ ] Install Porymap 6.x, verify it opens your project
- [ ] Set up mGBA link cable testing with a vanilla Emerald ROM
- [ ] Create first test map: NewBarkTown (simplest Johto map)
- [ ] Add NewBarkTown to map groups, verify it compiles
- [ ] Add a debug warp from Littleroot to NewBarkTown
- [ ] Walk around NewBarkTown in your hack
- [ ] Test link trade with vanilla Emerald — **your first compatibility gate**
- [ ] If trade works: proceed to Phase 1 at full speed
- [ ] If trade fails: you changed something you shouldn't have — diff against vanilla
