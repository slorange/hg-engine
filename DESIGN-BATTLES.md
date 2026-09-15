# Pokémon Wandering Heart — Battles, Trainers & Progression

> Gyms, badges, level caps, trainer scaling, and QoL.
>
> **Index:** `[DESIGN.md](DESIGN.md)` · **Vision:** `[DESIGN-VISION.md](DESIGN-VISION.md)` · **World:** `[DESIGN-WORLD.md](DESIGN-WORLD.md)` · **Wilds:** `[DESIGN-WILDS.md](DESIGN-WILDS.md)`

## Sections

| Section | Status |
| ------- | ------ |
| [Battle-1. Gyms and Badges](#battle-1-gyms-and-badges) | PARTIALLY IMPLEMENTED |
| [Battle-2. Healing and Attrition](#battle-2-healing-and-attrition) | IMPLEMENTED — [KB-2](DESIGN.md#index-5-known-bugs) |
| [Battle-3. Core Trainer-Battle Philosophy](#battle-3-core-trainer-battle-philosophy) | DECIDED |
| [Battle-4. Badge-Based Level Caps](#battle-4-badge-based-level-caps) | DECIDED |
| [Battle-5. Gym Rosters](#battle-5-gym-rosters) | DECIDED |
| [Battle-6. EXP Share](#battle-6-exp-share) | PARTIALLY IMPLEMENTED |
| Dynamic battle rosters & universal PC | Moved — [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) |

---

# Battle-1. Gyms and Badges


**Status: PARTIALLY IMPLEMENTED**

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


**Status: IMPLEMENTED** — verified wild, trainer, flee, and catch ([Index-2](DESIGN.md#index-2-current-technical-baseline)). Known bug: intermittent post-battle crash ([KB-2](DESIGN.md#index-5-known-bugs)). Recipe: `documentation/HACK-NOTES.md` § **Heal after every battle**.

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

Note, this might have already been implemented in HG-Engine as a feature flag.

Symmetrical agreed battle size (2v2–6v6): [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) / [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties). Initial release uses vanilla party sizes.

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
- **Ordinary trainer scaling** — badge level band below ([Trainer scaling](#trainer-scaling-implemented)); **hard ceiling 80** even if the player is Champion. Route trainers, Gym trainers, and rematches should not creep past 80 without an explicit exception.

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

**Design intent:**

- Candies are the **deliberate exception** to the cap, not a loophole on every mon at once — each use is a consumable choice.
- Creates meaningful timing decisions: hoard Rare Candies for a hard Gym Leader or special trainer; spike one ace for a single fight to get an evolution or move early. Example: 6 badges (34 level cap), 2 rare candies for early lv36 Typhlosion
- Power spikes from candies should feel **earned and spent**, not a substitute for badge progression across the whole party.

Player level cap hooks are **not enabled** in the ROM yet. When ready: `documentation/HACK-NOTES.md` § **Player badge level cap & Rare Candies**.

## Trainer scaling (implemented)

**Status: PARTIALLY IMPLEMENTED** — level band, moves, and stage adjust verified; Gym Leader at cap partial; Gym in-Gym type filter still open ([Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties)). Implementation: `documentation/HACK-NOTES.md` § **Trainer level scaling**.

When the player has `n` **badges earned**, trainer Pokémon use the same cap formula as the player (`10 + 4n`, **80** at 16 badges). **Ordinary trainers:** uniform random level in **`[cap − 4, cap]`** (`floor = cap − 4`, `ceiling = cap`). **Gym Leaders:** every slot at **cap** exactly ([Battle-5](#battle-5-gym-rosters)).

| Badges earned | Player cap | Trainer level range |
| ------------- | ---------- | ------------------- |
| 0             | 10         | 6–10                |
| 1             | 14         | 10–14               |
| 2             | 18         | 14–18               |
| 3             | 22         | 18–22               |
| …             | …          | …                   |
| 15            | 70         | 66–70               |
| 16            | 80         | 76–80 (ordinary); E4 band TBD |

On trainer battle start (release behaviour):

1. **Species** — vanilla party (random species: [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties)).
2. **Levels** — band above; Leaders at cap.
3. **Moves** — last four level-up moves at assigned level (same rule as wild Pokémon).
4. **Stage** — `AdjustEncounterSpeciesForLevel()` — level-up chains + synthetic edges ([Wilds-1 synthetic stages](DESIGN-WILDS.md#synthetic-evolution-stages-wild--trainer)); `data/synthetic_evolution_thresholds.tsv`.

Generated parties, dynamic rosters, and living trainers: [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties), [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc), [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions).

---

---

# Battle-5. Gym Rosters


**Status: DECIDED** (release) — vanilla Leader species at scaled levels. Generated rosters, type filters, and family hints: [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties).

## Scaling (badge tier)

Gym battles use the same badge-tier ladder as ordinary trainers ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps) [Trainer scaling](#trainer-scaling-implemented)).

- **Gym trainers** (inside the Gym): levels in the current band (`floor`–`ceiling`)
- **Gym Leaders:** **every Pokémon is exactly at level cap** 

Rematches use the player's **current** badge tier and cap, not the tier at first defeat.

## Rematches

**Status: DECIDED**

Gym Leaders can be rematched.

Rematches use the player's **current badge tier**, rather than repeating the difficulty at which the Gym was originally defeated.

Gym rematches are also a renewable source of that Gym's TM ([World-5](DESIGN-WORLD.md#world-5-tms)).

There is no intended hard limit on the number of rematches/TM copies.

## Gym Leader rewards (first defeat)

**Status: DECIDED conceptually; family lists and hint text TBD**

After a Gym Leader battle, the standard reward sequence is:

1. **Badge**
2. **HM** — the field ability for this badge count ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)); only on badge counts that grant a new unlock (not every badge grants an HM)
3. **TM** — that Gym's TM ([World-5](DESIGN-WORLD.md#world-5-tms))

Optional **family location hint** (first clear): [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) (requires [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle)).

Rematches continue to award **TM copies** only ([Rematches](#rematches) above).

---

---

# Battle-6. EXP Share


**Status: PARTIALLY IMPLEMENTED** — interim full-party share verified in-game; final battle-limit EXP recipient formula still **TBD** below. Recipe: `documentation/HACK-NOTES.md` § **Full party EXP share (interim)**.

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
