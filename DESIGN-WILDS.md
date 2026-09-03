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

**Guard-style gating** ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)) is an **alternative** to distance caps for wild levels — likely **minimal** if Wilds-3 ships (Victory Road, HM/Flash, endgame pockets only). Trainer and Gym scaling by badge tier ([Battle-8](DESIGN-BATTLES.md#battle-8-implementation)) should land before broad ecology implementation so starting-city balance does not depend entirely on static vanilla tables.

---


---

# Wilds-2. Increased Wild Pokémon Level Range

**Status: DECIDED conceptually; TECHNICAL UNKNOWN for implementation**

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
| Rolled level + family rules | **Valid evolution stage** |

---


---

# Wilds-3. Starting-City Distance-Based Wild Level Caps

**Status: TBD — leading alternative to World-2 wild gating**

Primary alternative to badge-guard / encounter-tile wild progression ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)). **Undecided** which model ships; **likely:** Wilds-3 for wild levels **plus** a **small** amount of World-2 (Victory Road, HM/Flash gates, optional hard zones — not guard spam on every route).

If Wilds-3 is primary, the player can **enter** high-distance areas early but encounters scale from [Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range) level ranges tied to graph distance — danger is in the fights, not a coord gate on the grass.

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

For **every valid starting city**:

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

## Edge costs (tuning TBD)

Costs do not necessarily equal one per map transition. Possible weighting:

| Connection type | Example cost |
|-----------------|-------------:|
| city / town interior connector | 0 or negligible |
| short connector maps | 1 |
| SS Aqua / Magnet Train | 1 |
| normal route traversal | 2 |
| substantial dungeon | 3+ |
| deeper dungeon section | additional cost |

Exact weighting should be tuned after generating and inspecting the distance matrix.

## Distance → tier → level cap

Convert graph distance to **progression tiers** rather than directly to level numbers.

Conceptual example only (not final):

| Distance from start | Tier |
|--------------------:|-----:|
| 0–1 | 0 |
| 2 | 1 |
| 3 | 2 |
| … | … |
| farthest areas | highest |

Then map tier → wild maximum level for use by [Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range).

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

| Region | Location | Notes |
|--------|----------|--------|
| South Johto | Route 32 Pokémon Center | Vanilla Old Rod area |
| West Johto (coast) | Olivine City | Vanilla fishing NPC |
| East Johto | **Blackthorn City** | **Likely new NPC** — gives Blackthorn a way to farm at lv5 since all connected routes are too high level |
| West Kanto | **Viridian City or Pewter City** | **Likely new NPC** |
| Mid Kanto (coast) | Vermilion City | **Likely new NPC** (not vanilla Rod giver) |
| South Kanto | Fuchsia City | **Likely new NPC** (not vanilla Rod giver) |
| East Kanto | Route 12 / Silence Bridge | Vanilla Super Rod area |

Exact map and `(x, z)` per guru are implementation details; prefer towns the player already visits for other reasons (Mart, Gym, ferry) over dead-end-only cells.

Any guru on this network reads the same global fishing-progression state and offers the appropriate Rod (Old on first talk, then Good / Super when family counts are met).

---


---

# Wilds-5. Pokémon Generations / Content Scope

**Status: TBD / TECHNICAL INVESTIGATION**

The final set of supported Pokémon generations has not been decided.

The project is based on HG-Engine, which supports a number of mechanics, Pokémon/forms, moves, abilities and other features beyond vanilla Generation IV.

Do NOT currently assume:

- Gen I–II only;
- Gen I–IV only;
- Gen I–VI;
- Gen I–IX;
- any other exact cutoff.

The available HG-Engine capabilities should be investigated before making this decision.

The project is open to later-generation Pokémon and mechanics where they work well with the game.

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


Primary design: [Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology) (ecology seed), [Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range) (broad level bands), [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) (distance-based caps — TBD).

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
