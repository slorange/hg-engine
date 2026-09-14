# Pokémon Wandering Heart — Future & Addon Systems

> **V2–V4 scope:** Apricorn economy, ball rebalance, Full Moon, unlimited moves. Not required for the core ROM.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Core vision:** [`DESIGN-VISION.md`](DESIGN-VISION.md)
>
> **Scope:** Everything from [Future-2](#future-2-apricorn-economy) onward is **V2** unless marked otherwise. **V3** begins at [Future-15](#future-15-full-moon-system-v3). **V4** begins at [Future-16](#future-16-unlimited-learned-moves-v4). None of this is required for the core open-world ROM.
>
> **Dependency (V2 only):** Apricorn tree refresh assumes an accelerated in-game clock ([World-4](DESIGN-WORLD.md#world-4-accelerated-daynight-cycle)). That clock is core; the Apricorn economy is not.

## Sections

| Section |
| ------- |
| [Future-1. Instructions](#future-1-instructions) |
| [Future-2. Apricorn Economy](#future-2-apricorn-economy) |
| [Future-3. Poké Ball Design Philosophy](#future-3-poké-ball-design-philosophy) |
| [Future-4. Shop Balls](#future-4-shop-balls) |
| [Future-5. Removed / Replaced Balls](#future-5-removed--replaced-balls) |
| [Future-6. Apricorn Balls (overview)](#future-6-apricorn-balls-overview) |
| [Future-7. Fast Ball](#future-7-fast-ball) |
| [Future-8. Heavy Ball](#future-8-heavy-ball) |
| [Future-9. Love Ball](#future-9-love-ball) |
| [Future-10. Friend Ball](#future-10-friend-ball) |
| [Future-11. Level Ball](#future-11-level-ball) |
| [Future-12. Dream Ball](#future-12-dream-ball) |
| [Future-13. Quick Ball](#future-13-quick-ball) |
| [Future-14. Dusk Ball](#future-14-dusk-ball) |
| [Future-15. Full Moon System (V3)](#future-15-full-moon-system-v3) |
| [Future-16. Unlimited Learned Moves (V4)](#future-16-unlimited-learned-moves-v4) |
| [Future-17. Technical investigation (when V2 is scheduled)](#future-17-technical-investigation-when-v2-is-scheduled) |
| [Future-18. Open design questions (V2–V4)](#future-18-open-design-questions-v2v4) |
| [Future-19. Map Editing — World Connectivity Wishlist](#future-19-map-editing--world-connectivity-wishlist) |

---

# Future-1. Instructions

- Do **not** implement ball/Apricorn changes unless explicitly requested for the current task.
- Prefer config-driven catch multipliers where hg-engine already supports them.
- Mom's starting grants already include an **Apricorn Box** for inventory convenience — not this full V2 rebalance.

---

# Future-2. Apricorn Economy

Apricorns become a renewable crafting resource tied to the accelerated game clock.

Current target:

- trees refresh approximately once per in-game day;
- each tree yields approximately **3–5 Apricorns**.

With the current ~30-minute day target, this creates a much faster renewable economy than vanilla HGSS.

Exact quantities and refresh timing remain subject to balance testing.

The player should not need to repeatedly return to Azalea Town merely to craft Apricorn Balls.

Pokémon Center crafting or another distributed crafting system is currently being considered.

---

# Future-3. Poké Ball Design Philosophy

Poké Balls are being rebalanced around two broad categories.

## Shop Balls

> **Readily available, generally weaker/reliable bonuses.**

The player can purchase these in quantity.

They should be useful without one infinitely purchasable ball becoming the obvious solution to nearly every encounter.

## Apricorn Balls

> **Renewable but resource-limited, with stronger and more specialized bonuses.**

Apricorn harvesting/crafting limits availability enough that these balls can have substantially stronger effects.

The player should have reasons to carry and select different balls for different encounters.

The intended outcome is explicitly to avoid:

> "Buy 99 Quick Balls and throw one at everything."

---

# Future-4. Shop Balls

| Ball | Maximum | Effect |
|---|---:|---|
| Poké Ball | 1× | Standard |
| Great Ball | 1.5× | Standard |
| Ultra Ball | 2× | Standard |
| Timer Ball | 4× | Increasing bonus during long battles |
| Repeat Ball | 3× | Bonus against previously caught species |
| Net Ball | 3× | Bonus against Water or Bug Pokémon |

Additional shop balls may exist later.

However, **Quick Ball and Dusk Ball are intentionally removed from normal shops**.

---

# Future-5. Removed / Replaced Balls

The following vanilla/special balls are currently removed or replaced:

- Heal Ball
- Dive Ball
- Luxury Ball
- Nest Ball
- Lure Ball

## Heal Ball

The Heal Ball is unnecessary because **all newly caught Pokémon are automatically healed** ([Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition)).

## Luxury Ball

Its conceptual role is replaced by the redesigned Friend Ball.

## Nest Ball

Removed due to conceptual overlap with Level Ball.

## Dive / Lure

Removed because the ball roster otherwise contains excessive overlap between Water-oriented capture bonuses.

These decisions can theoretically be revisited, but they are not currently part of the intended ball roster.

---

# Future-6. Apricorn Balls (overview)

New Apricorn colours may be introduced.

Colours are chosen primarily to communicate the identity of the resulting Ball rather than to preserve vanilla Apricorn associations.

Current mapping:

| Apricorn | Ball | Maximum | Proposed Effect |
|---|---|---:|---|
| 🔴 Red | Fast Ball | 5× / 10× beasts | Scales roughly 1–5× according to base Speed; 10× against roaming legendary beasts |
| 🩶 Grey | Heavy Ball | 5× | Scales roughly 1–5× according to weight |
| 🩷 Pink | Love Ball | 8× | 3× opposite gender; 8× opposite gender + compatible Egg Group |
| 🟢 Green | Friend Ball | 8× | 8× against qualifying friendship-evolution families; caught Pokémon starts at 200 friendship |
| 🟡 Yellow | Level Ball | 8× | Scales according to player's level advantage |
| 🟣 Purple | Dream Ball | 4× | Sleeping target |
| 🔵 Blue | Quick Ball | 5× | First turn |
| ⚫ Black | Dusk Ball | ~7× | 4× at night; increasingly powerful with cave depth |

Grey and Purple are intentionally new Apricorn colours.

This immediately communicates to experienced HGSS players that the Apricorn system has changed.

---

# Future-7. Fast Ball

Fast Ball scales according to the target species' **base Speed**.

Target range:

**~1× to 5×**

Exact thresholds/formula remain TBD.

## Roaming beasts

Fast Ball receives:

**10×**

against the roaming legendary beasts.

The intended targets are specifically the Johto roaming beasts such as:

- Raikou;
- Entei;
- Suicune, where relevant to encounter implementation.

This is a deliberate thematic specialty.

---

# Future-8. Heavy Ball

Heavy Ball scales according to target weight.

Maximum:

**5×**

The exact weight thresholds/formula remain TBD.

---

# Future-9. Love Ball

Love Ball:

**3×** against an opposite-gender target.

**8×** if the target is opposite gender AND shares a compatible Egg Group.

This intentionally makes Love Ball extremely strong when its narrower thematic condition is fully satisfied.

---

# Future-10. Friend Ball

Friend Ball combines capture specialization with its friendship utility.

## Capture modifier

**8×**

against a Pokémon belonging to an evolutionary family that contains a friendship evolution.

The bonus applies to the **entire evolutionary family**, not only the exact species that evolves through friendship.

For example, if a family contains a friendship evolution, other catchable members of that family can also qualify.

## Friendship

Pokémon caught in a Friend Ball begin at:

**200 friendship**

This puts friendship-evolution Pokémon close to being ready to evolve.

---

# Future-11. Level Ball

Maximum:

**8×**

The Ball becomes stronger based on the player's level advantage over the target.

The vanilla concept is retained.

The exact progression may become more gradual than vanilla.

Formula:

**TBD**

---

# Future-12. Dream Ball

Dream Ball receives:

**4×**

against sleeping Pokémon.

Because Sleep is already one of the strongest capture statuses, the bonus intentionally remains lower than the most specialized Apricorn Balls.

---

# Future-13. Quick Ball

Quick Ball receives:

**5×**

on the first turn.

Quick Ball is moved from normal shops into the Apricorn economy because an infinitely purchasable 5× first-turn ball otherwise risks becoming the default capture strategy.

---

# Future-14. Dusk Ball

Dusk Ball receives:

**3× at night.**

In caves, its strength increases according to cave depth.

Current concept:

- shallow cave → approximately 4×;
- deeper floor → approximately 5×;
- deeper still → approximately 6×;
- deepest areas → approximately 7×.

Exact mapping between map/floor depth and modifier remains TBD.

This gives Dusk Ball an unusually powerful ceiling while requiring increasingly specialized conditions.

---

# Future-15. Full Moon System (V3)

A full-moon system is NOT part of the initial intended scope.

If implemented later, it should be a meaningful world system rather than existing solely to justify Moon Ball mechanics.

Possible system:

- full moon every X in-game days;
- lasts several nights;
- special encounters;
- NPC dialogue/world changes;
- quests/events;
- potentially special legendary/mythical content;
- Darkrai/Lunala-related content depending on available generations.

Do not implement Moon Ball capture rules without this broader world system.

## Moon Ball

**8×** against every member of an evolutionary family containing a Moon Stone evolution.

During a full moon:

**8× against all Pokémon.**

Therefore the Moon Ball is normally niche but temporarily becomes a powerful general-purpose Ball during the event.

Do not implement the Moon Ball independently unless the broader moon system is intentionally brought into scope.

---

# Future-16. Unlimited Learned Moves (V4)

Long-term desired design:

> **Pokémon retain every move they learn rather than being restricted to four moves.**

The inspiration is closer to the Pokémon anime: learning a fifth move does not require permanently forgetting one of the previous four.

This means genuinely having access to more than four learned moves, NOT merely selecting four moves before each battle from a larger remembered list.

This is expected to be technically difficult.

Potentially affected systems include:

- Pokémon data structures;
- save format;
- box storage;
- battle UI;
- move-selection UI;
- AI;
- move learning;
- evolution;
- scripts;
- compatibility assumptions throughout HGSS/HG-Engine.

This should NOT be attempted as part of initial development.

Before implementation, a dedicated feasibility investigation is required.

---

# Future-17. Technical investigation (when V2 is scheduled)

Questions to resolve before implementation:

- additional Apricorn colours;
- inventory/data representation;
- crafting UI and locations;
- tree objects and refresh logic;
- custom Ball formulas in hg-engine;
- cave-depth detection for Dusk Ball;
- compatibility with existing item data and shops.

---

# Future-18. Open design questions (V2–V4)

- Exact Apricorn yield and refresh rate.
- Exact Apricorn crafting mechanism and locations.
- Fast Ball intermediate Speed curve.
- Heavy Ball weight thresholds.
- Level Ball scaling formula.
- Dusk Ball cave-depth mapping.
- Whether any removed shop balls return in a revised roster.

**V3 (Full Moon / Moon Ball):**

- Full-moon calendar cadence and duration.
- Which encounters, NPCs, and quests change during the event.
- Moon Ball crafting source (Apricorn colour TBD).

**V4 (unlimited moves):**

- Feasibility of expanding move storage in save data and battle UI.
- Whether any intermediate design (remember-all, pick-four-per-battle) is acceptable as a stepping stone.

---

# Future-19. Map Editing — World Connectivity Wishlist

These changes are deferred until reliable HGSS map/geometry editing is possible.

## Surface Fixes

- Replace the Route 42 ferry NPC with a physical bridge.
- Remove the Route 4 one-way ledge currently handled by the "ledge bump" NPC.

## Johto Underground Network

Expand the cave system into a connected underground travel network.

- **Union Cave**
  - Connect to Slowpoke Well.
  - Connect to Dark Cave.
  - Connect underground to Ruins of Alph.

- **Dark Cave**
  - Connect to Union Cave.
  - Connect to Mt. Mortar.
  - Connect to Mt. Silver.
  - Connect to Ice Path.
  - Connect to Tohjo Falls.

- **Mt. Mortar**
  - Connect to Ice Path.

The intent is for Johto's caves to function as a genuine secondary transportation network rather than a collection of mostly isolated dungeons.

Connections should still preserve dungeon identity and progression rather than turning every cave into one indistinguishable tunnel system.

## New Surface / Water Connections

- Add a water route connecting Route 40 / Whirl Islands to Goldenrod Harbor.
- Add a route connecting Olivine to National Park.

## Kanto Connections

- Add a route from Viridian City to Route 16.
- Add a route south of Mt. Moon:
  - directly connect Route 3 to Route 4;
  - branch south toward Celadon City.
- Water route from Route 27 to Route 21

## Design Goal

Use new connections to create multiple legitimate paths through the world.

The player should gradually discover that Johto and Kanto contain:

- the obvious surface road network;
- water routes;
- an interconnected cave network;
- fast travel between already discovered cities.

The underground network should reward exploration and map knowledge without being required for basic city/Gym access.

---
