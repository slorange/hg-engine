# Pokémon Wandering Heart — World & Travel

> Transportation, route gating, HMs, field moves, living trainers, shops, services, and accelerated time.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Vision:** `[DESIGN-VISION.md](DESIGN-VISION.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)`

# World-1. World Transportation

**Status: DECIDED conceptually**

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

## Kanto island ferries

**Status: DECIDED — not implemented**

Vanilla reach to **Cinnabar** and **Seafoam** assumes Surf (HM03). Open-world rules require a **non-Surf path** until HM03 unlocks from badge count ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)). Blaine’s Gym is on **Seafoam B4F** — see [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) for story-gate removal only.

Add **paid ferry NPCs** (Route 42 recipe — `documentation/HACK-NOTES.md`) for two destinations — separate services, same implementation pattern:


| Destination         | Why the player goes                                    | Design notes                                                                                                                                                        |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cinnabar Island** | Fire-type wilds, Mart/town services                    | Map work planned to **enable field encounters across the whole island** (not just the small vanilla grass patch). Ferry for pre-Surf travel from south Kanto coast. |
| **Seafoam Islands** | **Blaine** Gym; Ice-type encounter options in the cave | Ferry to entrance (or agreed shore); internal puzzles stay. Surf remains the free route once HM03 is available.                                                     |


Ferries are **transportation only** — no fetch chains, no badge gates on boarding. Price and shore NPC placement TBD; prefer routes the player already uses (Fuchsia, Vermilion, south Kanto coast) over dead-end-only cells.

Related: mandatory-route bypass principle ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)); Route 42 ferry verified in [Index-2](DESIGN.md#index-2-current-technical-baseline).

---



# World-2. Routes and Content Gating

**Status: PARTIALLY DECIDED** — open-travel principles are firm; **wild-level gating** here vs [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) is **undecided** (alternatives, or Wilds-3 primary with only light World-2).

## Open travel (DECIDED)

Cities should generally remain accessible regardless of badge count.

Where geography makes a dangerous route **mandatory** for reaching another city, the player should have an alternative transportation option (ferries, paid bypass NPCs — [World-1](DESIGN-WORLD.md#world-1-world-transportation), `HACK-NOTES.md`).

## Wild progression: World-2 vs Wilds-3 (TBD)

Two competing models keep wild areas from being appropriate everywhere at once:


| Model                             | How it works                                                                                                             | Doc                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **World-2** (badge / tile gating) | Block or warn on high-tier **grass, caves, routes** — guards, encounter-tile checks, badge counts                        | This section                                                                    |
| **Wilds-3** (distance caps)       | **Starting city + graph distance** sets each area's wild level ceiling; player can enter but fights scale with geography | [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) |


**Likely direction:** **Wilds-3 primary**, with **only a little World-2** where distance alone is not enough (see below). If Wilds-3 ships, **guard-style and encounter-tile wild gating see little use** — walking into high-level grass is a risk choice, not a hard block.

**Route 29 → Route 46 gatehouse** (2-badge coord gate) remains a verified PoC and template, but is **not** the intended main progression tool if Wilds-3 wins.

Gating methods when World-2 *is* used:

- guards;
- doors;
- badge/HM checks;
- encounter-tile checks;
- alternate paths.

Where guards would feel heavy-handed, encounter-tile gating is lighter: traverse freely on paths, block only stepping onto dangerous encounter tiles with a short message (e.g. *"The wild Pokémon here seem dangerous. You shouldn't enter yet."*).

Some routes may contain both low- and high-progression encounter areas simultaneously (more relevant in a World-2-heavy design).

## Always needed (regardless of Wilds-3)

World-2-style gating **still applies** for non–wild-level concerns:

- **HM / Flash / Headbutt** milestone locks ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)) — Surf routes, Flash dungeons (Dark Cave, Rock Tunnel), etc.
- **Victory Road / Pokémon League** — 16 badges.
- **Optional hard areas** — dungeons, postgame paths, or similar where distance caps alone are insufficient; light World-2 complements Wilds-3 here.

Wild **level** progression specifically may use [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps) instead of badge-gated encounter tiles across most of the world.

## Proof of concept (implemented)

**Route 29 → Route 46 gatehouse** — walk-past coord gate requiring **2 badges** (Zephyr + Hive). See `documentation/HACK-NOTES.md` § Route 46 gate. Template only if Wilds-3 is not the primary wild-progression model.

---

---



# World-3. HMs and Field Moves

**Status: DECIDED conceptually; unlock order and eligibility lists TBD**

HMs remain part of the game, but their overworld function is redesigned.

## HM progression

HMs are associated with **badge count**, not with defeating a particular specific Gym Leader.

Because Gyms can be completed in any order:

> Defeating the player's Nth Gym can unlock the Nth progression reward/HM.

The exact badge-count-to-HM mapping remains TBD.

This allows new world content to become available at predictable progression milestones regardless of Gym order.

## Field use

A Pokémon does **not** need to know the HM move to use its field ability.

Instead:

> If an eligible Pokémon species exists anywhere in the player's collection, the unlocked HM field ability can be used.

The Pokémon may be:

- in the field party; or
- stored in the box.



## Battle use

HMs still exist as moves.

The player can teach an HM normally if they actually want that move for combat.

## Inventory of field abilities (for design decisions)

Vanilla HGSS exposes several party-menu field moves beyond HMs. Policy below.

### Official HMs (HM01–HM08)


| Item | Move       | Typical field role                             |
| ---- | ---------- | ---------------------------------------------- |
| HM01 | Cut        | Remove small trees / grass obstacles           |
| HM02 | Fly        | Fast travel between visited cities             |
| HM03 | Surf       | Traverse water; water encounters               |
| HM04 | Strength   | Push boulders                                  |
| HM05 | Whirlpool  | Clear whirlpools on water routes               |
| HM06 | Rock Smash | Break rocks; can trigger Rock Smash encounters |
| HM07 | Waterfall  | Climb waterfalls                               |
| HM08 | Rock Climb | Climb rocky walls                              |


All eight use **badge-count unlock** + **collection-based field use** (see [Field use](#field-use) above). Exact badge → HM mapping TBD.

### Badge-gated field moves (HM-adjacent)

**Status: DECIDED** — **Flash** and **Headbutt** follow the **same rules as HMs**: unlock at a badge-count milestone (exact slot TBD), field use from any eligible species in the collection without teaching the move for overworld utility.


| Move         | Field role                      | Notes                                                                                                                                                                                                                                                      |
| ------------ | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Flash**    | Light dark caves / dungeons     | Without Flash unlocked, certain **dark dungeons are gated** — player cannot enter (or cannot progress past entrance) until the ability is unlocked. **Examples:** Dark Cave, Rock Tunnel. Exact map list and gate style (full block vs entrance-only) TBD. |
| **Headbutt** | Shake trees for wild encounters | Unlocks the **Headbutt encounter method** — separate tables (`data/Headbutt.c`), not the grass table. Trees remain a distinct ecology / progression tier alongside grass, fishing, Rock Smash, etc.                                                        |


Battle use: Flash and Headbutt remain normal learnable moves if the player wants them in combat; overworld utility does not require a moveslot (same principle as HMs).

### Other field moves (vanilla — no change planned)

**Status: DECIDED** — **not** badge-gated and **not** part of the HM/collection-field redesign. Leave vanilla behaviour (learn the move, use from party menu) unless a future task explicitly targets them.


| Move            | Vanilla field role               |
| --------------- | -------------------------------- |
| **Sweet Scent** | Force a wild encounter           |
| **Dig**         | Escape to previous cave entrance |
| **Teleport**    | Return to last Pokémon Center    |




### Related encounter / traversal systems (not party “field moves,” but same design bucket)


| System                                          | Role                          | Notes                                                                                                                        |
| ----------------------------------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Rock Smash encounters                           | Wild mons from smashing rocks | Own slots in `EncounterData` (2 slots); HM06-gated                                                                           |
| Surf / fishing encounters                       | Water wilds                   | Own tables per map; **Rod tier** gates which species appear — see [Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression) |
| Headbutt trees                                  | Wild mons from trees          | Own data files; **requires Headbutt unlock** (badge-gated, see above)                                                        |
| Cut trees / smashable rocks / Strength boulders | Map obstacles                 | Badge-gated collection field use                                                                                             |
| Whirlpool / Waterfall / Rock Climb tiles        | Traversal gates               | Same                                                                                                                         |
| Fishing Rods (Old / Good / Super)               | Tiered fishing encounters     | **Not badge-gated** — see [Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression)                                         |
| Flash-required dungeons                         | Dark Cave, Rock Tunnel, …     | **Traversal gate** until Flash unlock; list expandable                                                                       |




### Design questions to resolve

- Which **badge count** unlocks each HM, **Flash**, and **Headbutt**?
- Full list of **Flash-gated** dungeons and whether gating is map-wide or entrance-only.
- Should **Headbutt** / **Rock Smash** encounter pools tie into early vs late progression tiers (similar to grass gating)?

Mark HM/Flash/Headbutt unlock order here as decided; do not invent badge slots without explicit design.

---

---



# World-4. Accelerated Day/Night Cycle

**Status: DECIDED direction; exact timing subject to balance**

HGSS's real-world clock should be replaced by an accelerated in-game clock.

Current target:

> **Approximately 30 real-world minutes = one complete in-game day.**

This number may be tuned.

The accelerated clock affects systems including:

- day/night encounters;
- evolutions;
- NPC behaviour;
- events;
- potentially other systems (including Apricorn refresh if `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)` is implemented);



## Time advancement

The player should be able to deliberately advance time rather than waiting.

Likely mechanisms include both:

### Resting at Pokémon Centers / hotels

Allows controlled advancement of time ([World-7](DESIGN-WORLD.md#world-7-pokmon-centers)).

### Portable resting

A tent, sleeping bag, camping system, or similar mechanic can potentially allow resting outside towns.

Exact implementation remains TBD.

---

---

---



# World-5. Living Trainers

**Status: CORE FEATURE / DECIDED conceptually**

This is intended to be one of the project's most distinctive systems.

Ordinary Pokémon trainers should not primarily exist as static NPCs permanently staring at a single tile waiting for the player.

Trainers are intended to create the illusion of a population travelling through Johto and Kanto on Pokémon journeys of their own.

They can:

- move around cities;
- travel between locations;
- appear on routes;
- walk through grass;
- have different levels of progression;
- interact with the player in multiple ways;
- appear to be battling each other.

Each trainer has or represents a badge progression level.

Trainer progression distributions may be influenced by location.

The player should generally battle trainers whose progression is reasonably comparable to their own.

## Simulation requirements

**Status: TBD / TECHNICAL**

The game does NOT necessarily need to permanently simulate hundreds of individual NPCs throughout the entire world.

A technically simpler system may generate or populate trainers when maps load while maintaining the **illusion** of a persistent travelling trainer population.

The experiential goal matters more than literally simulating every trainer off-screen.

---



# World-6. Trainer Interactions

**Status: DECIDED conceptually**

Living trainers are not exclusively battle dispensers.

Potential interactions include:

### Pokémon location requests

A trainer may ask:

> "Do you know where I can find a Heracross?"

If the player has encountered the requested Pokémon in the wild, they can provide a known encounter location from the **generated ecology** ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)).

The trainer provides a reward.

Possible rewards include:

- items;
- money;
- another Pokémon's encounter information;
- TMs;
- other useful information.



### Encounter information

Trainers may tell the player where Pokémon they have not yet discovered can be found (data from [Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)).

This creates a social/information economy around exploration.

### Pokémon trades

Some trainers request trades.

### Item trading

Trainers may buy or sell items.

### TMs

Some trainers provide renewable access to otherwise rare TMs ([World-8](DESIGN-WORLD.md#world-8-tms)).

### Gym advice

Trainers may provide information about nearby undefeated Gyms or their current scaled teams.

### Other quests

Additional lightweight interactions and quests can be added later.

---



# World-7. Pokémon Centers

**Status: DECIDED direction; exact services expandable**

Because healing is automatic ([Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition)) and PC access is universal ([Battle-6](DESIGN-BATTLES.md#battle-6-dynamic-battle-rosters)), Pokémon Centers no longer need to function primarily as healing/PC locations.

They instead become **trainer service hubs**.

Potential/current services include:

### Abra transportation

A trainer/Abra service can transport the player to other locations for a fee ([World-1](DESIGN-WORLD.md#world-1-world-transportation)).

### Resting

The player can rest to intentionally advance the accelerated in-game clock ([World-4](DESIGN-WORLD.md#world-4-accelerated-daynight-cycle)).

### Apricorn crafting

If the `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)` addon is implemented, Pokémon Centers may provide distributed Apricorn Ball crafting. **Not core scope.**

### Additional services

Other useful trainer services can be added as systems develop.

---



# World-8. TMs

**Status: DECIDED**

TMs remain **consumable**.

However:

> **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops — see [World-10](DESIGN-WORLD.md#world-10-shops) (major hubs: Goldenrod, Celadon).

## Game Corner TMs

Some TMs remain Game Corner rewards.

## Rare / overworld TMs

Rare TMs that would traditionally exist as one overworld copy can also become obtainable through [living-trainer interactions](DESIGN-WORLD.md#world-6-trainer-interactions).

## Gym TMs

The first Gym victory awards the Gym's TM.

Rematching that Gym Leader at the player's current badge tier awards another copy ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).

Gym TM farming is intentionally unlimited.

---



# World-9. Evolution Methods (Trade & Stones)

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
- Interaction with [Battle-8](DESIGN-BATTLES.md#battle-8-implementation) Phase 5 (trainers exclude trade/stone lines until policy exists).

Shop availability for stones and Link Cables: [World-10](DESIGN-WORLD.md#world-10-shops).

---



# World-10. Shops

**Status: DECIDED direction; per-mart inventories TBD**

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

Standard balls remain in marts across the region (Great / Ultra / Premier as progression unlocks). Specialty balls follow [DESIGN-FUTURE.md](DESIGN-FUTURE.md) Apricorn policy when that addon ships — **Quick Ball** and **Dusk Ball** stay out of normal shops even in core design notes.

### TMs

Renewable TM stock at **department-store hubs** — primarily **Goldenrod** and **Celadon** ([World-8](DESIGN-WORLD.md#world-8-tms)). Smaller towns do not need full TM shelves.

### Evolution items

When [World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones) ships:

- **Evolution stones** (Fire, Water, Thunder, Leaf, Moon, Sun, Dusk, Dawn, Shiny, Ice if used) at Goldenrod / Celadon, and sprinkled throughout.
- **Link Cable** (trade-evolution substitute) at the same hubs;
- held-item trade evolutions use **on-Pokémon item use** — those held items (Metal Coat, Dragon Scale, etc.) should also be buyable at hubs or from specialists.

### Held items (combat gear)

Unlocked via Badge count, and sprinkled around the shops. Intentionally not consolidated at Goldenrod/Saffron

20% type boosters available in their matching gym type city. Normal, Ground, Dark available in the big marts.

### Field / utility (keep)

- **Repel**, Super Repel, Max Repel — wild-level risk remains ([Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps));
- **Escape Rope**
- **Vitamins** (Protein, Iron, etc.) — EV training unchanged in vanilla; still sold if EVs matter.

## Hub vs route marts


| Mart type                                   | Typical stock                                                           |
| ------------------------------------------- | ----------------------------------------------------------------------- |
| **Route / small town**                      | Poké Balls, Repels, 1-2 held items & 1-2 evolution items                |
| **Mid city**                                | Above + wider held pool, some mid-tier gear                             |
| **Goldenrod / Celadon (department stores)** | Full ball range, **TMs**, **stones / Link Cable**, broad held selection |


Vanilla per-map mart tables (`src/field/mart.c`, `data/mart/` or equivalent) need a **pass** — see [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog) for obsolete entries (e.g. Secret Medicine only via Olivine special clerk, not random route shops).

## Living-trainer economy

[World-6](DESIGN-WORLD.md#world-6-trainer-interactions) trainers may **buy and sell** items — good sink for duplicates and source for rare TMs / held gear without putting everything in static marts.

## Open questions

- Sell-only / buyback marts for treasure (Nugget, Pearl, etc.)?
- Dedicated **berry** vendors vs mixing berries into held tier?
- Game Corner: coins for TMs / held items only — no battle boosters?
- Badge-gated shop tiers (e.g. Ultra Balls, late held items)?
- Ability Patch / Capsule, mints, mega stones — if ever added, likely **not** general marts.

---



# World-11. Technical Investigations

Open engineering questions for this area (from the former monolithic design doc). Battle-system investigations live in [Battle-9](DESIGN-BATTLES.md#battle-9-technical-investigations).

## Accelerated clock

Questions include:

- replacing RTC dependencies;
- event compatibility;
- day/night rendering;
- encounter tables;
- evolutions;
- manual time advancement.

(Apricorn refresh: `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)` addon.)

## HM progression

Questions include:

- decoupling field use from learned moves;
- checking eligible species across party + boxes;
- badge-count unlocks;
- existing scripts expecting specific badges/HMs.



## Living trainers

Questions include:

- map spawning;
- movement;
- persistence;
- generated identities;
- badge counts;
- generated collections;
- map transitions;
- save-state requirements.



## Trainer interactions

Questions include:

- ecology-linked location requests ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology));
- reward economy;
- trade and item-exchange UI;
- TM distribution hooks ([World-8](DESIGN-WORLD.md#world-8-tms)).



## Pokémon Centers

Questions include:

- Abra fast-travel integration ([World-1](DESIGN-WORLD.md#world-1-world-transportation));
- resting / time advancement ([World-4](DESIGN-WORLD.md#world-4-accelerated-daynight-cycle));
- which vanilla Center scripts to repurpose once healing/PC are automatic.



## TMs

Questions include:

- Game Corner integration;
- Gym TM rematch rewards ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters));
- renewable rare-TM sources via living trainers.

(Shop shelves and pricing: [World-10](DESIGN-WORLD.md#world-10-shops).)

## Evolution methods (trade & stones)

Questions include:

- Link Cable vs level-up trade substitutes ([World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones));
- held-item-on-use evolutions;
- optional expanded stone mechanics;
- stone/trade evolution policy for generated trainer teams ([Battle-8](DESIGN-BATTLES.md#battle-8-implementation) Phase 5).



## Shops

Questions include:

- rewriting `mart.c` / per-map inventories vs one global table;
- Goldenrod vs Celadon department-store layout;
- held-item tier gating by badge or city;
- Game Corner prize roster;
- removing obsolete healing / X-item entries without breaking scripts that `giveitem` them.

---

