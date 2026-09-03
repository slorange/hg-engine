# Hack notes: what HG-Engine exposes (and what it doesn’t)

Working notes for this fork so we don’t re-discover the text/data layout every session.

## Git (agents)

**Read-only only.** Agents may run git commands that **inspect** state (`status`, `diff`, `log`, `show`, etc.). **Never commit, push, merge, rebase, reset, checkout, add, stash, or any other mutating git action** — the user handles all of that themselves. If they say they’re committing, they mean they will do it; don’t beat them to it.

## Why the Mom line was hard to find

It wasn’t “lots of lines in the repo.” **That dialogue was not in the repo at all.**

- HGSS stores dialogue/UI strings in msgdata NARC `a/0/2/7` (~**854** text banks).
- HG-Engine only **overrides** banks that exist as `data/text/<bank>.txt` (or are generated into `build/rawtext/` at compile time).
- At the time of the first search we tracked ~**45** banks (~**5%**). Mom’s early-game line lived in **bank 545**, still vanilla until we dumped it.

So: grepping the repo will miss most field dialogue until that bank is dumped into `data/text/`.

## How text editing works

1. Build extracts vanilla `base/root/a/0/2/7`.
2. For every `data/text/*.txt` (and generated `build/rawtext/*.txt`), `msgenc` encodes and **replaces** that bank by number (`7_<bank>`).
3. Untouched banks stay vanilla.

**To edit a missing line:**

1. Confirm `base/root/a/0/2/7` exists (after a successful build/extract).
2. Decode banks with `tools/msgenc -d -c charmap.txt` until you find the string (or script a scan).
3. Write the full bank to `data/text/<N>.txt`, edit the line, rebuild.
4. Keep the **entire bank** — replacing a bank replaces all of its strings.

Control codes you’ll see: `\n` newline, `\r` paragraph/advance, `\f` scroll, `{STRVAR_...}`, `{YESNO 0}`, etc. Validate with the build’s text checker.

## Known `data/text` banks (tracked / important)

| Bank | Role (approximate) |
|------|--------------------|
| 040 | Pokémon Center, save prompts, some Mom-at-rest text |
| **545** | **New Bark Mom house dialogue** (dumped for our test; includes “Professor Elm has been waiting…”) |
| **374** | **Route 29/46 gatehouse dialogue** (includes badge gate line) |
| 197 | Battle system messages |
| 203 | Blackout / hurry-to-Center text |
| 222 | Item names |
| 300 / 302 | Party / bag-ish UI strings |
| 435 | Shop / mart dialogue |
| 720–722 | Ability names / related |
| 728 / 729 | Trainer battle text / names (**generated** from trainer data) |
| 730 / 731 | Trainer class names |
| 003 / 749–751 | Move names/descriptions (**generated** from move data) |
| 237 / 238 / 803 / 812–817 / 823 | Species names / dex-ish strings (**generated** from species data) |
| 829–853 | Expanded item/dex/UI-style banks for newer content |
| 010 / 024 / 221 / 223 / 224 / 735 / 811 | Smaller / placeholder / misc UI banks — inspect before editing |

Generated banks: prefer editing the **source data** (`data/Moves.c`, `data/Species.c`, `data/Trainers.c`, etc.), not hand-editing `build/rawtext/`.

## Easy wins vs awkward targets

**Usually easy (in-repo source):**

- Pokémon / moves / items / abilities / learnsets / evolutions / encounters / trainers → `data/*.c`, `data/learnsets/`, `data/itemdata/`, wiki docs under `documentation/wiki/`
- Battle scripts → `data/battle_scripts/`
- Battle engine / field C → `src/battle/`, `src/field/`, `src/individual/`
- Compile toggles → `CONFIG.md`, `include/config.h`, `armips/include/config.s`
- Text **already** under `data/text/` → edit + rebuild

**Awkward / not simply in-repo yet:**

- **Map location banners** (e.g. “New Bark Town” / “Winds of a New Beginning”) — not found in tracked text; treat as vanilla until we identify the bank/system
- **Most overworld NPC dialogue** — still in undumped msg banks
- **Map scripts / events** — `armips/scr_seq/` and `data/zone_event/` (see **Badge gate blocks** below)

## Build and verification

**Agents are expected to run builds** when verifying implementation work — the user does not build manually for routine agent tasks.

| File | Role |
|------|------|
| `rom.nds` | User-provided base ROM (input). **Never commit.** |
| `test.nds` | Build output for DeSmuME / manual playtesting. **Never commit.** |
| `build/` | Intermediate artifacts (NARCs, objects, extracted vanilla). Regenerated; do not commit. |

### How to build (this fork)

**Prefer Docker** on this machine — native MSYS2/UCRT64 linking has been unreliable with hg-engine’s dual linker scripts.

1. **One-time:** `docker build . -t hg-engine`
2. **Full ROM:** `./docker-makerom.cmd` (interactive shell that runs `make`), **or** non-interactive:

```bat
docker run --rm --mount "type=bind,source=<repo-path>,destination=/hg-engine" hg-engine bash -lc "cd /hg-engine && make -j24"
```

3. Load **`test.nds`** in DeSmuME. Use a **new save** after changes to intro scripts, starting city, or flags-on-load patches.

Upstream native/WSL setup (without Docker): [README.md](../README.md).

### Build types

| Command | Use when | Output / notes |
|---------|----------|----------------|
| `make -j24` | Default — verify any change end-to-end | Full **`test.nds`**: C/asm (`src/`, `asm/`), `data/*.c`, armips, NARC rebuild, overlays |
| `make build/narc/scr_seq.narc build/narc/zone_event.narc NOSCAN=1` | Iterating on scr_seq / zone_event only | NARCs only; still repack `test.nds` before in-game test |
| `make scr_seq_clean && make -j24` | Suspect scr_seq corruption or duplicate NPCs after patch | Clears scr_seq build artifacts, then full rebuild |
| `make clean_code && make -j24` | C/asm changed but objects seem stale | Drops compiled code objects only |
| `make clean && make -j24` | Broken build state, tool rebuild, or “nothing makes sense” | Full clean (slow) |
| `make AUTO_TEST=Y -j24` | Battle-engine automated tests | Same **`test.nds`** name, compiled with `DEBUG_BATTLE_SCENARIOS`; see [data/battle_tests/README.md](../data/battle_tests/README.md) |
| `make restore_build` | Reset extracted `base/` from `rom.nds` then rebuild | Nuclear reset of extracted filesystem |

**`NOSCAN=1`** skips dependency scanning — use for targeted NARC targets to save time; not a substitute for a full verify before calling something done.

**Compile toggles** (`HEAL_AFTER_BATTLE`, trainer scaling, open-world grants, etc.) live in `include/config.h` and `armips/include/config.s` — documented in [CONFIG.md](../CONFIG.md) and [Index-2](DESIGN.md#index-2-current-technical-baseline).

### What a full build covers (roughly)

1. **Tools** — armips, nitrogfx, msgenc, ndstool, patch scripts, …
2. **Generated data** — species/move/trainer text banks, learnsets, evo tables, …
3. **NARCs** — encounters, scr_seq, zone_event, sprites, msgdata overrides from `data/text/`, …
4. **Engine code** — `src/` + overlays linked into `base/`
5. **Pack** — `test.nds` from `rom.nds` + modified `base/root/`

Field-script recipes in this file often add Python **verify_*.py** scripts — run those after the relevant `make` when listed.

## Build workflow on this machine

- Prefer **Docker** (UCRT64 + binutils 2.47 broke ARM linking with the dual linker scripts).
- First time / dirty MSYS leftovers: clear Windows-built `tools/source/**/*.o` before Linux Docker builds.
- Typical rebuild (replace path with repo root):

```bat
docker run --rm --mount "type=bind,source=C:\msys64\home\Sylvain\git\hg-engine,destination=/hg-engine" hg-engine bash -lc "cd /hg-engine && make -j24"
```

- Do **not** commit `rom.nds`. `test.nds` is a build output.
- After text-only edits, rebuilds are much faster than a cold first build.

## Quick “find this dialogue” checklist

1. `rg` / search in `data/text/` and `data/*.c` (trainer speech lives in `data/Trainers.c`).
2. If missing: scan decoded msgdata banks (Docker + `msgenc` + `ndspy`).
3. Dump full bank → `data/text/<N>.txt` → edit → `make` in Docker → reload `test.nds`.

## Scope reminder (upstream)

HG-Engine’s main focus is the **battle engine** and related expansions (dex, moves, abilities, items, trainers). Field/story editing is possible but less paved; expect more ROM archaeology for map banners and random NPC lines.

---

## Badge gate blocks (field scripting)

Reusable pattern: walk-past coord trigger → script checks badge count → message + step player back, or pass through if requirement met.

### Three IDs per map (don’t mix them up)

| What | Route 46 example | Override file |
|------|------------------|---------------|
| **Map header** (game constant) | `MAP_R29R0101` = **134** | — |
| **Map scripts** (`scr_seq.narc` / `a/0/1/2`) | member **226** | `armips/scr_seq/scr_seq_00226_R29R0101.s` |
| **Map events** (`zone_event.narc` / `a/0/3/2`) | member **130** | `data/zone_event/130_R29R0101.json` |

**Gotcha:** map header ID ≠ scr_seq index ≠ zone_event index. We once overwrote scr_seq **134** (`D52R0102`, a dungeon) instead of **226**; bad overrides can stick in `base/root/` until you restore `a/0/1/2` and/or `a/0/3/2` from a clean `rom.nds` extract.

To find indices for another map: pret decomp names (`130_R29R0101.json`, `scr_seq_00226_R29R0101.s`) or `scripts/_scan_zone_events.py` on `base/root/a/0/3/2`.

### Recipe for a new gate

1. **Zone events** — copy vanilla JSON from pret (`files/fielddata/eventdata/zone_event/<index>_<MAP>.json`) into `data/zone_event/`. Add a `coords` entry:
   - `scriptId`: gate script slot + 1 (e.g. `_EV_scr_seq_R29R0101_000 + 1`)
   - `x`, `z`, `w`, `h`: rectangle on the guard line (`w` = width in x, `h` = depth in z)
   - `var`: must **not** be `0` (that disables the trigger); use e.g. `VAR_TEMP_x400F`
   - `val`: compare value (often `0`)
2. **Script** — in the matching `armips/scr_seq/scr_seq_XXXXX_<MAP>.s`, use an empty slot (often `_000`):
   - `scrcmd_609`, `lockall`, `count_badges`, compare, `goto_if_ge` pass branch
   - else: `faceplayer`, `npc_msg <index>`, `apply_movement obj_player, …`, `wait_movement`, `wait_button_or_walk_away`, `closemsg`, `releaseall`
   - Step-back movement: **`step 13` (south) + `step 1` (face down)** — relative `step 104` only turned the player without moving
3. **Text** — gate line in the map’s msg bank (`data/text/<bank>.txt`); add a line, set `npc_msg` to that index
4. **Build** — Docker `make -j24` → test in `test.nds`

### Zone event rebuild (Makefile)

1. Vanilla extract → `build/a032/2_<index>`
2. `tools/zone_event_enc.py` on each `data/zone_event/*.json`
3. Repack → ROM as `a/0/3/2`

Helper files: `tools/zone_event_enc.py`, `data/zone_event/events/event_<MAP>.h`, `scripts/test_zone_event_roundtrip.py`.

### Route 46 gate (reference implementation)

**Goal:** block Route 29 ↔ Route 46 gatehouse until **2 badges**.

| File | Role |
|------|------|
| `data/zone_event/130_R29R0101.json` | Coord trigger + vanilla objects/warps |
| `armips/scr_seq/scr_seq_00226_R29R0101.s` | Slot `_000`: badge check + step-back |
| `data/text/374.txt` | Gate message at index 2 |

**Layout** (`130_R29R0101.json`):

- South warp → Route 29: `(x=5, z=12)`
- North warp → Route 46: `(x=5, z=2)`
- Counter NPC: `(x=1, z=8)` — slot `_001` talk script
- Boy NPC: `(x=7, z=6)` — slot `_002` talk script

**Coord trigger** (guard line, full walkable width):

- `(x=2, z=8)`, `w=7`, `h=1` — tiles x=2–8 at the counter row
- Script `_000+1`, `var=VAR_TEMP_x400F`, `val=0`

**Dialogue** (bank 374, index 2): *“Whoa! It's not safe for you to go through here yet. Come back after you've earned at least two Gym Badges.”*

Vanilla had no coord events on this map; slots `_001`/`_002` keep their NPC talk scripts unchanged.

---

## Remove Sudowoodo block (Route 36) — verified PoC

**Goal:** walk Violet ↔ Goldenrod / Ecruteak with **0 badges**; Sudowoodo never blocks the path. **Tested in-game:** tree gone, no collision, existing save OK.

### Wiring (pret decomp)

| What | ID / symbol |
|------|-------------|
| Map header | `MAP_R36` = **40** |
| scr_seq member | **243** — patched via `tools/patch_scr_seq_r36.py` |
| scr_seq init header | **488** (`scr_seq_00488_R36_hdr.s`) |
| zone_event member | **037** (`037_R36.json`) |
| Sudowoodo object | `obj_R36_usokky` |
| Hide flag | `FLAG_HIDE_ROUTE_36_SUDOWOODO` (**450**) |

Vanilla init header runs **`scr_seq_R36_010` on map load**. **`tools/patch_scr_seq_r36.py`** rewrites slot `_010` after scr_seq extract to **`setflag FLAG_HIDE_ROUTE_36_SUDOWOODO`** on every Route 36 load.

**Option B (fallback):** remove `obj_R36_usokky` from `037_R36.json` if the flag alone leaves collision (not needed — flag patch sufficient).

**Out of scope for now:** Floria / SquirtBottle / flower-shop chain, moving Sudowoodo encounter elsewhere.

---

## Remove Route 32 badge gate (south of Violet) — verified pattern

**Goal:** walk Route 32 toward Union Cave / Azalea with **0 badges**; no Cooltrainer M stop, no invisible barrier line.

### Wiring (pret decomp)

| What | ID |
|------|-----|
| Map header | `MAP_R32` = **36** |
| zone_event member | **033** (not 040 — that is Route 39 / Moomoo Farm) |
| scr_seq member | **232** (not 225 — that is Route 29) |

Vanilla gate: **coord script 3** at `(475,305)`; **obj1** sprite **328** `(477,305)` script **2** (GSMIDDLEMAN1 — renders as an old man). No Miltank barrier sprites (those live on Route 39 member 040). No outdoor-matrix duplicate found (unlike Mahogany).

**Gotcha:** map header ID ≠ zone_event index ≠ scr_seq index. Cross-check pret `map_headers.h` / `{NNN}_R32` filenames before patching.

| File | Role |
|------|------|
| `tools/patch_zone_event_r32_badge.py` | Remove blocker NPC, barriers, coord trigger |
| `tools/patch_scr_seq_r32_badge.py` | OnLoad sets flags **550/552**; NOP walk-past/coord/talk scripts |
| `narcs.mk` | Hook after scr_seq / zone_event extract |

**Test checklist:** new save → leave Violet south → no NPC stop, path walkable toward Ruins/Union Cave.

---

## Remove Surge / Erika Cut trees — gym access

**Status:** verified in-game (Aug 2026). 0 badges, no Cut — Vermilion Gym door, Celadon Gym door, and Erika inside Celadon Gym all reachable.

**Goal:** reach Vermilion and Celadon Gyms (and Erika inside her Gym) without Cut — [Story-1](DESIGN-STORY.md#story-1-story-and-script-content).

| Map | zone_event member | Trees removed |
|-----|-------------------|---------------|
| Vermilion City | **051** → `2_051` | 1 outside Gym |
| Celadon City | **052** → `2_052` | 1 outside Gym |
| Celadon Gym | **352** → `2_352` | 3 inside maze |

Cut trees are `SPRITE_TREE` (86) + `std_field_cut` (script 10000) objects — **not** Blender map geometry.

| File | Role |
|------|------|
| `tools/patch_zone_event_gym_cut_trees.py` | Strip matching tree objects from the three members above |
| `narcs.mk` | Hook after zone_event extract |

Surge Gym interior keeps the trash-can puzzle (no cut trees there).

**Verified:** new save, 0 badges, no Cut mon — walk to Vermilion Gym door; Celadon Gym door; inside Celadon Gym reach Erika without Cut.

---

## Heal after every battle

**Status:** verified (wild, trainer, flee, and catch tested in-game).

**Design:** [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition) — full HP/PP/status restore after every battle (wild, trainer, flee; no special exclusions).

| What | Where |
|------|--------|
| Toggle | `HEAL_AFTER_BATTLE` in `include/config.h` (enabled by default; comment out to disable) |
| Hook | existing `Battle_End` overlay hook → `BattleEndRevertFormChange` in `src/battle/battle_pokemon.c` |
| Logic | Nurse Joy–equivalent: max HP, clear status, `RestoreBoxMonPP` on save party + battle-work copies |

**Verified:** wild, trainer, flee, and catch all restore HP/PP/status on return to field.

---

## Full party EXP share (interim)

**Status:** verified in-game.

**Design:** interim stand-in until [Battle-7](DESIGN-BATTLES.md#battle-7-exp-share) battle-limit EXP share exists. Every non-fainted party member gets the **full** calculated EXP for each KO (not split). Fainted bench mons still get nothing. No Exp Share item required.

| What | Where |
|------|--------|
| Toggle | `FULL_PARTY_EXP_SHARE` in `include/config.h` (enabled by default) |
| Hook | `Task_DistributeExp_Extend` in `src/battle/battle_script_commands.c` |

**Verified:** bench mons gain EXP (and level) from wild/trainer KOs while only one mon is out in battle.

---

## Paid ferry / local bypass NPCs (reusable recipe)

**Status:** Route 42 reference implementation **verified in-game** (Aug 2026).

**Use when:** geography blocks travel (water without Surf, long mandatory gaps) and you want a **diegetic paid bypass** instead of a bridge edit or global fast travel. Same toolchain as badge gates, but adds **object NPCs** + **append scr_seq slots** instead of coord triggers.

**Do not use for:** story roadblocks (prefer removing them) or map-wide walkability (that is `land_data`, not scripts).

### Three IDs per map (don’t mix them up)

| What | Route 42 example |
|------|------------------|
| **Map header** (`include/constants/maps.h`) | `MAP_R42` = **44** |
| **scr_seq** (`a/0/1/2`) | member **252** |
| **zone_event** (`a/0/3/2`) | member **041** |
| **Text bank** | **399** (`data/text/399.txt`) |

Find indices via pret names (`041_R42.json`, `scr_seq_0252_R42.s`) or `scripts/_scan_zone_events.py`.

**Facing constants (object `facingDirection`):** pret `DIR_NORTH=0`, `DIR_SOUTH=1`, `DIR_WEST=2`, `DIR_EAST=3` (`global_fieldmap.h`).

**scriptId on objects/bg events = scr_seq slot index + 1** (slot `_006` → scriptId **7**).

### Recipe for a new ferry pair (copy Route 42)

1. **Recon in-game / DSPRE** — note world `(x, z)` for each shore NPC, landing tile after warp, and nearby sign/bg-event tiles (avoid placing NPC on same tile as a sign).

2. **scr_seq script** — one `.s` per crossing, e.g. `armips/scr_seq/scr_seq_<map>_ferry_west.s`:
   - Output blob: `build/<name>.bin` via `.create "build/....bin", 0` … `.close`
   - Flow: `play_se`, `lockall`, `faceplayer`, offer text (`npc_msg`), `yesno VAR_SPECIAL_RESULT`
   - **HGSS yes/no:** `0` = Yes, `1` = No → `compare VAR_SPECIAL_RESULT, 1` / `goto_if_eq` decline branch
   - `hasenoughmoneyimmediate` / `submoneyimmediate` for fee
   - `fade_screen` → `warp MAP_<X>, WARP_DOOR, <x>, <z>, DIR_*` → fade in → `releaseall` / `end`
   - Decline / no-money branches: message + `wait_button_or_walk_away` + `closemsg`

3. **Text** — append lines to the map’s msg bank (`data/text/<bank>.txt`). Reuse indices across ferries on the same map if dialogue is identical. Use curly apostrophe **`’`** (U+2019), not ASCII `'`.

4. **scr_seq patch tool** — copy/adapt `tools/patch_scr_seq_r42_ferry.py`:
   - Set `MEMBER_INDEX`, `PATCH_SOURCES`, `VANILLA_SCRIPT_COUNT`, slot numbers (`WEST_SLOT`, …)
   - **Always rebuild from vanilla** via `extract_scripts()` + `build_scr_seq()` — never insert bytes into the offset table (that corrupts existing sign/story scripts; see **Gotchas** below)
   - Hook in `narcs.mk` after scr_seq extract: `$(PYTHON) tools/patch_scr_seq_<map>_ferry.py $(SCR_SEQ_DIR)/2_<NNN>`

5. **zone_event patch tool** — copy/adapt `tools/patch_zone_event_r42_ferry.py`:
   - Pack `OBJECT_EVENT` (32 bytes): sprite, `movement 15` (stand), `type 0` (NPC), `scriptId`, facing, `x`, `z`
   - Use **unused object ids** above vanilla max; patcher should strip `id >= <first_ferry_id>` before re-adding (idempotent rebuild)
   - Hook in `narcs.mk` after zone_event extract: `$(PYTHON) tools/patch_zone_event_<map>_ferry.py $(ZONE_EVENT_DIR)/2_<NNN>`

6. **Header defs** — extend `data/zone_event/events/event_<MAP>.h` with new `_EV_scr_seq_*` slot `#define`s and `obj_*` ids.

7. **Build & test** — Docker `make -j1` (avoid `make clean` on Windows bind mounts). Close emulator, load fresh `test.nds`. Test: talk to NPC both sides, yes/no, no-money, warp landing visible and walkable, vanilla signs still readable.

### Route 42 reference (verified)

**Goal:** cross both Route 42 water gaps without Surf — one fisherman per outer shore, full crossing per trip.

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_r42_ferry_west.s` | Slot **6** (scriptId **7**) → warp to `(504, 173)` |
| `armips/scr_seq/scr_seq_r42_ferry_east.s` | Slot **7** (scriptId **8**) → warp to `(427, 178)` |
| `tools/patch_scr_seq_r42_ferry.py` | Rebuild member **252** from vanilla + 2 scripts |
| `tools/patch_zone_event_r42_ferry.py` | Objects **13** / **14** at `(429,177)` / `(502,172)` |
| `data/text/399.txt` | Indices **10–13** (offer / aboard / decline / no money) |
| `data/zone_event/events/event_R42.h` | Slot + object id defs |

**Fee:** $200. **Sprite:** fishing NPC (`347`).

### Debug helpers (keep using these)

| Script | Purpose |
|--------|---------|
| `scripts/inspect_zone_event.py build/a032/2_<NNN>` | bg events, objects, coords |
| `scripts/inspect_scr_seq.py build/a012/2_<NNN>` | script slot offsets |
| `scripts/dump_scr_seq_slots.py build/a012/2_<NNN>` | slot sizes + bytecode heads |
| `scripts/verify_scr_seq_patch.py build/a012_vanilla/2_<NNN> build/a012/2_<NNN>` | confirm vanilla slots unchanged |
| `scripts/decode_r42_objects.py` | quick object field dump (adapt member path) |

Vanilla scr_seq for recovery: `build/a012_vanilla/2_<NNN>` (extracted from `rom.nds` on first patch run).

### Gotchas

- **scr_seq append corruption:** inserting into the offset table shifts script bodies without updating old pointers → signs and story scripts break silently. `patch_scr_seq_r42_ferry.py` must **extract vanilla bodies and rebuild the table** (`build_scr_seq()` in `tools/patch_scr_seq_r42_ferry.py` / `tools/append_scr_seq_script.py`).
- **Healthy scr_seq size:** Route 42 member ~**1188 bytes** (8 scripts). Multi‑MB member = corrupt; patcher resets from vanilla when `count != VANILLA_SCRIPT_COUNT` or size > 8 KB.
- **Duplicate NPCs on rebuild:** zone_event patcher must delete prior ferry objects by id before re-adding.
- **Sign overlap:** bg-event signs and object NPCs on the same tile fight for interaction; offset NPC one tile from sign.
- **land_data ≠ ferry:** walking on water still needs terrain edits; ferries only skip the gap via warp. Failed bridge exports live in `rawdata/changed_maps/route_42/failed attempt at bridge/`; apply manually via `scripts/apply_changed_maps.py` (not in Makefile). Matrix loads land_data member **44** for Route 42 chunks — DSPRE export indices 082–084 ≠ runtime member.

### Route 42 bridges (abandoned)

**Status:** abandoned in favour of ferry NPCs above. Bridge metatile/collision experiments archived under `rawdata/changed_maps/route_42/failed attempt at bridge/` (members 082–084). See pret `041_R42.json` for vanilla sign/warp coords during recon.

**IDs (same map):** header **44**, zone_event **041**, scr_seq **252**, encounters **52**, text **399**. Shared Johto matrix — world coords ~x 422–504, z ~164–184.

Water walkability is **`land_data.narc`** (`a/0/6/5`), not scr_seq. hg-engine rebuilds scr_seq/zone_event automatically; land_data persists in `base/root/` until re-extracted from `rom.nds`.

**Pret references:** `files/fielddata/eventdata/zone_event/041_R42.json`, `scr_seq_0252_R42.s`.

---

## Skip Mahogany Rocket arc — post-clear town on load

**Goal:** Mahogany Town behaves as if the Rocket Hideout was cleared — gym accessible, rocket grunts gone, shady RageCandyBar salesman gone, Route 43 gate normal — without running the hideout event chain. **Red Gyarados at Lake of Rage must remain** (do not set flags 483, 362, 201, or 202).

### Wiring (pret decomp)

| What | ID / symbol |
|------|-------------|
| Map header | `MAP_T28` = **87** |
| scr_seq member | **930** — patched via `tools/patch_scr_seq_t28_rocket.py` |
| scr_seq init header | **703** — OnLoad → scriptId **6** (slot **5**) |
| zone_event member | **084** |
| Scene var | `VAR_SCENE_ROCKET_TAKEOVER` (`0x4077`) → **5** (post-clear) |

Vanilla OnLoad (`scr_seq_T28_005`) **starts** the takeover (`VAR_SCENE_ROCKET_TAKEOVER = 2`, sets rocket flags). **`tools/patch_scr_seq_t28_rocket.py`** replaces the first bytes at OnLoad entry (**38**) with `call` → appended patch blob (preserves overlapping script layout — **do not** rebuild the offset table).

**Flags set:** hide rocket town NPCs (439–444), shady salesman (498), Lance in shop (504), Route 43 gate rockets (506); restore normal shopkeeper (`clearflag` 487), gate guard (`clearflag` 507); hide hideout interior NPCs if entered. **`clearflag FLAG_ROCKET_TAKEOVER_ACTIVE`** (2459), **`clearflag FLAG_UNK_0C5`** (197), **`setflag FLAG_BEAT_RADIO_TOWER_ROCKETS`** (198), **`setflag FLAG_ROCKET_HIDEOUT_CLEARED`** (202, Route 43 toll).

**Gym blocker:** hide flag **439** on obj1. **East exit:** remove middleman obj0 `(540,175)` from zone_event **084** *and* matrix duplicate **043** (script 65535 — visible from Route 44); remove exit coord script 2; remove bigman obj2 `(523,184)`. **Route 44:** remove all three junction NPCs from **046** (incl. sprite 325 blocker) plus matrix duplicates in **090**. OnLoad sets `VAR_UNK_407A=1`, flags **505/517**, `hide_person 0/2`.

**Build note:** `tools/extract_scr_seq_vanilla.py` seeds `build/a012` from `rom.nds` every scr_seq rebuild. Do not extract scr_seq from `base/root` after a bad build — member files can get shuffled/corrupted.

**Flags left alone (Gyarados):** `FLAG_HIDE_LAKE_OF_RAGE_RED_GYARADOS` (483), `FLAG_CAUGHT_RED_GYARADOS` (362), `FLAG_GOT_RED_SCALE` (201). Flag **202** is hideout-cleared (pret name), not Gyarados hide.

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_t28_005_patch.s` | OnLoad replacement bytecode |
| `tools/patch_scr_seq_t28_rocket.py` | Append patch; `call` from OnLoad entry **38** (keep slot 0 @ **101**) |
| `tools/patch_zone_event_t28_rocket.py` | zone_event **084** (town) + **043** (outdoor matrix) |
| `tools/patch_zone_event_r44_rocket.py` | zone_event **046** (Route 44) + **090** (outdoor matrix) |
| `narcs.mk` | Hook after scr_seq / zone_event extract |

**Test checklist:** load Mahogany (new + existing save) → no rocket grunts, gym enterable, shop normal, Route 44 reachable, Lake of Rage red Gyarados still present.

---

## Removing / skipping story NPCs (reusable recipe)

**Use when:** a roadblock NPC should be gone from the start (or after a scripted state) — gym blockers, arc skip, etc. Same toolchain as badge gates + ferries, but usually **delete objects** and/or **set hide flags** instead of adding new ones.

**Status:** Mahogany rocket-skip **verified in-game** (Aug 2026). Expect the same multi-layer trap on other Johto outdoor blockers.

### Two layers of “remove this guy”

| Layer | What it does | Mahogany rocket example |
|-------|----------------|-------------------------|
| **scr_seq OnLoad** | Force post-event vars/flags; `hide_person N` for map-local ids | `scr_seq_t28_005_patch.s` via member **930** |
| **zone_event objects** | Static overworld spawns — **must patch every copy** | See table below |

**scr_seq alone is not enough** if the NPC still appears: vanilla often duplicates the same `(x, z)` object across **outdoor matrix** zone_event members. Removing only the “town map” member leaves a ghost visible from the connecting route.

### zone_event members to check (Mahogany RageCandyBar)

| Member | Role | Object removed |
|--------|------|----------------|
| **084** | Mahogany Town map | middleman `(540,175)` script **1**, bigman `(523,184)` |
| **043** | Outdoor matrix — Mahogany chunk | middleman `(540,175)` script **65535** ← visible from Route 44 |
| **046** | Route 44 map | sprites **325/328/332** at junction |
| **090** | Outdoor matrix — Route 44 chunk | sprites **328/332** at junction |

**Lesson:** after fixing the “obvious” map member, stand on the **connecting route** and re-check. If still visible, scan vanilla for duplicates.

### Recon workflow (copy for next blocker)

1. **In-game** — note map, world-ish position, sprite look. Confirm blocker is gone functionally but maybe still visible (cosmetic duplicate).
2. **Find map member** — pret JSON / HACK-NOTES / `inspect_zone_event.py build/a032/2_<NNN>`.
3. **Scan all copies in vanilla:**
   ```bash
   # sprite + coords from inspect; search build/a032_vanilla/2_*
   python3 scripts/inspect_zone_event.py build/a032_vanilla/2_<NNN>
   ```
   Grep all members for same `(x,z)` or sprite id near that area (see `tools/patch_zone_event_*` — object match is `(obj_id, script, x, z)`).
4. **Static matrix copies** — script **65535** (`WARP_DOOR`) on an object usually means “display only, no talk” outdoor-layer duplicate.
5. **Patch** — extend or copy `tools/patch_zone_event_<name>.py`:
   - Seed from `extract_zone_event_vanilla.py` (never patch stale `base/root`)
   - `MEMBER_SPECS` dict: member id → list of `(obj_id, script, x, z)` tuples to delete
   - Optional: hide flag on obj instead of delete (gym blocker uses flag **439**)
   - Hook in `narcs.mk` after zone_event extract
6. **State script** (if needed) — OnLoad patch sets scene var + hide flags + `hide_person`. Use **`call` + append** for overlapping scr_seq (T28) or full rebuild when slots are clean (R42 ferry).
7. **Build & test** — `make build/narc/zone_event.narc` for quick iterate, full `make -j1` for `test.nds`. Test from **both** maps (town + connecting route).

### Debug helpers

| Script | Purpose |
|--------|---------|
| `scripts/inspect_zone_event.py build/a032/2_<NNN>` | objects, warps, coords |
| `scripts/inspect_zone_event.py build/a032_vanilla/2_<NNN>` | vanilla baseline before patch |
| `scripts/dump_zone_objects.py` | bulk object dump (adapt path) |
| `scripts/decode_clear_script.py build/a012/2_<NNN> <off> <end>` | OnLoad bytecode |

Vanilla zone_event: `build/a032_vanilla/2_<NNN>` (from `extract_zone_event_vanilla.py`).

### Gotchas

- **One member ≠ one map** — Johto overworld uses extra zone_event members for matrix chunks; same NPC at same world coords can appear in **084 + 043** or **046 + 090**.
- **Delete vs hide flag** — delete for gone-for-good skip; hide flag when vanilla toggles visibility later (gym blocker **439**).
- **coord events** — Mahogany east exit also had a **coord script** blocking walk-through; remove from zone_event coords table, not just the object.
- **Idempotent patchers** — match on `(obj_id, script, x, z)`; raise if vanilla object missing (catches wrong member / already-wrong base).
- **Do not commit `build/`** — patchers re-seed from `rom.nds` each rebuild.

---

## Open-world starting inventory (new saves)

**Toggle:** `OPENWORLD_STARTING_ITEMS` in `include/config.h` (on by default).

**Testing toggle:** `OPENWORLD_TESTING_GRANTS` in `include/config.h` — dev-only extras (currently HM02 from Mom). **Disable before builds for others** ([Index-2](DESIGN.md#index-2-current-technical-baseline)).

**Hook:** Mom downstairs cutscene — scr_seq member **845** (`T20R0201`), script slot **0**.

**Loop fix:** keep vanilla init header **618** (OnFrame `var==0`, like retail). Script **0** sets `VAR_SCENE_PLAYERS_HOUSE_1F = 1` on the first frame before any `wait`, so the cutscene cannot re-trigger. Do **not** move this cutscene to OnTransition — that runs too early and crashes on stairs.

**Grants:** Rebuilt script **0** inserts items/shoes/dex after UI unlock fanfares. `std_give_item_verbose` already waits for A per item — do not add extra `wait_button` between grants; one `closemsg` after **all** item grants (including HM02) clears the window.

| Grant | Item / command |
|-------|----------------|
| S.S. Ticket | `ITEM_SS_TICKET` (456) |
| Pass | `ITEM_PASS` (480) |
| Apricorn Box | `ITEM_APRICORN_BOX` (468) + flag 109 |
| Running shoes | `give_running_shoes` |
| Pokédex | `FLAG_GOT_POKEDEX` + `GivePokedex` |
| Pokégear | `FLAG_GOT_POKEGEAR` + fanfare |
| Town Map card | `UpgradePokegear(1)` only — **do not** use `town_map` / `WorldMapScreen` (cmd 157); it opens the map UI during `lockall` and softlocks on close |
| Phone numbers | `register_gear_number` — Mom (0), Elm (1), Oak (2) |
| HM02 Fly (testing) | `ITEM_HM02` (421) when `OPENWORLD_TESTING_GRANTS` is defined |

**Starting city / starter (v1 prototype — [Vision-3](DESIGN-VISION.md#vision-3-starting-location)):**

**Status: PoC verified in-game (Sep 2026)** — city pick → Mom cutscene → walk out front door → chosen city; re-enter home → exit again. Stairs bedroom ↔ 1F intact.

| Step | When | What |
|------|------|------|
| 1 | Mom cutscene, before starter menu | 3-city `ListLocalText` → `VAR_PLAYER_START_CITY` (**0x4031**) → `_set_home_dynamic_warp` |
| 2 | Same cutscene | Starter **12-option text menu** → `give_mon` (not `choose_starter`) → `FLAG_GOT_STARTER` |
| 3 | Same cutscene | Mom grants (bag, Pokédex, Pass, etc.) — **no post-cutscene teleport** |
| 4 | Walk to front door **(3, 10)** on 1F | Dynamic exit warp → outdoor home door in chosen city |

**Cities (v1):** New Bark (0), Goldenrod (1), Saffron (2).

### Starter selection — **not** `choose_starter`

Open-world intro **does not** use vanilla `choose_starter` (3-ball UI) or `src/starters.c`. Those are a **different, unused path** in this hack.

| | **Open-world path (what we use)** | **Vanilla / legacy path (not used)** |
|---|-----------------------------------|--------------------------------------|
| Where | Mom scr_seq **845** script **0** (`scr_seq_t20_mom_script0.s`) | `choose_starter` script cmd → `CreateStarter_*` hooks |
| UI | 12-row `ListLocalText` text menu | Three Poké Balls on a table |
| Give Pokémon | `give_mon` per menu branch (Johto/Kanto/Gen 3/Gen 4) | Engine creates mon from `starters.c` trio |
| Species count | **12** (hardcoded in script) | **6** in `sStarterChoices[]` (Johto 0–2 + Kanto 3–5 only) |
| `VAR_PLAYER_STARTER` | Menu index **0–11** after pick | Was **0** or **3** (region base for which trio) |
| Dex / phone register | `set_starter_choice` from **party slot 0 species** after `give_mon` | Same cmd, but after ball pick |

**Implications for dev:**

- Adding a starter → edit **`scr_seq_t20_mom_script0.s`** (+ string in **`data/text/545.txt`**). Do **not** expect `starters.c` changes to affect Mom’s menu.
- **`src/starters.c`** + **`hooks`** (`CreateStarter_SetStarterSpecies`, `CreateStarter_CreateMon`) still ship with the engine but are **dead code** unless some other scr_seq calls `choose_starter`. Grep shows **no** open-world scr_seq does — bedroom **846** is vanilla and must stay that way (verify script rejects `choose_starter` there).
- Old design docs ([Vision-3](DESIGN-VISION.md#vision-3-starting-location)) still describe Johto/Kanto YES/NO + 3-ball UI; **implementation superseded** that with the 12-option list.

**Pokémon menu:** `FLAG_GOT_BAG` set during Mom cutscene (not bedroom).

### ID cheat sheet (easy to mix up)

| What | Value | pret / file |
|------|-------|-------------|
| `VAR_PLAYER_START_CITY` | **0x4031** | `armips/include/vars.s` |
| `VAR_PLAYER_STARTER` | **0x4030** | same |
| Map header `MAP_T20R0201` (Mom 1F) | **63** | ≠ scr_seq member |
| Map header `MAP_T20R0202` (bedroom) | **64** | zone_event **061** |
| Map header `MAP_T20` (New Bark outdoor) | **60** | zone_event **057** |
| Map header `MAP_T25` (Goldenrod outdoor) | **76** | zone_event **073** |
| Map header `MAP_T11` (Saffron outdoor) | **59** | zone_event **056** |
| scr_seq Mom house | member **845** | script **0** = cutscene |
| zone_event Mom 1F interior | member **060** | 2 warps — **do not reindex** |
| zone_event bedroom 2F | member **061** | warp down uses **anchor 1** → 1F warp **slot 1** |
| Goldenrod home door | **073** warp **14** at **(376, 335)** | was `T25R0801` (205) |
| Saffron home door | **056** warp **14** at **(1323, 242)** | was `T11R0501` (399) |
| New Bark player house door | **057** warp **1** at **(695, 396)** | vanilla → header 63 |
| Text bank Mom dialogue | **545** | city strings 2–5, starters 6+ |

### Home = bidirectional door + interior swap

Canonical interior stays **`T20R0201`** (scr_seq **845**, Mom). Per-city **outdoor door** warps in; **dynamic warp** handles exit.

| City | Outdoor door (zone_event) | Displaced interior (New Bark door swap) | Dynamic exit (`set_dynamic_warp`) |
|------|---------------------------|----------------------------------------|-----------------------------------|
| New Bark | **057** warp **1** at **(695, 396)** | *(none — vanilla)* | map **60**, warp **1** |
| Goldenrod | **073** warp **14** at **(376, 335)** → hdr **63** | **198** `T25R0801` | map **76**, warp **14** |
| Saffron | **056** warp **14** at **(1323, 242)** → hdr **63** | **356** `T11R0501` (+ 2F) | map **59**, warp **14** |

Goldenrod door confirmed in-game: NE house by Flower Shop / Squirtbottle (**not** Friendship Checker at (373, 362) / `T25R0301`). Saffron: Copycat house warp **14** (**not** warp 7 at 1297,218 / `T11R0801`).

**Verified working pattern (do not simplify):**

1. **Outdoor doors only** — patch **073** / **056** destination header to **63** (`tools/patch_zone_event_start_city.py`).
2. **Interior 060 warp slot 0** — change **(3, 10)** from `hdr=60, anchor=1` to **`hdr=0xFFF (4095), anchor=0x100 (256)`**. Keep warp slot **1** `(3,3)→64` untouched (stairs).
3. **Mom script 0** — after city pick, `set_dynamic_warp` using **`VAR_TEMP_x4000`–`x4004`** (cmd **240** reads all five args via `ScriptGetVar`, not literals).
4. **No post-cutscene `warp`** — player walks to the door.
5. **No coord script at (3, 10)** and **no removing warp slot 0** — both break stairs (black void) or misfire.

**Engine reference (pret `field/field_control.c`):** warp with `anchor == 0x100` and `header == 0xFFF` uses `LocalFieldData.dynamicWarp`. Vanilla examples: zone_event **396–402** (elevator exits).

### Failed approaches (save future dev time)

| Approach | Why it failed |
|----------|----------------|
| Remove interior exit warp + coord at (3,10) | Reindexes warps → bedroom **061** anchor **1** → wrong slot → **black void** on stairs |
| `set_dynamic_warp` with literal map/x args | Args are var IDs; must `setvar VAR_TEMP_*` first |
| `set_dynamic_warp` alone (vanilla exit warp) | Exit still hardwired to New Bark until slot 0 uses 0xFFF/0x100 |
| Post-cutscene `warp` to outdoor door | Wrong UX |
| New Bark door coord script / remove static warp | Cascading wrong warps, black screen |
| `FLAG_OPENWORLD_HOME_EXIT` gate on exit | False premise — Mom does not walk player onto door tile |
| scr_seq exit script + removed warp 0 | Same reindex bug as row 1 |

**Deferred:** New Bark door → displaced interior when start city ≠ New Bark; Copycat/swap-house story scripts.

**Build / verify:**

```bash
make build/narc/scr_seq.narc build/narc/zone_event.narc NOSCAN=1
python scripts/verify_t20_mom_patch.py
python scripts/verify_start_city_patch.py
# repack test.nds
```

**Files:** `armips/scr_seq/scr_seq_t20_mom_script0.s`, `tools/patch_scr_seq_t20_mom.py` (`2_845`), `tools/patch_zone_event_start_city.py` (`073`/`056`/`060`), `tools/patch_scr_seq_start_city.py` (no-op placeholder), `scripts/verify_start_city_patch.py`, `data/text/545.txt`, `armips/include/vars.s`. Init header **618** stays vanilla.

**Bedroom starter:** not used — bedroom scr_seq **846** stays vanilla (**no** `choose_starter`, no OnTransition starter hook). All starter picking is in **Mom script 0** only. Bedroom / OnTransition hooks crashed or never ran reliably when tried.

**Adding a 4th+ city:** recon outdoor door (member, warp index, x/z, old header) → add row to `patch_zone_event_start_city.py` → menu string + `AddListOption` + branch in `_set_home_dynamic_warp` → verify **060** still has exactly 2 warps.

**Next (not started):** Phase 4 story strip (Elm errand, rival, Cherrygrove guide) — [Story-1](DESIGN-STORY.md#story-1-story-and-script-content); or more cities using recipe above.

**Dialogue:** Mom intro greet **545** strings **0–1**. String **6** is post-cutscene talk (vanilla Elm errand line). Cutscene skips bag/card/save/options `npc_msg`s; fanfares + flags unlock touch menu.

**Note:** Test with **new saves** after ROM changes. Story hooks (Elm, rival) still vanilla until Phase 4.

---

## Magnet Train (Goldenrod ↔ Saffron)

**Toggle:** same `OPENWORLD_STARTING_ITEMS` gate as Mom grants.

**Assumption:** Pass (`ITEM_PASS` 480) and S.S. Ticket (`ITEM_SS_TICKET` 456) already in bag from Mom; coord gates keep vanilla `HasItem ITEM_PASS` (passes). No Copycat / power-plant story required.

**Members patched:**

| Member | Map | What changed |
|--------|-----|--------------|
| **893** | `T25R0501` Goldenrod station 1F | OnTransition **006**, OnInit **005**, policeman **000** — `FLAG_RESTORED_POWER` (280) gates → unconditional branch to “power restored” path |
| **834** | `T11R0601` Saffron station 1F | Same for **006** / **005** / **000**, plus NPC **001** (weekday-flavour line gated on power) |

**Ride scripts (895 / 836):** unchanged — no power or ticket checks; only play ride animation after coord gate sets boarding vars.

**Patch style:** in-place bytecode (`checkflag 280` + `goto_if` → `goto`); no `build_scr_seq()` rebuild (table layout is non-sequential).

**Files:** `tools/patch_scr_seq_train.py` (`2_893`, `2_834` in narcs.mk), `scripts/verify_train_patch.py`, `scripts/scan_train_power.py`.

**Verify:** `make scr_seq_clean && make -j24`, then `python scripts/verify_train_patch.py`. In-game: new save → Mom intro → Goldenrod or Saffron station → policeman allows platform → pass coord gate → board train.

**Gotcha:** map header IDs ≠ scr_seq members (`MAP_T25R0501` / `MAP_T11R0601` vs **893** / **834**).

---

## Route 4 ledge boost (Cerulean → Mt Moon)

**Status:** **verified in-game** (Aug 2026). NPC **(1270, 118)** / landing **(1270, 116)** — no coordinate tuning needed.

**Goal:** one-way paid bypass below the Cerulean-side ledge — fisherman boosts you up 2 tiles for **$100** (same flow as Route 42 ferry, single shore).

### Four IDs (easy to mix up)

| What | Route 4 value | pret name |
|------|---------------|-----------|
| **Map header** | `MAP_R04` = **12** | — |
| **zone_event** | member **009** | `009_R04.json` |
| **scr_seq** | member **178** | `scr_seq_0178_R04.s` |
| **Text bank** | **328** | `msg_0328_R04` |

**Not** zone_event 178 (that is a different small map). **Not** scr_seq 009.

No outdoor-matrix duplicate found for Route 4 object coords (unlike Mahogany / Route 44).

### Coordinates (verified)

| Constant | Value | File |
|----------|-------|------|
| NPC tile | **(1270, 118)** facing **south** (sprite **333** hiker) | `tools/patch_zone_event_r04_boost.py` |
| Landing tile | **(1270, 116)** — 2 north of NPC | same + `armips/scr_seq/scr_seq_r04_boost.s` (`LAND_X` / `LAND_Z`) |
| Object id | **4** | zone_event patch |
| scr_seq slot | **1** → scriptId **2** | scr_seq patch |

### Files

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_r04_boost.s` | Paid warp script |
| `tools/patch_scr_seq_r04_boost.py` | Append slot to **2_178** |
| `tools/patch_zone_event_r04_boost.py` | Object on **2_009** |
| `data/text/328.txt` | Trainer tips (0) + boost lines (1–4) |
| `scripts/verify_r04_boost.py` | Post-build check |
| `scripts/find_r04_coords.py` | Recon helper for world `(x,z)` |

**Verify:** `make scr_seq_clean && make -j24`, then `python scripts/verify_r04_boost.py`.

---

## Olivine Secret Medicine (Jasmine)

**Goal:** Heal Ampharos without a Cianwood fetch. Buy Secret Medicine locally, use it at the Lighthouse.

**Mart:** Olivine Poké Mart **second clerk** (`std_special_mart`, `VAR_SPECIAL_x8004 = 10`) → repointed `sOlivineMart` in `src/field/mart.c`. With `MART_EXPANSION`, the first clerk uses badge-tier `ScrCmd_MartBuy` and ignores city extras.

**Price:** `ITEM_SECRET_MEDICINE` buy price **¥500** in `data/itemdata/itemdata.c`. Cianwood pharmacy still gives it free via `giveitem`.

**Lighthouse gate:** Vanilla `scr_seq` member **66** (`D27R0107`) only offers the medicine scene when **`FLAG_GOT_SECRETPOTION`** (185) is set — buying the item alone is not enough. **`Bag_AddItem`** sets that flag when `ITEM_SECRET_MEDICINE` (464) is added (mart purchase or pharmacy).

**IDs:** map header `MAP_D27R0107` = 225; scr_seq member **66**; Olivine mart scr_seq **912** (`T26FS0101`).

**Verify in-game:** Olivine Mart → second clerk → buy Secret Medicine → Lighthouse top → Jasmine uses medicine on Ampharos → Gym.

**Text:** Lighthouse dialogue in `data/text/094.txt` (msg bank **094**, map `D27R0107`). Edits lines 0–1 (local mart hint) and 3 (item name).

