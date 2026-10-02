# Pokémon Wandering Heart — Battles, Trainers & Progression

> Gyms, badges, level caps, trainer scaling, and QoL.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Wilds:** [`DESIGN-WILDS.md`](DESIGN-WILDS.md) · **Story:** [`DESIGN-STORY.md`](DESIGN-STORY.md)

**Progression at a glance:** [Battle-2](#battle-2-badge-level-caps) badge cap and trainer level band → moves and stage ([Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution)). Wild grass uses distance caps first ([Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps), [Wilds-2](DESIGN-WILDS.md#wilds-2-wild-pokémon-level-range)), then the same stage rules.

## Sections

| Section | Status |
| ------- | ------ |
| [Battle-1. Fair Trainer Battles](#battle-1-fair-trainer-battles) | IMPLEMENTED |
| [Battle-2. Badge Level Caps](#battle-2-badge-level-caps) | PARTIALLY IMPLEMENTED |
| [Battle-3. Gyms](#battle-3-gyms) | PARTIALLY IMPLEMENTED |
| [Battle-4. Experience](#battle-4-experience) | IMPLEMENTED |
| Generated trainer & Gym parties | Moved — [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) |
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

Because recovery is automatic, and items cannot be used in battle, there is no more use for Potions, Antidotes, X-items, etc. Shop stock shifts toward held items and berries ([World-6](DESIGN-WORLD.md#world-6-shops)).

## Equal Party sizes

Deferred to [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc)

---

# Battle-2. Badge Level Caps

**Status: PARTIALLY IMPLEMENTED**

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

After trainer Pokémon levels are set from the [cap ladder](#cap-ladder), evolution stage and moves are adjusted to match — same rules as wild encounters ([Wilds-3](DESIGN-WILDS.md#wilds-3-encounter-stage-evolution--devolution)). Release uses **vanilla trainer species** at scaled levels ([Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) replaces species later).

## Rare Candies

**Rare Candies ignore the badge cap**.

- Each candy is a **deliberate spike**, not a party-wide bypass.
- Example: at 6 badges (cap 34), two candies can push a Quilava to 36 for an early evolution before the next cap increase.
- While rare candies are available in shop, they are expensive and should be used as a last resort.

## Wild catches above the player cap

[Wilds-1](DESIGN-WILDS.md#wilds-1-starting-city-distance-based-wild-level-caps) can roll wild levels **above** the current player cap. Catching them would skip the cap loop.

**Policy:** block the catch when wild level **>** current player cap — clear message or 0% catch rate. Gifts, trades, and scripted catches are handled per encounter.

---

# Battle-3. Gyms

All **16** Johto and Kanto Gyms in **any order**; all **16 badges** required for Victory Road / League ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)).

## Levels

- **Gym trainers:** same band as route trainers (`floor`–`ceiling` from [Battle-2](#battle-2-badge-level-caps)).
- **Gym Leaders:** every Pokémon at **cap** for the player's current badge count.

## First defeat rewards

After a Leader battle:

1. **Badge**
2. **HM** — field ability for this badge count when that row grants a new unlock ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves))
3. **TM** — player picks one from that Leader's pool they qualify for by badge count ([World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms))
4. **Wild Pokemon Hint** ([Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties), [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle))

## Rematches

Gym Leaders can be rematched without a hard limit. Each rematch offers the same **TM choice** as the first win.

**Rematches** use the current badge tier and cap, not the tier at first defeat.

---

# Battle-4. Experience

**Status: IMPLEMENTED**

**Full-party** EXP — each non-fainted party member receives full calculated EXP per KO (not split); no Exp Share item required. Fainted Pokémon receive **no** EXP. Pokémon already at the badge cap are **skipped** as recipients.

Combined with level caps, increased EXP should naturally push players to raise more Pokémon instead of just a permanent six.

Will change with the dynamic rosters of [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc)
