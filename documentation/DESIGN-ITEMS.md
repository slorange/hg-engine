# Pokémon Wandering Heart — Items & Economy

> Item sources, rewards, TMs, evolution items, shops, berries, and Apricorn Balls.
>
> **Index:** [Design index](DESIGN.md) · **World:** [World & Travel](DESIGN-WORLD.md)

## Sections

| Section | Status |
| ------- | ------ |
| [Items-1. Item acquisition channels](#items-1-item-acquisition-channels) | PARTIALLY IMPLEMENTED |
| [Items-2. TMs](#items-2-tms) | IMPLEMENTED |
| [Items-3. Evolution Methods (Trade & Stones)](#items-3-evolution-methods-trade--stones) | IMPLEMENTED |
| [Items-4. Shops](#items-4-shops) | IMPLEMENTED |
| [Items-5. Berry economy](#items-5-berry-economy) | IMPLEMENTED |
| [Items-6. Apricorn economy & Poké Ball rebalance](#items-6-apricorn-economy--poké-ball-rebalance) | PARTIALLY IMPLEMENTED |

---

# Items-1. Item acquisition channels

**Status: PARTIALLY IMPLEMENTED** — not every row or channel in this section is required for **initial release**; ship channels independently as scope allows.

The matrix below is the target for **where** each item category may appear. **Berries** follow [Items-5](#items-5-berry-economy). **Apricorn Ball** rebalancing and tree harvest are [Items-6](#items-6-apricorn-economy--poké-ball-rebalance).

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
<tr><th>Item category</th><th><a href="#items-4-shops">Shops</a></th><th>Ground / Hidden</th><th>Bug Contest</th><th>Pokéathlon</th><th>Battle Frontier</th><th>Pokédex rewards</th><th><a href="#items-2-tms">Game Corner</a></th></tr>
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

Ground and hidden pickups roll a category, then a reward within that category. The category weights are **20% Treasures**, **15% Evolution items**, **10% Held items**, **10% TMs**, **10% Balls**, **15% Apricorns**, and **20% Pokémon upgrades**. Pokémon upgrades include Rare Candy, PP Up and PP Max, vitamins, Bottle Caps, Mints, Ability Capsule, and Ability Patch. Treasures are the vanilla ones, plus Heart Scale. Berries and field utility items are disabled. If enabled, the Berry pool uses the 45 berries mentioned in Items-5.

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

**Hidden Power** type is set by using an Arceus Plate on the Pokémon. The plate stays in the bag ([Future-11](DESIGN-FUTURE.md#hidden-power)). Until then, the type stays IV-dependent. The Unown collection scales Hidden Power’s power ([World-6](DESIGN-WORLD.md#world-6-unown-collection-quest)).

---

# Items-2. TMs

**Status: IMPLEMENTED**

TMs remain **consumable**. However **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops — see [Data-5. Department stores](DESIGN-DATA.md#goldenrod--celadon-department-stores).

## Game Corner TMs

Coin prizes at the department-store Game Corners

See [Data-1. Game Corner prize pools](DESIGN-DATA.md#data-1-game-corner-prize-pools).

## Gym TMs

Each Gym Leader has a **curated TM pool**. Every TM has its own **minimum badge count**. See [Data-2. Gym Leader TM pools](DESIGN-DATA.md#data-2-gym-leader-tm-pools).

After the player **defeats** that Leader (first clear or **rematch**), they **choose one TM** from that Leader's pool among entries whose badge requirement is **≤ badges earned** (including the badge just awarded). Same choice rules on rematch — renewable TM source ([Battle-3](DESIGN-BATTLES.md#rematches)).

---

# Items-3. Evolution Methods (Trade & Stones)

**Status: IMPLEMENTED**

## Evolution stones and items

Every standard evolution stone is **renewably buyable** at themed town marts and dept-store shelves ([Items-4 § What we’ve done](#what-weve-done)) — e.g. Fire at Ecruteak, Water at Cerulean — instead of vanilla’s mostly one-off pickups. Some evolution items also drop from **Rock Smash** as a field source.

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

# Items-4. Shops

**Status: IMPLEMENTED** — renewable **TMs** ([Items-2](#items-2-tms)), **evolution items**, and **held gear** without vanilla’s one-shot consumable grind.

## Overall idea

Marts follow [Battle-1](DESIGN-BATTLES.md#recovery) (full restore after every battle) and [Battle-1](DESIGN-BATTLES.md#items) (no bag items in trainer battles). **Remove** as default shop stock: potions, antidotes, X items, etc.

**Sell:**

| Category | Intent |
| -------- | ------ |
| **Poké Balls & repels** | Capture and wild-level risk ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps)); specialty balls wait on [Items-6](#items-6-apricorn-economy--poké-ball-rebalance) — **Quick Ball** and **Dusk Ball** stay out of normal shops. |
| **TMs** | Renewable sets at **Goldenrod / Celadon** dept hubs; Gym **choice pools** and **Game Corner** lists in [Items-2](#items-2-tms). |
| **Evolution items** | Stones and trade-evolution held items at **themed town marts**; **Linking Cord** at Goldenrod dept 2F lower + Celadon 4F ([Items-3](#items-3-evolution-methods-trade--stones)). |
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

# Items-5. Berry economy

**Status: IMPLEMENTED**

Berries stay a meaningful **held-item** layer: the player cannot use Bag items in trainer battles ([Battle-1](DESIGN-BATTLES.md#items)), so automatic berry effects remain one of the main in-battle effects. Growth via Berry Pots is unchanged in role.

**Berries are restored after battle, along with all held items**

**Scope:** **45** Gen IV berries + Roseli

**Removed (19):** Figy-family weak-heal berries; Poffin / contest berries — little use beyond Natural Gift.

## Berry Pots and starter supply

Mom intro grants **Berry Pots** and **5× each** basic berry **Cheri through Persim**.

## Acquisition by group

| Group | Role | Primary sources | Status |
| ----- | ---- | ----------------- | ------ |
| Basic (Cheri–Persim) | Status cure, Leppa PP, Oran HP | Starter pack; Goldenrod & Celadon dept **2F upper** (partial medicine replacement) | Implemented |
| Lum + Sitrus | Full status / 25% max HP | Badge-scaled regular marts (4 and 6 badges) | Implemented |
| EV / friendship (Pomeg–Tamato) | −EVs, +friendship | Goldenrod Underground medicine seller (beside Haircut Brothers) | Implemented |
| Type-resistance (Occa–Chilan) & Roseli | Super-effective hit reduction | Themed **local specialty shops** ([Items-4 § Town clerks](#town--route-specialty-clerks) — e.g. Wacan at Vermilion, Passho at Cerulean). Mom’s vanilla resist-berry purchasing **unchanged for now**. | Implemented |
| Rare battle (Liechi–Rowap) | Pinch boosts, Enigma heal, Custap priority, Jaboca / Rowap counter | **Shard traders** in **Violet City** and **Fuchsia City** | Implemented |

## Wild Pokémon holds

**Implemented:** Wild Pokémon can hold any of the **46** fallback berries or any of the eight craftable Apricorn colours. The species held-item roll is **65%** common, **15%** rare, and **20%** nothing. With **Compound Eyes** in the lead, it is **70%** common and **30%** rare. Wild Pokémon that end up with no item get a **50%** chance (**100%** with Compound Eyes) of a fallback hold. That hold is **50%** a uniformly random berry and **50%** a uniformly random Apricorn.

---

# Items-6. Apricorn economy & Poké Ball rebalance


## Apricorn economy

Apricorns go directly into the Bag and become a renewable crafting resource tied to the accelerated game clock.

- Trees refresh once per in-game day (Not implemented)
- Each successful harvest yields **3–5 Apricorns**
- 29 additional Apricorn trees grow near the original locations across Kanto and Johto, bringing the total to 60. More locations are also planned (Not implemented)
- Colors are randomized per save file

The player does not need to repeatedly return to Azalea Town to craft Apricorn Balls. There is a new NPC in the Pokémon Center that will craft Apricorn Balls for a small fee.

## Ball design philosophy

**Shop balls** — readily available, generally weaker or reliable bonuses; useful without one infinitely purchasable ball dominating every capture.

**Apricorn balls** — renewable but resource-limited, with stronger specialized bonuses.

Intended to avoid: *"Buy 99 Quick Balls and throw one at everything."*

## Shop balls

Poké Ball, Great Ball, Ultra Ball, Timer Ball, Repeat Ball, Net Ball. Repeat and Net balls reduced to 3x catch rate.

## Apricorn balls

Colours signal ball identity rather than vanilla Apricorn associations. **Grey** and **Purple** are intentionally new — a signal to HGSS veterans that the system changed. The table lists the Center’s recipes and the proposed capture effects.

<table>
<colgroup>
<col style="width:10%">
<col style="width:12%">
<col style="width:11%">
<col style="width:67%">
</colgroup>
<thead>
<tr><th>Apricorn</th><th>Ball</th><th align="right">Maximum</th><th>Proposed effect</th></tr>
</thead>
<tbody>
<tr><td>🔴 Red</td><td>Fast Ball</td><td align="right">5× / 10× beasts</td><td>Base Speed under 40 / 40–59 / 60–79 / 80–99 / 100–119 / 120+ gives 0.5× / 1× / 2× / 3× / 4× / 5×. Raikou, Entei, and Suicune get 10×.</td></tr>
<tr><td>🩶 Grey</td><td>Heavy Ball</td><td align="right">8×</td><td>Effective weight under 10 / 10–24.9 / 25–49.9 / 50–99.9 / 100–199.9 / 200–399.9 / 400+ kg gives 0.5× / 1× / 2× / 3× / 4× / 6× / 8×.</td></tr>
<tr><td>🩷 Pink</td><td>Love Ball</td><td align="right">8×</td><td>3× opposite gender; 8× opposite gender + compatible Egg Group.</td></tr>
<tr><td>🟢 Green</td><td>Friend Ball</td><td align="right">8×</td><td>8× vs families with a friendship evolution (whole family qualifies); caught mon starts at <strong>200</strong> friendship.</td></tr>
<tr><td>🟡 Yellow</td><td>Level Ball</td><td align="right">8×</td><td>1× at equal level or above, 4× when the wild Pokémon is half the active Pokémon’s level, and 8× at one quarter or below. The multiplier rises linearly between each pair of points.</td></tr>
<tr><td>🟣 Purple</td><td>Dream Ball</td><td align="right">4×</td><td>Sleeping targets or targets with Comatose.</td></tr>
<tr><td>🔵 Blue</td><td>Quick Ball</td><td align="right">5×</td><td>First turn only.</td></tr>
<tr><td>⚫ Black</td><td>Dusk Ball</td><td align="right">7×</td><td>4× outdoors at night. Caves use 5× on floor 1, 6× on floors 2–3, and 7× on floors 4+ at any hour.</td></tr>
</tbody>
</table>

## Other potential ball ideas

- **Precision Ball** — increased catch rate when the target has exactly **1 HP** remaining.
- **Weather Ball** — increased catch rate during active weather (rain, sun, hail, sandstorm).
- **Pokédex Ball** — catch rate scales with **Pokédex completion percentage**.
- **Reversal Ball** — catch multiplier rises as the species' **base catch rate** falls (rarer species easier to catch).

## Balls removed from the roster

Heal Ball, Luxury Ball, Nest Ball, Dive Ball, Lure Ball
