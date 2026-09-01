# Pokémon Wandering Heart — Design Document

> Working design document (**Design 1 — core ROM**) for a Pokémon HeartGold/SoulSilver ROM hack built using HG-Engine.
>
> This document is the source of truth for **core** game design: open world, progression, battles, trainers, travel, and world systems.
>
> **Future / addon design:** [`DESIGN2.md`](DESIGN2.md) — V2 ball rebalance, V3 Full Moon, V4 unlimited moves. Not required for the core ROM.
>
> **This document is NOT an instruction to automatically implement everything described here.**

---

# 1. Instructions for Coding Agents

This project contains systems that may require substantial changes to Pokémon HeartGold and HG-Engine.

When using this document as development context:

- Only implement features explicitly requested for the current task.
- Do not interpret the existence of a feature in this document as permission to begin implementing it.
- Prefer small, incremental changes that leave the ROM buildable and playable.
- Investigate HG-Engine and HGSS architecture before making invasive engine changes.
- Identify technical risks before modifying fundamental systems.
- If the desired design conflicts with HG-Engine or HGSS limitations, explain the limitation and possible alternatives rather than silently changing the design.
- Do not simplify a design merely because the simpler implementation is easier without discussing the tradeoff first.
- Configuration should be preferred for balance-sensitive numbers where practical.
- Preserve compatibility with the existing Docker build process.
- `rom.nds` and generated ROM files must never be committed.

The design statuses used in this document are:

**DECIDED** — Current intended design. Numbers may still be balanced later.

**TBD** — The design has deliberately not been decided yet.

**TECHNICAL UNKNOWN** — Desired behaviour is understood, but feasibility/implementation in HGSS/HG-Engine needs investigation.

**V2 / PARKING LOT** — Interesting idea explicitly excluded from initial scope.

---

# 2. Core Vision

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

# 3. Open-World Philosophy

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

# 4. Starting Location

## Starting city

**Status: DECIDED (prototype scope locked for v1 testing)**

The player chooses their starting city from locations throughout Johto and Kanto.

Long-term intention is broad freedom rather than a small set of traditional starting towns. **v1 prototype list (functionality testing only — not final design):**

| Index | City |
|------:|------|
| 0 | New Bark Town |
| 1 | Goldenrod City |
| 2 | Saffron City |

Every available starting city must provide reasonable access to:

- appropriately levelled encounters;
- early trainer content;
- necessary services;
- transportation;
- a viable first Gym challenge.

### Home / house wiring (v1 approach)

Not a simple “redirect the house exit.” Each city needs a **designated outdoor door** that is “home” in both directions:

1. **Exit from home interior** → chosen city’s outdoor door tile.
2. **Enter that outdoor door** → same home interior (Mom, grants, PC upstairs).

**Interior swap (preferred v1 strategy):** keep **one canonical player house interior** (`T20R0201` / Mom scripts) for all starts. The outdoor door in the chosen city warps into it. On exit, `set_dynamic_warp` returns to that door. The **displaced vanilla house** (the one we repurposed as “home” in that city) becomes what New Bark’s player-house door leads into when the player did **not** start in New Bark — so walking into the old New Bark house does not dump the player into Mom’s cutscene by mistake.

Exact door/interior pairs are documented in `documentation/HACK-NOTES.md` (pret zone_event recon). Final house picks TBD after in-game walk-through.

## Starter selection

**Status: DECIDED (prototype scope locked for v1 testing)**

Long-term options (any non-legendary, curated pools, location-specific pools) remain open. **v1 prototype:**

| Index | Species |
|------:|---------|
| 0–2 | Chikorita, Cyndaquil, Totodile |
| 3–5 | Bulbasaur, Charmander, Squirtle |

Six choices total; stored in `VAR_PLAYER_STARTER` (existing). `src/starters.c` must be extended from 3 → 6 slots.

## Intro timing (v1)

**Status: DECIDED (prototype)**

Selection flow runs **after Professor Oak / name / gender**, **before** the player ends up in their bedroom:

1. City picker (3 options)
2. Starter picker (6 options)
3. Grant starter to party
4. Spawn in **player house 2F (bedroom)** regardless of chosen city — player walks downstairs and Mom’s cutscene runs (menu unlocks, Pass, Pokédex, etc.). Non–New Bark cities use the house-swap / dynamic-warp wiring so the same upstairs→downstairs flow works from the chosen city’s house door.

**Open test:** whether the Pokémon menu unlocks correctly when the party already has a starter before Mom’s cutscene — may need an explicit flag if vanilla gating assumes Elm’s lab.

Story beats that assume a New Bark → Cherrygrove/Violet opening are removed — see [§35](#35-story-and-script-content).

---

# 5. Gyms and Badges

**Status: DECIDED**

All 16 Johto and Kanto Gyms can be challenged in any order.

All 16 badges are required to access Victory Road / the Pokémon League.

Gym difficulty scales according to the player's current badge count.

Therefore, the same Gym Leader represents a different challenge depending on whether they are fought as the player's:

- first Gym;
- fifth Gym;
- tenth Gym;
- sixteenth Gym;
- etc.

This scaling may affect:

- Pokémon levels;
- available Pokémon pool;
- battle size;
- moves;
- held items;
- AI;
- other battle parameters.

Exact scaling rules remain subject to balancing.

## Progression priority

**Badge-scaled Gyms and general trainer scaling should be prototyped before badge-based level caps are enabled.** Without scaled opposition, alternate starting cities go from very difficult to impossible; level caps alone would punish players without fixing what they fight.

Trainer scaling (§§8–9) and Gym scaling (§6) are prerequisites for fair starting-city selection (§4) and for level caps (§7).

---

# 6. Gym Leader Rosters

**Status: DECIDED, implementation details TBD**

Gym Leader battles use the same general dynamic-roster battle system as other trainer battles.

Gym Leaders do NOT necessarily have one predetermined fixed party.

Their available Pokémon can be dynamically generated or selected according to:

- Gym identity;
- type;
- badge tier;
- battle size;
- balance requirements.

Gym Leaders are **monotype by default**, but this is not an absolute restriction.

Thematically appropriate exceptions are allowed for characterization (see [§9 Phase 6](#phase-6--gym-trainers-and-gym-leaders) for the generation rule: at least one type must match the Gym).

Examples:

- Jasmine may use Ampharos despite it not being Steel-type.
- Brock could potentially use a thematically appropriate non-Rock Pokémon such as Ninetales.

These should be deliberate characterization/design decisions rather than random violations of the Gym's identity.

## Scaling (badge tier)

Gym battles use the same badge-tier ladder as ordinary trainers ([§7](#7-badge-based-level-caps), [§9](#9-trainer-generation)).

- **Gym trainers** (inside the Gym): levels in the current band (`floor`–`ceiling`); every Pokémon must have **at least one type matching the Gym**.
- **Gym Leaders:** same type rule; **every Pokémon is exactly at level cap** (not a random level in the band).

Rematches use the player's **current** badge tier and cap, not the tier at first defeat.

## Rematches

**Status: DECIDED**

Gym Leaders can be rematched.

Rematches use the player's **current badge tier**, rather than repeating the difficulty at which the Gym was originally defeated.

Gym rematches are also a renewable source of that Gym's TM.

There is no intended hard limit on the number of rematches/TM copies.

---

# 7. Badge-Based Level Caps

**Status: DECIDED**

Pokémon levels are capped according to the player's badge progression.

The purpose is not merely difficulty control.

Level caps are fundamental to the collection-oriented progression system.

Once the player's primary Pokémon reach the current cap, additional experience naturally encourages the player to develop more Pokémon rather than continuously overlevelling a small permanent party.

## Level cap curve

**+4 levels per badge earned**, starting at **10** before the first Gym:

| Badges earned | Level cap |
|---:|---:|
| 0 | 10 |
| 1 | 14 |
| 2 | 18 |
| 3 | 22 |
| … | … (+4 each) |
| 15 | 70 |
| 16 | 80 |

Formula (badges 0–15): **`cap = 10 + 4 × badges_earned`**

- **0 badges → cap 10** (before first Gym).
- **3 badges → cap 22** (example checkpoint).
- **15 badges → cap 70** (before the sixteenth Gym / Victory Road band).
- **All 16 badges → cap 80** (Victory Road and Elite Four). This is a **+10 jump** from the +4-per-badge ladder, not another +4 step.
- **Champion → cap removed** (postgame progression toward Level 100).

### Player cap vs trainer levels

These ladders are **not the same thing**:

- **Player level cap** — badge ladder above, then **uncapped after Champion** (toward 100 in postgame). Champion status is a **player-only** unlock; it does not raise the badge-tier formula.
- **Ordinary trainer scaling** — badge band from [§9](#9-trainer-generation); **hard ceiling 80** even if the player is Champion. Route trainers, Gym trainers, and rematches should not creep past 80 without an explicit exception.

**Special trainers** (scripted bosses, postgame fights) may override the band. Candidates need a curated list — not badge-tier random levels.

| Trainer / fight | Level policy (TBD) |
|---|---|
| Elite Four / Champion (first clear) | Likely fixed or band tied to 16-badge tier (76–80 / cap 80) — **TBD** |
| **Red** (Mt. Silver / equivalent) | Full party **~100**; Pikachu intentionally **buffed** (target **100**, stretch goal **120** if engine allows) |
| Other postgame rematches | Default **≤80** unless flagged special |

Red and similar fights are **design exceptions**, not extensions of `10 + 4n`. Implementation: trainer ID whitelist, script flag, or dedicated battle setup — **TBD** (no code until designed).

Victory Road and the Elite Four therefore operate within the level 70–80 endgame band (trainer/Gym scaling may use the full band; player cap is 80 until Champion).

## Rare Candies and power spikes

**Status: DECIDED**

When level caps are enabled, **Rare Candies are not subject to the badge level cap** — they may raise a Pokémon **above** the current cap. Normal EXP (wild, trainer, EXP Share) still stops at the cap.

**Implementation:** enable **`UNCAP_CANDIES_FROM_LEVEL_CAP`** alongside **`IMPLEMENT_LEVEL_CAP`** in `include/config.h`. Optionally **`ALLOW_LEVEL_CAP_EVOLVE`** so a Rare Candy on a capped Pokémon can still trigger a natural level-up evolution when the new level meets that evolution’s threshold.

**Design intent:**

- Candies are the **deliberate exception** to the cap, not a loophole on every mon at once — each use is a consumable choice.
- Creates meaningful timing decisions: hoard Rare Candies for a hard Gym Leader, rival, or special trainer; spike one ace for a single fight to get an evolution or move early. 6 badges (34 level cap), 2 rare candies for early lv36 Typhlosion
- Power spikes from candies should feel **earned and spent**, not a substitute for badge progression across the whole party.

The hg-engine hook **`IMPLEMENT_LEVEL_CAP`** exists in `include/config.h` but remains disabled until trainer/Gym scaling is prototyped (see [Implementation order](#implementation-order)).

## Implementation order

**Do not enable level caps until Gym and trainer scaling exists (or is prototyped).** Level caps encourage building a wider collection; they do not make late-game areas safe for a low-badge player who walks in from another starting city. Scaling trainer/Gym levels and teams by badge tier must come first.

---

# 8. Living Trainers

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

# 9. Trainer Generation

**Status: DECIDED conceptually; phased implementation**

Ordinary trainer Pokémon will eventually be **generated** rather than relying on fixed vanilla teams. Implementation is deliberately staged — rescaling existing parties is the first milestone.

## Trainer level band (same badge ladder as §7)

When the player has **`n` badges earned**, their level cap is **`10 + 4n`** (max **70** while `n < 16`; **80** with all 16 badges).

**Ordinary trainers** draw Pokémon levels from the current **4-level band** ending at that cap:

| Badges earned | Player cap | Trainer level range |
|---:|---:|---|
| 0 | 10 | 6–10 |
| 1 | 14 | 10–14 |
| 2 | 18 | 14–18 |
| 3 | 22 | 18–22 |
| … | … | … |
| 15 | 70 | 66–70 |
| 16 | 80 | 76–80 |

Formula: **`floor = cap − 4`**, **`ceiling = cap`** (inclusive), using the cap for the player's current badge count.

**Trainer ceiling:** ordinary scaled trainers **never exceed level 80**, regardless of Champion status. Postgame badge-tier fights stay in the **76–80** band at 16 badges. Fights above 80 require a **special-trainer** flag ([§7 player cap vs trainer levels](#player-cap-vs-trainer-levels)).

Example: **3 badges** → cap **22** → ordinary trainer Pokémon at levels **18–22** (the band since the last +4 step).

**Gym Leaders** are an exception: all party Pokémon are at **level cap** exactly ([§6](#6-gym-leader-rosters)).

## Target behaviour (full system)

When a battle starts, the opponent's party is built for the player's current badge tier:

1. **Level** — ordinary trainers: each Pokémon in the current band (`floor`–`ceiling`). Gym Leaders: **all at cap** (§6).
2. **Species (later phases)** — Phases 3–4 below. Stone and trade evolutions are **excluded for now** (Phase 5).
3. **Moves (Phase 2)** — last **four level-up moves** the species would know at its assigned level (same rule as wild Pokémon). No bespoke move sets yet.
4. **Held items** — **none for now** (roadmap).
5. **TMs** — **none for now** (roadmap).
6. **Gym type filter (Phase 6)** — every Pokémon on **Gym trainers and Gym Leaders** must have **at least one type matching the Gym** (§6).

Longer term, a trainer may own a generated collection larger than battle size (§12 dynamic rosters), with on-demand generation and optional counter-picking — unchanged from prior design intent.

## Implementation phases

Work in order. Do not skip ahead unless a phase is blocked and the spike is explicitly scoped.

### Phase 1 — Rescale vanilla teams *(start here)*

On trainer battle start: read badge count, compute `floor`/`ceiling`, **keep the trainer's existing species and party size**, only **remap levels** into the band (e.g. uniform random per slot, or proportional offset — pick one and document in code).

No random species, no move changes, no items. This alone makes open-world travel viable.

**Exit criterion:** same Youngster on Route 30 fights at ~6–10 with 0 badges and ~18–22 with 3 badges; species unchanged.

**Implementation note (Phase 1):** `TRAINER_LEVEL_SCALING` in `include/config.h` — `MakeTrainerPokemonParty()` in `src/field/enemy_party.c`. Uses badge count only; **does not** apply Champion uncap to trainers (max band 80 at 16 badges). Special-trainer overrides deferred.

### Phase 2 — Level-appropriate moves

After levels are set, assign **last four level-up moves** at that level (wild-mon logic). Still fixed or rescaled species from vanilla data.

**Implementation note (Phase 2):** `TRAINER_LEVEL_APPROPRIATE_MOVES` in `include/config.h` — skips NARC move sets, calls `InitBoxMonMoveset()` after `ChangeToBattleForm` in `MakeTrainerPokemonParty()`.

### Phase 3 — Downgrade / upgrade (same species)

Keep the trainer's **vanilla species identity** (or current party slot species), but adjust **evolution stage** so the form is legal at the assigned level:

- **Downgrade** when the natural line evolves above `ceiling` (e.g. Dragonite at cap 22 → Dratini or Dragonair).
- **Upgrade** when a lower stage is below the intended level and a higher stage is legal (e.g. Pidgey at level 18 → Pidgeotto if cap allows).

Still no random species swap. Stone/trade lines remain excluded until Phase 5 (only `EVO_LEVEL` edges are used).

**Stage rule:** walk the full level-up chain from base using forward tables generated from `Evolutions.c`. Pick the stage whose **level window** contains the scaled level (min stage level through next evolution level − 1). Example: Dratini line (30 / 55) at **L22 → Dratini**, not Dragonair; Pidgey at **L18 → Pidgeotto**.

**Implementation note (Phase 3):** `TRAINER_SPECIES_STAGE_ADJUST` — build-time tables via `scripts/gen_level_up_evo_tables.py` → `src/field/level_up_evo_tables.c` (regenerated when `Evolutions.c` changes). Runtime: O(chain depth) array lookups, no NARC scans.

### Phase 4 — Randomize species

Replace party species with **random eligible species** from the available dex, then apply Phase 3 rules so the chosen stage fits the level band. Levels still from Phase 1 band (Leaders still at cap once Phase 6 is in scope).

### Phase 5 — Evolution exclusions (interim rules)

Trainers do not receive stone- or trade-evolution lines until player-side rules exist ([§25](#25-evolution-methods-trade--stones)). Document exceptions (e.g. allow level-only final evos only).

### Phase 6 — Gym trainers and Gym Leaders

Apply scaling to **in-Gym trainer battles** and **Gym Leader battles**, on top of whichever species phase is active (Phase 1 alone is enough for a first Gym prototype):

| Role | Level rule | Type rule |
|---|---|---|
| Gym trainer | `floor`–`ceiling` (same as routes) | ≥1 type matches Gym |
| Gym Leader | **all at level cap** | ≥1 type matches Gym |

Gym type matching applies to generated parties too (Phase 4 rolls from a Gym-type-filtered pool). Characterization exceptions (§6) remain manual/curated, not random off-type.

**Implementation note (Phase 6 — Gym Leader cap):** `TRAINER_GYM_LEADER_CAP_LEVEL` in `include/config.h` — `MakeTrainerPokemonParty()` in `src/field/enemy_party.c`. Detects Johto/Kanto Gym Leader trainer classes (`TRAINERCLASS_LEADER_*`); every party slot gets the badge cap exactly instead of a random level in the band. Gym trainer band + type filter still TBD.

### Phase 7 — Agreed battle size

Trainer battles use a **symmetrical, agreed roster size** ([§11](#11-core-trainer-battle-philosophy)): same number of active slots for both sides (2v2 through 6v6). Who proposes or accepts the size (trainer, badge tier, player, mix) remains **TBD**.

Phases 1–6 can keep vanilla party sizes until this lands. Exit criterion: a Route trainer and the player fight **3v3** (or chosen size) with roster-slot parity, still using fixed or generated parties from earlier phases.

### Phase 8 — Dynamic rosters

Replace “pick your party before battle” with **collection-as-bench** ([§12](#12-dynamic-battle-rosters)):

- battle starts with one send-out per side;
- each **new** Pokémon brought in consumes a roster slot until the agreed size is reached;
- then the roster **locks**; fainted mons still occupy slots.

**Depends on** universal PC / box access during trainer battles ([§14](#14-pc--collection-access)). Without that, Phase 8 is blocked.

### Phase 9 — Counter-picking

Opponents (and eventually AI) **respond to revealed player commitments** ([§13](#13-counter-picking-and-information)): unrevealed Pokémon may be generated or selected from a hidden pool when the trainer spends another slot. Strength of intentional counter-play remains **TBD** — should feel responsive, not omniscient.

Builds on Phase 4 (generated species) and Phase 8 (slot commitment). Early stub: fixed party order; full vision: on-demand counters from generated collection.

### Phase 10 — Held items

Assign held items to trainer Pokémon (roadmap; none in Phases 1–9).

### Phase 11 — TM moves

Allow TM moves on trainer movesets beyond level-up sets (roadmap).

### Phase 12 — Living trainers

Field population, movement, and map-level trainer generation ([§8](#8-living-trainers), [§10](#10-trainer-interactions)) — distinct from battle-start scaling; location-weighted distributions and non-battle interactions.

## Collection and counter-picking (design intent)

A trainer may have a generated collection larger than the number of Pokémon ultimately used in a battle.

For example:

> Trainer Maya owns 12 relevant Pokémon.
>
> The battle is 4v4.
>
> During the battle she dynamically commits up to four Pokémon from that collection.

However, persistent full collections are not mandatory until **Phase 8+**; on-demand generation for **Phase 9** counter-picks is an alternative.

Another possible implementation is to generate unrevealed Pokémon **on demand** as the trainer commits additional roster slots.

This would allow trainer AI/difficulty logic to generate an appropriate response to what the player has revealed.

How strongly generation should intentionally counter the player remains TBD.

The system should feel strategically responsive without feeling obviously omniscient or unfair.

---

# 10. Trainer Interactions

**Status: DECIDED conceptually**

Living trainers are not exclusively battle dispensers.

Potential interactions include:

### Pokémon location requests

A trainer may ask:

> "Do you know where I can find a Heracross?"

If the player has encountered the requested Pokémon in the wild, they can provide a known encounter location.

The trainer provides a reward.

Possible rewards include:

- items;
- money;
- another Pokémon's encounter information;
- TMs;
- other useful information.

### Encounter information

Trainers may tell the player where Pokémon they have not yet discovered can be found.

This creates a social/information economy around exploration.

### Pokémon trades

Some trainers request trades.

### Item trading

Trainers may buy or sell items.

### TMs

Some trainers provide renewable access to otherwise rare TMs.

### Gym advice

Trainers may provide information about nearby undefeated Gyms or their current scaled teams.

### Other quests

Additional lightweight interactions and quests can be added later.

---

# 11. Core Trainer-Battle Philosophy

**Status: DECIDED**

Trainer battles should be symmetrical wherever practical.

The goal is to avoid difficulty created by giving NPCs arbitrary privileges that the player does not have.

## Bag items

Bag items cannot be used during trainer battles.

This restriction applies to **both sides**.

Held items remain legal.

## Battle size

Trainer battles use an agreed number of Pokémon.

Examples:

- 2v2
- 3v3
- 4v4
- 5v5
- 6v6

Exactly who determines battle size is:

**TBD**

Possibilities include:

- trainer preference;
- badge progression;
- encounter type;
- player choice;
- some combination.

---

# 12. Dynamic Battle Rosters

**Status: CORE FEATURE / DECIDED**

Trainer battles do NOT begin by selecting a fixed team.

Instead:

> **Each trainer's entire collection is their bench. The actual battle roster forms dynamically as Pokémon are revealed.**

Suppose a battle is 4v4.

The player does not choose four Pokémon before battle.

They initially choose one Pokémon to send out.

The opponent does the same.

Whenever the player would normally be allowed to send out or switch Pokémon, they may select:

1. a Pokémon already committed to this battle; or
2. an unused Pokémon from their entire collection.

The first time a unique Pokémon enters the battle, that Pokémon permanently consumes one of the player's roster slots.

In a 4v4:

- first unique Pokémon = slot 1;
- second unique Pokémon = slot 2;
- third unique Pokémon = slot 3;
- fourth unique Pokémon = slot 4.

After four unique Pokémon have entered:

> **The roster is locked.**

The player may continue switching among those Pokémon, but cannot introduce a fifth.

Fainted Pokémon continue to occupy their roster slots.

The opponent follows the same rules.

---

# 13. Counter-Picking and Information

**Status: DECIDED / INTENTIONAL**

Dynamic counter-picking is an intentional part of the battle system.

The player does not know the opponent's complete available collection.

The opponent does not initially know which Pokémon the player will commit.

If an opponent reveals Gyarados, the player may respond by introducing an Electric Pokémon.

However, doing so permanently spends another roster slot.

The opponent can then respond to the newly revealed Electric Pokémon, but doing so may require committing another one of their own limited slots.

Therefore:

> **Revealing a counter is both an advantage and a commitment.**

This creates an information-management/drafting layer inside normal Pokémon battles.

NPC AI should eventually understand this concept rather than simply selecting Pokémon independently.

---

# 14. PC / Collection Access

**Status: DECIDED**

The player's Pokémon storage is accessible anywhere.

This includes:

- overworld;
- trainer battles;
- wild battles.

There is no requirement to physically visit a Pokémon Center PC to reorganize the player's collection.

## Trainer battles

The full collection serves as the player's dynamic battle bench.

## Wild battles

PC access remains available during wild encounters as well.

Exact wild-battle UI/selection behaviour is a technical design problem to investigate.

---

# 15. Field Party vs Full Collection

**Status: DECIDED conceptually**

The six-member field party remains meaningful even though the player's collection is universally accessible.

## Field Party

The six field Pokémon:

- determine the player's following Pokémon;
- receive unused trainer-battle EXP slots;
- can be prioritized for overworld presentation/mechanics;
- provide convenient default Pokémon ordering.

## Full Collection

The entire collection:

- is accessible anywhere;
- can be accessed during battle;
- serves as the trainer-battle bench;
- can satisfy HM field requirements;
- allows the game to encourage development of significantly more than six Pokémon.

A major design goal is:

> **The player's collection is their team.**

---

# 16. EXP Share

**Status: DECIDED conceptually; numerical formula TBD**

EXP Share is tied to the **battle's Pokémon limit**.

For example:

A 4v4 trainer battle provides up to **four EXP recipient slots**.

Pokémon that actually participated in the battle receive priority.

If fewer than four Pokémon participated, unused recipient slots are filled by eligible Pokémon from the player's field party in party order.

Example:

A 4v4 battle occurs.

The player only uses:

- Typhlosion
- Ampharos

Two additional eligible field-party Pokémon receive EXP.

Therefore four Pokémon receive EXP.

## Level-capped Pokémon

Pokémon already at the current badge level cap are skipped as EXP recipients.

EXP that would otherwise be assigned to capped Pokémon should not simply make level-cap management annoying.

Exact redistribution behaviour is part of the configurable EXP formula.

## Fainted Pokémon

**DECIDED:**

Fainted Pokémon receive **no EXP**.

**TBD:**

Whether the EXP share that would have gone to a fainted Pokémon:

- disappears; or
- is redistributed among remaining eligible recipients.

## EXP amount

**TBD / MUST BE BALANCEABLE**

The exact EXP amount awarded to each recipient has NOT been finalized.

The system should be configurable so that we can tune:

- total EXP generation;
- recipient scaling;
- splitting;
- redistribution;
- badge progression pacing.

Do not hard-code an assumed EXP formula unnecessarily.

---

# 17. Healing and Attrition

**Status: DECIDED**

Traditional long-term HP/PP attrition is intentionally removed.

The design principle is:

> **Every battle should begin with the player's Pokémon ready to fight.**

After every battle, including wild battles:

- HP is restored;
- PP is restored;
- status conditions are removed.

Newly caught Pokémon are also immediately restored and battle-ready.

The game should therefore balance difficulty around **individual encounters**, not around gradually exhausting the player's resources over a route.

This is a significant intentional departure from vanilla Pokémon.

---

# 18. Pokémon Centers

**Status: DECIDED direction; exact services expandable**

Because healing is automatic and PC access is universal, Pokémon Centers no longer need to function primarily as healing/PC locations.

They instead become **trainer service hubs**.

Potential/current services include:

### Abra transportation

A trainer/Abra service can transport the player to other locations for a fee.

### Resting

The player can rest to intentionally advance the accelerated in-game clock.

### Apricorn crafting

If the [`DESIGN2.md`](DESIGN2.md) addon is implemented, Pokémon Centers may provide distributed Apricorn Ball crafting. **Not core scope.**

### Additional services

Other useful trainer services can be added as systems develop.

---

# 19. World Transportation

**Status: DECIDED conceptually**

Most traditional story roadblocks should be removed ([§35](#35-story-and-script-content)).

Transportation systems should allow broad world traversal from early in the game.

These include:

- trains;
- ferries;
- Fly;
- Abra transportation;
- local paid route bypasses where required.

## Cross-region Fly

Fly works across Johto and Kanto.

## Abra fast travel

Pokémon Centers may contain an Abra transportation service.

Travel likely costs money.

Exact destinations/costs remain TBD.

---

# 20. Routes and Content Gating

**Status: DECIDED**

Cities should generally remain accessible regardless of badge count.

Dangerous content can be restricted.

Examples:

- grass patches;
- caves;
- dungeon floors;
- optional routes;
- special areas.

Gating methods include:

- guards;
- doors;
- HM requirements;
- badge checks;
- terrain;
- alternate paths;
- encounter-tile checks.

Some routes may contain both low-progression and high-progression encounter areas simultaneously.

Where guards would feel heavy-handed, encounter-tile gating is a lighter option: the player can traverse the route freely, but stepping into grass, caves, or other encounter areas above their current progression level triggers a block and a short message (e.g. *"The wild Pokémon here seem dangerous. You shouldn't enter yet."*). Path tiles remain walkable; only the encounter tiles themselves are restricted.

Where geography makes a dangerous route mandatory for reaching another city, the player should have an alternative transportation option.

## Proof of concept (implemented)

**Route 29 → Route 46 gatehouse** — walk-past coord gate requiring **2 badges** (Zephyr + Hive). See `documentation/HACK-NOTES.md` § Route 46 gate. Template for guard-style gating; broader encounter-tile gating remains TBD.

---

# 21. HMs and Field Moves

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

Therefore:

> **Field utility does not consume a battle moveslot.**

## Inventory of field abilities (for design decisions)

Vanilla HGSS exposes these from the party menu. Not all are HMs. Decide for each: badge-gated collection field use, remains learn-the-move, removed, always available, or other.

### Official HMs (HM01–HM08)

| Item | Move | Typical field role |
|------|------|--------------------|
| HM01 | Cut | Remove small trees / grass obstacles |
| HM02 | Fly | Fast travel between visited cities |
| HM03 | Surf | Traverse water; water encounters |
| HM04 | Strength | Push boulders |
| HM05 | Whirlpool | Clear whirlpools on water routes |
| HM06 | Rock Smash | Break rocks; can trigger Rock Smash encounters |
| HM07 | Waterfall | Climb waterfalls |
| HM08 | Rock Climb | Climb rocky walls |

### Other party-menu field moves (not HMs)

| Move | Typical field role | Notes |
|------|--------------------|-------|
| Flash | Light dark caves | TM70 in HGSS, not an HM |
| Headbutt | Shake trees for encounters | Tutor move; **separate encounter tables** (`data/Headbutt.c`), not the grass table |
| Sweet Scent | Force a wild encounter | Useful with open-world encounter design |
| Dig | Escape to previous entrance in caves/dungeons | Escape utility |
| Teleport | Return to last Pokémon Center / healing point | Escape/travel utility |

### Related encounter / traversal systems (not party “field moves,” but same design bucket)

| System | Role | Notes |
|--------|------|-------|
| Rock Smash encounters | Wild mons from smashing rocks | Own slots in `EncounterData` (2 slots) |
| Surf / fishing encounters | Water wilds | Own tables per map; **Rod tier** gates which species appear — see [§22](#22-fishing-rod-progression) |
| Headbutt trees | Wild mons from trees | Own data files; good candidate for gated/high-value encounters |
| Cut trees / smashable rocks / Strength boulders | Map obstacles | Script/map event gated today by badge + knowing the move; **Cut trees blocking Gym access** — Surge/Erika **removed** ([§35](#35-story-and-script-content), `HACK-NOTES.md`) |
| Whirlpool / Waterfall / Rock Climb tiles | Traversal gates | Same |
| Fishing Rods (Old / Good / Super) | Tiered fishing encounters | **Not badge-gated** — see [§22](#22-fishing-rod-progression) |

### Design questions to resolve

- Which of the eight HMs unlock at which **badge count**?
- Does **Flash** follow the same collection-field rules as HMs, or stay “know the move”?
- Is **Headbutt** always available once obtained, badge-gated, or species-collection like HMs?
- Keep **Sweet Scent / Dig / Teleport** as learn-move field tools, convert to collection tools, or remove once auto-heal / transport exist?
- Should **Headbutt** / **Rock Smash** encounter pools be used as early vs gated content tiers (similar to grass gating ideas)?

Mark decisions here as they are made; do not invent unlock order without explicit design.

---

# 22. Fishing Rod Progression

**Status: DECIDED**

Fishing Rod progression is based on the player's experience **catching Water-type Pokémon**, not badge count or geographic progression. This is a **separate progression track** from [§21](#21-hms-and-field-moves) HM unlocks.

The historical Fishing Guru / Fishing Brother NPCs across Johto and Kanto should share the same progression. The player may return to **any one of them** for later Rod upgrades; progression does not require visiting the vanilla Rod locations in order.

- **Old Rod** — given freely on first interaction.
- **Good Rod** — awarded after catching Pokémon from **5 unique Water-type evolutionary families**.
- **Super Rod** — awarded after catching Pokémon from **15 unique Water-type evolutionary families**.

## Counting rules

- Count **evolutionary families**, not individual species.
- Catching multiple members of the same evolutionary family counts only once.
  - Example: catching Poliwag, Poliwhirl and Poliwrath still counts as **1 family**.
- A family qualifies if the player has caught at least one member that is **Water-type**.
- Either primary or secondary Water typing qualifies.
- Use Pokédex caught data rather than the player's current collection, so traded away or released Pokémon still count.
- Branching evolutions remain a single family.
- The progression should be shared globally between all Fishing Guru / Fishing Brother NPCs.

This creates a self-contained fishing progression loop:

**Old Rod → catch 5 Water families → Good Rod → access more fishing encounters → catch 15 Water families → Super Rod**

## Fishing Guru locations

**Target:** a **network** of interchangeable Fishing Guru / Fishing Brother NPCs spread across Johto and Kanto so the player is never far from the next Rod tier — any one of them can award whichever Rod is next.

**Vanilla HGSS caveat:** HeartGold/SoulSilver does **not** mirror every historical Gen I–IV Rod-giver city. Confirmed or typical vanilla hooks include **Route 32** (Old Rod) and **Route 12 / Silence Bridge** (Super Rod); **Olivine** has a fishing NPC. **Vermilion and Fuchsia do not have Rod givers in vanilla HGSS** — if we want them on the network, we must **add new NPCs** (zone_event object + scr_seq + text).

**Distribution goal:** avoid clustering every guru in mid-Johto / south Kanto. Where practical, place gurus at:

| Region | Location | Notes |
|--------|----------|--------|
| South Johto | Route 32 Pokémon Center | Vanilla Old Rod area |
| West Johto (coast) | Olivine City | Vanilla fishing NPC |
| East Johto | **Blackthorn City** | **Likely new NPC** — gives Blackthorn a way to farm at lv5 since all connected routes are too high level |
| West Kanto | **Viridian City or Pewter City** | **Likely new NPC** |
| Mid Kanto (coast) | Vermilion City | **Likely new NPC** (not vanilla Rod giver) |
| South Kanto | Fuchsia City | **Likely new NPC** (not vanilla Rod giver) |
| East Kanto | Route 12 / Silence Bridge | Vanilla Super Rod area |

Exact map and `(x, z)` per guru are implementation details; prefer towns the player already visits for other reasons (Mart, Gym, ferry) over dead-end-only cells.

Any guru on this network reads the same global fishing-progression state and offers the appropriate Rod (Old on first talk, then Good / Super when family counts are met).

---

# 23. TMs

**Status: DECIDED**

TMs remain **consumable**.

However:

> **No TM is permanently finite.**

This preserves the decision of spending a TM without creating the classic problem where players hoard their only copy forever.

Different TMs have different renewable sources.

## Common TMs

Available from shops, especially major shopping locations such as:

- Goldenrod;
- Celadon.

## Game Corner TMs

Some TMs remain Game Corner rewards.

## Rare / overworld TMs

Rare TMs that would traditionally exist as one overworld copy can also become obtainable through living-trainer interactions.

## Gym TMs

The first Gym victory awards the Gym's TM.

Rematching that Gym Leader at the player's current badge tier awards another copy.

Gym TM farming is intentionally unlimited.

---

# 24. Accelerated Day/Night Cycle

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
- potentially other systems (including Apricorn refresh if [`DESIGN2.md`](DESIGN2.md) is implemented);

## Time advancement

The player should be able to deliberately advance time rather than waiting.

Likely mechanisms include both:

### Resting at Pokémon Centers / hotels

Allows controlled advancement of time.

### Portable resting

A tent, sleeping bag, camping system, or similar mechanic can potentially allow resting outside towns.

Exact implementation remains TBD.

---

# 25. Evolution Methods (Trade & Stones)

**Status: PARTIALLY DECIDED — stone expansion OPTIONAL / TBD**

QoL changes to trade and stone evolution. **Not required** for the core open-world shell or trainer scaling; can ship on its own schedule. Placed before the Apricorn addon pointer because both touch items, but this section is **core Design 1**, not [`DESIGN2.md`](DESIGN2.md).

## Trade evolutions — with held item

Evolutions that normally require **trade while holding an item** should evolve when the item is **used on the Pokémon** — no trade required.

Examples: Dragon Scale → Kingdra, Metal Coat → Scizor, Protector → Rhyperior, etc.

## Trade evolutions — no item

Evolutions that require **trade alone** need a substitute for multiplayer. **TBD — pick one (or combine):**

### Option A: Link Cable item

Add a **Link Cable** usable item that triggers the same evolution as trade (inventory convenience, no level gate).

### Option B: Level-up evolution

| Pokémon | Evolves at |
|---|---:|
| Graveler → Golem | 38 |
| Machoke → Machamp | 38 |
| Kadabra → Alakazam | 42 |
| Haunter → Gengar | 42 |

Other trade-only lines (e.g. Phantump, Pumpkaboo if in scope) need explicit rules when implemented.

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

| Stage pattern | Stone | Level without stone |
|---|---|---:|
| 1st stage, stone-only (e.g. Exeggcute, Growlithe) | matching stone at any level | **35** |
| 2nd stage, stone-only (e.g. Gloom, Poliwhirl) | matching stone at any level | **50** |

### Open questions (stones)

- Exact −5 behaviour: one-time per stage, permanent flag, or repeatable?
- Dual-types: either type matches, or primary type only?
- Using a stone on a Pokémon with no evolution in that line — no effect?
- Interaction with [`§9`](#9-trainer-generation) Phase 5 (trainers exclude trade/stone lines until policy exists).

---

# 26. Apricorn Economy & Poké Balls (addon)

**Status: ADDON — see [`DESIGN2.md`](DESIGN2.md)**

Apricorn tree refresh, shop ball rebalance, removed balls, and all Apricorn ball formulas live in the addon design doc. **Not core to the open-world ROM** — vanilla shop balls remain until that addon is deliberately scheduled.

Core touchpoints only:

- Accelerated clock ([§24](#24-accelerated-daynight-cycle)) — shared with addon tree refresh if implemented later.
- Auto-heal on capture ([§17](#17-healing-and-attrition)) — rationale for removing Heal Ball in the addon doc.
- Mom's open-world Apricorn Box (`OPENWORLD_STARTING_ITEMS`) — inventory convenience only, not the full rebalance.

Do not implement ball changes from DESIGN2 unless explicitly requested.

---

# 27. Wild Encounters

**Status: PARTIALLY DECIDED**

Wild encounters need to support open-world progression.

Encounter design should ensure that every viable starting city provides useful low-level Pokémon.

Different sections of the same route may support different progression tiers.

Badge-gated grass or dungeon areas can contain stronger encounters while leaving the overall geography traversable.

**Guard-style gating** has one proof of concept (Route 29→46, §20). **Trainer and Gym scaling by badge tier should land before broad encounter-table work or level caps** — otherwise starting-city balance depends entirely on static vanilla tables.

Exact encounter-scaling philosophy remains to be designed.

Questions still include:

- Are individual wild Pokémon levels scaled?
- Are encounter tables changed according to badge tier?
- Are different physical grass patches used for different tiers?
- How much stronger content should simply remain inaccessible until later?

These should not be assumed without explicit design work.

---

# 28. Pokémon Generations / Content Scope

**Status: TBD / TECHNICAL INVESTIGATION**

The final set of supported Pokémon generations has not been decided.

The project is based on HG-Engine, which supports a number of mechanics, Pokémon/forms, moves, abilities and other features beyond vanilla Generation IV.

Do NOT currently assume:

- Gen I–II only;
- Gen I–IV only;
- Gen I–VI;
- Gen I–IX;
- any other exact cutoff.

The available HG-Engine capabilities should be investigated before making this decision.

The project is open to later-generation Pokémon and mechanics where they work well with the game.

This decision affects:

- encounters;
- starters;
- evolutions;
- Gym pools;
- trainer generation;
- friendship evolution families;
- types;
- abilities;
- moves;
- items;
- legendaries;
- postgame content.

---

# 29. Design Principles

When evaluating future ideas, prefer designs that support these principles.

## The collection is the player's team

Traditional Pokémon heavily incentivizes maintaining approximately six permanent Pokémon.

Wandering Heart should encourage catching, training and actually using a much larger collection.

Dynamic rosters, level caps, EXP Share and universal PC access all support this goal.

## Individual battles matter more than attrition

Automatic restoration means challenge should come from strategically interesting battles rather than arriving at the end of a cave with no PP.

## Symmetry where practical

Trainer battles should generally operate under rules shared by both sides.

Examples:

- equal roster limits;
- no bag items;
- dynamic roster commitment;
- counter-picking.

## Open travel does not require flat difficulty

The player should be free to move through the world while still encountering areas they are not ready to challenge.

## Reduce chores, preserve decisions

Remove mechanics that mostly create repetitive work while preserving mechanics that create interesting choices.

Examples:

**Remove/reduce:**
- repeated Pokémon Center healing;
- returning to PCs;
- HM slaves;
- permanently finite TMs.

(Vanilla Apricorn waiting and ball rebalance chores: [`DESIGN2.md`](DESIGN2.md) addon only.)

**Preserve/enhance:**
- choosing which TM to spend now;
- selecting the right Poké Ball (vanilla until addon);
- deciding which Pokémon to commit during battle;
- choosing where to explore;
- choosing which Gym to challenge;
- building a diverse collection.

## Avoid invisible scaling where physical world design works better

Where practical, use:

- gated grass;
- alternate paths;
- dungeon floors;
- badge-access areas;
- trainer progression;
- world geography

rather than making every Pokémon and encounter magically scale directly to the player.

This principle is not absolute; implementation and balance may require scaling systems.

---

# 30. Major Technical Investigations

The following designs should receive dedicated technical investigation before implementation.

## Dynamic battle rosters

Questions include:

- accessing boxed Pokémon from battle;
- introducing a boxed Pokémon into an active battle;
- tracking committed roster slots;
- dynamically generated opponent collections;
- opponent counter-picking AI;
- wild-battle PC access;
- battle UI.

## Living trainers

Questions include:

- map spawning;
- movement;
- persistence;
- generated identities;
- badge counts;
- generated collections;
- trainer interactions;
- map transitions;
- save-state requirements.

## Open-world encounter structure

Questions include:

- encounter-table modification;
- badge-conditioned encounter tables;
- grass-tile-specific encounter sets;
- map scripting;
- guards (PoC: Route 29→46);
- doors;
- HM gates.

## Badge-scaled Gyms and trainers

**Priority investigation** — should precede level caps and broad starting-city rollout.

**Phase 1 target:** hook trainer battle start → badge count → level band → rescale existing party levels ([§9 Phase 1](#phase-1--rescale-vanilla-teams-start-here)).

**Phase 6 target:** Gym trainers (band + type filter); Gym Leaders (cap + type filter).

**Phases 7–9 target:** symmetrical battle size → dynamic rosters (requires §14 PC) → counter-picking AI / hidden pools.

Questions include:

- where hg-engine assembles the trainer party at battle start;
- reading badge count from battle code (field scripts already use `count_badges`);
- identifying current badge count;
- scaling wild-adjacent trainer levels and teams by badge tier;
- dynamic trainer generation (phases 2–5);
- dynamic Gym generation (Phase 6 type filter + Leader cap levels);
- agreed battle size rules (Phase 7);
- battle-time PC access and roster locking (Phase 8);
- counter-pick generation and AI strength (Phase 9);
- battle-size selection;
- rematches;
- TM rewards;
- monotype generation with curated exceptions;
- stone/trade evolution policy for generated teams.

## Universal PC

Questions include:

- overworld access;
- trainer battle access;
- wild battle access;
- interaction with party assumptions in vanilla HGSS.

## Automatic restoration

Questions include:

- correct hook after all battle outcomes;
- HP;
- PP;
- status;
- newly captured Pokémon.

## Accelerated clock

Questions include:

- replacing RTC dependencies;
- event compatibility;
- day/night rendering;
- encounter tables;
- evolutions;
- manual time advancement.

(Apricorn refresh: [`DESIGN2.md`](DESIGN2.md) addon.)

## HM progression

Questions include:

- decoupling field use from learned moves;
- checking eligible species across party + boxes;
- badge-count unlocks;
- existing scripts expecting specific badges/HMs.

---

# 31. Initial Development Philosophy

The project should NOT begin by attempting its most ambitious systems.

Early development should establish a reliable understanding of HG-Engine and HGSS.

Suggested progression:

1. Maintain a reliable Docker build.
2. Verify trivial data/text modifications.
3. Modify simple Pokémon/trainer/game data.
4. Create small scripting changes.
5. Investigate badge-count access from scripts/code.
6. Implement a simple badge-gated world interaction.
7. Prototype one small piece of a major system.
8. Expand only after the prototype is understood and stable.

The first implementation targets should preferably:

- produce obvious visible results;
- teach us something about HGSS/HG-Engine;
- be independently testable;
- avoid large architectural commitments.

---

# 32. Current Technical Baseline

As of August 2026:

### Build and toolchain

- HG-Engine builds reliably via **Docker** (`make -j24` → `test.nds`; DeSmuME verification).
- Field scripting workflow is established: **scr_seq**, **zone_event**, **text banks**, Python patch tools, and `narcs.mk` hooks.
- Map identity pitfalls are documented (`map header ≠ scr_seq member ≠ zone_event member`) in `documentation/HACK-NOTES.md`.

### Core battle / QoL (verified in-game)

| Feature | Toggle / hook | Design ref |
|---------|---------------|------------|
| Post-battle heal (HP/PP/status) | `HEAL_AFTER_BATTLE` | §17 |
| Full-party EXP share (interim) | `FULL_PARTY_EXP_SHARE` | §16 |

### Open-world shell (verified or implemented)

| Feature | Status | Notes |
|---------|--------|-------|
| Mom starting grants (Ticket, Pass, Apricorn Box, shoes, dex) | Verified | scr_seq **845**; `OPENWORLD_STARTING_ITEMS` |
| Magnet Train (Goldenrod ↔ Saffron) | Verified | No power-plant gate; scr_seq **893** / **834** |
| Route 42 paid ferry | Verified | Reference recipe for paid bypass NPCs |
| Route 4 ledge boost ($100 hiker) | Verified | `2_009` / `2_178`; coords (1270,118)→(1270,116) |
| Route 29→46 gate (2 badges) | PoC verified | Guard-style encounter gating template |
| Route 36 Sudowoodo removed | Verified | 0-badge Violet ↔ Goldenrod path |
| Route 32 badge gate removed | Verified | 0-badge path toward Union Cave |
| Mahogany rocket arc skipped | Verified | Town accessible on load; full Rocket removal per [§35](#35-story-and-script-content) |
| Surge / Erika Cut trees removed | Verified | `2_051`, `2_052`, `2_352`; `patch_zone_event_gym_cut_trees.py` — [§35](#35-story-and-script-content) |

Reusable recipes for badge gates, ferry NPCs, and story NPC removal live in **`documentation/HACK-NOTES.md`**.

### Story and script policy

See [§35](#35-story-and-script-content). Surge/Erika Cut trees verified; remaining gym rows (Bugsy, Jasmine, Clair, Misty, Blue) and rival arc still open.

### Not yet started (core design priorities)

- **Trainer scaling phase 1** — rescale vanilla trainer levels by badge band (§9).
- **Gym scaling phase 6** — Gym trainers + Leaders (type filter; Leaders at cap).
- **Battle systems phases 7–9** — agreed size, dynamic rosters, counter-picking (after scaling).
- Starting city selection (§4).
- Living trainers, dynamic rosters, universal PC, collection-based HMs.
- Level caps (`IMPLEMENT_LEVEL_CAP`) — after scaling prototype.
- Story implementation pass ([§35](#35-story-and-script-content)) — Surge/Erika Cut trees done; opening skip, Rocket, remaining gym rows.

The basic development loop is proven:

> **edit source/data → Docker build → test.nds → DeSmuME → verify**

Docker remains the known-good build path.

---

# 33. Open Design Questions

The following are intentionally unresolved.

- Exact starter system.
- Exact selectable starting cities.
- Who determines trainer battle size.
- Exact trainer generation algorithms.
- How aggressively NPCs counter-pick.
- Whether generated trainers have persistent full collections or generate unrevealed Pokémon on demand.
- Exact Gym roster generation.
- Exact EXP formula.
- Whether fainted Pokémon's lost EXP is redistributed.
- Exact wild encounter scaling/gating model.
- Exact HM progression order.
- Exact transportation prices.
- Exact Pokémon Center service list.
- Exact accelerated-time resting mechanics.
- Included Pokémon generations/content.
- Rival role ([§35](#35-story-and-script-content)).
- Clair Dragon's Den: remove trial vs HM-free path ([§35](#35-story-and-script-content)).
- Jasmine Lighthouse rewrite vs immediate availability ([§35](#35-story-and-script-content)).
- Trade evolutions without items: Link Cable vs fixed levels ([§25](#25-evolution-methods-trade--stones)).
- Whether expanded stone mechanics ([§25](#25-evolution-methods-trade--stones)) ship at all.
- Special-trainer roster (Red ~100 / Pikachu buff, E4 first-clear levels) vs badge-tier cap at 80 ([§7](#7-badge-based-level-caps)).

(Ball/Apricorn V2 questions: [`DESIGN2.md`](DESIGN2.md) §18. V3/V4 deferred scope also in DESIGN2.)

These questions should remain open until deliberately resolved.

---

# 34. Deferred Scope (V2–V4)

Features deliberately outside **core** scope are documented in [`DESIGN2.md`](DESIGN2.md):

- **V2** — Apricorn economy and Poké Ball rebalance
- **V3** — Full Moon world system and Moon Ball
- **V4** — Unlimited learned moves (anime-style move retention)

These should not influence initial core architecture unless doing so is inexpensive and clearly prevents future incompatibility.

---

# 35. Story and Script Content

**Status: DECIDED (rival arc TBD)**

Field scripts, NPCs, and map obstacles that assume vanilla story order or a New Bark start are removed or rewritten. Target: **any starting city**, **any-order Gyms**.

## Opening and tutorial — remove

- Elm errand, rival intro, Oak visit, Togepi egg, New Bark–specific Mom/house cutscenes
- Cherrygrove guide (Town Map, running shoes); Route 30 Apricorn Box NPC (covered by `OPENWORLD_STARTING_ITEMS` / Mom grants — [§32](#32-current-technical-baseline))

No replacement fetch quests at other cities unless optional flavour, not service gates.

## Team Rocket — remove

Rocket grunts, hideouts, Radio Tower arc, and related roadblocks must not gate travel, Gyms, or items. Mahogany post-clear on load is the verified pattern (`HACK-NOTES.md`); extend to Goldenrod basement, Radio Tower, etc.

## Rival — TBD

Role undecided (remove, optional encounters, badge-tier rematches, …). No rival story hooks until resolved.

## Gyms — access and story policy

**Rules (all Leaders):**

1. **City-local events only** — pre/post-battle flavour OK if it stays in the Gym town; cut anything that sends the player elsewhere and expects a return.
2. **No story-gated Gym approach** — no Cut/Surf/Strength/Whirlpool (or Rocket/badge-count) blocking the Gym door or Leader when HMs come from badge count ([§21](#21-hms-and-field-moves)). Route/danger gating ([§20](#20-routes-and-content-gating)) still applies outside Gym access.
3. **Internal Gym puzzles** — trash cans, maze, etc. stay unless they hard-require an HM.

### Required changes

| Leader | Change |
|--------|--------|
| **Bugsy** (Azalea) | Remove Team Rocket. |
| **Jasmine** (Olivine) | Secret Medicine in Olivine Poké Mart special clerk (¥500); `FLAG_GOT_SECRETPOTION` set when item enters bag. Cianwood pharmacy still works. |
| **Clair** (Blackthorn) | Drop 7-badge + Goldenrod Rocket gates. Drop or HM-free the Dragon's Den trial before the badge (Den currently needs Surf + Whirlpool). |
| **Misty** (Cerulean) | Drop Power Plant / Machine Part / Route 25 chain; Leader available in Gym without leaving town. |
| **Blue** (Viridian) | Drop “7 Kanto badges first” gate; challengeable at any badge tier. |

### Verified

| Leader | Notes |
|--------|--------|
| **Lt. Surge** (Vermilion) | Cut tree outside Gym removed (`2_051`); internal trash-can puzzle unchanged. |
| **Erika** (Celadon) | City tree (`2_052`) + three Gym maze trees (`2_352`) removed; Leader reachable without Cut. |
| **Pryce** (Mahogany) | Rocket skip on load (see above). |

Implementation: `tools/patch_zone_event_gym_cut_trees.py` — verified in-game Aug 2026.

### OK as-is (city-local or no external gate)

Falkner, Whitney, Morty (Burned Tower is Ecruteak-local), Chuck, Sabrina, Janine, Brock, Blaine (once Seafoam is reachable).

## Implementation

- Prefer flag-on-load and script skips over deleting assets (`HACK-NOTES.md` recipes).
- Starting-city selector ([§4](#4-starting-location)) must not depend on Elm/rival/New Bark flags.
- Gym obstacles are **zone_event** objects (e.g. Cut trees), not Blender map edits — patch `zone_event` / `scr_seq` like Route 36 Sudowoodo.

---

# 36. One-Sentence Game Identity

> **Pokémon Wandering Heart is an open-world HGSS journey where the player builds a collection rather than a fixed party, travels freely through Johto and Kanto, challenges all 16 scaling Gyms in any order, and encounters other trainers undertaking dynamic journeys of their own.**