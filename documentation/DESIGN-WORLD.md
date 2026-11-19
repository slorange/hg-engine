# Pokémon Wandering Heart — World & Travel

> Transportation, route gating, HMs, field moves, living trainers, shops, services, and accelerated time.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)` · **Story:** `[DESIGN-STORY.md](DESIGN-STORY.md)`

## Sections

| Section | Status |
| ------- | ------ |
| [World-0. Open-World Principles](#world-0-open-world-principles) | DECIDED |
| [World-1. World Transportation](#world-1-world-transportation) | PARTIALLY IMPLEMENTED |
| [World-2. Routes and Content Gating](#world-2-routes-and-content-gating) | PARTIALLY IMPLEMENTED (PoC) |
| [World-3. HMs and Field Moves](#world-3-hms-and-field-moves) | IMPLEMENTED |
| [World-4. TMs](#world-4-tms) | PARTIALLY IMPLEMENTED |
| [World-5. Evolution Methods (Trade & Stones)](#world-5-evolution-methods-trade--stones) | IMPLEMENTED |
| [World-6. Shops](#world-6-shops) | IMPLEMENTED |
| [World-7. Berry economy](#world-7-berry-economy) | IMPLEMENTED |
| [World-8. Item acquisition channels](#world-8-item-acquisition-channels) | PARTIALLY IMPLEMENTED |
| [World-9. Accelerated day/night cycle](#world-9-accelerated-daynight-cycle) | PARTIALLY IMPLEMENTED |
| [World-10. Shared Pokémon Center Hub](#world-10-shared-pokémon-center-hub) | PARTIALLY IMPLEMENTED |
| Living trainers & interactions | Moved — [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) |

---

# World-0. Open-World Principles

**Status: DECIDED**

> **Travel is open. Content can still be dangerous or gated.**

The player should generally be able to **travel between cities regardless of badge count** — trains, ships, and local paid bypasses instead of story errands blocking the map ([World-1](DESIGN-WORLD.md#world-1-world-transportation), [Story-3](DESIGN-STORY.md#story-3-story-and-script-policy)).

That does **not** mean that every route, dungeon, grass patch, encounter, or optional area must be immediately appropriate for a new trainer. Dungeons stay behind **HM and badge-order field unlocks** ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)); a handful of **badge guards** protect endgame corridors such as the League approach ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)). Where geography would force everyone through a high-tier gauntlet, **paid ferries and lifts** offer a way around without closing the region entirely.

Because the player may **start in any of eighteen cities** ([Story-1](DESIGN-STORY.md#story-1-starting-city-and-home)), the world must not behave as if every chosen hometown were late-game: wild levels scale with **distance from that start**, not with badges on the grass ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), [Wilds-2](DESIGN-WILDS.md#wilds-2-wild-pokémon-level-range)), and HM-gated areas can enforce **minimum** caps so a nearby start city does not under-level Whirlpool or Waterfall content. Trainer battles scale with **badges earned**, not with map position ([Battle-2](DESIGN-BATTLES.md#battle-2-badge-level-caps)), while the player’s own level cap keeps early parties from outleveling the curve. All **sixteen Gyms** remain viable in **any order**; only Victory Road / League and postgame peaks expect the full badge set ([Battle-3](DESIGN-BATTLES.md#battle-3-gyms)).

Progression favors **exploration and a large roster**, not route attrition: fights are tuned as **single encounters** with recovery afterward ([Battle-1](DESIGN-BATTLES.md#recovery)), trainer battles aim for **symmetry** with the player ([Battle-1](DESIGN-BATTLES.md#items)), and renewable **TMs, stones, and evolution items** in shops reduce one-shot scavenger hunts ([World-4](DESIGN-WORLD.md#world-4-tms), [World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones), [World-6](DESIGN-WORLD.md#world-6-shops)). Fishing rod tiers and a separate **Water-type catch** track add optional progression off the badge ladder ([Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression)).

---

# World-1. World Transportation

**Status: PARTIALLY IMPLEMENTED**

Most traditional story roadblocks should be removed ([Story-3](DESIGN-STORY.md#story-3-story-and-script-policy)).

Transportation systems should allow broad world traversal from early in the game.

These include:

- Goldenrod/Saffron Train
- Olivine/Vermilion **S.S. Aqua**
- local paid route/cave bypasses
- Pokémon Center Abra transportation before Fly HM unlock

## Paid ferry NPCs

**Status: IMPLEMENTED** 

**Route 42** Ecruteak ↔ Mahogany water skip.

**Route 40 (Olivine) ↔ Cianwood** — Route 40 Surf gate removed.

**Route 31 ↔ Route 45 (Dark Cave)**

**Route 46 → Route 45 (mountain lift)**

**Blackthorn ↔ Route 44 (Ice Path bypass)**

**Pallet Town, Cinnabar Island, Seafoam Islands, and Fuchsia** with a 3-destination menu to any of the other stops.

## SS Aqua (Olivine ↔ Vermilion)

**Status: IMPLEMENTED** — Mom grants S.S. Ticket; pier ticket sailors allow boarding **every day of the week**; crossing completes without being forced through the vanilla missing-girl arc.

**Known v1 gap:** optional vanilla side dialogue (e.g. engine-room sailor / missing girl) is still available if the player seeks it out; **leaving the ship does not require completing the fetch quest.**

## Abra fast travel

**Status: NOT IMPLEMENTED** 

Pokémon Centers may contain an Abra transportation service ([World-10](DESIGN-WORLD.md#world-10-shared-pokémon-center-hub) — shared hub desk).

Travel likely costs money.

Only to cities that have already been visited.

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



# World-4. TMs

**Status: PARTIALLY IMPLEMENTED**

TMs remain **consumable**. However **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops — see [Data-5. Department stores](DESIGN-DATA.md#goldenrod--celadon-department-stores).

## Game Corner TMs

Coin prizes at the department-store Game Corners

See [Data-1. Game Corner prize pools](DESIGN-DATA.md#data-1-game-corner-prize-pools).

### Coin income (not implemented)

**Temporary pricing:** all Game Corner TM, held-item, and Pokémon prizes cost **50 Coins** until proper coin income and tiered pricing ship. This is a playtest shortcut only — not the long-term economy.

Prize menus are wired; **earning Coins is still vanilla** (**Voltorb Flip** on the Game Corner floor). Game Corner TMs are buyable in principle but **Coin income is the bottleneck** until something from [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes) ships.

## Gym TMs

Each Gym Leader has a **curated TM pool**. Every TM has its own **minimum badge count**. See [Data-2. Gym Leader TM pools](DESIGN-DATA.md#data-2-gym-leader-tm-pools).

After the player **defeats** that Leader (first clear or **rematch**), they **choose one TM** from that Leader's pool among entries whose badge requirement is **≤ badges earned** (including the badge just awarded). Same choice rules on rematch — renewable TM source ([Battle-3](DESIGN-BATTLES.md#rematches)).


---



# World-5. Evolution Methods (Trade & Stones)

**Status: IMPLEMENTED**

## Evolution stones and items

Every standard evolution stone is **renewably buyable** at themed town marts and dept-store shelves ([World-6 § What we’ve done](DESIGN-WORLD.md#what-weve-done)) — e.g. Fire at Ecruteak, Water at Cerulean — instead of vanilla’s mostly one-off pickups. Some evolution items also drop from **Rock Smash** as a field source.

Existing explicit item evolutions keep their normal requirements: use the appropriate item directly on an eligible Pokémon. The early-evolution rule below adds options for ordinary level-up evolutions.

## Early evolution with matching items

A matching item causes **immediate evolution** once the Pokémon reaches **90% of its normal level-up evolution level, rounded up, minus three levels** (minimum level 1). The item must match either type of the **resulting evolution**; a type lost on evolution does not qualify.

**Type matches:** Fire Stone → Fire; Water Stone → Water; Leaf Stone → Grass; Thunder Stone → Electric; Ice Stone → Ice; Dusk Stone → Ghost; Metal Coat → Steel. A newly acquired type qualifies, so Pineco and Prinplup can use Metal Coat, and Seel can use Ice Stone.

Only **plain level-up evolutions** qualify. Move-known, friendship, gender/stat/personality conditions, location requirements, and other special methods do not qualify for this shortcut. Pseudo legendaries are also excluded.

Below the requirement, the party menu shows **LV** followed by the required level; eligible Pokémon show **ABLE**, and incompatible Pokémon show **UNABLE**.

Examples: Fire Stone evolves Cyndaquil at **10** instead of 14, Quilava at **30** instead of 36. Metal Coat evolves Pineco at **25** instead of 31 and Prinplup at **30** instead of 36. Ice Stone evolves Snorunt into Glalie at **35** instead of 42.

Wild and opposing trainer stage selection is separate: [Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution).

## Trade evolutions

### With a held item

Evolutions that normally require **trade while holding an item** evolve when the item is **used on the Pokémon** — no trade required. Examples: Dragon Scale → Kingdra, Metal Coat → Scizor, Protector → Rhyperior.

### Without an item

**Linking Cord** — use on the Pokémon like a stone for plain trade lines.

## Evolution changes from vanilla HGSS

Additional methods and changed evolution timing are listed in [Data-4](DESIGN-DATA.md#data-4-evolution-changes).

---

# World-6. Shops

**Status: IMPLEMENTED** — renewable **TMs** ([World-4](DESIGN-WORLD.md#world-4-tms)), **evolution items**, and **held gear** without vanilla’s one-shot consumable grind.

## Overall idea

Marts follow [Battle-1](DESIGN-BATTLES.md#recovery) (full restore after every battle) and [Battle-1](DESIGN-BATTLES.md#items) (no bag items in trainer battles). **Remove** as default shop stock: potions, antidotes, X items, etc.

**Sell:**

| Category | Intent |
| -------- | ------ |
| **Poké Balls & repels** | Capture and wild-level risk ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps)); specialty balls wait on [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) — **Quick Ball** and **Dusk Ball** stay out of normal shops. |
| **TMs** | Renewable sets at **Goldenrod / Celadon** dept hubs; Gym **choice pools** and **Game Corner** lists in [World-4](DESIGN-WORLD.md#world-4-tms). |
| **Evolution items** | Stones and trade-evolution held items at **themed town marts**; **Linking Cord** at Goldenrod dept 2F lower + Celadon 4F ([World-5](DESIGN-WORLD.md#world-5-evolution-methods-trade--stones)). |
| **Held items** | **Badge-gated** progression, some on dept **2F**, **20% type boosters** in matching Gym cities |
| **Utility** | Escape Rope, Poké Doll, vitamins + EV training at hubs. |


## What we’ve done

### Badge-gated shelf (most shops)

See [Data-5 — Badge-gated shelf](DESIGN-DATA.md#badge-gated-shelf-most-shops).

### Goldenrod & Celadon department stores

See [Data-5 — Department stores](DESIGN-DATA.md#goldenrod--celadon-department-stores).

### Town / route specialty clerks

See [Data-5 — Specialty clerks](DESIGN-DATA.md#town--route-specialty-clerks).

---

# World-7. Berry economy

**Status: IMPLEMENTED**

Berries stay a meaningful **held-item** layer: the player cannot use Bag items in trainer battles ([Battle-1](DESIGN-BATTLES.md#items)), so automatic berry effects remain one of the main in-battle effects. Growth via **Berry Pots** is unchanged in role.

**Berries are restored after battle, along with all held items**

**Scope:** **45** Gen IV berries, all obtainable in-game — no Pokéwalker courses, events, Pal Park, or multiplayer.

**Removed (19):** Figy-family weak-heal berries; Poffin / contest berries — little use beyond Natural Gift.

## Berry Pots and starter supply

Mom intro grants **Berry Pots** and **5× each** basic berry **Cheri through Persim**.

## Acquisition by group

| Group | Role | Primary sources | Status |
| ----- | ---- | ----------------- | ------ |
| Basic (Cheri–Persim) | Status cure, Leppa PP, Oran HP | Starter pack; Goldenrod & Celadon dept **2F upper** (partial medicine replacement) | Implemented |
| Lum + Sitrus | Full status / 25% max HP | Badge-scaled regular marts (4 and 6 badges) | Implemented |
| EV / friendship (Pomeg–Tamato) | −EVs, +friendship | Goldenrod Underground medicine seller (beside Haircut Brothers) | Implemented |
| Type-resistance (Occa–Chilan) | Super-effective hit reduction | Themed **local specialty shops** ([World-6 § Town clerks](#town--route-specialty-clerks) — e.g. Wacan at Vermilion, Passho at Cerulean). Mom’s vanilla resist-berry purchasing **unchanged for now**. | Implemented |
| Rare battle (Liechi–Rowap) | Pinch boosts, Enigma heal, Custap priority, Jaboca / Rowap counter | **Shard traders** in **Violet City** and **Fuchsia City** | Implemented |

## Wild Pokémon holds

**Implemented:** In addition to the table above, every supported berry can be a wild Pokémon's **held-item**, and so can the eight craftable Apricorn colours. After the normal species held-item table roll (buffed to **65%** common / **15%** rare / **20%** nothing; **Compound Eyes** lead **70%** / **30%** / **0%**), wilds with no item get a **50%** chance (**100%** with Compound Eyes) of a fallback hold. That hold is **50%** a uniform random berry from the **45** supported berries and **50%** a uniform random Apricorn.

---

# World-8. Item acquisition channels

**Status: PARTIALLY IMPLEMENTED** — not every row or channel in this section is required for **initial release**; ship channels independently as scope allows.

The matrix below is the target for **where** each item category may appear. **Berries** follow [World-7](#world-7-berry-economy). **Apricorn Ball** rebalancing and tree harvest are [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance).

<table>
<colgroup>
<col style="width:14%">
<col style="width:12%">
<col style="width:11%">
<col style="width:9%">
<col style="width:9%">
<col style="width:11%">
<col style="width:11%">
<col style="width:11%">
</colgroup>
<thead>
<tr><th>Item category</th><th><a href="#world-6-shops">Shops</a></th><th>Ground / Hidden</th><th>Bug Contest</th><th>Pokéathlon</th><th>Battle Frontier</th><th>Pokédex rewards</th><th><a href="#world-4-tms">Game Corner</a></th></tr>
</thead>
<tbody>
<tr><td><strong>Treasures</strong> (sellables)</td><td>—</td><td>✓</td><td>✓</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><strong>Evolution stones / items</strong></td><td>Themed shops</td><td>✓</td><td>—</td><td>✓</td><td>—</td><td>✓</td><td>—</td></tr>
<tr><td><strong>Rare Candies</strong></td><td>Dept. Store</td><td>✓</td><td>✓</td><td>✓</td><td>—</td><td>✓</td><td>—</td></tr>
<tr><td><strong>Held items</strong></td><td>Badge-gated</td><td>✓</td><td>—</td><td>—</td><td>Only the best</td><td>—</td><td>✓</td></tr>
<tr><td><strong>TMs</strong></td><td>Dept. Store / Gym</td><td>✓</td><td>—</td><td>—</td><td>Only the best</td><td>—</td><td>✓</td></tr>
<tr><td><strong>PP Up / PP Max</strong></td><td>Dept. Store</td><td>✓</td><td>✓</td><td>✓</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><strong>Vitamins</strong></td><td>Dept. Store</td><td>✓</td><td>—</td><td>✓</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><strong>Bottle Caps</strong></td><td>—</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>—</td></tr>
<tr><td><strong>Mints</strong></td><td>—</td><td>✓</td><td>—</td><td>✓</td><td>✓</td><td>✓</td><td>—</td></tr>
<tr><td><strong>Ability Capsules / Patches</strong></td><td>—</td><td>✓</td><td>✓</td><td>—</td><td>✓</td><td>✓</td><td>—</td></tr>
<tr><td><strong>Shop and Apricorn Balls</strong></td><td>Shop balls</td><td>✓</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
<tr><td><strong>Master Balls</strong></td><td>—</td><td>—</td><td>—</td><td>—</td><td>✓</td><td>✓</td><td>—</td></tr>
<tr><td><strong>Pokémon</strong></td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>✓</td></tr>
<tr><td><strong>Apricorns</strong></td><td>—</td><td>✓</td><td>—</td><td>✓</td><td>✓</td><td>✓</td><td>—</td></tr>
</tbody>
</table>

Shops, Bug Catching Contest, Game Corner, and randomized ground and hidden items are implemented. Pokéathlon, Battle Frontier, and Pokédex rewards are planned.

Additional consideration is needed for Pickup ability.

## Ground and hidden items

Ground and hidden pickups roll a category, then a reward within that category. The category weights are **20% Treasures**, **15% Evolution items**, **10% Held items**, **10% TMs**, **10% Balls**, **15% Apricorns**, and **20% Pokémon upgrades**. Pokémon upgrades include Rare Candy, PP Up and PP Max, vitamins, Bottle Caps, Mints, Ability Capsule, and Ability Patch. Treasures are the vanilla ones, plus Heart Scale. Berries and field utility items are disabled. If enabled, the Berry pool uses the 45 berries mentioned in World-7.

Ultra Balls come in bundles of **3–5** and specialty Balls in bundles of **2–3**. Apricorns go directly into the Bag in bundles of **3–5** of one color. Each spot's reward is stable within a save and the spot is collected only after the full reward fits.

Evolution items are Fire, Thunder, Water, Leaf, Ice, and Dusk Stones, plus Metal Coat. The held-item pool contains one standard booster for each of the 18 types, including Fairy Feather. TM01 through TM92 are eligible. The Ball pool contains Ultra, Net, Repeat, Timer, Fast, Level, Heavy, Love, Friend, Dream, Quick, and Dusk Balls.

## Bug-Catching Contest, Pokéathlon, and Battle Frontier

Curated prize lists aligned with the matrix (not the ground/hidden random pool, not vanilla HGSS menus). Postgame menus can be **renewable but effort-gated** where balance calls for infinite access without shop trivialization.

**Bug-Catching Contest:**
- **First:** Ability Patch, Gold Bottle Cap, or Ability Capsule.
- **Second:** Star Piece, Bottle Cap, or PP Max.
- **Third:** Nugget, Big Pearl, Rare Candy, or PP Up.
- **Consolation** — Grip Claw, Sticky Barb, or Shed Shell.

**Pokéathlon:** Exchange or prize menus stock items from the rows/columns where they are marked ✓.

**Battle Frontier:** Offer **every rare item that shops do not sell**, so endgame players can still obtain the full rare-item set with work. **Held items** and **TMs** on the Frontier still emphasize top-tier options where the matrix notes **only the best**.

## Pokédex milestone rewards

**Pokédex completion thresholds** grant rare items. Milestones are **curated** (specific rewards at specific counts), not random rolls from the ground/hidden pool. Exact items, amounts, and thresholds TBD. The research society in Pokémon Centers may be where these are claimed ([Future-11](DESIGN-FUTURE.md#future-11-pokémon-research-society)).

## Mints, Bottle Caps, Ability Capsules and Patches

**Status: PARTIALLY IMPLEMENTED** — Mints, Ability Capsules, and Ability Patches can appear in ground and hidden pickups. Bottle Caps can also appear there and are currently sellable items without a training effect. Effort-gated renewable postgame sources follow the matrix above.

**Mints.** Using one stores that nature and consumes the Mint. The summary screen shows the new nature. Stat calculation still uses the personality nature, so battles do too.

**Ability Capsule.** Swaps the two regular abilities when the species has two different ones. A Hidden Ability blocks it. Consumed on use.

**Ability Patch.** Switches between the regular ability and the Hidden Ability when the species has one. Consumed on use.

**Bottle Caps.** Silver and Gold Caps cannot be used. Hyper Training is not implemented.

**Hidden Power** type is set by using an Arceus Plate on the Pokémon. The plate stays in the bag ([Future-11](DESIGN-FUTURE.md#hidden-power)). Until then, the type stays IV-dependent. The Unown collection scales Hidden Power’s power ([Future-12](DESIGN-FUTURE.md#future-12-unown-collection-quest)).

---

# World-9. Accelerated day/night cycle

**Status: PARTIALLY IMPLEMENTED** 

HGSS's real-world clock is replaced by an accelerated in-game clock. 30 real minutes = one in-game day.

Applies to:
- Overworld tint, Pokégear clock, ecology land period, evolutions. 
Does not apply to: 
- Bug Catching Contest timer, Calendar date, Daily rollovers

**Pokémon Center rest:** Nurse Joy can advance the time of day for the current session ([World-10](DESIGN-WORLD.md#world-10-shared-pokémon-center-hub)). Restarting the game restores the real-clock-based schedule; the calendar date stays unchanged.

**Still open:** portable camping in [Future-9](DESIGN-FUTURE.md#future-9-time-advancement); virtual calendar for [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) tree refresh; RTC penalty when the player sets the clock backward.

---

# World-10. Shared Pokémon Center Hub

**Status: PARTIALLY IMPLEMENTED**

## Design Goal

Pokémon Centers are **optional convenience hubs**, not required stops for healing or storage: battles already restore the party afterward ([Battle-1](DESIGN-BATTLES.md#recovery)), and [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) will provide PC access from the menu. Players can use the same services from any Center, avoiding unnecessary trips to specific NPCs across Johto and Kanto.

## Services

| Service | Description | Status |
| ------- | ----------- | ------ |
| **Abra fast travel** | Pay $400 to choose a visited destination on the travel map, then Teleport to its usual Fly landing spot. | Implemented |
| **Move Relearner** | Relearn moves for $300 per successfully learned move. | Implemented |
| **Rest / pass time** | Nurse Joy offers free rest until morning (4:00 AM), daytime (10:00 AM), or night (8:00 PM), replacing her healing interaction. The time shift lasts for the current session and resets on a fresh game start; the calendar date stays unchanged. | Implemented |
| **Apricorn crafting** | Instantly exchange eligible Apricorns in the Bag for specialty balls, one per Apricorn, for $100 per ten Apricorns rounded up. The eight recipes follow [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance). | Implemented |
| **Move Tutor** | Make special move tutoring available from any Center. | Maybe |
| **Specialty Trader** | Exchange items or currencies for selected rewards. Inventory and pricing TBD. | Maybe |
| **Researchers** | Register Arceus Plates and claim plate and Pokédex rewards ([Future-11](DESIGN-FUTURE.md#future-11-pokémon-research-society)). | Planned |

Other services may be added as future systems develop. Keep location-specific shops and rewards in the world when they provide a meaningful reason to explore.

## Shared Interior

Outdoor Pokémon Center entrances lead to a shared interior, tracking the originating Center so the exit returns to the correct outdoor door. The return destination persists when the player saves and restarts inside the Center. Indigo Plateau remains separate, preserving its unique layout and League access.

Individual Centers’ NPCs do not carry over into the shared interior. The actual Pokemon Center used is the Route 32 one, and all vanilla npcs have been removed.

---
