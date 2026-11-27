# Pokémon Wandering Heart — Story & Cleanup

> Open-world intro and script policy (what vanilla must not do).
>
> **Index:** [`DESIGN.md`](DESIGN.md)

## Sections

| Section | Status |
| ------- | ------ |
| [Story-1. Starting City and Home](#story-1-starting-city-and-home) | IMPLEMENTED |
| [Story-2. Starter Pokémon and Intro Flow](#story-2-starter-pokémon-and-intro-flow) | IMPLEMENTED |
| [Story-3. Story and Script Policy](#story-3-story-and-script-policy) | PARTIALLY IMPLEMENTED |

---

# Story-1. Starting City and Home

**Status: IMPLEMENTED**

During the opening cutscene with Mom, the player chooses one of **18 starting cities** across Johto and Kanto. The chosen city determines where the player lives and is the starting point for [wild Pokémon level caps](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps).

## How the home doors work

Each eligible city has a designated home building. Its front door leads to Mom’s house if the player chooses that city, and Mom’s front door leads back outside to the same spot. The player first uses this exit when leaving the house after the opening cutscene.

- **Starting in New Bark Town.** Mom’s house keeps its original front door in New Bark Town.
- **Starting anywhere else.** The chosen city’s designated building becomes the entrance to Mom’s house. The interior that originally belonged to that building is now accessible through the original New Bark player-house door. Leaving that interior puts the player back outside the New Bark door.

The designated buildings in all other cities keep their original entrances and interiors.

---

# Story-2. Starter Pokémon and Intro Flow

**Status: IMPLEMENTED**

During the same Mom cutscene as [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home), **three** type menus (grass / fire / water) with **four** species each — player receives **one Pokémon per type** (**3** total). Not the vanilla three-ball bedroom picker.

Long-term options (any non-legendary, curated pools, location-specific starters) remain in [Future-*](DESIGN-FUTURE.md).

## Intro flow

After Professor Oak / name / gender, the player still wakes in the **bedroom** (vanilla map), walks downstairs, and Mom’s cutscene runs:

1. **City picker** — [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home).
2. **Starter pick** — grass, then fire, then water menus (4 options each).
3. **Mom grants** — bag, Pass, Pokédex, shoes, etc.
4. **Exit** — walk out the front door to the chosen city ([Story-1 § How the home doors work](DESIGN-STORY.md#how-the-home-doors-work)).

---

# Story-3. Story and Script Policy

**Status: PARTIALLY IMPLEMENTED**

Vanilla HeartGold and SoulSilver cast the player as the **sole protagonist** of a fixed script: the world waits on Elm’s errand, a named rival, Team Rocket set pieces, and badge order implied by roadblocks and fetch quests. [Index-2 — Game Identity](DESIGN.md#index-2-game-identity) reframes the romhack as a **trainer’s road trip** — you are **one of many travelers**, not the center of a plot the whole region revolves around. That only works if the map and NPCs stop assuming **New Bark → linear opening → prescribed Gym route**.

So we **remove or rewrite** a large share of vanilla story scripting: not to tell a different novel, but to **get out of the player’s way** — any [starting city](DESIGN-STORY.md#story-1-starting-city-and-home), **any-order Gyms**, travel and services without errand gates, and League progression when *you* are ready. What we strip is listed under the **remove** headings below; what we keep is under [What stays](#what-stays). Open implementation and cleanup rows live in **TODO.md** (document map).

Open-world intro replaces the vanilla opening: [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home), [Story-2](DESIGN-STORY.md#story-2-starter-pokémon-and-intro-flow). Prefer disabling a script branch or removing an object over deleting assets.

## What stays

**League arc (reordered, not removed):** collect **16 badges** from Johto and Kanto Gyms in **any order** ([Battle-3](DESIGN-BATTLES.md#battle-3-gyms)), then **Elite Four and Champion** behind the usual endgame gates ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)). No linear rival or fetch chain is required to reach Gyms or the League.

**Postgame legendaries:** vanilla **post–Champion legendary** encounters and quests (e.g. box legends, roaming beasts, Mt. Silver) stay **as HGSS designed them** unless we explicitly decide otherwise — we are not stripping endgame legendaries/mythicals for open-world travel.

**Dex and species scope:** **Completing the Pokédex** remains a **primary goal**. Release scope is **every Gen I–IV species obtainable**, plus evolutions of those that were added in later-generation, as well as the Volcarona line ([Wilds-5](DESIGN-WILDS.md#wilds-5-pokémon-generations--content-scope)); **additional legendary** stories may be added to fill that goal. Broader generations stay [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes).

## Route Cut on travel routes — remove

Players should reach cities and dungeons without **story-gated Cut** on main through-routes when HMs come from Gym Leaders ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)). Gym-adjacent Cut trees (Surge, Erika) and selected travel paths (Ilex Forest main path, Route 35) follow the same policy. Optional side areas may still use Cut until audited.

## Team Rocket — remove

Rocket grunts, hideouts, Radio Tower arc, and related roadblocks must not gate travel, Gyms, or items. Mahogany post-clear on load is the reference pattern; extend to Goldenrod basement, Radio Tower, and remaining grunts until release-complete.

## Silver — flexible encounter order

Newbarktown storyline and rocket encounters are removed. But all other encounter locations remain, and additional ones are to be added in Kanto. Encounters can be done in any order and dialogue is reworked to handle that.

## Gyms — access and story policy

**Rules (all Leaders):**

1. **City-local events only** — pre/post-battle flavour OK if it stays in the Gym town; cut anything that sends the player elsewhere and expects a return.
2. **No story-gated Gym approach** — no Cut/Surf/Strength/Whirlpool (or Rocket/badge-count) blocking the Gym door or Leader; HMs are granted by Gym Leaders per badge order ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Battle-3](DESIGN-BATTLES.md#first-defeat-rewards)). HM/Flash/dungeon gating ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)) and endgame badge guards ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)) still apply outside Gyms. Wild **levels** use [Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), not badge guard tiles.
3. **Internal Gym puzzles** — trash cans, maze, etc. stay unless they hard-require an HM.


---
