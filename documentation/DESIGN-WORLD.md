# Pokémon Wandering Heart — World & Travel

> Transportation, route gating, HMs, field moves, living trainers, services, and accelerated time.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)` · **Story:** `[DESIGN-STORY.md](DESIGN-STORY.md)`

## Sections

| Section | Status |
| ------- | ------ |
| [World-0. Open-World Principles](#world-0-open-world-principles) | DECIDED |
| [World-1. World Transportation](#world-1-world-transportation) | IMPLEMENTED |
| [World-2. Routes and Content Gating](#world-2-routes-and-content-gating) | PARTIALLY IMPLEMENTED (PoC) |
| [World-3. HMs and Field Moves](#world-3-hms-and-field-moves) | IMPLEMENTED |
| [World-4. Accelerated day/night cycle](#world-4-accelerated-daynight-cycle) | IMPLEMENTED |
| [World-5. Shared Pokémon Center Hub](#world-5-shared-pokémon-center-hub) | IMPLEMENTED |
| [World-6. Unown collection quest](#world-6-unown-collection-quest) | IMPLEMENTED |
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

**Status: PARTIALLY IMPLEMENTED (PoC)**

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

**Status: IMPLEMENTED** 

HGSS's real-world clock is replaced by an accelerated in-game clock. 30 real minutes = one in-game day.

Applies to:
- Overworld tint, Pokégear clock, ecology land period, evolutions. 
Does not apply to: 
- Bug Catching Contest timer, Calendar date, Daily rollovers

**Pokémon Center rest:** Nurse Joy can advance the time of day for the current session ([World-5](#world-5-shared-pokémon-center-hub)). Restarting the game restores the real-clock-based schedule; the calendar date stays unchanged.

---

# World-5. Shared Pokémon Center Hub

**Status: IMPLEMENTED**

## Design Goal

Pokémon Centers are **optional convenience hubs**, not required stops for healing or storage: battles already restore the party afterward ([Battle-1](DESIGN-BATTLES.md#recovery)), and [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) will provide PC access from the menu. Players can use the same services from any Center, avoiding unnecessary trips to specific NPCs across Johto and Kanto.

## Services

| Service | Description | Status |
| ------- | ----------- | ------ |
| **Abra fast travel** | Pay $400 to choose a visited destination on the travel map, then Teleport to its usual Fly landing spot. | Implemented |
| **Move Relearner** | Relearn moves for $300 per successfully learned move. | Implemented |
| **Rest / pass time** | Nurse Joy offers free rest until morning (4:00 AM), daytime (10:00 AM), or night (8:00 PM), replacing her healing interaction. The time shift lasts for the current session and resets on a fresh game start; the calendar date stays unchanged. | Implemented |
| **Apricorn crafting** | Instantly exchange eligible Apricorns in the Bag for specialty balls, one per Apricorn, for $100 per ten Apricorns rounded up. The eight recipes follow [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance). | Implemented |

[Future-11](DESIGN-FUTURE.md#future-11-pokémon-research-society) plans to add researchers to the shared hub so players can register Arceus Plates and claim plate and Pokédex rewards.

Other services may be added as future systems develop. Keep location-specific shops and rewards in the world when they provide a meaningful reason to explore.

## Shared Interior

Outdoor Pokémon Center entrances lead to a shared interior, tracking the originating Center so the exit returns to the correct outdoor door. The return destination persists when the player saves and restarts inside the Center. Indigo Plateau remains separate, preserving its unique layout and League access.

Individual Centers’ NPCs do not carry over into the shared interior. The actual Pokemon Center used is the Route 32 one, and all vanilla npcs have been removed.

---

# World-6. Unown collection quest

Collect all **28 Unown forms** across Johto and Kanto on a fresh run. Each **unique form caught** and registered in the Pokédex **permanently** improves **all Unown** and increases **Hidden Power's base power for every Pokémon**. Wild encounters provide all 28 forms.

## Progression

Unown's base stats and Hidden Power's base power scale linearly from 0 unique forms caught to 28.

| Track | At 0 forms | At 28 forms |
| ----- | ---------- | ----------- |
| **BST** (HP / Atk / Def / Sp. Atk / Sp. Def / Speed) | 66 / 44 / 44 / 66 / 44 / 44 (**308** total) | 150 / 100 / 100 / 150 / 100 / 100 (**700** total) |
| **Hidden Power (all Pokémon)** | **60** BP (not IV-dependent) | **100** BP |

Unown's base catch rate falls geometrically from **255** on the first new form to **3** on the 28th. With `n` unique forms already caught, the base catch rate is `round(255 × (3 / 255)^(min(n, 27) / 27))`. Each new form divides the unrounded rate by about **1.18**. Integer rounding can give adjacent stages the same rate. Duplicate catches leave the rate unchanged, and the rate stays at **3** after completion.

- **Hidden Power type** stays **IV-dependent** until the player sets it with an Arceus Plate ([Future-11](DESIGN-FUTURE.md#hidden-power)). The plate is not consumed.
- **Typelessness (Unown only):** Unown has no type weaknesses, resistances, immunities, or STAB, even when its ability is suppressed.
- **Ability (Unown only):** **Runic Power** multiplies ordinary move damage by **1.33×**. Ability suppression disables the damage bonus. Fixed-damage moves keep their stated damage.
- **EV yield:** **1 HP** and **1 Sp. Atk**.
- **Wild held item:** Wild Unown have a **50%** chance to hold **TM10 (Hidden Power)**. TM10 can also appear among randomized field pickups.

## Moveset

| Level | Moves |
| ----- | ----- |
| 1 | Ancient Power, Ominous Wind, Silver Wind, Hidden Power |
| 15 | Teleport |
| 30 | Safeguard |
| 45 | Recover |
| 60 | Perish Song |

The level up set is meant to make it harder to catch Unown as the level increases. Unown cannot learn any TMs. 

## Encounter locations

Each location’s **theme word** lists the **unique letter forms** that can appear there. Letters may overlap between locations.

| Location | Theme / available forms |
| -------- | ------------------------ |
| Ruins of Alph | RUINS + ALPH + UNOWN |
| Dark Cave | DARK |
| Union Cave | UNION |
| Slowpoke Well | SLOW |
| Ilex Forest | ILEX |
| Sprout Tower | GROW |
| Burned Tower | FIRE |
| Bell Tower | BELL |
| Mt. Mortar | MORTAR |
| Lake of Rage | RAGE |
| Ice Path | ICE |
| Dragon's Den | DRAGON |
| Whirl Islands | WHIRL |
| Mt. Moon | MOON |
| Rock Tunnel | ROCK |
| Diglett's Cave | DIG |
| Seafoam Islands | FROST |
| Victory Road | VICTORY |
| Tohjo Falls | TOHJO |
| Cinnabar Island | MAGMA |

### Endgame and exclusive forms

- **!** and **?** are the **Johto** and **Kanto** roamers, respectively. Both start roaming when all four picture puzzles in the Ruins of Alph are solved. They are level 45 and the normal catch level cap applies. They use standard roamer fleeing and retain HP and status across encounters. A knocked-out roamer returns at full health after the player's next Pokémon League clear, including a repeat clear. A caught roamer stays caught. Each roamer changes routes when the player travels between maps.
- **Q** is exclusive to **Mt. Silver** and **Z** to **Cerulean Cave**.
- **V** and **Y** — **Victory Road only** ([World-2](#world-2-routes-and-content-gating) **16-badge** gate).

### Wild encounter rules

- At each designated location, **5%** of eligible wild encounters are **Unown** instead of the normal slot species. An **Unown in the lead slot** raises that chance to **50%**.
- When Unown is selected, pick **uniformly** among that location’s allowed forms; otherwise use normal encounter tables.
- Applies to **grass**, **cave**, **Surf**, **Rock Smash**, and **Headbutt**. Does **not** apply to **Fishing**.
- The encounter rooms inside the **Ruins of Alph** have a **100% Unown** rate with the letters RUINS + ALPH + UNOWN. The outside area uses the usual 5% or 50% rate with the same letters.

### Other notes

- **Caught indicator:** Show the wild **Poké Ball icon** for Unown **only when that exact form** was caught before — not when any Unown was caught.
- **Repeat Ball:** Its catch bonus applies to Unown only if the player has already caught that exact form.
- **Completion reward** — After all **28 forms** are registered, the research society gives out **unlimited copies of TM10 (Hidden Power)** on request.
- The research society may also give a reward for each newly registered Unown form ([Future-11](DESIGN-FUTURE.md#pokédex-research)).
