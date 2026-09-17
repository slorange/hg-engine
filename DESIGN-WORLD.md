# Pokémon Wandering Heart — World & Travel

> Transportation, route gating, HMs, field moves, living trainers, shops, services, and accelerated time.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Vision:** `[DESIGN-VISION.md](DESIGN-VISION.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)`

## Sections

| Section | Status |
| ------- | ------ |
| [World-1. World Transportation](#world-1-world-transportation) | PARTIALLY IMPLEMENTED |
| [World-2. Routes and Content Gating](#world-2-routes-and-content-gating) | PARTIALLY DECIDED |
| [World-3. HMs and Field Moves](#world-3-hms-and-field-moves) | PARTIALLY IMPLEMENTED |
| [World-4. Pokémon Centers](#world-4-pokémon-centers) | DECIDED direction |
| [World-5. TMs](#world-5-tms) | DECIDED — **core release target** (renewable shop TMs) |
| [World-6. Evolution Methods (Trade & Stones)](#world-6-evolution-methods-trade--stones) | PARTIALLY DECIDED |
| [World-7. Shops](#world-7-shops) | DECIDED — **core release target** (TMs, evolution items) |
| Accelerated day/night cycle | Moved — [Future-9](DESIGN-FUTURE.md#future-9-accelerated-daynight-cycle) |
| Living trainers & interactions | Moved — [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) |
| Expanded stone mechanics | Moved — [Future-13](DESIGN-FUTURE.md#future-13-expanded-stone-mechanics) |

---

# World-1. World Transportation

**Status: PARTIALLY IMPLEMENTED**

Most traditional story roadblocks should be removed ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)).

Transportation systems should allow broad world traversal from early in the game.

These include:

- Goldenrod/Saffron Train
- Olivine/Vermillion SSAqua
- Early Fly HM — field use partially unblocked ([HACK-NOTES](documentation/HACK-NOTES.md) § Field HM badge bypass). **Kanto Fly map destinations not yet enabled** — in Kanto the UI still shows Johto only (vanilla likely E4 / SS Aqua gated).
- Pokemon Center Abra transportation
- local paid route bypasses where required



## Abra fast travel

Pokémon Centers may contain an Abra transportation service.

Travel likely costs money.

Exact destinations/costs remain TBD.

Likely only to cities that have already been visited.

## Paid ferry NPCs

**Status: PARTIALLY IMPLEMENTED** — Route 42 verified; additional ferries planned

**Route 42** (Blackthorn ↔ Mahogany water gaps) is the reference implementation — verified in [Index-2](DESIGN.md#index-2-current-technical-baseline); recipe in `documentation/HACK-NOTES.md`.

Add more **paid ferry NPCs** (same Route 42 recipe) for:

- Olivine ↔ Cianwood
- Dark Cave (Blackthorn ↔ Violet)
- Ice Path
- Pallet / Cinnabar / Seafoam / Fuchsia

---



# World-2. Routes and Content Gating

**Status: PARTIALLY DECIDED** — open-travel principles are firm. **Wild level progression** uses [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps) (implemented Sep 2026), **not** badge-guard / encounter-tile wild gating below.

## Open travel (DECIDED)

Cities should generally remain accessible regardless of badge count.

Where geography makes a dangerous route **mandatory** for reaching another city, the player should have an alternative transportation option (ferries, paid bypass NPCs — [World-1](DESIGN-WORLD.md#world-1-world-transportation), `HACK-NOTES.md`).

## Wild progression: World-2 vs Wilds-2 (decided)

Two models were considered for keeping wild areas from being appropriate everywhere at once:


| Model                             | How it works                                                                                                             | Status                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Wilds-2** (distance caps)       | **Starting city + graph distance** sets each area's wild level ceiling; player can enter but fights scale with geography | **Shipped** — [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps), verified Sep 2026 |
| **World-2** (badge / tile gating) | Block or warn on high-tier **grass, caves, routes** — guards, encounter-tile checks, badge counts                        | **Not used for wild levels** — retained below for HM/League/optional hard zones |

**Decision:** wild **levels** follow **Wilds-2** only. Walking into high-level grass is a risk choice, not a badge-gated tile block. We are **not** adding guard-style or encounter-tile wild level gates across the world.

**Route 29 → Route 46 gatehouse** (2-badge coord gate) remains a verified PoC and scripting template, but is **not** the wild progression model — see [Always needed](#always-needed-regardless-of-wilds-3) for where World-2-style gating still applies.

Gating methods when World-2 *is* used:

- guards;
- doors;
- badge/HM checks;
- encounter-tile checks;
- alternate paths.

Where guards would feel heavy-handed, encounter-tile gating is lighter: traverse freely on paths, block only stepping onto dangerous encounter tiles with a short message (e.g. *"The wild Pokémon here seem dangerous. You shouldn't enter yet."*).

Some routes may contain both low- and high-progression encounter areas simultaneously (more relevant in a World-2-heavy design).

## Always needed (regardless of Wilds-2)

World-2-style gating **still applies** for non–wild-level concerns:

- **HM / Flash / Headbutt** milestone locks ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)) — Surf routes, Flash dungeons (Dark Cave, Rock Tunnel), etc.
- **Victory Road / Pokémon League** — 16 badges.
- **Optional hard areas** — dungeons, postgame paths, or similar where distance caps alone are insufficient; light World-2 complements Wilds-2 here.

Wild **level** progression uses [Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps) exclusively (not badge-gated encounter tiles).

## Proof of concept (implemented)

**Route 29 → Route 46 gatehouse** — walk-past coord gate requiring **2 badges** (Zephyr + Hive). See `documentation/HACK-NOTES.md` § Route 46 gate. Scripting template only — **not** used for wild level progression ([Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps) handles wild levels).

---

---



# World-3. HMs and Field Moves

**Status: PARTIALLY IMPLEMENTED** — unlock order below decided; Johto Gym HM pilot partial; **collection-based field use** and full Leader grant flow not complete.

Field abilities unlock by **badges earned** (any Gym order): when badge count hits a row below, the defeating Gym Leader grants that unlock with badge + TM ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)). Vanilla HM fetch quests and tutors are removed ([Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)).

**Field use:** eligible species **anywhere in the collection** (party or box) can perform the overworld action — the Pokémon need not know the move. **Battle use:** HMs (and Flash / Headbutt) remain teachable moves if the player wants them in combat.

## Badge → field abilities (single reference)


| Badges | Unlock | Field role | Notes |
| ------ | ------ | ---------- | ----- |
| 1 | **Flash** | Light dark dungeons | **Traversal gate** until unlocked (Cannot enter Dark Cave, Rock Tunnel). Not an HM item. |
| 2 | **Cut** (HM01) | Trees / obstacles | |
| 3 | **Rock Smash** (HM06) | Break rocks | Separate **Rock Smash** encounter slots when smashing |
| 4 | **Headbutt** | Tree encounters | `data/Headbutt.c` — not grass table; not an HM item |
| 5 | **Fly** (HM02) | Fast travel between visited cities | Johto fly map works; **Kanto destinations still locked** — see [HACK-NOTES § Fly map](documentation/HACK-NOTES.md#fly-map--kanto-destinations-not-yet) |
| 6 | **Surf** (HM03) | Water routes + Surf encounters | |
| 7 | **Strength** (HM04) | Push boulders | |
| 10 | **Whirlpool** (HM05) | Clear whirlpools | |
| 13 | **Waterfall** (HM07) | Climb waterfalls | |
| 16 | **Rock Climb** (HM08) | Climb rock walls | |

Badge counts not in the table get Badge + TM only

**Unchanged vanilla** (learn move, party menu — not badge-gated, not collection-field): Sweet Scent, Dig, Teleport.

## Headbutt & Flash — battle teaching (vanilla vs target)

**Vanilla HGSS:** **Flash** is **TM070** (normal TM teach in battle). **Headbutt is not a TM** — the only teach source is the **Move Tutor** (`TUTOR_HEADBUTT`; first `TUTOR_HEADBUTT` row in tutor data is the only one read). Overworld Headbutt is gated on that tutor chain (Goldenrod → Azalea), not on a machine item.

**Target (this rom):** Badge **1** / **4** still unlock **collection-based field** Flash and Headbutt ([table above](#badge--field-abilities-single-reference)). Players who want those moves **in battle** need a teach item like any other field-adjacent move.

**Implementation backlog (not decided):**

1. **Make room for a Headbutt TM** — Vanilla has no Headbutt TM, Tutor only. Repurpose an existing TM number (`src/item.c` machine table, `data/itemdata`, hub mart arrays in `src/field/mart.c`) **or** map Headbutt onto an expanded TM item (`ITEM_TM093+` / HG-Engine TM expansion)
2. **Headbutt tutor** — Consider removing vanilla tutor NPC ([Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog))
3. **Learnset pass** — Audit species with **level-up** Headbutt (`MOVE_HEADBUTT`); Consider removing if any learn it at too low a level (before badge would naturally be acquired)
4. **Shops** — list **Headbutt TM** (and **Flash / TM070**) after badge requirement met

**Status today:** Johto Gym scripts grant badge + TM only at counts **1** and **4** — no Flash / Headbutt field flags yet ([HACK-NOTES](documentation/HACK-NOTES.md) § Gym HM grants).


---

---



# World-4. Pokémon Centers

**Status: DECIDED direction; exact services expandable**

Because healing is automatic ([Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition)), Pokémon Centers no longer need to function primarily as healing stations. Universal PC everywhere / in battle is [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc); vanilla PC locations remain for initial release.

They instead become **trainer service hubs**.

Potential/current services include:

### Abra transportation

A trainer/Abra service can transport the player to other locations for a fee ([World-1](DESIGN-WORLD.md#world-1-world-transportation)).

### Resting

The player can rest to intentionally advance the accelerated in-game clock when [Future-9](DESIGN-FUTURE.md#future-9-accelerated-daynight-cycle) is implemented.

### Apricorn crafting

If [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) is implemented, Pokémon Centers may provide distributed Apricorn Ball crafting.

### Additional services

Other useful trainer services can be added as systems develop.

---



# World-5. TMs

**Status: DECIDED — core release target.** Renewable hub TM shelves are **implemented** in `src/field/mart.c` ([World-7 § What we’ve done](DESIGN-WORLD.md#what-weve-done)); **Game Corner TM menus implemented** ([HACK-NOTES § Game Corner TM prizes](documentation/HACK-NOTES.md#game-corner-tm-prizes)); rare overworld TMs unchanged.

TMs remain **consumable**.

However:

> **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops — see [World-7](DESIGN-WORLD.md#world-7-shops) (major hubs: Goldenrod, Celadon).

## Game Corner TMs

Coin prizes at the department-store Game Corners (renewable — implemented in scr_seq + text banks; see [HACK-NOTES § Game Corner TM prizes](documentation/HACK-NOTES.md#game-corner-tm-prizes)):

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

Prize menus are wired; **earning Coins is still vanilla** — international HGSS replaced slot machines with **Voltorb Flip** on the Game Corner floor (`T25SP0101` / `T07SP0101`). That minigame is **not** the intended long-term coin grind for this rom.

**Requirement:** add at least one **renewable, low-friction** way to obtain Coins without playing Voltorb Flip, so Game Corner TMs stay a practical source alongside dept-store shelves.

**Not decided yet (pick one or combine):**

- **Buy Coins for ¥** — clerk at Goldenrod / Celadon Game Corner or dept store (exchange rate TBD).
- **Dept-store Coin counter** — same prize clerks also sell Coin bundles.
- **Restore a simpler casino game** — if technically feasible; slots were removed from non-JP HGSS.
- **Battle / trainer payout** — small Coin bonus from trainer wins (needs economy tuning vs [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition) money policy).

Until this ships, Game Corner TMs are technically buyable but **Coin income is the bottleneck**.

## Rare / overworld TMs

Rare TMs that would traditionally exist as one overworld copy can also become obtainable through [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) living-trainer interactions; **initial release** relies on [World-7](DESIGN-WORLD.md#world-7-shops) hub shelves.

## Gym TMs

Each Gym Leader has a **curated TM pool** (table below). Every `(Leader, TM)` row has a **minimum badge count** (authored per TM; not necessarily uniform within a pool).

After the player **defeats** that Leader (first clear or **rematch**), they **choose one TM** from that Leader's pool among entries whose badge requirement is **≤ badges earned** (including the badge just awarded). Same choice rules on rematch — renewable TM source ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).

Gym TM picks are intentionally **unlimited** over rematches (no finite TM problem — [World-5](#world-5-tms) policy).

**Implementation:** not shipped; vanilla / pilot scripts still grant a single fixed TM per Leader ([HACK-NOTES](documentation/HACK-NOTES.md) § Gym Leader HM rewards).

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



# World-6. Evolution Methods (Trade & Stones)

**Status: PARTIALLY DECIDED**

## Evolution stones

**Shipped:** Every standard evolution stone is **renewably buyable** at themed town marts and dept-store shelves ([World-7 § What we’ve done](DESIGN-WORLD.md#what-weve-done)) — e.g. Fire at Ecruteak, Water at Cerulean, Thunder at Vermilion, Moon at Mt. Moon Square, Sun & Leaf at Celadon 4F — instead of vanilla’s mostly one-off pickups.

**Planned:** All evolution stones will also be added to the **Rock Smash item tables** (`src/field/rock_smash_item.c`) as a field source alongside shops.

Player stone evolution rules are **unchanged** (use a stone on an eligible Pokémon). Optional flexible stone mechanics (type-matching shortcuts, high-level paths without stones) are deferred — [Future-13](DESIGN-FUTURE.md#future-13-expanded-stone-mechanics).

## Trade evolutions

QoL changes to trade evolution (held-item use-on-Pokémon, Link Cable / level-up substitutes for trade). **Not required** for the core open-world shell or trainer scaling; can ship on its own schedule.

### Trade evolutions — with held item

Evolutions that normally require **trade while holding an item** should evolve when the item is **used on the Pokémon** — no trade required.

Examples: Dragon Scale → Kingdra, Metal Coat → Scizor, Protector → Rhyperior, etc.

### Trade evolutions — no item

Evolutions that require **trade alone** need a substitute for multiplayer. **TBD — pick one (or combine):**

#### Option A: Link Cable item

Add a **Link Cable** usable item that triggers the same evolution as trade (inventory convenience, no level gate).

#### Option B: Level-up evolution


| Pokémon            | Evolves at |
| ------------------ | ---------- |
| Graveler → Golem   | 38         |
| Machoke → Machamp  | 38         |
| Kadabra → Alakazam | 42         |
| Haunter → Gengar   | 42         |

Shop availability for Link Cables (when implemented): [World-7](DESIGN-WORLD.md#world-7-shops).

---



# World-7. Shops

**Status: DECIDED — core release target** — renewable **TMs** ([World-5](DESIGN-WORLD.md#world-5-tms)), **evolution items**, and **held gear** without vanilla’s one-shot consumable grind.

## Overall idea

Marts follow [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition) (full restore after every battle) and [Battle-3](DESIGN-BATTLES.md#battle-3-core-trainer-battle-philosophy) (no bag items in trainer battles). **Remove** as default shop stock: potions and Full Restore; single-status cures and PP restores; X items, Dire Hit, and Guard Spec; food/healing fluff with no other role (Moomoo Milk, route drinks, etc.) unless repurposed later.

**Sell:**

| Category | Intent |
| -------- | ------ |
| **Poké Balls & repels** | Capture and wild-level risk ([Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps)); specialty balls wait on [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) — **Quick Ball** and **Dusk Ball** stay out of normal shops. |
| **TMs** | Renewable sets at **Goldenrod / Celadon** dept hubs; Gym **choice pools** and **Game Corner** lists in [World-5](DESIGN-WORLD.md#world-5-tms). |
| **Evolution items** | Stones and trade-evolution held items at **themed town marts** (and hub floors where noted); **Link Cable** at major hubs when [World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones) ships. |
| **Held items** | **Badge-gated** progression, some on dept **2F**, **20% type boosters** in matching Gym cities |
| **Utility** | Escape Rope, Poké Doll, vitamins + EV training at hubs. |


**Later (not initial release):** [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) living-trainer buy/sell for duplicates and rare TMs — hub marts carry the economy first.

## What we’ve done

**ROM:** `#define MART_EXPANSION` in `include/config.h` → **`src/field/mart.c`** ([HACK-NOTES § Mart expansion](documentation/HACK-NOTES.md#mart-expansion-srcfieldmartc)). Playtest after edits.

### Badge-gated shelf (most shops)

`ScrCmd_MartBuy` → `sBadgeMart[]`: Poké / Great / Ultra / Net / Repeat / Timer Balls; Repels; Escape Rope; Poké Doll; Sitrus & Lum Berries; **TM70 (Flash)**; Cleanse Tag; White / Mental / Power Herbs; Muscle Band & Wise Glasses; Big Root; Expert Belt; Light Clay; Metronome; Leftovers; Shell Bell; Focus Sash; Choice Band / Specs / Scarf; Life Orb — each row gated by **minimum badge count** (0–12).

### Goldenrod & Celadon department stores

| Floor | Stock |
| ----- | ----- |
| **2F (upper)** | Cheri → Persim status berries (replaces potion aisle) |
| **2F (lower)** | Balls, Escape Rope, Doll, Repels; Goldenrod adds Chilan Berry, Silk Scarf, Grip Claw, Sticky Barb, Shed Shell (Celadon lower 2F: no mail) |
| **TM floor** | **Celadon 3F:** TM12, 20, 21, 28, 41, 76, 78, 87 — **Goldenrod 5F:** TM16, 17, 33, 43, 54, 63, 64, 83 |
| **Battle items** | **Celadon 5F left / Goldenrod 3F:** Power Bracer–Weight + Macho Brace (replaces X items) |
| **Vitamins** | Protein–HP Up + **Rare Candy**, **PP Up**, **PP Max** |
| **Celadon 4F** | Sun & Leaf Stones, Rindo Berry, Miracle Seed, Grip Claw, Sticky Barb, Shed Shell |
| **Goldenrod herbs** | Pomeg, Kelpsy, Qualot, Hondew, Grepa, Tamato Berries (replaces powders/roots) |

### Town / route specialty clerks (`std_special_mart` arrays)

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

## What’s left to do

**Implementation**

- ~~**Game Corner TM + held-item menus**~~ — **done** ([HACK-NOTES § Game Corner TM prizes](documentation/HACK-NOTES.md#game-corner-tm-prizes)); Pokémon submenu still vanilla.
- **Game Corner Coin income** — alternative to Voltorb Flip ([World-5 § Coin income](DESIGN-WORLD.md#coin-income-not-implemented)); not investigated.
- **Gym TM choice** — Leader pools + per-TM badge gates + pick-one UI ([World-5 § Gym TMs](DESIGN-WORLD.md#gym-tms)); scripts still grant one fixed TM ([HACK-NOTES](documentation/HACK-NOTES.md) § Gym Leader HM rewards).
- **Link Cable** on hub shelves when trade-evolution substitute ships ([World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones)).
- **Headbutt TM** slot and badge-gated shop row alongside Flash ([World-3](DESIGN-WORLD.md#headbutt--flash--battle-teaching-vanilla-vs-target)).

---
