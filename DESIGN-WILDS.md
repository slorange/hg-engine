# Pokémon Wandering Heart — Wild Encounters & Ecology

> Seeded ecology, wild level ranges, distance caps, fishing, and content scope.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md)

## Sections

| Section | Status |
| ------- | ------ |
| [Wilds-1. Increased Wild Pokémon Level Range](#wilds-1-increased-wild-pokémon-level-range) | IMPLEMENTED |
| [Wilds-2. Starting-City Distance-Based Wild Level Caps](#wilds-2-starting-city-distance-based-wild-level-caps) | IMPLEMENTED (near complete) |
| [Wilds-3. Fishing Rod Progression](#wilds-3-fishing-rod-progression) | PARTIALLY IMPLEMENTED |
| [Wilds-4. Pokémon Generations / Content Scope](#wilds-4-pokémon-generations--content-scope) | DECIDED (release scope) |
| Per-save ecology shuffle | Moved — [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle) |
| Expanded Pokédex / generations | Moved — [Future-6](DESIGN-FUTURE.md#future-6-expanded-pokédex--generations) |

---

# Wilds-1. Increased Wild Pokémon Level Range

**Status: IMPLEMENTED** — distance caps ([Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps)), [level distribution](#level-distribution), **stage adjust** (level-up + [synthetic edges](#synthetic-evolution-stages-wild--trainer), shared with trainer battles). Details: `documentation/HACK-NOTES.md` § **Wild level caps (distance-based)**.

Replace narrow per-area wild level bands with a **broad range** from low levels up to an area-specific maximum.

## Current vs proposed model

**Current-style model:** Route X might contain Pokémon around Lv 18–22 only.

**Proposed model:**

- Route X has a **maximum wild level**, e.g. Lv 22.
- Encounters can occur from approximately **Lv 3 through that maximum**.
- The full range remains available even at high player progression levels.

After rolling the encounter level, determine the **appropriate evolution stage** for the assigned family.

## Example (simple level-evolution family)

Pidgey family assigned to an area with max level 45:

| Rolled level | Stage |
|-------------:|-------|
| 3–17 | Pidgey |
| 18–35 | Pidgeotto |
| 36–45 | Pidgeot |

One habitat can therefore naturally contain **multiple stages** of the same evolutionary family.

## Benefits

- Earlier evolution stages never disappear from the world.
- Dex completion does not require finding a separate low-level area for every family.
- Ecologies feel **persistent** rather than replacing weak species with strong ones as the player progresses.

## Level distribution

**Implemented (Sep 2026).** Wild levels are never **1** (minimum encounter level **2**).

| Condition | Roll |
|-----------|------|
| Area cap below **10** | Adult band only: uniform **`[⌊0.9×cap⌋ − 2, cap]`** (e.g. cap 9 → **6–9**) |
| Cap **≥ 10**, **15%** “baby” | Uniform **2–7** |
| Cap **≥ 10**, **85%** “adult” | Uniform **`[⌊0.9×cap⌋ − 2, cap]`** (e.g. cap 10 → **7–10**; cap 60 → **52–60**) |

After rolling, evolution **stage** is chosen from level-up chains plus [synthetic edges](#synthetic-evolution-stages-wild--trainer).

## Synthetic evolution stages (wild + trainer)

Encounter tables still list a base species (e.g. Poliwhirl, Exeggcute). After the rolled level is known, **`AdjustEncounterSpeciesForLevel()`** (`include/encounter_species_stage.h`):

1. Walks **prevos** through linear **`EVO_LEVEL`** chains (`data/Evolutions.c`) **and** synthetic edges (`data/synthetic_evolution_thresholds.tsv`) to find the chain root (so authored Alakazam / Vileplume devolve correctly at low levels).
2. Walks **forward** from that root, applying level-up thresholds then synthetic edges (level ≥ `min_level`) up to 8 steps. ROM data: `scripts/build/gen_level_up_evo_tables.py` + `gen_synthetic_evo_edges.py` → field overlay rodata.

**Verified Sep 2026** in-game for wild rolls and trainer scaling (including devolving authored trade/stone finals at low levels). Offline check: `scripts/dev/verify_encounter_stage.py`.

Synthetic thresholds **do not** change player evolution rules ([World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones) QoL is separate from wild/trainer stage adjust). Wild/trainer mons still get moves and stats from the **final** species (`PokeParaSet` / `InitBoxMonMoveset`), same as today.

**Authoring tiers** (each TSV row has an explicit `min_level`; tiers are for filling the sheet, not runtime logic):

| Vanilla method | Stage 1 | Stage 2 |
|----------------|--------:|--------:|
| Trade (incl. held item) | 20 | 35 |
| Stone (incl. location-based — player uses stones; wild/trainer treat as stone tier) | 25 | 35 |
| Friendship (incl. time-of-day variants) | 20 | 30 |
| Move-known | HGSS learn level + 1 | — |

**Special:** Piloswine → Mamoswine uses **34** (AncientPower is Lv1/relearner in HGSS; Swinub → Piloswine at 33).

**Branches:** `branch` empty = single outcome; `random50` = pick one row at random for the same `from` + `min_level` (Gloom, Poliwhirl, Clamperl, **Wurmple**).

**Deferred (not in TSV until later):** Eevee, Tyrogue, Shedinja, **gendered** evolutions (Burmy, Combee, Gallade, Froslass, etc.).

**Future enhancements** (probabilistic synthetic edges; wild / trainer / Gym Leader rates): [Future-11](DESIGN-FUTURE.md#future-11-encounter-stage-selection-wild--trainer).

## Separation of concerns

Three independent inputs:

| Input | Determines |
|-------|------------|
| Ecology ([Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle); vanilla tables today) | **Which family** can spawn |
| Area maximum ([Wilds-1](DESIGN-WILDS.md#wilds-1-increased-wild-pokémon-level-range), [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps)) | **Possible encounter levels** |
| Rolled level + stage rules | **Evolution stage** (level-up tables + synthetic edges) |

---


---

# Wilds-2. Starting-City Distance-Based Wild Level Caps

**Status: IMPLEMENTED (near complete)** — distance caps verified in-game (Sep 2026). Remaining gaps: Safari Zone, Bug Catching Contest, roamers/scripted wilds, balance tuning.

**Decision:** distance-from-start-city caps ([Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps)) replace badge-guard / encounter-tile wild **level** progression. The alternative ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) wild gating) is **not pursued** for general wild levels; World-2 remains for HM/Flash/League and optional hard zones only.

The player can **enter** high-distance areas early; encounters scale from [Wilds-1](DESIGN-WILDS.md#wilds-1-increased-wild-pokémon-level-range) level ranges tied to graph distance — danger is in the fights, not a coord gate on the grass.

**Interaction with [Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps):** wild **levels** may exceed the **player** badge cap; **catching** those Pokémon must be blocked (decided — see [Wild catches above the player level cap](DESIGN-BATTLES.md#wild-catches-above-the-player-level-cap)).

Wild-area difficulty should depend on the player's **chosen starting city** ([Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon)) rather than one fixed world progression curve or badge-count encounter blocks.

## World graph

Build a **directional graph** representing the explorable world:

- cities / towns;
- routes;
- forests;
- caves / dungeons;
- meaningful dungeon subareas / depths;
- one-way traversal where relevant (e.g. ledges);
- physical connections between these nodes.

## Build-time precomputation

For **every valid starting city** ([Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon) — 18 cities):

1. Shortest-path **exploration distance** from that city to each encounter area on the world graph.
2. Convert distance → **maximum wild level** (and optional tier for tuning).
3. Precompute the full matrix **offline** and ship it as a ROM lookup table — **no graph traversal during gameplay**.

Implementation (graph files, generators, runtime hooks): `documentation/HACK-NOTES.md` § **Wild level caps (distance-based)**.

## Encounter methods (PoC coverage)

| Method | PoC status |
|--------|------------|
| Grass / cave walking | **Verified** |
| Surf / rods / Rock Smash | **Verified** |
| Headbutt | **Verified** |
| Hoenn / Sinnoh Sound | **Hooked** (after species swap) |
| Swarms | **Hooked** when using normal wild tables |
| Roamers / rare table | **Vanilla levels** (not distance-scaled) |
| Safari Zone | **Not yet** |
| Bug Catching Contest | **Not yet** |
| Scripted wild battles | **Not hooked** (script levels unchanged) |

## Edge costs (tuning TBD)

PoC uses **uniform edge cost = 1** per graph hop. Possible future weighting:

| Connection type | Example cost |
|-----------------|-------------:|
| city / town interior connector | 0 or negligible |
| short connector maps | 1 |
| SS Aqua / Magnet Train | 1 |
| normal route traversal | 2 |
| substantial dungeon | 3+ |
| deeper dungeon section | additional cost |

Exact weighting should be tuned after generating and inspecting the distance matrix.

## Distance → level cap (PoC formula)

Normal wild encounters use the cap + [Wilds-1 level distribution](#level-distribution). Roamers, Safari, and most scripted wilds are unchanged — see table above.

Player badge level caps run up to **70–80** ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps)). Wild area caps use a lower ceiling (**5–60**) for balance:

```
levelCap = 55 × max(0, route_distance − 1) / (max_route_distance − 1) + 5
```

- `route_distance` — shortest graph distance from the chosen starting city to the encounter area.
- `max_route_distance` — farthest reachable distance for that starting city on the same graph.
- Integer division; at distance **0–1** → cap **5** (starter town + first connected routes); at max distance → cap **60**.
- **Starting city:** Mom menu stores Vision-3 index **0–17** in `VAR_PLAYER_START_CITY`; used directly as the Wilds-2 table row.

### Future level-cap overrides (not in PoC)

| Areas | Intended cap band |
|-------|-------------------|
| Routes **27**, **26**, **23** | **70–80** |
| Route **28**, **Mt. Silver**, **Cerulean Cave** | **80–90** |

Add as a post-processing step on the generated cap table once base distance scaling is validated in play.

### Cave depth (future)

PoC treats each cave dungeon as **one graph node** → one cap for every floor. Later, split dungeon subareas into separate graph nodes (or override rows) so deeper HM-gated sections can exceed entrance tiers without per-floor encounter tables.

## Interaction with ecology and level range

- **starting city + graph distance** → area maximum level;
- **encounters** range from ~Lv 3 to that maximum ([Wilds-1](DESIGN-WILDS.md#wilds-1-increased-wild-pokémon-level-range));
- **family assignment** uses vanilla tables today; per-save shuffle is [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle).

## Overrides and validation

Still needed:

- optional / endgame regions (League, Mt. Silver paths) can remain naturally distant / high-tier, with optional gates;
- dungeon **depth** can use separate nodes so deeper HM-gated sections have higher distance / tier than entrances.

## Replayability

- **Starting city** changes the world's difficulty gradient on vanilla species (**implemented** via distance caps).
- **World seed** / ecology shuffle — [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle) adds a second axis when implemented.

---


---

# Wilds-3. Fishing Rod Progression

**Status: PARTIALLY IMPLEMENTED** — Route 44 and Olivine gurus verified; full Johto/Kanto network not complete.

Fishing Rod progression is based on the player's experience **catching Water-type Pokémon**, not badge count or geographic progression. This is a **separate progression track** from [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves) HM unlocks.

The historical Fishing Guru / Fishing Brother NPCs across Johto and Kanto should share the same progression. The player may return to **any one of them** for later Rod upgrades; progression does not require visiting the vanilla Rod locations in order.

- **Old Rod** — given freely on first interaction.
- **Good Rod** — awarded after catching Pokémon from **5 unique Water-type evolutionary families**.
- **Super Rod** — awarded after catching Pokémon from **15 unique Water-type evolutionary families**.

## Counting rules

- Count **evolutionary families**, not individual species.
- Catching multiple members of the same evolutionary family counts only once.
  - Example: catching Poliwag, Poliwhirl and Poliwrath still counts as **1 family**.
- A family qualifies if the player has caught at least one member that is **Water-type**.
- Either primary or secondary Water typing qualifies.
- Use Pokédex caught data rather than the player's current collection, so traded away or released Pokémon still count.
- Branching evolutions remain a single family.
- The progression should be shared globally between all Fishing Guru / Fishing Brother NPCs.

This creates a self-contained fishing progression loop:

**Old Rod → catch 5 Water families → Good Rod → access more fishing encounters → catch 15 Water families → Super Rod**

## Fishing Guru locations

**Target:** a **network** of interchangeable Fishing Guru / Fishing Brother NPCs spread across Johto and Kanto so the player is never far from the next Rod tier — any one of them can award whichever Rod is next.

**Vanilla HGSS caveat:** HeartGold/SoulSilver does **not** mirror every historical Gen I–IV Rod-giver city. Typical vanilla hooks include **Route 32** (Old Rod) and **Route 12 / Silence Bridge** (Super Rod); **Olivine** has a fishing NPC. **Vermilion and Fuchsia** have no Rod givers in vanilla — add new gurus there if they join the network.

**Distribution goal:** avoid clustering every guru in mid-Johto / south Kanto. Prefer towns the player already visits (Mart, Gym, ferry) over dead-end-only cells.

| Region | Location | Status | Notes |
|--------|----------|--------|--------|
| East Johto | **Route 44** (bridge) | **Implemented** | Verified in-game Sep 2026 |
| West Johto (coast) | **Olivine City** | **Implemented** | Verified in-game Sep 2026 |
| South Johto | Route 32 Pokémon Center | Planned | Vanilla Old Rod area |
| East Johto | **Blackthorn City** | Planned | **Likely new NPC** — local Rod access when surrounding wild caps are high |
| West Kanto | **Viridian or Pewter** | Planned | **Likely new NPC** |
| Mid Kanto (coast) | Vermilion City | Planned | **Likely new NPC** |
| South Kanto | Fuchsia City | Planned | **Likely new NPC** |
| East Kanto | Route 12 / Silence Bridge | Planned | Vanilla Super Rod area |

Any guru reads the same global progression and offers Old → Good → Super when family counts are met. **Implementation:** `documentation/HACK-NOTES.md` § **Fishing Rod guru NPCs**.

---


---

# Wilds-4. Pokémon Generations / Content Scope

**Status: DECIDED (release scope)**

**Ship scope:** **Gen I–IV plus the Volcarona line** (Larvesta, Volcarona). No broad Gen V+ rollout in the first release.

Broader dex / generations: [Future-6](DESIGN-FUTURE.md#future-6-expanded-pokédex--generations).
