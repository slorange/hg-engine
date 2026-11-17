# Pokémon Wandering Heart — Wild Encounters & Ecology

> Seeded ecology, wild level caps, level rolls, encounter stage, fishing, and content scope.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md)

## Sections

| Section | Status |
| ------- | ------ |
| [Wilds-1. Starting-City Distance-Based Wild Level Caps](#wilds-1-starting-city-distance-based-wild-level-caps) | IMPLEMENTED* |
| [Wilds-2. Wild Pokémon Level Range](#wilds-2-wild-pokémon-level-range) | IMPLEMENTED |
| [Wilds-3. Encounter Stage (Evolution & Devolution)](#wilds-3-encounter-stage-evolution--devolution) | IMPLEMENTED |
| [Wilds-4. Fishing Rod Progression](#wilds-4-fishing-rod-progression) | IMPLEMENTED |
| [Wilds-5. Pokémon Generations / Content Scope](#wilds-5-pokémon-generations--content-scope) | DECIDED (release scope) |
| [Wilds-6. Per-save wild ecology shuffle](#wilds-6-per-save-wild-ecology-shuffle) | IMPLEMENTED* |
| Expanded Pokédex / generations | Moved — [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes) |

Wilds 1 and Wilds 6 are implemented with the exception of Safari Zone.

**Encounter pipeline (wild grass/cave/etc.):** [Wilds-6](#wilds-6-per-save-wild-ecology-shuffle) species (where hooked) → [Wilds-1](#wilds-1-starting-city-distance-based-wild-level-caps) area cap → [Wilds-2](#wilds-2-wild-pokémon-level-range) rolled level → [Wilds-3](#wilds-3-encounter-stage-evolution--devolution) species stage. **Trainer battles** use the same stage rules after their level is set ([Battle-2 § Trainer scaling](DESIGN-BATTLES.md#trainer-scaling-release)).

---

# Wilds-1. Starting-City Distance-Based Wild Level Caps

**Status: PARTICIALLY IMPLEMENTED**

Each area’s **maximum wild level** comes from graph distance from the chosen start city. Actual encounter levels are rolled in [Wilds-2](#level-distribution)

## World graph

Build a **directional graph** representing the explorable world:

- cities / towns;
- routes;
- caves / dungeons;
- one-way traversal where relevant (e.g. ledges);

## Build-time precomputation

For **every valid starting city** ([Story-1](DESIGN-STORY.md#story-1-starting-city-and-home) — 18 cities, index **0–17**):

1. Shortest-path **exploration distance** from that city to each encounter area on the world graph.
2. Convert distance → **maximum wild level** (and optional tier for tuning).
3. Precompute the full matrix **offline** and ship it as a ROM lookup table — **no graph traversal during gameplay**.

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
| Bug Catching Contest | **Hooked** — shares National Park cap; needs in-game verification |
| Scripted wild battles | **Not hooked** (script levels unchanged) |

## Edge costs

PoC uses **uniform edge cost = 1** per graph hop. Could change edge cost based on route/dungeon size / traversal time. Could reduce town cost.

## Distance → level cap (PoC formula)

Wild area caps have range (**5–60**):

```
levelCap = 55 × max(0, route_distance − 1) / (max_route_distance − 1) + 5
```

- `route_distance` — shortest graph distance from the chosen starting city to the encounter area.
- `max_route_distance` — farthest reachable distance for that starting city on the same graph.
- Integer division; at distance **0–1** → cap **5** (starter town + first connected routes); at max distance → cap **60**.

### Level-cap post-processing (build-time)

After the distance formula, `scripts/build/gen_wild_level_caps.py` applies rows in `scripts/dev/Route Levels/cap_postprocess.tsv` per encounter area’s graph node (`encounter_area_graph.tsv`):

| Kind | Meaning |
|------|---------|
| **fixed** | Replace distance cap with an exact value (endgame tiers). |
| **floor** | `max(distance cap, value)` — HM-gated regions where nearby start cities would otherwise undershoot. |

**Fixed caps (16-badge vs Waterfall tier):**

| Graph location | Wild cap |
|----------------|--------:|
| **23**, **Victory Road** | **75** |
| **28**, **Mt. Silver**, **Cerulean Cave** | **85** |

**HM floors** (badge tier at HM unlock — [Battle-2](DESIGN-BATTLES.md#cap-ladder), [World-3](DESIGN-WORLD.md#badge--field-abilities-single-reference)):

| Graph location | Gating HM | Min cap |
|----------------|-----------|--------:|
| **Dark Cave**, **Rock Tunnel** | Flash | **14** |
| **Whirl Islands** | Whirlpool | **50** |
| **26**, **27** | Waterfall | **62** |

### Cave depth (future)

PoC treats each cave dungeon as **one graph node** → one cap for every floor. Later, split dungeon subareas into separate graph nodes (or override rows) so deeper HM-gated sections can exceed entrance tiers without per-floor encounter tables.



---

# Wilds-2. Wild Pokémon Level Range

**Status: IMPLEMENTED** — uses area caps from [Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps); stage after roll in [Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution).

Add occasional low-level “baby” encounters so early stages stay findable.

## Design intent

Many areas will have high level caps (40+), but we don't want a player who's trying to complete the dex to have to breed up hundreds of babies because only the final form is available in the wild.

## Level distribution

| Condition | Roll |
|-----------|------|
| Area cap below **10** | Adult band only: uniform **`[⌊0.9×cap⌋ − 2, cap]`** (e.g. cap 9 → **6–9**) |
| Cap **≥ 10**, **15%** “baby” | Uniform **2–7** |
| Cap **≥ 10**, **85%** “adult” | Uniform **`[⌊0.9×cap⌋ − 2, cap]`** (e.g. cap 10 → **7–10**; cap 60 → **52–60**) |

After the level is rolled, [Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution) picks the evolution stage for that family.

---

# Wilds-3. Encounter Stage (Evolution & Devolution)

**Status: IMPLEMENTED** — wild encounters resolve their stage after the [Wilds-2](DESIGN-WILDS.md#level-distribution) level roll; trainer teams resolve it after [Battle-2](DESIGN-BATTLES.md#trainer-scaling-release) assigns level. Player-owned Pokémon use their actual evolution methods ([World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones)).

For both wild and trainer mons, we need to handle the cases where a first stage pokemon is now high level, and a late stage pokemon is now low level.

For level up evolutions this is trivial, we evolve or devolve based on the level. Learned move evolutions use the level the move is learned. Example in this ROM Piloswine learns Ancient Power at 36, so that is the threshold we use for wild and trainer Piloswine.

## Baby species

Ordinary wild encounters and trainer teams skip Pichu, Cleffa, Igglybuff, Togepi, Smoochum, Elekid, Magby, Azurill, Wynaut, Budew, Chingling, Bonsly, Mime Jr., Happiny, Munchlax, Riolu, and Mantyke. Their first non-baby stage is the family’s minimum encounter stage, regardless of level or its usual evolution method.

The special low-level baby roll in [Wilds-2](DESIGN-WILDS.md#level-distribution) may still produce these babies. A low level from an ordinary roll does not grant this exception.

## Item and friendship evolution

For wild pokemon, a distinction is made for item evolutions based on whether this item could be found in the wild. Wild pokemon cannot evolve from friendship evolution.

**Natural items:** evolution stones, King’s Rock, Dragon Scale, Metal Coat, Reaper Cloth, Prism Scale, Razor Fang, Razor Claw, Deep Sea Tooth, Deep Sea Scale, Black Augurite, and Peat Block. Their encounter evolution does not require an actual item, time of day, or location condition.

**Trainer-only items:** Link Cable, Up-Grade, Dubious Disc, Protector, Electirizer, and Magmarizer. Their evolutions do not occur through wild stage selection.

**Wild natural-item evolutions:** probability increases linearly from **0%** at the later of **level 15** or **five levels after the source stage becomes available**, to **100% at level 60**. For example, Growlithe starts at 15; Poliwhirl becomes available at 25, so its Poliwrath/Politoed curve starts at 30. Once a source stage is available at level 60 or above, its natural-item evolution is certain.

**Trainer item evolutions:** probability increases linearly from **0% at 15** to **100% at 40** for ordinary trainers, or **100% at 25** for Gym Leaders and Elite Four. These endpoints use absolute level rather than time spent in the source stage. The Champion uses the same tier as Elite Four. Leader rematches retain Leader rates; ordinary rematches retain ordinary rates.

**Trainer friendship evolutions:** probability increases linearly from **0% at 15** to **100% at 25** for ordinary trainers, or **100% at 20** for the Leader tier.

## Fixed move-known thresholds

Minor adjustments made to the learnset to adjust evolution levels:
- Aipom → Ambipom: Double Hit at **28**; 
- Lickitung → Lickilicky: Rollout at **30**.
- Stantler → Wyrdeer: Psyshield Bash at **31**.
- Tangela → Tangrowth: AncientPower at **32**; 
- Girafarig → Farigiraf: Twin Beam at **32**; 
- Dunsparce → Dudunsparce: Hyper Drill at **32**.
- Yanma → Yanmega: AncientPower at **33**; 
- Primeape → Annihilape: Rage Fist at **35**.
- Piloswine → Mamoswine: AncientPower at **36** (Also Swinub → Piloswine at **22**)

## Special Cases

Where a pokemon can have multiple evolutions and the requirements are met, one is chosen at random. This applies to Wurmple, Nincada, Tyrogue, Kirlia, Snorunt, Eevee, Scyther. An additional check is done to ensure we don't end up with a gender / mon combination that isn't possible. If the pokemon ends up being a gallade or vespiquen then the gender is adjusted.

---

# Wilds-4. Fishing Rod Progression

**Status: IMPLEMENTED (Oct 2026)** — Shared rod script + **ten** guru sites; table below.

Rod tiers advance by **catching Water-type Pokémon**, not badges or visit order — a separate track from [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves) HMs. Every shipped guru uses the same progression; the player can talk to any of them for the next rod.

| Rod | Requirement |
|-----|-------------|
| **Old** | Free on first guru interaction |
| **Good** | **5** distinct evolutionary families with at least one **caught** member that is Water-type (primary or secondary) |
| **Super** | **15** such families |

Count **families**, not species (Poliwag + Poliwrath = 1). Use Pokédex caught flags so released or traded Pokémon still count. Branching lines stay one family.

**Guru network** — interchangeable **new** fishermen (sprite 347, no Yes/No before grant). Any shipped guru can hand out the next tier per [Wilds-4](#wilds-4-fishing-rod-progression) counts.

| Region | Location | Notes |
|--------|----------|--------|
| North East Johto | Route 44 | world (568, 183) |
| North West Johto | Olivine City | world (273, 248) |
| Central Johto | Route 34 (Day-Care) | world (358, 409) |
| South Johto | Route 32 Pokémon Center | Interior local (4, 15) (classic brother spot) |
| North Kanto | Route 24 / 25 border | world (1320, 65) — **duplicate** on events **025** + **026** (map seam) |
| West Kanto | Viridian City | world (1023, 264) |
| Mid Kanto | Vermilion City | world (1298, 304) |
| South Kanto | Fuchsia City | world (1230, 430) |
| East Kanto | Route 12 / Silence Bridge | world (1429, 319) |

---

# Wilds-5. Pokémon Generations / Content Scope

**Status: DECIDED (release scope)**

**Ship scope:** Gen I–IV plus the Volcarona line and Sylveon, Kleavor, Wyrdeer, Ursaluna, Annihilape, Farigiraf, and Dudunsparce. No broad Gen V+ rollout planned.

Every included family must have an acquisition source.

Evolution methods and item acquisition: [World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones).

---

# Wilds-6. Per-save wild ecology shuffle

**Status: PARTIALLY IMPLEMENTED**

At new-game creation, generate a **stable per-save wild Pokémon ecology** instead of fixed vanilla species for hooked methods.

This is **not fully random**. Species and families must still appear in appropriate habitats and encounter methods.

## Core rules

- **Families stay together geographically.** If the Zubat family is assigned to Dark Cave, Zubat / Golbat / Crobat all belong to that same habitat rather than being independently scattered.
- **Every obtainable family** must be available in at least one location.
- **Duplicate family locations** are allowed and desirable for common / generalist species.
- **Habitat compatibility** must be respected (aquatic families on water methods, cave species in caves, ice on snowy routes, and so on). Compatibility is often **weighted**, not strictly binary.
- **Encounter method compatibility** remains meaningful: fishing, Surf, grass / cave encounters, Headbutt, Rock Smash, etc.
- **Area identity** should stay coherent — typed locations favor families that match the area theme when land slots are themed.
- No requirement that every type appear separately in both Johto and Kanto.
- **Special encounters** — gifts, fossils, swarms, legendaries, static overworld Pokémon, etc. — need an explicit policy per category **TBD**.

## National Park and Bug-Catching Contest

National Park grass and the Bug-Catching Contest share one pool of 17 families. All 17 belong to the park in every save, an exception to the usual eight-family land pool and the random assignment per save file.

Both modes use the park's [distance cap](#wilds-1-starting-city-distance-based-wild-level-caps), [level distribution](#level-distribution), and [encounter stages](#wilds-3-encounter-stage-evolution--devolution).

Contest score is the sum of the stats, including maximum HP, not current HP. The contest is available **every day**, with **one entry per day**. The time limit is **four in-game hours**, using the existing accelerated clock (roughly 5 minutes).

See [World-8. Item acquisition channels](#world-8-item-acquisition-channels) for reward details

## Persistence and seed

Generation is deterministic from a save-specific world seed:

1. Generate ecology once per play session.
2. Store the assignment for that session.
3. **Never reshuffle** species locations during the same playthrough.
