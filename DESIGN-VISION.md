# Pokémon Wandering Heart — Vision

> Core vision, open-world philosophy, and starting location.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **World:** `[DESIGN-WORLD.md](DESIGN-WORLD.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)` · **Battles:** `[DESIGN-BATTLES.md](DESIGN-BATTLES.md)` · **Story:** `[DESIGN-STORY.md](DESIGN-STORY.md)` · **Future:** `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)`

# Vision-1. Core Vision

**Status: DECIDED**

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
- a living population of trainers;
- strategically fair trainer battles;
- reduced tedious resource management;
- meaningful individual battles rather than attrition;
- freedom to travel without making all content equally accessible from the beginning.

A core goal is to preserve the identity and world of HGSS while substantially changing how the player progresses through it.

---

---



# Vision-2. Open-World Philosophy

**Status: DECIDED**

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



# Vision-3. Starting Location

**Status: PARTIALLY IMPLEMENTED** — v1 three-city picker and twelve-starter menu verified in-game; broader city list and starter pools still TBD ([Index-2](DESIGN.md#index-2-current-technical-baseline)).

## Starting city

**Status: DECIDED (prototype scope locked for v1 testing)**

The player chooses their starting city from locations throughout Johto and Kanto.

Long-term intention is broad freedom rather than a small set of traditional starting towns. **v1 prototype list (functionality testing only — not final design):**


| Index | City           |
| ----- | -------------- |
| 0     | New Bark Town  |
| 1     | Goldenrod City |
| 2     | Saffron City   |


Every available starting city must provide reasonable access to:

- appropriately levelled encounters ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)–[Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps));
- early trainer content;
- necessary services;
- transportation;
- a viable first Gym challenge.



### Home / house wiring (v1 approach)

Not a simple “redirect the house exit.” Each city needs a **designated outdoor door** that is “home” in both directions:

1. **Exit from home interior** → chosen city’s outdoor door tile.
2. **Enter that outdoor door** → same home interior (Mom, grants, PC upstairs).

**Interior swap (preferred v1 strategy):** keep **one canonical player house interior** (`T20R0201` / Mom scripts) for all starts. The outdoor door in the chosen city warps into it. On exit, `set_dynamic_warp` returns to that door. The **displaced vanilla house** (the one we repurposed as “home” in that city) becomes what New Bark’s player-house door leads into when the player did **not** start in New Bark — so walking into the old New Bark house does not dump the player into Mom’s cutscene by mistake.

Exact door/interior pairs are documented in `documentation/HACK-NOTES.md` (pret zone_event recon). Goldenrod and Saffron home doors verified in-game; **New Bark door swap** (displaced interior when start city ≠ New Bark) is deferred — see [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog).

**Implemented (Sep 2026):** 3-city `ListLocalText` menu in Mom cutscene → `VAR_PLAYER_START_CITY` (**0x4031**) → `_set_home_dynamic_warp`. Player walks to front door **(3, 10)** on 1F; dynamic exit warp lands at the chosen city’s outdoor home door. No post-cutscene teleport.

## Starter selection

**Status: DECIDED (prototype scope locked for v1 testing)**

Long-term options (any non-legendary, curated pools, location-specific pools) remain open. **v1 prototype:**


| Index | Species                         |
| ----- | ------------------------------- |
| 0–2   | Chikorita, Cyndaquil, Totodile  |
| 3–5   | Bulbasaur, Charmander, Squirtle |
| 6–8   | Treecko, Torchic, Mudkip        |
| 9–11  | Turtwig, Chimchar, Piplup       |


Twelve choices total; menu index stored in `VAR_PLAYER_STARTER` (**0x4030**). **Implemented:** 12-row `ListLocalText` text menu in Mom scr_seq **845** script **0** (`scr_seq_t20_mom_script0.s`); each branch uses `give_mon` (not vanilla `choose_starter` / 3-ball UI). Strings in `data/text/545.txt`. `src/starters.c` **is unused** on this path — see `HACK-NOTES.md`.

## Intro timing (v1)

**Status: DECIDED (prototype) — implemented in Mom cutscene**

Flow runs **after Professor Oak / name / gender**. Player still wakes in **player house 2F (bedroom)** regardless of chosen city, walks downstairs, and Mom’s cutscene runs:

1. **City picker** (3 options) — **implemented** in Mom script **0**, before starter menu.
2. **Starter picker** (12 options) — **implemented** in same cutscene; bedroom scr_seq **846** stays vanilla (no starter hook there).
3. **Mom grants** (bag, Pass, Pokédex, shoes, etc.) — same cutscene, after starter pick.
4. **Exit** — player walks to front door; dynamic warp to chosen city. Non–New Bark cities use outdoor-door + dynamic-warp wiring documented in `HACK-NOTES.md`.

Vanilla story beats that assume a New Bark → Cherrygrove/Violet opening are **not fully removed yet** — see [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) and [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog).