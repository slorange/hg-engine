# Pokémon Wandering Heart — Wild Encounters & Ecology

> Seeded ecology, wild level ranges, distance caps, fishing, and content scope.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md)

# Wilds-1. Randomized Wild Pokémon Ecology

**Status: DECIDED conceptually; TECHNICAL UNKNOWN for implementation**

At new-game creation, generate a **stable per-save wild Pokémon ecology** instead of using fixed vanilla species locations.

This is **not fully random**. Species and families must still appear in appropriate habitats and encounter methods.

## Core rules

- **Families stay together geographically.** If the Zubat family is assigned to Dark Cave, Zubat / Golbat / Crobat all belong to that same habitat rather than being independently scattered.
- **Every obtainable family** must be available in at least one location.
- **Duplicate family locations** are allowed and desirable for common / generalist species.
- **Habitat compatibility** must be respected:
  - aquatic / fish families → Surf, fishing, water habitats;
  - cave species → strongly prefer caves;
  - Ice species → icy / snowy areas;
  - forest, mountain, grassland, coastal, etc. → their own compatibility tags.
- Habitat compatibility should often be **weighted** rather than strictly binary. Some families can plausibly live in several environments.
- **Encounter method compatibility** remains meaningful: fishing, Surf, grass / cave encounters, Headbutt, Rock Smash, etc. ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression)).
- **Area identity** should remain coherent. If an area is intended to have a strong type / environment theme, generated families should preserve that theme.
- **Global availability** matters more than equal regional distribution. There is no hard requirement that every type appear separately in both Johto and Kanto, since regional travel will be easy.
- **Special encounters** — gifts, fossils, swarms, legendaries, Red Gyarados, static overworld Pokémon, etc. — need an explicit policy for how they interact with this system (**TBD** per category).
- If there are any flags where there are more pokemon families than route spots to support them, Safari Zone and in game trades both work as backup catch-all options

## Persistence and seed

Generation must be **deterministic from a save-specific world seed**:

1. generate ecology once when starting a new game;
2. save / store the seed or generated mapping;
3. **never reshuffle** species locations during the same playthrough.

## Downstream consumers

All location-aware systems should query the generated ecology rather than hardcoded vanilla locations:

- Pokédex habitat / location data;
- trainers asking where a Pokémon has been seen ([World-6](DESIGN-WORLD.md#world-6-trainer-interactions));
- trainers giving location hints ([World-6](DESIGN-WORLD.md#world-6-trainer-interactions)).

## Relationship to progression

Conceptually:

- **world seed** determines **where** Pokémon families live;
- **progression systems** ([Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range), [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)) determine **how strong / evolved** encountered Pokémon are.

**Wild level progression:** [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) is **decided and implemented** (PoC verified Sep 2026). Badge / encounter-tile wild gating ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)) is **not** the model for wild levels — kept in docs only for HM/League gates and the Route 46 template.

---


---

# Wilds-2. Increased Wild Pokémon Level Range

**Status: PARTIALLY IMPLEMENTED** — broad `[3, cap]` rolls ([Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)) and **same-line stage adjust** (`AdjustSpeciesForLevel` in `include/species_stage_for_level.h`, shared with trainer battles) ship in PoC. Weighted level distribution curves remain TBD.

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

Do **not** necessarily use a uniform probability over every level from 3 to cap.

Prefer weighting levels toward the **upper portion** of the range so late-game encounters remain relevant while low levels stay possible:

- **low levels** — possible but uncommon;
- **middle levels** — moderate frequency;
- **levels near the area cap** — most common.

Exact weighting curves remain **TBD** and should be balanceable (config or data tables).

## Non-level evolution methods

Evolution methods that are not simple level thresholds need explicit handling (**TBD**):

- friendship;
- stones / items;
- branching evolutions;
- trade replacements ([World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones)).

## Separation of concerns

Three independent inputs:

| Input | Determines |
|-------|------------|
| Ecology ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)) | **Which family** can spawn |
| Area maximum ([Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range), [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)) | **Possible encounter levels** |
| Rolled level + family rules | **Valid evolution stage** (level-up chains only — stones / trade / friendship **TBD**) |

---


---

# Wilds-3. Starting-City Distance-Based Wild Level Caps

**Status: DECIDED and implemented — PoC verified in-game (Sep 2026)**

**Decision:** distance-from-start-city caps ([Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)) replace badge-guard / encounter-tile wild **level** progression. The alternative ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) wild gating) is **not pursued** for general wild levels; World-2 remains for HM/Flash/League and optional hard zones only.

The player can **enter** high-distance areas early; encounters scale from [Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range) level ranges tied to graph distance — danger is in the fights, not a coord gate on the grass.

Wild-area difficulty should depend on the player's **chosen starting city** ([Vision-3](DESIGN-VISION.md#vision-3-starting-location)) rather than one fixed world progression curve or badge-count encounter blocks.

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

For **every valid starting city** ([Vision-3](DESIGN-VISION.md#vision-3-starting-location) — 18 cities; graph data in `scripts/dev/Route Levels/`):

1. Run a shortest-path calculation across the world graph.
2. Calculate the **exploration distance** from that starting city to every encounter area.
3. Convert distance into a progression **tier** / **maximum wild level**.
4. Precompute at **build time** (not during gameplay).
5. Output a lookup table compiled into the ROM.

**Desired runtime model:**

```c
WildAreaProgression[startingCity][encounterArea]
```

Potential stored values:

```c
struct EncounterAreaProgression
{
    u8 tier;
    u8 levelCap;
};
```

Do **not** perform graph traversal during gameplay unless there is a compelling reason. Generate the matrix offline and compile it into the ROM.

## Encounter methods (PoC coverage)

| Method | PoC status | Notes |
|--------|------------|-------|
| Grass / cave walking | **Verified** | `modify_species_encounter_data` |
| Surf / rods / Rock Smash | **Verified** | Same `EncountParamSet` path |
| Headbutt | **Verified** | Wild battle still uses `modify_species_encounter_data` |
| Hoenn / Sinnoh Sound | **Hooked** | Same path after species swap |
| Swarms | **Hooked** | Same path if normal `EncountParamSet` |
| Roamers / `_rare` | **Vanilla** | `modify_species_encounter_data_rare` not hooked |
| Safari Zone | **Not yet** | Separate NARC (`data/SafariEncounters.c`) — no distance cap or stage adjust |
| Bug Catching Contest | **Not yet** | Contest encounter table; verify whether it shares `modify_species_encounter_data` in-game |
| Roamers / `_rare` | **Vanilla** | `modify_species_encounter_data_rare` not hooked |
| Scripted `wild_battle` | **Not hooked** | Explicit script levels unchanged |

## Edge costs (tuning TBD)

PoC uses **uniform edge cost = 1** in `calculate_location_distances.py`. Possible future weighting:

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

**Status: implemented and verified** — build-time tables + runtime hooks (`WildEncSingle` / `WildWaterEncSingle` cache + `modify_species_encounter_data` apply on overlay 129, normal wilds only). **`modify_species_encounter_data_rare` is untouched** (roamers / special encounters keep vanilla levels). PoC rolls **uniformly** in `[3, cap]`; Wilds-2 weighted curves and balance passes remain TBD.

Implementation reference: `documentation/HACK-NOTES.md` § **Wild level caps (distance-based)**.

Player badge level caps run **3–70** ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps)). Wild area caps use a lower ceiling for balance:

```
levelCap = 57 × route_distance / max_route_distance + 3
```

- `route_distance` — shortest graph hops from the chosen starting city to the encounter area’s graph node (`scripts/dev/Route Levels/location_distances.txt`).
- `max_route_distance` — farthest reachable distance for that starting city ( **`MaxDistance`** row in the same file, computed by `calculate_location_distances.py` ).
- Integer division; at distance `0` → cap **3**; at `max_route_distance` → cap **60**.
- Within `[3, levelCap]`, PoC rolls **uniformly** (Wilds-2 weighted curve deferred).
- After rolling, **`AdjustSpeciesForLevel`** picks the stage matching the level (EVO_LEVEL chains only; same helper as `TRAINER_SPECIES_STAGE_ADJUST`).

**Build pipeline:**

1. `scripts/dev/Route Levels/calculate_location_distances.py` → `location_distances.txt` (includes `MaxDistance` row).
2. `scripts/dev/Route Levels/encounter_area_graph.tsv` — static `EncounterAreaId` → graph node (caves: **one node per dungeon** for PoC; all floors share the parent cave’s cap).
3. `scripts/build/gen_wild_level_caps.py` → `src/wild_level_caps_data.c` (compiled into ROM).

**Runtime:** `MapHeader_GetWildEncounterBank(mapId)` → precomputed cap from `VAR_PLAYER_START_CITY` (**0x4031**; PoC remaps menu 0/1/2 → New Bark / Goldenrod / Saffron table rows until the 18-city menu ships).

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
- **encounters** range from ~Lv 3 to that maximum ([Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range));
- **family assignment** remains fixed by the world seed ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)).

## Overrides and validation

Still needed:

- optional / endgame regions (League, Mt. Silver paths) can remain naturally distant / high-tier, with optional gates;
- dungeon **depth** can use separate nodes so deeper HM-gated sections have higher distance / tier than entrances.

## Replayability

Two independent axes:

- **world seed** changes where Pokémon families live;
- **starting city** changes the world's difficulty gradient.

The same seeded ecology can play very differently depending on where the player begins.

---


---

# Wilds-4. Fishing Rod Progression

**Status: DECIDED**

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

**Vanilla HGSS caveat:** HeartGold/SoulSilver does **not** mirror every historical Gen I–IV Rod-giver city. Confirmed or typical vanilla hooks include **Route 32** (Old Rod) and **Route 12 / Silence Bridge** (Super Rod); **Olivine** has a fishing NPC. **Vermilion and Fuchsia do not have Rod givers in vanilla HGSS** — if we want them on the network, we must **add new NPCs** (zone_event object + scr_seq + text).

**Distribution goal:** avoid clustering every guru in mid-Johto / south Kanto. Where practical, place gurus at:

| Region | Location | Status | Notes |
|--------|----------|--------|--------|
| East Johto | **Route 44** (bridge) | **Implemented** | `(568, 183)` west of bridge fisherman; scr_seq **257**, zone_event **043** — verified in-game Sep 2026 |
| South Johto | Route 32 Pokémon Center | Planned | Vanilla Old Rod area |
| West Johto (coast) | Olivine City | **Implemented** | world `(273, 248)` by city sign; zone_event **074**, scr_seq **911**, msg **604** — verified in-game Sep 2026 |
| East Johto | **Blackthorn City** | Planned | **Likely new NPC** — gives Blackthorn a way to farm at lv5 since all connected routes are too high level |
| West Kanto | **Viridian City or Pewter City** | Planned | **Likely new NPC** |
| Mid Kanto (coast) | Vermilion City | Planned | **Likely new NPC** (not vanilla Rod giver) |
| South Kanto | Fuchsia City | Planned | **Likely new NPC** (not vanilla Rod giver) |
| East Kanto | Route 12 / Silence Bridge | Planned | Vanilla Super Rod area |

Exact map and `(x, z)` per guru are implementation details; prefer towns the player already visits for other reasons (Mart, Gym, ferry) over dead-end-only cells.

Any guru on this network reads the same global fishing-progression state and offers the appropriate Rod (Old on first talk, then Good / Super when family counts are met). Shared bytecode: `armips/scr_seq/scr_seq_r44_rod_guru.s` / `scr_seq_olivine_rod_guru.s` (append via per-map patcher). Implementation recipe and ID-discovery notes: `documentation/HACK-NOTES.md` § **Fishing Rod guru NPCs**.

**Outdoor-matrix maps** (Route 44 body uses zone_event member **043**, not the map-header zone index): place objects with **`type=0`** + low **scriptId** bound to that route’s **scr_seq** member (pret `scriptsBank` in `map_headers.h`). Vanilla walkable NPCs on the matrix often use **`type=1`** + scripts **3000+** instead.

---


---

# Wilds-5. Pokémon Generations / Content Scope

**Status: PARTIALLY DECIDED — expand later**

**v1 scope:** treat the dex as **Gen I–IV plus the Volcarona line** (Larvesta, Volcarona). No broad Gen V+ rollout yet.

**Long-term:** the full generation cutoff remains open. HG-Engine supports mechanics, Pokémon, forms, moves, and abilities well beyond vanilla Generation IV; additional families can be added incrementally once ecology, scaling, and content pipelines are stable.

Do NOT currently assume a fixed long-term cutoff (Gen I–VI, Gen I–IX, etc.) beyond the v1 rule above.

This decision affects:

- encounters ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology));
- starters;
- evolutions;
- Gym pools;
- trainer generation;
- friendship evolution families;
- types;
- abilities;
- moves;
- items;
- legendaries;
- postgame content.

---


---


---

# Wilds-6. Technical Investigations

Open engineering questions for this area (from the former monolithic design doc).

## Open-world encounter structure


Primary design: [Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology) (ecology seed), [Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range) (broad level bands), [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) (distance-based caps — **implemented**).

Questions include:

- per-save ecology generation and persistence (`data/Encounters.c` replacement or overlay);
- family / habitat tagging data format;
- evolution-stage selection at rolled wild level;
- build-time graph matrix for starting-city distance caps;
- Pokédex and trainer hint integration;
- special / static / legendary encounter policy;
- badge-gated encounter tiles vs distance-only caps ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating));
- grass-tile-specific encounter sets;
- map scripting;
- guards (PoC: Route 29→46);
- doors;
- HM gates.
