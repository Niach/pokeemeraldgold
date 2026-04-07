# CLAUDE.md

## Project

Pokemon Emerald Gold is a Crystal-first Johto port built on top of `pokeemerald`.

The goal is to port the Johto main-game world through Indigo Plateau while preserving Emerald-compatible runtime structures where that matters for stability and compatibility.

## Core Intent

- Johto is the active playable direction.
- `pokecrystal` is the authority for map topology, dimensions, block layout, warps, signs, object coordinates, and traversal shape.
- Emerald and FireRed are visual source pools, not topology authorities.
- New Johto maps should not be hand-patched from Hoenn placeholders.

## Current Strategy

The active map strategy is an exact-size Crystal import pipeline.

That means:
- imported Johto layouts use exact Crystal block dimensions
- Emerald layout size is `crystal block width * 2` by `crystal block height * 2`
- borders handle off-map camera fill
- padding, anchor offsets, and filler-floor room shells are not the authoritative path anymore
- Crystal block translation is owned by shared blockset families, not ad hoc per-room hacks

## Authoritative Inputs

Exact Johto import manifests:
- [data/johto_import/crystal_tilesets.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/johto_import/crystal_tilesets.json)
- [data/johto_import/maps.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/johto_import/maps.json)
- [data/johto_import/crystal_ir](/Users/niach/WebstormProjects/pokeemeraldgold/data/johto_import/crystal_ir)

Importer and validator:
- [scripts/import_johto_maps.py](/Users/niach/WebstormProjects/pokeemeraldgold/scripts/import_johto_maps.py)
- [scripts/validate_johto_maps.py](/Users/niach/WebstormProjects/pokeemeraldgold/scripts/validate_johto_maps.py)

Tileset atlas and previews:
- [data/johto_tilesets/tileset_inventory.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/johto_tilesets/tileset_inventory.json)
- [scripts/render_johto_previews.py](/Users/niach/WebstormProjects/pokeemeraldgold/scripts/render_johto_previews.py)

Build wiring:
- [map_data_rules.mk](/Users/niach/WebstormProjects/pokeemeraldgold/map_data_rules.mk)
- [json_data_rules.mk](/Users/niach/WebstormProjects/pokeemeraldgold/json_data_rules.mk)

## Current Milestone

The current milestone is a connected New Bark -> Route 29 -> Cherrygrove pilot slice running through the exact Crystal import pipeline.

Imported New Bark slice:
- [data/maps/NewBarkTown/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/NewBarkTown/map.json)
- [data/maps/NewBarkTown_PlayersHouse_1F/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/NewBarkTown_PlayersHouse_1F/map.json)
- [data/maps/NewBarkTown_PlayersHouse_2F/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/NewBarkTown_PlayersHouse_2F/map.json)
- [data/maps/PlayersNeighborsHouse/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/PlayersNeighborsHouse/map.json)
- [data/maps/ElmsHouse/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/ElmsHouse/map.json)
- [data/maps/ElmsLab/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/ElmsLab/map.json)
- [data/maps/Route29/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/Route29/map.json)
- [data/maps/Route29Route46Gate/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/Route29Route46Gate/map.json)
- [data/maps/CherrygroveCity/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/CherrygroveCity/map.json)
- [data/maps/CherrygroveMart/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/CherrygroveMart/map.json)
- [data/maps/CherrygrovePokecenter1F/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/CherrygrovePokecenter1F/map.json)
- [data/maps/Pokecenter2F/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/Pokecenter2F/map.json)
- [data/maps/GuideGentsHouse/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/GuideGentsHouse/map.json)
- [data/maps/CherrygroveGymSpeechHouse/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/CherrygroveGymSpeechHouse/map.json)
- [data/maps/CherrygroveEvolutionSpeechHouse/map.json](/Users/niach/WebstormProjects/pokeemeraldgold/data/maps/CherrygroveEvolutionSpeechHouse/map.json)

Current outcome:
- New Bark interiors now regenerate from exact-size Crystal imports instead of padded room canvases.
- Route 29 and Cherrygrove are scaffolded through the same importer and connection pipeline.
- Borders are defined by shared tileset family.
- Exact warps compile from Crystal map ids and 1-based warp numbers into Emerald targets.
- Generated Crystal tilesets currently cover `johto`, `players_house`, `players_room`, `house`, `lab`, `gate`, `pokecenter`, and `mart`.
- The runtime fixes now include correct indoor palettes, working house stairs, non-walkable outdoor water, and corrected banked-tile rendering for Elm's Lab.

## Known Gaps

- The importer currently owns layouts, borders, warp topology, connections, and selected event placement, but it does not auto-convert Crystal story/dialogue scripts.
- Farther Johto endpoints outside the current slice still resolve as explicit placeholders until those maps are imported too.
- Bootstrap-only local actors should be removed when a map becomes Crystal-authored. `PlayersHouse1F` was cleaned up as part of this pass after a duplicate non-Crystal NPC was spotted in runtime.

## Next Steps

1. Manually verify New Bark, Route 29, and Cherrygrove in mGBA after each importer change.
2. Extend exact-generated tileset coverage to the remaining Johto families needed for the next routes and towns.
3. Continue importing outward through the Johto overworld in connected chunks rather than room-by-room repair.
4. Replace remaining bootstrap event/script shims with Crystal-authored map content as each slice becomes stable.

## Guardrails

- Do not touch `src/link.c`, `src/trade.c`, or compatibility-critical protocol/data boundaries unless explicitly intended.
- Do not reintroduce padded room shells as the runtime source of truth for imported Johto maps.
- Do not express Johto topology through Hoenn-specific placeholder map geometry.
- Prefer shared blockset-family fixes over local map hacks.
- Keep `make modern` as the active development target.

## Useful Commands

Build:

```sh
make modern -j2
```

Regenerate imported Johto maps:

```sh
python3 scripts/import_johto_maps.py
```

Validate imported Johto maps:

```sh
python3 scripts/validate_johto_maps.py
```

Render preview sheets:

```sh
python3 scripts/render_johto_previews.py
```

## Reference Repos

Expected sibling references:
- `/Users/niach/WebstormProjects/pokecrystal`
- `/Users/niach/WebstormProjects/pokefirered`

`pokecrystal` is the topology source of truth.

`pokefirered` is a visual/metatile source pool when Emerald alone is insufficient.
