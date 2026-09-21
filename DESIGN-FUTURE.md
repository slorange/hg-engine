# Pokémon Wandering Heart — Future & Addon Systems

Deferred systems and wishlist items. **Sections are not listed in intended implementation order**
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Core vision:** [`DESIGN-VISION.md`](DESIGN-VISION.md)
>

## Sections

| Section |
| ------- |
| [Future-1. Apricorn economy & Poké Ball rebalance](#future-1-apricorn-economy--poké-ball-rebalance) |
| [Future-2. Full Moon system](#future-2-full-moon-system) |
| [Future-3. Unlimited learned moves](#future-3-unlimited-learned-moves) |
| [Future-4. Map editing — world connectivity wishlist](#future-4-map-editing--world-connectivity-wishlist) |
| [Future-5. Per-save wild ecology shuffle](#future-5-per-save-wild-ecology-shuffle) |
| [Future-6. Expanded Pokédex / generations](#future-6-expanded-pokédex--generations) |
| [Future-7. Generated trainer & Gym parties](#future-7-generated-trainer--gym-parties) |
| [Future-8. Dynamic battle rosters & universal PC](#future-8-dynamic-battle-rosters--universal-pc) |
| [Future-9. Accelerated day/night cycle](#future-9-accelerated-daynight-cycle) |
| [Future-10. Living trainers & interactions](#future-10-living-trainers--interactions) |
| [Future-11. Encounter stage selection (wild + trainer)](#future-11-encounter-stage-selection-wild--trainer) |
| [Future-12. Berry economy & distribution](#future-12-berry-economy--distribution) |
| [Future-13. Expanded stone mechanics](#future-13-expanded-stone-mechanics) |

---

# Future-1. Apricorn economy & Poké Ball rebalance

Apricorn harvesting, crafting, and a two-tier ball roster (shop vs Apricorn). Tree refresh assumes [Future-9](#future-9-accelerated-daynight-cycle) (accelerated in-game clock).

## Apricorn economy

Apricorns become a renewable crafting resource tied to the accelerated game clock.

- trees refresh approximately once per in-game day;
- each tree yields approximately **3–5 Apricorns**.

With the ~30-minute day target, this is a faster renewable economy than vanilla HGSS. Exact quantities and refresh timing remain subject to balance testing.

The player should not need to repeatedly return to Azalea Town merely to craft Apricorn Balls. Pokémon Center crafting or another distributed crafting system is under consideration ([World-4](DESIGN-WORLD.md#world-4-pokémon-centers) notes).

### More Apricorn trees

We would like **additional Apricorn trees** across Johto and Kanto so harvesting is not tied to vanilla placement alone. That has **not** been technically investigated yet — see [Technical investigation](#technical-investigation) below.

## Ball design philosophy

**Shop balls** — readily available, generally weaker or reliable bonuses; useful without one infinitely purchasable ball dominating every capture.

**Apricorn balls** — renewable but resource-limited, with stronger specialized bonuses. 

Intended to avoid: *"Buy 99 Quick Balls and throw one at everything."*

## Shop balls

<!-- HTML table: pipe tables cannot set column width; colgroup gives a wider effect column in IDE preview -->
<table>
<colgroup>
<col style="width:16%">
<col style="width:10%">
<col style="width:74%">
</colgroup>
<thead>
<tr><th>Ball</th><th align="right">Maximum</th><th>Effect</th></tr>
</thead>
<tbody>
<tr><td>Poké Ball</td><td align="right">1×</td><td>Standard</td></tr>
<tr><td>Great Ball</td><td align="right">1.5×</td><td>Standard</td></tr>
<tr><td>Ultra Ball</td><td align="right">2×</td><td>Standard</td></tr>
<tr><td>Timer Ball</td><td align="right">4×</td><td>Increasing bonus during long battles</td></tr>
<tr><td>Repeat Ball</td><td align="right">3×</td><td>Bonus against previously caught species</td></tr>
<tr><td>Net Ball</td><td align="right">3×</td><td>Bonus against Water or Bug Pokémon</td></tr>
</tbody>
</table>


## Balls removed from the roster

<table>
<colgroup>
<col style="width:22%">
<col style="width:78%">
</colgroup>
<thead>
<tr><th>Ball</th><th>Why dropped</th></tr>
</thead>
<tbody>
<tr><td>Heal Ball</td><td>Unnecessary — newly caught Pokémon are auto-healed (<a href="DESIGN-BATTLES.md#battle-2-healing-and-attrition">Battle-2</a>).</td></tr>
<tr><td>Luxury Ball</td><td>Role absorbed by redesigned Friend Ball.</td></tr>
<tr><td>Nest Ball</td><td>Overlaps Level Ball conceptually.</td></tr>
<tr><td>Dive Ball</td><td>Water-capture overlap with Net ball.</td></tr>
<tr><td>Lure Ball</td><td>Water-capture overlap with Net ball.</td></tr>
</tbody>
</table>


## Apricorn balls

New Apricorn colours may be introduced. Colours signal ball identity rather than vanilla Apricorn associations. **Grey** and **Purple** are intentionally new — a signal to HGSS veterans that the system changed. Shipping new colours needs separate investigation (items, harvest, art) — see [Technical investigation](#technical-investigation).

<table>
<colgroup>
<col style="width:10%">
<col style="width:14%">
<col style="width:12%">
<col style="width:64%">
</colgroup>
<thead>
<tr><th>Apricorn</th><th>Ball</th><th align="right">Maximum</th><th>Proposed effect</th></tr>
</thead>
<tbody>
<tr><td>🔴 Red</td><td>Fast Ball</td><td align="right">5× / 10× beasts</td><td>~1–5× by base Speed; <strong>10×</strong> vs Johto roaming beasts (Raikou, Entei, Suicune where implemented). Speed/weight curves TBD.</td></tr>
<tr><td>🩶 Grey</td><td>Heavy Ball</td><td align="right">5×</td><td>~1–5× by weight. Thresholds TBD.</td></tr>
<tr><td>🩷 Pink</td><td>Love Ball</td><td align="right">8×</td><td>3× opposite gender; 8× opposite gender + compatible Egg Group.</td></tr>
<tr><td>🟢 Green</td><td>Friend Ball</td><td align="right">8×</td><td>8× vs families with a friendship evolution (whole family qualifies); caught mon starts at <strong>200</strong> friendship.</td></tr>
<tr><td>🟡 Yellow</td><td>Level Ball</td><td align="right">8×</td><td>Scales with player's level advantage (vanilla concept, possibly smoother curve). Formula TBD.</td></tr>
<tr><td>🟣 Purple</td><td>Dream Ball</td><td align="right">4×</td><td>Sleeping target (lower cap because Sleep is already strong).</td></tr>
<tr><td>🔵 Blue</td><td>Quick Ball</td><td align="right">5×</td><td>First turn only.</td></tr>
<tr><td>⚫ Black</td><td>Dusk Ball</td><td align="right">~7×</td><td>~4× at night; in caves, scales with depth (~4× shallow → ~7× deepest). Floor mapping TBD.</td></tr>
</tbody>
</table>

## Technical investigation

Before implementation:

- inventory/data representation;
- crafting UI and locations;
- tree objects and refresh logic;
- custom Ball formulas in hg-engine;
- cave-depth detection for Dusk Ball;
- compatibility with existing item data and shops.

**More trees (existing colours):** map authoring is **very difficult** ([Future-4](#future-4-map-editing--world-connectivity-wishlist)). Unknown whether Apricorns are baked into map assets or placed as field objects after load.

**New Apricorn colours:** item IDs, pick/harvest flow, Kurt or replacement crafting, ball data, UI strings, and **overworld art we do not have** (trees, Apricorn icons, ball graphics).

**Refresh economy** ties to [Future-9](#future-9-accelerated-daynight-cycle) once tree representation is understood.

## Open design questions

- Exact Apricorn yield and refresh rate.
- Exact Apricorn crafting mechanism and locations.
- Fast Ball Speed curve; Heavy Ball weight thresholds; Level Ball formula; Dusk Ball depth mapping.
- Whether any removed shop balls return in a revised roster.

---

# Future-2. Full Moon system

A full-moon system should be a meaningful world feature — not only a hook for Moon Ball mechanics.

Possible system:

- full moon every X in-game days;
- lasts several nights;
- special encounters;
- NPC dialogue/world changes;
- quests/events;
- potentially special legendary/mythical content;
- Darkrai/Lunala-related content depending on generation scope.

Do not implement Moon Ball capture rules without this broader system.

### Moon Ball

**8×** against every member of an evolutionary family containing a Moon Stone evolution.

During a full moon: **8× against all Pokémon** — niche normally, strong general-purpose ball during the event.

### Open design questions

- Full-moon calendar cadence and duration.
- Which encounters, NPCs, and quests change during the event.
- Moon Ball crafting source (Apricorn colour TBD).

---

# Future-3. Unlimited learned moves

Long-term desired design:

> **Pokémon retain every move they learn rather than being restricted to four moves.**

Learning a fifth move does not require permanently forgetting a previous one — genuinely more than four stored moves, not merely picking four before each battle from a larger list.

Expected to be technically difficult. Potentially affected: Pokémon data structures, save format, box storage, battle and move-selection UI, AI, move learning, evolution, scripts, and HGSS/HG-Engine assumptions.

---

# Future-4. Map editing — world connectivity wishlist

Deferred until reliable HGSS map/geometry editing is possible.

## Surface fixes

- Replace the Route 42 ferry NPC with a physical bridge.
- Remove the Route 4 one-way ledge currently handled by the "ledge bump" NPC.

## Johto underground network

Expand caves into a connected underground travel network.

- **Union Cave** — Slowpoke Well; Dark Cave; Ruins of Alph (underground).
- **Dark Cave** — Union Cave; Mt. Mortar; Mt. Silver; Ice Path; Tohjo Falls.
- **Mt. Mortar** — Ice Path.

Johto caves should function as a secondary transportation network, not isolated one-off dungeons. Preserve dungeon identity — not one indistinguishable tunnel system.

## New surface / water connections

- Water route: Route 40 / Whirl Islands ↔ Goldenrod Harbor.
- Route: Olivine ↔ National Park.

## Kanto connections

- Viridian City ↔ Route 16.
- South of Mt. Moon: Route 3 ↔ Route 4; branch south toward Celadon City.
- Water route: Route 27 ↔ Route 21.

## Design goal

Multiple legitimate paths through the world: surface roads, water routes, interconnected caves, and fast travel between discovered cities. The underground network rewards exploration without being required for basic city/Gym access.

---

# Future-5. Per-save wild ecology shuffle

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
- Habitat compatibility should often be **weighted** rather than strictly binary. Some families can plausibly live in several environments.
- **Encounter method compatibility** remains meaningful: fishing, Surf, grass / cave encounters, Headbutt, Rock Smash, etc.
- **Area identity** should remain coherent. If an area is intended to have a strong type / environment theme, generated families should preserve that theme.
- No considerations for regional distribution. There is no requirement that every type appear separately in both Johto and Kanto, since regional travel will be easy.
- **Special encounters** — gifts, fossils, swarms, legendaries, Red Gyarados, static overworld Pokémon, etc. — need an explicit policy for how they interact with this system (**TBD** per category).
- If there are more Pokémon families than route spots to support them, Safari Zone and in-game trades both work as backup catch-all options.

## Persistence and seed

Generation must be **deterministic from a save-specific world seed**:

1. generate ecology once when starting a new game;
2. save / store the seed or generated mapping;
3. **never reshuffle** species locations during the same playthrough.


## Gym Leader family location hint

After first Gym clear (alongside badge, HM, TM — see [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)):

The Leader offers to point the player toward **one evolutionary family** matching the Gym's type(s).

Example flow (Lt. Surge, Electric):

> *"As an extra reward, if there's any Electric-type you're looking for, I'll tell you where to look."*

The player picks from a curated list of families for that Gym. The Leader names a **concrete location** from the player's **generated ecology**, including encounter method when relevant:

> *"Chinchou can be found in Dark Cave using the Good Rod."*

**Rules:**
- One family choice per first Gym clear (not rematches unless redesigned later).
- Hint data must come from the save's ecology tables, not hardcoded vanilla locations.
- Multi-type Leaders (Whitney, Morty) offer families from **either** qualifying type.
- Family lists are curated per Leader — not every species of that type in the dex.
- Blue has no type and will need special handling. Consider giving him a curated list of rare mons unavailable by other gym leaders

## Technical investigation
- per-save ecology generation and persistence (`data/Encounters.c` replacement or overlay);
- family / habitat tagging data format;
- Pokédex and trainer hint integration;
- special / static / legendary encounter policy;
- grass-tile-specific encounter sets (if used alongside distance caps).

---

# Future-6. Expanded Pokédex / generations

**Current scope is:** [Wilds-4](DESIGN-WILDS.md#wilds-4-pokémon-generations--content-scope) — **Gen I–IV plus the Volcarona line**

But HG-Engine supports up to gen 9 minus Paradox and DLC.

---

# Future-7. Generated trainer & Gym parties

### Randomize species

Replace party species with **random eligible species** from the available dex ([Wilds-4](DESIGN-WILDS.md#wilds-4-pokémon-generations--content-scope)), then apply the same stage rules as release scaling ([Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented)) so the chosen form fits the level band.

## Gym rosters
Gyms (both trainers and leaders) are **monotype by default**, with exceptions:

| Leader | Gym type(s) for hints / filters | Roster notes |
|--------|--------------------------------|--------------|
| Whitney | **Normal** + **Fairy** | |
| Morty | **Ghost** + **Dark** | |
| Brock | **Rock** / **Ground** | Vulpix line |
| Blue | **Flexible** | No Specialty |
| Jasmine | Steel | Ampharos line |
| Misty | Water | Togepi line |
| Blaine | Fire | Rhydon line |

All other Leaders use their vanilla Gym type only.

## TMs and Held Items
Once a trainer's team is generated, we also give the trainer some TMs randomly, and teach them to their team where appropriate. TM list will need to be curated so no useless TMs are taught. Number and Quality of TMs should increase as Badge count increases. Gym trainers should have more of that Gym's type of TMs. Gym Leaders should get an additional boost of Number and Quality of TMs.

## Technical investigation

- random species for generated teams;
- monotype generation with curated exceptions.
- tms and held items

---

# Future-8. Dynamic battle rosters & universal PC

## Dynamic roster rules

**Each trainer's entire collection is their bench. The actual battle roster forms dynamically as Pokémon are revealed.**

Suppose a battle is 4v4. The player does not choose four Pokémon before battle. They initially choose one send-out; the opponent does the same.

Whenever the player may send out or switch, they may select:

1. a Pokémon already committed to this battle; or
2. an unused Pokémon from their entire collection.

The first time a unique Pokémon enters, it **permanently consumes one roster slot**. After the agreed number of unique Pokémon have entered, **the roster is locked**. Fainted Pokémon continue to occupy slots. The opponent follows the same rules.

## Counter-picking and information

Dynamic counter-picking is intentional. Neither side initially knows the other's full collection. Revealing a counter spends a roster slot — **advantage and commitment**. NPC AI should eventually understand this rather than selecting independently.

## PC / collection access

The player's storage is accessible anywhere: overworld, trainer battles, wild battles. No requirement to visit a Center PC to reorganize.

Exact wild-battle UI/selection behaviour is a technical design problem.

## Field party vs full collection

The six field Pokémon: following mon, EXP defaults ([Battle-6](DESIGN-BATTLES.md#battle-6-exp-share)), overworld presentation, convenient ordering.

The entire collection: accessible anywhere including in battle; trainer-battle bench; can satisfy HM field requirements ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

> **The player's collection is their team.**

## Technical investigation

- accessing boxed Pokémon from battle;
- introducing a boxed Pokémon into an active battle;
- tracking committed roster slots;
- dynamically generated opponent collections;
- opponent counter-picking AI;
- wild-battle PC access;
- battle UI;
- overworld / trainer / wild battle access vs vanilla party assumptions.

---

# Future-9. Accelerated day/night cycle

**Not required for initial release.**

HGSS's real-world clock should be replaced by an accelerated in-game clock.

Current target:

> **Approximately 30 real-world minutes = one complete in-game day.**

This number may be tuned.

The accelerated clock affects systems including:

- day/night encounters;
- evolutions;
- NPC behaviour;
- events;
- potentially other systems (including Apricorn refresh if [Future-1](#future-1-apricorn-economy--poké-ball-rebalance) is implemented).

## Time advancement

The player should be able to deliberately advance time rather than waiting.

### Resting at Pokémon Centers / hotels

Allows controlled advancement of time ([World-4](DESIGN-WORLD.md#world-4-pokémon-centers)).

### Portable resting

A tent, sleeping bag, camping system, or similar mechanic can potentially allow resting outside towns. Exact implementation TBD.

## Technical investigation

- replacing RTC dependencies;
- event compatibility;
- day/night rendering;
- encounter tables;
- evolutions;
- manual time advancement.

---

# Future-10. Living trainers & interactions

**Not required for initial release.** Initial release: static vanilla trainers with [Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented) scaling. Renewable TMs via [World-5](DESIGN-WORLD.md#world-5-tms) / [World-7](DESIGN-WORLD.md#world-7-shops), not trainer buy/sell economy.

## Living trainers

Ordinary Pokémon trainers should not primarily exist as static NPCs permanently staring at a single tile waiting for the player.

Trainers are intended to create the illusion of a population travelling through Johto and Kanto on Pokémon journeys of their own.

They can:

- move around cities;
- travel between locations;
- appear on routes;
- walk through grass;
- have different levels of progression;
- interact with the player in multiple ways;
- appear to be battling each other.

Each trainer has or represents a badge progression level. Trainer progression distributions may be influenced by location. The player should generally battle trainers whose progression is reasonably comparable to their own.

### Simulation requirements

The game does NOT necessarily need to permanently simulate hundreds of individual NPCs throughout the entire world.

A technically simpler system may generate or populate trainers when maps load while maintaining the **illusion** of a persistent travelling trainer population.

The experiential goal matters more than literally simulating every trainer off-screen.

## Trainer interactions

Living trainers are not exclusively battle dispensers.

### Pokémon location requests

A trainer may ask for a species location. If the player has encountered the requested Pokémon, they can provide a location from **generated ecology** ([Future-5](#future-5-per-save-wild-ecology-shuffle)). Rewards: items, money, encounter info, TMs, etc.

### Encounter information

Trainers may tell the player where undiscovered species can be found (ecology data). **Gym Leaders:** structured first-clear hint — [Future-7](#future-7-generated-trainer--gym-parties).

### Pokémon trades / item trading

Some trainers request trades or buy/sell items (sink for duplicates; source for rare TMs / held gear).

### TMs

Some trainers provide renewable access to otherwise rare TMs ([World-5](DESIGN-WORLD.md#world-5-tms)) — alternative to putting everything in static marts.

### Gym advice / other quests

Information about nearby undefeated Gyms or scaled teams; additional lightweight interactions TBD.

## Field population (living trainers)

Map-level trainer generation, movement, and placement — distinct from [Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented) battle-start scaling; location-weighted distributions and non-battle interactions.

## Technical investigation

- map spawning; movement; persistence; generated identities; badge counts; generated collections; map transitions; save-state requirements;
- ecology-linked location requests; reward economy; trade and item-exchange UI; TM distribution hooks.

---

# Future-11. Encounter stage selection (wild + trainer)

**Release behaviour** ([Wilds-1 synthetic stages](DESIGN-WILDS.md#synthetic-evolution-stages-wild--trainer), [Battle-4 trainer scaling](DESIGN-BATTLES.md#trainer-scaling-implemented)): after an encounter level is known, `AdjustEncounterSpeciesForLevel()` walks **prevos** through level-up and synthetic edges to the chain root, then walks **forward** applying both edge types (level ≥ `min_level` → step to evolved form; below threshold → lower stage). Verified Sep 2026 for wild rolls and trainer scaling (including devolving authored trade/stone finals). Wild and trainer battles share one ruleset today. Player evolution ([World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones)) — trade-item use-on-Pokémon and Linking Cord shipped; wild/trainer stage adjust is separate.

## Probabilistic synthetic evolutions

Today, crossing a synthetic threshold always evolves (except explicit `random50` **branch** picks among equally authored outcomes — Gloom, Poliwhirl, Clamperl, Wurmple — not partial rates on a single edge).

**Wishlist:** optional **partial** evolution for special methods (stone, trade, friendship, etc.) so tables can still list base species without every high-level encounter being fully evolved.

| Idea | Example |
|------|---------|
| Fixed rate above threshold | 50% of Growlithe at Lv 25+ appear as Arcanine; 50% stay Growlithe. |
| Level-scaled rate | Same threshold (e.g. 25), but probability rises with level — Lv 15 → 10%, Lv 30 → 40%, Lv 45 → 70%. |
| Method-specific defaults | Stone-tier edges might default to higher certainty; friendship-tier edges might default to lower. |

Authoring could extend `synthetic_evolution_thresholds.tsv` (or successor data) with `probability`, curves, or per-method columns. RNG should be **per encounter** (wild) or **per slot** (trainer), stable for that battle.

## Wild vs trainer vs Gym Leader divergence

Release: **identical** stage logic for wild rolls and trainer battle-start scaling (Gym Leaders use the same path at battle start today — [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).

**Wishlist:** separate parameters or TSV views by **encounter context**, with a simple ordering for synthetic-edge certainty:

**wild** → **ordinary trainer** → **Gym Leader** (each step: higher evolution rates across method classes, not only friendship).

| Method class | Wild (example intent) | Ordinary trainer | Gym Leader |
|--------------|----------------------|------------------|------------|
| Friendship / happiness | Very rare — wild mons do not “grind friendship” | Common — cared-for teams | Very common — ace teams feel fully bonded |
| Trade / held-item | Moderate — ecology, not player trades | Higher — plausible off-screen trades | Highest — elite teams with rare evolutions |
| Stone / location stone | Lower — stones are player tools | Slightly higher | Highest — Leaders’ signature lines often fully evolved at cap |

Rematches and Elite Four would share the **Gym Leader** tier

Implementation sketch: `AdjustEncounterSpeciesForLevel()` gains a **context** flag (`wild`, `trainer`, `gym_leader`, …) that selects probability tables, tier offsets, or multipliers without duplicating level-up chain logic.

---

# Future-12. Berry economy & distribution

Berries stay a meaningful **held-item** layer: the player cannot use Bag items in trainer battles ([Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition)), so automatic berry effects remain one of the main in-battle consumables. Growth via **Berry Pots** is unchanged in role.

**Scope:** keep **45 of 64** Gen IV berries, all obtainable in-game — no Pokéwalker courses, events, Pal Park, or multiplayer.

**Dropped (19):** Figy-family weak-heal berries (**159–163**); Poffin / contest berries (**164–168**, **175–183**) — no contest system and little use beyond Natural Gift.

## Berry Pots & starter supply

Give **Berry Pots at game start** (Mom’s opening conversation), replacing vanilla Route 36 Sudowoodo unlock. Include ~5 of each **basic** berry (Cheri–Persim)

## Acquisition by group

| Group | Item IDs | Role | Primary sources |
| ----- | -------- | ---- | ---------------- |
| Basic | **149–156** (Cheri–Persim) | Status cure, Leppa PP, Oran HP | Starter pack; Goldenrod & Celadon Dept. Stores (partial medicine replacement) |
| Lum + Sitrus | **157–158** | Full status / 25% max HP | Badge-scaled regular marts (~**6 badges**, tunable) |
| EV / friendship | **169–174** (Pomeg–Tamato) | −EVs, +friendship | Goldenrod Underground medicine seller (beside Haircut Brothers) |
| Type-resistance | **184–200** (Occa–Chilan) | Super-effective hit reduction | Themed **local specialty shops** (town ↔ type; detail in [World-7](DESIGN-WORLD.md#world-7-shops) — e.g. Wacan→Vermilion, Passho→Cerulean). Mom’s vanilla resist-berry purchasing **unchanged for now**. |
| Rare battle | **201–212** (Liechi–Rowap) | Pinch boosts, Enigma heal, Custap priority, Jaboca/Rowap counter | Violet City and Fuchsia City shard traders |

## Wild Pokémon holds

New global rule: any wild species may hold a berry (species-agnostic). If selected, pick uniformly from the **45 supported** Berries. Configurable hold rate - tentative 30%.

## Open design questions

- Starter quantities for the eight basics; exact Lum/Sitrus badge gate.
- Wild berry-hold probability
- Shard trade costs and bundle sizes.
- Final town assignment per resistance berry
- Berry Pot growth times/yields (unchanged? What about day/night cycle changes?)
- Whether to later remove, keep, or repurpose Mom’s resist-berry shop.

---

# Future-13. Expanded stone mechanics

Evolution stones become more flexible for the matching **elemental type** (Fire Stone on Fire-types, Water Stone on Water-types, etc.).

## Pokémon that do not normally evolve with that stone

Using the matching stone **lowers the next natural level-up evolution by ~5 levels** (one step toward the target stage). Exact stacking rules TBD.

Example — Cyndaquil line (natural levels **16** / **36**):

- Stone on Fire-type at **11+** / **31+** instead of waiting for 16 / 36.

Example — Rapidash (natural level **40**):

- Level **40** as today, **or** Fire Stone on Ponyta/Rapidash at **35+**.

## Pokémon that normally evolve by stone only

- **Stone at any level** (keep the classic convenience).
- **Also** a **high level-up path** without the stone.

| Stage pattern                                     | Stone                       | Level without stone |
| ------------------------------------------------- | --------------------------- | ------------------- |
| 1st stage, stone-only (e.g. Exeggcute, Growlithe) | matching stone at any level | **35**              |
| 2nd stage, stone-only (e.g. Gloom, Poliwhirl)     | matching stone at any level | **50**              |

## Open design questions

- Exact −5 behaviour: one-time per stage, permanent flag, or repeatable?
- Dual-types: either type matches, or primary type only?
- Using a stone on a Pokémon with no evolution in that line — no effect?
- Interaction with [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) evolution exclusions for generated trainer teams.

Shop availability for stones: [World-7](DESIGN-WORLD.md#world-7-shops).

---
