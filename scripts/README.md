# Scripts

Python helpers for hg-engine. See `.cursor/rules/agents.mdc` § **Scripts layout** for the rules agents should follow.

| Folder | Purpose |
|--------|---------|
| `build/` | Build pipeline — referenced from `Makefile`, `narcs.mk`, `overlays.mk`, or `data/codetables.mk` |
| `dev/` | Reusable inspect/verify tools for map scripts, zone events, trainers, etc. |
| `local/` | One-off recon and session experiments — **gitignored** (except this README chain) |
| `fixed/` | monData numbering metadata — unrelated to the layout above |

## `build/` inventory

| Script | Wired from |
|--------|------------|
| `make.py` | `Makefile` — overlay injection |
| `generate_ld.py` | `Makefile`, `overlays.mk` — linker scripts |
| `msg_cat.py` | `narcs.mk` — rawtext generation |
| `gen_level_up_evo_tables.py` | `narcs.mk` → `src/field/level_up_evo_tables.c` |
| `rebuild_json.py` | `narcs.mk` — zone_event JSON rebuild |
| `build_learnsets.py` | `data/codetables.mk` |
| `build_tests.py` | `data/codetables.mk` |
| `update_machine_moves.py` | `Makefile` |
| `check_rod_guru_text.py` | `narcs.mk` |
| `verify_r44_rod_guru_patch.py` | `narcs.mk` |
| `verify_olivine_rod_guru_scr_seq.py` | `narcs.mk` |
| `rod_guru_patch_checks.py` | imported by rod guru patcher + verify script |
| `gen_wild_level_caps.py` | `narcs.mk` → `src/field/wild_level_caps_data.c` |
| `patch_level_up_evo_addrs.py` | `Makefile`, `make.py` — patch level-up + synthetic table addresses into overlay 129 |
| `gen_synthetic_evo_edges.py` | `narcs.mk` → `src/field/synthetic_evo_edges_data.c` |

## `dev/` highlights

Common entry points (run from repo root after a build):

```bash
python3 scripts/dev/inspect_zone_event.py build/a032/2_<NNN>
python3 scripts/dev/inspect_scr_seq.py build/a012/2_<NNN>
python3 scripts/dev/dump_scr_seq_slots.py build/a012/2_<NNN>
python3 scripts/dev/verify_scr_seq_patch.py build/a012_vanilla/2_<NNN> build/a012/2_<NNN>
```

Feature-specific verify scripts: `verify_*_patch.py`, `verify_r44_zone_event.py`, `verify_olivine_rod_guru_zone_event.py`, etc.

Placement / text recon: `find_zone_event_member.py`, `find_msg_text.py` (see HACK-NOTES § World placement).

**Route Levels** (`dev/Route Levels/`): world graph + distance matrix for [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps). Run `calculate_location_distances.py` after editing `connections.txt`; `gen_wild_level_caps.py` (build/) consumes the outputs at make time.

**Synthetic evolution stages:** `data/synthetic_evolution_thresholds.tsv` → `scripts/build/gen_synthetic_evo_edges.py` → `src/field/synthetic_evo_edges_data.c` (see `narcs.mk`). Sanity check: `python3 scripts/dev/verify_encounter_stage.py`.

Test runner: `scripts/dev/run_tests.sh` (also used by CI).

## `local/`

Throwaway scripts live here. Prefix with `_` when possible. When something graduates to `dev/` or `build/`, move the file and update Makefile/docs references.
