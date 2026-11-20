# Pokémon Wandering Heart — World & Travel

> Transportation, route gating, HMs, field moves, living trainers, services, and accelerated time.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)` · **Story:** `[DESIGN-STORY.md](DESIGN-STORY.md)`

## Sections

| Section | Status |
| ------- | ------ |
| [World-0. Open-World Principles](#world-0-open-world-principles) | DECIDED |
| [World-1. World Transportation](#world-1-world-transportation) | PARTIALLY IMPLEMENTED |
| [World-2. Routes and Content Gating](#world-2-routes-and-content-gating) | PARTIALLY IMPLEMENTED (PoC) |
| [World-3. HMs and Field Moves](#world-3-hms-and-field-moves) | IMPLEMENTED |
| [World-4. Accelerated day/night cycle](#world-4-accelerated-daynight-cycle) | PARTIALLY IMPLEMENTED |
| [World-5. Shared Pokémon Center Hub](#world-5-shared-pokémon-center-hub) | PARTIALLY IMPLEMENTED |
| Living trainers & interactions | Moved — [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) |

---

# World-0. Open-World Principles

**Status: DECIDED**

> **Travel is open. Content can still be dangerous or gated.**

The player should generally be able to **travel between cities regardless of badge count** — trains, ships, and local paid bypasses instead of story errands blocking the map ([World-1](DESIGN-WORLD.md#world-1-world-transportation), [Story-3](DESIGN-STORY.md#story-3-story-and-script-policy)).

That does **not** mean that every route, dungeon, grass patch, encounter, or optional area must be immediately appropriate for a new trainer. Dungeons stay behind **HM and badge-order field unlocks** ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)); a handful of **badge guards** protect endgame corridors such as the League approach ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)). Where geography would force everyone through a high-tier gauntlet, **paid ferries and lifts** offer a way around without closing the region entirely.

Because the player may **start in any of eighteen cities** ([Story-1](DESIGN-STORY.md#story-1-starting-city-and-home)), the world must not behave as if every chosen hometown were late-game: wild levels scale with **distance from that start**, not with badges on the grass ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), [Wilds-2](DESIGN-WILDS.md#wilds-2-wild-pokémon-level-range)), and HM-gated areas can enforce **minimum** caps so a nearby start city does not under-level Whirlpool or Waterfall content. Trainer battles scale with **badges earned**, not with map position ([Battle-2](DESIGN-BATTLES.md#battle-2-badge-level-caps)), while the player’s own level cap keeps early parties from outleveling the curve. All **sixteen Gyms** remain viable in **any order**; only Victory Road / League and postgame peaks expect the full badge set ([Battle-3](DESIGN-BATTLES.md#battle-3-gyms)).

Progression favors **exploration and a large roster**, not route attrition: fights are tuned as **single encounters** with recovery afterward ([Battle-1](DESIGN-BATTLES.md#recovery)), trainer battles aim for **symmetry** with the player ([Battle-1](DESIGN-BATTLES.md#items)), and renewable **TMs, stones, and evolution items** in shops reduce one-shot scavenger hunts ([Items-2](DESIGN-ITEMS.md#items-2-tms), [Items-3](DESIGN-ITEMS.md#items-3-evolution-methods-trade--stones), [Items-4](DESIGN-ITEMS.md#items-4-shops)). Fishing rod tiers and a separate **Water-type catch** track add optional progression off the badge ladder ([Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression)).

---

# World-1. World Transportation

**Status: IMPLEMENTED**

Most traditional story roadblocks should be removed ([Story-3](DESIGN-STORY.md#story-3-story-and-script-policy)).

Transportation systems should allow broad world traversal from early in the game.

These include:

- Goldenrod/Saffron Train
- Olivine/Vermilion **S.S. Aqua**
- local paid route/cave bypasses
- Pokémon Center Abra transportation before Fly HM unlock

## Paid ferry NPCs

**Route 42** Ecruteak ↔ Mahogany water skip.

**Route 40 (Olivine) ↔ Cianwood** — Route 40 Surf gate removed.

**Route 31 ↔ Route 45 (Dark Cave)**

**Route 46 → Route 45 (mountain lift)**

**Blackthorn ↔ Route 44 (Ice Path bypass)**

**Pallet Town, Cinnabar Island, Seafoam Islands, and Fuchsia** with a 3-destination menu to any of the other stops.

## SS Aqua (Olivine ↔ Vermilion)

Mom grants S.S. Ticket; pier ticket sailors allow boarding **every day of the week**; crossing completes with the vanilla missing-girl arc being optional.

## Abra fast travel

Pokémon Centers may contain an Abra transportation service ([World-5](#world-5-shared-pokémon-center-hub) — shared hub desk).

---

# World-2. Routes and Content Gating

**Status: PARTIALLY IMPLEMENTED (PoC)** — badge guards for **endgame** access only; not used for wild levels or city-to-city travel.

Before [Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), the plan was to gate large parts of the map with badge checks, HMs, guards, and ferries so every city stayed reachable while wild areas stayed “appropriate” for progression. **That model is retired.** Cities stay open via [World-1](DESIGN-WORLD.md#world-1-world-transportation) (ferries, trains, Aqua, etc.); wild difficulty is distance-based ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps)), not badge-guarded grass. HM milestone locks for dungeons and routes remain in [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves).

**Badge-guard PoC (in ROM today):** **Route 29 → Route 46** gatehouse — requires **2 badges**. This guard needs to be removed before final release but is our working template for badge-gated content.

**Planned badge gates (same pattern as the PoC):**

- **Route 26** — guard until **13 badges earned** (same count as **Waterfall** field unlock — [World-3](#badge--field-abilities-single-reference)); Kanto-Johto corridor becomes Waterfall gated on both ends.
- **Route 23** and **Victory Road** / Pokémon League — block until badge requirement for the League is met.
- **Route 28** and **Mt. Silver** — block until postgame badge requirement is met.

---

# World-3. HMs and Field Moves

**Status: IMPLEMENTED**

Field abilities unlock by **badges earned** (any Gym order): when badge count hits a row below, the defeating Gym Leader grants that unlock with badge + TM ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards)). Vanilla HM fetch quests and tutors are removed ([Story-3](DESIGN-STORY.md#story-3-story-and-script-policy)).


## Badge → field abilities

| Badges | Unlock | Notes |
| ------ | ------ | ----- |
| 1 | **Flash** | Dark Cave and Rock Tunnel: a message at the entrance until this unlock. Sold as a TM in the general shop. |
| 2 | **Cut** (HM01) |  |
| 3 | **Rock Smash** (HM06) |  |
| 4 | **Headbutt** | Sold as a TM in the general shop. |
| 5 | **Fly** (HM02) |  |
| 6 | **Surf** (HM03) |  |
| 7 | **Strength** (HM04) |  |
| 10 | **Whirlpool** (HM05) |  |
| 13 | **Waterfall** (HM07) | Route 26 and Route 27 stay blocked until this unlock. |
| 16 | **Rock Climb** (HM08) |  |

Badge counts not in the table get Badge + TM only

**Unchanged vanilla** (learn move, party menu — not badge-gated): Sweet Scent, Dig, Teleport.

## Flash and Headbutt

TM05 has been changed from Roar to Headbutt. Badge **1** puts Flash in the general shop. Badge **4** puts Headbutt there. The Leader who crosses that count mentions the shop instead of handing over an HM.

---

# World-4. Accelerated day/night cycle

**Status: PARTIALLY IMPLEMENTED** 

HGSS's real-world clock is replaced by an accelerated in-game clock. 30 real minutes = one in-game day.

Applies to:
- Overworld tint, Pokégear clock, ecology land period, evolutions. 
Does not apply to: 
- Bug Catching Contest timer, Calendar date, Daily rollovers

**Pokémon Center rest:** Nurse Joy can advance the time of day for the current session ([World-5](#world-5-shared-pokémon-center-hub)). Restarting the game restores the real-clock-based schedule; the calendar date stays unchanged.

**Still open:** portable camping in [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes); virtual calendar for [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) tree refresh; RTC penalty when the player sets the clock backward.

---

# World-5. Shared Pokémon Center Hub

**Status: PARTIALLY IMPLEMENTED**

## Design Goal

Pokémon Centers are **optional convenience hubs**, not required stops for healing or storage: battles already restore the party afterward ([Battle-1](DESIGN-BATTLES.md#recovery)), and [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) will provide PC access from the menu. Players can use the same services from any Center, avoiding unnecessary trips to specific NPCs across Johto and Kanto.

## Services

| Service | Description | Status |
| ------- | ----------- | ------ |
| **Abra fast travel** | Pay $400 to choose a visited destination on the travel map, then Teleport to its usual Fly landing spot. | Implemented |
| **Move Relearner** | Relearn moves for $300 per successfully learned move. | Implemented |
| **Rest / pass time** | Nurse Joy offers free rest until morning (4:00 AM), daytime (10:00 AM), or night (8:00 PM), replacing her healing interaction. The time shift lasts for the current session and resets on a fresh game start; the calendar date stays unchanged. | Implemented |
| **Apricorn crafting** | Instantly exchange eligible Apricorns in the Bag for specialty balls, one per Apricorn, for $100 per ten Apricorns rounded up. The eight recipes follow [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance). | Implemented |
| **Move Tutor** | Make special move tutoring available from any Center. | Maybe |
| **Specialty Trader** | Exchange items or currencies for selected rewards. Inventory and pricing TBD. | Maybe |
| **Researchers** | Register Arceus Plates and claim plate and Pokédex rewards ([Future-11](DESIGN-FUTURE.md#future-11-pokémon-research-society)). | Planned |

Other services may be added as future systems develop. Keep location-specific shops and rewards in the world when they provide a meaningful reason to explore.

## Shared Interior

Outdoor Pokémon Center entrances lead to a shared interior, tracking the originating Center so the exit returns to the correct outdoor door. The return destination persists when the player saves and restarts inside the Center. Indigo Plateau remains separate, preserving its unique layout and League access.

Individual Centers’ NPCs do not carry over into the shared interior. The actual Pokemon Center used is the Route 32 one, and all vanilla npcs have been removed.
