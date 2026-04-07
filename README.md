# Pokemon Emerald Gold

This repository is a Crystal-first Johto port built on top of the `pokeemerald` decompilation.

The current development direction is:
- make Johto the active playable region
- import Crystal map topology exactly from `pokecrystal`
- keep Emerald-compatible runtime structures and link-sensitive boundaries intact
- use Johto-owned Gen 3 tilesets and borders instead of Hoenn placeholder map shells

The main development build is:
- `make modern -j2`

That produces:
- `pokeemerald_modern.gba`

## Status

The project has already replaced the Hoenn truck start with a Johto bootstrap and now uses an exact-size Crystal import pipeline for a connected New Bark -> Route 29 -> Cherrygrove pilot slice.

Current active pilot area:
- New Bark Town
- Player's House 1F/2F
- Player's neighbor's house
- Elm's House
- Elm's Lab
- Route 29
- Route 29 Route 46 Gate
- Cherrygrove City
- Cherrygrove Mart
- Cherrygrove Pokecenter 1F/2F
- Guide Gent's House
- Cherrygrove Gym Speech House
- Cherrygrove Evolution Speech House

The next major objective is expanding that exact import pipeline from New Bark to the rest of Johto through Indigo Plateau.

## References

The port uses side-by-side reference repos outside this repository:
- `pokecrystal`
- `pokefirered`

Default sibling locations:
- `/Users/niach/WebstormProjects/pokecrystal`
- `/Users/niach/WebstormProjects/pokefirered`

These are treated as source material for topology and visual borrowing. Runtime assets and generated outputs remain committed in this repository.

## Important Docs

- Project tracker: [CLAUDE.md](CLAUDE.md)
- Setup notes: [INSTALL.md](INSTALL.md)

## Core Commands

Build the main ROM:

```sh
make modern -j2
```

Regenerate the exact-size Johto import slice:

```sh
python3 scripts/import_johto_maps.py
```

Validate imported Johto maps:

```sh
python3 scripts/validate_johto_maps.py
```

Render Johto preview sheets:

```sh
python3 scripts/render_johto_previews.py
```
