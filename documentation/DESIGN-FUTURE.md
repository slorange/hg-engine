# Pokémon Wandering Heart — Future & Addon Systems

Deferred systems and wishlist items. **Sections are not listed in intended implementation order**
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Identity:** [Index-2 — Game Identity](DESIGN.md#index-2-game-identity)
>

## Sections

| Section |
| ------- |
| [Future-2. Full Moon system](#future-2-full-moon-system) |
| [Future-3. Unlimited learned moves](#future-3-unlimited-learned-moves) |
| [Future-4. Map editing — world connectivity wishlist](#future-4-map-editing--world-connectivity-wishlist) |
| [Future-5. Gym Leader Ecology Hints](#future-5-gym-leader-ecology-hints) |
| [Future-7. Trainer party improvements](#future-7-trainer-party-improvements) |
| [Future-8. Dynamic battle rosters & universal PC](#future-8-dynamic-battle-rosters--universal-pc) |
| [Future-10. Living trainers & interactions](#future-10-living-trainers--interactions) |
| [Future-11. Pokémon Research Society](#future-11-pokémon-research-society) |
| [Future-12. Unown collection quest](#future-12-unown-collection-quest) |
| [Future-14. Other potential changes](#future-14-other-potential-changes) |
| [Priority](#priority) |

---

# Future-2. Full Moon system

A full-moon system should be a meaningful world feature — not only a hook for Moon Ball mechanics.

Possible system:

- full moon every X in-game days;
- lasts several nights;
- special encounters;
- NPC dialogue/world changes;
- quests/events;
- potentially special legendary/mythical content;
- Darkrai/Lunala-related content depending on generation scope;
- **Ursaring → Ursaluna** (or equivalent full-moon evolution hook for cross-gen lines).

Do not implement Moon Ball capture rules without this broader system.

### Moon Ball

**8×** against every member of an evolutionary family containing a Moon Stone evolution.

During a full moon: **8× against all Pokémon** — niche normally, strong general-purpose ball during the event.

### Open design questions

- Full-moon calendar cadence and duration.
- Which encounters, NPCs, and quests change during the event.
- Moon Ball crafting source (Apricorn colour TBD).

---

# Future-3. Unlimited learned moves

Long-term desired design:

> **Pokémon retain every move they learn rather than being restricted to four moves.**

Learning a fifth move does not require permanently forgetting a previous one — genuinely more than four stored moves, not merely picking four before each battle from a larger list.

Expected to be technically difficult. Potentially affected: Pokémon data structures, save format, box storage, battle and move-selection UI, AI, move learning, evolution, scripts, and HGSS/HG-Engine assumptions.

---

# Future-4. Map editing — world connectivity wishlist

Deferred until reliable HGSS map/geometry editing is possible.

## Surface fixes

- Replace the Route 42 ferry NPC with a physical bridge.
- Remove the Route 4 one-way ledge currently handled by the "ledge bump" NPC.

## Johto underground network

Expand caves into a connected underground travel network.

- **Union Cave** — Slowpoke Well; Dark Cave; Ruins of Alph (underground).
- **Dark Cave** — Union Cave; Mt. Mortar; Mt. Silver; Ice Path; Tohjo Falls.
- **Mt. Mortar** — Ice Path.

Johto caves should function as a secondary transportation network, not isolated one-off dungeons. Preserve dungeon identity — not one indistinguishable tunnel system.

## New surface / water connections

- Water route: Route 40 / Whirl Islands ↔ Goldenrod Harbor.
- Route: Olivine ↔ National Park.

## Kanto connections

- Viridian City ↔ Route 16.
- South of Mt. Moon: Route 3 ↔ Route 4; branch south toward Celadon City.
- Water route: Route 27 ↔ Route 21.

## Design goal

Multiple legitimate paths through the world: surface roads, water routes, interconnected caves, and fast travel between discovered cities. The underground network rewards exploration without being required for basic city/Gym access.

---

# Future-5. Gym Leader Ecology Hints

**Prerequisite** [Wilds-6](DESIGN-WILDS.md#wilds-6-per-save-wild-ecology-shuffle). Core rules, seed behavior, documented there.

## Gym Leader family location hint

After first Gym clear (alongside badge, HM, TM — see [Battle-3](DESIGN-BATTLES.md#first-defeat-rewards)):

The Leader offers to point the player toward **one evolutionary family** matching the Gym's type(s).

Example flow (Lt. Surge, Electric):

> *"As an extra reward, if there's any Electric-type you're looking for, I'll tell you where to look."*

The player picks from a curated list of families for that Gym. The Leader names a **concrete location** from the player's **generated ecology**, including encounter method when relevant:

> *"Chinchou can be found in Dark Cave using the Good Rod."*

**Rules:**
- One family choice per first Gym clear (not rematches unless redesigned later).
- Hint data must come from the save's ecology tables, not hardcoded vanilla locations.
- Multi-type Leaders (Whitney, Morty) offer families from **either** qualifying type.
- Family lists are curated per Leader — not every species of that type in the dex.
- Blue has no type and will need special handling. Consider giving him a curated list of rare mons unavailable by other gym leaders


---

# Future-7. Trainer party improvements

Build on [Battle-5](DESIGN-BATTLES.md#battle-5-generated-trainer--gym-parties).

## Roster curation

- Create a usable Sketched moveset for Smeargle before adding it to the eligible pool.
- Curate narrower species lists for Lance and Clair, and consider curated lists for other trainer classes as needed.
- Mitigate shared team weaknesses. Distinguish 2× and 4× weaknesses so Brock doesn't end up with 4× Grass weaknesses.

## Moveset and stat tuning

- Go through [Data-6 § Trainer damaging moves](DESIGN-DATA.md#trainer-damaging-moves) and set modifiers where needed.
- Score physical and special moves using the Pokémon’s offensive stats and evaluate actual matchup coverage. Evaluate Body Press using Defense.
- Compare damage and status when filling later slots. Proposed status scores are **S = 150, A = 100, B = 60, C = 30**. Revisit damage-plus-utility scoring after playtesting the current bonuses.
- Review special move scores against what the battle AI can use. Check HP-dependent and retaliatory damage for Super Fang, Endeavor, Final Gambit, Counter, Mirror Coat, Metal Burst, and Comeuppance. Review variable power for Crush Grip, Electro Ball, Flail, Reversal, Fling, Frustration, Natural Gift, Present, Return, and Spit Up. Review conditional damage and usage costs for Assurance, Avalanche, Brine, Facade, Fury Cutter, Hex, Payback, Power Trip, Revenge, Stored Power, Venoshock, and Weather Ball. Consider Fling, Natural Gift, Beltch.
- Choose natures that fit the physical or special set and EV spread. Consider more focused Gym Leader EV spreads at higher badge counts.
- Rank abilities into tiers and use those tiers to tune selection odds. Proposed hidden ability rates are **20% for ordinary trainers** and **30% for Gym trainers**. The earlier proposal also specified **10% in the wild**.
- Consider whether to tune PP, form, gender, friendship, ball, and shininess.

## Held-item scoring and conditions

Give each held item a score and explicit eligibility conditions. Keep badge gates as minimum unlocks and evaluate every unlocked item that fits the Pokémon. Use the score to favor stronger or better-fitting items. An early unlock can remain a strong choice when it suits the species, moveset, ability, or role. Decide score values, how much randomness to retain, and how to resolve ties during the tuning pass.

Defer Power Herb, White Herb, Flame Orb, Toxic Orb, Black Sludge, Big Root, Light Clay, weather rocks, Grip Claw, Iron Ball, Lagging Tail, Shed Shell, Lansat Berry, Wide Lens, Zoom Lens, and Choice items until the synergy pass.

## Synergy

- Evaluate combinations such as Swift Swim with Drizzle, Guts with Flame Orb, and recoil attacks with Rock Head or Magic Guard. Avoid combinations such as Choice Band with Swords Dance.
- Pair Sleep Talk with Rest and Dream Eater with a sleep-inducing move when the AI can use the combination.
- Allow distinct entry hazards together, favor complementary hazards, and consider placing hazard setters in the lead.
- Pair Sleep Talk with Rest and Dream Eater with a sleep-inducing move when the AI can use the combination. Keep both moves excluded from normal selection until the pairing rules are in place.
- Revisit Protect and Substitute once the selector can recognize sets that benefit from them. Both start at B tier because their value depends on the rest of the set.
- Score recoil attacks for the holder’s actual ability. Account for Rock Head or Magic Guard where the ability prevents the relevant recoil. Also revisit damage scoring for Technician with eligible low-power moves, Skill Link with variable-hit moves, and Contrary with moves that normally lower the user’s stats.
- Evaluate weather across the team, such as a Drizzle setter supporting a teammate with Swift Swim. Evaluate weather rocks alongside the setter and the teammates that benefit from that weather.
- Evaluate status orbs alongside the abilities and moves that can take advantage of them, such as Flame Orb with Guts. Consider Sticky Barb with Trick or Switcheroo only after checking whether the trainer AI can use the swap.
- Score Choice items against the full moveset. Avoid combinations that interfere with the set’s purpose, such as Choice Band with Swords Dance.
- Give Power Herb and White Herb explicit conditions tied to the moves that benefit from them. Review Wide Lens and Zoom Lens against the set’s actual accuracy needs and check whether the AI can take advantage of Zoom Lens.
- Revisit Acrobatics once moves and items can be chosen together. Its current score assumes a held item, so any bonus should depend on whether the set is expected to use it without one.
- Check each proposed combination against battle AI move selection and usage. Keep speculative bonuses deferred until the AI can actually use the interaction.

---

# Future-8. Dynamic battle rosters & universal PC

## Dynamic roster rules

**Each trainer's entire collection is their bench. The actual battle roster forms dynamically as Pokémon are revealed.**

Suppose a battle is 4v4. The player does not choose four Pokémon before battle. They initially choose one send-out; the opponent does the same.

Whenever the player may send out or switch, they may select:

1. a Pokémon already committed to this battle; or
2. an unused Pokémon from their entire collection.

The first time a unique Pokémon enters, it **permanently consumes one roster slot**. After the agreed number of unique Pokémon have entered, **the roster is locked**. Fainted Pokémon continue to occupy slots. The opponent follows the same rules.

- Consider allowing each side to commit at most one Pokémon of a given species per battle. Once a species is committed, a second individual of that species would be ineligible for the rest of the battle.

## Counter-picking and information

Dynamic counter-picking is intentional. Neither side initially knows the other's full collection. Revealing a counter spends a roster slot — **advantage and commitment**. NPC AI should eventually understand this rather than selecting independently.

## PC / collection access

The player's storage is accessible anywhere: overworld, trainer battles, wild battles. No requirement to visit a Center PC to reorganize.

Exact wild-battle UI/selection behaviour is a technical design problem.

## Field party vs full collection

The six field Pokémon: following mon, EXP defaults ([Battle-4](DESIGN-BATTLES.md#battle-4-experience)), overworld presentation, convenient ordering.

The entire collection: accessible anywhere including in battle; trainer-battle bench.

> **The player's collection is their team.**

### Field HMs from the full collection

An eligible species **anywhere in the collection** (party or box) can perform an unlocked overworld HM / Flash / Headbutt action — **the Pokémon need not know the move** on that slot. Badge unlock order from [World-3](DESIGN-WORLD.md#badge--field-abilities-single-reference) still gates *which* field abilities exist; this changes *who* can execute them. **Battle use** stays separate: HMs (and Flash / Headbutt) remain teachable moves for combat when the player wants them on the active roster.

## Technical investigation

- accessing boxed Pokémon from battle;
- introducing a boxed Pokémon into an active battle;
- tracking committed roster slots;
- dynamically generated opponent collections;
- opponent counter-picking AI;
- wild-battle PC access;
- battle UI;
- overworld / trainer / wild battle access vs vanilla party assumptions.

---




# Future-10. Living trainers & interactions

**Deferred.** [Battle-5](DESIGN-BATTLES.md#battle-5-generated-trainer--gym-parties) generates parties for the existing trainer encounters. Renewable TMs come from the sources in [Items-2](DESIGN-ITEMS.md#items-2-tms) and [Items-4](DESIGN-ITEMS.md#items-4-shops).

## Living trainers

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

Each trainer has or represents a badge progression level. Trainer progression distributions may be influenced by location. The player should generally battle trainers whose progression is reasonably comparable to their own.

### Simulation requirements

The game does NOT necessarily need to permanently simulate hundreds of individual NPCs throughout the entire world.

A technically simpler system may generate or populate trainers when maps load while maintaining the **illusion** of a persistent travelling trainer population.

The experiential goal matters more than literally simulating every trainer off-screen.

## Trainer interactions

Living trainers are not exclusively battle dispensers.

### Pokémon location requests

A trainer may ask for a species location. If the player has encountered the requested Pokémon, they can provide a location from **generated ecology** ([Wilds-6](DESIGN-WILDS.md#wilds-6-per-save-wild-ecology-shuffle)). Rewards: items, money, encounter info, TMs, etc.

### Encounter information

Trainers may tell the player where undiscovered species can be found (ecology data). **Gym Leaders:** structured first-clear hint — [Future-5](#future-5-gym-leader-ecology-hints).

### Pokémon trades / item trading

Some trainers request trades or buy/sell items (sink for duplicates; source for rare TMs / held gear).

### TMs

Some trainers provide renewable access to otherwise rare TMs ([Items-2](DESIGN-ITEMS.md#items-2-tms)) — alternative to putting everything in static marts.

### Gym advice / other quests

Information about nearby undefeated Gyms or scaled teams; additional lightweight interactions TBD.

## Field population (living trainers)

Investigate map-level trainer generation, movement, placement, location-weighted distributions, and non-battle interactions. Existing trainers receive their levels at battle start under [Battle-2](DESIGN-BATTLES.md#trainer-scaling).

## Technical investigation

- map spawning; movement; persistence; generated identities; badge counts; generated collections; map transitions; save-state requirements;
- ecology-linked location requests; reward economy; trade and item-exchange UI; TM distribution hooks.

---

# Future-11. Pokémon Research Society

A shared research organization with representatives in every Pokémon Center. The representative is a service in the shared hub ([World-5](DESIGN-WORLD.md#world-5-shared-pokémon-center-hub)), so the player can register finds and claim rewards from any Center.

The society handles two related collection systems: **Arceus Plate** research and **Pokédex** completion rewards.

## Plate research

All **17** Arceus Plates, including the **Pixie Plate**, are distributed throughout Johto and Kanto.

The player shows plates to a researcher, who registers them and gives them back. Plates are never consumed.

Each newly registered plate unlocks one Pokémon reward. Rewards progress through tiers, and the player chooses one Pokémon from the current tier.

Most plates are found loose in caves and optional areas. Locations may be randomized per save. Some sit behind badge-gated field obstacles ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

Some plates may instead be tied to a specific encounter:

| Plate | Encounter |
| ----- | --------- |
| Flame, Zap, Icicle | Legendary birds |
| Splash | Red Gyarados |
| Mind | Mewtwo |

The challenge is collecting plates across the whole world. Each find stays a modest exploration goal.

Plates may grant a stronger damage bonus than ordinary type-boosting items. Whether they do is still open.

## Hidden Power

Using a plate on a Pokémon sets that Pokémon’s **Hidden Power** type to the plate’s type. The plate stays in the bag. Plates are never consumed, including when shown to the researchers above.

Until a plate is used, Hidden Power’s type stays IV-dependent. That roll can be any type, including **Fairy**. It skips Fairy today, because Fairy occupies the old ??? type slot; the roll should include Fairy too. The Unown collection still scales Hidden Power’s power ([Future-12](DESIGN-FUTURE.md#future-12-unown-collection-quest)).

## Pokémon rewards

| Tier | Plates | Rewards |
| ---- | ------ | ------- |
| 1 | 1–4 | Kecleon, Delibird, Spinda, Chatot |
| 2 | 5–7 | Dunsparce, Wobbuffet, Tyrogue |
| 3 | 8–10 | Togepi, Riolu, Eevee |
| 4 | 11–13 | Lapras, Snorlax, Spiritomb |
| 5 | 14–15 | Shaymin, Manaphy |
| 6 | 16–17 | Undecided mythical, Arceus |

Tiers **1–5** are obtainable before the Elite Four. Tiers **1–4** are awarded as eggs.

Tiers **5** and **6** are location reports. The researcher describes newly detected activity, and the player investigates. **Arceus** is the final reward, potentially encountered at **Sinjoh Ruins**.

The last two plates are reserved for postgame areas, potentially **Cerulean Cave** and **Mt. Silver**.

**Wobbuffet** (tier 2) and **Eevee** (tier 3) are also Game Corner prizes ([Items-2](DESIGN-WORLD.md#pokémon-prizes)).

## Pokédex research

The same organization could also manage Pokédex completion rewards ([Items-1](DESIGN-ITEMS.md#pokédex-milestone-rewards)).

Milestones grant items, or location information for other legendary and mythical Pokémon.

The same researchers may give a reward each time the player registers a new Unown form ([Future-12](DESIGN-FUTURE.md#future-12-unown-collection-quest)). What that reward is remains open.

## Open design questions

- Organization name and NPC presentation.
- Pokédex milestones and reward structure.
- What the researchers give for each newly registered Unown form.
- Whether plate locations are randomized, and how hints work.
- How plates are split between exploration, encounters, and Pokédex rewards.
- Which mythical shares tier 6 with Arceus.
- Whether plates deal more damage than ordinary type-boosting items.
- Whether plate rewards and Pokédex rewards stay separate tracks or become more integrated.

---

# Future-12. Unown collection quest

Collect all **28 Unown forms** across Johto and Kanto. Each **unique form** registered in the Pokédex **permanently** improves **all Unown**. Completing forms also improves **Hidden Power globally** for every Pokémon (not only Unown).

## Progression

Scaling is linear from 0 unique forms registered to 28.

| Track | At 0 forms | At 28 forms |
| ----- | ---------- | ----------- |
| **BST** | 44 / 66 / 44 / 66 / 44 / 44 (**308** total) | 100 / 150 / 100 / 150 / 100 / 100 (**700** total) |
| **Hidden Power (all Pokémon)** | **60** BP (not IV-dependent) | **100** BP |
| **Catch rate (Unown)** | **255** | **3** |

- **Hidden Power type** stays **IV-dependent** until the player sets it with an Arceus Plate ([Future-11](DESIGN-FUTURE.md#hidden-power)). The plate is not consumed.
- **Ability (Unown only):** custom ability — all **damaging** moves deal **+33%**; Unown is **typeless** (no weaknesses, resistances, or STAB).
- **Wild held item:** **50%** chance to hold **TM10 (Hidden Power)**, which is the only source of the TM in the game.

## Moveset

| Level | Moves |
| ----- | ----- |
| 1 | Secret Power, Ancient Power, Ominous Wind, Silver Wind, Hidden Power |
| 15 | Teleport |
| 30 | Safeguard |
| 45 | Recover |
| 60 | Perish Song |

The level up set is meant to make it harder to catch Unown as the level increases. Unown cannot learn any TMs. 

## Encounter locations

Each location’s **theme word** lists the **unique letter forms** that can appear there. Letters may overlap between locations.

| Location | Theme / available forms |
| -------- | ------------------------ |
| Ruins of Alph | RUINS + ALPH + UNOWN |
| Dark Cave | DARK |
| Union Cave | UNION |
| Slowpoke Well | SLOW |
| Ilex Forest | ILEX |
| Sprout Tower | GROW |
| Burned Tower | FIRE |
| Bell Tower | BELL |
| Mt. Mortar | MORTAR |
| Lake of Rage | RAGE |
| Ice Path | ICE |
| Dragon's Den | DRAGON |
| Whirl Islands | WHIRL |
| Mt. Moon | MOON |
| Rock Tunnel | ROCK |
| Diglett's Cave | DIG |
| Seafoam Islands | FROST |
| Victory Road | VICTORY |
| Tohjo Falls | TOHJO |
| Cinnabar Island | MAGMA |

### Endgame and exclusive forms

- **Q**, **Z**, **!**, **?** — one each from a **Johto roamer**, **Kanto roamer**, **Mt. Silver**, and **Cerulean Cave** (exact assignments TBD).
- **V** and **Y** — **Victory Road only** ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) **16-badge** gate).

### Wild encounter rules

- At each designated location, **5%** of wild encounters are **Unown** instead of the normal slot species.
- When Unown is selected, pick **uniformly** among that location’s allowed forms; otherwise use normal encounter tables.
- Applies to **grass**, **cave**, **Surf**, **Rock Smash**, and **Headbutt**. Does **not** apply to **Fishing**.
- **Ruins of Alph** has **100% Unown** rate, same as Vanilla, but with only the letters RUINS + ALPH + UNOWN.

### Other notes

- **Caught indicator:** Show the wild **Poké Ball icon** for Unown **only when that exact form** was caught before — not when any Unown was caught.
- The research society may also give a reward for each newly registered Unown form ([Future-11](DESIGN-FUTURE.md#pokédex-research)).

---

# Future-14. Other potential changes

Ideas that do not have their own `Future-*` section yet.

- **Portable resting** — consider a tent, sleeping bag, or camping system that lets players rest outside towns to advance time.
- **Move Tutor** — make special move tutoring available from any Pokémon Center through the [shared hub](DESIGN-WORLD.md#world-5-shared-pokémon-center-hub).
- **Specialty Trader** — let players exchange items or currencies for selected rewards through the [shared hub](DESIGN-WORLD.md#world-5-shared-pokémon-center-hub). Inventory and pricing TBD.
- **Post-battle party heal timing** — [Battle-1](DESIGN-BATTLES.md#recovery) expects recovery as soon as a battle ends. Initial release applies heal on the **first overworld step** (workaround for battle-overlay crashes). Move heal to **end of battle / return to field** so the party, follower, and back-to-back trainer fights match design (no heal gap on turn-in-place or chained trainers).
- **Game Corner Coin income** — [prize menus](DESIGN-DATA.md#data-1-game-corner-prize-pools) work today and all prizes cost 50 Coins during playtesting. Players currently earn Coins through **Voltorb Flip**. Potential sources include buying Coins for ¥, trainer payouts, the Amulet Coin, Voltorb Flip changes, and department-store bundles. Exchange rates, UI, and tiered prize pricing are TBD.
- **Move balance** — every type needs viable early-, mid-, and late-game attacks; consider thematic type changes (e.g. Cut → Grass or Bug) and buffs to weak 20 BP moves.
- **Pokémon learnsets** — every species should have appropriate STAB through progression plus some coverage options.
- **Evolution levels** — review evolution levels. Ponyta → Rapidash at level 40 is tragic
- **Pokémon balance** — every species reasonably viable; encounter rarity roughly reflects power; adjust BST, abilities, and learnsets as needed.
- **Legendary / Mythical encounters** — quests or encounters for missing species; e.g. each vanilla legendary spot could roll from uncaught legendaries on map load when the player is Champion (Mewtwo slot → Arceus, Moltres spot → Heatran, …). Plate and Pokédex collection is [Future-11](DESIGN-FUTURE.md#future-11-pokémon-research-society).
- **Battle AI** — increase switching for type matchups when no good damaging move is available.
- **Separate Blackthorn and Battle Frontier shops** — give each shop its own inventory so Blackthorn’s themed stock can change independently of the Battle Frontier.

---

# Priority

Working scores for what to build next. [Future-14](#future-14-other-potential-changes) is a list of leftovers, not one feature, so it has no row.

**Score** = Vision + Excitement + Uniqueness + Presence − 2 × Difficulty. Difficulty is counted twice because a hard item should have to clear a higher bar, and the other columns tend to rise and fall together. The Difficulty column itself still means “higher is harder.” Ties break toward the higher Vision score.

| Column | What it measures |
| ------ | ---------------- |
| **Score** | Vision + Excitement + Uniqueness + Presence − 2×Difficulty. |
| **Vision** | How much the road-trip identity needs this. A **5** means the hack is about it. |
| **Excitement** | How much we want to work on it. |
| **Difficulty** | Expected effort and risk. Higher is harder. Only unlimited moves is a **5**. Subtracted twice in the total. |
| **Uniqueness** | How unlike other romhacks this is. A **1** is common hack craft. |
| **Presence** | How often a player feels it on a normal run. A **1** is a single side track; a **5** shows up every session. |
| **Depends on** | What should exist first. |

| Item | Score | Vision | Excitement | Difficulty | Uniqueness | Presence | Depends on |
| ---- | :---: | :----: | :--------: | :--------: | :--------: | :------: | ---------- |
| [Future-8](#future-8-dynamic-battle-rosters--universal-pc) Dynamic rosters | 10 | 5 | 3 | 4 | 5 | 5 | — |
| [Future-10](#future-10-living-trainers--interactions) Living trainers | 9 | 5 | 4 | 4 | 4 | 4 | — |
| [Future-12](#future-12-unown-collection-quest) Unown quest | 8 | 2 | 4 | 2 | 4 | 2 | — |
| [Future-7](#future-7-trainer-party-improvements) Trainer party improvements | 7 | 3 | 2 | 1 | 1 | 3 | — |
| [Future-11](#future-11-pokémon-research-society) Pokémon Research Society | 7 | 3 | 3 | 2 | 2 | 3 | — |
| [Future-3](#future-3-unlimited-learned-moves) Unlimited moves | 6 | 3 | 3 | 5 | 5 | 5 | — |
| [Future-5](#future-5-gym-leader-ecology-hints) Gym Leader Ecology Hints | 5 | 2 | 2 | 2 | 3 | 2 | — |
| [Future-4](#future-4-map-editing--world-connectivity-wishlist) Map connectivity | 2 | 4 | 2 | 4 | 1 | 3 | — |
| [Future-2](#future-2-full-moon-system) Full moon | 1 | 1 | 1 | 2 | 2 | 1 | — |
