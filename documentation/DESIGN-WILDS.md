# Pokémon Wandering Heart — Wild Encounters & Ecology

> Seeded ecology, wild level caps, level rolls, encounter stage, fishing, and content scope.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md)

## Sections

| Section | Status |
| ------- | ------ |
| [Wilds-1. Starting-City Distance-Based Wild Level Caps](#wilds-1-starting-city-distance-based-wild-level-caps) | PARTIALLY IMPLEMENTED |
| [Wilds-2. Wild Pokémon Level Range](#wilds-2-wild-pokémon-level-range) | IMPLEMENTED |
| [Wilds-3. Encounter Stage (Evolution & Devolution)](#wilds-3-encounter-stage-evolution--devolution) | IMPLEMENTED (wild + trainer) |
| [Wilds-4. Fishing Rod Progression](#wilds-4-fishing-rod-progression) | IMPLEMENTED |
| [Wilds-5. Pokémon Generations / Content Scope](#wilds-5-pokémon-generations--content-scope) | DECIDED (release scope) |
| Per-save ecology shuffle | Moved — [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle) |
| Expanded Pokédex / generations | Moved — [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes) |

**Encounter pipeline (wild grass/cave/etc.):** [Wilds-1](#wilds-1-starting-city-distance-based-wild-level-caps) area cap → [Wilds-2](#wilds-2-wild-pokémon-level-range) rolled level → [Wilds-3](#wilds-3-encounter-stage-evolution--devolution) species stage. **Trainer battles** use the same stage rules after their level is set ([Battle-2 § Trainer scaling](DESIGN-BATTLES.md#trainer-scaling-release)).

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
| Bug Catching Contest | **Not yet** |
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

**Status: IMPLEMENTED** — shared by **wild encounters** (after [Wilds-2](DESIGN-WILDS.md#level-distribution) roll) and **trainer Pokémon** (after [Battle-2](DESIGN-BATTLES.md#trainer-scaling-release) assigns level). Player party evolution ([World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones)) is separate.

For both wild and trainer Pokemon, we need to handle the cases where 
 - A first stage pokemon is now high level
 - A late stage pokemon is now low level

Once **level is fixed**, stage adjust:

1. Walk **prevos** through level-up evolution chains and **synthetic edges** to find the chain root (so authored finals **devolve** at low levels).
2. Walk **forward** from that root, applying level-up thresholds then synthetic edges (minimum level per edge) up to a bounded number of steps.

Wild and trainer battles use the **same** rules today. Gym Leaders use the same path at battle start ([Battle-3](DESIGN-BATTLES.md#battle-3-gyms)). Wishlist: different evolution rates by context — [Future-11](DESIGN-FUTURE.md#future-11-encounter-stage-selection-wild--trainer).

## Synthetic evolution stages

Synthetic thresholds stand in for trade, stone, friendship, move-known, and similar methods so tables can list one species without every high-level encounter being fully evolved.

**Authoring tiers** (each data row has an explicit `min_level`; tiers guide the sheet, not runtime logic):

| Vanilla method | Stage 1 | Stage 2 |
|----------------|--------:|--------:|
| Trade (incl. held item) | 20 | 35 |
| Stone (incl. location-based) | 25 | 35 |
| Friendship (incl. time-of-day variants) | 20 | 30 |
| Move-known | HGSS learn level + 1 | — |

**Special:** Piloswine → Mamoswine uses **34** (AncientPower is Lv1/relearner in HGSS; Swinub → Piloswine at 33).

**Branches:** empty = single outcome; `random50` = pick one row at random for the same source + `min_level` (Gloom, Poliwhirl, Clamperl, Wurmple).

**Deferred until later:** Eevee, Tyrogue, Shedinja, gendered evolutions (Burmy, Combee, Gallade, Froslass, etc.).

Battle presentation (moves, stats, name, caught mon) follows the **resolved** stage species.

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

**Ship scope:** **Gen I–IV plus the Volcarona line**. No broad Gen V+ rollout in the first release.


Broader dex / generations: [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes).
