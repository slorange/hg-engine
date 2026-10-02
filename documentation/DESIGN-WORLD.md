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
| [World-3. HMs and Field Moves](#world-3-hms-and-field-moves) | PARTIALLY IMPLEMENTED |
| [World-4. TMs](#world-4-tms) | DECIDED — **core release target** (renewable shop TMs) |
| [World-5. Evolution Methods (Trade & Stones)](#world-5-evolution-methods-trade--stones) | DECIDED |
| [World-6. Shops](#world-6-shops) | DECIDED — **core release target** (TMs, evolution items) |
| [World-7. Berry economy](#world-7-berry-economy) | PARTIALLY IMPLEMENTED |
| Accelerated day/night cycle | Moved — [Future-9](DESIGN-FUTURE.md#future-9-accelerated-daynight-cycle) |
| Living trainers & interactions | Moved — [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) |
| Expanded stone mechanics | Moved — [Future-13](DESIGN-FUTURE.md#future-13-expanded-stone-mechanics) |
| Pokémon Center hub services | Moved — [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes) |

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

**Route 42** Blackthorn ↔ Mahogany water gaps.

**Route 40 ↔ Cianwood** — fishermen on the Olivine-side Route 40 beach and Cianwood east shore; **$200** paid warp each way; static Lapras companion sprites; Route 40 Surf gate removed.

**Route 31 ↔ Route 45 (Dark Cave)** — hikers + static Quagsire companions outside both cave entrances; **$200** paid warp each way.

**Route 46 → Route 45 (mountain lift)** — hiker + static Rhydon at the south end of Route 46; **$200** one-way paid warp to north Route 45 near Blackthorn.

**Blackthorn ↔ Route 44 (Ice Path bypass)** — hikers + static Piloswine companions on Blackthorn outdoors and Route 44 bridge area; **$200** paid warp each way (no Ice Path map edits).

**Kanto coastal mesh** — fishermen at Pallet Town south shore, Cinnabar Island beach, Route 20 (Seafoam cave mouth), and Route 19 (south of Fuchsia); **$200** with a **3-destination menu** to any of the other stops (Pallet Town / Cinnabar Island / Seafoam Island / Fuchsia City).

## SS Aqua (Olivine ↔ Vermilion)

**Status: IMPLEMENTED** — Mom grants S.S. Ticket; pier ticket sailors allow boarding **every day of the week**; crossing completes without being forced through the vanilla missing-girl arc.

**Known v1 gap:** optional vanilla side dialogue (e.g. engine-room sailor / missing girl) is still available if the player seeks it out; **leaving the ship does not require completing the fetch quest.**

## Abra fast travel

**Status: NOT IMPLEMENTED** 

Pokémon Centers may contain an Abra transportation service.

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

**Status: PARTIALLY IMPLEMENTED** — unlock order below decided; Johto Gym HM pilot partial; full Leader grant flow not complete.

Field abilities unlock by **badges earned** (any Gym order): when badge count hits a row below, the defeating Gym Leader grants that unlock with badge + TM ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards)). Vanilla HM fetch quests and tutors are removed ([Story-3](DESIGN-STORY.md#story-3-story-and-script-policy)).


## Badge → field abilities (single reference)


| Badges | Unlock | Notes |
| ------ | ------ | ----- |
| 1 | **Flash** | Dark Cave, Rock Tunnel, blocked until unlocked. Not an HM item. |
| 2 | **Cut** (HM01) |  |
| 3 | **Rock Smash** (HM06) |  |
| 4 | **Headbutt** | Not an HM item |
| 5 | **Fly** (HM02) |  |
| 6 | **Surf** (HM03) |  |
| 7 | **Strength** (HM04) |  |
| 10 | **Whirlpool** (HM05) |  |
| 13 | **Waterfall** (HM07) |  |
| 16 | **Rock Climb** (HM08) |  |

Badge counts not in the table get Badge + TM only

**Unchanged vanilla** (learn move, party menu — not badge-gated): Sweet Scent, Dig, Teleport.

## Headbutt & Flash — battle teaching (vanilla vs target)

**Vanilla HGSS:** **Flash** is a normal TM teach in battle. **Headbutt is not a TM** — tutor-only teach.

**Target (this rom):** Badge **1** / **4** unlock **field** Flash and Headbutt ([table above](#badge--field-abilities-single-reference)) for party use when a Pokémon knows the move. Players who want those moves **in battle** need a teach item like any other field-adjacent move.

**Open work:** add a **Headbutt TM** (vanilla has none), remove or bypass vanilla tutor gates, audit early learnsets, and sell Flash / Headbutt from badge-gated shops when ready.

**Status today:** Johto Gym HM pilot grants badge + TM at some counts; Flash / Headbutt field unlock flow is not complete ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards)).


---

---



# World-4. TMs

**Status: PARTIALLY IMPLEMENTED**

TMs remain **consumable**. However **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops — see [World-6](DESIGN-WORLD.md#world-6-shops) (major hubs: Goldenrod, Celadon). **implemented**

## Game Corner TMs

Coin prizes at the department-store Game Corners **implemented**:

| Location | TM pool |
| -------- | ------- |
| **Goldenrod Game Corner** | TM05, TM44, TM46, TM75, TM90, TM92 |
| **Celadon Game Corner** | TM10, TM32, TM49, TM58, TM67, TM82 |

**Held items** (implemented with TMs above):

| Location | Items |
| -------- | ----- |
| **Goldenrod Game Corner** | Bright Powder, Quick Claw, Wide Lens, Metronome |
| **Celadon Game Corner** | Focus Band, Zoom Lens, Scope Lens, Luck Incense |

### Coin income (not implemented)

**Temporary pricing:** all Game Corner TM, held-item, and Pokémon prizes cost **50 Coins** until proper coin income and tiered pricing ship. This is a playtest shortcut only — not the long-term economy.

Prize menus are wired; **earning Coins is still vanilla** (**Voltorb Flip** on the Game Corner floor). Game Corner TMs are buyable in principle but **Coin income is the bottleneck** until something from [Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes) ships.

## Gym TMs

**Not implemented**

Each Gym Leader has a **curated TM pool** (table below). Every `(Leader, TM)` row has a **minimum badge count** (authored per TM; not necessarily uniform within a pool).

After the player **defeats** that Leader (first clear or **rematch**), they **choose one TM** from that Leader's pool among entries whose badge requirement is **≤ badges earned** (including the badge just awarded). Same choice rules on rematch — renewable TM source ([Battle-3](DESIGN-BATTLES.md#rematches)).

Gym TM picks are intentionally **unlimited** over rematches

### Leader TM pools

**Badge count per TM** (minimum badges to offer that line in the choice menu) is defined in data when implemented — not listed here yet.

| Leader | TM pool |
| ------ | ------- |
| **Falkner** | TM40, TM51, TM88 |
| **Bugsy** | TM62, TM81, TM89 |
| **Whitney** | TM15, TM27, TM42, TM45, TM68 |
| **Morty** | TM30, TM56, TM65, TM66, TM79 |
| **Chuck** | TM01, TM08, TM31, TM52, TM60 |
| **Jasmine** | TM23, TM47, TM74, TM91 |
| **Pryce** | TM07, TM13, TM14, TM72 |
| **Clair** | TM02, TM59 |
| **Brock** | TM26, TM37, TM39, TM69, TM71, TM80 |
| **Misty** | TM03, TM18, TM55 |
| **Lt. Surge** | TM24, TM25, TM34, TM57, TM73 |
| **Erika** | TM09, TM19, TM22, TM53, TM86 |
| **Janine** | TM06, TM36, TM84 |
| **Sabrina** | TM04, TM29, TM48, TM77, TM85 |
| **Blaine** | TM11, TM35, TM38, TM50, TM61 |

---



# World-5. Evolution Methods (Trade & Stones)

**Status: IMPLEMENTED**

## Evolution stones

Every standard evolution stone is **renewably buyable** at themed town marts and dept-store shelves ([World-6 § What we’ve done](DESIGN-WORLD.md#what-weve-done)) — e.g. Fire at Ecruteak, Water at Cerulean — instead of vanilla’s mostly one-off pickups.

Some evolution items also drop from **Rock Smash** as a field source.

Player stone evolution rules are **unchanged** (use a stone on an eligible Pokémon). Flexible stone mechanics (type-matching shortcuts, high-level paths without stones) are deferred — [Future-13](DESIGN-FUTURE.md#future-13-expanded-stone-mechanics).

### Trade evolutions — with held item

*Evolutions that normally require **trade while holding an item** evolve when the item is **used on the Pokémon** — no trade required.

Examples: Dragon Scale → Kingdra, Metal Coat → Scizor, Protector → Rhyperior, etc.

### Trade evolutions — no item

**Linking Cord** — use on the Pokémon like a stone for plain trade lines. **Marts:** Goldenrod dept **2F lower** and Celadon dept **4F** ([World-6 § dept stores](#goldenrod--celadon-department-stores)).

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

Poké / Great / Ultra / Net / Repeat / Timer Balls; Repels; Escape Rope; Poké Doll; Sitrus & Lum Berries; **Flash TM**; Cleanse Tag; held battle items through Life Orb — each row gated by **minimum badge count** (0–12).

### Goldenrod & Celadon department stores

| Floor | Stock |
| ----- | ----- |
| **2F (upper)** | **Goldenrod:** Poké Balls, Repels, Escape Rope, Doll, Cheri → Persim berries — **Celadon:** same berry aisle as vanilla-style upper 2F |
| **2F (lower)** | **Goldenrod:** **Linking Cord**, Chilan Berry, Silk Scarf, Grip Claw, Sticky Barb, Shed Shell — **Celadon:** Poké Balls, Repels, Escape Rope, Doll |
| **TM floor** | **Celadon 3F:** TM12, 20, 21, 28, 41, 76, 78, 87 — **Goldenrod 5F:** TM16, 17, 33, 43, 54, 63, 64, 83 |
| **Battle items** | **Celadon 5F left / Goldenrod 3F:** Power Bracer–Weight + Macho Brace (replaces X items) |
| **Vitamins** | Protein–HP Up + **Rare Candy**, **PP Up**, **PP Max** |
| **Celadon 4F** | **Linking Cord**, Sun & Leaf Stones, Rindo Berry, Miracle Seed, Grip Claw, Sticky Barb, Shed Shell |
| **Goldenrod herbs** | Pomeg, Kelpsy, Qualot, Hondew, Grepa, Tamato Berries (replaces powders/roots) |

### Town / route specialty clerks

Themed Evolution items, held items, resist berries:

| Location | Items (summary) |
| -------- | ----------------- |
| Azalea | King's Rock, Silver Powder, Tanga Berry |
| Violet | Razor Fang, Coba Berry |
| Ecruteak | Fire Stone, Charcoal, Occa Berry, Magmarizer, Flame Orb |
| Olivine | Secret Medicine, Metal Coat, Babiri Berry |
| Cianwood pharmacy clerk | Poké Ball, Dawn Stone, Black Belt, Chople Berry |
| Vermilion / Safari | Thunder Stone, Electirizer, Magnet, Wacan Berry |
| Cerulean | Water Stone, DeepSea Tooth/Scale, Mystic Water, Passho Berry |
| Lavender | Dusk Stone, Reaper Cloth, Black Glasses, Spell Tag, Kasib, Colbur Berries |
| Saffron | Up-Grade, Dubious Disc, Twisted Spoon, Payapa Berry |
| Fuchsia | Shiny Stone, Poison Barb, Kebia Berry, Toxic Orb, Black Sludge |
| Pewter | Hard Stone, Charti Berry |
| Viridian | Protector, Soft Sand, Shuca Berry |
| Blackthorn / Battle Frontier | Dragon Scale, Dragon Fang, Haban Berry |
| Mt. Moon Square | Moon Stone |
| Mahogany | Poké Ball, Never-Melt Ice, Yache Berry, Razor Claw |
| Indigo Plateau | Ultra & Timer Balls, Max Repel, Lum Berry, Leftovers, Shell Bell, Focus Sash, Choice Band / Specs / Scarf, Life Orb |

---

# World-7. Berry economy

**Status: MOSTLY IMPLEMENTED** — Remaining item is Violet / Fuchsia shard traders (Liechi–Rowap).

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
| Rare battle (Liechi–Rowap) | Pinch boosts, Enigma heal, Custap priority, Jaboca / Rowap counter | **Shard traders** in **Violet City** and **Fuchsia City** | Not implemented |

## Wild Pokémon holds

**Implemented:** In addition to the table above, every supported berry can be a wild Pokémon's **held-item**. After the normal species held-item table roll (buffed to **65%** common / **15%** rare / **20%** nothing; **Compound Eyes** lead **70%** / **30%** / **0%**), wilds with no item get a **50%** chance (**100%** with Compound Eyes) of a uniform random berry from the **45** supported berries.

---
