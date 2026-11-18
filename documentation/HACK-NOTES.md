# Hack notes: what HG-Engine exposes (and what it doesn’t)

Working notes for this fork so we don’t re-discover the text/data layout every session.

**New agent session?** Cursor loads `.cursor/rules/agents.mdc` automatically (build, git, workflow).

## Building `test.nds` (agents)

The user playtests **`test.nds`** at the repo root in DeSmuME — not `build/output.bin`.

| Step | Detail |
|------|--------|
| **Playable ROM** | **`make test.nds -j24`** inside Docker (see [agents.mdc § Agents: always build](../.cursor/rules/agents.mdc#agents-always-build-user-does-not)) |
| **Not enough** | Plain **`make -j24`** runs target **`all`** only (compile + NARCs into `base/`) — **no** `ndstool` repack; **`test.nds` timestamp will not move** |
| **Verify** | Check **`test.nds`** modified time after the build; reload the file in the emulator (close ROM first) |
| **Fast vs slow** | **`make -j24`** ≈ **`all`** (compile/link; often seconds after a small C change). **`make test.nds`** adds **`make.py`**, armips, NARC install, **`ndstool`** — the pack step usually dominates wall-clock time |

```bat
docker run --rm -v "e:/Code/hg-engine:/hg-engine" -w /hg-engine hg-engine make test.nds -j24
```

## Contents

Implementation recipes only — link **to** [DESIGN.md](DESIGN.md) / CHANGELOG / [TODO.md](TODO.md) for context; **design docs do not link** to HACK-NOTES, CHANGELOG, or TODO ([agents.mdc § Design docs](../.cursor/rules/agents.mdc#design-docs-and-agent-boundaries)). **Known bugs:** [TODO.md § Known bugs](TODO.md#known-bugs) symptoms + [§ below](#known-bugs-todomd). **Agents:** `.cursor/rules/agents.mdc`.

| Topic | Section |
| ----- | ------- |
| **Agents: pack `test.nds`** | [Building `test.nds` (agents)](#building-testnds-agents) |
| Mom dialogue discovery | [Why the Mom line was hard to find](#why-the-mom-line-was-hard-to-find) |
| Text / msgenc | [How text editing works](#how-text-editing-works) |
| Important msg banks | [Known `data/text` banks](#known-datatext-banks-tracked--important) |
| What to patch first | [Easy wins vs awkward targets](#easy-wins-vs-awkward-targets) |
| Upstream scope | [Scope reminder (upstream)](#scope-reminder-upstream) |
| Badge coord gates | [Badge gate blocks](#badge-gate-blocks-field-scripting) → [Recipe](#recipe-for-a-new-gate), [Route 46 reference](#route-46-gate-reference-implementation) |
| Route 36 Sudowoodo | [Remove Sudowoodo block (Route 36)](#remove-sudowoodo-block-route-36--verified) |
| Route 32 gate | [Remove Route 32 badge gate](#remove-route-32-badge-gate-south-of-violet--verified-pattern) |
| Gym Cut trees | [Remove Surge / Erika Cut trees](#remove-surge--erika-cut-trees--gym-access) |
| Cut trees (gyms + Ilex + R35) | [Remove Surge / Erika Cut trees](#remove-surge--erika-cut-trees--gym-access) |
| Post-battle heal | [Heal after every battle](#heal-after-every-battle) |
| Gym HM grants | [Gym Leader HM rewards (Johto pilot)](#gym-leader-hm-rewards-johto-pilot) → [Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags), [Fly map (Kanto)](#fly-map--kanto-destinations) |
| Blackthorn Clair | [Blackthorn Gym — Clair (Rising Badge)](#blackthorn-gym--clair-rising-badge) |
| Gym TM choice (Brock) | [Pewter Gym — Brock + Gym TM choice pool](#pewter-gym--brock--gym-tm-choice-pool-prototype) |
| Interim EXP | [Full party EXP share (interim)](#full-party-exp-share-interim) |
| Trainer scaling | [Trainer level scaling](#trainer-level-scaling) |
| Player level cap | [Player badge level cap & Rare Candies](#player-badge-level-cap--rare-candies) |
| Paid ferries | [Paid ferry / local bypass NPCs](#paid-ferry--local-bypass-npcs-reusable-recipe) → [Route 42](#route-42-reference-verified), [Route 40 / Cianwood](#route-40--cianwood-reference-verified), [Route 31 / Route 45](#route-31--route-45-dark-cave-reference) |
| Mahogany Rocket | [Skip Mahogany Rocket arc](#skip-mahogany-rocket-arc--post-clear-town-on-load) |
| Story NPC removal | [Removing / skipping story NPCs](#removing--skipping-story-npcs-reusable-recipe) |
| Accelerated game clock ([World-9](DESIGN-WORLD.md#world-9-accelerated-daynight-cycle)) | [30-minute days (48× RTC)](#accelerated-game-clock) |
| Apricorn trees / new OW gfx | [Apricorn & custom overworld graphics (Future-1)](#apricorn--custom-overworld-graphics-future-1) |
| Mom intro / start city | [Open-world starting inventory](#open-world-starting-inventory-new-saves) → [Starter menu](#starter-selection--not-choose_starter), [Home warps](#home--bidirectional-door--interior-swap) |
| Story flag sweep (dev) | [Story flag range sweep (dev)](#story-flag-range-sweep-dev) |
| HGSS story flags (pret) | [HGSS-STORY-FLAGS.md](HGSS-STORY-FLAGS.md) — index **100–399**; add Wandering Heart notes as we map skips |
| Magnet Train | [Magnet Train (Goldenrod ↔ Saffron)](#magnet-train-goldenrod--saffron) |
| Route 4 hiker boost | [Route 4 ledge boost](#route-4-ledge-boost-cerulean--mt-moon) |
| Jasmine medicine | [Olivine Secret Medicine (Jasmine)](#olivine-secret-medicine-jasmine) |
| Mart inventories | [Mart expansion (`src/field/mart.c`)](#mart-expansion-srcfieldmartc) → [KB-18](#kb-18--saffron-mart-second-clerk-vanished) |
| Trade-item evolution | [Trade-item evolution (use on Pokémon)](#trade-item-evolution-use-on-pokémon) |
| Game Corner TMs | [Game Corner TM prizes](#game-corner-tm-prizes) |
| Overlay 129 (32 KiB) | [Overlay 129 — engine code budget](#overlay-129-32-kib-engine-overlay) |
| Wild distance caps | [Wild level caps (distance-based)](#wild-level-caps-distance-based--verified-poc) → [Formula](#formula-and-table), [Runtime](#runtime-pipeline), [Synthetic edges](#editing-synthetic-stage-edges) |
| Wild ecology shuffle ([Wilds-6](DESIGN-WILDS.md#wilds-6-per-save-wild-ecology-shuffle)) | [Per-save ecology](#per-save-wild-ecology-shuffle-wilds-6) → [ROM PoC](#ecology-rom-integration-in-rom-poc), [Files](#ecology-file-shorthand), [Mom gen / overlay 131](#mom-gen-overlay-131-vs-host-ecologygen), [Encounter hooks (KB-12)](#kb-12--wild-ecology-encounter-hooks-setencountdata), [129↔131 (KB-11)](#kb-11--undefined-instruction-from-overlay-129--field-code-calls), [Mom freeze (KB-14)](#kb-14--mom-ecology-gen-freeze-overlay-131-compat-pointer) |
| DSPRE / map IDs | [World placement (DSPRE)](#world-placement-dspre) |
| Fishing gurus | [Fishing Rod guru NPCs](#fishing-rod-guru-npcs) |
| Map header vs NARC indices | [Field map IDs](#field-map-ids-dont-mix-them-up) |
| Known bugs | [Known bugs (TODO.md)](#known-bugs-todomd) |

## Known bugs (TODO.md)

Symptom list: [TODO.md § Known bugs](TODO.md#known-bugs). Implementation detail lives below (and in related recipe sections).

### KB-2 — Post-battle return to field crash

**Status (Oct 2026):** **removed from [TODO.md](TODO.md#known-bugs)** — no longer repro on step-heal ([Heal after every battle](#heal-after-every-battle)). **Latent** if heal moves back into battle teardown.

**Was:** heal during `Battle_End` party sync → crash / party corruption; overlay-12 hook experiments made it worse ([Heal § failed attempts](#heal-after-every-battle)). **Bisect:** `HEAL_AFTER_BATTLE` off in `include/config.h`.

### KB-3 — Cherrygrove guide cutscene

**Symptom:** Town Map / running-shoes tutorial cutscene still runs; guide NPC invisible (hidden on new saves via Mom intro flag sweep).

**Design:** [TODO.md — Cherrygrove guide](TODO.md#superseded-by-mom-cutscene--starting-grants).

**Fix direction:** skip or nop guide **coord / trigger scripts**, not only `FLAG_HIDE_CHERRYGROVE_GUIDE_GENT`.

### KB-4 — Slowpoke Well Rocket grunt

**Symptom:** at least one Team Rocket grunt still blocks Slowpoke Well entrance on some new saves despite Azalea rocket skips.

**Design:** [Story-3 — Team Rocket](DESIGN-STORY.md#team-rocket--remove).

**Partial work:** `openworld_story_skip_flags.inc`, `tools/patch_scr_seq_t23_azalea.py` (scr_seq member **866**), `tools/patch_zone_event_t23_azalea.py` (zone_event **071** — remove well entrance obj **0** @ **434,461**).

### KB-6 — Seated Mom dialogue after intro

**Symptom:** after open-world intro, talking to seated Mom shows garbled dialogue or wrong menus (vanilla Elm-fetch flow).

**Design:** [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home), [Story-2](DESIGN-STORY.md#story-2-starter-pokémon-and-intro-flow).

**Related recipe:** [Open-world starting inventory](#open-world-starting-inventory-new-saves) — only script slot **0** rebuilt; scr_seq **845** other slots + **545** text remap may not match sitting-script branches.

### KB-10 — Surf wild encounters (wrong species)

**Symptom ([TODO.md](TODO.md#known-bugs)):** Surf showed wrong species (e.g. **Cetoddle**) or crash-on-catch **`"---"`** mon.

**Status (Oct 2026):** **Re-test on Wilds-6** — grass/surf/fish/headbutt share **`SetEncountData_Ecology`** ([KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata)). Surf NARC tables were always vanilla; old bug was hook/scratch path, not `Encounters.c`.

**If wrong species return:** separate from KB-12; check ecology assignment + `verify_encount_overlay2.py`. **Cap debug level 5 everywhere** = `encBank == NA` on bad `mapId` — see [debug toggles](#debug-toggles-turn-off-for-normal-play) and `sWildLevelCapDebug` @ **`0x021FF910`** ([runtime pipeline](#runtime-pipeline)).

### KB-11 — Undefined instruction from overlay 129 → field **code** calls

**Symptom:** `ARM9: Undefined instruction` with PC in overlay **129** (`0x023D8xxx`) or garbage; often **first wild** after new game, or during **Mom intro** if 129 calls field overlay **131** functions.

**Cause:** Overlays **129** and **131** share overlapping ARM9 load windows ([memory map](#memory-map-arm9)). **`patch_level_up_evo_addrs.py`** is for **read-only field rodata** only. Patching a pointer to a **function** in 131 and calling it from 129 while 131 is unloaded executes non-code.

**Fix (verified Oct 2026):** **`src/wild_berry_hold.c`** lives in overlay **129** (`WildMonSetRandomHeldItem_hook`, `WildMonApplyHeldItemForEncounter`). Species held **tables** stay in **`src/field/wild_species_held_items.c`**; 129 uses patched **`WildSpeciesHeldCommonFieldAddr`** / **`WildSpeciesHeldRareFieldAddr`**. **`TryApplyWildEncounterHeldItem`** in `src/wild_level_caps.c` calls the 129 helper directly — do **not** use **`WildMonApplyHeldItemFieldAddr`**. Field **`AddWildPartyPokemon`** uses ARM9 **`WildMonSetRandomHeldItem`** → hook in 129.

**Verify after link:** `python3 scripts/dev/verify_overlay129_field_addrs.py` (Docker). **`build/output.bin`** is patched after **`build/field_linked.o`** and **`build/linked.o`** exist (`Makefile` `$(OUTPUT)` rule; also `make.py` `writeall()`).

**Rule:** Hot-path **logic** on the wild hook belongs in **`src/`** (129); do not assume 131 is loaded merely because a patched pointer exists. Field-service exception: the synchronous Apricorn dispatcher checks `IsOverlayLoaded(131)` before calling its patched entry, never loads/unloads overlays or yields inside the call, and returns unavailable with zero outputs when the entry or overlay is absent.

### KB-12 — Wild ecology encounter hooks (`SetEncountData`)

**Symptom:** Grass/surf/fish crashes on first wild; wrong species; **100% crash** after removing a `SetEncountData` hook from `hooks` while `base/overlay/overlay_0002.bin` still contains a trampoline.

**Historical baseline (Oct 2026):** commit **`fae496a1f`** — grass-only via **`EcologyScratchSetActiveMethod`** + **`modify_species` @ `7B42`** (no **`7B64`** hook). **Current Wilds-6:** **`SetEncountData_Ecology` @ `7B64`** for all hooked methods; **`modify_species` @ `7B42`** remains for any **`EncountParamSet`** path that still runs vanilla slot setup.

**Overlay 2 sites (US HeartGold, field overlay load ~`0x02245B80`):**

| VMA | Role | Baseline |
|-----|------|----------|
| **`0x02247B64`** | **`SetEncountData`** entry | **Unhooked:** must match **`rom.nds`** overlay 2 extract (pret US ref `04 2c f7 db 38 1c 01 21` if input ROM is retail **IPKE**) |
| **`0x02247B42`** | Tail of **`EncountParamSet`** | **Hook** (register **r3**) → overlay **129** `modify_species_encounter_data` — **not** a wrapper; bytes **`7B42–7B4B`** are replaced, then **`bx`** resume @ **`0x02247B4C`** |

**`hooks` vs `base/overlay`:** `scripts/build/make.py` only **writes** addresses listed in **`hooks`**. It does **not** restore bytes when a line is removed. A leftover **`ldr r3; bx r3`** @ **`7B64`** (same target as **`7B42`**) makes every **`SetEncountData`** jump into **`modify_species`** with the wrong stack/regs → **guaranteed crash**. After any hook experiment: **`make clean`** (re-extract from **`rom.nds`**) or restore **`7B64`** manually, then **`make test.nds`**.

**Strategies tried (do not repeat without fixing root cause):**

| Approach | Result |
|----------|--------|
| **`EcologyScratchSetActiveMethod` only in `WildEncSingle`** | **Grass OK** on baseline; **surf/fish/headbutt/smash** never set method — **`WildWaterEncSingle` clears scratch** (`EcologyActiveMethodRef = 0`) |
| Pending scratch + consume @ **`modify_species`** (`r7`, `[sp,#0x14]`) | Unreliable enc type; intermittent wrong mon |
| **`SetEncountData` C “wrapper”** calling **`0x02247B6C`** | Skips prologue/slot loop — crashes + wrong **`PartyPokemon`** |
| Asm tramp into **`0x02247B58` / `7B6C`** | **100% crash** — not a function entry |
| Stale **`7B64`** stub after removing hook from **`hooks`** | **100% grass crash** until overlay bytes restored |
| **`ldr r0; bx r0` @ `7B64`** (hook register **0**) | **`r0` = `pp` at entry** — clobbered with jump target → undefined instruction @ **`SetEncountData_Ecology`** / garbage **`PartyPokemon`** |

**Chosen architecture (Wilds-6):** **`WildEncounterFinalize`** / **`WildEncounterFinalizeForEncount`** (`src/wild_encounter_finalize.c`); **`SetEncountData_Ecology`** @ **`0x02247B64`** (`src/setencount_ecology.c`, **`hooks`**) — placeholder **`PokeParaSet`** (**Wooloo**, level **5** — obvious dev stub; **`WildEncounterFinalizeForEncount`** replaces species from ecology), then **`PokeParty_Add`**. A vanilla-looking first mon before finalize meant ecology was broken; Wooloo makes “still placeholder” obvious. **`modify_species` @ `7B42`** remains for any **`EncountParamSet`** path not via this stub. **Do not** tail-call **`0x02247B6C`**. **`7B64` hook:** use **`hooks`** bl stub (no register field — **255**), **not** `ldr r0; bx` — **`r0`–`r3` are live `SetEncountData` args at entry** (`pp`, rod, encInfo, encArea).

**Verify after `make test.nds`:**

```bash
python3 scripts/dev/verify_encount_overlay2.py
```

With **`IMPLEMENT_ECOLOGY_GENERATION`**, expect **`7B64` → `SetEncountData_Ecology+1`**; otherwise **`7B64` = `rom.nds` extract**. **`7B42`** → **`modify_species_encounter_data+1`**. Mismatch **`base/overlay` ≠ rom.nds** (unhooked) → **`make clean && make test.nds`**.

**Related:** [Runtime pipeline](#runtime-pipeline), [ROM integration (Wilds-6)](#rom-integration-wilds-6), [KB-10](#kb-10--surf-wild-encounters-wrong-species) (surf species / scratch clear), [KB-19](#kb-19--wild-shiny-sparkle-vs-caught-mon) (fixed).

### KB-14 — Mom ecology gen freeze (overlay 131 compat pointer)

**Status (Nov 2026):** **Fixed** — **`src/field/ecology_generate.c`** sets **`sEcoGenCompatView = view`** in overlay **131** and routes gen **`ECO_*`** macros through that pointer (not **`gEcologyCompatView`**). Required-route loop capped at **`ECOLOGY_NUM_REQUIRED_ROUTES`**.

**Symptom:** New game → Mom intro → message about generating Pokémon ecology → **hard freeze** (no wilds yet — **`DEBUG_ECOLOGY_GEN_LEVELS`** on wild level is useless until gen finishes).

**Not the cause (verified Oct 2026):** Overlay **131** size — **`wc -c build/output_field.bin`** was **~39 KiB** vs linker **`0x18000` (96 KiB)** after the Required-on-Route / Pairing gen rewrite. **No new `src/` ROM files** in that merge (only **`documentation/ecology.md`** added).

**Host vs ROM:** **`tools/ecologygen`** links the same **`src/field/ecology_generate.c`** with **`-DECOLOGY_STANDALONE`** and static **eco-host-csr** — assignment completes in **~30 ms** on PC. A ROM-only bug will **not** show up as slow host **ecologygen**.

**Regression (commit `12900633` vs parent `80aa029b3`):** Gen in overlay **131** was switched from **`sEcoGenCompatView = view`** (local pointer set from the **`view`** argument) to **`ecology_compat_access.h`** macros that read **`gEcologyCompatView`** globally, while **`(void)view`** discards the parameter.

| Path | Compat tables |
|------|----------------|
| **129** `ecology_script.c` | Binds NARC blob → **`gEcologyCompatView`**, calls **`fn(gEcologyCompatView, seed, …)`** via **`EcologyGenerateWorldFieldAddr`** |
| **131** `EcologyGenerateWorld` (broken) | Ignores **`view`**; all **`ECO_*`** macros dereference **`gEcologyCompatView`** (extern living in **129** image) |
| **131** (working pattern) | **`if (view == NULL) return FALSE;`** then **`sEcoGenCompatView = view;`** — macros use **`sEcoGenCompatView`**, not the global |

If **131** reads a **NULL / stale / garbage** global while **`view`** is valid, behavior ranges from instant **`FALSE`** to **de facto infinite work** (garbage **`landOffsets`** / **`numRequiredRoutes`**). Latest adds **`EcologyAssignRequiredRoutes`**, which loops **`ECO_REQUIRED_ROUTE_COUNT`** (= **`gEcologyCompatView->numRequiredRoutes`**) with **no iteration cap** — parent had no required-route phase.

**Fix (shipped):** **`static const EcologyCompatView *sEcoGenCompatView`**, **`sEcoGenCompatView = view`** at gen entry, local **`ECO_*`** macro overrides in **`ecology_generate.c`**. Do **not** revert to **`gEcologyCompatView`** inside overlay **131**.

**Related:** [Mom gen — overlay 131 vs host](#mom-gen-overlay-131-vs-host-ecologygen), [KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls) (wild hook must not call **131** code; Mom **function pointer** to **`EcologyGenerateWorld`** is a separate, patched path).

### KB-16 — Encounter moves not rebuilt after species/level change

**Status:** **Fixed** — **`ClearMonMoves`** immediately before **`InitBoxMonMoveset`** on wild finalize and scaled trainer parties (user-tested Nov 2026).

**Was:** Pokémon kept **stale move slots** after species or effective level changed — moves **stacked** instead of matching the final species at battle level.

| Source | Example |
| ------ | ------- |
| **Wild (ecology)** | Low-level wilds knew **Growl** and **Tackle** **plus** the rolled species’ moves — **Wooloo** stub (**`WILD_PLACEHOLDER_LEVEL` 5** in `src/setencount_ecology.c`) left placeholder moves in occupied slots. |
| **Trainers (scaling + devolve)** | Sabrina slot authored **Alakazam** L55; after **`TRAINER_SPECIES_STAGE_ADJUST`** the slot could be **Abra** but still know **Psybeam** from the pre-adjust **`PokeParaSet`** learnset. |

**Cause:** Vanilla **`InitBoxMonMoveset`** (ARM9 `0x020712D8`; learnset table patches in `armips/asm/levelup.s` only) walks the level-up table and **adds** each legal move into the **first empty** slot (`MOVE_NONE`). It does **not** clear existing slots — so leftover moves from an earlier species or stub **`PokeParaSet`** persist.

| Path | Pipeline |
| ---- | -------- |
| **Wild** | [KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata) — **`PokeParaSet`(`SPECIES_WOOLOO`, L5)** → **`WildEncounterFinalizeForEncount`** → **`ClearMonMoves`** → **`InitBoxMonMoveset`** (`src/wild_encounter_finalize.c`) |
| **Trainer** | **`PokeParaSet`(authored species, scaled level)** → … → **`ApplyEncounterStageAdjustToMon`** → **`ClearMonMoves`** → **`InitBoxMonMoveset`** (`src/field/enemy_party.c` when **`TRAINER_LEVEL_APPROPRIATE_MOVES`**) |

**Fix:** Call **`ClearMonMoves`** (`src/pokemon.c` — zeros four move IDs; same pattern as egg scripts in `src/field/script_commands.c`) before **`InitBoxMonMoveset`**. PP is set when moves are added; no need to extend **`ClearMonMoves`**.

**Verify:** Ecology grass — no **Growl**/**Tackle** unless the species learns them. Low-badge Sabrina — devolved psychics only know **`learnsets.json`** moves at slot level.

**Related:** [Trainer level scaling](#trainer-level-scaling), [Runtime pipeline](#runtime-pipeline), [KB-13](#kb-13--kb-17--wild-encounter-overwrote-the-party-lead-fixed) (lead overwritten by wild — fixed). Optional follow-up: drop Wooloo stub and **`PokeParaSet`** final species directly ([Per-save ecology](#per-save-wild-ecology-shuffle-wilds-6)).

### KB-13 / KB-17 — Wild encounter overwrote the party lead (fixed)

**Status (Nov 2026):** **Fixed**, pending playtest ([TODO § Needs testing](TODO.md#needs-testing)).

**Symptoms:**

- **KB-13:** after a wild (fishing) battle the **lead party slot** became the wild species (e.g. Bulbasaur → Tentacool).
- **KB-17:** held items "duplicated" after wild battles (first misfiled as Game Corner prize quantity). Later builds: the wild's held item ended up on the lead and the player's own item went to the bag, even when fleeing turn 1.

**Root cause:** vanilla **`SetEncountData`** (overlay 2 **`0x02247B64`**) receives the player's **save-party lead** as its first argument — **read-only**, for ability checks (Static, Magnet Pull, Cute Charm). Vanilla builds the wild in its own buffer (**`EncountParamSet`**: **`AllocMonZeroed(11)`** → **`AddWildPartyPokemon`** → **`sys_FreeMemoryEz`**). **`SetEncountData_Ecology`** treated that pointer as the wild buffer, so **`PokeParaSet`** + finalize (species, level, held item) overwrote the save lead. Usually invisible: the battle setup party is copied from the save **before** this call and copied back **after** battle. Anything reading the save party mid-battle saw the wild instead — including the **`RESTORE_ITEMS_AT_BATTLE_END`** start snapshot in **`ServerInit`**, so the reconcile treated the wild's item as the player's.

**Fix:**

| File | Change |
| ---- | ------ |
| `src/setencount_ecology.c` | Build the wild in **`AllocMonZeroed(HEAPID_WORLD)`**, **`PokeParty_Add`**, free; never write the lead pointer |
| `src/battle/battle_pokemon.c` | **`BattleEndReconcilePlayerHeldItems`**: start = save party at **`ServerInit`**; end + writes = battle party (**`BattleWorkPokemonParamGet(bw, 0, i)`**) — the copy vanilla syncs back after the hook. Per slot: same → no change; different → bag loot (wild-only when **`BATTLE_END_BAG_STOLEN_HELD_ITEMS_WILD_ONLY`**), clear, re-equip start item |

**Pitfalls:**

- The **`Battle_End`** hook runs **before** vanilla copies battle parties → setup (`0x022384D6` loop). Writes to the **save** party there are overwritten later; write the **battle** party.
- Don't snapshot via **`BattleWorkPokemonParamGet`** in **`ServerInit`** — battle work isn't ready (battle-start undefined-instruction crash).

**Related:** [KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata), [Per-save ecology](#per-save-wild-ecology-shuffle-wilds-6).

### KB-18 — Saffron Mart second clerk vanished

**Status (Nov 2026):** **Fixed**, playtested — removed from [TODO.md](TODO.md#known-bugs). Cause was `tools/patch_zone_event_violet_gym.py` deleting obj **3** / script **2** on member **365**, which is this mart, not Violet Gym (member **131**). That patch is gone. `scripts/dev/verify_saffron_mart_clerks.py` fails the zone-event build if either clerk object is missing.

**Was:** Inside **Saffron City’s Poké Mart**, the **second teller** (specialty clerk — Up-Grade, Dubious Disc, Twisted Spoon, Payapa Berry) was **gone**. The main clerk still opens the badge-tier **`ScrCmd_MartBuy`** list.

**Design:** [World-6 § Shops](DESIGN-WORLD.md#world-6-shops) — Saffron specialty line matches **`sSaffronMart[]`** in **`src/field/mart.c`**.

**IDs (retail HGSS naming):**

| What | Value |
| ---- | ----- |
| Map header | **`MAP_T11FS0101`** (**409**) |
| Zone event member | **365** (`build/a032/2_365`) — not the map header |
| scr_seq NARC member | **409** (`build/a012/2_409`), slot **1** — `setvar VAR_SPECIAL_x8004, 15` then `std_special_mart` |
| Specialty inventory | **`sSaffronMart`** — repoint index **15** (`repoints` @ `0210FA78`) |

**Verify:** Saffron Mart → **two** clerks at the counter → second opens Up-Grade, Dubious Disc, Twisted Spoon, Payapa Berry. Violet Gym elevator and hidden guide unchanged (scripts still on scr_seq **859**; zone **131** untouched).

**Related:** [Mart expansion](#mart-expansion-srcfieldmartc), [Violet Gym](#violet-gym-falkner--859--zone_event-131).

### KB-19 — Wild shiny sparkle vs caught mon

**Status (Nov 2026):** **Fixed** — removed from [TODO.md](TODO.md#known-bugs). **`WildEncounterApplyPlayerOtId`** in **`src/wild_encounter_finalize.c`** sets **`MON_DATA_OTID`** to **`Sav2_PlayerData_GetProfileAddr` → `profile->id`** after level/gender finalize so battle and post-catch **`MonIsShiny`** use the same OTID + PID (vanilla catch no longer re-stamps OT onto OTID **0** rolls).

**Was:** Wild **`PokeParaSet`** used OTID **0**; sparkle in battle could disagree with party after catch.

### KB-20 — Wild encounter crash (single-tester report)

**Resolved (Nov 2026) — emulator setting, not a ROM bug:** the tester fixed it by changing DeSmuME **Config → 3D Settings → 3D Rendering Engine** from **SoftRasterizer** to **OpenGL 3.2**. Removed from [TODO.md](TODO.md#known-bugs). If a wild-encounter crash is reported again, ask for the renderer setting first. Original notes below.

**Symptom:** Hard **crash** when entering a **wild** encounter (grass step, surf, rod, headbutt, rock smash — exact method **unconfirmed**). Tester sees immediate freeze or emulator exception; developer **cannot reproduce** on the same shipped **`test.nds`** after retest.

**Status:** **Open / unconfirmed** — one external report only. Treat as **possible** environment, stale ROM, or save-specific corruption until a second repro or exception PC is captured. Do **not** assume ecology is broken globally ([KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata) regressions were historically **100%** on first wild).

**Repro (when available):** New save vs continued save → note map, time of day, encounter method → trigger wild → note whether crash is **before** battle fade, **during** send-out, or **after**. Compare DeSmuME vs other emulators only if tester used non-default build.

**Collect from reporter (minimum):**

| Item | Why |
| ---- | --- |
| **`test.nds` file date** (or commit hash if known) | Stale ROM vs current tree |
| **Emulator + settings** (especially **Advanced → Exceptions → Break on** in DeSmuME) | Undefined-instruction vs data abort |
| **New save vs old save** + **party** (species, eggs, full?) | [KB-13](#kb-13--kb-17--wild-encounter-overwrote-the-party-lead-fixed) party slot corruption can surface oddly |
| **Map / route**, **badges**, **lead Pokémon** | Wild level cap + ecology assignment vary by progress |
| **Ecology gen finished?** (Mom intro line completed without freeze — [KB-14](#kb-14--mom-ecology-gen-freeze-overlay-131-compat-pointer) was fixed Nov 2026) | Incomplete / corrupt ecology flash |
| **Exception PC** (ARM9 address) if DeSmuME breaks | **`0x023D8xxx`** → overlay **129** ([KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls)); **`0x02247xxx`** → overlay **2** encount hooks ([KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata)) |

**Likely buckets (bisect only after repro):**

| Bucket | Clues |
| ------ | ----- |
| **Overlay / hook** | Undefined instruction @ **129** or **2**; verify `python3 scripts/dev/verify_encount_overlay2.py` and `verify_overlay129_field_addrs.py` on the **built** tree |
| **Invalid mon data** | Wrong species id, broken form, or dex sprite path — compare [KB-10](#kb-10--surf-wild-encounters-wrong-species) **`"---"`** / corrupt name cases |
| **Save-only state** | Same ROM + new save OK, old save crashes → export save for local replay |
| **One-off emulator** | Single tester, zero dev repro — hardware/renderer edge case; still log emulator version |

**Fix direction (open):**

1. **Reproduce** with reporter save + ROM hash; if impossible, downgrade severity or close when no second report across N builds.
2. On break: map PC to symbol (`hooks`, overlay 129/2, **`SetEncountData_Ecology`**, **`modify_species_encounter_data`**).
3. Rule out stale **`base/overlay/overlay_0002.bin`** / wrong **`7B64`** stub ([KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata)) on **tester’s** build artifact.

**Verify after fix:** Same save + map that crashed → wild battle completes; smoke grass + surf + one rod tier on new save.

**Related:** [KB-9](TODO.md#known-bugs) (Mahogany exit — intermittent crash pattern), [KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls), [KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata), [KB-13](#kb-13--kb-17--wild-encounter-overwrote-the-party-lead-fixed), [Runtime pipeline](#runtime-pipeline).

---

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

## Field map IDs (don’t mix them up)

Every map uses **separate indices** from pret [`map_headers.h`](https://github.com/pret/pokeheartgold/blob/master/src/data/map_headers.h):

| Index | NARC / path | Fork override |
|-------|-------------|---------------|
| **Map header** | `include/constants/maps.h` (`MAP_*`) | — |
| **`eventsBank`** | `a/0/3/2` member `NNN` | `data/zone_event/NNN_<MAP>.json` |
| **`scriptsBank`** | `a/0/1/2` member | `armips/scr_seq/scr_seq_<NNNN>_<MAP>.s` |
| **`msgBank`** | msgdata `a/0/2/7` | `data/text/<bank>.txt` |

**Gotchas:** header id ≠ any member (Route 32 header **36** → zone_event **033**, scr_seq **232**). **`eventsBank` 077** = Ecruteak Gym, not Olivine header **77**. Walkable Route 44 = zone_event **043**, not pret `046_R44`. Wrong scr_seq member sticks in `base/root/` until re-extract from `rom.nds`. Find indices: pret filenames, [World placement (DSPRE)](#world-placement-dspre), `scripts/dev/find_zone_event_member.py`, `scripts/local/_scan_zone_events.py`.

## Badge gate blocks (field scripting)

Reusable pattern: walk-past coord trigger → script checks badge count → message + step player back, or pass through if requirement met.

**IDs:** [Field map IDs](#field-map-ids-dont-mix-them-up) — Route 46 gatehouse: header **134**, scr_seq **226**, zone_event **130** (we once patched scr_seq **134**, a dungeon, by mistake).

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
4. **Build** — Docker `make test.nds -j24` → test in `test.nds`

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

## Remove Sudowoodo block (Route 36) — verified

**Goal:** walk Violet ↔ Goldenrod / Ecruteak with **0 badges**; Sudowoodo never blocks the path. **Tested in-game:** tree hidden on first Route 36 visit (new save).

### Wiring (pret decomp)

| What | ID / symbol |
|------|-------------|
| Map header | `MAP_R36` = **40** |
| zone_event member | **037** (`037_R36.json`) |
| Sudowoodo object | `obj_R36_usokky` |
| Hide flag | `FLAG_HIDE_ROUTE_36_SUDOWOODO` (**450**) |

Mom intro (`scr_seq_t20_mom_script0.s`) **`setflag FLAG_HIDE_ROUTE_36_SUDOWOODO`** with other world-clearance flags — before the player can reach Route 36. Route 36 scr_seq stays vanilla.

**Option B (fallback):** remove `obj_R36_usokky` from `037_R36.json` if the flag alone leaves collision (not needed — Mom flag sufficient).

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

| File | Role |
|------|------|
| `tools/patch_zone_event_r32_badge.py` | Remove blocker NPC, barriers, coord trigger |
| `tools/patch_scr_seq_r32_badge.py` | OnLoad sets flags **550/552**; NOP walk-past/coord/talk scripts |
| `narcs.mk` | Hook after scr_seq / zone_event extract |

**Test checklist:** new save → leave Violet south → no NPC stop, path walkable toward Ruins/Union Cave.

---

## Remove Surge / Erika Cut trees — gym access

**Status:** verified in-game (Aug 2026). 0 badges, no Cut — Vermilion Gym door, Celadon Gym door, and Erika inside Celadon Gym all reachable.

**Goal:** reach Vermilion and Celadon Gyms (and Erika inside her Gym) without Cut — [Story-3](DESIGN-STORY.md#story-3-story-and-script-policy).

| Map | zone_event member | Trees removed |
|-----|-------------------|---------------|
| Vermilion City | **051** → `2_051` | 1 outside Gym |
| Celadon City | **052** → `2_052` | 1 outside Gym |
| Celadon Gym | **352** → `2_352` | 3 inside maze |
| Ilex Forest (`D36R0101`) | **114** → `2_114` | 1 @ **(16, 62)** — header **117** ≠ eventsBank **114** |
| Route 35 (`MAP_R35` = **39**) | **036** → `2_036` | 1 @ **(380, 265)** — optional; `tools/patch_zone_event_r35_cut_tree.py` |

Cut trees are `SPRITE_TREE` (86) + `std_field_cut` (script 10000) objects — **not** Blender map geometry.

| File | Role |
|------|------|
| `tools/patch_zone_event_gym_cut_trees.py` | Strip matching tree objects from the members above (incl. Ilex `2_114`) |
| `narcs.mk` | Hook after zone_event extract |

Surge Gym interior keeps the trash-can puzzle (no cut trees there).

**Verified:** new save, 0 badges, no Cut mon — Vermilion/Celadon gym doors; Ilex Forest Route 34 ↔ 35; optional Route 35 outdoor tree.

---

## Heal after every battle

**Status:** **workaround shipped** — full party heal on **every overworld step** (`PlayerStepEvent_RepelCounterDecrement`); user-tested stable on DeSmuME and phone emulator (Oct 2026). Not design-perfect; target is **post-battle** apply ([Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes), [Battle-1](DESIGN-BATTLES.md#recovery)).

**Design:** [Battle-1](DESIGN-BATTLES.md#recovery) — full HP/PP/status restore after every battle (wild, trainer, flee; no special exclusions).

| What | Where |
|------|--------|
| Toggle | `HEAL_AFTER_BATTLE` in `include/config.h` (enabled by default; comment out to disable) |
| Form / items hook | `Battle_End` @ overlay 12 **`0x0B90`** → `BattleEndRevertFormChange` only (no heal in battle overlay) |
| Heal impl | `src/heal_after_battle.c` → **`build/linked.o`** (ARM9 extension, same link unit as `src/repel.c`); **`PokeParty_GetPokeCount`** + **`Party_GetMonByIndex`** + **`MON_DATA_SPECIES_EXISTS`**; HP/status as **`u16`** |
| Field apply | **`HealAfterBattle_HealPartyOnFieldStep(saveData)`** — pass **`saveData` from the step hook**, not `gFieldSysPtr->savedata` |
| Logic | Nurse Joy–equivalent: max HP, clear status, `RestoreBoxMonPP` |

**Step-heal limitations (why we still want end-of-battle):**

- Party stays injured on the field until the **first full step** — follower sprite/order can lag (e.g. lead fainted in battle) until party menu refresh.
- **Turn-in-place** (no step) can enter another battle without heal.
- **Back-to-back trainer chains** at one tile can run multiple fights with no step between.
- A **pending heal flag** in ARM9 scratch (near wild-cap scratch @ **`0x021FF940`**) was tried; apply-on-step/menu was flaky — not shipped; step heal runs unconditionally each step when the toggle is on.

**Oct 2026 — party corruption (“Bad Eggs”):** iterating **`party->members[i]`** or using **`party->count`** instead of **`Party_GetMonByIndex`** / **`PokeParty_GetPokeCount`** caused **`SetMonData`** on wrong memory — checksum failures, Bad Eggs in slots 1+, possible **`LDMIA with Empty Rlist`** on later battles. **Corrupted saves are not repaired by a fixed ROM**; test on a new save.

**Agent notes (do not repeat without new evidence):**

| Attempt | Result |
| -------- | ------ |
| Pending flag + heal on `StoreFieldSysPtr` (ARM9) | **Crash before fade** if pending is set — heal during `Battle_End` party sync. Do not call heal from `StoreFieldSysPtr`; preserve **`r0`** if adding other logic there. |
| Pending flag + heal on step/menu only | Stable but heal often **did not run** (flag/trigger/save pointer issues). |
| Overlay 12 hook @ **`0xEB6`** (any stub) | **Crash before fade** — 8-byte patch clobbers post-`pop` insns; bad branch (e.g. PC **`0x021E3FA0`**, undef **`0x0100091F`**). On a dirty tree, re-extract overlay 12 from **`rom.nds`** or patch vanilla bytes back @ **`0xDE8` / `0xEB6`**. |
| `HealAfterBattle_*` C from battle overlay @ `Battle_End` | **Crash** — do not `bl` save/party code from overlay 12/130 stubs. |
| Heal in `BattleEndRevertFormChange` / start of `Battle_End` | No lasting heal — vanilla overwrites save party after sync. |
| Heal on `UnloadOverlayByID(OVERLAY_BATTLE)` | No heal — path did not run reliably in testing. |
| `WIPE_SYS_EndCheck` hook | **Load/overworld crash** — do not skip first 8 bytes of vanilla; restore @ **`0x0200FB5C`**. |
| Second hook @ overlay `080011A2` (“end of `Battle_End`”) | **Battle-start crash** — site is not battle-end-only. Removing the hook from `hooks` **does not** revert bytes in `base/overlay/overlay_0012.bin`. |
| Heal every step (safe iteration) | **Works** for HP/PP/status; see limitations above. |

**If [KB-2](#kb-2--post-battle-return-to-field-crash) or heal regressions return:** bisect with `HEAL_AFTER_BATTLE` off in `config.h`. For **battle-start** crash after overlay experiments, re-extract overlay 12 from `rom.nds` (preferred) or restore 10 vanilla bytes @ `080011A2` through `080011AB`. Helper: `python scripts/local/check_overlay12_hook.py`. For **end-of-battle** heal, use a **verified** hook after vanilla party sync (decomp/xref) — not another guessed offset; consider vanilla **`heal_party`** scr cmd **282** or decomp heal helper instead of hand-rolled `SetMonData` loops.

**Files:** `include/heal_after_battle.h`, `src/heal_after_battle.c`, call from `src/repel.c`. No overlay-12 heal hook in **`hooks`**.

**`bytereplacement` (repo tool):** at pack time, **`scripts/build/make.py`** writes literal hex bytes into **`base/arm9.bin`** or **`base/overlay/overlay_NNNN.bin`** (see [DS code injection — bytereplacement](https://ds-pokemon-hacking.github.io/docs/generation-iv/guides/hgss-code_injection/#bytereplacement)). Used elsewhere in this fork for table sizes and hook stubs. **Not part of the shipped step-heal fix** — only needed if you experimentally patched overlay 12 / WIPE and need to undo bytes without a full **`make restore_build`**.

---

## Gym Leader HM rewards (Johto pilot)

**Status (Nov 2026):** all **16** Leaders playtested — badge, level-cap line, HM or mart mention, TM choice, and rematch. **Morty**’s pre–Burned Tower elder line is still blank ([KB-8](TODO.md#known-bugs)). Whitney’s first win still cries and withholds the badge; the reward block runs on the talk after the chase.

**Design:** [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Battle-3](DESIGN-BATTLES.md#first-defeat-rewards) — after badge fanfare, grant field ability by **`count_badges`** (any-order Gyms), then TM. **Flash / Headbutt not implemented yet** (badge rows 1 and 4 grant badge + TM only). Headbutt battle teach needs a **custom TM** (not in vanilla); see [World-3 § Headbutt & Flash](DESIGN-WORLD.md#headbutt--flash--battle-teaching-vanilla-vs-target).

| What | Where |
|------|--------|
| Toggle | `GYM_BADGE_COUNT_FIELD_REWARDS` in `include/config.h` |
| Field HM use | `OPENWORLD_FIELD_MOVES_NO_BADGE_GATE` — [Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags) (verified Sep 2026) |
| Shared logic | `armips/include/gym_badge_hm_reward.inc` — level cap (`10 + 4×badges`, 80 at 16) + HM table |
| Shared text | `data/text/854.txt` — level cap, HM names, TM intro |
| Falkner | scr_seq **859** — slots **0–5** patched (`tools/patch_scr_seq_gym_falkner.py`, armips slots **1–5**). Zone event is **131** (`T22GYM0101`) and stays vanilla — do **not** edit member **365** (that is the Saffron Poké Mart). TM choice in slot **1** (Aerial Ace + Pluck always, Roost @**4**), rematch **712**, text **558** indices **20–26** — [Violet Gym](#violet-gym-falkner--859--zone_event-131). `FLAG_GOT_TM51_FROM_FALKNER` (**115**) |
| Morty | member **922**, slot **1** — `scr_seq_morty_gym_slot1.s`, text **614** (blank-line bank; labels **20–24**, rematch **25–28**). Fling + Payback always, Shadow Claw @**2**, Shadow Ball + Dark Pulse @**6**. Rematch **715**. `FLAG_GOT_TM30_FROM_MORTY` (**166**) |
| Pryce | member **932** — **append-only** ([Mahogany Gym — Pryce scr_seq 932](#mahogany-gym--pryce-scr_seq-932)); text **622** labels **10–13**, rematch **14–17**. Hail only below **2** badges, Avalanche @**2**, Blizzard @**8**, Ice Beam @**10**. Rematch **716**. `FLAG_GOT_TM07_FROM_PRYCE` (**210**) |
| Jasmine | member **913**, slot **0** — `scr_seq_jasmine_gym_slot0.s`, text **606** labels **25–28**, rematch **29–32**. Steel Wing only below **2** badges, Gyro Ball @**2**, Iron Tail + Flash Cannon @**6**. Rematch **717**. `FLAG_GOT_TM23_FROM_JASMINE` (**194**) |
| Clair | member **943**, slot **0** — `scr_seq_clair_gym_slot13.s`, text **631** labels **14–15**, rematch **16–19**; zone_event **137** — [Blackthorn Gym](#blackthorn-gym--clair-rising-badge). Dragon Claw only below **8** badges, then Dragon Pulse. Rematch **719**. `FLAG_GOT_TM59_FROM_CLAIR` (**218**) |
| Bugsy | member **869**, slot **1** (script **2**) — `scr_seq_bugsy_gym_slot1.s`, text **567** labels **7–9**, rematch **10–13**. Silver Wind only below **4** badges, U-turn @**4**, X-Scissor @**6**. Rematch **713**. `FLAG_GOT_TM89_FROM_BUGSY` (**127**). Playable room is `MAP_T23GYM0102`; entrance **868** has no battle. On-transition slot **16** (level scripts **642**) — leave vanilla |
| Whitney | member **886**, slot **0** only — `scr_seq_whitney_gym_slot0.s`, text **582** labels **14–18**, rematch **19–22**. First win cries (no badge). Slot **1** chase and slot **4** on-transition stay vanilla. Badge talk: Attract only below **2** badges, Facade @**2**, Return @**4**, Hyper Beam + Giga Impact @**8**. Rematch **714**. `FLAG_GOT_TM45_FROM_WHITNEY` (**133**) |
| Chuck | member **877**, slot **0** — `scr_seq_chuck_gym_slot0.s`, text **574** labels **15–19**, rematch **20–23**. Brick Break only below **4** badges, Bulk Up + Drain Punch @**4**, Focus Punch @**6**, Focus Blast @**8**. Rematch **718**. `FLAG_GOT_TM01_FROM_CHUCK` (**186**). Still increments `VAR_UNK_4134` and sets `VAR_SCENE_ROCKET_TAKEOVER` when that counter is **3**. On-transition slot **1** (level scripts **650**) — leave vanilla. `VAR_TEMP_x4000 == 0` still shows the training line |
| Brock (Kanto) | member **752**, slot **0** — `scr_seq_brock_gym_slot0.s`, text **462**, trainer **253** / rematch **720**; TM choice + badge gating + rematch — [Pewter Gym](#pewter-gym--brock--gym-tm-choice-pool-prototype). `FLAG_GOT_TM80_FROM_BROCK` (**383**) = took a Brock TM. On-transition slot **3** (level scripts **525**) — leave vanilla |
| Misty (Kanto) | member **760**, slot **0** — `scr_seq_misty_gym_slot0.s`, text **469** (pre **8**, post **9**, badge **10**, revisit **13**, labels **17–19**, rematch **20–23**); trainer **254** / rematch **721**; TM03 / TM18 / TM55 (Brine **4** badges) — [Cerulean Gym](#cerulean-gym--misty--gym-tm-choice-pool). `FLAG_GOT_TM03_FROM_MISTY` (**384**). On-transition slot **3** (level scripts **533**) — leave vanilla; slots **4–7** = Machine Part / Rocket (story skip flags) — do not patch |
| Lt. Surge (Kanto) | member **778**, slot **23** (script **24**) — `scr_seq_surge_gym_slot23.s`, text **485**; trainer **255** / rematch **722** — [Vermilion Gym](#vermilion-gym--lt-surge--gym-tm-choice-pool). **`MAP_T06GYM0101` (365)** is the playable interior (warp from Vermilion **051**). `MAP_T08GYM0101` (480) / scr **809** is **Fuchsia Gym (Janine)**, not Vermilion. `FLAG_GOT_TM34_FROM_LT_SURGE` (**385**). On-transition **script 23** = slot **22** (level scripts **551**); slots **0–22** = trash-can puzzle — patch slot **23** only |
| Janine (Kanto) | member **809**, slot **1** (script **2**) — `scr_seq_janine_gym_slot1.s`, text **514** (pre **0**, post **1**, badge **2**, revisit **4**, labels **19–21**, rematch **22–25**); trainer **257** / rematch **724**; TM06 always, TM84 @**6**, TM36 @**8**. Below **6** badges the menu is skipped and TM06 is given directly — [Fuchsia Gym](#fuchsia-gym--janine--gym-tm-choice-pool). `FLAG_GOT_TM84_FROM_JANINE` (**301**). On-transition slot **0** (level scripts **582** = `02 01 00`) — leave vanilla |
| Blue (Kanto) | member **743**, slot **0** — `scr_seq_blue_gym_slot0.s`, text **454**; trainer **261** / rematch **727**; Swagger always, Safeguard @**2**, Double Team @**4**, Swords Dance @**6**, Trick Room @**8**. Below **2** badges the menu is skipped — [Viridian Gym](#viridian-gym--blue--gym-tm-choice-pool). `FLAG_GOT_TM92_FROM_BLUE` (**382**). On-transition slot **2** — flag flip only |
| Erika (Kanto) | member **786**, slot **0** — `scr_seq_erika_gym_slot0.s`, text **492**; trainer **256** / rematch **723**; Bullet Seed always, Grass Knot @**2**, Giga Drain @**4**, Solar Beam + Energy Ball @**8**. Below **2** badges the menu is skipped — [Celadon Gym](#celadon-gym--erika--gym-tm-choice-pool). `FLAG_GOT_TM19_FROM_ERIKA` (**292**). On-transition slot **2** (level scripts **559**) — leave vanilla. Do not rewrite zone **352** (cut trees) |
| Sabrina (Kanto) | member **829**, slot **0** — `scr_seq_sabrina_gym_slot0.s`, text **531**; trainer **258** / rematch **725**; Skill Swap + Psych Up always (menu is never skipped), Calm Mind @**4**, Dream Eater @**6**, Psychic @**10** — [Saffron Gym](#saffron-gym--sabrina--gym-tm-choice-pool). `FLAG_GOT_TM48_FROM_SABRINA` (**386**). On-transition slot **4** (level scripts **602**) — leave vanilla |
| Blaine (Kanto) | member **15** (`2_015`), slot **0** — `scr_seq_blaine_gym_slot0.s`, text **053**; trainer **259** / rematch **726**; Sunny Day always, Will-O-Wisp @**2**, Fire Blast + Overheat @**8**, Flamethrower @**10**. Below **2** badges the menu is skipped — [Cinnabar Gym](#cinnabar-gym--blaine--gym-tm-choice-pool). `MAP_D11R0106` (**457**), not a `*GYM0101` header. `FLAG_GOT_TM50_FROM_BLAINE` (**381**). Level scripts **276** use slots **8** and **9** — leave vanilla |
| Patch tools | `tools/patch_scr_seq_gym_{falkner,morty,pryce,jasmine,clair,brock,misty,surge}.py` — all but Pryce use `patch_script_slot()` (appends the new slot body, repoints only that slot; vanilla bytes never move); **Pryce is special** (do not rebuild 932) |
| Badge test hook (fixed Nov 2026) | `hooks` line `PlayerProfile_TestBadgeFlag_hook 02028F98` used branch register **r1**, which is the `badgeNumber` argument — the stub overwrote it with the hook address, so every non-bypass `TestBadgeFlag` returned FALSE (trainer card showed no badges, `CheckBadge` always 0, mart badge rows hidden) while `count_badges` / save menu still counted correctly. Now **r2**. **Rule:** the last column in `hooks` is the scratch register for the jump stub — pick one that is **not an argument** of the hooked function (r0–r3 are args) |
| Slot order pitfall | Vanilla slot bodies are often stored **out of table order** (e.g. 943: slot 0 at byte 274, slot 1 at 26). The old `extract_scripts` + `build_scr_seq` rebuild silently dropped / misaligned slots — fixed in `patch_scr_seq_gym_falkner.py` only. Ferry / rod-guru / Mom / other patchers still carry their **own copy** of the old rebuild; unaudited — suspect them first if a patched map crashes on entry or an NPC runs the wrong script |
| Map header lookup | Script IDs in zone_event / level scripts are **1-based** (script N = slot N−1). Find a map's scr_seq / level-script / msg / zone_event members from the arm9 map header table (24-byte entries) before patching |
| Verify | `scripts/build/verify_falkner_gym_hm_patch.py build/a012/2_859 …`; Clair: `scripts/build/verify_clair_gym_patch.py build/a012/2_943` |
| Recon | `scripts/dev/inspect_gym_slots.py` (after `build/a012_vanilla` exists) — leader trainer id per slot |

**Text bank indexing:** `msgenc` treats every line as a message index, including blank lines. Vanilla dumps of `558.txt` / `614.txt` have a blank line between each string — leader scripts must use indices **0, 2, 4, 6, 8** for pre / post / badge / TM / already-beaten. **`622.txt` compacted (0–4).** `606.txt` keeps two placeholder lines at 3–4 so TM = 5 and already-beaten = 6 (Steelix trade strings stay at 7+). **`631.txt` (Blackthorn Gym)** is compact (one string per line, **14** messages) — Clair leader uses **3** pre, **4** post-win, **7** TM flavor; TM intro is **`854` index 9** via `non_npc_msg_extern` (same as Morty). **Before editing any gym text bank, decode indices** (`tools/msgenc -d … build/text/7_NNN`) — off-by-one in `631` shows post-win “Take it.” before battle or bag-full text after TM.

**HM rows (badges earned → reward):** 2 Cut, 3 Rock Smash, 5 Fly, 6 Surf, 7 Strength, 10 Whirlpool, 13 Waterfall, 16 Rock Climb. **1** / **4**: bank **854** lines — Flash / Headbutt TMs **in Poké Marts** (messaging only until mart tables ship). Other counts without an HM row: badge + TM only.

**Flow:** win dialogue → `GiveBadge` → receipt → `SEQ_ME_BADGE` → shared level-cap line → **`count_badges`** → HM line (if row) + `SEQ_ME_WAZA` + silent `giveitem` → shared TM intro + fanfare + TM + Leader flavor text.

**Test:** beat a Gym as **2nd** badge → Cut; as **5th** → Fly; badge **1** or **4** → no HM, TM only.

### Mahogany Gym — Pryce scr_seq 932

**Do not** patch Pryce with `patch_slot1()` / `build_scr_seq()` like Morty or Jasmine. Member **932** is only **528 bytes** and **two** script entries with retail-specific layout:

| Slot | File offset | Role |
|------|-------------|------|
| **0** | **190** | Ice puzzle, entering the last room, Pryce battle, badge fanfare (`trainer_battle` @ **222** in vanilla) |
| **1** | **10** | Short flag script (~25 bytes), **not** the Leader talk script |

Rebuilding the offset table (or replacing “slot 1” with a full Leader script) breaks slot **0** → crash when entering Pryce’s room. Bisect: `GYM_BADGE_COUNT_FIELD_REWARDS` off leaves vanilla **932** and confirms the HM patch path, not ice tiles alone.

**Working approach** (`tools/patch_scr_seq_gym_pryce.py`, verified in-game Oct 2026):

1. Copy the retail **528-byte** member verbatim (offset table: slot **0** → **190**, slot **1** → **10**).
2. Leave bytes **190–315** unchanged except the badge-owned branch at **210** (room entry through `SEQ_ME_BADGE` + `wait_fanfare`).
3. Replace the vanilla TM tail (**315–528**) with opcode **22** `goto` to bytecode appended at file offset **528** (pad remainder with `scr_end` / zero).
4. Append `armips/scr_seq/scr_seq_pryce_gym_hm_ext.s` → `build/pryce_gym_hm_ext.bin` (`gym_badge_hm_reward.inc` + the TM choice). Hail is item **334**. Below **2** badges the menu is skipped.
5. Retarget the badge-owned `goto_if` at file **210** to `_pryce_revisit` in that extension (armips `-sym`). That branch used to enter the photo script at **376**, which this trampoline already overwrites. Revisit is now bag-full retry or rematch trainer **716**. Decline uses text **622** index **4**.

`scripts/build/verify_falkner_gym_hm_patch.py` accepts HM bytecode in the appended tail (whole-member scan for **932**). Recon: `scripts/dev/decode_pryce_932.py`, `scripts/dev/inspect_gym_slots.py` on `build/a012_vanilla/2_932`.

`scr_seq_pryce_gym_slot1.s` is a **Morty-style skeleton only** — not wired into the retail 932 patcher; keep for reference if 932 is ever restructured.

Mahogany **town** rocket skip is unrelated — [Skip Mahogany Rocket arc](#skip-mahogany-rocket-arc--post-clear-town-on-load).

### Field HM use without per-Gym badge flags

**Status: verified in-game Sep 2026** — Mom HM02 + party Fly without Storm Badge; Goldenrod dept mart shelves still badge-gated.

**Toggle:** `OPENWORLD_FIELD_MOVES_NO_BADGE_GATE` in `include/config.h` (on by default with open-world HM work). Covers party-menu HM checks and direct A-button HM interactions. Required for [OPENWORLD_TESTING_GRANTS](#open-world-starting-inventory-new-saves) HM02 to work from the party menu — granting the item alone is not enough; vanilla `FieldMove_CheckFly` still demands Storm Badge without this hook.

Vanilla `FieldMove_Check*` (arm9 ~`0x02067F00`) calls `PlayerProfile_TestBadgeFlag` for a **specific** Gym badge before returning `FIELD_MOVE_RESPONSE_NEED_BADGE` (2). That is independent of gym HM grants and of `FLAG_GOT_HM*`.

| What | Where |
|------|--------|
| Hook | `src/field_move_badge.c` → `PlayerProfile_TestBadgeFlag_hook` @ arm9 `0x02028F98` |
| Bypass | When caller LR is in `0x02067F87`–`0x0206888B` (party field-move checks) or equals `0x021E7539` (overlay 1 shore Surf check), return TRUE |
| Shared interaction scripts | `scripts/build/patch_field_hm_badges.py`, wired through `narcs.mk`, patches member **146**: Cut, Rock Smash, Strength, Rock Climb, Waterfall, Whirlpool. Replace each six-byte `CheckBadge` with six-byte `SetVar TRUE`, preserving offsets and all other script bytes; disabled setting leaves vanilla checks |
| Preserved | Mart badge shelves (`ScrCmd_MartBuy`, LR in field overlay ~`0x023Cxxxx`), TM teach helpers, other script/map gates |

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

**Direct interaction regression checks (Nov 2026):** with the corresponding vanilla badge absent, test A-button Cut, Rock Smash, Strength, Rock Climb, Surf, Waterfall, and Whirlpool with a party member knowing the move; accept and decline prompts, check effects/animations, and compare party-menu use. Repeat without a party member knowing the move to confirm rejection. Shore Surf still checks terrain and party Surf; ordinary script badge checks remain unchanged. Offline verification: `python3 scripts/build/patch_field_hm_badges.py build/a012 --verify`; compare member 146 against vanilla to ensure only the six badge instructions differ. Emulator playtesting remains required.

**Out of scope (for now):** `FLAG_GOT_HM02`, Flash dungeon scripts, Surf terrain restrictions, collection-based field HMs ([Future-8 § Field HMs from the full collection](DESIGN-FUTURE.md#field-hms-from-the-full-collection-deferred)).

### Fly map — Kanto destinations

**Status: implemented, awaiting in-game cross-region Fly confirmation** — `OPENWORLD_FLY_MAP` in `include/config.h`. Kanto scrolling and Johto ↔ Kanto selection use ARM9 hooks. **`Pokegear_GetMapUnlockLevel`** on linked arm9 at **`0x0202EE70`** (pret getter — **not** **`0x0202EE84`**, mid-function in rebased arm9 → Fly crash). Do **not** hook overlay 101 into overlay 129 (Fly map may unload 129).

Vanilla gates the Fly / Pokégear map on **`SavePokegear.mapUnlockLevel`** (0 = Johto scroll only, 2 = full Kanto), set by story **`ScrCmd_804`** — not by Mom’s `UpgradePokegear(1)` and **not** by `PlayerProfile.gameClear`. Cross-region spot picking compares each flypoint’s region to **`mapApp->curRegion`** (struct field @ **+0x0E** in overlay 101). Pret’s **`ov101_021EA7E4`** label does **not** line up with the live retail gate (see attempts below).

| Hook | File | ARM address |
|------|------|-------------|
| `Pokegear_GetMapUnlockLevel_hook` (clamp return to ≥ 2) | `src/fly_map_openworld.c` | arm9 `0x0202EE70` |

Individual cities still require **`FLAG_SYS_FLYPOINT_*`** (Pokémon Center visit). Re-scan after rebases: `python scripts/dev/verify_fly_map_hooks.py` (after `base/` exists).

`PokegearTownMap_LaunchApp_hook` replaces the ARM9 launcher at **0x0203EAB0** before entering the map application. It preserves vanilla allocation (heap **11**, size **0x2C**), argument initialization (**0x02092D8C**), application launch (**0x0203EA5C**), and ownership/return pointer. For kind **0** (Fly), only transient `args.x/z` become **(28×32, 6×32)**, the native neutral Indigo region. This permits either region in the unmodified destination filter, as already used by Abra. Actual map ID, matrix marker/cursor coordinates, save pointer, visit flags, selection/cancellation and Fly landing/animation tasks remain native. Kind **1** (ordinary town map) keeps its original arguments. No saved location or actual Indigo map is changed.

Validation: `python scripts/dev/verify_cross_region_fly.py` exercises the installed ARM9 hook and compiled launcher from Johto, Kanto and Indigo source arguments, verifies marker/result/save-pointer preservation and unchanged ordinary town maps, and compares the function bytes against packed overlay 129. Run `python scripts/dev/verify_abra_travel_arm.py` and `python scripts/dev/verify_center_abra.py` for Abra regression coverage. Playtest Fly in both directions, same-region Fly, unvisited destinations and cancellation after reloading `test.nds`.

**Target ([World-1](DESIGN-WORLD.md#world-1-world-transportation), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)):** once HM Fly is unlocked, fly to **visited cities in both regions** without E4 or SS Aqua story prerequisites — without setting `gameClear` on new saves.

#### Cross-region fly attempts (pinned)

**Historical attempts:** Kanto **map scroll** via arm9 **`Pokegear_GetMapUnlockLevel`** hook @ **`0x0202EE70`** was the only working change before the launcher fix above.

**Tried (overlay 101, retail base ~`0x021E7740`):** pret-named helpers and guessed **`0x021EF09C`** / **`0x021E81A8`** patches — crash, no-op, or no cross-region spot pick. Pret labels do not match live callers; need BL graph from party Fly → overlay 101, not symbol grep.

**Resolved approach (Nov 2026):** retain the native spot filter and supply the neutral region through launcher arguments, as with Abra. The failed overlay patches are not required. Earlier session recon was **`scripts/local/`** only (not in git).


### Violet Gym (Falkner) — 859 / zone_event 131

**Status (Nov 2026):** Elevator and guide hide verified. TM choice is in the leader slot and still needs a playtest: Aerial Ace and Pluck from the first badge (menu always opens), Roost at **4**. Rematch trainer **712**.

Vanilla Violet Gym uses **six scr_seq slots**, not just the leader. Open-world patches scr_seq **0–5** only. Zone event member **131** (`T22GYM0101`) stays vanilla. Member **365** is the Saffron Poké Mart (`T11FS0101`); an object-removal patch aimed at “Violet Gym obj 3” deleted that mart’s specialty clerk (obj **3**, script **2**). Do not strip objects from **131** either: guide NPCs stay in the file and are hidden with flags **739** / **740**.

| Slot | Role | Patch |
|------|------|-------|
| 0 | OnLoad | **`patch_scr_seq_gym_falkner.py`** — keep vanilla **`violet_gym_init` (324)** (3D lift platform + gymmick save); prepend **`setflag` 739/740** (Sprout-skip guide hide); **`hide_person 1`** (opcode **101**) right after init and again before `scr_end`. **Must not** omit init (lift disappears; **`VioletGymElevator`** crashes). **Must not** remove **obj 1** from zone_event (init / `hide_person` need the object index). |
| 1 | Falkner leader + HM table | `scr_seq_falkner_gym_slot1.s` |
| 2 | Hint NPC (zone **131** obj **3**, script **3**, flag **740**) | `scr_seq_falkner_gym_slot2.s` — hidden by flag; leave the object in place |
| 3 | Sprout gate talk (obj 1 script 3) | `scr_seq_falkner_gym_slot3.s` — obj 1 hidden after OnLoad |
| 4 | Upper lift pad (obj 2 script 4) | `scr_seq_falkner_gym_slot4.s` — `violet_gym_elevator` (vanilla slot **4** was empty) |
| 5 | Lower lift (engine scripts **10201** / **10202**) | `scr_seq_falkner_gym_slot5.s` — elevator only (no TM51 / Roost gate) |

**Zone_event 131 (vanilla, not patched):** Falkner **obj 0** (script **2**), guide **obj 3** (script **3**, flag **740**), guide **obj 4** (script **6**, flag **739**). `hide_person 1` in the OnLoad script still needs **obj 1** present on this member.

**New saves:** `openworld_story_skip_flags.inc` sets **739** and **740** so the guide stays hidden on first gym entry.

**Pitfalls:** `hide_person` is opcode **101** (not **102**). Dropping obj 1 without the OnLoad patch crashes on `hide_person`; skipping **`violet_gym_init`** removes the lift. Recon helpers (optional): **`scripts/local/`** — `decode_falkner_gym.py`, `disasm_scr_seq.py`, `scan_violet_gym.py`.

### Next leaders

| Leader | scr_seq | Leader slot | Notes |
|--------|---------|-------------|--------|
| **Whitney** | **886** | **0** (slots 1 and 4 vanilla) | Shipped — cry on the first win; badge, level cap, HM, and TM menu on the post-chase talk. |
| Bugsy | **869** | **1** | Shipped — slot **16** on-transition left vanilla. |
| Chuck | **877** | **0** | Shipped — slot **1** on-transition left vanilla. Rocket scene still keys off `VAR_UNK_4134 == 3`. |
| Janine | **809** | **1** | Shipped — [Fuchsia Gym](#fuchsia-gym--janine--gym-tm-choice-pool) |

**Template for “easy” leaders (Falkner / Morty / Pryce / Jasmine pattern):** one leader slot, copy script skeleton, set badge + TM constants, fix **text indices** (blank-line banks vs compact), wire `narcs.mk` + patch py + verify member.

### Blackthorn Gym — Clair (Rising Badge)

**Status (Nov 2026):** Verified — open-world Leader battle with **0** prior Johto badges; post-win **Rising Badge**, badge fanfare, shared level-cap / shop-hint block, **TM59 (Dragon Pulse)** with item fanfare. Dragon’s Den shrine trial is **not** required for the badge (Den scripts unchanged).

**Design:** [Story-3 Gyms](DESIGN-STORY.md#gyms--access-and-story-policy) — drop 7-badge / Goldenrod Rocket gates; grant Rising Badge in-gym without Dragon’s Den trial (Den / HM follow-ups still open).

**Map IDs (retail):** interior `MAP_T30GYM0101` — zone_event member **137** (`137_T30GYM0101.json`), scr_seq member **943** (not **938**, which is a different map). Clair is zone **obj 0**, sprite **359** (`SPRITE_GSLEADER8`), **script 1**. Script IDs are **1-based**: script 1 = slot **0**. Slot **1** (script 2) is the on-transition script (level scripts member **716**) — patching it crashes / hangs on gym entry.

| What | Where |
|------|--------|
| Leader script | scr_seq **943**, slot **0** — `armips/scr_seq/scr_seq_clair_gym_slot13.s` → `build/clair_gym_slot13.bin` (filename legacy: was wrong member/slot) |
| scr_seq patch | `tools/patch_scr_seq_gym_clair.py` — `patch_script_slot(0, …)`; `trainer_battle` **39→35** (fork Leader id **35**) |
| Clair object | zone_event **137** — `tools/patch_zone_event_blackthorn_gym_clair.py` sets **obj 0** → script **1** |
| Text | `data/text/631.txt` — leader **3** pre, **4** post-win, **7** TM flavor, **9** revisit; plaque **11–12**; TM intro **`data/text/854.txt` index 9** |
| Badge grant | `GiveJohtoBadgeOpenWorld` → `RunNewCommand` case **3** in `src/script_new_cmds.c` |
| TM flag | `FLAG_GOT_TM59_FROM_CLAIR` (**218**) — `_already_beaten` still grants TM if badge already owned |
| Build / verify | `narcs.mk` → `2_943`, `2_137`; `scripts/build/verify_clair_gym_patch.py build/a012/2_943` |

**Flow (shipped):** pre-battle (**631** **3**) → Morty-style `trainer_battle` + `check_battle_won` → post-win (**631** **4**) → `GiveJohtoBadgeOpenWorld` + midgame badge var → `SEQ_ME_BADGE` → `gym_badge_hm_reward.inc` (level cap; badge **1** → Flash mart line) → TM choice. Below **8** badges only Dragon Claw is legal, so the menu is skipped. At **8+** the menu is Dragon Claw + Dragon Pulse. Rematch trainer **719**; decline uses index **9**. Loss: **631** **5** then `white_out`.

**Pitfalls:** Do not use **631** file line numbers as script indices (duplicate Yo! lines at **2–3** shift Clair intro to **3**). Vanilla slot **0** ended at msg **5** with no badge (Den trial design). Wrong scr_seq member (**938**) patches a non-playable gym map.

### Pewter Gym — Brock + Gym TM choice pool (prototype)

**Status (Nov 2026):** **Verified in-game** — first win (badge, level cap, HM row, badge-gated TM menu, farewell) **and** rematch (offer / decline / battle / TM pick). Brock = first Kanto leader on the shared HM/level-cap flow **and** the [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) choice-menu template (Misty = second). Template for rolling the TM choice out to the other leaders.

**Map IDs:** `MAP_T03GYM0101` (473) → scr_seq **752**, level scripts **525**, msg bank **462**, zone_event **426**. Brock = zone **obj 1** (sprite 373), **script 1 = slot 0**. Level scripts **525** = `02 04 00 …` → on-transition **script 4 = slot 3** (leave vanilla).

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_brock_gym_slot0.s` → `build/brock_gym_slot0.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_brock.py build/a012/2_752` (`patch_script_slot(0, …)`); `scripts/build/verify_falkner_gym_hm_patch.py build/a012/2_752`; both in `narcs.mk`, `.s` listed in `SCR_SEQ_PATCH_ONLY` |
| Text | `data/text/462.txt` — menu labels **10–15** in **unlock order** (0-badge: TM37/39/69, then TM80 @4, TM71 @8, TM26 @12); menu picker values **0–5** in that same order |
| Vanilla facts | trainer **253** (unchanged in fork), `GiveBadge BADGE_BOULDER` + `addvar VAR_UNK_4135` (Kanto badge var) + `settrainerflag` **308** / **685** (gym trainers), `FLAG_GOT_TM80_FROM_BROCK` (**383**) |

**Flow:** pre (**0**) → `trainer_battle 253` → post-win (**1**) → badge + vars → "received Badge" (**2**) → `SEQ_ME_BADGE` → `gym_badge_hm_reward.inc` → `_tm_grant`: prompt (854/12) → `touchscreen_menu_hide` → `menu_init 1,1,0,0,VAR_SPECIAL_RESULT` → six `menu_item_add <local msg>, 255, <n>` → `menu_exec` → `touchscreen_menu_show` → `switch` sets `VAR_SPECIAL_x8004` = TM item → `hasspaceforitem` → `callstd std_give_item_verbose` ("obtained TM##" + fanfare) → `setflag FLAG_GOT_TM80_FROM_BROCK` (now means "took a Brock TM"). Revisit with flag unset → straight to menu (bag-full retry); flag set → msg **5**.

**Rolling the TM choice out to another leader (recipe):**

1. **Find the map's members** from the arm9 map header table (24-byte entries; Blackthorn entry at `base/arm9.bin` `0xf7918` = map 141, so `base = 0xf7918 - 141*24`; fields: scripts, level scripts, msg bank, …, zone_event). Dump the level-scripts member to learn the on-transition script — **never** replace it.
2. **Script IDs are 1-based** (zone_event object script N = scr_seq slot N−1). Check which slot the leader object uses in zone_event before patching.
3. **Menu labels must be in the map's local msg bank** (`menu_init` reads the local bank; extern banks are not supported). Dump the whole bank to `data/text/<bank>.txt` (`tools/msgenc -d -c charmap.txt build/text/7_<bank> …` in Docker), normalize CRLF→LF, **append** labels at the end (never shift existing indices). **Decode and `nl -ba` the bank** — script `npc_msg` / menu indices are **0-based line indices** (line 18 in the dump = index **17**, a common off-by-one when appending after a 16-line vanilla bank).
4. Label format `TM## MoveName` — move names from `sMachineMoves[]` in `src/item.c` (fork may differ from vanilla, e.g. TM05 = Headbutt). Item id = `328 + TM# − 1` (TM01 = 328, TM80 = 407).
5. Copy Brock's `_tm_grant` block; keep **`touchscreen_menu_hide` / `touchscreen_menu_show` around the menu** — without hide the menu never draws and the game soft-locks on the prompt (A does nothing).
6. **`menu_item_add` values are 0–N**, matching the `switch` / `case` labels. An unmatched result falls through to the 0-badge TM.
7. Every Johto and Kanto leader is on this menu. Pryce stays append-only (932).

**Pool data:** [`data/gym_tms/gym_tm_pools.tsv`](../data/gym_tms/gym_tm_pools.tsv) — one row per `(Leader, TM)` with move stats (from `data/Moves.c` / `sMachineMoves`), **Min Badges**, and **Status** (`In game` vs `Proposed`). Hand-edited planning sheet; **not read by the build yet** — when rolling a leader out, copy its Min Badges into that leader's `.s` (`BADGES_TMxx`) and flip Status. If a future generator emits menu labels / gating from it, wire it in `narcs.mk` and keep the TSV as the source of truth.

**Badge gating (shipped for Brock):** `count_badges VAR_SPECIAL_x8000` before `menu_init`; ungated TMs added first, then gated TMs in **ascending** requirement order, each preceded by `compare VAR_SPECIAL_x8000, BADGES_TMxx` / `goto_if_lt _menu_show` (one early exit skips all higher tiers). Menu **values stay fixed per TM** (not display position), so the `switch` table is unchanged. Brock: Sandstorm / Rock Tomb / Rock Polish **0**, Rock Slide **4**, Stone Edge **8**, Earthquake **12** (count includes the badge just won). Every pool needs at least one **0**-badge entry or the menu could be empty.

**Rematch (shipped for Brock):** badge owned + TM flag set → msg **16** offer + `yesno` (0 = yes, 1 = no). No → vanilla msg **5**. Yes → msg **17** → `trainer_battle 720` (vanilla phone-rematch team, 6 mons — **roster differs from the first fight**, expected; interim until [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) generated Gym parties replace it; Gym Leader cap scaling sets levels to the **current** cap) → loss `white_out`; win → msg **18** → `clearflag FLAG_GOT_TM80_FROM_BROCK` (so a bag-full reward is retried instead of re-offering a battle) → same `_tm_grant` menu (gated by **current** badges). No badge, HM, level-cap or shop lines on rematch. Every TM grant (first win or rematch) ends with a **per-leader farewell** (msg **19**, personality line inviting a rematch). Script entry checks `FLAG_GOT_TM80_FROM_BROCK` **before** `CheckBadge` (jumps straight to the rematch offer) — added while the badge-test hook bug was live; harmless redundancy now.

**Per-leader text to author when rolling out:** TM labels, rematch offer, rematch accept, rematch win, farewell (4 custom lines + labels). Check `data/Trainers.c` for a vanilla rematch trainer id (same `TRAINERCLASS_LEADER_*`, higher index — e.g. Brock 253 / 720).

**Shipped:** every Johto and Kanto leader uses the choice menu. Generating labels from `src/item.c` is still hand-typed. Menu height with >6 entries is untested (Brock is the largest pool at 6). If only one pool TM is unlocked, skip the menu and give that TM. Menu values are **0–N**, matching the `switch` cases.

### Cerulean Gym — Misty + Gym TM choice pool

**Status (Nov 2026):** shipped in tree — same flow as [Pewter Gym](#pewter-gym--brock--gym-tm-choice-pool-prototype) (HM / level cap, TM menu, rematch). Playtest before calling verified.

**Map IDs:** `MAP_T04GYM0101` (427) → scr_seq **760**, level scripts **533**, msg bank **469**, zone_event **382**. Leader **script 1 = slot 0**. Level scripts **533** → on-transition **script 4 = slot 3** (leave vanilla).

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_misty_gym_slot0.s` → `build/misty_gym_slot0.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_misty.py build/a012/2_760`; `scripts/build/verify_falkner_gym_hm_patch.py build/a012/2_760`; `narcs.mk` + `SCR_SEQ_PATCH_ONLY` |
| Text | `data/text/469.txt` — indices **0–16** vanilla (Rocket / sign / leader / Machine Part); **17–23** appended (TM labels + rematch + farewell). Prompt **854** index **12** |
| Vanilla facts | trainer **254**, rematch **721**, `GiveBadge BADGE_CASCADE` + `addvar VAR_UNK_4135`, `FLAG_GOT_TM03_FROM_MISTY` (**384**). Vanilla slot **0** had no `settrainerflag` — not added |

**Pool:** Water Pulse / Rain Dance (**0** badges), Brine (**4**). Three-menu entry count (no >6 scroll test).

### Vermilion Gym — Lt. Surge + Gym TM choice pool

**Status (Nov 2026):** shipped in tree — same Brock/Misty flow. Playtest before calling verified.

**Map IDs:** playable interior **`MAP_T06GYM0101` (365)** → scr_seq **778**, level scripts **551**, msg bank **485**, zone_event **322**. `MAP_T08GYM0101` (header **480**) / scr_seq **809** / text **514** is Fuchsia Gym — see [Janine](#fuchsia-gym--janine--gym-tm-choice-pool).

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_surge_gym_slot23.s` → `build/surge_gym_slot23.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_surge.py build/a012/2_778`; `verify_falkner_gym_hm_patch.py` |
| Text | `data/text/485.txt` — leader lines **0–5**; trash / fence strings **6–15**; appended **16–24** (TM labels + rematch) |
| Vanilla facts | `BADGE_THUNDER`, rematch **722**, `FLAG_GOT_TM34_FROM_LT_SURGE` (**385**) |

**Pool:** Shock Wave / Charge Beam (**0**); Thunder Wave (**2**); Thunder (**8**); Thunderbolt (**10**). Five-entry menu (same pattern as Brock).

### Fuchsia Gym — Janine + Gym TM choice pool

**Status (Nov 2026):** shipped in tree. Playtest before calling verified.

**Map IDs:** `MAP_T08GYM0101` (480) → scr_seq **809**, level scripts **582**, msg bank **514**, zone_event **433**. Real Janine is zone **obj 2** (sprite **372**, hide flag **755**), **script 2 = slot 1**. Level scripts **582** = `02 01 00` → on-transition **script 1 = slot 0** (leave vanilla; it shows the real Janine). Disguise trainers stay in other slots.

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_janine_gym_slot1.s` → `build/janine_gym_slot1.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_janine.py build/a012/2_809`; `verify_falkner_gym_hm_patch.py` |
| Text | `data/text/514.txt` — vanilla **0–18**; appended **19–25** (TM labels in unlock order, rematch, farewell) |
| Vanilla facts | trainer **257**, rematch **724**, `GiveBadge BADGE_SOUL` + `addvar VAR_UNK_4135`, `settrainerflag` **83 / 84 / 136 / 183**, `FLAG_GOT_TM84_FROM_JANINE` (**301**), `setvar VAR_TEMP_x400B, 111` around `trainer_battle` |

**Pool:** Toxic (**0**), Poison Jab (**6**), Sludge Bomb (**8**). If `count_badges` is below **6**, only Toxic is legal, so `_tm_grant` skips the choose prompt and menu and gives TM06. At **6+** the menu is Toxic + Poison Jab; at **8+** Sludge Bomb is added. Same skip applies on a rematch.

### Viridian Gym — Blue + Gym TM choice pool

**Status (Nov 2026):** shipped in tree. Playtest before calling verified.

**Map IDs:** `MAP_T02GYM0101` (496) → scr_seq **743**, level scripts **516**, msg bank **454**, zone_event **448**. Blue is zone **obj 5** (sprite **375**, hide flag **758**), **script 1 = slot 0**. Level scripts **516** = `02 03 00` → on-transition **script 3 = slot 2** (leave the body; `patch_scr_seq_gym_blue.py` only flips `setflag 758` to `clearflag` so he is visible). Slot **3** stays the open-world coord skip.

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_blue_gym_slot0.s` → `build/blue_gym_slot0.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_blue.py build/a012/2_743` (also OnLoad + coord); `verify_falkner_gym_hm_patch.py` |
| Text | `data/text/454.txt` — vanilla **0–10**; appended **11–19** |
| Vanilla facts | trainer **261**, rematch **727**, `GiveBadge BADGE_EARTH`, `FLAG_GOT_TM92_FROM_BLUE` (**382**). First win still sets trainer flags **681–684** and the vanilla post-win flags |

**Pool:** Swagger (**0**), Safeguard (**2**), Double Team (**4**), Swords Dance (**6**), Trick Room (**8**). Below **2** badges only Swagger is legal, so the menu is skipped. Those five left the department floors and Game Corners; both corners stay at **6** TMs and both TM floors at **5**.

### Celadon Gym — Erika + Gym TM choice pool

**Status (Nov 2026):** shipped in tree. Playtest before calling verified.

**Map IDs:** `MAP_T07GYM0101` (395) → scr_seq **786**, level scripts **559**, msg bank **492**, zone_event **352**. Erika is zone **obj 5** (sprite **371**, hide flag **754**), **script 1 = slot 0**. Level scripts **559** = `02 03 00` → on-transition **script 3 = slot 2** (leave vanilla). Zone **352** is also the Celadon cut-tree member — do not rewrite it.

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_erika_gym_slot0.s` → `build/erika_gym_slot0.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_erika.py build/a012/2_786`; `verify_falkner_gym_hm_patch.py` |
| Text | `data/text/492.txt` — vanilla **0–6**; appended **7–15** |
| Vanilla facts | trainer **256**, rematch **723**, `GiveBadge BADGE_RAINBOW`, `settrainerflag` **326 / 356 / 336 / 346**, `FLAG_GOT_TM19_FROM_ERIKA` (**292**) |

**Pool:** Bullet Seed (**0**), Grass Knot (**2**), Giga Drain (**4**), Solar Beam (**8**), Energy Ball (**8**). Below **2** badges only Bullet Seed is legal, so the menu is skipped. At **8** both Solar Beam and Energy Ball are added together.

### Saffron Gym — Sabrina + Gym TM choice pool

**Status (Nov 2026):** shipped in tree. Playtest before calling verified.

**Map IDs:** `MAP_T11GYM0101` (410) → scr_seq **829**, level scripts **602**, msg bank **531**, zone_event **366**. Sabrina is zone **obj 5** (sprite **369**, hide flag **753**), **script 1 = slot 0**. Level scripts **602** = `02 05 00` → on-transition **script 5 = slot 4** (leave vanilla).

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_sabrina_gym_slot0.s` → `build/sabrina_gym_slot0.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_sabrina.py build/a012/2_829`; `verify_falkner_gym_hm_patch.py` |
| Text | `data/text/531.txt` — vanilla **0–9**; appended **10–18** |
| Vanilla facts | trainer **258**, rematch **725**, `GiveBadge BADGE_MARSH`, `setflag` **2456**, `settrainerflag` **230 / 415 / 368 / 369**, `FLAG_GOT_TM48_FROM_SABRINA` (**386**) |

**Pool:** Skill Swap (**0**), Psych Up (**0**), Calm Mind (**4**), Dream Eater (**6**), Psychic (**10**). Two TMs are legal from the first badge, so the menu always opens.

### Cinnabar Gym — Blaine + Gym TM choice pool

**Status (Nov 2026):** shipped in tree. Playtest before calling verified.

**Map IDs:** `MAP_D11R0106` (457) — the burned gym inside the Cinnabar cave, not a `*GYM0101` header. scr_seq **15** (`build/a012/2_015`), level scripts **276**, msg bank **53** (`data/text/053.txt`), zone_event **412**. Blaine is zone **obj 0** (sprite **374**, hide flag **757**), **script 1 = slot 0**. Level scripts **276** reference scripts **9** and **10** (slots **8** and **9**) — leave those vanilla.

| What | Where |
|------|--------|
| Leader script | `armips/scr_seq/scr_seq_blaine_gym_slot0.s` → `build/blaine_gym_slot0.bin` |
| Patch / verify | `tools/patch_scr_seq_gym_blaine.py build/a012/2_015`; `verify_falkner_gym_hm_patch.py` |
| Text | `data/text/053.txt` — vanilla **0–25**; appended **26–34**. Filename is zero-padded so it overwrites narc member `7_053` |
| Vanilla facts | trainer **259**, rematch **726**, `GiveBadge BADGE_VOLCANO`, `setflag` **613 / 665 / 319 / 320 / 316**, `clearflag` **666**, `FLAG_GOT_TM50_FROM_BLAINE` (**381**) |

**Pool:** Sunny Day (**0**), Will-O-Wisp (**2**), Fire Blast (**8**), Overheat (**8**), Flamethrower (**10**). Below **2** badges only Sunny Day is legal, so the menu is skipped. At **8** both Fire Blast and Overheat are added together.

---

## Full party EXP share (interim)

**Status:** verified in-game.

**Design:** [Battle-4](DESIGN-BATTLES.md#battle-4-experience) — full-party EXP per KO (not split), and the same living party members receive that KO’s EVs, including those at the badge cap. Battle-limit recipients when [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) lands. Fainted bench mons get nothing. No Exp Share item required.

| What | Where |
|------|--------|
| Toggle | `FULL_PARTY_EXP_SHARE` in `include/config.h` (enabled by default) |
| Hook | `Task_DistributeExp_Extend` in `src/battle/battle_script_commands.c` |

**Verified:** bench mons gain EXP (and level) from wild/trainer KOs while only one mon is out in battle.

**EVs:** the same KO pays EVs to every living, non-egg party member, including Pokémon at or above the badge cap. Fainted party members are skipped. Vanilla's per-mon EV `bl` in `Task_DistributeExp` (`0x02245B3A`) is nop'd in `bytereplacement`; `GivePartyEffortValuesForFaint` grants them once per faint or capture-exp task. Macho Brace, Power items, and Pokérus still apply per recipient inside `DistributeEffortValues`.

---

## Trainer level scaling

**Status:** level band and **species** stage adjust verified in-game (Sep 2026) — e.g. authored Alakazam → Abra/Kadabra at low caps; Gym Leader cap enabled. **Moves at scaled level:** fixed ([KB-16](#kb-16--encounter-moves-not-rebuilt-after-specieslevel-change)). Gym trainer band + type filter still open ([Battle-2](DESIGN-BATTLES.md#trainer-scaling-release), [Battle-3](DESIGN-BATTLES.md#battle-3-gyms)).

**Design:** [Battle-2](DESIGN-BATTLES.md#cap-ladder) — badge count → cap `10 + 4×badges` (max **80** at 16 badges). Ordinary trainers: uniform random level in **`[cap−4, cap]`**. Gym Leaders: **every slot at cap exactly**. Trainers never exceed **80** (Champion uncap does not apply to NPCs). Generated parties / dynamic battles: [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties), [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc).

| Feature | Toggle | Where |
|---------|--------|--------|
| Rescale levels | `TRAINER_LEVEL_SCALING` | `MakeTrainerPokemonParty()` in `src/field/enemy_party.c` — `CountPlayerBadges()`, `PickTrainerLevelInBand()` |
| Level-up moves | `TRAINER_LEVEL_APPROPRIATE_MOVES` | Same — skips NARC move sets when set; **`ClearMonMoves`** then **`InitBoxMonMoveset()`** after stage adjust ([KB-16](#kb-16--encounter-moves-not-rebuilt-after-specieslevel-change)) |
| Stage adjust | `TRAINER_SPECIES_STAGE_ADJUST` | Same — `AdjustEncounterSpeciesForLevel()` in `include/encounter_species_stage.h` (requires level scaling): walk **prevos** (level-up + synthetic), then **forward** to the stage for scaled level. Tables: `gen_level_up_evo_tables.py` + `gen_synthetic_evo_edges.py`; `patch_level_up_evo_addrs.py` patches overlay 129 (shared with [wild stage adjust](#runtime-pipeline)). Docker/Linux check: `python3 scripts/dev/verify_encounter_stage.py` (compiles actual shared C) |
| Gym Leader cap | `TRAINER_GYM_LEADER_CAP_LEVEL` | Same — `IsGymLeaderTrainerClass()` for all 16 Johto/Kanto Leaders; requires level scaling |

**Dependencies:** moves and stage adjust require `TRAINER_LEVEL_SCALING`; Gym Leader cap requires level scaling.

---

## Player badge level cap & Rare Candies

**Design:** [Battle-2](DESIGN-BATTLES.md#rare-candies) — EXP stops at badge cap; **Rare Candies may exceed the cap**.

**Day Care verified in-game (Nov 16, 2026):** user confirmed capped growth, Rare Candy Pokémon above the cap, growth quotes, withdrawal fees, and normal withdrawals after the r3 hook correction. The reported second-deposit refusal was a misunderstanding of the dialogue, not a confirmed party-count bug.

| Piece | Where |
|-------|--------|
| `GetLevelCap()` | `src/pokemon.c` — `GetPlayerLevelCapForBadges(PlayerProfile_CountBadges(...))`; **100** when `PlayerProfile.gameClear` |
| Trainer cap helper | `include/player_level_cap.h` (inline; shared with `enemy_party.c`) |
| `IMPLEMENT_LEVEL_CAP` / `UNCAP_CANDIES_FROM_LEVEL_CAP` | `include/config.h` (on) |
| `ALLOW_LEVEL_CAP_EVOLVE` | Optional — Rare Candy at cap runs level-up evolution check (off by default) |
| EXP / candy hooks | `ImplementLevelCap_hook` (battle EXP), `Pokemon_TryLevelUp` @ ARM9 (level-up + **EXP clamp at cap** — empty bar), `CanUseItemOnMonInParty`; `CapRareCandies` only when UNCAP off |
| Day Care | `GetDaycareUpdatedLevel` @ `0x0206C0A0` (quote, fee, level readout) and `Save_Daycare_MoveMonToParty` @ `0x0206BFC4` (withdraw). Both hooks must branch through **r3**: r1 carries the step count or DaycareMon pointer and must survive the trampoline; clobbering it causes instant capped quotes and corrupt withdrawals. Mons at or below the cap still run vanilla `Daycare_LearnLevelUpMoves` @ `0x0206BF60`, which stops on the cap through `Pokemon_TryLevelUp`. Mons already above the cap do not receive step EXP, so withdraw cannot raise them. Fee stays `(levels gained + 1) × 100` using the capped gain |
| Wild catch above cap | `ShouldPreventMonCapture` / `PrintBallBlockedMessage` in `other_battle_calculators.c` — deflect + “too strong” msg when wild level **>** `GetLevelCap()` ([Battle-2 § Wild catches](DESIGN-BATTLES.md#wild-catches-above-the-player-cap)) |

---

## Paid ferry / local bypass NPCs (reusable recipe)

**Status:** Route 42 reference implementation **verified in-game** (Aug 2026).

**Use when:** geography blocks travel (water without Surf, long mandatory gaps) and you want a **diegetic paid bypass** instead of a bridge edit or global fast travel. Same toolchain as badge gates, but adds **object NPCs** + **append scr_seq slots** instead of coord triggers.

**Do not use for:** story roadblocks (prefer removing them) or map-wide walkability (that is `land_data`, not scripts).

**IDs:** [Field map IDs](#field-map-ids-dont-mix-them-up) — Route 42: header **44**, scr_seq **252**, zone_event **041**, msg **399**.

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

**Route 36 Sudowoodo (Mom intro):** `FLAG_HIDE_ROUTE_36_SUDOWOODO` (**450**) in the same block (see [Remove Sudowoodo block](#remove-sudowoodo-block-route-36--verified)).

**Vanilla cleanup (Mom intro):** with `OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS`, `armips/include/openworld_story_skip_flags.inc` sets early-route hide flags, rival/Elm skips, Azalea + Mahogany rocket flags, and **`FLAG_BOAT_ARRIVED` (235)** + **`FLAG_UNK_0F2` (242)** / pret S.S. Ticket from Elm for SS Aqua repeat-travel (ticket item already granted). Pier/gangplank scr_seq patches: [§ SS Aqua](#ss-aqua-olivine--vermilion). Mahogany rocket **story flags** are not duplicated on map load when the define is on — `tools/patch_scr_seq_t28_rocket.py` uses `scr_seq_t28_005_onload.s` (`hide_person` only). **Kanto Fly map** uses `SavePokegear.mapUnlockLevel`, not `gameClear` — see [Fly map](#fly-map--kanto-destinations).

### SS Aqua (Olivine ↔ Vermilion)

**Design:** [World-1 § SS Aqua](DESIGN-WORLD.md#ss-aqua-olivine--vermilion). **Mom intro** (`openworld_story_skip_flags.inc`) sets **`FLAG_BOAT_ARRIVED` (235)** and grants the S.S. Ticket for open-world repeat travel.

**Build:** `narcs.mk` runs **`tools/patch_scr_seq_ss_aqua_weekday.py`** on four scr_seq members, then **`scripts/build/verify_ss_aqua_weekday_scr_seq.py`**. **In-place bytecode only** — never `build_scr_seq()` on these members (vanilla uses non-sequential empty-slot pointers; rebuilding the offset table silenced all pier scripts).

| scr_seq | Map | What is patched |
|--------|-----|-----------------|
| **152** | `P01R0101` Olivine pier | Ticket seaman slot **2** (scriptId **3**): `GetWeekday` → `goto` allow-boarding; `GoToIfUnset FLAG_GAME_CLEAR` → ticket path; embark **`clearflag 235`** → **`setflag 235`** (×2 in slot) |
| **154** | `P01R0103` Vermilion pier | Ticket seaman slot **1** (scriptId **2**): weekday `goto`; embark **`clearflag 235`** → **`setflag 235`** |
| **153** | `P01R0102` Olivine gangplank / ship deck | Slot **0** (scriptId **1**): **`GoToIfSet FLAG_BOAT_ARRIVED`** neutralized (rel **0**) — vanilla showed msg **256** “ship not moving” when **235** is set (opposite of pier logic) |
| **155** | `P01R0104` Vermilion gangplank | Same gangplank fix on slot **0** |

**Who to talk to:** pier **ticket** seaman only for boarding — Olivine zone_event **240** obj **2** (scriptId **3**); Vermilion **386** obj **1** (scriptId **2**). Other pier sailors use empty or facing-only scripts (no dialogue). After the ticket flow, the **gangplank** sailor (scriptId **1** on ship maps **330** / **387**) walks you aboard.

**Onboard first voyage:** With **235** kept set at embark, ship OnLoad (**156** / related) skips the forced captain announcement / missing-girl **mandatory** flow. **Optional:** vanilla cabin NPCs (engine-room sailor, etc.) may still offer the fetch quest if you talk to them; **disembark warps work without completing it** — acceptable for open-world v1; full quest strip not done.

**Pret refs:** `scr_seq_0152_P01R0101.s` (pier), `scr_seq_0153_P01R0102.s` (`scr_seq_P01R0102_000` gangplank), `scr_seq_0154_P01R0103.s`, `scr_seq_0155_P01R0104.s`; msg **256** gangplank block line.

**Verify (after `make`):**

```text
scripts/build/verify_ss_aqua_weekday_scr_seq.py build/a012/2_152 build/a012/2_154 build/a012/2_153 build/a012/2_155
```

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
- **SS Aqua scr_seq:** patch **152–155** in place on the extracted member file (`patch_scr_seq_ss_aqua_weekday.py`). Do **not** rebuild the scr_seq table for pier members — same rule as Route 32 badge NOP patches.
- **Healthy scr_seq size:** Route 42 member ~**1188 bytes** (8 scripts). Multi‑MB member = corrupt; patcher resets from vanilla when `count != VANILLA_SCRIPT_COUNT` or size > 8 KB.
- **Duplicate NPCs on rebuild:** zone_event patcher must delete prior ferry objects by id before re-adding.
- **Sign overlap:** bg-event signs and object NPCs on the same tile fight for interaction; offset NPC one tile from sign.
- **land_data ≠ ferry:** walking on water still needs terrain edits; ferries only skip the gap via warp. **`scripts/dev/apply_changed_maps.py`** runs before ROM pack (`Makefile` `all` target): replaces `base/root/a/0/6/5` members from `rawdata/changed_maps/**/*.bin` (filename must start with **NARC member index**). Skips paths containing **`failed`** (Route 42 bridge experiments stay archived only). **DSPRE:** `map{col}_{row}c` in the export name is matrix cell coords; the numeric prefix is the land_data member (e.g. Cinnabar **`205`** = `map32_15c`). **Do not** confuse `MAP_R42` header id **44** with land_data members **082–084**.

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

**Flags set:** hide rocket town NPCs (439–444), shady salesman (498), Lance in shop (504), Route 43 gate rockets (506); restore normal shopkeeper (`clearflag` 487), gate guard (`clearflag` 507); hide hideout interior NPCs if entered. **`clearflag FLAG_ROCKET_TAKEOVER_ACTIVE`** (2459), **`clearflag FLAG_UNK_0C5`** (197), **`setflag FLAG_BEAT_RADIO_TOWER_ROCKETS`** (198), **`setflag FLAG_ROCKET_HIDEOUT_CLEARED`** (202, Route 43 toll). With **`OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS`**, the same flag/var block runs at **Mom intro** (`openworld_story_skip_flags.inc`); Mahogany OnLoad patch is **`hide_person` only** (`scr_seq_t28_005_onload.s`).

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

**Debug helpers:** same as [Paid ferry § Debug helpers](#debug-helpers-keep-using-these) plus `decode_clear_script.py` for OnLoad bytecode.

### Gotchas

- **One member ≠ one map** — Johto overworld uses extra zone_event members for matrix chunks; same NPC at same world coords can appear in **084 + 043** or **046 + 090**.
- **Delete vs hide flag** — delete for gone-for-good skip; hide flag when vanilla toggles visibility later (gym blocker **439**).
- **coord events** — Mahogany east exit also had a **coord script** blocking walk-through; remove from zone_event coords table, not just the object.
- **Idempotent patchers** — match on `(obj_id, script, x, z)`; raise if vanilla object missing (catches wrong member / already-wrong base).
- **Do not commit `build/`** — patchers re-seed from `rom.nds` each rebuild.

---

## Accelerated game clock

**Design:** [World-9 — Accelerated day/night cycle](DESIGN-WORLD.md#world-9-accelerated-daynight-cycle). **Toggle:** `IMPLEMENT_ACCELERATED_GAME_CLOCK` in `include/config.h` (constants **`GAME_CLOCK_GAME_SECONDS_PER_REAL_SECOND`** = **48**, **`GAME_CLOCK_REAL_SECONDS_PER_GAME_DAY`** = **1800**). Comment out the master define to disable hooks and revert to vanilla RTC.

**After any `hooks` change:** `make clean && make test.nds -j24` — stale **`00 48 00 47`** stubs in `base/arm9.bin` if you skip clean.

| Layer | Files |
|-------|--------|
| Toggles | `include/config.h` |
| Hooks | `hooks` → `scripts/build/make.py` |
| Logic | `src/game_clock.c` |

**DeSmuME:** close ROM before loading a new `test.nds`.

### Rule (30 real minutes = 1 in-game day, wristwatch aligned)

- Real DS RTC is the input; read from **`sRTCWork.time_async`** / **`date_async`** (pret `struct GFRtcWork` @ **`0x021D1048`**).
- Phase = `(h×3600+m×60+s) % 1800` → scaled time-of-day (**48** game seconds per real second within the slot).
- **In-game midnight** on every real **:00** and **:30**.

**Wristwatch check:** **10:05** real (5 min into the 10:00 slot) → **4:00 AM** in-game. **10:00** / **10:30** real → in-game **00:00**.

**Scope:** scaled **time-of-day** only; **calendar date** still real async. Do **not** hook **`GF_RTC_UpdateOnFrame`** or rewrite **`sRTCWork.date/time`** each frame (boot crash / assert history).

### Hooks (all on when master define is set)

| Hook | Address | Reg | Role |
|------|---------|-----|------|
| `GF_RTC_CopyDateTime_hook` | **`0x02014708`** | **2** | Pokegear, many field callers |
| `GF_RTC_CopyTime_hook` | **`0x0201474C`** | **1** | BGM / `IsNighttime`, etc. |
| `GF_RTC_TimeToSec_hook` | **`0x020147A4`** | **0** | Overworld **`AreaLightManager`** tint (reads cache, not Copy) |

**Playtest (Nov 2026):** Pokegear matches wristwatch; ecology land period scaled (**Zubat** in caves during real daytime with cave-ignore flag); overworld tint matches after **`TimeToSec`** hook.

### Policy (not RTC hooks)

- **Bug Catching Contest** — preserve the existing clock hooks; duration is **240 game minutes (four hours)**. The elapsed-minute counter advances through the existing RTC update path, which reads accelerated `GF_RTC_CopyDateTime`. At configured **48×**, four game hours nominally equal **five real minutes**. Daily availability is handled through scripts.
- **Weekday events** — prefer removing day gates (e.g. S.S. Aqua) over faking weekdays on the real calendar.

### Still open

[Remaining RTC surfaces](#remaining-rtc-surfaces) — calendar, daily rollover, berry pots, manual rest ([World-9](DESIGN-WORLD.md#world-9-accelerated-daynight-cycle)).

### Remaining RTC surfaces

After **Copy\*** + **`GF_RTC_TimeToSec`**, these still use **other** paths. Accelerated PoC leaves **real calendar** where noted.

| Source | What it reads | Player-visible examples |
|--------|----------------|-------------------------|
| **`Save_SysInfo_RTC`** via **`Field_Get*`** | Save RTC + map-load sync | Scr **`get_hour`**; trades; day care dates; some dungeon light tasks (**`Field_GetTimeOfDay`**, not **`TimeToSec`**) |
| **`GF_RTC_DateTimeToSec`** | Absolute seconds from cache | **Bug Catching Contest** timer; Pal Park; Safari link gift; overlay 112 |
| **`GF_RTC_CopyDate` only** | Real date | Pokéathlon weekday stock; Lake of Rage Wed layout |
| **Calendar on save RTC** | Real **`date_async`** | Daily rollover (apricorns, Pokérus, loto, …) — **real 24h**, not 30 min |
| **`berry_datetime`**, etc. | Save snapshots | Berry pot growth |
| **`UpdateOnFrame`**, penalty | Raw hardware refresh | Clock-set-back punishment |

**Scaled TOD today:** **`CopyTime`**, **`CopyDateTime`**, **`GetTimeOfDay`**, **`GetTimeOfDayWildParam`**, **`IsNighttime`**, **`TimeToSec`**.

---

## Apricorn & custom overworld graphics (Future-1)

**Design:** [Future-1 — Apricorn economy](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) (renewable harvest, new colours such as purple/grey, distributed crafting TBD). Trees are **field objects** placed at map load, not map terrain — placement is zone_event + scr_seq, not Future-4 geometry edits.

### Verified gotcha: do not use `03xx` filenames in `data/graphics/overworlds/`

Sources under `data/graphics/overworlds/*.png` compile to `build/pokemonow/1_<name>.btx0` and repack **`pokemonow.narc`** (`narcs.mk`). For **`1_*`** assets, the **numeric suffix matches the gfx index** referenced from `gOWTagToFileNum` in `src/field/overworld_table.c`.

Follower Pokémon use **`MON_OVERWORLD_GFX_START` (297) + internal species id**:

```c
#define MON_FOLLOWER_ENTRY(species, cbparams) \
    { .tag = ..., .gfx = MON_OVERWORLD_GFX_START + species, ... },
```

So **`0300.png` is not a “free” custom slot** — gfx **300** is **Venusaur** (`SPECIES_VENUSAUR` = 3 → 297 + 3). Adding or replacing **`1_0300.btx0`** without retuning the whole table **inserts or overwrites that narc index**. On a **full / clean** NARC rebuild, every follower (and static OW) with **gfx ≥ 300** can load the **wrong** sheet (**off by one**): e.g. **Turtwig (387 → gfx 684) showing Deoxys (386 → gfx 683)**, **Totodile showing Typhlosion**, and an Apricorn tree object bound to gfx **300** looking like **Venusaur** / the wrong prop.

**Do not** park new Apricorn tree art at **`0300.png`** (or any **`03xx`** that collides with `297 + SPECIES_*` for a real species).

### Safe patterns for new Apricorn tree colours

| Layer | Vanilla reference | New colour (e.g. purple) |
| ----- | ----------------- | ------------------------ |
| Field tree gfx | Tags **262–269** → gfx **251–258**; sources **`0251.png`–`0258.png`** + matching **`.json`** + **`*_pl.pal`** | Pick an **unused gfx index below 297**, name sources **`0NNN.png`** with **`NNN` = that gfx index** (same layout as **`0257.png`** / **`0257.json`** for a 3-frame coloured tree). Register **tag → gfx** in `overworld_table.c` (apricorn trees use callback **`0x5647`** like existing bonguri rows). |
| Bag icon | `data/graphics/item/red_apricorn.png` etc. | New PNG + `data/graphics/itemgra.mk` row + item id in `include/constants/item.h` + msg banks (`222`, `830`, `831`–`833`, …). |
| Map placement | `obj_*_bonguri` in zone_event | New objects + harvest scr_seq; save tree state in `APRICORN_TREE` (`include/save.h`). |

**Alternative:** [HGSS new overworlds guide](https://ds-pokemon-hacking.github.io/docs/generation-iv/guides/hgss-new_overworlds/hgss-new_overworlds.md) — props under **`data/graphics/overworlds/custom/`** → **`2_*.btx0`**, then wire **tag / gfx** explicitly (see comment block at top of `overworld_table.c` and **`narcs.mk`**). Do not assume the filename number is safe unless it matches an unused **gfx** slot in the table.

**More context:** [Overworld System Documentation](wiki/Overworld-System-Documentation.md), [Editing Pokémon Data § overworlds](wiki/Editing-Pokémon-Data.md) (`0297` = Bulbasaur follower filename example).

**Rebuild:** after OW or item gfx changes, full Docker `make` so `test.nds` gets a fresh `pokemonow.narc` / itemgra — verify followers on a new save, not only the new tree.

---

## Open-world starting inventory (new saves)

**Toggle:** `OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS` in `include/config.h` (on by default). Same switch enables Mom starting grants, `openworld_story_skip_flags.inc`, start-city zone_event patches, Magnet Train scr_seq bypass, and slim Mahogany OnLoad when rocket flags are set at Mom intro.

**Testing toggle:** `OPENWORLD_TESTING_GRANTS` in `include/config.h` — dev-only extras (100 Rare Candies silent + HMs 01–08 from Mom). Party-menu Fly needs **`OPENWORLD_FIELD_MOVES_NO_BADGE_GATE`** ([Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags)). Optional commented **`OPENWORLD_STORY_FLAG_SWEEP`** for flag-range bisect ([Story flag range sweep](#story-flag-range-sweep-dev)). **Disable before builds for others** ([CHANGELOG § Dev testing grants](../CHANGELOG.md#new-game--starting-experience)).

**Hook:** Mom downstairs cutscene — scr_seq member **845** (`T20R0201`), script slot **0**.

**Loop fix:** keep vanilla init header **618** (OnFrame `var==0`, like retail). Script **0** sets `VAR_SCENE_PLAYERS_HOUSE_1F = 1` on the first frame before any `wait`, so the cutscene cannot re-trigger. Do **not** move this cutscene to OnTransition — that runs too early and crashes on stairs.

**KB-6:** after the cutscene, **seated Mom** talk is broken (weird menus / wrong conversation). Script **0** only — other **845** slots + **545** text remap may not match vanilla sitting behaviour ([TODO.md KB-6](TODO.md#known-bugs)).

**Grants:** Rebuilt script **0** inserts items/shoes/dex after UI unlock fanfares. `std_give_item_verbose` already waits for A per item — do not add extra `wait_button` between grants; one `closemsg` after **all** item grants (including HM02) clears the window.

| Grant | Item / command |
|-------|----------------|
| S.S. Ticket | `ITEM_SS_TICKET` (456) |
| Pass | `ITEM_PASS` (480) |
| Apricorn Box | `ITEM_APRICORN_BOX` (468) + flag 109 |
| Poké Balls | `ITEM_POKE_BALL` (4) ×5; marts need **`FLAG_UNK_09A` (154)** — `setflag` with Pokégear ([Mart Poké Ball](#mart-poké-ball)) |
| Running shoes | `give_running_shoes` |
| Pokédex | `FLAG_GOT_POKEDEX` + `GivePokedex` |
| National Dex | `nat_dex_flag_action 1, VAR_SPECIAL_RESULT` (opcode 477) after `GivePokedex` — save bits on Pokedex + PlayerProfile, same as Oak’s upgrade. Not a story flag. `ALWAYS_HAVE_NATIONAL_DEX` in `armips/include/config.s` is a separate getter patch (also changes Bug Contest levels); leave off when Mom grants it. |
| Pokégear | `FLAG_GOT_POKEGEAR` + fanfare |
| Town Map card | `UpgradePokegear(1)` only — **do not** use `town_map` / `WorldMapScreen` (cmd 157); it opens the map UI during `lockall` and softlocks on close |
| Phone numbers | `register_gear_number` — Mom (0), Elm (1), Oak (2) |
| Dev testing grants | `ITEM_RARE_CANDY` ×100 (silent `giveitem`) + `ITEM_HM01`–`ITEM_HM08` when `OPENWORLD_TESTING_GRANTS` is defined; Fly field use via [Field HM badge bypass](#field-hm-use-without-per-gym-badge-flags) |

**Starting city / starter (v1 — [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home), [Story-2](DESIGN-STORY.md#story-2-starter-pokémon-and-intro-flow)):**

**Status (Sep 2026):** **18-city menu**, **three-type starter pick** (grass / fire / water, 4 options each → **3** Pokémon), and **step 1 exit** verified in-game. Outdoor home-door routing (**Story-1 steps 2–4**) not complete — step 2 was attempted twice and rolled back; see [Home = bidirectional door + interior swap](#home--bidirectional-door--interior-swap).

| Step | When | What |
|------|------|------|
| 1 | Mom cutscene, before starter menu | **18-city** `ListLocalText` (menu index **0–17**) → `VAR_PLAYER_START_CITY` (**0x4031**) → `_set_home_dynamic_warp` |
| 2 | Same cutscene | **Three** starter menus (grass / fire / water, 4 options each) → **3×** `give_mon` (not `choose_starter`) → `FLAG_GOT_STARTER` |
| 3 | Same cutscene | Mom grants (bag, Pokédex, Pass, etc.) — **no post-cutscene teleport** |
| 4 | Walk to front door **(3, 10)** on 1F | Dynamic exit warp → outdoor home door in chosen city (**Story-1 home step 1 — works**) |

**Menu index = Wilds-1 table row** (direct lookup in `src/wild_level_caps.c`; no PoC remap).

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
- Release design ([Story-2](DESIGN-STORY.md#story-2-starter-pokémon-and-intro-flow)): type-split text menus (grass / fire / water), not Johto/Kanto YES/NO + 3-ball UI.

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

Canonical interior stays **`T20R0201`** (scr_seq **845**, Mom). Four warp behaviours per save ([Story-1 home wiring](DESIGN-STORY.md#home-wiring-four-steps)):

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

**v1:** mass-patched all outdoor home doors → interior **63** — proved warp table, wrong UX. **v2:** ARM9 `Field_InitMapEvents` RAM hook — map-load crashes; hook bytes stuck in `base/arm9.bin` until **`rm -rf base && make`**. **Current / v3 plan:** outdoor doors **vanilla** in ROM; patch **only start city** door → **63** on load (not implemented). Steps 3–4 still open.

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

**Dialogue:** Mom intro greet **545** strings **0–1**. Post-cutscene talk still uses vanilla Elm errand strings until [Story-3](DESIGN-STORY.md#story-3-story-and-script-policy). Cutscene skips bag/card/save/options `npc_msg`s; fanfares + flags unlock touch menu.

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

**Toggle:** same `OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS` gate as Mom grants.

**Assumption:** Pass (`ITEM_PASS` 480) and S.S. Ticket (`ITEM_SS_TICKET` 456) already in bag from Mom; coord gates keep vanilla `HasItem ITEM_PASS` (passes). No Copycat / power-plant story required.

**Members patched:**

| Member | Map | What changed |
|--------|-----|--------------|
| **893** | `T25R0501` Goldenrod station 1F | OnTransition **006**, OnInit **005**, policeman **000** — `FLAG_RESTORED_POWER` (280) gates → unconditional branch to “power restored” path |
| **834** | `T11R0601` Saffron station 1F | Same for **006** / **005** / **000**, plus NPC **001** (weekday-flavour line gated on power) |

**Ride scripts (895 / 836):** unchanged — no power or ticket checks; only play ride animation after coord gate sets boarding vars.

**Patch style:** in-place bytecode (`checkflag 280` + `goto_if` → `goto`); no `build_scr_seq()` rebuild (table layout is non-sequential).

**Files:** `tools/patch_scr_seq_train.py` (`2_893`, `2_834` in narcs.mk), `scripts/dev/verify_train_patch.py`, `scripts/dev/scan_train_power.py`.

**Verify:** `make scr_seq_clean && make test.nds -j24`, then `python scripts/dev/verify_train_patch.py`. In-game: new save → Mom intro → Goldenrod or Saffron station → policeman allows platform → pass coord gate → board train.

**Gotcha:** map header IDs ≠ scr_seq members (`MAP_T25R0501` / `MAP_T11R0601` vs **893** / **834**).

---

## Route 4 ledge boost (Cerulean → Mt Moon)

**Status:** **verified in-game** (Aug 2026). NPC **(1270, 118)** / landing **(1270, 116)** — no coordinate tuning needed.

**Goal:** one-way paid bypass below the Cerulean-side ledge — blackbelt + Machoke boost you up 2 tiles for **$100** (same flow as Route 42 ferry, single shore).

**IDs:** [Field map IDs](#field-map-ids-dont-mix-them-up) — Route 4: header **12**, zone_event **009**, scr_seq **178**, msg **328** (not member **178** on zone_event).

No outdoor-matrix duplicate for Route 4 object coords (unlike Mahogany / Route 44).

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

**Verify:** `make scr_seq_clean && make test.nds -j24`, then `python scripts/dev/verify_r04_boost.py`.

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

**Lighthouse trap (medicine before Jasmine door):** vanilla `scr_seq` **66** slot **0** jumps straight to the heal scene when **`FLAG_GOT_SECRETPOTION`** (185) is set, skipping the door beat that sets **`FLAG_UNK_1D8`** (472). Mom intro sets post-quest lighthouse state (`VAR_SCENE_LIGHTHOUSE_JASMINE` → **2**, **`FLAG_UNK_1D8`**, **`clearflag FLAG_HIDE_JASMINE_IN_GYM`**, **`clearflag FLAG_HIDE_OLIVINE_GYM_GENTLEMAN/GIRL` (476/477)**, … in `openworld_story_skip_flags.inc`). **`tools/patch_scr_seq_olivine_lighthouse.py`** neutralizes OnLoad door-stop script **4** and fixes the potion **`goto_if`** so medicine no longer skips the scene compare. New saves: battle Jasmine in the Gym without doing the fetch; lighthouse top is optional (healthy Amphy dialogue).

**Olivine Gym gossip NPCs (open follow-up):** map **`MAP_T27GYM0101`** (header **80**) → zone_event member **080** (not scr_seq member **913**). Vanilla **obj 1** script **3** @ **(9, 2)**, **obj 2** script **2** @ **(3, 2)** — msg bank **606** lighthouse flavour. Mom intro clears hide **476/477** so they render like post-fetch vanilla. **`setflag` hide alone still allows invisible-tile talk** (do not rely on flags only). Tried removing objs via zone patch — user still saw ghost dialogue (verify map member **080** in-game before further edits). Proper fix: remove or repoint objs on **080**, and/or NOP scr_seq **913** slots **2–3**, and/or replace **606** strings — see [TODO.md § Olivine Gym gossip NPCs](TODO.md#olivine-gym-lighthouse-gossip-npcs).

---

## Mart expansion (`src/field/mart.c`)

**Toggle:** `#define MART_EXPANSION` in `include/config.h` (on in this fork).

**Design:** [World-6](DESIGN-WORLD.md#world-6-shops) (player-facing summary in [CHANGELOG.md](../CHANGELOG.md) § Shops).

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

**Saffron second clerk:** restored — [KB-18](#kb-18--saffron-mart-second-clerk-vanished). Do not delete objects on zone member **365**.

---

## Trade-item evolution (use on Pokémon)

**Design:** [World-5 § Trade evolutions — with held item](DESIGN-WORLD.md#with-a-held-item) — use the held item **on** the Pokémon (like a stone), no trade required.

**Status:** verified in-game Sep 2026.

- **Trade + held item** — use the item on the Pokémon (Metal Coat, Up-Grade, …); see table below.
- **Trade, no item** — use **Linking Cord** (`ITEM_LINKING_CORD`) like a stone; extra `EVO_STONE` + `ITEM_LINKING_CORD` rows in `data/Evolutions.c` (Kadabra, Machoke, Graveler, Haunter, …).
- **Marts (Linking Cord):** first slot — Goldenrod dept **2F lower** (`sGoldenrodDepartmentLower2F`), Celadon dept **4F** (`sCeladonDepartment4F`); price **¥8000** (itemdata).

### How it works

| Layer | File | Change |
| ----- | ---- | ------ |
| Evolution check | `src/individual/GetMonEvolutionInternal.c` | In `EVOCTX_ITEM_USE` / `EVOCTX_ITEM_CHECK`, `EVO_TRADE_ITEM` matches when `usedItem == param` (direct use). Link Cable + held item still works as fallback. |
| Item usability | `data/itemdata/itemdata.c` | Trade-evo held items get `fieldUseFunc = 20`, `partyUse = 1`, `evolve = TRUE` (same as stones). |
| Evolution data | `data/Evolutions.c` | Unchanged — still `EVO_TRADE_ITEM` rows (Metal Coat → Scizor, Up-Grade → Porygon2, …). |

**Items patched:** King's Rock, Metal Coat, Dragon Scale, Protector, Electirizer, Magmarizer, Up-Grade, Dubious Disc, Reaper Cloth, DeepSea Tooth/Scale, Prism Scale.

**Verify in-game:** buy Metal Coat (Olivine) → use on Scyther → Scizor; Up-Grade (Saffron) on Porygon → Porygon2. Wrong species should show “no effect” like stones.

**Not covered:** `EVO_TRADE_SPECIFIC_MON` (Shelmet/Karrablast). Plain trade lines use **Linking Cord** ([World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones)).

---

## Game Corner TM prizes

**Design:** [World-4 § Game Corner TMs](DESIGN-WORLD.md#game-corner-tms) — renewable coin-purchased TMs at both Game Corners.

International HGSS prize menus are **hardcoded scr_seq** (not the unused `sDPPlGameCornerPrizeMap` table from pret’s `scrcmd_dppl_prizes.c`). Each prize block embeds an item id and a coin cost. Submenus: **6 TMs + Cancel**, **4 held items + Cancel**, **3 Pokémon + Cancel**.

| Corner | Pokémon prizes (menu order) |
| ------ | ----------------------------- |
| Goldenrod | Rotom, Wobbuffet, Smeargle |
| Celadon | Porygon, Eevee, Castform |

| Corner | Map | scr_seq member | Text bank |
| ------ | --- | -------------- | --------- |
| **Goldenrod** prize clerks | `T25SP0101` | **910** (`2_910`) | **603** (`data/text/603.txt`) — TM menu lines **15–20** (indices 14–19) |
| **Celadon** prize clerks | `T07R0501` (dept store 5F) | **804** (`2_804`) | **509** (`data/text/509.txt`) — TM menu lines **24–29** |

**Not** the Voltorb Flip floor (`T07SP0101` → scr_seq **806**).

### TM lists

| Corner | TMs (menu order) |
| ------ | ---------------- |
| Goldenrod | TM43 Secret Power, TM64 Explosion, TM44 Rest, TM46 Thief, TM90 Substitute, TM83 Natural Gift |
| Celadon | TM58 Endure, TM41 Torment, TM10 Hidden Power, TM49 Snatch, TM67 Recycle, TM82 Sleep Talk |

| Corner | Held items (menu order) |
| ------ | ----------------------- |
| Goldenrod | Bright Powder, Quick Claw, Wide Lens, Metronome |
| Celadon | Focus Band, Zoom Lens, Scope Lens, Luck Incense |

**Coin costs (temporary):** every TM, held item, and Pokémon prize is **50 Coins** (`PRIZE_COIN_COST` in `patch_scr_seq_game_corner.py`). Flat pricing is a playtest shortcut until [World-4 § Coin income](DESIGN-WORLD.md#coin-income-not-implemented) ships; restore tiered costs when coin income is decided.

### Files

| File | Role |
| ---- | ---- |
| `tools/patch_scr_seq_game_corner.py` | Item-id, coin-cost, species-variable, and prize-level `u16` patches in `2_910` / `2_804` after vanilla extract |
| `scripts/build/verify_game_corner_patch.py` | Patched item ids, costs, species, level 10 GiveMon commands, party-space gates, and protected Goldenrod jumps |
| `data/text/603.txt`, `data/text/509.txt` | Prize menu labels (TMs, held items, Pokémon) |

**Build:** wired in `narcs.mk` after gym scr_seq patches.

**Verify in-game:** Coin Case → Goldenrod Game Corner → right-hand clerk → TM, held-item, and Pokémon submenus; Celadon dept store 5F prize clerk → same lists (different corner).

### Pokémon prize levels and script safety

**Prize level:** all Pokémon prizes at both clerks arrive at **level 10** (`PRIZE_LEVEL` in `tools/patch_scr_seq_game_corner.py`). Each clerk assigns the selected species to variable **0x4002**, then calls one shared **GiveMon** command (**137**): offset **2744** in Goldenrod member **910**, **2359** in Celadon member **804**. The level argument is the `u16` at command offset **+4**; vanilla was **15**.

**Celadon false party-full fix (formerly KB-15; user-tested Nov 16, 2026):** the coin-cost patch at **2209** mistook bytes **05 0D** for price **3333**. Those bytes are actually the conditional-branch condition **5** and the first byte of relative jump **13**, immediately after the party-count comparison against six. Writing **50** corrupted the branch that skips the full-party message. Remove this cost entry; the real 3333-Coin comparison and deduction operands are at **2284** and **2402**. A species patch at **2359** also mistook the GiveMon opcode **137** for Porygon and replaced the command with **351**; remove that entry too. Castform is selected by the species-variable assignment at **2189**.

**Goldenrod control-flow cleanup:** remove species entries at **2621**, **2657**, **2693**, and **2814**. Their vanilla values **23 / 23 / 23 / 27** are relative jump offsets, not species operands. Goldenrod purchases appeared fine in the user's initial test; these were additional confirmed bytecode errors, not the confirmed source of the Celadon symptom.

**Guard against recurrence:** a matching numeric value alone does not prove an offset is an item, price, or species operand. `validate_pokemon_flow` checks both complete vanilla party-space gates, both GiveMon commands (opcode, species variable, level, remaining arguments), and the four protected Goldenrod jumps. The patcher and build verifier both call it. Verification passed on the rebuilt scripts; the user confirmed the playable fix and level change. Existing saves work; reload the rebuilt `test.nds` in DeSmuME.

**Coin income:** prize menus only — earning Coins is still **Voltorb Flip** on the casino floor (scr_seq **806** / `CasinoGame` in **910**). Design requires a non–Voltorb Flip source: [World-4 § Coin income](DESIGN-WORLD.md#coin-income-not-implemented).

**Changing TMs later:** edit replacement tables in `patch_scr_seq_game_corner.py`, update menu strings in the text banks (keep `{CURSOR_X …}` padding if renaming), rebuild.

---

## Overlay 129 — engine code budget

### Overlay architecture and inspecting actual memory use

Vanilla HGSS supplies overlay IDs **0–128**. This HG-Engine build adds **129–151**. Overlay **129** is the resident extension and the default destination for root `src/` custom code. Overlay **130** extends battle; **131** extends field execution. Their RAM ranges overlap because the loader switches contexts; neither is a general-purpose always-resident code region. `src/overlay.c` defines linked-overlay loading and cleanup.

Many individual service overlays reuse **0x023C0400–0x023C4000**. This is an established area for temporarily loaded code, not an automatically safe scratch region. A resident wrapper must arrange loading, call the service, and unload only overlays it owns. Audit the entire nested call chain: loading a second overlay over a still-running caller destroys its code and return target, even if both functions are individually short. Persistent state and callbacks must outlive their overlays appropriately. Not all IDs **133–151** share this range or are mutually exclusive; **134**, **142**, **146**, and **147**, for example, use other regions. The evolution service's alternate placement and ownership handling are a working example; see [Evolution-service overlay relocation](#evolution-service-overlay-relocation).

Overlay **139** (`BattleFormChangeCheck`) starts at **0x023C2400**, rather than the usual **0x023C0400**. Its wrapper in `src/battle/battle_pokemon.c` explicitly unloads vanilla overlay **6**, loads/calls/unloads 139, then restores 6. This is confirmed coexistence handling; the original reason for choosing that exact starting address has not been established. Do not infer that 139 can coexist with every service just because their current compiled ranges appear separate.

Actual ranges are available from the ROM overlay table: **used end = RAM start + initialized code/data size + BSS size**, with end addresses exclusive. These sizes are decompressed RAM footprints, not compressed file sizes, linker capacity or runtime heap usage. `python scripts/dev/dump_overlay_memory.py` exports all entries to `build/overlay_memory_ranges.txt`. `python scripts/dev/build_overlay_viewer.py` generates `build/overlay-memory-viewer.html`, a local browser viewer with address windows, zoom/pan, ID/name filters, code/data versus BSS, descriptions and CSV export. It can also read another local `.nds` directly. Labels and unresolved source hints live in `scripts/dev/overlay_descriptions.json`; unverified vanilla purposes are explicitly unresolved.

Current layout after the Nov 18 resident expansion: **129** occupies **0x023D6000–0x023DDCE9** (**31,977 bytes**, **8,983 bytes free** in its **40 KiB** window ending at **0x023E0000**). It previously started at **0x023D8000**, with only **791 bytes free**. The lower **8 KiB** was reclaimed from unused battle/field capacity; no other overlay's initialized data or BSS intersects the expanded resident window among all **152** ARM9 entries. **130** remains at **0x023C4000–0x023D5D38** (**73,016 bytes**), with a new **72 KiB** linker capacity and **712 bytes free**. **131** remains at **0x023C8000–0x023D2886** (**43,142 bytes**), with a new **56 KiB** linker capacity and **14,202 bytes free**. Both linkers now reject growth past **0x023D6000**.

Expansion implementation: `src/linker.ld`, `src/battle/linker.ld`, `src/field/linker.ld`, trainer-AI prefix assembly, field pointer patchers and budget verifiers use the new boundary. The 96-byte prefix is retained; the custom code starts at **0x023D6060**. `make.py` derives the overlay-table load address from the resident linker and all generated imports/hooks are relinked. Root and suboverlay linker scripts are explicit Make dependencies so address/limit changes cannot leave stale binaries. `python scripts/dev/verify_resident_layout.py` checks packed bytes, every ARM9/ARM7 overlay's code/data+BSS against the resident window, battle/field limits, trainer-AI branches into the relocated prefix, and the compiled boot-load thunk followed by resident code execution. Loader filesystem behavior is adapted in that test; it is not a complete emulator boot. Field pointer, evolution, encounter, Bug-Catching Contest, Center hub, actual ARM Apricorn transaction, Abra and Fly regression checks passed. User smoke test passed on Nov 18 after rebuilding: the expanded layout appears to work normally. For future relocations, restart the ROM and load the in-game save, not a pre-relocation emulator save state; smoke-test field/battle/menu transitions and NPC services alongside automated checks.

**Next time 129 approaches capacity:** consider trimming unused functionality from battle overlay **130**, then extending 129 downward again into the recovered contiguous space. This successfully expanded 129 by **8 KiB** without repeatedly moving individual services into other overlays. Prefer evaluating this layout option before another round of service relocation. Battle currently has only **712 bytes** of growth margin, so further reclamation requires reducing its actual compiled size first; preserve deliberate battle headroom and check field 131 against the same new boundary. Audit all overlay/BSS ranges and other memory users again, update linkers, trainer-AI prefix origin, patchers and verification constants, regenerate all imports/hooks, rebuild the ROM and repeat the automated and in-game checks. Do not merely increase 129's length over live code.

**Battle cleanup candidates:** Wandering Heart does not intend to use Mega Evolution, Dynamax, Z-Moves or Terastallization. Audit these systems and associated UI/support code for removal before the next repartition; the full savings have not been measured. An isolated compile probe disabling Mega Evolution and Primal Reversion reduced `src/battle/mega.c` from **1,296 to 224 bytes**, a **1,072-byte** object-level saving before linker alignment and wider cleanup. Those options remain enabled in production; the probe did not remove any feature. In contrast, removing Mega-specific cry handling from resident `src/pokemon.c` saved only **20 bytes**, and disabling the two options alone saved nothing there. General alternate-form mapping/reversion supports ordinary forms and must not be removed as if it were Mega-only. Reducing 130 creates potential resident capacity only after the memory boundary is explicitly moved again.

Overlay gaps are not proof of free RAM. The broad **0x02280000–0x023C0000** gap is absent from the overlay table, but dynamic heap allocations and other memory users are not shown there; the current heap-3 size at ARM9 **0x020F62BC** is **0x110000 bytes**. Its precise runtime bounds have not been traced. Above 129, **0x023E0000** is also the SDK's initial ARM9 main-arena upper bound; absence of overlays between there and **0x02400000** does not establish reclaimable space. Heap/system/ARM7 reservations need a separate audit before using either apparent gap.

HG-Engine packs most **custom C/asm** into **overlay 129** (vanilla slot **129**, file `base/overlay/overlay_0129.bin`). This fork also uses the **field overlay** (`src/field/`, overlay **131** in `src/field/linker.ld`) for large **read-only tables**. The two share overlapping **ARM9 load addresses** — growing one without a plan can break the other.

### Memory map (ARM9)

| Overlay | Linker | Load origin | Size (linker) | What links here |
|---------|--------|-------------|---------------|-----------------|
| **129** | `src/linker.ld` | `0x023D6000 + 0x60` | `0xA000 − 0x60` (**40 KiB** total window) | All `src/*.c` + `asm/*.s` → `build/linked.o` → `build/output.bin` |
| **Field (131)** | `src/field/linker.ld` | `0x023C8000` | `0xE000` (**56 KiB**) | All `src/field/*.c` → `build/field_linked.o` (evo tables, wild cap matrix, …) |

Field capacity spans `0x023C8000`–`0x023D6000`; battle capacity spans `0x023C4000`–`0x023D6000`. Resident overlay **129** occupies `0x023D6000`–`0x023E0000`. Do not extend either contextual overlay into the resident window; linker limits and packed-ROM checks enforce this boundary.

### Hard limit

- **129 code blob:** `build/output.bin` must stay within **40,864 bytes** (`0xA000 - 0x60`, matching `LENGTH` in `src/linker.ld`). The complete overlay has a **40 KiB** window, including the **96-byte** prefix before the custom blob.
- **Check after `make`:** `wc -c build/output.bin` (PowerShell: `(Get-Item build/output.bin).Length`). Re-check whenever you add root `src/*.c` logic, big `.rodata`, or new asm in `asm/`. The **Nov 16, 2026** cleanup build uses **29,649 bytes**, leaving **3,023 bytes**; remeasure after subsequent changes.
- **Pack into ROM:** `scripts/build/make.py` writes `output.bin` into `overlay_0129.bin` at **`OFFSET_START_IN_129 = 0x60`** (matches the `+ 0x60` in `src/linker.ld`). Do not change one without the other.

### Where to put new data

| Need | Prefer |
|------|--------|
| Large static tables (arrays, generated cap/evo data) | **`src/field/`** — link into field overlay rodata |
| Runtime access from overlay 129 | **`u32 SomeTableFieldAddr`** in root `src/` + **`scripts/build/patch_level_up_evo_addrs.py`** patches the pointer into `build/output.bin` after link (symbols in field ELF, slot in overlay ELF) |
| Small constants / hot path code | Root **`src/`** / **`asm/`** if budget allows |
| Cross-battle scratch that must survive 129 reload | **ARM9 fixed RAM** — see `rom.ld` + [wild caps scratch table](#arm9-scratch-armipsasmwild_level_capss-romld) (`0x021FF900` region). Not the same as field pointers |

**Working examples (data pointers only):** `LevelUpEvoTablesFieldAddr`, `SyntheticEvoEdgesFieldAddr`, `WildLevelCapsFieldAddr` in `src/wild_level_caps.c` → tables in `src/field/level_up_evo_tables.c`, `synthetic_evo_edges_data.c`, `wild_level_caps_data.c`. Wild berry hold: **`WildSpeciesHeldCommonFieldAddr`** / **`WildSpeciesHeldRareFieldAddr`** in `src/wild_berry_hold.c` → `src/field/wild_species_held_items.c`.

**129 budget (Oct 2026):** With ecology PoC + berry hold in 129, measure **`wc -c build/output.bin`** (~**31 KiB** / 32 KiB). **`src/fishing_rod.c`** uses a **heap** family table (not a static array in 129 BSS) — required for link after ecology landed.

**Anti-patterns:**

- Linking multi-kilobyte `.rodata` into root `src/` (bloats `output.bin` fast).
- Reserving field space with a linker hole that pushes field content into **`0x023D6000+`** (clobbered 129 in past experiments).
- Hooks that assume field overlay layout without using patched pointers (129 reloads; field addresses move per build).
- **Calling field overlay functions from 129** via a patched function pointer ([KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls)).
- **`armips/asm/syntheticoverlay.s`** experiments (async overlay **129** load / skipping the hooked prologue) — caused early boot **`0x02000F64`** ARM/Thumb faults on test builds; keep vanilla load unless actively debugging boot.

**Failed approach (home warps):** mid/tail hook on `Field_InitMapEvents` inside overlay 129 — overlap / wrong thunk; abandoned ([failed approaches](#failed-approaches-save-future-dev-time)).

### Hooks and symbols

- **`hooks` / `armhooks`:** `make.py` resolves symbols from `build/linked.o` and each `build/<subdir>_linked.o` (field first in the list) when inserting branches into ARM9 or overlay files.
- **129-only logic** often lives in `asm/other_hook.s` (e.g. wild encounter species hook) calling into `src/wild_level_caps.c` (`-DOVERLAY129` on that translation unit only).

### November 2026 space cleanup

**Measured full builds, Nov 16, 2026:** `build/output.bin` went from **31,541** to **30,057 bytes** after unused-mechanic cleanup, shared location resolution, and battle-table relocation (**1,484 bytes recovered**). The bag/summary refactors then reduced it to **29,649 bytes** (**408 more bytes**, **1,892 bytes total recovered**). Remaining custom-blob capacity is **3,023 bytes**. These are linked binary sizes, not source-line counts; isolated probe savings need not add exactly because of compiler decisions and alignment.

**Unused helpers commented out:** `BufferItemNameGiveItem` (`src/message.c`), `GetGenesectType`, `ChangePartyPokemonToFormSwapMove`, `GenerateShinyPIDKeepSubstructuresIntact` (`src/pokemon.c`), `QMul64_RoundDown` (`src/qmath64.c`), and `EcologyGetGenDebugStage` (`src/ecology_script.c`). Their definitions are retained for reference, excluded from compilation; header declarations alone allocate no code. Inspection included C/asm references, `hooks`, `routinepointers`, and ELF references: absence of a C caller alone does not make a ROM hook unused.

**Unused later-species mechanics commented out:** Genesect held-item/form handling (including its branch in `src/individual/BattleFormChangeCheck.c`); Deerling/Sawsbuck seasonal helpers and their callers; Kyurem/Zacian/Zamazenta move-remapping helper and callers; Reveal Glass, DNA Splicers, Nectar, and fusion-specific party-menu handling. Relevant files are `src/pokemon.c`, `src/item.c`, and `src/individual/PartyMenu_HandleUseItemOnMon.c`. The seasonal function bodies/callers are commented out independently of the `IMPLEMENT_SEASONS` toggle. This is a targeted cleanup, not a blanket removal of every post-Gen-4 feature.

**Preserve shared Gen-4 and item behavior:** Arceus plates, Giratina forms, Shaymin/Gracidea and nighttime reversion, Rotom Catalog, Ability Capsule/Patch, and mints retain their handling. `partyMenuSignal` still supports ability/mint messages; do not remove it as supposedly fusion-only. `PokeListProc_End_Extend` remains as a forwarding shim to vanilla `PokeListProc_End` for the existing routine-pointer target, with its fusion party-count adjustment commented out. Save-layout fields for stored fusion mons remain allocated; do not shrink the save structure as part of this code cleanup.

**Item-use index stability:** `sNewItemFieldUseFuncs` in `src/item.c` keeps six slots in this order: disabled Reveal Glass (`NULL`), disabled DNA Splicers (`NULL`), Ability Capsule, Mint, disabled Nectar (`NULL`), Rotom Catalog. Keep the disabled slots as `{ NULL, NULL, NULL }`; deleting rows shifts the indices encoded in item data. The NULL placeholders themselves save no array space: removing the referenced handler bodies provides the saving. The seven disabled handler definitions are grouped under `// Unused: retained for reference; commented out to save space in overlay 129.` and an explicit preservation note. Do not delete that note or those retained functions.

**Shared map resolution:** `src/encounter_location.c` / `include/encounter_location.h` now provide `EncounterResolveFieldSystem` and `EncounterResolveMapId` to ecology encounters and wild level caps. The former prefers `gFieldSysPtr`, then `sPersistFieldSysPtr`; the latter first reads the current position from `SaveBlock2_get()` local-field save data, then tries the resolved field system's local-field save data, then its `location`. Missing data returns `FALSE`. The old implementations matched before consolidation, and their fallback order is preserved; this matters when field-system pointers are unavailable during battle.

**Battle move-effect table relocation:** the unchanged **432-byte** `move_effect_to_subscripts` array moved from `src/moves.c` (overlay **129**) to `src/battle/move_effect_table.c` (overlay **130**). Its sole consumer is `remap_move_effect_to_subscript_table` in `asm/battle/battle_hooks.s`, also in **130**. The table maps battle move-effect IDs to battle subscripts (status, stat changes, recoil, draining, etc.). Field moves, lead-ability encounter modifiers, fishing bite rates, and wild held-item rolls do not consume this table. In particular, Compound Eyes/item rolls remain in `src/wild_berry_hold.c` on **129**; do not move that runtime logic to unloaded field code (KB-11).

**Bag refactor:** `src/bag.c` uses the small `sPocketOffsets` table with existing `sPocketCounts` for `Bag_GetItemPocket`, `CreateBagView`, and `Bag_GetPocketSlotN`, replacing three repeated switches. Pocket IDs, `BAG_DATA` layout, capacities, and invalid-pocket behavior are preserved. `Bag_TakeItem` resolves the pocket once and delegates removal/compaction to existing `Pocket_TakeItem`, avoiding duplicate logic and a second pocket lookup. The offset entries are byte offsets into the bag, not absolute pointers.

**Summary/nature refactor:** `src/summary.c` prints the five non-HP stat values in a loop, preserving Attack, Defense, Sp. Attack, Sp. Defense, Speed display order. `NatureStatEffect` replaces the **150-byte** nature-effect table: `nature / 5` selects the boosted stat, `nature % 5` the reduced stat, with equal selections cancelling for neutral natures. `windowToStat` maps summary order to nature order (Attack, Defense, Speed, Sp. Attack, Sp. Defense); HP always returns zero. This helper also feeds `ModifyStatByNature`, so preserve equivalence for actual stat calculations as well as summary colors/signs. Mint-aware nature lookup remains unchanged.

**Verification and its limits:** both stages completed Docker `make test.nds -j24` and updated `test.nds`. Offline checks confirmed that the relocated table's **432 compiled bytes** match its source entries, all six patched field addresses match their ELF targets, and packed overlays match the corresponding generated engine/battle binaries. Temporary host C differential checks compared old/new bag pocket addresses, capacities, bounds, view entries, **192 item-removal cases**, and **all 150 nature/stat effects**. Those checks used simulated bags and mocked game calls; they did **not** execute the ROM or validate the UI in DeSmuME. No emulator playtest was performed during this cleanup.

**Playtest coverage:** after reloading the rebuilt ROM, check several consecutive wild/trainer battles with switching and representative move effects (Sleep Powder, Toxic, Swords Dance, Take Down, Giga Drain, Protect, Leech Seed); grass/Surf/fishing/Headbutt/Rock Smash/BCC species and levels across maps and after save reload; bag pockets, item use/removal and compaction; summary raw/EV/IV values, nature colors/signs and mints; Ability Capsule/Patch, Rotom Catalog, Arceus plates, Griseous Orb, and Gracidea/nighttime Shaymin reversion. The lead-ability and held-item systems were not intentionally changed.

**Investigation-only candidates still unimplemented:** local buffers instead of heap allocations in `GetMoveData` and party-menu context creation, byte-sized fishing-family flags, further encounter/learn-move cleanup, and debug-only helper guards. Scratch compile/link probes do not constitute production changes or ROM playtests. Preserve readability and measure the linked blob: caching a repeatedly read value can increase code size even when it reduces runtime work.

### Future systems requiring an overlay 129 budget review

Before implementing any of the following, review the overlay split and measure current `build/output.bin` size. The last measured cleanup build (Nov 16, 2026) leaves **3,023 bytes** out of the **32,672-byte** custom-code allocation; this is shared headroom for all new features, not a separate allowance per system. The estimates below describe likely pressure on overlay 129, not measured byte requirements.

- **[Future-3 — Unlimited learned moves](DESIGN-FUTURE.md#future-3-unlimited-learned-moves): large potential impact.** Shared Pokémon accessors, move learning, save format, and box storage cross field/battle boundaries. Plan data representation, save compatibility, and overlay residency before implementation; do not assume the full system fits in 129.
- **[Future-8 — Dynamic rosters and universal PC](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc): large potential impact.** Collection access, Pokémon transfers, and shared party assumptions span multiple execution contexts. Plan resident adapters separately from battle roster tracking, AI, field services, and UI; assess RAM and save-storage requirements as well as code size.
- **[Future-12 — Unown collection quest](DESIGN-FUTURE.md#future-12-unown-collection-quest): moderate potential impact.** Encounter/form selection, collection progress, and collection-dependent stat calculation may extend shared 129 code. Keep location/form lists and other large tables in external data or verified field rodata; battle ability/damage and capture logic should use their appropriate overlays.
- **[Wilds-3 — Encounter stage probabilities and context](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution): small-to-moderate potential impact.** Wild stage adjustment executes in 129 while trainer generation executes in field code. Extend the shared rules carefully, keep probability tables outside 129, and avoid duplicating large stage-selection implementations.

**Implementation guidance:** keep 129 additions limited to logic that must be available across the required contexts; use field, battle, individual, or explicitly managed overlays for the rest. Do not enlarge the linker window into another overlay's load region, or call unloaded field code from encounter hooks (see [KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls)). Check both code and data residency, measure linked-size changes incrementally, and finish ROM-affecting work with the full playable-ROM build. A successful link or size check does not replace in-game testing.

### Related docs

- Wild distance caps pipeline (uses this split): [below](#wild-level-caps-distance-based--verified-poc).
- Upstream `CONFIG.md` overlay notes are stale; treat this section as canonical for this fork.

---

## Wild level caps (distance-based) — verified PoC

**Status: verified in-game Sep 2026** — distance level rolls ([Wilds-2 level distribution](DESIGN-WILDS.md#level-distribution)), level-up **and synthetic** stage adjust (e.g. Mareep → Flaaffy, Golbat → Crobat @ 30, trade/stone lines from TSV). Sprite, stats, moves, battle name, and caught mon match the final species. Design: [Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), [Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution).

**Toggle:** `IMPLEMENT_WILD_DISTANCE_LEVEL_CAPS` in `include/config.h` (on by default). Comment out to restore vanilla wild levels.

### Formula and table

Build-time cap per `(starting city, encounter area id)`:

```
levelCap = 55 × max(0, route_distance − 1) / (max_route_distance − 1) + 5   // caps in [5, 60]
```

- **Graph data:** `scripts/dev/Route Levels/connections.txt`, `starting_cities.txt`
- **Distances:** `scripts/dev/Route Levels/calculate_location_distances.py` → `location_distances.txt` (includes `MaxDistance` row per city column)
- **Enc area → graph node:** `scripts/dev/Route Levels/encounter_area_graph.tsv` (`ENCDATA_*` index → location name)
- **Post-process:** `scripts/dev/Route Levels/cap_postprocess.tsv` — `fixed` (exact endgame cap) or `floor` (`max(distance, min)`) per graph location name
- **ROM table:** `scripts/build/gen_wild_level_caps.py` → `src/field/wild_level_caps_data.c` + `include/constants/generated/wild_level_caps.h` (Makefile rule in `narcs.mk`)

Runtime lookup: field-overlay `sWildLevelCaps` via patched `WildLevelCapsFieldAddr` — `[startCityIndex][encBank]` where `encBank = MapHeader_GetWildEncounterBank(mapId)`.

**Start city var:** Mom menu sets `VAR_PLAYER_START_CITY` (**0x4031**) to menu index **0–17**; `ResolveStartCityIndex` uses it directly as the Wilds-1 table row (`src/wild_level_caps.c`). Index ↔ city names: [Designated home doors](#home--bidirectional-door--interior-swap) table below.

**Example (Saffron start):** Route 37 → **23**, Violet → **23**, Route 31 → **29**, Dark Cave → **35**, Route 30 → **35**. **Example (Pallet start):** Route 1 → **5** (distance 0–1 both cap at starter floor).

### Runtime pipeline

| Stage | Where | What |
|-------|--------|------|
| Persist FieldSystem | `StoreFieldSysPtr` hook @ `0x0203E028` | Writes `gFieldSysPtr` → ARM9 scratch `sPersistFieldSysPtr` @ `0x021FF900` |
| Cache cap (field) | `WildEncSingle` / `WildWaterEncSingle` in `src/pokemon.c` | `CacheWildLevelCapFromFieldSystem(fsys)` while FieldSystem is valid |
| Apply level (battle) | `modify_species_encounter_data` → **`WildEncounterFinalize`** (`src/wild_encounter_finalize.c`, overlay 129) | Ecology species (scratch method) → form → **`ApplyWildDistanceLevelCapToMon`** → ability → moveset; tail-calls vanilla stub `0x02247B4C` last |
| Stage adjust | `include/encounter_species_stage.h` | `AdjustEncounterSpeciesForLevel` walks prevos (level-up + synthetic), then forward to the stage matching level (`data/synthetic_evolution_thresholds.tsv` → `sSyntheticEvoEdgesData` in field overlay). Overlay 129: patched `LevelUpEvoTablesFieldAddr` + `SyntheticEvoEdgesFieldAddr` |
| Species display | `ApplyWildSpeciesStageForLevel` in `src/wild_level_caps.c` | After `SetMonData(MON_DATA_SPECIES, …)`, call `SetMonData(MON_DATA_SPECIES_NAME, NULL)` — same as `PokeParaSet` — or battle/caught UI keeps the encounter-table name while sprite/stats use the new species |
| Level write | `src/wild_level_caps.c` | Roll level → adjust species → set exp + `MON_DATA_LEVEL` → `RecalcPartyPokemonStats` |
| Held item (if `IMPLEMENT_WILD_BERRY_HOLD`) | `TryApplyWildEncounterHeldItem` → `WildMonApplyHeldItemForEncounter` in **`src/wild_berry_hold.c`** (129) | Species tables via patched pointers — not a cross-overlay **code** call ([KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls)) |

**Map ID:** read from `SaveBlock2` → `LocalFieldData.currentPosition.mapId` (not `fsys->location`, which is often `MAP_EVERYWHERE` during encounters).

**Not hooked:** Safari Zone (`data/SafariEncounters.c`), `modify_species_encounter_data_rare` (roamers), scripted `wild_battle`. Bug Catching Contest is now hooked; see [National Park and contest](#national-park-and-bug-catching-contest-shared-pool).

**Stage adjust:** `AdjustEncounterSpeciesForLevel(species, level, entropy, context, allowBabies)` resolves the family root, then selects forward stages. Plain level-up tables come from `data/Evolutions.c`; `data/synthetic_evolution_thresholds.tsv` classifies fixed, natural-item, trainer-item, and friendship edges. `data/encounter_babies.txt` supplies the ordinary-encounter exclusions. Wild callers carry the actual baby-roll flag through `RollWildLevel` and `ApplyWildEncounterLevelAndStage`, including Bug-Catching Contest generated entries. Trainer context is selected by class, so Leader and Elite Four/Champion rematches keep elite rates while ordinary rematches do not. Branch and probability entropy are derived separately per source species from one slot/encounter seed; a failed roll is not retried during the stage walk. See [Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution) for curves, exceptions, and move-known levels. Existing gender corrections remain in `include/encounter_species_gender.h`.

### ARM9 scratch (`armips/asm/wild_level_caps.s`, `rom.ld`)

| Symbol | Address | Size |
|--------|---------|------|
| `sPersistFieldSysPtr` | `0x021FF900` | 4 |
| `sWildLevelCapDebug` | `0x021FF910` | 32 |
| `sWildCapCache` | `0x021FF930` | 8 |
| `sLevelUpEvoTablesRuntimePtr` | `0x021FF940` | 4 |

`0x021FF940` is zeroed in `armips/asm/wild_level_caps.s` but unused — overlay 129 uses patched pointers into **field overlay rodata**, not ARM9 scratch. (KB-2 work briefly considered a pending-heal byte in scratch after **`0x021FF940`**; step heal does not use it.)

Stage tables live in **contiguous field overlay rodata** (`sLevelUpEvoTablesData`, `sSyntheticEvoEdgesData`). Do not pin them with a linker hole — that bloated the field overlay past `0x023D8000` and clobbered overlay 129.

**Build-time patch:** `scripts/build/patch_level_up_evo_addrs.py` runs after `field_linked.o` + `linked.o` exist; patches overlay 129 **`LevelUpEvoTablesFieldAddr`**, **`SyntheticEvoEdgesFieldAddr`**, **`WildLevelCapsFieldAddr`**, and (when `IMPLEMENT_WILD_BERRY_HOLD`) **`WildSpeciesHeldCommonFieldAddr`** / **`WildSpeciesHeldRareFieldAddr`** in `build/output.bin` (also from `scripts/build/make.py`). Table source: **`src/field/wild_level_caps_data.c`** (generated). If **`WildLevelCapsFieldAddr`** is **0**, cap lookup fails closed to min level. If evo pointers are **0**, wild stage adjust is skipped (`ApplyWildSpeciesStageForLevel` guard in `src/wild_level_caps.c`).

Scratch survives overlay 129 reload; do not reuse these addresses for other features without updating `rom.ld`.

**Overlay 129 size:** must stay **≤ 40 KiB** — see [Overlay 129 — engine code budget](#overlay-129-32-kib-engine-overlay) (measure `build/output.bin`, field vs 129 split, pointer-patch recipe).

### Debug toggles (turn off for normal play)

| Define | File | Effect |
|--------|------|--------|
| `DEBUG_WILD_LEVEL_CAP_LEVELS` | `include/debug.h` | Level = diagnostic code (4–9 fail) or exact table cap on success. **KB-10 pass:** level **5** (`encBank == NA`) on grass/fish/surf — [KB-10](#kb-10--surf-wild-encounters-wrong-species) |
| `DEBUG_WILD_LEVEL_CAP_EXACT` | `include/config.h` | Level = cap exactly (no random roll) |
| `DEBUG_WILD_LEVEL_CAPS` | `include/debug.h` | melonDS `debug_printf` on cache/apply |
| `DEBUG_ECOLOGY_GEN_LEVELS` | `include/debug.h` | Wild level = ecology gen stage **11–21**, **22–27** if `EcologyGenerateWorld` bails ([Wilds-6](#per-save-wild-ecology-shuffle-wilds-6)); normal rolled level ⇒ cap hook not running |

Production: wild/ecology debug toggles **off**; `RollWildLevel(cap)` — adult band **`[⌊0.9×cap⌋−2, cap]`** always; if `cap ≥ 10`, **15%** uniform **2–7** else adult band (never level 1). See [Wilds-2 level distribution](DESIGN-WILDS.md#level-distribution).

### Editing caps

1. Edit graph / distances / encounter mapping under `scripts/dev/Route Levels/`; endgame and HM floors in `cap_postprocess.tsv`.
2. Re-run `python3 scripts/build/gen_wild_level_caps.py` (or full `make` — `narcs.mk` regenerates the table).
3. Rebuild `test.nds`.

**C array gotcha:** `sWildLevelCaps[18][143]` must use **one `{ ... }` brace pair per city row**. Extra top-level `{ ... },` every N values become separate rows in C; columns past the first chunk zero-fill → cap **0** / diagnostic level **8**.

### Scripts layout (this feature)

All tracked — nothing belongs in `scripts/local/`:

| Path | Bucket | Role |
|------|--------|------|
| `scripts/build/gen_wild_level_caps.py` | build | Cap table → `src/field/wild_level_caps_data.c` (`narcs.mk`) |
| `scripts/build/gen_level_up_evo_tables.py` | build | Stage tables → `src/field/level_up_evo_tables.c` + `include/constants/generated/level_up_evo_tables.h` |
| `scripts/build/patch_level_up_evo_addrs.py` | build | Patch `LevelUpEvoTablesFieldAddr`, `SyntheticEvoEdgesFieldAddr`, `WildLevelCapsFieldAddr` in `build/output.bin` (`Makefile`, `make.py`) |
| `scripts/build/gen_synthetic_evo_edges.py` | build | TSV → `src/field/synthetic_evo_edges_data.c` + generated header (`narcs.mk`) |
| `data/synthetic_evolution_thresholds.tsv` | data | Authoring source for synthetic stage edges (`from`, `to`, `method`, `min_level`, `branch`, `requirement`) |
| `include/species_stage_for_level.h` | include | `AdjustSpeciesForLevel` (level-up forward bands only; used internally) |
| `include/synthetic_evo_apply.h` | include | `PickSyntheticEvolutionStep` (inline; reads `gSyntheticEvoEdgesPtr`) |
| `include/encounter_species_stage.h` | include | `AdjustEncounterSpeciesForLevel` — unified prevo walk + forward stage (wild + trainer) |
| `scripts/dev/verify_encounter_stage.py` | dev | Offline sanity check for trade/stone devolve cases (Alakazam, Vileplume, …) |
| `scripts/dev/Route Levels/calculate_location_distances.py` | dev | Regenerate `location_distances.txt` after graph edits |
| `scripts/dev/Route Levels/*.txt`, `encounter_area_graph.tsv`, `cap_postprocess.tsv` | dev | Source graph inputs |

**Not in `scripts/local/`:** wild-cap and synthetic-stage tooling is all under `data/`, `scripts/build/`, and `scripts/dev/Route Levels/`. Session throwaways stay gitignored per § Scripts layout.

**Generated (rebuilt every `make`):** `include/constants/generated/wild_level_caps.h`, `level_up_evo_tables.h`, `synthetic_evo_edges.h`. `.c` outputs may be committed for convenience (`src/field/wild_level_caps_data.c`, `level_up_evo_tables.c`, `synthetic_evo_edges_data.c`). `wild_level_caps.o` uses `-DOVERLAY129` for patched field pointers.

### Editing synthetic stage edges

1. Edit `data/synthetic_evolution_thresholds.tsv`: `method` is `fixed`, `natural_item`, `trainer_item`, or `friendship`; `min_level` is required for fixed edges and retains old baby thresholds for baby-roll compatibility. Item and friendship edges otherwise leave it empty. `branch` is empty or `random` (uniform among permitted outcomes, including more than two). `requirement` labels the move/item for author review. Ordinary encounter baby exclusions live in `data/encounter_babies.txt`.
2. Run `python3 scripts/dev/verify_encounter_stage.py` inside Docker/Linux. It compiles the actual shared C and checks method curves, baby-roll handling, class tiers, branch outcomes, move-learnset alignment, and multi-stage probabilities.
3. Full `make` (or `python3 scripts/build/gen_synthetic_evo_edges.py`) regenerates field rodata.
4. Rebuild `test.nds` — confirm both patch lines in the build log.

---

## National Park and Bug-Catching Contest shared pool

**Status:** built and host-verified; needs in-game verification on a new save. Design: [Wilds-6 § National Park](DESIGN-WILDS.md#national-park-and-bug-catching-contest).

- `data/ecology/ecology_locations.tsv` contains one **National Park Bug Catching Contest** group for encounter banks **23 and 24**, preserving Headbutt as a separate bucket. `gen_ecology_compatibility.py` pins the 17 `BCC` families into its land bucket and overrides ordinary land habitat restrictions only there. Other areas keep eight land slots. Required placement skips partners already placed in that bucket, so Volbeat/Illumise do not consume duplicate slots.
- `src/ecology_encounter.c` samples the same saved assignment for both maps, retaining time eligibility and selecting uniformly among currently eligible slots. All 17 park families occupy one slot each, so rarity does not affect their encounter odds. Filtered eligible-slot indexing is applied once.
- Overlay **2**, **0x02247ED8**: replace the seven-argument contest internal generator with `BugContest_GenerateEcologyEncounter` in overlay 129. It caches the cap, builds an independent wild mon through the shared ecology finalizer, checks Repel against the final level, guarantees one perfect IV, and adds the mon to the enemy party. Vanilla Repel helper **0x02248290** stays in overlay 2.
- Overlay **24**, **0x02259DF0**: BugContest_InitEcologyEntries keeps the five vanilla NPC identities. Each NPC rolls five actual temporary Pokémon from the park pool and level distribution, with random nature/IVs, zero EVs, and one guaranteed perfect IV. ApplyWildEncounterLevelAndStage shares the player encounter stage, experience, gender, and stat recalculation path. The highest six-stat total and its final species are retained. One allocated buffer is reused and freed; retail contest size **0xC0** and contestant offset **0x70** remain unchanged.
- Overlay **24**, **0x02259E60**: BugContest_JudgeEcologyMon returns zero for no catch, otherwise the same ContestStatTotal used for NPCs: maximum HP plus the five other stats. No explicit rarity, IV, level, or current-HP terms remain. Text bank **246** explains the total-stat rule and removes the old low-HP judging advice.
- Overlay **24**, **0x022599FA**: BugContest_AssignPrize_hook replaces only the prize-selection tail of vanilla judging, preserving ranking and placement. BugContest_AssignPrize selects one item from the placement pool in DESIGN-WORLD and writes the existing prize field. Vanilla announcements, quantity-one delivery, and bag-full pending-prize storage use that same selection. The hook returns through the native saved-register frame; verify_bug_contest_ecology.py checks both the patched target and stack-frame compatibility.
- `bytereplacement` raises the contest limit from **20** to **240 game minutes** at overlay **1**, **0x021E7A7E** (expiration comparison), **0x02202A9A** (remaining-time comparison), and **0x02202A9E** (remaining-time subtraction). The remaining-time formatter at **0x02202AB0** allows three digits so **240** displays correctly. The receptionist's introduction in text bank **246** says **4 hours**; remaining-time messages still show minutes. No clock hooks or speed settings change.
- `scripts/build/make.py` includes overlay **24** in `OVERLAYS_TO_DECOMPRESS`; its retail file is compressed, so hooks must be applied after decompression.
- `scripts/build/patch_bug_contest_daily.py` patches scr_seq **151** (shared registration), **242** (Route 35 gate), and **245** (Route 36 gate) in place. Both gates use the contest NPC configuration every day. Registration uses a local Tuesday selector for valid vanilla opponent identities; the real calendar and **FLAG_DAILY_DID_BUG_CONTEST** remain unchanged. Text bank **246** describes daily availability and retains the compressed `{TRNAME}` NPC-name markers. Verify with `python3 scripts/build/patch_bug_contest_daily.py build/a012 --verify`.

Verify after a full build and `make -C tools/source/ecologygen`: `python3 scripts/dev/verify_bug_contest_ecology.py`. This checks eight assignment seeds, all three time periods, original hook signatures, hooks in **test.nds**, and equal park caps for all 18 starting cities. Also run `verify_encount_overlay2.py` and `verify_overlay129_field_addrs.py`.

Playtest normal grass and contest battles from near/far starts, including babies, evolved catches, Repel, catch replacement, no catch, timeout/balls exhausted, judging, prizes, party restoration, and full-party PC delivery.

## Per-save wild ecology shuffle (Wilds-6)

**Design:** [Wilds-6](DESIGN-WILDS.md#wilds-6-per-save-wild-ecology-shuffle). Deferred addon scope (Gym hints, flash persistence, other methods): [Future-5](DESIGN-FUTURE.md#future-5-wild-ecology--remaining-scope). This section is the **implementation recipe** for authoring, prebuild compat, offline assignment tests, and the in-ROM PoC.

**Status (Nov 2026):** **Compat + Mom gen + encounter hooks + flash persistence shipped** — Mom gen freeze fixed ([KB-14](#kb-14--mom-ecology-gen-freeze-overlay-131-compat-pointer)). World generated on **`SCRIPT_NEW_CMD_ECOLOGY_GENERATE`**; seed = trainer ID; **`EcologyWorldSave`** in **`SAVE_MISC`**. **`SetEncountData_Ecology`** @ **`7B64`** rolls species for **grass, Surf, rods, Headbutt, Rock Smash** ([KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata)). Placeholder species **Wooloo** (level 5) until **`WildEncounterFinalizeForEncount`** runs. **Still open:** swarms/Safari/special policy, real mon creation (drop placeholder **`PokeParaSet`**). Lead-overwrite bug fixed ([KB-13 / KB-17](#kb-13--kb-17--wild-encounter-overwrote-the-party-lead-fixed)). **Cave land time:** **`ECOLOGY_GROUP_FLAG_CAVE_IGNORE_LAND_TIME`** (Cave habitat only; encounter roll in **`ecology_encounter.c`**). **Pairing** + **Required on Route** + baseline ladder: [ecology.md](ecology.md).

**Goal:** Assign shuffleable **families** to placement **groups** and methods; persist per save; hooks read assignment instead of static NARC species. **Next:** swarms, category rules for gifts/statics/legendaries, gen rules for new eco-fam columns.

### Ecology ROM integration (in-ROM PoC)

Toggle: **`IMPLEMENT_ECOLOGY_GENERATION`** in `include/config.h`.

| Step | Where |
|------|--------|
| Compat blob | **`build/ecology/ecology_compat.bin`** → code addon **`CODE_ADDON_ECOLOGY_COMPAT` (19)** in NARC `a/0/2/8` member **`9_19`** (`data/codetables.mk`, `make move_narc`) |
| Runtime load | **`EcologyCompatLoadFromFilesystem`** → heap bind in `src/ecology_load.c` |
| Generation | **`EcologyGenerateWorld`** in `src/field/ecology_generate.c` (overlay **131**, Mom via **`EcologyGenerateWorldFieldAddr`**) |
| Session + flash | **`EcologySaveWriteGeneration`** → session; **`EcologySaveWriteFlash`** → **`SAVE_MISC_DATA.ecologyWorldSave`** (`src/ecology_save.c`) |
| Session trigger | Mom **`SCRIPT_NEW_CMD_ECOLOGY_GENERATE`** → **`EcologyRunNewGameGeneration`** (`src/ecology_script.c`) |
| Reload | **`EcologySaveGetMutable`** copies valid flash blob into session when heap copy invalid |
| Species override | **`src/ecology_encounter.c`** + `asm/other_hook.s` |
| **131 code call from 129** | **Wild encounter hot path:** do **not** call **131** functions from **129** ([KB-11](#kb-11--undefined-instruction-from-overlay-129--field-code-calls)). **Mom gen:** **129** calls **`EcologyGenerateWorld`** in **131** via patched **`EcologyGenerateWorldFieldAddr`** — compat must flow through the **`view`** argument ([KB-14](#kb-14--mom-ecology-gen-freeze-overlay-131-compat-pointer)). **Encounter override** stays **`src/ecology_encounter.c`** on **129**. |

**Do not** link full compat CSR into field overlay **131** or root `src/` rodata (~38 KiB+) — use the NARC blob only. **`EcologyGenerateWorld`** + large field tables live in **`src/field/`** (overlay **131**); **`ecology_load.c` / `ecology_script.c`** stay on **129**. Host **ecologygen** links **`src/field/ecology_generate.c`** + **eco-host-csr** under **`tools/source/ecologygen/`**.

**Overlay pitfalls (Oct 2026 detours — avoid repeating):** **`PrizeMoney`** / **`src/battle/trainermoney.c`** belongs in **battle overlay 130** (overlay **12** repoints via **`GetSymbols()`**); do **not** put the table in **field 131** (unloaded in battle). Do not duplicate **`EncounterSlot_*`** in **129** without a **`GetSymbols()`** plan; **129** ROM is tight (~tens of bytes margin).

### Ecology file shorthand

| Shorthand | Path | Role |
|-----------|------|------|
| **eco-fam** | `data/ecology/ecology_families.tsv` | Author families (habitat columns, rarity, demand, Avoid Tag, …) |
| **eco-loc** | `data/ecology/ecology_locations.tsv` | Author groups (ENCDATA symbols, Water, Habitat, Types, method presence) |
| **gen-compat** | `scripts/build/gen_ecology_compatibility.py` | TSV → ROM CSR + human dumps |
| **dump-fam** | `data/ecology/ecology_compat_by_family.tsv` | Audit: where each family *may* appear (split by `type_match`) |
| **dump-grp** | `data/ecology/ecology_compat_by_group.tsv` | Audit: who *may* appear per group / method / `type_match` |
| **compat-h** | `include/constants/generated/ecology_compat.h` | C structs, counts, `ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE` |
| **eco-bin** | `build/ecology/ecology_compat.bin` | Runtime compat blob (packed header + CSR; shipped as **9_19**) |
| **eco-host-csr** | `tools/source/ecologygen/ecology_compat_data.c` | Host **ecologygen** tables (not linked into field overlay) |
| **eco-strings** | `tools/source/ecologygen/ecology_strings_data.c` | Group/family names (host **ecologygen** + debug) |
| **gen-core** | `src/field/ecology_generate.c` (ROM + host **ecologygen**), `include/ecology/ecology_generate.h` | Per-seed assignment ([ecology.md](ecology.md)) |
| **ecologygen** | `tools/ecologygen` (build: `tools/source/ecologygen/`) | Host CLI over **eco-host-csr** |
| **run-eco** | `scripts/dev/run_ecology_generate.py` | Regen compat (optional), build **ecologygen**, write **assign** |
| **assign** | `build/ecology/ecology_assignment.tsv` | One deterministic test world (not committed) |

**Pipeline:** **eco-fam + eco-loc** → **gen-compat** → **eco-bin** + **dump-*** + **eco-host-csr** / **compat-h** → **assign** (via **run-eco** or in-game Mom when PoC on).

### Workflow (agents)

1. Edit **eco-fam** / **eco-loc**.
2. **`make ecology-compat`** — runs **gen-compat** + `scripts/dev/verify_ecology_compatibility.py`, then repacks ROM (see `Makefile`; heavier than a table-only regen). Normal **`make test.nds`** runs **gen-compat** when TSV inputs change (via **eco-bin** dependency).
3. For assignment experiments only:  
   `python scripts/dev/run_ecology_generate.py --seed 0xDEADBEEF`  
   On Windows (no native `gcc`), **run-eco** builds **ecologygen** inside Docker automatically.
4. Commit: **eco-fam**, **eco-loc**, **dump-fam**, **dump-grp**, **eco-host-csr**, **eco-strings**, **compat-h** (+ **gen-compat** / **gen-core** when logic changes). **assign**, **eco-bin**, and **ecologygen** binary stay gitignored unless you intentionally refresh committed host tables after TSV edits.

### Ecology compat (prebuild) rules

**gen-compat** builds edges `(family, group, method)` stored in **eco-csr** (land list + per-method buckets). Families with `Special` or `Encounter Methods` = 0 are excluded from shuffle.

| Check | Source | Notes |
|--------|--------|--------|
| Habitat | eco-fam Field/Mountain/Forest/Cave/Ruins/Tower vs eco-loc `Habitat` | Land only |
| Wet/Dry | eco-fam `Wet/Dry` vs eco-loc `Water` | Land / headbutt / rock smash. **Water** column is comma-separated: `Dry`, `Fresh`, `Salt`, `Cave` (salt = sea). Surf/rod ignore `Dry` for water-type rules. |
| Required Tag | eco-fam `Required Tag` must appear in eco-loc `Types` | Inclusion when tag set |
| **Avoid Tag** | eco-fam `Avoid Tag` (comma types) ∩ eco-loc `Types` | **Hard exclude** entire group for that family |
| Land time | eco-fam `Nocturnal` vs group period mask | Intersection must be non-empty for land |
| Fishing / Surfing | eco-fam vs method | Surf vs Fish vs Both |
| Water type (family) | Salt/Fresh/Cave… vs non-Dry water tokens on group | Surf / rods |
| **Type overlap** | Type1, Type2, Type (Vibe) vs eco-loc `Types` | Sets edge flag **`ECOLOGY_EDGE_TYPE_MATCH`** — **not** a hard filter (except themed land fill; see below) |

National Park's normal and contest encounter banks share one group; the authored `Bug Catching Contest = BCC` families supply its 17 required land entries. See [National Park and contest](#national-park-and-bug-catching-contest-shared-pool).

**Version:** `ECOLOGY_COMPAT_VERSION` = first 4 bytes of SHA256(**eco-fam** + **eco-loc**).

### Slot budgets (shuffle targets)

Derived in **gen-compat** from eco-loc columns (presence = `> 0`, not the numeric value):

| Method | Slots when present |
|--------|-------------------|
| Land | **8** total (shared across time — not 24×3); National Park exception: **17** |
| Surf | **3** |
| Old Rod | **2** |
| Good Rod | **1** |
| Super Rod | **1** |
| Headbutt | **3** |
| Rock Smash | **2** |

**Morning / Day / Night** on eco-loc: which **periods exist** (`landPeriodMask`), not slot counts. Runtime (future) rolls only slots whose **`land_time`** mask matches the current period.

**Rods (future in-game):** Good Rod encounter roll = pool(**Old** ∪ **Good**); Super Rod = **Old** ∪ **Good** ∪ **Super**. **assign** / **gen-core** still fill three separate buckets for inspection; merge at hook time.

### Ecology assignment (gen-core)

**Entry:** `EcologyGenerateWorld(…)` in **`src/field/ecology_generate.c`** (overlay **131**). Deterministic LGC (`1664525` / `1013904223`). Phases: required routes → unplaced → route baseline ladder → fill — see [ecology.md](ecology.md).

### Mom gen — overlay 131 vs host ecologygen

**Call chain:** Mom **`SCRIPT_NEW_CMD_ECOLOGY_GENERATE`** → **`EcologyRunNewGameGeneration`** (**129**, `src/ecology_script.c`) → load/bind **eco-bin** → heap scratch → **`EcologyGenerateWorldFieldAddr`** → **`EcologyGenerateWorld`** (**131**).

**Debug stages** (`DEBUG_ECOLOGY_GEN_LEVELS` in `include/debug.h`): **11–21** on Mom path; **22–27** = early exit inside **`EcologyGenerateWorld`** (e.g. **23** = null **`view`** / **`gEcologyCompatView`** at gen entry). Wild-level channel is useless if Mom never returns.

**Size checks (after `make`):**

```bash
wc -c build/output.bin build/output_field.bin   # 129 ~30 KiB / 32 KiB cap; 131 ~40 KiB / 96 KiB cap
```

**Host timing (Docker, seed `0xC0FFEE`, ~1150 slots):** full **`tools/ecologygen`** run **~30–45 ms** (includes TSV write). That is **not** a profile of ARM **131** execution.

**Clean rebuild when ecology feels stale** (compat version, **`9_19`**, or after **`git`** revert):

1. Remove stale host objects: **`tools/ecologygen`**, **`tools/source/ecologygen/*.o`**, **`src/field/ecology_generate.o`**, **`src/ecology_layout.o`** if present.
2. **`make clean`** (drops **`build/`**, **`base/`**, **`include/constants/generated/`**).
3. **`python3 scripts/build/gen_ecology_compatibility.py`** + **`verify_ecology_compatibility.py`** (or **`make ecology-compat`**).
4. **`make -C tools/source/ecologygen clean && make`** — keep host **`.o`** files **inside** **`tools/source/ecologygen/`** only (see pitfall below).
5. **`make test.nds -j24`** (default **`make`** does **not** pack **`test.nds`** — need explicit target).

**Pitfall — `make test.nds` / `make.py`:** Default **`%.o: %.c`** for **`tools/source/ecologygen`** can compile **`../../../src/field/ecology_generate.c`** → **`src/field/ecology_generate.o`**. **`make.py`** treats any **`src/*`** entry without **`.c`** in the name as an overlay (e.g. **`ecology_layout.o`**) and fails looking for **`build/ecology_layout.o_linked.o`**. **Fix:** host Makefile should emit **`host_ecology_generate.o`** under **`tools/source/ecologygen/`** only; delete stray **`src/*.o`** before **`make test.nds`**.

**New save after compat bump:** **`ECOLOGY_COMPAT_VERSION`** in flash must match **eco-bin** shipped in **`9_19`**; regen compat → rebuild ROM → **new save** for Mom gen.

**Fill rarity weights** (Normal / Common / Rare only; Very Rare excluded from fill): **3 / 9 / 1** (no extra weight on `type_match`).

**Rod rarity gates** (assignment only; compat lists may still list other rarities):

| Rod | Allowed rarities |
|-----|------------------|
| Old | Common only |
| Good | Common + Normal |
| Super | All tiers |

**Land time on assign:** Each land slot gets effective mask = family nocturnal mask ∩ group period mask. **assign** column **`land_time`**: blank = all periods at that location; else `Morning`, `Night`, `Morning, Night`, etc.

### Typed locations (land theme slots)

When eco-loc **`Types`** is non-empty, **gen-compat** stores `sEcologyGroupLocationTypeCount[group]`.

**Land fill:**

1. Target themed slots = **`ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE` (3) × type count**, capped by land capacity (8).
2. Until target met: pick only **`type_match`** land compat entries (rarity weights only).
3. Remaining land slots: pick from **non–type_match** pool only.
4. If themed pool cannot satisfy target, fall back to general pool for unfilled themed slots (see audit).

**Demand phase** can still place **type_match** families on themed routes **before** fill, so **assign** may show **more** than 2 themed families on single-type routes (e.g. three Fire lines on Cinnabar). Hard cap including demand is not implemented yet.

**Untyped locations:** all land compat eligible; rarity-weighted fill only.

**Phases 2–3 edge pick:** per placement attempt, **50%** try **`type_match`** edges first (then others), **50%** the reverse — see [ecology.md](ecology.md).

### Typed land pool shortfalls (audit)

Compare **dump-grp** Land `type_match=1` family count vs **2 × |Types|** for groups **with land**. Insufficient themed compat (Oct 2026 data):

- **0 themed families:** Route 10 (Electric), Route 4/9/24 (Water).
- **1 themed family (need 2):** Route 37, Route 38 (Ghost — only Drifloon).

Many **cities** carry a `Types` tag but **no land** slots (surf/headbutt only); land theme guarantee does not apply there.

Re-run audit after eco-fam edits:  
`python scripts/local/_typed_pool_audit.py` (session helper; move to `scripts/dev/` if promoted).

**Still open (Wilds-6):** swarms policy, Gym hints ([Future-5](DESIGN-FUTURE.md#future-5-wild-ecology--remaining-scope)). Runtime reads **eco-bin** NARC only — not field-overlay CSR ([Overlay 129 budget](#overlay-129-32-kib-engine-overlay)).

### SAVE_MISC flash (`EcologyWorldSave`)

Embedded **`struct EcologyWorldSave`** in **`SAVE_MISC_DATA`** (`include/save.h`). Hook **`Sav2_Misc_sizeof`** only — do **not** hook **`SaveData_InitSubstructs`**.

| Piece | Detail |
|-------|--------|
| Magic | **`ECO1`** (`ECOLOGY_SAVE_MAGIC`) |
| Payload | **`u8 familyIds[1012]`**, sparse **`(familyId, landTimeMask)`** for families with ROM land-time (max **96**) |
| Write | **`EcologySaveWriteFlash`** after Mom gen |
| Load | **`EcologySaveGetMutable`** hydrates session from flash when needed |
| Compat TSV version | **`compatVersion` field** written at gen; **not** used to invalidate saves after TSV regen — keep frozen assignment until new game |
| Verify in-game | **`DEBUG_ECOLOGY_GEN_LEVELS`**: wild level **28** when flash valid after Mom + save + reload |
| Verify in `.dsv` | **`python scripts/dev/probe_ecology_in_dsv.py`** `<path/to/test.dsv>` |

**Size note:** Misc chunk grew from header-only era; total **`Sav2_Misc_sizeof`** ~**0xB70** with compact blob (well under Phase-A probe cliff ~**0x12A0**).

### Scripts (Wilds-6)

| Path | Bucket | Role |
|------|--------|------|
| `scripts/build/gen_ecology_compatibility.py` | build | **gen-compat** |
| `scripts/dev/verify_ecology_compatibility.py` | dev | Sanity + regen via **make ecology-compat** |
| `scripts/dev/run_ecology_generate.py` | dev | **run-eco** |
| `scripts/dev/verify_encount_overlay2.py` | dev | Post-**`make test.nds`** — **`7B64` / `7B42`** vs **`hooks`** + **`linked.o`** ([KB-12](#kb-12--wild-ecology-encounter-hooks-setencountdata)) |
| `scripts/dev/probe_ecology_in_dsv.py` | dev | Scan DeSmuME **`.dsv`** for **ECO1** / assignment summary |
| `scripts/dev/verify_save_misc_size.py` | dev | Print **`Sav2_Misc_sizeof`** from **`build/save.o`** |
| `tools/source/ecologygen/` | tools | Host **ecologygen** (`-DECOLOGY_STANDALONE`) |

See also [`scripts/README.md`](../scripts/README.md) ecology bullets.

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

**Header vs NARC members:** [Field map IDs](#field-map-ids-dont-mix-them-up). Johto outdoors use **world `(x, z)`** in zone_event (local coords on interiors / small maps). Matrix seams → patch **two** `eventsBank` members (Mahogany **084** + **043**, Route 24/25, …).

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

## Shared Pokémon Center hub (World-10)

`SHARED_POKEMON_CENTER` in `include/config.h` routes the 24 ordinary Centers into Route 32 1F (`MAP_R32PC0101`, header 169), preserving its basement (170) and nurse/PC services. **Indigo Plateau is excluded**: its outdoor entrance, League lobby, scripts, and Elite Four access retain their existing behavior. No exterior warp tables are rewritten.

`src/center_hub.c` fully replaces vanilla `sub_02052F94` at ARM9 **0x02052F94**, resolving the destination before map events load while retaining vanilla previous-position, warp-anchor, and dynamic-warp bookkeeping. The shared front door resolves to the originating Center's original outdoor map/warp. Returning from the shared basement or Union Room preserves the origin. Mom's house/elevator dynamic-warp slot remains independent. Avoid the previously failed mid-function `Field_InitMapEvents` approach.

`SAVE_MISC_DATA.centerHubOrigin` occupies the three former padding bytes at **0x2DD–0x2DF**: magic `CH` and a stable 1-based Center ID. The save chunk size and following field offsets do not change. Never reorder `gCenterHubDoors`; append future destinations. Older/invalid records fall back to Route 32. Loading a save inside the hub preserves both player position and origin; a save made in another legacy Center stays there until the player next enters a Center. Runtime reload/flash behavior still needs emulator playtesting.

The second hook, ARM9 **0x0203BB20** (`MapHeader_GetSpawnIdForDeathWarp`), uses the origin's original interior for blackout lookup, retaining the vanilla spawn table and each location's enabled/disabled blackout policy. Fly unlocks remain attached to the unchanged outdoor maps.

Validation: Docker `make test.nds -j24`, then `.venv/bin/python scripts/dev/verify_center_hub.py` inside Docker; run `python scripts/dev/verify_r32_outdoor_rod_guru.py` for the fisherman. Routing host tests: `gcc -w -DCENTER_HUB_HOST_TEST -Iinclude src/center_hub.c scripts/dev/test_center_hub.c -o build/test_center_hub && build/test_center_hub` inside Docker. In-game: enter from two different cities, exit to each original door, save inside/restart/exit, visit the basement and return, and verify Indigo's entrance remains normal.

### Hub Abra travel

The Psychic handler (object **7**, sprite **351**, local **(10, 19)**) and Abra (object **8**, follower tag **2563**, local **(11, 19)**) stand to the right of the entrance, both initially facing north. `scripts/build/patch_center_abra.py` appends slots **6/7** (scriptIds **7/8**) to member **233** after crafting; previous script bodies, relative branches, and warp indices are preserved. Text bank **381**, messages **32–37**. Fare is **$400**, checked before the map and again before departure. Cancellation, invalid/unvisited selections, insufficient money, and allocation failure never charge.

`src/abra_travel.c`, custom command **208/subcommand 6**, uses mode **0** to launch native Fly picker **0x0203EAB0**, mode **1** to consume/free its **0x2C-byte PokegearArgs** result in script environment field **20**, and mode **2** to validate/pay/start Teleport. The native callback waits for application exit without freeing arguments prematurely. Read/free the result before `RestoreOverworld` (command 150); restore/fade in the Center, then open/close the departure message before starting Teleport. Avoid the ordinary Town Map callback that frees args before selection can be read.

The picker retains saved Fly visit flags and uses the originating Center's exterior and special-spawn matrix coordinates for its marker/cursor. Transient `args.x/z` use the **neutral Indigo coordinate (28, 6)** solely for `Pokegear_GetCurrentRegion`, allowing both Johto and Kanto within this picker; `matrixX/Y` stay at the actual source. No overlay-101 hook, ordinary Fly change, real player-location change, Indigo map change, or visit-flag writes are needed. Before charging, validate the result against the vanilla Fly-enabled spawn table and flag **0x9B0 + entry flag**.

Native Teleport departure steps **0x0224C71C**, **0x0224C75C**, **0x0224C7D4** operate on the original **0x30-byte** effect environment. Start at step **2** to omit the party Pokémon cut-in: the static Abra provides the service, with no party move or badge requirement. After cleanup, **0x02053B04** starts arrival kind **2** (Teleport), using Fly's exact outdoor destination and special-spawn data. Last blackout spawn and saved Center origin are not repurposed. Towns without a Center use their ordinary Fly landing spot.

Before native step **2**, the service waits for purchase SE **1603** using native `IsSEPlaying` **0x02006184** so Teleport's SE **1613** does not interrupt it. Departure movement **0x02253820** accelerates (pause commands decrease from **2** to **1**, then no pauses); arrival movement **0x02253884** decelerates (pauses increase from **1** through **5**). The ARM verifier also checks those sequences in the packed ROM; animations themselves remain vanilla.

NPC idle facing: zone-event movement types **14/15/16/17** force **up/down/left/right** on their first update, overriding `facingDirection`. Both Abra service objects use **14**. Type **0** has no direction override (the vanilla Apricorn giver uses this with direction **3**, right). Do not use type **15** as a generic stand-still setting when another direction is intended; this also explains earlier fisherman-facing issues. Native movement table **0x020FD1F4**, initialization **0x02061690–0x020616B4**, update **0x0206166C**.

Validation: Docker `make test.nds -j24`; `python scripts/dev/verify_center_abra.py` checks compiled script flow/window/application transitions; `python scripts/dev/verify_abra_travel_arm.py` executes compiled ARM code with deterministic engine adapters (requires `unicorn`; session-local install supported). Tests cover argument layout, wait/free ordering, source marker, both-region context, all native landing entries, visited-only acceptance, cancellation, exact/insufficient funds, allocation failure, revalidation, charging, native animation API wiring, and unchanged blackout/origin bytes. These do not render GUI/effects: playtest selection/cancellation, both regions, Teleport departure/arrival, wallet, NPC tiles, and existing services in DeSmuME. Reload and re-enter the Center to refresh NPCs on an existing save.

### Hub Apricorn crafting

Overlay placement: `src/apricorn_craft.c` is a small resident dispatcher in 129; the transaction and colour table live in `src/field/apricorn_craft.c` in 131. `patch_level_up_evo_addrs.py` patches `ApricornCraftFieldAddr` to the Thumb entry `ApricornCraft_FieldRun` after linking both overlays and rejects entries at or above 129's origin. The dispatcher requires 131 already loaded; it never tries to load it over active code. Both quote and commit finish synchronously during field-script execution, before the script's fade/pause. `python scripts/dev/verify_apricorn_overlay.py` verifies packed placement, absence of the transaction implementation from 129, non-overlap, and the actual compiled dispatcher's loaded/unloaded/null guards and argument forwarding.

Measured Nov 18 relocation build: complete overlay 129 decreased from **32,301 to 31,977 bytes**, recovering **324 bytes net** and leaving **791 bytes free** in its 32 KiB window. The custom blob is **31,881 bytes**, excluding its 96-byte prefix. Host transaction tests, compiled dispatcher guards, packed placement, existing field pointer checks, Center scripts, Abra and cross-region Fly checks passed; the relocated NPC exchange still needs an in-game smoke test.

Relocation crash fix: the first packed version entered an imported Thumb Bag helper through an ARM linker trampoline (`PC=0x023D8744`). Generated linker assignments retain odd addresses but lack Thumb function metadata for direct BL relocation. The field implementation now uses explicit `LONG_CALL` aliases for quantity lookup, division, copy and clear; existing add/remove imports already use indirect calls. Do not reintroduce implicit struct-copy, zero-loop-to-memset, or division helper calls here without checking their linked instruction-set transitions. `verify_apricorn_overlay.py` now executes the real packed field transaction and resident memcpy/memset/division helpers, asserts Thumb state at imported helper entries, and covers quote, successful exchange, insufficient funds and capacity failure. Its original dispatcher-only test did not cover this failure. The `rom_gen.ld` Makefile rule depends on the resident ELF rather than `output.bin`, removing the field-link/address-patch dependency cycle.

The remaining vanilla gift giver in Route 32 1F (zone_event **163**, object **6**, local **(1, 18)**) now uses scriptId **6**, replacing the vanilla Lure Ball gift even on saves that already claimed it. `scripts/build/patch_center_apricorn.py` runs after the relearner patch, appends script slot **5** in member **233**, and preserves all original code, movement data, NPC placement, and warp indices. Messages **25–31** are appended to bank **381**.

`src/field/apricorn_craft.c` (overlay 131) counts both ordinary Bag Apricorn stacks and the first seven colour-count bytes in the vanilla Apricorn Box. It exchanges everything immediately at **one ball per Apricorn**, using Kurt's mapping: red → Level, yellow → Moon, blue → Lure, green → Friend, pink → Love, white → Fast, black → Heavy. The fee is **100 × ceil(total / 10)** across all colours and both stores combined, with no fee for zero Apricorns. The confirmation quote prints fee hundreds followed by `00`, avoiding 16-bit script-var truncation for large fees.

Custom command **208/subcommand 5** takes mode **0** to quote or **1** to recheck and commit. It outputs total in **0x8000**, fee hundreds in **0x8001**, and status in **0x800C** (0 success, 1 empty, 2 insufficient money, 3 insufficient ball space, 4 temporary allocation failure). It simulates every removal/addition on a temporary Bag copy, checks the 999-per-ball stack limit, and only then commits the Bag, zeroes the seven Box colour counts, and deducts money. It does not touch Kurt's pending order or Aprijuice. The standard purchase sound plays only after a successful commit. No new save fields are needed.

Validation: compile/run `gcc -w -DAPRICORN_CRAFT_HOST_TEST -Iinclude src/field/apricorn_craft.c scripts/dev/test_apricorn_craft.c -o build/test_apricorn_craft && build/test_apricorn_craft` inside Docker. After building `test.nds`, run `python scripts/dev/verify_center_apricorn.py`, `python scripts/dev/verify_center_relearner.py`, and `python scripts/dev/verify_r32_outdoor_rod_guru.py`. The transaction test covers rounding, mixed colours/stores, cancellation safety, exact/insufficient funds, a full ball pocket, stack overflow, rollback after a later colour fails, preserved Kurt order bytes, and fees above 65535 dollars. In-game testing should check the quote, colour outputs, inventory/money, and an already-claimed vanilla-gift save.

After a successful confirmation/exchange, the script closes the quote window, fades to black, waits **30 frames**, and fades back before the purchase sound and **“All done!”**. This is presentation only; it does not advance the accelerated clock or calendar. Declines and failed exchanges do not run the fade.

**Workbench recon (v2):** Kurt's house uses matrix **127** → land_data member **239**. Its event member **158** contains three character objects and no furniture object. The land member contains a **528-byte placed-prop block (11 × 48-byte records)** before its BMD model, with model IDs **1, 56, 143, 142, 71, 139**. This is a promising route for transplanting furniture, but the workbench's exact prop/model and its compatibility with the Center's area model resources still need visual identification; no furniture was changed for the first service version.

### Hub Move Relearner

The Move Relearner stands at local **(4, 15)** in Route 32 1F (zone_event **163**, object **4**, sprite **332**, scriptId **5**). `scripts/build/patch_center_relearner.py` runs after the fisherman relocation and appends slot **4** to script member **233**, preserving the original bytecode and relative branches. Dialogue is appended at messages **17–24** in bank **381**. The Blackthorn service retains its existing behavior.

`armips/scr_seq/scr_seq_center_relearner.s` uses the existing party picker, eligibility command **466**, relearner application **467**, and result command **469**. Cost is **$300**, checked before opening the party picker and deducted only when the relearner returns success (**0**). Declining, cancelling either screen, selecting an Egg, having no eligible moves, or lacking money never charges the player. Existing expanded-learnset support in `armips/asm/levelup.s` remains in use.

After Docker `make test.nds -j24`, run `python scripts/dev/verify_center_relearner.py` to check event/script preservation and exercise the compiled bytecode's success/cancellation/payment paths. In-game testing still needs to verify party and move-selection screens, the taught move, and the money balance. Leave and re-enter the Center when loading an existing save inside it to refresh NPCs.

**Party-selection freeze:** the first hub script called `CloseMsg` again after returning from the party picker without creating another message window. Native `ScrCmd_CloseMsg` at **0x02041168** unconditionally clears/removes the window; it does not guard against a second close. Match the original Blackthorn sequence: print **message 24** after the eligibility check, then close it and fade to the move-learning screen. The bytecode verifier now tracks message-window state and rejects the old sequence before rebuilding. The existing ARM learnset patch also has a duplicate-filter issue observed in an isolated probe; that is separate from this window-lifecycle fix and was not changed here.

## Fishing Rod guru NPCs

**Design:** [Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression).

**Ship status (Nov 2026):** **Ten** outdoor/matrix guru sites patched. Build hooks in `narcs.mk`, text in `data/text/*.txt`, `scripts/build/check_rod_guru_text.py`. **Route 32** guru **obj 19** @ world **(466, 419)** beside the Center entrance (shared rod progression, no Yes/No); the interior fisherman is removed. Tier logic is global (`src/fishing_rod.c`, flags 117/189, Super = `hasitem`).

**Goal:** One shared fisherman script gives Old → Good → Super Rod based on Pokédex caught Water-type evolutionary families (any catch source). Dialogue is region-agnostic for reuse across gurus.

**Inventory (all guru sites):**

| Location | zone_event | scr_seq | msg | Patch prefix |
|----------|------------|---------|-----|--------------|
| Route 44 | `2_043` | `2_257` | 404 | `r44_rod_guru` |
| Route 34 | `2_035` | `2_237` | 384 | `r34_rod_guru` |
| Olivine | `2_074` | `2_911` | 604 | `olivine_rod_guru` |
| Viridian | `2_047` | `2_741` | 452 | `viridian_rod_guru` |
| Vermilion | `2_051` | `2_776` | 483 | `vermilion_rod_guru` |
| Route 12 | `2_017` | `2_199` | 348 | `r12_rod_guru` |
| Fuchsia | `2_053` | `2_807` | 512 | `fuchsia_rod_guru` |
| Route 24 | `2_025` | `2_215` | 362 | `r24_rod_guru` |
| Route 25 | `2_026` | `2_216` | 363 | `r25_rod_guru` (mirror — same tile as R24) |
| Route 32 outdoors | `2_033` | `2_232` (scriptId 11) | 380 (messages 20–24) | `scripts/build/patch_r32_outdoor_rod_guru.py` |

**Guru coordinates:** Outdoor coordinates are world `(x, z)`; Route 32 Pokémon Center uses interior local coordinates.

- Route 44: world **(568, 183)**.
- Olivine City: world **(273, 248)**.
- Route 34 (Day-Care): world **(358, 409)**.
- Route 32 Pokémon Center: local **(4, 15)** (classic Fishing Brother spot).
- Route 24 / 25 border: world **(1320, 65)**; duplicate on zone_event **025** and **026** at the map seam.
- Viridian City: world **(1023, 264)**.
- Vermilion City: world **(1298, 304)**.
- Fuchsia City: world **(1230, 430)**.
- Route 12: world **(1429, 319)**.

**Matrix seam rule:** If a guru vanishes when crossing a route/city header boundary, duplicate the **same world `(x, z)`** on **both** adjacent `eventsBank` members and append the guru script to **both** `scriptsBank` members (different msg banks). Documented example: Route 24/25 below.

**Progression:** `FISHING_ROD_GOOD_FAMILIES` (default **5**) and `FISHING_ROD_SUPER_FAMILIES` (default **15**) in `include/config.h` / `armips/include/config.s`. Super Rod ownership is `hasitem(ITEM_SUPER_ROD)` — no save flag.

**C:** `src/fishing_rod.c` counts families via union-find on evolution data + dex caught flags. Script hooks: `Script_RunNewCmd` cases **1** (count) and **2** (remaining until next tier) in `src/script_new_cmds.c`.

**Flags:** `FLAG_GOT_OLD_ROD` (117), `FLAG_GOT_GOOD_ROD` (189).

**Item grants:** Use `giveitem_no_check` (wraps `std_give_item_verbose`) — same flashy obtain UI + fanfare as Mom’s Pass/Ticket grants. Do **not** use bare `giveitem` (silent, no fanfare). **`npc_msg` does not wait for A** — before each grant use `wait_button_or_walk_away` + `closemsg`, then `giveitem_no_check` (obtain UI waits for A on its own). **After** the grant, `closemsg` again (Mom script 0 line 116) — otherwise the “put in pocket” line sticks and the touch menu stays locked. Still **no Yes/No** before the grant (unlike vanilla fisherman).

**Text buffers:** Progress line uses `{STRVAR_1 52, 0, 0}` + script `TextNumber 0, var`. Do **not** use STRVAR type **50** (shows “GOLD” / points UI) or **51** (item names — “Good Rod” when buffer stale).

**Recipe (all sites):** shared `scr_seq_*_rod_guru.s` → `tools/patch_scr_seq_<prefix>_rod_guru.py` on the inventory **scr_seq** member; `tools/patch_zone_event_*_rod_guru.py` on **zone_event**; append guru lines to the inventory **msg** bank. **`type=0`** + map `scriptId` for talk NPCs; **`type=1`** + 3000-range script for vanilla bridge fishermen (not your guru). After `make`: `python3 scripts/build/verify_<prefix>_rod_guru_scr_seq.py build/a012/2_<NNN>` and matching `scripts/dev/verify_*_zone_event.py` — see [`scripts/README.md`](../scripts/README.md) rod-guru list.

**Reference — Route 44 (outdoor matrix):** header **46**, zone_event **043**, scr_seq **257** (not **260** = Route 47), msg **404**; guru obj **15** @ **(568, 183)**, slot **3** / scriptId **4**, lines **2–6**. **Olivine:** header **77** → events **074**, scr_seq **911**, msg **604** (member **077** is Ecruteak Gym).

**Wrong-ID traps (once):** pret `046_R44` ≠ walkable R44 (**043**); Ice Path junction **046/090**; scr_seq **260** = R47. **ID recon:** pret `map_headers.h`, `find_msg_text.py`, in-game coords, [Field map IDs](#field-map-ids-dont-mix-them-up).

**Route 24 / 25 seam:** guru @ world **(1320, 65)** — duplicate object + scr_seq append on **both** **025**/**215**/**362** and **026**/**216**/**363** (see inventory table).

**Route 32:** for World-10, the guru now stands outside at world **(466, 419)** beside the Center door **(468, 419)**. The build patch removes interior objects 4/5, appends outdoor script 11 while preserving the original route bytecode and relative branches, and uses outdoor text bank 380. The hub relearner subsequently occupies interior object 4 with a new script; the original scripts in member 233 remain intact. Verify after building with `python scripts/dev/verify_r32_outdoor_rod_guru.py`; check placement and conversation in-game.

**Gym-area story skip (Radio Tower / Elm phone coord):** vanilla **coord script 2** at world **(272, 239)** (west of the gym) when **`VAR_UNK_4078`** is 0 — not the rival hide flag (**470**). Mom intro sets **4078 → 1** (`openworld_story_skip_flags.inc`); **`tools/patch_scr_seq_olivine_gym_story.py`** NOPs scr_seq **911** slot **2** entry; **`tools/patch_zone_event_olivine_gym_story.py`** removes the coord from **074**.



## Elemental stone early-evolution proof of concept

`include/stone_level_evolution.h` supplies the shared rule: Fire/Water/Leaf/Thunder/Ice/Dusk Stone or Metal Coat must match either evolved type (Fire/Water/Grass/Electric/Ice/Ghost/Steel respectively). The evolution method must be plain `EVO_LEVEL`, and the requirement is `max(1, ceil(normalLevel * 0.90) - 3)`. Only the target species/form’s personal types are checked; a type lost on evolution does not qualify. Nosepass additionally has a native Metal Coat item entry alongside Thunder Stone in `data/Evolutions.c`. Early item evolution unconditionally excludes targets Metang and Metagross, preserving both Beldum-family level evolutions. The generic acceleration rule adds no evolution entries or saved modifiers; Nosepass’s explicit Metal Coat option is a separate native item entry. Existing explicit item methods take priority in `src/individual/GetMonEvolutionInternal.c`. Both item-check and item-use contexts resolve through this path; `CanUseItemOnMonInParty` explicitly routes matching level-up cases through the item-use resolver before the existing bag-consumption gate.

`GetStoneLevelEvolutionRequirement` in `src/pokemon.c` dispatches to the evolution overlay, whose internal reader reads the full evolution NARC record, including its trailing terminator, for the shared threshold. `PartyMenu_PrintEvoStoneCompatString` replaces ARM9 `0x0207DC20` via `hooks`; its original caller remains in place. The resident hook forwards to the evolution overlay for rendering; the renderer calls its local requirement reader directly, avoiding nested overlay loads. Below-level compatible Pokémon display `LVnn` in the existing compatibility window. Native ABLE/UNABLE strings and palette are retained. The hook address and call signature were checked against ARM9 disassembly and pret’s `party_context_menu.c`.

Verification: Docker/Linux `python3 scripts/dev/verify_stone_level_evolution.py` compiles the actual requirement reader, item-resolution branch, and menu-label function against the current evolution data. Tests cover all seven items, target types, hybrid rounded thresholds, immediate targets, native stone methods, wrong types/items, final forms, move-known exclusions, eggs, and LV35/ABLE/UNABLE output. In-game menu rendering and evolution animation still require playtesting. Design: [World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones).


## Eevee supplementary player evolution methods

`data/eevee_extra_evolutions.h` authors eight supplementary methods: mossy rock, icy rock, Route 10 magnetic field, Dawn/Sun → Espeon, Dusk/Moon → Umbreon, and Shiny → Sylveon. `include/eevee_evolutions.h` merges them into a temporary **16-entry** Eevee buffer in `GetMonEvolutionInternal`; all resolver loops use the per-species count. `MAX_EVOS_PER_POKE` remains **9**, and `data/Evolutions.c` plus all evolution NARC records keep their original size. Other readers, including early-stone hints, fishing family checks, and Eviolite checks, continue reading the original records. The same shared resolver source supplies field and battle evolution overlays.

The merge preserves Eevee’s first six native entries (five stones and Fairy-move friendship), inserts the eight supplementary methods, then retains daytime/nighttime friendship. The ninth native slot is empty and excluded from Eevee’s active count. Consequently Fairy-move friendship wins over location, and all three location methods win over ordinary friendship. Explicit item choices work at any level; no level-only path is added. Encounter-stage TSV rules are separate and unchanged.

Verification: `python3 scripts/dev/verify_stone_level_evolution.py` in Docker/Linux checks all ten Eevee item choices, both friendship outcomes, all four mossy/icy maps, Route 10, Fairy-move priority, the 16-versus-9 entry counts, and absence of a level-only fallback, alongside existing early-item regressions. Included in the successful Nov 17 playable-ROM build; new methods still need in-game confirmation.

## Evolution-service overlay relocation

The field and battle evolution overlays (133 and 134) expose a three-pointer `EvolutionOverlayApi` table at the start of their load regions, **0x023C0400** and **0x021FBE60**. Both linker scripts place `.evolution_api` first. The entries resolve evolution targets, read early-item level requirements, and render the party compatibility label. **The load address is now data, not a Thumb function entry: do not call `base | 1`.** Resident wrappers in `src/pokemon.c` and `src/party_menu.c` call through the table defined in `include/evolution_overlay.h`.

`OpenEvolutionOverlay` reuses an already-loaded evolution overlay without taking ownership. Otherwise it selects the alternate overlay when the battle extension or item-use overlay is loaded, preserving the existing shared-address protection. `CloseEvolutionOverlay` unloads only overlays owned by that call. The relocated renderer calls its local requirement reader directly. Unrelated item checks return before loading an evolution overlay. No field-overlay code calls or additional overlay IDs are introduced.

**Measured Nov 17 full build:** overlay 129 decreased from **30,629 to 30,273 bytes**, recovering **356 bytes** and leaving **2,399 bytes free**. Each evolution overlay uses **2,824 bytes**, within its existing region. The relocated readers and renderer live in those overlays, with only dispatch and item filtering remaining in 129.

Docker/Linux checks: `python3 scripts/dev/verify_stone_level_evolution.py` covers behavior and the actual resident dispatchers with mocked load ownership. After a full ROM build, `python3 scripts/dev/verify_evolution_overlay.py` checks both linked API tables, Thumb function pointers, region bounds, absence of the relocated implementations from overlay 129, and exact packed-ROM contents for overlays 129, 133, and 134. Menu responsiveness, early item use, ordinary level-up evolution, and nested item-use overlay loading still need in-game confirmation after the relocation.
