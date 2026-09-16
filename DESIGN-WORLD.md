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

---

# World-1. World Transportation

**Status: PARTIALLY IMPLEMENTED**

Most traditional story roadblocks should be removed ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)).

Transportation systems should allow broad world traversal from early in the game.

These include:

- Goldenrod/Saffron Train
- Olivine/Vermillion SSAqua
- Early Fly HM and Fly works across regions.
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
| 5 | **Fly** (HM02) | Fast travel between visited cities | |
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

If [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) is implemented, Pokémon Centers may provide distributed Apricorn Ball crafting. **Not core scope.**

### Additional services

Other useful trainer services can be added as systems develop.

---



# World-5. TMs

**Status: DECIDED — core release target** (not implemented as designed; mart pass still open — [KB-4](DESIGN.md#index-5-known-bugs)).

TMs remain **consumable**.

However:

> **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops — see [World-7](DESIGN-WORLD.md#world-7-shops) (major hubs: Goldenrod, Celadon).

## Game Corner TMs

Some TMs remain Game Corner rewards.

## Rare / overworld TMs

Rare TMs that would traditionally exist as one overworld copy can also become obtainable through [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) living-trainer interactions; **initial release** relies on [World-7](DESIGN-WORLD.md#world-7-shops) hub shelves.

## Gym TMs

The first Gym victory awards the Gym's TM.

Rematching that Gym Leader at the player's current badge tier awards another copy ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).

Gym TM farming is intentionally unlimited.

---



# World-6. Evolution Methods (Trade & Stones)

**Status: PARTIALLY DECIDED — stone expansion OPTIONAL / TBD**

QoL changes to trade and stone evolution. **Not required** for the core open-world shell or trainer scaling; can ship on its own schedule. Placed before the Apricorn addon pointer because both touch items, but this section is **core Design 1**, not `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)`.

## Trade evolutions — with held item

Evolutions that normally require **trade while holding an item** should evolve when the item is **used on the Pokémon** — no trade required.

Examples: Dragon Scale → Kingdra, Metal Coat → Scizor, Protector → Rhyperior, etc.

## Trade evolutions — no item

Evolutions that require **trade alone** need a substitute for multiplayer. **TBD — pick one (or combine):**

### Option A: Link Cable item

Add a **Link Cable** usable item that triggers the same evolution as trade (inventory convenience, no level gate).

### Option B: Level-up evolution


| Pokémon            | Evolves at |
| ------------------ | ---------- |
| Graveler → Golem   | 38         |
| Machoke → Machamp  | 38         |
| Kadabra → Alakazam | 42         |
| Haunter → Gengar   | 42         |


## Optional: expanded stone mechanics

**Status: OPTIONAL — cool but not committed**

Evolution stones become more flexible for the matching **elemental type** (Fire Stone on Fire-types, Water Stone on Water-types, etc.).

### Pokémon that do not normally evolve with that stone

Using the matching stone **lowers the next natural level-up evolution by ~5 levels** (one step toward the target stage). Exact stacking rules TBD.

Example — Cyndaquil line (natural levels **16** / **36**):

- Stone on Fire-type at **11+** / **31+** instead of waiting for 16 / 36.

Example — Rapidash (natural level **40**):

- Level **40** as today, **or** Fire Stone on Ponyta/Rapidash at **35+**.



### Pokémon that normally evolve by stone only

- **Stone at any level** (keep the classic convenience).
- **Also** a **high level-up path** without the stone.


| Stage pattern                                     | Stone                       | Level without stone |
| ------------------------------------------------- | --------------------------- | ------------------- |
| 1st stage, stone-only (e.g. Exeggcute, Growlithe) | matching stone at any level | **35**              |
| 2nd stage, stone-only (e.g. Gloom, Poliwhirl)     | matching stone at any level | **50**              |


### Open questions (stones)

- Exact −5 behaviour: one-time per stage, permanent flag, or repeatable?
- Dual-types: either type matches, or primary type only?
- Using a stone on a Pokémon with no evolution in that line — no effect?
- Interaction with [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) evolution exclusions for generated trainer teams.

Shop availability for stones and Link Cables: [World-7](DESIGN-WORLD.md#world-7-shops).

---



# World-7. Shops

**Status: DECIDED — core release target** — especially **renewable TMs** ([World-5](DESIGN-WORLD.md#world-5-tms)) and **evolution items** (stones, Link Cable, trade held items when [World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones) ships). Per-mart inventories TBD.

**Known bug:** current ROM mart stock is wrong ([KB-4](DESIGN.md#index-5-known-bugs)) — treat shop redesign below as target, not what ships today.

Marts are redesigned around [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition) (post-battle full restore) and [Battle-3](DESIGN-BATTLES.md#battle-3-core-trainer-battle-philosophy) (no bag items in trainer battles). Most vanilla consumables no longer have a job.

## Remove from shops

### Battle-only stat boosters

Not usable in trainer battles; wild fights end with full restore, so mid-battle buffs are unnecessary.

- X Attack, X Defend, X Special, X Sp. Def (if present), X Speed, X Accuracy;
- Dire Hit;
- Guard Spec.

### Healing and status cures

HP, PP, and status are restored after every battle (including wild). Healing items cannot be used in trainer battles anyway.

- Potions (Regular / Super / Hyper / Max), Full Restore;
- Revive, Max Revive;
- Full Heal and single-status cures (Antidote, Burn Heal, Ice Heal, Awakening, Paralyze Heal);
- PP restoration (Ether, Elixir, Max Ether, Max Elixir);
- Food/healing fluff with no other role (Moomoo Milk, Fresh Water, Soda Pop, Lemonade, Lava Cookie, etc.) unless repurposed later.

## Keep / expand

### Poké Balls

Standard balls remain in marts across the region (Great / Ultra / Premier as progression unlocks). Specialty balls follow [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) when that ships — **Quick Ball** and **Dusk Ball** stay out of normal shops even in core design notes.

### TMs

Renewable TM stock at **department-store hubs** — primarily **Goldenrod** and **Celadon** ([World-5](DESIGN-WORLD.md#world-5-tms)). Smaller towns do not need full TM shelves.

### Evolution items

When [World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones) ships:

- **Evolution stones** (Fire, Water, Thunder, Leaf, Moon, Sun, Dusk, Dawn, Shiny, Ice if used) at Goldenrod / Celadon, and sprinkled throughout.
- **Link Cable** (trade-evolution substitute) at the same hubs;
- held-item trade evolutions use **on-Pokémon item use** — those held items (Metal Coat, Dragon Scale, etc.) should also be buyable at hubs or from specialists.

### Held items (combat gear)

Unlocked via Badge count, and sprinkled around the shops. Intentionally not consolidated at Goldenrod/Saffron

20% type boosters available in their matching gym type city. Normal, Ground, Dark available in the big marts.

### Field / utility (keep)

- **Repel**, Super Repel, Max Repel — wild-level risk remains ([Wilds-2](DESIGN-WILDS.md#wilds-2-starting-city-distance-based-wild-level-caps));
- **Escape Rope**
- **Vitamins** (Protein, Iron, etc.) — EV training unchanged in vanilla; still sold if EVs matter.

## Hub vs route marts


| Mart type                                   | Typical stock                                                           |
| ------------------------------------------- | ----------------------------------------------------------------------- |
| **Route / small town**                      | Poké Balls, Repels, 1-2 held items & 1-2 evolution items                |
| **Mid city**                                | Above + wider held pool, some mid-tier gear                             |
| **Goldenrod / Celadon (department stores)** | Full ball range, **TMs**, **stones / Link Cable**, broad held selection |


Vanilla per-map mart inventories need a **pass** when shop redesign ships — see [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog) (e.g. Secret Medicine only via Olivine clerk, not random route shops).

## Living-trainer economy

[Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions): trainers may **buy and sell** items — sink for duplicates and source for rare TMs / held gear. **Not initial release scope**; hub marts carry the renewable economy first.

## Open questions

- Sell-only / buyback marts for treasure (Nugget, Pearl, etc.)?
- Dedicated **berry** vendors vs mixing berries into held tier?
- Game Corner: coins for TMs / held items only — no battle boosters?
- Badge-gated shop tiers (e.g. Ultra Balls, late held items)?
- Ability Patch / Capsule, mints, mega stones — if ever added, likely **not** general marts.
