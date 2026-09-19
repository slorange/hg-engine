# Pokémon Wandering Heart — Vision

> Core vision, open-world philosophy, and starting location.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **World:** `[DESIGN-WORLD.md](DESIGN-WORLD.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)` · **Battles:** `[DESIGN-BATTLES.md](DESIGN-BATTLES.md)` · **Story:** `[DESIGN-STORY.md](DESIGN-STORY.md)` · **Future:** `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)`

## Sections

| Section | Status |
| ------- | ------ |
| [Vision-1. Core Vision](#vision-1-core-vision) | PARTIALLY IMPLEMENTED |
| [Vision-2. Open-World Philosophy](#vision-2-open-world-philosophy) | PARTIALLY IMPLEMENTED |
| [Vision-3. Starting Location and Pokémon](#vision-3-starting-location-and-pokémon) | PARTIALLY IMPLEMENTED |

---

# Vision-1. Core Vision

**Status: PARTIALLY IMPLEMENTED**

Base game:

**Pokémon HeartGold / SoulSilver**

Pokémon Wandering Heart is intended to turn Johto and Kanto into a largely open-world Pokémon journey.

There should be little or no traditional linear story forcing the player's progression.

The player is not the singular protagonist around whom the entire world waits. They are another Pokémon trainer travelling through the world while many other trainers are undertaking journeys of their own.

The game should emphasize:

- exploration;
- collection;
- building a large roster rather than only six Pokémon;
- flexible progression;
- replayability;
- a living population of trainers ([Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) — deferred);
- strategically fair trainer battles ([Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) — deferred);
- reduced tedious resource management;
- meaningful individual battles rather than attrition;
- freedom to travel without making all content equally accessible from the beginning.

A core goal is to preserve the identity and world of HGSS while substantially changing how the player progresses through it.

---

---



# Vision-2. Open-World Philosophy

**Status: PARTIALLY IMPLEMENTED**

The central rule is:

> **Travel is open. Content can still be dangerous or gated.**

The player should generally be able to travel between cities regardless of badge count.

This does NOT mean that every route, dungeon, grass patch, encounter, or optional area must be immediately appropriate for a new trainer.

This specifically avoids a problem found in some previous open-world Pokémon hacks: allowing the player to begin in a late-game city while leaving the surrounding encounters and trainers designed for late-game progression.

Every possible starting location needs access to viable early-game content.

## World progression tools

Possible gating mechanisms include:

- guards;
- doors;
- badge-count checks;
- HM progression;
- blocked grass tiles;
- dungeon entrances;
- alternate paths;
- transportation around dangerous routes;
- encounter-tile checks (see below).

A single map can potentially contain areas intended for different progression levels.

For example, one set of grass tiles may be available immediately while another portion of the same route is blocked until a higher badge count.

As an alternative to route-wide guards, the player could be allowed to walk freely along a route's paths. Only when they attempt to step onto a dangerous encounter tile would they be stopped, with a message such as: *"The wild Pokémon here seem dangerous. You shouldn't enter yet."* This keeps travel open while still preventing inappropriate wild encounters.

Where a route is geographically necessary for travel between cities but cannot reasonably support unrestricted traversal, paid transportation should allow the player to bypass the dangerous section.

---

---



# Vision-3. Starting Location and Pokémon

**Status: PARTIALLY IMPLEMENTED** — **18-city menu**, **three-type starter pick** (grass / fire / water), and **Mom exit → start city** verified in-game (Sep 2026). Outdoor home-door routing (steps 2–4 below) not complete; see [Home wiring (four steps)](#home-wiring-four-steps).

## Starting city

**Status: IMPLEMENTED** — 18-city Mom menu; `VAR_PLAYER_START_CITY` drives wild level caps and Mom’s dynamic exit warp.

The player chooses their starting city from locations throughout Johto and Kanto.

**Starting city list** (used for [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps) distance precomputation):


| Index | City           | Region |
| ----- | -------------- | ------ |
| 0     | New Bark Town  | Johto  |
| 1     | Violet City    | Johto  |
| 2     | Azalea Town    | Johto  |
| 3     | Goldenrod City | Johto  |
| 4     | Ecruteak City  | Johto  |
| 5     | Olivine City   | Johto  |
| 6     | Cianwood City  | Johto  |
| 7     | Mahogany Town  | Johto  |
| 8     | Blackthorn City | Johto |
| 9     | Pallet Town    | Kanto  |
| 10    | Viridian City  | Kanto  |
| 11    | Pewter City    | Kanto  |
| 12    | Cerulean City  | Kanto  |
| 13    | Saffron City   | Kanto  |
| 14    | Lavender Town  | Kanto  |
| 15    | Celadon City   | Kanto  |
| 16    | Vermilion City | Kanto  |
| 17    | Fuchsia City   | Kanto  |


**In-game picker:** full table above (index **0–17** = menu choice = Wilds-2 distance row). Mom interior exit patched via `tools/patch_zone_event_start_city.py` ([HACK-NOTES § Open-world starting inventory](documentation/HACK-NOTES.md)).


### Home wiring (four steps)

Bidirectional “home” needs four warp behaviours per save. Canonical interior stays **`T20R0201`** (Mom, grants, PC upstairs).

| Step | Direction | Requirement | Status |
| ---- | --------- | ----------- | ------ |
| **1** | Leave Mom interior | Front door → **chosen start city’s** outdoor home door tile | **Complete** — dynamic exit warp + Mom `_set_home_dynamic_warp` |
| **2** | Enter start city’s outdoor home door | That door → **Mom interior (header 63)** | **Attempted, rolled back** — mass `zone_event` patch + RAM hook caused map-load crashes; see HACK-NOTES |
| **3** | Enter New Bark player-house door (when start ≠ New Bark) | → **displaced** vanilla interior for start city (not Mom cutscene) | **Not started** |
| **4** | Leave that displaced interior | → **New Bark outdoor** door tile | **Not started** |

**Planned v2 for step 2:** leave outdoor doors **vanilla** in ROM; on map load, patch **only the start city’s** home-door warp header to 63 (same timing as step 1, no mass revert loop). Steps 3–4 likely need a similar targeted runtime or interior-side pattern.

Displaced-interior NPC/story cleanup: [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog). Wiring recipe and rollback notes: `documentation/HACK-NOTES.md` § **Home = bidirectional door + interior swap**.

## Starter selection

**Status: PARTIALLY IMPLEMENTED**

Long-term options (any non-legendary, curated pools, location-specific pools) remain open. **v1 prototype:**


| Index | Species                         |
| ----- | ------------------------------- |
| 0–2   | Chikorita, Cyndaquil, Totodile  |
| 3–5   | Bulbasaur, Charmander, Squirtle |
| 6–8   | Treecko, Torchic, Mudkip        |
| 9–11  | Turtwig, Chimchar, Piplup       |


**Implemented (Sep 2026):** three **type menus** (grass / fire / water, four options each) in the Mom cutscene — player receives **one starter per type** (not vanilla three-ball `choose_starter`). Species table above. Details: `documentation/HACK-NOTES.md` § **Open-world starting inventory**.

## Intro timing (v1)

**Status: PARTIALLY IMPLEMENTED**

Flow runs **after Professor Oak / name / gender**. Player still wakes in **player house 2F (bedroom)** regardless of chosen city, walks downstairs, and Mom’s cutscene runs:

1. **City picker** — 18 cities ([Starting city](#starting-city)).
2. **Starter picker** (grass / fire / water menus, 4 options each → 3 Pokémon) — same Mom cutscene; bedroom wake stays vanilla.
3. **Mom grants** (bag, Pass, Pokédex, shoes, etc.) — same cutscene, after starter pick.
4. **Exit** — player walks out the front door to the chosen city (no post-cutscene teleport).

Vanilla story beats that assume a New Bark → Cherrygrove/Violet opening are **not fully removed yet** — see [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) and [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog).