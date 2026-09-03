# Pokémon Wandering Heart — Battles, Trainers & Progression

> Gyms, badges, level caps, battle systems, implementation phases, and QoL.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Vision:** `[DESIGN-VISION.md](DESIGN-VISION.md)` · **World:** `[DESIGN-WORLD.md](DESIGN-WORLD.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)`

# Battle-1. Gyms and Badges


**Status: DECIDED**

All 16 Johto and Kanto Gyms can be challenged in any order.

All 16 badges are required to access Victory Road / the Pokémon League.

Trainer Battles and Gym difficulty scales according to the player's current badge count.

This scaling may affect:

- Pokémon levels;
- available Pokémon pool;
- battle size;
- moves;
- held items;

---

---

# Battle-2. Healing and Attrition


**Status: IMPLEMENTED** — `HEAL_AFTER_BATTLE` in `include/config.h`; verified wild, trainer, flee, and catch ([Index-2](DESIGN.md#index-2-current-technical-baseline)).

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

---

# Battle-3. Core Trainer-Battle Philosophy


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

- 1v1
- 3v3
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

---

# Battle-4. Badge-Based Level Caps


**Status: DECIDED**

Pokémon levels are capped according to the player's badge progression.

The purpose is not merely difficulty control.

Level caps are fundamental to the collection-oriented progression system.

Once the player's primary Pokémon reach the current cap, additional experience naturally encourages the player to develop more Pokémon rather than continuously overlevelling a small permanent party.

## Level cap curve

**+4 levels per badge earned**, starting at **10** before the first Gym:


| Badges earned | Level cap   |
| ------------- | ----------- |
| 0             | 10          |
| 1             | 14          |
| 2             | 18          |
| 3             | 22          |
| …             | … (+4 each) |
| 15            | 70          |
| 16            | 80          |


Formula (badges 0–15): `cap = 10 + 4 × badges_earned`

- **0 badges → cap 10** (before first Gym).
- **3 badges → cap 22** (example checkpoint).
- **15 badges → cap 70** (before the sixteenth Gym / Victory Road band).
- **All 16 badges → cap 80** (Victory Road and Elite Four). This is a **+10 jump** from the +4-per-badge ladder, not another +4 step.
- **Champion → cap removed** (postgame progression toward Level 100).



### Player cap vs trainer levels

These ladders are **not the same thing**:

- **Player level cap** — badge ladder above, then **uncapped after Champion** (toward 100 in postgame). Champion status is a **player-only** unlock; it does not raise the badge-tier formula.
- **Ordinary trainer scaling** — badge band from [Battle-8](DESIGN-BATTLES.md#battle-8-implementation); **hard ceiling 80** even if the player is Champion. Route trainers, Gym trainers, and rematches should not creep past 80 without an explicit exception.

**Special trainers** (scripted bosses, postgame fights) may override the band. Candidates need a curated list — not badge-tier random levels.


| Trainer / fight                     | Level policy (TBD)                                                                                            |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Elite Four / Champion (first clear) | Likely fixed or band tied to 16-badge tier (76–80 / cap 80) — **TBD**                                         |
| **Red** (Mt. Silver / equivalent)   | Full party **~100**; Pikachu intentionally **buffed** (target **100**, stretch goal **120** if engine allows) |
| Other postgame rematches            | Default **≤80** unless flagged special                                                                        |


Red and similar fights are **design exceptions**, not extensions of `10 + 4n`. Implementation: trainer ID whitelist, script flag, or dedicated battle setup — **TBD** (no code until designed).

Victory Road and the Elite Four therefore operate within the level 70–80 endgame band (trainer/Gym scaling may use the full band; player cap is 80 until Champion).

## Rare Candies and power spikes

**Status: DECIDED**

When level caps are enabled, **Rare Candies are not subject to the badge level cap** — they may raise a Pokémon **above** the current cap. Normal EXP (wild, trainer, EXP Share) still stops at the cap.

**Implementation:** enable `UNCAP_CANDIES_FROM_LEVEL_CAP` alongside `IMPLEMENT_LEVEL_CAP` in `include/config.h`. 

**Design intent:**

- Candies are the **deliberate exception** to the cap, not a loophole on every mon at once — each use is a consumable choice.
- Creates meaningful timing decisions: hoard Rare Candies for a hard Gym Leader, rival, or special trainer; spike one ace for a single fight to get an evolution or move early. Example: 6 badges (34 level cap), 2 rare candies for early lv36 Typhlosion
- Power spikes from candies should feel **earned and spent**, not a substitute for badge progression across the whole party.

The hg-engine hook `IMPLEMENT_LEVEL_CAP` exists in `include/config.h` but likely does not do exactly what we need.

---

---

# Battle-5. Gym Rosters


**Status: DECIDED, implementation details TBD**

Gym Leader battles use the same general dynamic-roster battle system as other trainer battles; they do NOT have one predetermined fixed party.

Gyms (both trainers and leaders) are **monotype by default**, with some exceptions (listed below)

Blue remains flexible. 

Other exceptions:

- Jasmine Ampharos line
- Brock Vulpix line
- Whitney is changed to Fairy type but keeps her iconic Miltank
- Misty Togepi line
- Blaine Rhydon line

## Scaling (badge tier)

Gym battles use the same badge-tier ladder as ordinary trainers ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps), [Battle-8](DESIGN-BATTLES.md#battle-8-implementation)).

- **Gym trainers** (inside the Gym): levels in the current band (`floor`–`ceiling`)
- **Gym Leaders:** **every Pokémon is exactly at level cap** 

Rematches use the player's **current** badge tier and cap, not the tier at first defeat.

## Rematches

**Status: DECIDED**

Gym Leaders can be rematched.

Rematches use the player's **current badge tier**, rather than repeating the difficulty at which the Gym was originally defeated.

Gym rematches are also a renewable source of that Gym's TM ([World-8](DESIGN-WORLD.md#world-8-tms)).

There is no intended hard limit on the number of rematches/TM copies.

---

---

# Battle-6. Dynamic Battle Rosters


**Status: CORE FEATURE / DECIDED**

Trainer battles do **not** use a fixed pre-battle team. The player's **full collection** is the bench; roster slots commit dynamically as Pokémon enter. Counter-picking and information asymmetry are intentional. The six-member field party still matters for EXP overflow and presentation.

## Dynamic roster rules

Trainer battles do NOT use your party as a fixed team.

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

## Counter-picking and information

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

## PC / collection access

**Status: DECIDED**

The player's Pokémon storage is accessible anywhere.

This includes:

- overworld;
- trainer battles;
- wild battles.

There is no requirement to physically visit a Pokémon Center PC to reorganize the player's collection.

### Trainer battles

The full collection serves as the player's dynamic battle bench.

### Wild battles

PC access remains available during wild encounters as well.

Exact wild-battle UI/selection behaviour is a technical design problem to investigate.

## Field party vs full collection

**Status: DECIDED conceptually**

The six-member field party remains meaningful even though the player's collection is universally accessible.

### Field Party

The six field Pokémon:

- determine the player's following Pokémon;
- receive unused trainer-battle EXP slots ([Battle-7](DESIGN-BATTLES.md#battle-7-exp-share));
- can be prioritized for overworld presentation/mechanics;
- provide convenient default Pokémon ordering.



### Full Collection

The entire collection:

- is accessible anywhere;
- can be accessed during battle;
- serves as the trainer-battle bench;
- can satisfy HM field requirements ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves));
- allows the game to encourage development of significantly more than six Pokémon.

A major design goal is:

> **The player's collection is their team.**

---

---

# Battle-7. EXP Share


**Status: IMPLEMENTED (interim)** — `FULL_PARTY_EXP_SHARE` verified in-game. Final battle-limit EXP recipient formula still **TBD** below.

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

---

# Battle-8. Implementation


**Status: PARTIALLY IMPLEMENTED** — Phases **1–3** verified; **Phase 6** (Gym Leader level cap) verified; Phases 4–5, 7–12 not started. See [Index-2](DESIGN.md#index-2-current-technical-baseline).

## Trainer level band (same badge ladder as Battle-4)

When the player has `n` **badges earned**, their level cap is `10 + 4n` (max **70** while `n < 16`; **80** with all 16 badges).

**Ordinary trainers** draw Pokémon levels from the current **4-level band** ending at that cap:


| Badges earned | Player cap | Trainer level range             |
| ------------- | ---------- | ------------------------------- |
| 0             | 10         | 6–10                            |
| 1             | 14         | 10–14                           |
| 2             | 18         | 14–18                           |
| 3             | 22         | 18–22                           |
| …             | …          | …                               |
| 15            | 70         | 66–70                           |
| 16            | 80         | 70–75 regi;ar trainers 76-80 E4 |


Formula: `floor = cap − 4`, `ceiling = cap` (inclusive), using the cap for the player's current badge count.

**Trainer ceiling:** ordinary scaled trainers **never exceed level 80**, regardless of Champion status. Postgame badge-tier fights stay in the **70–80** band at 16 badges. Fights above 80 require a **special-trainer** flag ([Battle-4 player cap vs trainer levels](#player-cap-vs-trainer-levels)).

Example: **3 badges** → cap **22** → ordinary trainer Pokémon at levels **18–22** (the band since the last +4 step).

**Gym Leaders** are an exception: all party Pokémon are at **level cap** exactly ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).

## Target behaviour (full system)

When a battle starts, the opponent's party is built for the player's current badge tier:

1. **Level** — ordinary trainers: each Pokémon in the current band (`floor`–`ceiling`). Gym Leaders: **all at cap** (Battle-5).
2. **Species (later phases)** — Phases 3–4 below. Stone and trade evolutions are **excluded for now** (Phase 5).
3. **Moves (Phase 2)** — last **four level-up moves** the species would know at its assigned level (same rule as wild Pokémon). No bespoke move sets yet.
4. **Held items** — **none for now** (roadmap).
5. **TMs** — **none for now** (roadmap).
6. **Gym type filter (Phase 6)** — every Pokémon on **Gym trainers and Gym Leaders** must have **at least one type matching the Gym** (Battle-5).

Longer term, a trainer may own a generated collection larger than battle size ([Battle-6](DESIGN-BATTLES.md#battle-6-dynamic-battle-rosters) dynamic rosters), with on-demand generation and optional counter-picking — unchanged from prior design intent.

## Implementation phases

Work in order. Do not skip ahead unless a phase is blocked and the spike is explicitly scoped.

### Phase 1 — Rescale vanilla teams

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

Trainers do not receive stone- or trade-evolution lines until player-side rules exist ([World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones)). Document exceptions (e.g. allow level-only final evos only).

### Phase 6 — Gym trainers and Gym Leaders

Apply scaling to **in-Gym trainer battles** and **Gym Leader battles**, on top of whichever species phase is active (Phase 1 alone is enough for a first Gym prototype):


| Role        | Level rule                         | Type rule           |
| ----------- | ---------------------------------- | ------------------- |
| Gym trainer | `floor`–`ceiling` (same as routes) | ≥1 type matches Gym |
| Gym Leader  | **all at level cap**               | ≥1 type matches Gym |


Gym type matching applies to generated parties too (Phase 4 rolls from a Gym-type-filtered pool). Characterization exceptions (Battle-5) remain manual/curated, not random off-type.

**Implementation note (Phase 6 — Gym Leader cap):** `TRAINER_GYM_LEADER_CAP_LEVEL` in `include/config.h` — `MakeTrainerPokemonParty()` in `src/field/enemy_party.c`. Detects Johto/Kanto Gym Leader trainer classes (`TRAINERCLASS_LEADER_`*); every party slot gets the badge cap exactly instead of a random level in the band. Gym trainer band + type filter still TBD.

### Phase 7 — Agreed battle size

Trainer battles use a **symmetrical, agreed roster size** ([Battle-3](DESIGN-BATTLES.md#battle-3-core-trainer-battle-philosophy)): same number of active slots for both sides (2v2 through 6v6). Who proposes or accepts the size (trainer, badge tier, player, mix) remains **TBD**.

Phases 1–6 can keep vanilla party sizes until this lands. Exit criterion: a Route trainer and the player fight **3v3** (or chosen size) with roster-slot parity, still using fixed or generated parties from earlier phases.

### Phase 8 — Dynamic rosters

Replace “pick your party before battle” with **collection-as-bench** ([Battle-6](DESIGN-BATTLES.md#battle-6-dynamic-battle-rosters)):

- battle starts with one send-out per side;
- each **new** Pokémon brought in consumes a roster slot until the agreed size is reached;
- then the roster **locks**; fainted mons still occupy slots.

**Depends on** universal PC / box access during trainer battles ([Battle-6 — PC / collection access](#pc--collection-access)). Without that, Phase 8 is blocked.

### Phase 9 — Counter-picking

Opponents (and eventually AI) **respond to revealed player commitments** ([Battle-6 — Counter-picking](#counter-picking-and-information)): unrevealed Pokémon may be generated or selected from a hidden pool when the trainer spends another slot. Strength of intentional counter-play remains **TBD** — should feel responsive, not omniscient.

Builds on Phase 4 (generated species) and Phase 8 (slot commitment). Early stub: fixed party order; full vision: on-demand counters from generated collection.

### Phase 10 — Held items

Assign held items to trainer Pokémon (roadmap; none in Phases 1–9).

### Phase 11 — TM moves

Allow TM moves on trainer movesets beyond level-up sets (roadmap).

### Phase 12 — Living trainers

Field population, movement, and map-level trainer generation ([World-5](DESIGN-WORLD.md#world-5-living-trainers), [World-6](DESIGN-WORLD.md#world-6-trainer-interactions)) — distinct from battle-start scaling; location-weighted distributions and non-battle interactions.

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

---

# Battle-9. Technical Investigations


Open engineering questions for **battle systems** (world/trainer-population topics moved to [World-11](DESIGN-WORLD.md#world-11-technical-investigations)).

## Dynamic battle rosters

Questions include:

- accessing boxed Pokémon from battle;
- introducing a boxed Pokémon into an active battle;
- tracking committed roster slots;
- dynamically generated opponent collections;
- opponent counter-picking AI;
- wild-battle PC access;
- battle UI.



## Badge-scaled Gyms and trainers

**Priority investigation** — should precede level caps and broad starting-city rollout.

**Phase 1 target:** hook trainer battle start → badge count → level band → rescale existing party levels ([Battle-8 Phase 1](#phase-1)).

**Phase 6 target:** Gym trainers (band + type filter); Gym Leaders (cap + type filter).

**Phases 7–9 target:** symmetrical battle size → dynamic rosters (requires [Battle-6 PC access](#pc--collection-access)) → counter-picking AI / hidden pools.

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
- monotype generation with curated exceptions.



## Universal PC

Questions include:

- overworld access;
- trainer battle access;
- wild battle access;
- interaction with party assumptions in vanilla HGSS.
