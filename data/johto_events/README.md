# Johto Event Matrix

`pre_league_event_matrix.json` is the machine-readable source of truth for Crystal-to-Emerald event parity work up to the Indigo Plateau / Hall of Fame.

`official_link_compatibility_manifest.json` is the companion source of truth for official Gen 3 interoperability guardrails. It records which Johto subsystems are save-only, local-only, or link-visible, and whether each one is already retail-safe.

Regenerate it with:

```bash
python3 scripts/generate_johto_event_matrix.py
```

Validate the compatibility manifest with:

```bash
python3 scripts/validate_official_link_compat_manifest.py
```

Each map entry includes:

- `crystal_map` and `crystal_map_id`
- `story_arc`
- `import_status` and optional Emerald target metadata
- `scene_scripts`
- `callbacks`
- `warp_events`
- `coord_events`
- `bg_events` plus `bg_event_counts_by_kind`
- `object_events` plus `object_event_counts_by_type`
- `visibility_time_gates`
- `referenced_flags`
- `referenced_vars`
- `script_refs`
- `unresolved_script_refs`
- `command_coverage`
- `unsupported_commands`
- `text_policy`
- `generated_status`
- `runtime_requirements`
- `script_asset_counts`
- `scene_ids`
- `object_consts`
- `std_calls`
- `substitute_tags`
- `substitute_system_policy`
- `acceptance_scenarios`

This file is meant to answer two questions quickly:

- What Crystal event mechanics exist on this map?
- What Emerald-side work still needs to happen for parity?
