# Hack notes: what HG-Engine exposes (and what it doesn’t)

Working notes for this fork so we don’t re-discover the text/data layout every session.

**New agent session?** Read [AGENTS.md](AGENTS.md) (build, git, workflow) before changing game files.

## Contents

Implementation recipes and reference notes (no design-status column — see [DESIGN.md](../DESIGN.md) for `Vision-*` / `World-*` / `Battle-*` specs). **Known bugs:** [DESIGN.md § Index-5](../DESIGN.md#index-5-known-bugs). **Agents:** [AGENTS.md](AGENTS.md).

| Topic | Section |
| ----- | ------- |
| Mom dialogue discovery | [Why the Mom line was hard to find](#why-the-mom-line-was-hard-to-find) |
| Text / msgenc | [How text editing works](#how-text-editing-works) |
| Important msg banks | [Known `data/text` banks](#known-datatext-banks-tracked--important) |
| What to patch first | [Easy wins vs awkward targets](#easy-wins-vs-awkward-targets) |
| Upstream scope | [Scope reminder (upstream)](#scope-reminder-upstream) |
| Badge coord gates | [Badge gate blocks](#badge-gate-blocks-field-scripting) → [Recipe](#recipe-for-a-new-gate), [Route 46 reference](#route-46-gate-reference-implementation) |
| Route 36 Sudowoodo | [Remove Sudowoodo block (Route 36)](#remove-sudowoodo-block-route-36--verified-poc) |
| Route 32 gate | [Remove Route 32 badge gate](#remove-route-32-badge-gate-south-of-violet--verified-pattern) |
| Gym Cut trees | [Remove Surge / Erika Cut trees](#remove-surge--erika-cut-trees--gym-access) |
| Post-battle heal | [Heal after every battle](#heal-after-every-battle) |
| Gym HM grants | [Gym Leader HM rewards (Johto pilot)](#gym-leader-hm-rewards-johto-pilot) → [Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags), [Kanto Fly map](#fly-map--kanto-destinations-not-yet) |
| Interim EXP | [Full party EXP share (interim)](#full-party-exp-share-interim) |
| Trainer scaling | [Trainer level scaling](#trainer-level-scaling) |
| Player level cap | [Player badge level cap & Rare Candies](#player-badge-level-cap--rare-candies-not-enabled-yet) |
| Paid ferries | [Paid ferry / local bypass NPCs](#paid-ferry--local-bypass-npcs-reusable-recipe) → [Route 42](#route-42-reference-verified), [Route 40 / Cianwood](#route-40--cianwood-reference-verified), [Route 31 / Route 45](#route-31--route-45-dark-cave-reference) |
| Mahogany Rocket | [Skip Mahogany Rocket arc](#skip-mahogany-rocket-arc--post-clear-town-on-load) |
| Story NPC removal | [Removing / skipping story NPCs](#removing--skipping-story-npcs-reusable-recipe) |
| Mom intro / start city | [Open-world starting inventory](#open-world-starting-inventory-new-saves) → [Starter menu](#starter-selection--not-choose_starter), [Home warps](#home--bidirectional-door--interior-swap) |
| Story flag sweep (dev) | [Story flag range sweep (dev)](#story-flag-range-sweep-dev) |
| HGSS story flags (pret) | [HGSS-STORY-FLAGS.md](HGSS-STORY-FLAGS.md) — index **100–399**; add Wandering Heart notes as we map skips |
| Magnet Train | [Magnet Train (Goldenrod ↔ Saffron)](#magnet-train-goldenrod--saffron) |
| Route 4 hiker boost | [Route 4 ledge boost](#route-4-ledge-boost-cerulean--mt-moon) |
| Jasmine medicine | [Olivine Secret Medicine (Jasmine)](#olivine-secret-medicine-jasmine) |
| Mart inventories | [Mart expansion (`src/field/mart.c`)](#mart-expansion-srcfieldmartc) |
| Game Corner TMs | [Game Corner TM prizes](#game-corner-tm-prizes) |
| Wild distance caps | [Wild level caps (distance-based)](#wild-level-caps-distance-based--verified-poc) → [Formula](#formula-and-table), [Runtime](#runtime-pipeline), [Synthetic edges](#editing-synthetic-stage-edges) |
| DSPRE / map IDs | [World placement (DSPRE)](#world-placement-dspre) |
| Fishing gurus | [Fishing Rod guru NPCs](#fishing-rod-guru-npcs) |

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

To find indices for another map: pret decomp names (`130_R29R0101.json`, `scr_seq_00226_R29R0101.s`) or `scripts/local/_scan_zone_events.py` on `base/root/a/0/3/2`.

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

Helper files: `tools/zone_event_enc.py`, `data/zone_event/events/event_<MAP>.h`, `scripts/dev/test_zone_event_roundtrip.py`.

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

**Goal:** walk Violet ↔ Goldenrod / Ecruteak with **0 badges**; Sudowoodo never blocks the path. **Tested in-game:** tree gone after re-entering the route, no collision, existing save OK. **Known bug [KB-1](../DESIGN.md#index-5-known-bugs):** Sudowoodo may still appear on the **first** visit until you leave and return.

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
| Hook | `Battle_End` → `BattleEndRevertFormChange` → `HealAfterBattle_HealParty(bw)` in `src/battle/heal_after_battle.c` |
| Heal impl | Battle-work party, then save (`SaveBlock2_get()`), with EWRAM pointer checks |
| Logic | Nurse Joy–equivalent: max HP, clear status, `RestoreBoxMonPP` |

**Verified:** wild, trainer, flee, and catch all restore HP/PP/status on return to field.

**KB-2 (Sep 2026):** intermittent crash when returning to the field after battle — **tentatively fixed**. Heal logic lives in this file; runs only when `sp->fight_end_flag` is set (`BattleStruct` @ `0x311F`), with EWRAM pointer checks on `bw`, `sp`, and party mons. Hook timing unchanged (`Battle_End` → `BattleEndRevertFormChange`). **100+ battle ends without repro** after the refactor; original rate was very low (~once per 70–80+ encounters), so treat as monitoring, not proof. Status: [DESIGN.md § Index-5 *Monitoring*](../DESIGN.md#monitoring-tentatively-resolved).

**Agent notes (do not repeat without new evidence):**

| Attempt | Result |
| -------- | ------ |
| Pending flag + heal on `StoreFieldSysPtr` (ARM9) | No heal — field overlay usually stays loaded during wild battles; hook often never runs after battle. If you hook `StoreFieldSysPtr`, preserve **`r0`** across any `bl` (vanilla needs it). |
| `HealAfterBattle_*` in **ARM9 main** called from battle overlay @ `Battle_End` | **Consistent crash** before fade — battle overlay build uses **`-mno-long-calls`**; do not `bl` main from overlay 12/130 stubs. |
| Save party only at start of `Battle_End` | No heal — vanilla overwrites save party after the hook returns. |
| Heal on `UnloadOverlayByID(OVERLAY_BATTLE)` | No heal — path did not run reliably in testing. |
| Second hook @ overlay `080011A2` (“end of `Battle_End`”) | **Battle-start crash** — site is not battle-end-only. Removing the hook from `hooks` **does not** revert bytes in `base/overlay/overlay_0012.bin`. |

**If KB-2 or heal regressions return:** bisect with `HEAL_AFTER_BATTLE` off in `config.h`. For **battle-start** crash after overlay experiments, re-extract overlay 12 from `rom.nds` (preferred) or restore 10 vanilla bytes @ `080011A2` through `080011AB` (`Hook(..., reg 0)` = 6-byte stub + 4-byte pointer; full span `10 BD 70 47 00 00 F8 B5 92 B0`). Helper: `python scripts/local/check_overlay12_hook.py`. For **end-of-battle** crash only, the next real fix is a **verified** hook after vanilla party sync (decomp/xref) — not another guessed offset.

**Commit shape (Sep 2026):** `include/heal_after_battle.h`, `src/battle/heal_after_battle.c`, call from `BattleEndRevertFormChange` in `battle_pokemon.c`. No `bytereplacement` for overlay 12 unless you intentionally want a team-wide band-aid for stale local overlays.

---

## Gym Leader HM rewards (Johto pilot)

**Status:** **Morty** verified in-game Sep 2026. **Falkner** leader HM + elevator mostly working but not polished (see follow-ups). **Pryce** / **Jasmine** build + bytecode verify only — need in-game pass. **Whitney** and remaining Johto leaders not started.

**Design:** [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters) — after badge fanfare, grant field ability by **`count_badges`** (any-order Gyms), then TM. **Flash / Headbutt not implemented yet** (badge rows 1 and 4 grant badge + TM only). Headbutt battle teach needs a **custom TM** (not in vanilla); see [World-3 § Headbutt & Flash](DESIGN-WORLD.md#headbutt--flash--battle-teaching-vanilla-vs-target).

| What | Where |
|------|--------|
| Toggle | `GYM_BADGE_COUNT_FIELD_REWARDS` in `include/config.h` |
| Field HM use | `OPENWORLD_FIELD_MOVES_NO_BADGE_GATE` — [Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags) (verified Sep 2026) |
| Shared logic | `armips/include/gym_badge_hm_reward.inc` — level cap (`10 + 4×badges`, 80 at 16) + HM table |
| Shared text | `data/text/854.txt` — level cap, HM names, TM intro |
| Falkner | scr_seq **859** — slots **1–5** patched; zone_event **365** sprout gate obj removed (`tools/patch_zone_event_violet_gym.py`) |
| Morty | member **922**, slot **1** — `scr_seq_morty_gym_slot1.s`, `data/text/614.txt` |
| Pryce | member **932**, slot **1** — `scr_seq_pryce_gym_slot1.s`, `data/text/622.txt` |
| Jasmine | member **913**, slot **0** — `scr_seq_jasmine_gym_slot0.s`, `data/text/606.txt` |
| Patch tools | `tools/patch_scr_seq_gym_{falkner,morty,pryce,jasmine}.py` — Falkner uses shared `patch_script_slot()` from falkner module |
| Verify | `scripts/build/verify_falkner_gym_hm_patch.py build/a012/2_859 build/a012/2_922 build/a012/2_932 build/a012/2_913` |
| Recon | `scripts/dev/inspect_gym_slots.py` (after `build/a012_vanilla` exists) — leader trainer id per slot |

**Text bank indexing:** `msgenc` treats every line as a message index, including blank lines. Vanilla dumps of `558.txt` / `614.txt` have a blank line between each string — leader scripts must use indices **0, 2, 4, 6, 8** for pre / post / badge / TM / already-beaten. **`622.txt` compacted (0–4).** `606.txt` keeps two placeholder lines at 3–4 so TM = 5 and already-beaten = 6 (Steelix trade strings stay at 7+). **Before editing any gym text bank, list indices** (`msgenc` line = index) — wrong indices cause blank lines or wrong dialogue (Pryce TM-after-blank, Morty post-battle blank, Falkner elevator TM preamble).

**HM rows (badges earned → reward):** 2 Cut, 3 Rock Smash, 5 Fly, 6 Surf, 7 Strength, 10 Whirlpool, 13 Waterfall, 16 Rock Climb. All other counts: badge + TM only.

**Flow:** win dialogue → `GiveBadge` → receipt → `SEQ_ME_BADGE` → shared level-cap line → **`count_badges`** → HM line (if row) + `SEQ_ME_WAZA` + silent `giveitem` → shared TM intro + fanfare + TM + Leader flavor text.

**Test:** beat a Gym as **2nd** badge → Cut; as **5th** → Fly; badge **1** or **4** → no HM, TM only.

### Field HM use without per-Gym badge flags

**Status: verified in-game Sep 2026** — Mom HM02 + party Fly without Storm Badge; Goldenrod dept mart shelves still badge-gated.

**Toggle:** `OPENWORLD_FIELD_MOVES_NO_BADGE_GATE` in `include/config.h` (on by default with open-world HM work). Required for [OPENWORLD_TESTING_GRANTS](#open-world-starting-inventory-new-saves) HM02 to work from the party menu — granting the item alone is not enough; vanilla `FieldMove_CheckFly` still demands Storm Badge without this hook.

Vanilla `FieldMove_Check*` (arm9 ~`0x02067F00`) calls `PlayerProfile_TestBadgeFlag` for a **specific** Gym badge before returning `FIELD_MOVE_RESPONSE_NEED_BADGE` (2). That is independent of gym HM grants and of `FLAG_GOT_HM*`.

| What | Where |
|------|--------|
| Hook | `src/field_move_badge.c` → `PlayerProfile_TestBadgeFlag_hook` @ arm9 `0x02028F98` |
| Bypass | When caller LR is in `0x02067F87`–`0x0206888B` (field-move checks only), return TRUE |
| Preserved | Mart badge shelves (`ScrCmd_MartBuy`, LR in field overlay ~`0x023Cxxxx`), TM teach helpers, script/map gates |

**Vanilla per-move badge checks** (pret `field_move.c`; rebases: re-scan arm9 for `bl #0x02028F98` from `FieldMove_Check*`):

| Field move | Vanilla badge | `BADGE_*` index |
|------------|---------------|-----------------|
| Rock Smash | Zephyr | 0 |
| Cut | Hive | 1 |
| Strength | Plain | 2 |
| Surf | Fog | 3 |
| Fly | Storm | 4 |
| Whirlpool | Glacier | 6 |
| Waterfall | Rising | 7 |
| Rock Climb | Earth | 15 |

Flash and Headbutt have **no** `TestBadgeFlag` call in vanilla field-move checks — their gates are script/map-side ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

**Test:** new save with `OPENWORLD_TESTING_GRANTS` → Mom HM02 → teach Fly → party menu Fly without Storm Badge; Goldenrod dept mart still gates shelves by badge count; Gym-granted HM (e.g. Cut as 2nd badge) usable without owning that Leader’s vanilla badge flag.

**Out of scope (for now):** `FLAG_GOT_HM02`, Flash dungeon scripts, Surf map tiles, collection-based field HMs ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

### Fly map — Kanto destinations (not yet)

**Status: not implemented** — confirmed in-game Sep 2026.

Party-menu Fly works in Johto after the [badge bypass](#field-hm-use-without-per-gym-badge-flags) above. When the player is **physically in Kanto** (e.g. Magnet Train to Saffron), the Fly destination UI still lists **Johto cities only** — no Kanto fly points. Vanilla HGSS likely gates the Kanto Fly map on story progress (**Elite Four clear** and/or **SS Aqua Kanto arrival**); neither applies in the open-world shell yet.

**Target ([World-1](DESIGN-WORLD.md#world-1-world-transportation), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)):** once HM Fly is unlocked, Fly to **visited cities in both regions** without E4 or SS Aqua story prerequisites.

**ROM work (TBD):** find Fly map / flypoint table init (pret `field_move*.c`, flypoint data) and decouple Kanto destination visibility from `gameClear` / SS Aqua flags — or set the minimum story flags on new saves if a lighter hack suffices.

### Falkner follow-ups (859 / zone_event 365)

Vanilla Violet Gym uses **six scr_seq slots**, not just the leader. Only patch slots you understand — other objects still reference them.

| Slot | Role | Patch status |
|------|------|----------------|
| 0 | `violet_gym_init` OnLoad | **vanilla** — sets elevator NPC visibility from flags |
| 1 | Falkner leader + HM table | **patched** |
| 2 | Trainer hint NPC (script 2 on obj 3) | **patched** — no blank msg before badge |
| 3 | Sprout gate talk (was obj 1 script 3) | **patched** — gate obj **removed** from zone_event |
| 4 | Was empty; obj 2 script 4 | **stub** (`releaseall` / `end`) |
| 5 | Elevator attendant (engine scripts 10201/10202 on objs 4–5) | **patched** — `violet_gym_elevator` only (vanilla opened with TM/Roost msg **6**) |

**Known rough edges:** elevator attendant **sprites** may still appear (objs 4–5, hide flags 679/680); slot **0** OnLoad untouched; full open-world “no Sprout Tower” path not re-tested on every save state. Falkner recon scripts live in **`scripts/local/`** (`decode_falkner_gym.py`, `disasm_scr_seq.py`, `scan_violet_gym.py`).

**Zone_event 365 (after patch):** 5 objects — Falkner obj0 script 1, trainer obj3 script 2, elevator objs script 10201/10202; **no** obj1 sprout blocker.

### Next leaders

| Leader | scr_seq | Leader slot | Notes |
|--------|---------|-------------|--------|
| **Whitney** | **886** | **0** (+ slots 1, 4) | **Hard** — sore-loser state machine (first win = cry, no badge; chase in slot 1; badge on second talk). Inject `.include` only on the badge-grant path; do not replace whole script. |
| Bugsy | TBD | TBD | Run `inspect_gym_slots.py` after vanilla extract |
| Chuck | TBD | TBD | |
| Clair | TBD | TBD | |
| Janine | TBD | TBD | Kanto |

**Template for “easy” leaders (Falkner / Morty / Pryce / Jasmine pattern):** one leader slot, copy script skeleton, set badge + TM constants, fix **text indices** (blank-line banks vs compact), wire `narcs.mk` + patch py + verify member.

---

## Full party EXP share (interim)

**Status:** verified in-game.

**Design:** interim stand-in until [Battle-6](DESIGN-BATTLES.md#battle-6-exp-share) battle-limit EXP share exists. Every non-fainted party member gets the **full** calculated EXP for each KO (not split). Fainted bench mons still get nothing. No Exp Share item required.

| What | Where |
|------|--------|
| Toggle | `FULL_PARTY_EXP_SHARE` in `include/config.h` (enabled by default) |
| Hook | `Task_DistributeExp_Extend` in `src/battle/battle_script_commands.c` |

**Verified:** bench mons gain EXP (and level) from wild/trainer KOs while only one mon is out in battle.

---

## Trainer level scaling

**Status:** level band, moves, and stage adjust verified in-game; Gym Leader cap enabled — Gym trainer band + type filter still open ([Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented), [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).

**Design:** [Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps) — badge count → cap `10 + 4×badges` (max **80** at 16 badges). Ordinary trainers: uniform random level in **`[cap−4, cap]`**. Gym Leaders: **every slot at cap exactly**. Trainers never exceed **80** (Champion uncap does not apply to NPCs). Special-trainer overrides deferred. Generated parties / dynamic battles: [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties), [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc).

| Feature | Toggle | Where |
|---------|--------|--------|
| Rescale levels | `TRAINER_LEVEL_SCALING` | `MakeTrainerPokemonParty()` in `src/field/enemy_party.c` — `CountPlayerBadges()`, `PickTrainerLevelInBand()` |
| Level-up moves | `TRAINER_LEVEL_APPROPRIATE_MOVES` | Same — skips NARC move sets when set; `InitBoxMonMoveset()` after `ChangeToBattleForm` |
| Stage adjust | `TRAINER_SPECIES_STAGE_ADJUST` | Same — `AdjustEncounterSpeciesForLevel()` in `include/encounter_species_stage.h` (requires level scaling). Tables: `gen_level_up_evo_tables.py` + `gen_synthetic_evo_edges.py`; `patch_level_up_evo_addrs.py` patches overlay 129 (shared with [wild stage adjust](#runtime-pipeline)) |
| Gym Leader cap | `TRAINER_GYM_LEADER_CAP_LEVEL` | Same — `IsGymLeaderTrainerClass()` for all 16 Johto/Kanto Leaders; requires level scaling |

**Dependencies:** moves and stage adjust require `TRAINER_LEVEL_SCALING`; Gym Leader cap requires level scaling.

---

## Player badge level cap & Rare Candies (not enabled yet)

**Design:** [Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps) — EXP stops at badge cap; **Rare Candies may exceed the cap** when both hooks are enabled.

| Toggle | Role |
|--------|------|
| `IMPLEMENT_LEVEL_CAP` | hg-engine level cap from `LEVEL_CAP_VARIABLE` (off in this fork by default) |
| `UNCAP_CANDIES_FROM_LEVEL_CAP` | Rare Candies ignore the cap (use with `IMPLEMENT_LEVEL_CAP`) |
| `ALLOW_LEVEL_CAP_EVOLVE` | Optional — evolve at cap via candy when evolution level matches |

All three are commented out in `include/config.h`. Trainer scaling (`TRAINER_LEVEL_SCALING`) is independent and **on** by default. Verify hg-engine cap behaviour matches design before enabling `IMPLEMENT_LEVEL_CAP`.

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

Find indices via pret names (`041_R42.json`, `scr_seq_0252_R42.s`) or `scripts/local/_scan_zone_events.py`.

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
   - **Warp facing:** the fifth `warp` argument sets **player facing after landing** (`DIR_NORTH=0`, `DIR_SOUTH=1`, `DIR_WEST=2`, `DIR_EAST=3`). Object `facingDirection` in zone_event only affects the NPC sprite until `faceplayer` runs.
   - **Landing tile:** must be **walkable land** — do not warp onto water or a static Lapras object tile (player can soft-lock). Place landing beside the shore NPC; test both directions in-game.
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
| `data/text/399.txt` | Ferry lines **10–13** |
| `data/zone_event/events/event_R42.h` | Ferry slot + object id defs |

**Fee:** $200. **Sprite:** fishing NPC (`347`).

### Route 40 / Cianwood reference (verified)

**Goal:** cross Route 40 ↔ Cianwood without Surf — one fisherman per shore, full crossing per trip. Route 40 Surf gate middleman removed (`tools/patch_zone_event_w40_surf_gate.py`).

| Shore | Map header | zone_event | scr_seq | Text bank | Ferry NPC | Lapras (static `1023`) | Landing after warp | Post-warp facing |
|-------|------------|------------|---------|-----------|-----------|------------------------|--------------------|------------------|
| Route 40 (Olivine side) | `MAP_W40` **94** | **091** | **962** slot **10** (scriptId **11**) | **744** msgs **13–16** | obj **7** `(248, 277)` | obj **8** `(248, 278)` | Cianwood `(190, 360)` | `DIR_WEST` (face left / toward town) |
| Cianwood (east shore) | `MAP_T24` **75** | **072** | **875** slot **16** (scriptId **17**) | **572** msgs **22–25** | obj **12** `(191, 360)` | obj **13** `(192, 360)` | Route 40 `(249, 277)` | `DIR_NORTH` |

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_w40_ferry_cianwood.s` | Route 40 → Cianwood warp |
| `armips/scr_seq/scr_seq_t24_ferry_route40.s` | Cianwood → Route 40 warp |
| `tools/patch_scr_seq_w40_ferry.py` / `tools/patch_scr_seq_t24_ferry.py` | Append ferry scripts to members **962** / **875** |
| `tools/patch_zone_event_w40_ferry.py` / `tools/patch_zone_event_t24_ferry.py` | Shore NPCs + Lapras |
| `data/text/744.txt` / `data/text/572.txt` | Offer / accept / decline / no-money lines (destination + **$200** in offer; no Lapras mention in dialogue) |

**Fee:** $200. **Sprite:** fishing NPC (`347`).

**Gotcha:** Cianwood text indices are **22–25** (0-based line numbers in `572.txt` after appended ferry lines) — off-by-one here showed “All aboard!” as the offer instead of the fare prompt.

### Route 31 / Route 45 Dark Cave reference

**Goal:** bypass Dark Cave on foot between Violet-side Route 31 and Blackthorn-side Route 45 — one hiker per outdoor cave mouth, full crossing per trip.

| Shore | Map header | zone_event | scr_seq | Text bank | Hiker NPC | Landing after warp | Post-warp facing |
|-------|------------|------------|---------|-----------|-----------|--------------------|------------------|
| Route 31 (Violet side) | `MAP_R31` **35** | **032** | **230** slot **6** (scriptId **7**) | **378** msgs **16–19** | obj **9** `(566, 270)` + Quagsire **10** `(567, 270)` | Route 45 `(650, 199)` | `DIR_SOUTH` |
| Route 45 (Blackthorn side) | `MAP_R45` **47** | **044** | **258** slot **5** (scriptId **6**) | **405** msgs **3–6** | obj **15** `(649, 199)` + Quagsire **16** `(648, 199)` | Route 31 `(565, 270)` | `DIR_SOUTH` |

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_r31_ferry_r45.s` | Route 31 → Route 45 warp |
| `armips/scr_seq/scr_seq_r45_ferry_r31.s` | Route 45 → Route 31 warp |
| `tools/patch_scr_seq_r31_ferry.py` / `tools/patch_scr_seq_r45_ferry.py` | Append ferry scripts to members **230** / **258** |
| `tools/patch_zone_event_r31_ferry.py` / `tools/patch_zone_event_r45_ferry.py` | Shore hiker NPCs |
| `data/text/378.txt` / `data/text/405.txt` | Offer / accept / decline / no-money lines |

**Fee:** $200. **Sprite:** hiker `SPRITE_MOUNT_2` (**333**).

**Companion Pokémon:** use static NPC prop tags (**994–1050**), not follower sprite IDs. Lapras **1023** and Quagsire **1050** reuse species overworld gfx from `pokemonow.narc` with `OVERWORLD_SIZE_SMALL` in `overworld_table.c`. Follower tag **626** (Quagsire) **crashes map load** as a zone_event object.

**Gotcha:** Route 31 msg indices are **16–19** in `378.txt` (append after vanilla line 17 / index 16).

### Route 46 → Route 45 (one-way mountain lift) reference

**Goal:** one-way paid bypass from lower Route 46 up to north Route 45 near Blackthorn — hiker + Rhydon at the south end of Route 46 only.

| Shore | Map header | zone_event | scr_seq | Text bank | Hiker NPC | Landing after warp | Post-warp facing |
|-------|------------|------------|---------|-----------|-----------|--------------------|------------------|
| Route 46 (departure) | `MAP_R46` **48** | **045** | **259** slot **3** (scriptId **4**) | **406** msgs **4–7** | obj **7** `(627, 366)` + Rhydon **8** `(626, 366)` | Route 45 `(663, 199)` | `DIR_NORTH` |

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_r46_ferry_r45.s` | Route 46 → Route 45 warp |
| `tools/patch_scr_seq_r46_ferry.py` | Append ferry script to member **259** |
| `tools/patch_zone_event_r46_ferry.py` | Shore hiker + Rhydon NPCs |
| `data/text/406.txt` | Offer / accept / decline / no-money lines |

**Fee:** $200. **Sprites:** hiker **333** (`SPRITE_MOUNT_2`); Rhydon **1020** (vanilla static slot in `overworld_table.c`).

### Blackthorn / Route 44 (Ice Path bypass) reference

**Goal:** paid outdoor warp between Blackthorn City and Route 44 — bypasses walking through Ice Path without editing any Ice Path maps.

| Shore | Map header | zone_event | scr_seq | Text bank | Hiker NPC | Landing after warp | Post-warp facing |
|-------|------------|------------|---------|-----------|-----------|--------------------|------------------|
| Blackthorn City | `MAP_T30` **89** | **086** | **941** slot **17** (scriptId **18**) | **629** msgs **15–18** | obj **10** `(692, 166)` + Piloswine **11** `(693, 166)` | Route 44 `(626, 171)` | `DIR_SOUTH` |
| Route 44 (bridge) | `MAP_R44` **46** | **043** | **257** slot **4** (scriptId **5**) | **404** msgs **7–10** | obj **16** `(627, 170)` + Piloswine **17** `(626, 170)` | Blackthorn `(691, 166)` | `DIR_SOUTH` |

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_t30_ferry_r44.s` | Blackthorn → Route 44 warp |
| `armips/scr_seq/scr_seq_r44_ferry_t30.s` | Route 44 → Blackthorn warp |
| `tools/patch_scr_seq_t30_ferry.py` / `tools/patch_scr_seq_r44_rod_guru.py` | Append ferry to **941** / rebuild **257** (rod guru + ferry) |
| `tools/patch_zone_event_t30_ferry.py` / `tools/patch_zone_event_r44_ferry.py` | Shore hiker + Piloswine NPCs |
| `data/text/629.txt` / `data/text/404.txt` | Offer / accept / decline / no-money lines |

**Fee:** $200. **Sprites:** hiker **333**; Piloswine **1051** (registered in `overworld_table.c` like Quagsire **1050**).

**ID gotchas:** map header **89** ≠ zone_event **086** (Olivine-class). Walkable Route 44 is zone_event **043**, not pret **`046_R44`** (Ice Path junction chunk). Rod guru stays obj **15** on **043**; ferry uses **16–17**.

### Kanto coastal ferry mesh reference

**Goal:** four paid water-route stops linked by a **3-choice destination menu** (`ListLocalText` / `AddListOption` / `ShowList`, same UI as Mom’s starter/city pick). Flow: offer → yes/no → $200 → “Where to?” → warp. **Not** a simple pairwise yes/no ferry.

| Stop | Map header | zone_event | scr_seq | msg bank | Fisherman + Lapras | scriptId |
|------|------------|------------|---------|----------|-------------------|----------|
| Pallet Town south shore | `MAP_T01` **49** | **046** | **735** slot **8** | **446** msgs **6–13** | obj **3–4** `(1036, 375)` / `(1036, 376)` | **9** |
| Cinnabar Island beach | `MAP_CINNABAR_ISLAND` **57** | **054** | **815** slot **5** | **519** msgs **22–30** | obj **3–4** `(1030, 503)` / `(1030, 504)` | **6** |
| Seafoam cave mouth | `MAP_W20` **92** | **089** | **960** slot **2** | **742** msgs **2–9** | obj **12–13** `(1125, 504)` / `(1124, 504)` | **3** |
| Route 19 (Fuchsia) | `MAP_W19` **91** | **088** | **958** slot **6** | **740** msgs **6–13** | obj **18–19** `(1203, 469)` / `(1203, 470)` | **7** |

**Landing tiles** (shared constants in `armips/scr_seq/kanto_waters_landings.s`):

| Destination | Warp map | Landing `(x, z)` | Facing |
|-------------|----------|------------------|--------|
| Pallet Town | `MAP_T01` **49** | `(1037, 375)` | north |
| Cinnabar Island | `MAP_T09` **57** | `(1031, 503)` | south |
| Seafoam cave mouth | `MAP_W20` **92** | `(1126, 504)` | north |
| Route 19 (Fuchsia) | `MAP_W19` **91** | `(1204, 469)` | north |

| File | Role |
|------|------|
| `armips/scr_seq/kanto_waters_landings.s` | Shared warp targets, fee, map constants |
| `armips/scr_seq/scr_seq_t01_kanto_ferry_pallet.s` | Pallet script (→ Cinnabar / Seafoam / Fuchsia) |
| `armips/scr_seq/scr_seq_t09_kanto_ferry_cinnabar.s` | Cinnabar script (→ Pallet / Seafoam / Fuchsia) |
| `armips/scr_seq/scr_seq_w19_kanto_ferry.s` | Route 19 script (→ Pallet / Cinnabar / Seafoam) |
| `armips/scr_seq/scr_seq_w20_kanto_ferry.s` | Route 20 script (→ Pallet / Cinnabar / Fuchsia) |
| `tools/patch_scr_seq_kanto_waters_ferry.py` | Append scripts to members **735**, **815**, **958**, **960** (+ legacy **961**) |
| `tools/patch_zone_event_kanto_waters_ferry.py` | Shore fishermen + Lapras on **046**, **054**, **088**, **089** |
| `data/text/446.txt` / `519.txt` / `740.txt` / `742.txt` | Ferry dialogue + destination labels |

**Fee:** $200. **Sprites:** fisherman **347**; Lapras static OW **1023** (registered in `overworld_table.c`).

**Menu labels:** Pallet Town, Cinnabar Island, Seafoam Island, Fuchsia City (no “Near …” prefix).

**Gotchas:**

- **Map header ID ≠ scr_seq / msg index** — Cinnabar uses zone_event **054** but scr_seq **815** and msg **519** (pret `map_headers.h` row for `MAP_CINNABAR_ISLAND`). Do **not** patch scr_seq member **054** or msg **741** for the beach fisherman.
- **Blaine shares zone_event 054** — vanilla Blaine (obj **1**, spr **374**) uses scriptId **5** (scr_seq **815** slot **4**, msg **519** line **10**). Ferry fisherman must use scriptId **6** (appended slot **5**). Wrong scriptId shows Blaine post-gym dialogue.
- **Pallet visible shore** — matrix water chunk **090** / scr_seq **961** is **not** used; ferry NPC lives on land member **046** so the fisherman is visible from town.
- **Route 21 water NPCs removed** — zone_event **090** no longer hosts ferry objects; scr_seq **961** append is harmless dead code unless a water-side NPC returns.
- **Seafoam stop** on walkable **089** near east cave warp `(1127, 501)`.
- **Text bank indexing:** `msgenc` treats every line as an index — split merged strings (Route 19 “All aboard!\nWhere to?” bug) before wiring `npc_msg` indices.

**Route 19 access (Mom intro):** `FLAG_UNLOCKED_WEST_KANTO` alone only affects Route 22 gate dialogue; clearing Fuchsia’s south shore also sets Blaine-equivalent flags in Mom intro: `FLAG_UNK_265`, `FLAG_HIDE_ROUTE_19_WORKMEN_*`, and `FLAG_MAPTEMP_010`–`014` (hide STOP signs, workmen, and rock-smash boulders).

### Debug helpers (keep using these)

| Script | Purpose |
|--------|---------|
| `scripts/dev/inspect_zone_event.py build/a032/2_<NNN>` | bg events, objects, coords |
| `scripts/dev/inspect_scr_seq.py build/a012/2_<NNN>` | script slot offsets |
| `scripts/dev/dump_scr_seq_slots.py build/a012/2_<NNN>` | slot sizes + bytecode heads |
| `scripts/dev/verify_scr_seq_patch.py build/a012_vanilla/2_<NNN> build/a012/2_<NNN>` | confirm vanilla slots unchanged |
| `scripts/dev/scan_scr_seq_msgs.py build/a012/2_<NNN>` | list `npc_msg` indices per script slot |
| `scripts/dev/extract_msg_banks.py <bank>…` | decode vanilla msg banks from ROM into `data/text/<bank>.txt` |
| `scripts/dev/decode_r42_objects.py` | quick object field dump (adapt member path) |

Vanilla scr_seq for recovery: `build/a012_vanilla/2_<NNN>` (extracted from `rom.nds` on first patch run).

### Gotchas

- **scr_seq append corruption:** inserting into the offset table shifts script bodies without updating old pointers → signs and story scripts break silently. `patch_scr_seq_r42_ferry.py` must **extract vanilla bodies and rebuild the table** (`build_scr_seq()` in `tools/patch_scr_seq_r42_ferry.py` / `tools/append_scr_seq_script.py`).
- **Healthy scr_seq size:** Route 42 member ~**1188 bytes** (8 scripts). Multi‑MB member = corrupt; patcher resets from vanilla when `count != VANILLA_SCRIPT_COUNT` or size > 8 KB.
- **Duplicate NPCs on rebuild:** zone_event patcher must delete prior ferry objects by id before re-adding.
- **Sign overlap:** bg-event signs and object NPCs on the same tile fight for interaction; offset NPC one tile from sign.
- **land_data ≠ ferry:** walking on water still needs terrain edits; ferries only skip the gap via warp. Failed bridge exports live in `rawdata/changed_maps/route_42/failed attempt at bridge/`; apply manually via `scripts/dev/apply_changed_maps.py` (not in Makefile). Matrix loads land_data member **44** for Route 42 chunks — DSPRE export indices 082–084 ≠ runtime member.

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
   python3 scripts/dev/inspect_zone_event.py build/a032_vanilla/2_<NNN>
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
| `scripts/dev/inspect_zone_event.py build/a032/2_<NNN>` | objects, warps, coords |
| `scripts/dev/inspect_zone_event.py build/a032_vanilla/2_<NNN>` | vanilla baseline before patch |
| `scripts/dev/dump_zone_objects.py` | bulk object dump (adapt path) |
| `scripts/dev/decode_clear_script.py build/a012/2_<NNN> <off> <end>` | OnLoad bytecode |

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

**Testing toggle:** `OPENWORLD_TESTING_GRANTS` in `include/config.h` — dev-only extras (currently HM02 from Mom). Party-menu Fly needs **`OPENWORLD_FIELD_MOVES_NO_BADGE_GATE`** ([Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags)). Optional commented **`OPENWORLD_STORY_FLAG_SWEEP`** for flag-range bisect ([Story flag range sweep](#story-flag-range-sweep-dev)). **Disable before builds for others** ([Index-2](DESIGN.md#index-2-current-technical-baseline)).

**Hook:** Mom downstairs cutscene — scr_seq member **845** (`T20R0201`), script slot **0**.

**Loop fix:** keep vanilla init header **618** (OnFrame `var==0`, like retail). Script **0** sets `VAR_SCENE_PLAYERS_HOUSE_1F = 1` on the first frame before any `wait`, so the cutscene cannot re-trigger. Do **not** move this cutscene to OnTransition — that runs too early and crashes on stairs.

**Grants:** Rebuilt script **0** inserts items/shoes/dex after UI unlock fanfares. `std_give_item_verbose` already waits for A per item — do not add extra `wait_button` between grants; one `closemsg` after **all** item grants (including HM02) clears the window.

| Grant | Item / command |
|-------|----------------|
| S.S. Ticket | `ITEM_SS_TICKET` (456) |
| Pass | `ITEM_PASS` (480) |
| Apricorn Box | `ITEM_APRICORN_BOX` (468) + flag 109 |
| Poké Balls | `ITEM_POKE_BALL` (4) ×5; marts need **`FLAG_UNK_09A` (154)** — `setflag` with Pokégear ([Mart Poké Ball](#mart-poké-ball)) |
| Running shoes | `give_running_shoes` |
| Pokédex | `FLAG_GOT_POKEDEX` + `GivePokedex` |
| Pokégear | `FLAG_GOT_POKEGEAR` + fanfare |
| Town Map card | `UpgradePokegear(1)` only — **do not** use `town_map` / `WorldMapScreen` (cmd 157); it opens the map UI during `lockall` and softlocks on close |
| Phone numbers | `register_gear_number` — Mom (0), Elm (1), Oak (2) |
| HM02 Fly (testing) | `ITEM_HM02` (421) when `OPENWORLD_TESTING_GRANTS` is defined; field use via [Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags) |

**Starting city / starter (v1 — [Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon)):**

**Status (Sep 2026):** **18-city menu**, **three-type starter pick** (grass / fire / water, 4 options each → **3** Pokémon), and **step 1 exit** verified in-game. Outdoor home-door routing (**Vision-3 steps 2–4**) not complete — step 2 was attempted twice and rolled back; see [Home = bidirectional door + interior swap](#home--bidirectional-door--interior-swap).

| Step | When | What |
|------|------|------|
| 1 | Mom cutscene, before starter menu | **18-city** `ListLocalText` (Vision-3 index **0–17**) → `VAR_PLAYER_START_CITY` (**0x4031**) → `_set_home_dynamic_warp` |
| 2 | Same cutscene | **Three** starter menus (grass / fire / water, 4 options each) → **3×** `give_mon` (not `choose_starter`) → `FLAG_GOT_STARTER` |
| 3 | Same cutscene | Mom grants (bag, Pokédex, Pass, etc.) — **no post-cutscene teleport** |
| 4 | Walk to front door **(3, 10)** on 1F | Dynamic exit warp → outdoor home door in chosen city (**Vision-3 step 1 — works**) |

**Menu index = Wilds-2 table row** (direct lookup in `src/wild_level_caps.c`; no PoC remap).

### Starter selection — **not** `choose_starter`

Open-world intro **does not** use vanilla `choose_starter` (3-ball UI) or `src/starters.c`. Those are a **different, unused path** in this hack.

| | **Open-world path (what we use)** | **Vanilla / legacy path (not used)** |
|---|-----------------------------------|--------------------------------------|
| Where | Mom scr_seq **845** script **0** (`scr_seq_t20_mom_script0.s`) | `choose_starter` script cmd → `CreateStarter_*` hooks |
| UI | **3×** 4-row `ListLocalText` menus (grass, fire, water) | Three Poké Balls on a table |
| Give Pokémon | **3×** `give_mon` (one per type menu) | Engine creates mon from `starters.c` trio |
| Species count | **12** options across **3** menus (hardcoded in script) | **6** in `sStarterChoices[]` (Johto 0–2 + Kanto 3–5 only) |
| `VAR_PLAYER_STARTER` | Grass menu index **0–3** after first pick | Was **0** or **3** (region base for which trio) |
| Dex / phone register | `set_starter_choice` from **party slot 0** (grass pick) after all `give_mon` | Same cmd, but after ball pick |

**Implications for dev:**

- Adding a starter → edit **`scr_seq_t20_mom_script0.s`** (+ string in **`data/text/545.txt`**). Do **not** expect `starters.c` changes to affect Mom’s menu.
- **`src/starters.c`** + **`hooks`** (`CreateStarter_SetStarterSpecies`, `CreateStarter_CreateMon`) still ship with the engine but are **dead code** unless some other scr_seq calls `choose_starter`. Grep shows **no** open-world scr_seq does — bedroom **846** is vanilla and must stay that way (verify script rejects `choose_starter` there).
- Old design docs ([Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon)) still describe Johto/Kanto YES/NO + 3-ball UI; **implementation superseded** that with type-split text menus (grass / fire / water).

**Pokémon menu:** `FLAG_GOT_BAG` set during Mom cutscene (not bedroom).

### ID cheat sheet (easy to mix up)

| What | Value | pret / file |
|------|-------|-------------|
| `VAR_PLAYER_START_CITY` | **0x4031** | `armips/include/vars.s` |
| `VAR_PLAYER_STARTER` | **0x4030** | same |
| Map header `MAP_T20R0201` (Mom 1F) | **63** | ≠ scr_seq member |
| Map header `MAP_T20R0202` (bedroom) | **64** | zone_event **061** |
| Map header `MAP_T20` (New Bark outdoor) | **60** | zone_event **057** |
| scr_seq Mom house | member **845** | script **0** = cutscene |
| zone_event Mom 1F interior | member **060** | 2 warps — **do not reindex** |
| zone_event bedroom 2F | member **061** | warp down uses **anchor 1** → 1F warp **slot 1** |
| New Bark player house door | **057** warp **1** at **(695, 396)** | vanilla → header 63; **no** `CITY_DOORS` patch |
| Text bank Mom dialogue | **545** | city prompt **2**, cities **3–20**, grass prompt **21**, species **22–33**, fire/water prompts **34–35** |

### Home = bidirectional door + interior swap

Canonical interior stays **`T20R0201`** (scr_seq **845**, Mom). Four warp behaviours per save ([Vision-3 four steps](../DESIGN-VISION.md#home-wiring-four-steps)):

| Step | Direction | Status |
|------|-----------|--------|
| **1** | Mom interior → start city outdoor door | **Complete** — dynamic exit (below) |
| **2** | Start city outdoor door → Mom interior | **Rolled back** — see [Outdoor entrance attempts](#outdoor-entrance-attempts-rolled-back) |
| **3** | New Bark door → displaced interior (start ≠ New Bark) | **Not started** |
| **4** | Displaced interior → New Bark outdoor | **Not started** |

**Designated home doors** (reference for Mom `_set_home_dynamic_warp` and future step 2/3). Outdoor doors stay **vanilla** in ROM as of Sep 2026 rollback.

| Idx | City | zone_event | warp | (x, z) | Outdoor hdr | Vanilla interior hdr |
|-----|------|------------|------|--------|-------------|----------------------|
| 0 | New Bark | **057** | 1 | (695, 396) | 60 | **63** (Mom — vanilla) |
| 1 | Violet | **070** | 8 | (459, 254) | 73 | 160 |
| 2 | Azalea | **071** | 4 | (419, 468) | 74 | 163 |
| 3 | Goldenrod | **073** | 14 | (376, 335) | 76 | 205 |
| 4 | Ecruteak | **075** | 1 | (375, 173) | 78 | 85 |
| 5 | Olivine | **074** | 6 | (287, 241) | 77 | 228 |
| 6 | Cianwood | **072** | 7 | (167, 335) | 75 | 385 |
| 7 | Mahogany | **084** | 4 | (537, 174) | 87 | 133 |
| 8 | Blackthorn | **086** | 4 | (684, 168) | 89 | 290 |
| 9 | Pallet | **046** | 0 | (1033, 363) | 49 | 503 |
| 10 | Viridian | **047** | 1 | (1034, 244) | 50 | 497 |
| 11 | Pewter | **048** | 5 | (1037, 111) | 51 | 477 |
| 12 | Cerulean | **049** | 2 | (1304, 131) | 52 | 431 |
| 13 | Saffron | **056** | 14 | (1323, 242) | 59 | 399 |
| 14 | Lavender | **050** | 2 | (1414, 249) | 53 | 436 |
| 15 | Celadon | **052** | 6 | (1225, 261) | 55 | 383 |
| 16 | Vermilion | **051** | 3 | (1301, 309) | 54 | 363 |
| 17 | Fuchsia | **053** | 8 | (1200, 439) | 56 | 481 |

Goldenrod: NE house by Flower Shop (**not** Friendship Checker / `T25R0301`). Saffron: Copycat house warp **14** (**not** warp 7 / `T11R0801`).

#### Step 1 — Mom exit (verified; keep as-is)

**Verified working pattern (do not simplify):**

1. **Interior 060 warp slot 0** — change **(3, 10)** from `hdr=60, anchor=1` to **`hdr=0xFFF (4095), anchor=0x100 (256)`**. Keep warp slot **1** `(3,3)→64` untouched (stairs). Patched by `tools/patch_zone_event_start_city.py`.
2. **Mom script 0** — after city pick, `set_dynamic_warp` using **`VAR_TEMP_x4000`–`x4004`** (cmd **240** reads all five args via `ScriptGetVar`, not literals). `_set_home_dynamic_warp` must match **outdoor map header + warp index** from table above.
3. **No post-cutscene `warp`** — player walks to the door.
4. **No coord script at (3, 10)** and **no removing warp slot 0** — both break stairs (black void) or misfire.

**Engine reference (pret `field/field_control.c`):** warp with `anchor == 0x100` and `header == 0xFFF` uses `LocalFieldData.dynamicWarp`. Vanilla examples: zone_event **396–402** (elevator exits).

#### Outdoor entrance attempts (rolled back)

**v1 (Sep 2026, rolled back):** patch all **17** non–New-Bark outdoor home doors in `zone_event` to header **63** via `tools/patch_zone_event_start_city.py` (`CITY_DOORS`). Every door entered Mom’s house; wrong for non-start cities but proved the door table and Mom exit wiring.

**v2 (Sep 2026, rolled back):** add ARM9 hook after `Field_InitMapEvents` to rewrite warp headers in **RAM** on map load — start city door → **63**; other cities → vanilla interior header; New Bark door when start ≠ New Bark → start city’s vanilla interior. Files were `armips/asm/start_city_home_warp_hook.s`, `start_city_home_warp_data.s`, `scripts/build/patch_field_init_map_events_hook.py`. **Map-load crashes** (`Undefined instruction` at `0x0203C108`, then `0x020537FC`) — Thumb/ARM interworking and register/stack bugs in the hook; never verified in-game.

**After rollback:** deleting the patch script does **not** unpatch `base/arm9.bin`. The hook wrote a `bl` over `0x02052FD2` on each build; incremental `make` reuses cached `base/` until `rom.nds` is newer. Fix: **`rm -rf base && make -j24`** (full re-extract from `rom.nds`). Check: `python scripts/local/_check_arm9_hook_gone.py`.

**Planned v3 (not implemented):** leave outdoor doors **vanilla** in ROM (current state). On map load, patch **only the start city’s** home-door warp header to **63** — same *timing* as step 1, without mass-patching and reverting 16 doors. Steps 3–4 (New Bark ↔ displaced interior) still open.

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
| Patch all outdoor doors → 63 + RAM revert loop | Inverted design; hook crashes on map load; rolled back |
| `Field_InitMapEvents` mid/tail hook in overlay 129 | Overlay overlap / wrong thunk address; abandoned early |

**Deferred:** Copycat/swap-house story scripts inside displaced interiors.

**Build / verify:**

```bash
make build/narc/scr_seq.narc build/narc/zone_event.narc NOSCAN=1
python scripts/dev/verify_t20_mom_patch.py
python scripts/dev/verify_start_city_patch.py
# repack test.nds
```

**Files:** `armips/scr_seq/scr_seq_t20_mom_script0.s`, `tools/patch_scr_seq_t20_mom.py` (`2_845`), `tools/patch_zone_event_start_city.py` (interior **060** exit only), `scripts/dev/verify_start_city_patch.py`, `scripts/dev/verify_t20_mom_patch.py`, `data/text/545.txt`, `armips/include/vars.s`. Init header **618** stays vanilla.

**Bedroom starter:** not used — bedroom scr_seq **846** stays vanilla (**no** `choose_starter`, no OnTransition starter hook). All starter picking is in **Mom script 0** only.

**Change a home door:** recon in `build/a032_vanilla` (member, warp index, x/z, vanilla header) → update **`EXPECTED_DOORS`** in verify script + **`_set_home_dynamic_warp`** branch + warp constant in Mom script. Verify **060** still has exactly 2 warps.

**Dialogue:** Mom intro greet **545** strings **0–1**. Post-cutscene talk still uses vanilla Elm errand strings until [Story-1](DESIGN-STORY.md#story-1-story-and-script-content). Cutscene skips bag/card/save/options `npc_msg`s; fanfares + flags unlock touch menu.

**Note:** Test with **new saves** after ROM changes. Story hooks (Elm, rival) still vanilla until Phase 4.

---

## Story flag range sweep (dev)

**Purpose:** find which pret **story flag** (decimal **100–399**, `armips/include/flags.s`) gates some vanilla check — without guessing one flag at a time. First use case: [Mart Poké Ball](#mart-poké-ball) (`InitMartUI` hides `ITEM_POKE_BALL` until a story flag is set).

**Toggles** (`include/config.h`):

| Define | Role |
| ------ | ---- |
| `OPENWORLD_STORY_FLAG_SWEEP` | When defined, Mom intro loops `setflagvar` over an inclusive range (skips normal `FLAG_UNK_09A` mart grant). |
| `OPENWORLD_STORY_FLAG_SWEEP_START` | First flag index (decimal). |
| `OPENWORLD_STORY_FLAG_SWEEP_END` | Last flag index (decimal). |

**Implementation:** `armips/scr_seq/scr_seq_t20_mom_script0.s` (loop after Apricorn Box flag); `tools/patch_scr_seq_t20_mom.py` reads `config.h` and passes armips `-equ` values when assembling script **0**. Rebuild scr_seq / full ROM after changing the range.

**Workflow:** bisect `[START, END]` on **throwaway saves** (setting many flags breaks world state). When the minimal flag is known, add a single `setflag` in Mom intro (or the right script), **undef** `OPENWORLD_STORY_FLAG_SWEEP`, and document the flag in [HGSS-STORY-FLAGS.md](HGSS-STORY-FLAGS.md).

**Not runtime config:** the `.nds` does not read an external file; only build-time `config.h` (or future patcher-side cfg) controls the range.

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

**Files:** `tools/patch_scr_seq_train.py` (`2_893`, `2_834` in narcs.mk), `scripts/dev/verify_train_patch.py`, `scripts/dev/scan_train_power.py`.

**Verify:** `make scr_seq_clean && make -j24`, then `python scripts/dev/verify_train_patch.py`. In-game: new save → Mom intro → Goldenrod or Saffron station → policeman allows platform → pass coord gate → board train.

**Gotcha:** map header IDs ≠ scr_seq members (`MAP_T25R0501` / `MAP_T11R0601` vs **893** / **834**).

---

## Route 4 ledge boost (Cerulean → Mt Moon)

**Status:** **verified in-game** (Aug 2026). NPC **(1270, 118)** / landing **(1270, 116)** — no coordinate tuning needed.

**Goal:** one-way paid bypass below the Cerulean-side ledge — blackbelt + Machoke boost you up 2 tiles for **$100** (same flow as Route 42 ferry, single shore).

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
| NPC tile | **(1270, 118)** facing **south** (sprite **344** blackbelt) | `tools/patch_zone_event_r04_boost.py` |
| Machoke companion | **(1269, 118)** (sprite **1014** static Machoke) | same |
| Landing tile | **(1270, 116)** — 2 north of NPC | same + `armips/scr_seq/scr_seq_r04_boost.s` (`LAND_X` / `LAND_Z`) |
| Object ids | **4** (blackbelt), **5** (Machoke) | zone_event patch |
| scr_seq slot | **1** → scriptId **2** | scr_seq patch |

### Files

| File | Role |
|------|------|
| `armips/scr_seq/scr_seq_r04_boost.s` | Paid warp script |
| `tools/patch_scr_seq_r04_boost.py` | Append slot to **2_178** |
| `tools/patch_zone_event_r04_boost.py` | Object on **2_009** |
| `data/text/328.txt` | Trainer tips (0) + boost lines (1–4) |
| `scripts/dev/verify_r04_boost.py` | Post-build check |
| `scripts/dev/find_r04_coords.py` | Recon helper for world `(x,z)` |

**Verify:** `make scr_seq_clean && make -j24`, then `python scripts/dev/verify_r04_boost.py`.

---

## Olivine Secret Medicine (Jasmine)

**Goal:** Heal Ampharos without a Cianwood fetch. Buy Secret Medicine locally, use it at the Lighthouse.

**Mart:** Olivine Poké Mart **second clerk** (`std_special_mart`, `VAR_SPECIAL_x8004 = 10`) → `sOlivineMart` in `src/field/mart.c`. Full mart layout: [Mart expansion](#mart-expansion-srcfieldmartc). With `MART_EXPANSION`, the first clerk uses badge-tier `ScrCmd_MartBuy` and ignores city extras.

### Mart Poké Ball

Vanilla **`InitMartUI`** drops **`ITEM_POKE_BALL` (4)** from buy lists while Great/Ultra and other stock still show until a pret **story flag** is set.

**Verified (Sep 2026):** **`FLAG_UNK_09A` (154)** alone restores shop Poké Balls. Mom intro sets it with Pokégear / UI unlocks (`scr_seq_t20_mom_script0.s`). Not **`FLAG_MET_PASSERBY_BOY` (153)**, **`FLAG_UNK_0B5` (181)**, or **`FLAG_UNK_15D` (349)** alone. Found via [story flag sweep](#story-flag-range-sweep-dev) (151–156 bracket). Pret name only — vanilla trigger still TBD; index [HGSS-STORY-FLAGS.md](HGSS-STORY-FLAGS.md).

**Price:** `ITEM_SECRET_MEDICINE` buy price **¥500** in `data/itemdata/itemdata.c`. Cianwood pharmacy still gives it free via `giveitem`.

**Lighthouse gate:** Vanilla `scr_seq` member **66** (`D27R0107`) only offers the medicine scene when **`FLAG_GOT_SECRETPOTION`** (185) is set — buying the item alone is not enough. **`Bag_AddItem`** sets that flag when `ITEM_SECRET_MEDICINE` (464) is added (mart purchase or pharmacy).

**IDs:** map header `MAP_D27R0107` = 225; scr_seq member **66**; Olivine mart scr_seq **912** (`T26FS0101`).

**Verify in-game:** Olivine Mart → second clerk → buy Secret Medicine → Lighthouse top → Jasmine uses medicine on Ampharos → Gym.

**Text:** Lighthouse dialogue in `data/text/094.txt` (msg bank **094**, map `D27R0107`). Edits lines 0–1 (local mart hint) and 3 (item name).

---

## Mart expansion (`src/field/mart.c`)

**Toggle:** `#define MART_EXPANSION` in `include/config.h` (on in this fork).

**Design:** [World-7](DESIGN-WORLD.md#world-7-shops) (player-facing summary in [CHANGELOG.md](../CHANGELOG.md) § Shops).

### Two clerk models

| Mechanism | Used where | Source |
| --------- | ---------- | ------ |
| **`ScrCmd_MartBuy`** | Goldenrod & Celadon dept **2F** first clerk | Builds list from `sBadgeMart[]` (badge count → `required_badges` threshold). Does **not** merge city-specific extras. |
| **`std_special_mart` + `VAR_SPECIAL_x8004`** | Route/town marts, dept floors, Olivine 2nd clerk | Script picks index → pointer to `u16` array ending in `0xFFFF`. Arrays live in **`src/field/mart.c`**. |

Vanilla **`InitMartUI`** still hides **`ITEM_POKE_BALL`** until **`FLAG_UNK_09A` (154)** — see [Mart Poké Ball](#mart-poké-ball). Mom intro sets that flag.

### Arrays (edit here for stock changes)

| Symbol | Role |
| ------ | ---- |
| `sBadgeMart[]` | Badge-gated balls, repels, berries, TM70, held items |
| `sGoldenrodDepartment*` / `sCeladonDepartment*` | Dept store floors (berries, TMs, vitamins, stones, etc.) |
| `sGoldenrodHerbs[]` | Goldenrod herb clerk → EV-reduction berries |
| `sOlivineMart[]` | Olivine **second** clerk — Secret Medicine + specialty |
| `sCherrygroveCityMart[]`, `sVioletCityMart[]`, … | Per-city specialty shelves |
| `sCianwoodPharmacy[]` | Cianwood shop clerk (not healing stock) |
| `sIndigoPlateau[]` | Indigo mart |
| `sMtMoonSquare[]`, `sMahoganyPreRocketHideout[]`, `sMahoganyPostRocketHideout[]` | Route specials |

**Scr_seq wiring:** each map’s mart script sets `VAR_SPECIAL_x8004` to the index expected by the engine hook (Olivine **10** → `sOlivineMart` — see [Olivine Secret Medicine](#olivine-secret-medicine-jasmine)). When adding a new list, repoint the script constant and rebuild.

**Verify:** build ROM → sample Goldenrod/Celadon dept floors (both clerks), one town specialty mart, badge-gated 2F shelf at 0 vs 8 badges.

---

## Game Corner TM prizes

**Design:** [World-5 § Game Corner TMs](../DESIGN-WORLD.md#game-corner-tms) — renewable coin-purchased TMs at both Game Corners.

International HGSS prize menus are **hardcoded scr_seq** (not the unused `sDPPlGameCornerPrizeMap` table from pret’s `scrcmd_dppl_prizes.c`). Each prize block embeds an item id and a coin cost. Submenus: **6 TMs + Cancel**, **4 held items + Cancel**, **3 Pokémon + Cancel** (Pokémon menus still vanilla).

| Corner | Map | scr_seq member | Text bank |
| ------ | --- | -------------- | --------- |
| **Goldenrod** prize clerks | `T25SP0101` | **910** (`2_910`) | **603** (`data/text/603.txt`) — TM menu lines **15–20** (indices 14–19) |
| **Celadon** prize clerks | `T07R0501` (dept store 5F) | **804** (`2_804`) | **509** (`data/text/509.txt`) — TM menu lines **24–29** |

**Not** the Voltorb Flip floor (`T07SP0101` → scr_seq **806**).

### TM lists

| Corner | TMs (menu order) |
| ------ | ---------------- |
| Goldenrod | TM05, TM75, TM44, TM46, TM90, TM92 |
| Celadon | TM58, TM32, TM10, TM49, TM67, TM82 |

| Corner | Held items (menu order) |
| ------ | ----------------------- |
| Goldenrod | Bright Powder, Quick Claw, Wide Lens, Metronome |
| Celadon | Focus Band, Zoom Lens, Scope Lens, Luck Incense |

**Coin costs (temporary):** every TM, held item, and Pokémon prize is **50 Coins** (`PRIZE_COIN_COST` in `patch_scr_seq_game_corner.py`). Flat pricing is a playtest shortcut until [World-5 § Coin income](../DESIGN-WORLD.md#coin-income-not-implemented) ships; restore tiered costs when coin income is decided.

### Files

| File | Role |
| ---- | ---- |
| `tools/patch_scr_seq_game_corner.py` | Ordered `u16` item-id and coin-cost patches in `2_910` / `2_804` after vanilla extract |
| `scripts/build/verify_game_corner_patch.py` | Patched item ids and coin costs at each fixed offset |
| `data/text/603.txt`, `data/text/509.txt` | Prize menu labels (`ROAR`, `FURY CUTTER`, …) |

**Build:** wired in `narcs.mk` after gym scr_seq patches.

**Verify in-game:** Coin Case → Goldenrod Game Corner → right-hand clerk → TM and held-item submenus; Celadon dept store 5F prize clerk → same. Pokémon submenu still vanilla.

**Coin income:** prize menus only — earning Coins is still **Voltorb Flip** on the casino floor (scr_seq **806** / `CasinoGame` in **910**). Design requires a non–Voltorb Flip source: [World-5 § Coin income](../DESIGN-WORLD.md#coin-income-not-implemented).

**Changing TMs later:** edit replacement tables in `patch_scr_seq_game_corner.py`, update menu strings in the text banks (keep `{CURSOR_X …}` padding if renaming), rebuild.

---

## Wild level caps (distance-based) — verified PoC

**Status: verified in-game Sep 2026** — distance level rolls ([Wilds-1 level distribution](DESIGN-WILDS.md#level-distribution)), level-up **and synthetic** stage adjust (e.g. Mareep → Flaaffy, Golbat → Crobat @ 30, trade/stone lines from TSV). Sprite, stats, moves, battle name, and caught mon match the final species. Design: [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps).

**Toggle:** `IMPLEMENT_WILD_DISTANCE_LEVEL_CAPS` in `include/config.h` (on by default). Comment out to restore vanilla wild levels.

### Formula and table

Build-time cap per `(starting city, encounter area id)`:

```
levelCap = 55 × max(0, route_distance − 1) / (max_route_distance − 1) + 5   // caps in [5, 60]
```

- **Graph data:** `scripts/dev/Route Levels/connections.txt`, `starting_cities.txt`
- **Distances:** `scripts/dev/Route Levels/calculate_location_distances.py` → `location_distances.txt` (includes `MaxDistance` row per city column)
- **Enc area → graph node:** `scripts/dev/Route Levels/encounter_area_graph.tsv` (`ENCDATA_*` index → location name)
- **ROM table:** `scripts/build/gen_wild_level_caps.py` → `src/wild_level_caps_data.c` + `include/constants/generated/wild_level_caps.h` (Makefile rule in `narcs.mk`)

Runtime lookup: `sWildLevelCaps[startCityIndex][encBank]` where `encBank = MapHeader_GetWildEncounterBank(mapId)`.

**Start city var:** Mom menu sets `VAR_PLAYER_START_CITY` (**0x4031**) to Vision-3 index **0–17**; `ResolveStartCityIndex` uses it directly as the Wilds-2 table row (`src/wild_level_caps.c`).

**Example (Saffron start):** Route 37 → **23**, Violet → **23**, Route 31 → **29**, Dark Cave → **35**, Route 30 → **35**. **Example (Pallet start):** Route 1 → **5** (distance 0–1 both cap at starter floor).

### Runtime pipeline

| Stage | Where | What |
|-------|--------|------|
| Persist FieldSystem | `StoreFieldSysPtr` hook @ `0x0203E028` | Writes `gFieldSysPtr` → ARM9 scratch `sPersistFieldSysPtr` @ `0x021FF900` |
| Cache cap (field) | `WildEncSingle` / `WildWaterEncSingle` in `src/pokemon.c` | `CacheWildLevelCapFromFieldSystem(fsys)` while FieldSystem is valid |
| Apply level (battle) | `modify_species_encounter_data` in `asm/other_hook.s` (overlay 129) | `ApplyWildDistanceLevelCapToMon` **before** `InitBoxMonMoveset`; tail-calls vanilla stub `0x02247B4C` last |
| Stage adjust | `include/encounter_species_stage.h` | `AdjustEncounterSpeciesForLevel` = level-up `AdjustSpeciesForLevel` + synthetic edges (`data/synthetic_evolution_thresholds.tsv` → `sSyntheticEvoEdgesData` in field overlay). Overlay 129: patched `LevelUpEvoTablesFieldAddr` + `SyntheticEvoEdgesFieldAddr` |
| Species display | `ApplyWildSpeciesStageForLevel` in `src/wild_level_caps.c` | After `SetMonData(MON_DATA_SPECIES, …)`, call `SetMonData(MON_DATA_SPECIES_NAME, NULL)` — same as `PokeParaSet` — or battle/caught UI keeps the encounter-table name while sprite/stats use the new species |
| Level write | `src/wild_level_caps.c` | Roll level → adjust species → set exp + `MON_DATA_LEVEL` → `RecalcPartyPokemonStats` |

**Map ID:** read from `SaveBlock2` → `LocalFieldData.currentPosition.mapId` (not `fsys->location`, which is often `MAP_EVERYWHERE` during encounters).

**Not hooked:** Safari Zone (`data/SafariEncounters.c`), Bug Catching Contest (verify in-game path), `modify_species_encounter_data_rare` (roamers), scripted `wild_battle`.

**Stage adjust:** level-up chains (`data/Evolutions.c`) plus **synthetic edges** ([Wilds-1 § Synthetic evolution stages](DESIGN-WILDS.md#synthetic-evolution-stages-wild--trainer)) — trade, stone, friendship, move-known, etc. **Deferred in TSV:** Eevee, Tyrogue, Shedinja, gendered splits (Burmy, Gallade, …). Player evolution unchanged ([World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones)).

### ARM9 scratch (`armips/asm/wild_level_caps.s`, `rom.ld`)

| Symbol | Address | Size |
|--------|---------|------|
| `sPersistFieldSysPtr` | `0x021FF900` | 4 |
| `sWildLevelCapDebug` | `0x021FF910` | 32 |
| `sWildCapCache` | `0x021FF930` | 8 |
| `sLevelUpEvoTablesRuntimePtr` | `0x021FF940` | 4 |

`0x021FF940` is zeroed in `armips/asm/wild_level_caps.s` but unused — overlay 129 uses patched pointers into **field overlay rodata**, not ARM9 scratch.

Stage tables live in **contiguous field overlay rodata** (`sLevelUpEvoTablesData`, `sSyntheticEvoEdgesData`). Do not pin them with a linker hole — that bloated the field overlay past `0x023D8000` and clobbered overlay 129.

**Build-time patch:** `scripts/build/patch_level_up_evo_addrs.py` runs after `field_linked.o` + `linked.o` exist; patches overlay 129 **`LevelUpEvoTablesFieldAddr`** and **`SyntheticEvoEdgesFieldAddr`** in `build/output.bin` (also from `scripts/build/make.py`). Example log: `LevelUpEvoTablesFieldAddr @ … = 0x023CA4A8` and `SyntheticEvoEdgesFieldAddr @ … = 0x023CC220`. If either pointer is **0**, wild stage adjust is skipped (`ApplyWildSpeciesStageForLevel` guard in `src/wild_level_caps.c`).

Scratch survives overlay 129 reload; do not reuse these addresses for other features without updating `rom.ld`.

**Overlay 129 size:** must stay **≤ 32 KiB** (`0x8000`). It loads at startup @ `0x023D8000` and overlaps the field overlay reservation — do not link large rodata into overlay 129.

### Debug toggles (turn off for normal play)

| Define | File | Effect |
|--------|------|--------|
| `DEBUG_WILD_LEVEL_CAP_LEVELS` | `include/debug.h` | Level = diagnostic code (4–9 fail) or exact table cap on success |
| `DEBUG_WILD_LEVEL_CAP_EXACT` | `include/config.h` | Level = cap exactly (no random roll) |
| `DEBUG_WILD_LEVEL_CAPS` | `include/debug.h` | melonDS `debug_printf` on cache/apply |

Production: all three **off**; `RollWildLevel(cap)` — adult band **`[⌊0.9×cap⌋−2, cap]`** always; if `cap ≥ 10`, **15%** uniform **2–7** else adult band (never level 1). See [Wilds-1 level distribution](DESIGN-WILDS.md#level-distribution).

### Editing caps

1. Edit graph / distances / encounter mapping under `scripts/dev/Route Levels/`.
2. Re-run `python3 scripts/build/gen_wild_level_caps.py` (or full `make` — `narcs.mk` regenerates the table).
3. Rebuild `test.nds`.

**C array gotcha:** `sWildLevelCaps[18][143]` must use **one `{ ... }` brace pair per city row**. Extra top-level `{ ... },` every N values become separate rows in C; columns past the first chunk zero-fill → cap **0** / diagnostic level **8**.

### Scripts layout (this feature)

All tracked — nothing belongs in `scripts/local/`:

| Path | Bucket | Role |
|------|--------|------|
| `scripts/build/gen_wild_level_caps.py` | build | Cap table → `src/wild_level_caps_data.c` (`narcs.mk`) |
| `scripts/build/gen_level_up_evo_tables.py` | build | Stage tables → `src/field/level_up_evo_tables.c` + `include/constants/generated/level_up_evo_tables.h` |
| `scripts/build/patch_level_up_evo_addrs.py` | build | Patch `LevelUpEvoTablesFieldAddr` + `SyntheticEvoEdgesFieldAddr` in `build/output.bin` (`Makefile`, `make.py`) |
| `scripts/build/gen_synthetic_evo_edges.py` | build | TSV → `src/field/synthetic_evo_edges_data.c` + generated header (`narcs.mk`) |
| `data/synthetic_evolution_thresholds.tsv` | data | Authoring source for synthetic stage edges (`from`, `to`, `min_level`, `branch`) |
| `include/species_stage_for_level.h` | include | `AdjustSpeciesForLevel` (level-up chains only) |
| `include/synthetic_evo_apply.h` | include | `ApplySyntheticEvolutionEdges` (inline; reads `gSyntheticEvoEdgesPtr`) |
| `include/encounter_species_stage.h` | include | `AdjustEncounterSpeciesForLevel` — level-up then synthetic (wild + trainer) |
| `scripts/dev/Route Levels/calculate_location_distances.py` | dev | Regenerate `location_distances.txt` after graph edits |
| `scripts/dev/Route Levels/*.txt`, `encounter_area_graph.tsv` | dev | Source graph inputs |

**Not in `scripts/local/`:** wild-cap and synthetic-stage tooling is all under `data/`, `scripts/build/`, and `scripts/dev/Route Levels/`. Session throwaways stay gitignored per § Scripts layout.

**Generated (rebuilt every `make`):** `include/constants/generated/wild_level_caps.h`, `level_up_evo_tables.h`, `synthetic_evo_edges.h`. `.c` outputs may be committed for convenience (`wild_level_caps_data.c`, `level_up_evo_tables.c`, `synthetic_evo_edges_data.c`). `wild_level_caps.o` uses `-DOVERLAY129` for patched field pointers.

### Editing synthetic stage edges

1. Edit `data/synthetic_evolution_thresholds.tsv` (`branch`: empty or `random50`).
2. Full `make` (or `python3 scripts/build/gen_synthetic_evo_edges.py`) regenerates field rodata.
3. Rebuild `test.nds` — confirm both patch lines in the build log.

---

## World placement (DSPRE)

Use **DSPRE’s map matrix** to estimate where something lives, then patch the **correct zone_event member** with the **correct coordinate system**.

**Matrix tile → world origin (recon only)**

- Each matrix cell is **32×32** world tiles.
- Cell `(col, row)` → world range:
  - **x:** `col × 32` … `(col + 1) × 32 − 1`
  - **z:** `row × 32` … `(row + 1) × 32 − 1`
- Example: matrix **(8, 7)** → x **256–287**, z **224–255** (z **256** is already the next row down — cell **(8, 8)**).

**Within-cell offset → world (for scanning `build/a032_vanilla`)**

- DSPRE map-editor coords are **local to that map cell**.
- **World x** = `col × 32 + local_x`
- **World z** = `row × 32 + local_z`
- Example: door at local **(16, 25)** in cell **(8, 7)** → world **(272, 249)**.

**Map header ID ≠ zone_event / scr_seq / msg index**

`include/constants/maps.h` gives the **map header row** (e.g. `MAP_T26` = **77**, `MAP_R44` = **46**). Each row points at separate NARC members — look up pret [`src/data/map_headers.h`](https://github.com/pret/pokeheartgold/blob/master/src/data/map_headers.h):

| Map | Header id | `eventsBank` | `scriptsBank` | `msgBank` | Coords in zone_event |
|-----|-----------|--------------|---------------|-----------|----------------------|
| Route 44 | **46** | **043** | **257** | **404** | **world** |
| Olivine City | **77** | **074** | **911** | **604** | **world** |

Headbutt index **074** = Azalea Town; zone_event **074** = Olivine outdoors — same number, unrelated namespaces.

**Johto cities on the main matrix** (`map_matrix_0000_EVERYWHERE`) use **world `(x, z)`** in their `eventsBank` file, same as routes. Do **not** assume `eventsBank == map header id` (member **077** is Ecruteak Gym `077_T27GYM0101`, not Olivine).

**Decision tree**

1. Find `MAP_*` in `include/constants/maps.h` (header index).
2. Read pret `map_headers.h` row → **`eventsBank`**, **`scriptsBank`**, **`msgBank`**.
3. Patch **`build/a032/2_<eventsBank>`** using that file’s coord scale (world if max object x ≥ ~200).
4. Append scr_seq script to **`build/a012/2_<scriptsBank>`**; text in **`data/text/<msgBank>.txt`**.
5. Near a town/route boundary — may need **two** members (Mahogany **084** + matrix **043**).

**Recon commands**

```bash
# Which world-scale members cover a tile?
python3 scripts/dev/find_zone_event_member.py --world 273 248

# Inspect pret eventsBank member (Olivine = 74, not 77)
python3 scripts/dev/find_zone_event_member.py --member 74 --near 279 247
python3 scripts/dev/inspect_zone_event.py build/a032_vanilla/2_074

# Find which msg bank has a landmark string (needs base/root/a/0/2/7 extract)
python3 scripts/dev/find_msg_text.py "Olivine City" --bank 604
```

**Script types:** `type=0` + map `scriptId` for scr_seq slots; `type=1` is for 3000+ common scripts on outdoor matrix NPCs.

---

## Fishing Rod guru NPCs

**Goal:** One shared fisherman script gives Old → Good → Super Rod based on Pokédex caught Water-type evolutionary families (any catch source). Dialogue is region-agnostic for reuse across gurus.

**Progression:** `FISHING_ROD_GOOD_FAMILIES` (default **5**) and `FISHING_ROD_SUPER_FAMILIES` (default **15**) in `include/config.h` / `armips/include/config.s`. Super Rod ownership is `hasitem(ITEM_SUPER_ROD)` — no save flag.

**C:** `src/fishing_rod.c` counts families via union-find on evolution data + dex caught flags. Script hooks: `Script_RunNewCmd` cases **1** (count) and **2** (remaining until next tier) in `src/script_new_cmds.c`.

**Flags:** `FLAG_GOT_OLD_ROD` (117), `FLAG_GOT_GOOD_ROD` (189).

**Item grants:** Use `giveitem_no_check` (wraps `std_give_item_verbose`) — same flashy obtain UI + fanfare as Mom’s Pass/Ticket grants. Do **not** use bare `giveitem` (silent, no fanfare). **`npc_msg` does not wait for A** — before each grant use `wait_button_or_walk_away` + `closemsg`, then `giveitem_no_check` (obtain UI waits for A on its own). **After** the grant, `closemsg` again (Mom script 0 line 116) — otherwise the “put in pocket” line sticks and the touch menu stays locked. Still **no Yes/No** before the grant (unlike vanilla fisherman).

**Text buffers:** Progress line uses `{STRVAR_1 52, 0, 0}` + script `TextNumber 0, var`. Do **not** use STRVAR type **50** (shows “GOLD” / points UI) or **51** (item names — “Good Rod” when buffer stale).

**Route 44 reference (verified in-game Sep 2026 — copy this recipe for more gurus):**

| Layer | ID | Notes |
|-------|-----|--------|
| Map header | `MAP_R44` = **46** | pret `scriptsBank` → scr_seq member **257** (not 260!) |
| zone_event | member **043** (outdoor matrix) — obj **15**, sprite **347**, script **4**, **(568, 183)**, **`type=0`** | Bridge fisherman obj **1** at **(576, 184)** uses **`type=1`** + script **3124** (common script — not map scr_seq) |
| scr_seq | member **257** — rod guru in **slot 3** (scriptId **4**) | Vanilla slots **0–2** = empty + two signposts; append guru after slot 2 |
| msg bank | **404** | Vanilla signs **0–1**; guru lines **2–6** |

**Wrong IDs (learned the hard way):**

- scr_seq **260** = **Route 47** (Embedded Tower / Chuck), not Route 44 — sign text indices 0–1 match bank 404 only when misread out of context.
- zone_event **046/090** — Ice Path junction chunk (z≈367–477), not walkable Route 44 body.
- zone_event **086** — Blackthorn area (x≈661+).
- pret filename `046_R44` ≠ outdoor-matrix member for the bridge.

**ID discovery:** Headbutt tree envelope in `Headbutt.c`, in-game fisherman coords, pret `map_headers.h` (`scriptsBank` for `MAP_ROUTE_44` → **257**). Recon scripts (local, not tracked): `scripts/local/list_r44_npcs.py`, `scripts/local/find_r44_by_coords.py`, `scripts/local/analyze_scr_seq_260.py` (why 260 is R47).

**Patch:** `armips/scr_seq/scr_seq_r44_rod_guru.s` → `tools/patch_scr_seq_r44_rod_guru.py` (`2_257`). Zone: `tools/patch_zone_event_r44_rod_guru.py` on **`2_043`**. Text: `data/text/404.txt`.

**Verify:** `python3 scripts/build/verify_r44_rod_guru_patch.py build/a012/2_257` + `python3 scripts/dev/verify_r44_zone_event.py build/a032/2_043`. In-game: grass west of bridge fisherman **(576, 184)** → guru at **(568, 183)**.

**Olivine City (verified in-game Sep 2026):**

| Layer | ID | Notes |
|-------|-----|--------|
| Map header | `MAP_T26` = **77** | pret `[MAP_OLIVINE]` |
| zone_event | member **074** (`074_T26`) | **World** coords — pret `eventsBank` |
| scr_seq | member **911** — guru in **slot 13** (scriptId **14**) | Vanilla slots **0–12** (signs, rival, Cameron, …) |
| msg bank | **604** | Vanilla strings **0–8**; guru lines **9–13** |

**How we found the IDs (Olivine)**

1. **Msg bank:** `find_msg_text.py "Olivine City"` / `"Pokégear"` → bank **604** (confirmed in-game on sign + boy).
2. **Map link 604 → 77:** pret `map_headers.h` — `[MAP_OLIVINE].msgBank = NARC_msg_msg_0604_T26_bin`.
3. **zone_event / scr_seq:** same row → `eventsBank = 074`, `scriptsBank = 911` (not header **77**, not member **077**).
4. **Landmarks on `2_074`:** city sign bg **(279, 247)** → scr_seq slot **5** → msg **5**; Pokégear boy **(280, 242)** → scriptId **10** → msg **2**; warps (Poké Center **272, 257**, Full Heal hidden item **285, 231**) confirmed in-game.
5. **Failed attempt:** assumed zone_event member **077** (`MAP_T26` = 77) with **local** coords from a misidentified `2_077` parse — that NARC member is **Ecruteak Gym**, not Olivine. Sprite on **074** at **(277, 247)** was visible only after using the correct member.

**Rod guru:** obj **8**, sprite **347**, world **(273, 248)** by city sign, **`type=0`**, scriptId **14**.

**Patch:** `armips/scr_seq/scr_seq_olivine_rod_guru.s` → `tools/patch_scr_seq_olivine_rod_guru.py` (`2_911`). Zone: `tools/patch_zone_event_olivine_rod_guru.py` (`2_074`). Text: `data/text/604.txt`.

**Verify:** `python3 scripts/build/verify_olivine_rod_guru_scr_seq.py build/a012/2_911` + `python3 scripts/dev/verify_olivine_rod_guru_zone_event.py build/a032/2_074`. In-game: talk to guru west of the “Olivine City” sign → Old Rod flow.

