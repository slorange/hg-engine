# Pokémon Wandering Heart — Wild Encounters & Ecology

> Seeded ecology, wild level ranges, distance caps, fishing, and content scope.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md)

## Sections

| Section | Status |
| ------- | ------ |
| [Wilds-1. Randomized Wild Pokémon Ecology](#wilds-1-randomized-wild-pokémon-ecology) | DECIDED conceptually; TECHNICAL UNKNOWN |
| [Wilds-2. Increased Wild Pokémon Level Range](#wilds-2-increased-wild-pokémon-level-range) | IMPLEMENTED |
| [Wilds-3. Starting-City Distance-Based Wild Level Caps](#wilds-3-starting-city-distance-based-wild-level-caps) | IMPLEMENTED (near complete) |
| [Wilds-4. Fishing Rod Progression](#wilds-4-fishing-rod-progression) | PARTIALLY IMPLEMENTED |
| [Wilds-5. Pokémon Generations / Content Scope](#wilds-5-pokémon-generations--content-scope) | PARTIALLY DECIDED |
| [Wilds-6. Technical Investigations](#wilds-6-technical-investigations) | TECHNICAL UNKNOWN |

---

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

**Wild level progression:** [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) is **implemented (near complete)**. Badge / encounter-tile wild gating ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)) is **not** the model for wild levels — kept in docs only for HM/League gates and the Route 46 template.

---


---

# Wilds-2. Increased Wild Pokémon Level Range

**Status: IMPLEMENTED** — distance caps ([Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)), [level distribution](#level-distribution), **stage adjust** (level-up + [synthetic edges](#synthetic-evolution-stages-wild--trainer), shared with trainer battles). Details: `documentation/HACK-NOTES.md` § **Wild level caps (distance-based)**.

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

Encounter tables still list a base species (e.g. Poliwhirl, Exeggcute). After the rolled level is known, stage selection runs in order:

1. **`AdjustSpeciesForLevel`** — linear **`EVO_LEVEL`** chains from `data/Evolutions.c` (implemented today).
2. **Synthetic edges** — `data/synthetic_evolution_thresholds.tsv`: if level ≥ `min_level`, may step `from` → `to` (chained up to 8 steps). Runtime: `AdjustEncounterSpeciesForLevel()` in `include/encounter_species_stage.h`; ROM data from `scripts/build/gen_synthetic_evo_edges.py` → `sSyntheticEvoEdgesData` in field overlay.

Synthetic thresholds **do not** change how the player evolves Pokémon ([World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones) stays player-facing). Wild/trainer mons still get moves and stats from the **final** species (`PokeParaSet` / `InitBoxMonMoveset`), same as today.

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

## Separation of concerns

Three independent inputs:

| Input | Determines |
|-------|------------|
| Ecology ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)) | **Which family** can spawn |
| Area maximum ([Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range), [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)) | **Possible encounter levels** |
| Rolled level + stage rules | **Evolution stage** (level-up tables + synthetic edges) |

---


---

# Wilds-3. Starting-City Distance-Based Wild Level Caps

**Status: IMPLEMENTED (near complete)** — distance caps verified in-game (Sep 2026). Remaining gaps: Safari Zone, Bug Catching Contest, roamers/scripted wilds, 18-city start menu wiring, balance tuning.

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

For **every valid starting city** ([Vision-3](DESIGN-VISION.md#vision-3-starting-location) — 18 cities):

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

Normal wild encounters use the cap + [Wilds-2 level distribution](#level-distribution). Roamers, Safari, and most scripted wilds are unchanged — see table above.

Player badge level caps run up to **70–80** ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps)). Wild area caps use a lower ceiling (**3–60**) for balance:

```
levelCap = 57 × route_distance / max_route_distance + 3
```

- `route_distance` — shortest graph distance from the chosen starting city to the encounter area.
- `max_route_distance` — farthest reachable distance for that starting city on the same graph.
- Integer division; at distance **0** → cap **3**; at max distance → cap **60**.
- **PoC starting city:** Mom menu stores the choice; ROM still maps **3 menu options** to New Bark / Goldenrod / Saffron table rows until the full 18-city picker ships.

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
