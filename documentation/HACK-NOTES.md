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

## Build workflow on this machine

- Prefer **Docker** (UCRT64 + binutils 2.47 broke ARM linking with the dual linker scripts).
- First time / dirty MSYS leftovers: clear Windows-built `tools/source/**/*.o` before Linux Docker builds.
- Typical rebuild:

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

## Heal after every battle

**Status:** verified (wild, trainer, flee, and catch tested in-game).

**Design:** `DESIGN.md` §17 — full HP/PP/status restore after every battle (wild, trainer, flee; no special exclusions).

| What | Where |
|------|--------|
| Toggle | `HEAL_AFTER_BATTLE` in `include/config.h` (enabled by default; comment out to disable) |
| Hook | existing `Battle_End` overlay hook → `BattleEndRevertFormChange` in `src/battle/battle_pokemon.c` |
| Logic | Nurse Joy–equivalent: max HP, clear status, `RestoreBoxMonPP` on save party + battle-work copies |

**Verified:** wild, trainer, flee, and catch all restore HP/PP/status on return to field.

---

## Full party EXP share (interim)

**Status:** verified in-game.

**Design:** interim stand-in until `DESIGN.md` §16 battle-limit EXP share exists. Every non-fainted party member gets the **full** calculated EXP for each KO (not split). Fainted bench mons still get nothing. No Exp Share item required.

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

**Facing constants (object `dirn`):** 0=south, 1=north, 2=west, 3=east.

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
