# Pokémon Wandering Heart — Battles, Trainers & Progression

> Gyms, badges, level caps, trainer scaling, and QoL.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Wilds:** [`DESIGN-WILDS.md`](DESIGN-WILDS.md) · **Story:** [`DESIGN-STORY.md`](DESIGN-STORY.md)

**Progression at a glance:** [Battle-2](#battle-2-badge-level-caps) badge cap and trainer level band → moves and stage ([Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution)). Wild grass uses distance caps first ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), [Wilds-2](DESIGN-WILDS.md#wilds-2-wild-pokémon-level-range)), then the same stage rules.

## Sections

| Section | Status |
| ------- | ------ |
| [Battle-1. Fair Trainer Battles](#battle-1-fair-trainer-battles) | IMPLEMENTED |
| [Battle-2. Badge Level Caps](#battle-2-badge-level-caps) | IMPLEMENTED |
| [Battle-3. Gyms](#battle-3-gyms) | IMPLEMENTED |
| [Battle-4. Experience](#battle-4-experience) | IMPLEMENTED |
| [Battle-5. Generated trainer & Gym parties](#battle-5-generated-trainer--gym-parties) | IMPLEMENTED |
| Dynamic battle rosters & universal PC | Moved — [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc) |

---

# Battle-1. Fair Trainer Battles

**Status: IMPLEMENTED**

Trainer battles should feel like a fair fight between two trainers. Full restore after every battle so each fight stands alone. No Bag use in trainer battles on either side; held items and berries stay in play. Equal battle roster sizes planned for Future release.

## Recovery

Traditional long-term HP/PP attrition is intentionally removed. Balance targets **individual encounters**, not wearing the party down across a route. Every battle should begin with the player's Pokémon ready to fight.

After every battle (wild, trainer, flee, or catch):

- All pokemon revived
- HP and PP to full
- Status conditions removed
- Includes newly caught Pokémon

## Items

**Bag items** cannot be used during trainer battles. No X items, or healing items. The rule applies to **both** sides. **Held items** including berries remain legal.

Because recovery is automatic, and items cannot be used in battle, there is no more use for Potions, Antidotes, X-items, etc. Shop stock shifts toward held items and berries ([Items-4](DESIGN-ITEMS.md#items-4-shops)).

## Equal Party sizes

Deferred to [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc)

---

# Battle-2. Badge Level Caps

**Status: IMPLEMENTED**

Level caps follow **badge progression**, not map position ([World-0](DESIGN-WORLD.md#world-0-open-world-principles)).

## Cap ladder

**+4 levels per badge earned**, starting at **10** before the first Gym.

Formula (badges 0–15): `cap = 10 + 4 × badges_earned`

- **16 badges → cap 80** — a **+10** step.
- **Champion → player cap removed** (progression toward 100). Regular trainers still capped at 80

| Badges earned | Player cap | Ordinary trainers | Gym Leaders |
| ------------- | ---------- | ----------------- | ----------- |
| 0 | 10 | 6–10 | 10 |
| 1 | 14 | 10–14 | 14 |
| 2 | 18 | 14–18 | 18 |
| … | … (+4) | … (cap−4 to cap) | … (at cap) |
| 15 | 70 | 66–70 | 70 |
| 16 | 80 | 76–80 | 80 |

Ordinary trainers: uniform random level in **`[cap − 4, cap]`**. Gym Leaders: **every slot at cap** ([Battle-3](#battle-3-gyms)).

## Trainer scaling

After trainer Pokémon levels are set from the [cap ladder](#cap-ladder), evolution stage and moves are adjusted to match — same rules as wild encounters ([Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution)). Eligible battles draw teams under [Battle-5](#battle-5-generated-trainer--gym-parties).

## Rare Candies

**Rare Candies ignore the badge cap**.

- Each candy is a **deliberate spike**, not a party-wide bypass.
- Example: at 6 badges (cap 34), two candies can push a Quilava to 36 for an early evolution before the next cap increase.
- While rare candies are available in shop, they are expensive and should be used as a last resort.

## Day Care

Day Care levels stop at the badge cap. The man's growth quote and the withdrawal fee use those same levels. A Pokémon already above the cap keeps that level, and the fee is the no-growth charge.

## Wild catches above the player cap

[Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps) can roll wild levels **above** the current player cap. Catching them would skip the cap loop.

**Policy:** block the catch when wild level **>** current player cap — clear message or 0% catch rate. Gifts, trades, and scripted catches are handled per encounter.

---

# Battle-3. Gyms

**Status: IMPLEMENTED**

All **16** Johto and Kanto Gyms in **any order**; all **16 badges** required for Victory Road / League ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)).

## Levels

- **Gym trainers:** same band as route trainers (`floor`–`ceiling` from [Battle-2](#battle-2-badge-level-caps)).
- **Gym Leaders:** every Pokémon at **cap** for the player's current badge count.

## First defeat rewards

After a Leader battle:

1. **Badge**
2. **HM** — field ability for this badge count when that row grants a new unlock ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves))
3. **TM** — player picks one from that Leader's pool they qualify for by badge count ([Items-2 § Gym TMs](DESIGN-ITEMS.md#gym-tms))
4. **Wild Pokémon Hint** ([Future-5](DESIGN-FUTURE.md#future-5-gym-leader-ecology-hints))

## Rematches

Gym Leaders can be rematched without a hard limit. Each rematch offers the same **TM choice** as the first win.

**Rematches** use the current badge tier and cap, not the tier at first defeat.

---

# Battle-4. Experience

**Status: IMPLEMENTED**

**Full-party** EXP — each non-fainted party member receives full calculated EXP per KO (not split); no Exp Share item required. Fainted Pokémon receive **no** EXP. Pokémon already at the badge cap are **skipped** as EXP recipients.

The same non-fainted party members receive that KO’s EVs, including Pokémon already at the badge cap. Fainted Pokémon receive no EVs.

Combined with level caps, increased EXP should naturally push players to raise more Pokémon instead of just a permanent six.

Will change with the dynamic rosters of [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc)

---

# Battle-5. Generated trainer & Gym parties

**Status: IMPLEMENTED**

Generate opposing trainer parties, including Gym Leaders and their rematches. Link, Battle Frontier, tutorial, ally, and custom parties with additional scripted fields keep their authored teams. Use the battle-start badge count and the [trainer level rules](#trainer-scaling).

## Species and party size

Roll each slot from the eligible [dex scope](DESIGN-WILDS.md#wilds-5-pokémon-generations--content-scope) and apply the shared [level-based evolution rules](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution). Legendary and Mythical Pokémon, plus Unown and Smeargle are excluded. Each generated trainer party can contain each final species at most once. Different species from the same family can appear together.

| Badges | One opposing trainer | Each of two opposing trainers |
| ------ | -------------------- | ----------------------------- |
| 0 | 3 | 2 |
| 1 | 4 | 2 |
| 2 | 5 | 3 |
| 3+ | 6 | 3 |

A single trainer in a Double Battle uses the full party size. Two opposing trainers each get half the full size, rounded up.

## Type filters

Gyms use their Gym type to filter generated parties. See [Data-6 § Gym and League roster filters](DESIGN-DATA.md#gym-and-league-roster-filters) for the type pools and family exceptions. The Type filter(s) apply to both the gym leader and trainers, but the exceptions only apply to the gym leader. 

There is also a mapping from trainer classes to type. Eg: Bug Catcher -> Bug. See [Data-6 § Trainer class type pools](DESIGN-DATA.md#trainer-class-type-pools) for the class mapping. Gym membership takes precedence over ordinary trainer class.

## TMs, HMs, and generated movesets

Generate the team first. Use the badge count at battle start for move unlocks. Give the trainer every HM unlocked by that badge count under [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves). Draw a random supply of TM01–TM92 (except TM10 Hidden Power) from the TMs unlocked by that badge count. Trainers get **five TM rolls per badge**, so a trainer with no badges gets no TM rolls. Each draw is independent and may yield another copy of the same TM. Use the earliest badge unlock among shops, Game Corner prizes, and Gym Leader rewards. Map item pickups do not qualify as unlock sources. A qualifying source with no badge gate counts as a zero-badge unlock.

Clear each Pokémon's moveset. Build its complete candidate pool from its level-up learnset through its generated level, compatible TMs in the trainer's supply, and compatible unlocked HMs. Exclude egg moves, tutor moves, unimplemented moves, and anything on the trainer move blacklist. Each move can occupy at most one slot. Build the sets from the last party slot to the first so the ace gets first choice of the TM supply. Consume one copy when a Pokémon learns a move that requires a TM. Level-up and HM sources do not spend a TM copy.

**Damaging move score** = **effective power × accuracy ÷ 100**. Use 100% accuracy for moves that ignore accuracy checks. Multiply the damage score by **1.5** if the move matches either of the Pokémon’s types. See [Data-6 § Trainer damaging moves](DESIGN-DATA.md#trainer-damaging-moves) for additional scoring modifiers.

Status moves are separated by tier. See [Data-6 § Trainer status move tiers](DESIGN-DATA.md#trainer-status-move-tiers) for all assignments. Group status moves by function and allow at most one move from each group. See [Data-6 § Trainer status move categories](DESIGN-DATA.md#trainer-status-move-categories) for the full grouping.

1. Pick the highest-scoring damaging move first, including damaging utility moves. If no damage move is available, use the highest-tier status move.
2. For each remaining slot, use RNG to choose between damage and status. For damage, take the highest-scoring remaining attack of a type the set does not already use. For status, take the highest-tier remaining move from an unused status group. If only one category has a valid candidate, use it. Break ties randomly. Stop at four moves or when no candidates remain.



If selection yields zero moves, use up to four level-up moves available at the Pokémon’s current level. The fallback can use moves such as Splash and spends no TMs.

## EVs, IVs, nature, and ability

Ordinary trainers get **51 EVs per badge** and Gym Leaders get **102 EVs per badge**, with a total cap of **510**. Distribute the total as evenly as possible across all six stats. Ordinary trainers max out at **10 badges**, and Gym Leaders max out at **5**.

Roll all six **IVs** independently for every generated Pokémon. Then spend a team-wide budget to raise the lowest remaining imperfect IV to **31**, breaking ties randomly. Ordinary trainers get their first upgrade at **8 badges**, then gain one per badge up to **9** at badge 16. Gym Leaders start with **2** and gain one per badge, reaching **18** at badge 16.

For now, nature comes from the rolled personality value. That value also selects between the species’ regular ability slots when it has two. Generated trainers use regular abilities.

## Held items

See [Data-6 § Trainer held-item unlocks](DESIGN-DATA.md#trainer-held-item-unlocks) for the badge gates.

Species gear covers Pikachu (Light Ball), Cubone and Marowak (Thick Club), Farfetch’d (Leek), Ditto (Quick Powder and Metal Powder), and Clamperl (Deep Sea Tooth and Deep Sea Scale).

After building the moveset, give each generated Pokémon one item uniformly at random from its eligible pool. Teammates can roll the same item. Type boosters require a damaging move of the matching type. Resist berries cover a type weakness, with Chilan also eligible against neutral Normal damage. Muscle Band and Liechi require a physical attack. Wise Glasses and Petaya require a special attack. Metronome, Expert Belt, Scope Lens, Razor Claw, King’s Rock, Razor Fang, Shell Bell, and Life Orb require at least one damaging move.

Leave player progression items, field utility items, evolution-only items, Berry Juice, EV and friendship berries, and Leppa, Jaboca, Rowap, Ganlon, Apicot, Custap, Micle, and Enigma Berries out of generated trainer sets.

See [Future-7](DESIGN-FUTURE.md#future-7-trainer-party-improvements) for the next tuning pass.
