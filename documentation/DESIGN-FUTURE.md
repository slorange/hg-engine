# Pokémon Wandering Heart — Future & Addon Systems

Deferred systems and wishlist items. **Sections are not listed in intended implementation order**
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Identity:** [Index-2 — Game Identity](DESIGN.md#index-2-game-identity)
>

## Sections

| Section |
| ------- |
| [Future-1. Apricorn economy & Poké Ball rebalance](#future-1-apricorn-economy--poké-ball-rebalance) |
| [Future-2. Full Moon system](#future-2-full-moon-system) |
| [Future-3. Unlimited learned moves](#future-3-unlimited-learned-moves) |
| [Future-4. Map editing — world connectivity wishlist](#future-4-map-editing--world-connectivity-wishlist) |
| [Future-5. Gym Leader Ecology Hints](#future-5-gym-leader-ecology-hints) |
| [Future-7. Generated trainer & Gym parties](#future-7-generated-trainer--gym-parties) |
| [Future-8. Dynamic battle rosters & universal PC](#future-8-dynamic-battle-rosters--universal-pc) |
| [Future-9. Time advancement](#future-9-time-advancement) |
| [Future-10. Living trainers & interactions](#future-10-living-trainers--interactions) |
| [Future-11. Pokémon Research Society](#future-11-pokémon-research-society) |
| [Future-12. Unown collection quest](#future-12-unown-collection-quest) |
| [Future-14. Other potential changes](#future-14-other-potential-changes) |
| [Priority](#priority) |

---

# Future-1. Apricorn economy & Poké Ball rebalance

Apricorn harvesting, crafting, and a two-tier ball roster (shop vs Apricorn). Tree refresh assumes [World-9](DESIGN-WORLD.md#world-9-accelerated-daynight-cycle) (accelerated in-game clock / virtual calendar when implemented).

## Apricorn economy

Apricorns go directly into the Bag and become a renewable crafting resource tied to the accelerated game clock.

- trees refresh approximately once per in-game day;
- each successful harvest yields **3–5 Apricorns**.

With the ~30-minute day target, this is a faster renewable economy than vanilla HGSS. Exact quantities and refresh timing remain subject to balance testing.

The player should not need to repeatedly return to Azalea Town merely to craft Apricorn Balls. **Pokémon Center crafting** in the shared hub is the preferred direction ([World-10](DESIGN-WORLD.md#world-10-shared-pokémon-center-hub)); a distributed crafting system remains a fallback if the hub is not used.

### More Apricorn trees

We would like **additional Apricorn trees** across Johto and Kanto so harvesting is not tied to vanilla placement alone. Trees are **field objects placed when the map loads**, not part of map geometry — see [Technical investigation](#technical-investigation) for remaining authoring and save-state work.

## Ball design philosophy

**Shop balls** — readily available, generally weaker or reliable bonuses; useful without one infinitely purchasable ball dominating every capture.

**Apricorn balls** — renewable but resource-limited, with stronger specialized bonuses.

Intended to avoid: *"Buy 99 Quick Balls and throw one at everything."*

## Shop balls

<!-- HTML table: pipe tables cannot set column width; colgroup gives a wider effect column in IDE preview -->
<table>
<colgroup>
<col style="width:16%">
<col style="width:10%">
<col style="width:74%">
</colgroup>
<thead>
<tr><th>Ball</th><th align="right">Maximum</th><th>Effect</th></tr>
</thead>
<tbody>
<tr><td>Poké Ball</td><td align="right">1×</td><td>Standard</td></tr>
<tr><td>Great Ball</td><td align="right">1.5×</td><td>Standard</td></tr>
<tr><td>Ultra Ball</td><td align="right">2×</td><td>Standard</td></tr>
<tr><td>Timer Ball</td><td align="right">4×</td><td>Increasing bonus during long battles</td></tr>
<tr><td>Repeat Ball</td><td align="right">3×</td><td>Bonus against previously caught species</td></tr>
<tr><td>Net Ball</td><td align="right">3×</td><td>Bonus against Water or Bug Pokémon</td></tr>
</tbody>
</table>


## Balls removed from the roster

<table>
<colgroup>
<col style="width:22%">
<col style="width:78%">
</colgroup>
<thead>
<tr><th>Ball</th><th>Why dropped</th></tr>
</thead>
<tbody>
<tr><td>Heal Ball</td><td>Unnecessary — newly caught Pokémon are auto-healed (<a href="DESIGN-BATTLES.md#recovery">Battle-1</a>).</td></tr>
<tr><td>Luxury Ball</td><td>Role absorbed by redesigned Friend Ball.</td></tr>
<tr><td>Nest Ball</td><td>Overlaps Level Ball conceptually.</td></tr>
<tr><td>Dive Ball</td><td>Water-capture overlap with Net ball.</td></tr>
<tr><td>Lure Ball</td><td>Water-capture overlap with Net ball.</td></tr>
</tbody>
</table>


## Apricorn balls

Colours signal ball identity rather than vanilla Apricorn associations. **Grey** and **Purple** are intentionally new — a signal to HGSS veterans that the system changed. Both colours can be harvested on Route 37. The table lists the Center’s recipes and the proposed capture effects.

<table>
<colgroup>
<col style="width:10%">
<col style="width:14%">
<col style="width:12%">
<col style="width:64%">
</colgroup>
<thead>
<tr><th>Apricorn</th><th>Ball</th><th align="right">Maximum</th><th>Proposed effect</th></tr>
</thead>
<tbody>
<tr><td>🔴 Red</td><td>Fast Ball</td><td align="right">5× / 10× beasts</td><td>~1–5× by base Speed; <strong>10×</strong> vs Johto roaming beasts (Raikou, Entei, Suicune where implemented). Speed/weight curves TBD.</td></tr>
<tr><td>🩶 Grey</td><td>Heavy Ball</td><td align="right">5×</td><td>~1–5× by weight. Thresholds TBD.</td></tr>
<tr><td>🩷 Pink</td><td>Love Ball</td><td align="right">8×</td><td>3× opposite gender; 8× opposite gender + compatible Egg Group.</td></tr>
<tr><td>🟢 Green</td><td>Friend Ball</td><td align="right">8×</td><td>8× vs families with a friendship evolution (whole family qualifies); caught mon starts at <strong>200</strong> friendship.</td></tr>
<tr><td>🟡 Yellow</td><td>Level Ball</td><td align="right">8×</td><td>Scales with player's level advantage (vanilla concept, possibly smoother curve). Formula TBD.</td></tr>
<tr><td>🟣 Purple</td><td>Dream Ball</td><td align="right">4×</td><td>Sleeping target (lower cap because Sleep is already strong).</td></tr>
<tr><td>🔵 Blue</td><td>Quick Ball</td><td align="right">5×</td><td>First turn only.</td></tr>
<tr><td>⚫ Black</td><td>Dusk Ball</td><td align="right">~7×</td><td>~4× at night; in caves, scales with depth (~4× shallow → ~7× deepest). Floor mapping TBD.</td></tr>
</tbody>
</table>

## Other ball ideas

- **Precision Ball** — increased catch rate when the target has exactly **1 HP** remaining.
- **Weather Ball** — increased catch rate during active weather (rain, sun, hail, sandstorm).
- **Pokédex Ball** — catch rate scales with **Pokédex completion percentage**.
- **Reversal Ball** — catch multiplier rises as the species' **base catch rate** falls (rarer species easier to catch).

## Technical investigation

Before implementation:

- inventory/data representation;
- crafting UI and locations;
- tree objects and refresh logic;
- custom Ball formulas in hg-engine;
- cave-depth detection for Dusk Ball;
- compatibility with existing item data and shops.

**More trees (existing colours):** **Confirmed** — Apricorn trees are **not** baked into map terrain or collision art; they are **field objects added after the map loads** (same class as other overworld interactables). Adding trees should not require [Future-4](#future-4-map-editing--world-connectivity-wishlist)-style geometry edits, though **placing objects and wiring harvest scripts** across routes is still non-trivial.

**New Apricorn colours:** Route 37 has purple and grey trees in place of its red and black trees. Both new colours go into the Bag. The Pokémon Center crafter uses the eight recipes above. White Apricorns remain in the Bag. The ball-effect rebalance is still pending.

**Refresh economy** ties to [World-9](DESIGN-WORLD.md#world-9-accelerated-daynight-cycle) and per-tree save state (yield, regrowth timers).

## Open design questions

- Exact Apricorn tree refresh rate.
- Exact Apricorn crafting mechanism and locations.
- Fast Ball Speed curve; Heavy Ball weight thresholds; Level Ball formula; Dusk Ball depth mapping.
- Whether any removed shop balls return in a revised roster.

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

# Future-7. Generated trainer & Gym parties

### Randomize species

Replace party species with **random eligible species** from the available dex ([Wilds-5](DESIGN-WILDS.md#wilds-5-pokémon-generations--content-scope)), then apply the same stage rules as release scaling ([Battle-2](DESIGN-BATTLES.md#trainer-scaling-release)) so the chosen form fits the level band.

## Trainer party size vs badge count

Scaling **how many** Pokémon appear on trainer teams by badges (e.g. a late-game Falkner with four birds instead of two) means **generating** new species per slot, not only re-leveling vanilla parties. Same dependency as species randomization above — **deferred** with Future-7. Release keeps **vanilla authored party sizes** ([Battle-1 § Equal Party sizes](DESIGN-BATTLES.md#equal-party-sizes)).

## Gym rosters
Gyms (both trainers and leaders) are **monotype by default**, with exceptions:

| Leader | Gym type(s) for hints / filters | Roster notes |
|--------|--------------------------------|--------------|
| Whitney | **Normal** + **Fairy** | |
| Morty | **Ghost** + **Dark** | |
| Brock | **Rock** / **Ground** | Vulpix line |
| Blue | **Flexible** | No Specialty |
| Jasmine | Steel | Ampharos line |
| Misty | Water | Togepi line |
| Blaine | Fire | Rhydon line |

All other Leaders use their vanilla Gym type only.

## TMs and Held Items
Once a trainer's team is generated, we also give the trainer some TMs randomly, and teach them to their team where appropriate. TM list will need to be curated so no useless TMs are taught. Number and Quality of TMs should increase as Badge count increases. Gym trainers should have more of that Gym's type of TMs. Gym Leaders should get an additional boost of Number and Quality of TMs.

## IVs, EVs, and Nature

Scale trainer **EVs** with badges. **Gym Leaders** have higher **IVs** than ordinary trainers. **Nature** agrees with the EV spread and whether the set is physical or special.

## Trainer class

Class biases the species pool and how finished the set is. A late-game Youngster and a late-game Ace Trainer can share a badge count and still differ.

## Abilities

| Who | Hidden Ability |
| --- | -------------- |
| Wild Pokémon | **10%** |
| Ordinary trainers | **20%** |
| Gym trainers | **30%** |

**Ability tiers.** Rank abilities into tiers, then use those tiers to set the odds for trainer and Gym Leader Pokémon.

**Set synergy.** Swift Swim + Drizzle, Guts + Flame Orb, Choice Band − Swords Dance.

**Further considerations:** PP, form, gender, friendship, ball, shiny.

## Technical investigation

- random species for generated teams;
- monotype generation with curated exceptions.
- tms and held items
- badge-scaled EVs, higher Gym Leader IVs, and natures matched to the spread
- trainer-class bias for species and set quality
- hidden-ability rates, ability-tier odds, and set synergy

---

# Future-8. Dynamic battle rosters & universal PC

## Dynamic roster rules

**Each trainer's entire collection is their bench. The actual battle roster forms dynamically as Pokémon are revealed.**

Suppose a battle is 4v4. The player does not choose four Pokémon before battle. They initially choose one send-out; the opponent does the same.

Whenever the player may send out or switch, they may select:

1. a Pokémon already committed to this battle; or
2. an unused Pokémon from their entire collection.

The first time a unique Pokémon enters, it **permanently consumes one roster slot**. After the agreed number of unique Pokémon have entered, **the roster is locked**. Fainted Pokémon continue to occupy slots. The opponent follows the same rules.

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




# Future-9. Time advancement

The player should be able to deliberately advance time rather than waiting.

### Resting at Pokémon Centers / hotels
Allows controlled advancement of time. **Pokémon Center rest menus** live in the shared hub ([World-10](DESIGN-WORLD.md#world-10-shared-pokémon-center-hub)); hotels and other inns may share the same rest rules where they exist in the world.

### Portable resting
A tent, sleeping bag, camping system, or similar mechanic can potentially allow resting outside 
towns. Exact implementation TBD.

---

# Future-10. Living trainers & interactions

**Not required for initial release.** Initial release: static vanilla trainers with [Battle-2](DESIGN-BATTLES.md#trainer-scaling-release) scaling. Renewable TMs via [World-4](DESIGN-WORLD.md#world-4-tms) / [World-6](DESIGN-WORLD.md#world-6-shops), not trainer buy/sell economy.

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

Trainers may tell the player where undiscovered species can be found (ecology data). **Gym Leaders:** structured first-clear hint — [Future-7](#future-7-generated-trainer--gym-parties).

### Pokémon trades / item trading

Some trainers request trades or buy/sell items (sink for duplicates; source for rare TMs / held gear).

### TMs

Some trainers provide renewable access to otherwise rare TMs ([World-4](DESIGN-WORLD.md#world-4-tms)) — alternative to putting everything in static marts.

### Gym advice / other quests

Information about nearby undefeated Gyms or scaled teams; additional lightweight interactions TBD.

## Field population (living trainers)

Map-level trainer generation, movement, and placement — distinct from [Battle-2](DESIGN-BATTLES.md#trainer-scaling-release) battle-start scaling; location-weighted distributions and non-battle interactions.

## Technical investigation

- map spawning; movement; persistence; generated identities; badge counts; generated collections; map transitions; save-state requirements;
- ecology-linked location requests; reward economy; trade and item-exchange UI; TM distribution hooks.

---

# Future-11. Pokémon Research Society

A shared research organization with representatives in every Pokémon Center. The representative is a service in the shared hub ([World-10](DESIGN-WORLD.md#world-10-shared-pokémon-center-hub)), so the player can register finds and claim rewards from any Center.

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

**Wobbuffet** (tier 2) and **Eevee** (tier 3) are also Game Corner prizes ([World-4](DESIGN-WORLD.md#pokémon-prizes)).

## Pokédex research

The same organization could also manage Pokédex completion rewards ([World-8](DESIGN-WORLD.md#pokédex-milestone-rewards)).

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

Collect all **28 Unown forms** across Johto and Kanto. Each **unique form** registered in the Pokédex **permanently** improves **all Unown** in the player’s collection. Completing forms also improves **Hidden Power globally** for every Pokémon (not only Unown).

## Progression

Scaling is linear from 0 unique forms registered to 28.

| Track | At 0 forms | At 28 forms |
| ----- | ---------- | ----------- |
| **BST** | 44 / 66 / 44 / 66 / 44 / 44 (**308** total) | 100 / 150 / 100 / 150 / 100 / 100 (**700** total) |
| **Hidden Power (all Pokémon)** | **60** BP, fixed base power (not IV-dependent) | **100** BP, same fixed-power rule |
| **Catch rate (Unown)** | **255** | **3** |

- **Hidden Power type** stays **IV-dependent** until the player sets it with an Arceus Plate ([Future-11](DESIGN-FUTURE.md#hidden-power)). The plate is not consumed ([World-8](DESIGN-WORLD.md#world-8-item-acquisition-channels)).
- **Ability (Unown only):** custom ability — all **damaging** moves deal **+33%**; Unown is **typeless** (no weaknesses, resistances, or STAB).
- **Wild held item:** **50%** chance to hold **TM10 (Hidden Power)**.

## Moveset

| Level | Moves |
| ----- | ----- |
| 1 | Secret Power, Ancient Power, Ominous Wind, Silver Wind, Hidden Power |
| 15 | Teleport |
| 30 | Safeguard |
| 45 | Recover |
| 60 | Perish Song |

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
| Cinnabar | MAGMA |

### Endgame and exclusive forms

- **Q**, **Z**, **!**, **?** — one each from a **Johto roamer**, **Kanto roamer**, **Mt. Silver**, and **Cerulean Cave** (exact assignments TBD).
- **V** and **Y** — **Victory Road only** ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) **16-badge** gate).

### Wild encounter rules

- At each designated location, **5%** of wild encounters are **Unown** instead of the normal slot species.
- When Unown is selected, pick **uniformly** among that location’s allowed forms; otherwise use normal encounter tables.
- Applies to **grass**, **cave**, **Surf**, **Rock Smash**, and **Headbutt**.
- **Ruins of Alph** needs a special case — vanilla-style **100% Unown** areas remain; do not double-stack the 5% rule blindly.

### UX and postgame hooks

- **Caught indicator:** Prefer showing the wild **Poké Ball icon** for Unown **only when that exact form** was caught before — not when any Unown was caught.
- Unown collection may grant **clues** or **unlock options** for legendary / mythical postgame content ([Future-14](DESIGN-FUTURE.md#future-14-other-potential-changes), [Future-11](DESIGN-FUTURE.md#future-11-pokémon-research-society) — TBD).
- The research society may also give a reward for each newly registered Unown form ([Future-11](DESIGN-FUTURE.md#pokédex-research)).

## Open design questions

- How global Hidden Power BP scales per form vs only at milestones.
- Roamer / Mt. Silver / Cerulean Cave assignments for **!** and **?**.

---

# Future-14. Other potential changes

Ideas that do not have their own `Future-*` section yet.

- **Post-battle party heal timing** — [Battle-1](DESIGN-BATTLES.md#recovery) expects recovery as soon as a battle ends. Initial release applies heal on the **first overworld step** (workaround for battle-overlay crashes). Move heal to **end of battle / return to field** so the party, follower, and back-to-back trainer fights match design (no heal gap on turn-in-place or chained trainers).
- **Game Corner Coin income** — prize menus work today; earning Coins still means **Voltorb Flip** ([World-4 § Coin income](DESIGN-WORLD.md#coin-income-not-implemented)). Longer term: buy Coins for ¥, trainer payouts, amulet coin, Voltorb Flip changes, dept-store bundles — exchange rate and UI TBD.
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
| [Future-8](#future-8-dynamic-battle-rosters--universal-pc) Dynamic rosters | 10 | 5 | 3 | 4 | 5 | 5 | [Future-7](#future-7-generated-trainer--gym-parties) |
| [Future-10](#future-10-living-trainers--interactions) Living trainers | 9 | 5 | 4 | 4 | 4 | 4 | [Future-7](#future-7-generated-trainer--gym-parties) |
| [Future-7](#future-7-generated-trainer--gym-parties) Generated parties | 9 | 4 | 4 | 2 | 1 | 4 | — |
| [Future-1](#future-1-apricorn-economy--poké-ball-rebalance) Apricorn economy | 7 | 3 | 4 | 3 | 2 | 4 | — |
| [Future-12](#future-12-unown-collection-quest) Unown quest | 7 | 2 | 3 | 2 | 4 | 2 | — |
| [Future-3](#future-3-unlimited-learned-moves) Unlimited moves | 6 | 3 | 3 | 5 | 5 | 5 | — |
| [Future-5](#future-5-gym-leader-ecology-hints) Gym Leader Ecology Hints | 5 | 2 | 2 | 2 | 3 | 2 | — |
| [Future-9](#future-9-time-advancement) Time advancement | 4 | 1 | 1 | 1 | 3 | 1 | — |
| [Future-11](#future-11-pokémon-research-society) Pokémon Research Society | 3 | 2 | 3 | 3 | 2 | 2 | — |
| [Future-4](#future-4-map-editing--world-connectivity-wishlist) Map connectivity | 2 | 4 | 2 | 4 | 1 | 3 | — |
| [Future-2](#future-2-full-moon-system) Full moon | 1 | 1 | 1 | 2 | 2 | 1 | Moon Ball  wants [Future-1](#future-1-apricorn-economy--poké-ball-rebalance) |
