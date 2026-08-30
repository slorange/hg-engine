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

**Status: DECIDED**

The player chooses their starting city from locations throughout Johto and Kanto.

The exact list of selectable starting locations is TBD, but the intention is broad freedom rather than a small set of traditional starting towns.

Every available starting city must provide reasonable access to:

- appropriately levelled encounters;
- early trainer content;
- necessary services;
- transportation;
- a viable first Gym challenge.

## Starter selection

**Status: TBD**

Options under consideration include:

- any non-legendary Pokémon;
- a large curated starter pool;
- location-specific starter pools;
- some combination of the above.

Do not assume unrestricted starter selection until this is finalized.

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

Thematically appropriate exceptions are allowed.

Examples:

- Jasmine may use Ampharos despite it not being Steel-type.
- Brock could potentially use a thematically appropriate non-Rock Pokémon such as Ninetales.

These should be deliberate characterization/design decisions rather than random violations of the Gym's identity.

## Rematches

**Status: DECIDED**

Gym Leaders can be rematched.

Rematches use the player's **current badge tier**, rather than repeating the difficulty at which the Gym was originally defeated.

Gym rematches are also a renewable source of that Gym's TM.

There is no intended hard limit on the number of rematches/TM copies.

---

# 7. Badge-Based Level Caps

**Status: DECIDED; exact intermediate curve TBD**

Pokémon levels are capped according to the player's badge progression.

The purpose is not merely difficulty control.

Level caps are fundamental to the collection-oriented progression system.

Once the player's primary Pokémon reach the current cap, additional experience naturally encourages the player to develop more Pokémon rather than continuously overlevelling a small permanent party.

## Current progression targets

Before challenging Badge #1:

**Level cap: 10**

Each subsequent Gym generally increases the available level range by approximately:

**3–4 levels**

Before challenging Badge #16:

**Level cap: 70**

After obtaining all 16 badges:

**Level cap: 80**

Victory Road and the Elite Four therefore operate within the level 70–80 endgame progression.

After becoming Champion:

**The level cap is removed.**

Pokémon can then progress normally toward Level 100 during postgame content.

The exact cap associated with badges #2 through #15 remains TBD and should eventually be designed around:

- encounter levels;
- evolution levels;
- learnsets;
- Gym difficulty;
- trainer progression;
- overall pacing.

Do not invent the intermediate curve without explicit design work.

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

**Status: DECIDED conceptually; exact generation system TBD**

Ordinary trainer Pokémon are generated rather than relying primarily on fixed vanilla teams.

A trainer may have a generated collection larger than the number of Pokémon ultimately used in a battle.

For example:

> Trainer Maya owns 12 relevant Pokémon.
>
> The battle is 4v4.
>
> During the battle she dynamically commits up to four Pokémon from that collection.

However, persistent full collections are not mandatory.

Another possible implementation is to generate unrevealed Pokémon **on demand** as the trainer commits additional roster slots.

This would allow trainer AI/difficulty logic to generate an appropriate response to what the player has revealed.

For example, if the player reveals a Pokémon that strongly counters everything the opponent has shown, the trainer's next unrevealed Pokémon could be generated from an appropriate counter pool.

The player cannot see the opponent's unused collection, so either implementation can produce the same visible behaviour.

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

Most traditional story roadblocks should be removed.

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
| Surf / fishing encounters | Water wilds | Own tables per map |
| Headbutt trees | Wild mons from trees | Own data files; good candidate for gated/high-value encounters |
| Cut trees / smashable rocks / Strength boulders | Map obstacles | Script/map event gated today by badge + knowing the move |
| Whirlpool / Waterfall / Rock Climb tiles | Traversal gates | Same |

### Design questions to resolve

- Which of the eight HMs unlock at which **badge count**?
- Does **Flash** follow the same collection-field rules as HMs, or stay “know the move”?
- Is **Headbutt** always available once obtained, badge-gated, or species-collection like HMs?
- Keep **Sweet Scent / Dig / Teleport** as learn-move field tools, convert to collection tools, or remove once auto-heal / transport exist?
- Should **Headbutt** / **Rock Smash** encounter pools be used as early vs gated content tiers (similar to grass gating ideas)?

Mark decisions here as they are made; do not invent unlock order without explicit design.

---

# 22. TMs

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

# 23. Accelerated Day/Night Cycle

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

# 24. Apricorn Economy & Poké Balls (addon)

**Status: ADDON — see [`DESIGN2.md`](DESIGN2.md)**

Apricorn tree refresh, shop ball rebalance, removed balls, and all Apricorn ball formulas live in the addon design doc. **Not core to the open-world ROM** — vanilla shop balls remain until that addon is deliberately scheduled.

Core touchpoints only:

- Accelerated clock ([§23](#23-accelerated-daynight-cycle)) — shared with addon tree refresh if implemented later.
- Auto-heal on capture ([§17](#17-healing-and-attrition)) — rationale for removing Heal Ball in the addon doc.
- Mom's open-world Apricorn Box (`OPENWORLD_STARTING_ITEMS`) — inventory convenience only, not the full rebalance.

Do not implement ball changes from DESIGN2 unless explicitly requested.

---

# 25. Wild Encounters

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

# 26. Pokémon Generations / Content Scope

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

# 27. Design Principles

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

# 28. Major Technical Investigations

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

Questions include:

- identifying current badge count;
- scaling wild-adjacent trainer levels and teams by badge tier;
- dynamic trainer generation;
- dynamic Gym generation;
- battle-size selection;
- rematches;
- TM rewards;
- monotype generation with curated exceptions.

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

# 29. Initial Development Philosophy

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

# 30. Current Technical Baseline

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
| Route 4 ledge boost ($100 hiker) | Implemented | Coords may need in-game tuning |
| Route 29→46 gate (2 badges) | PoC verified | Guard-style encounter gating template |
| Route 36 Sudowoodo removed | Verified | 0-badge Violet ↔ Goldenrod path |
| Route 32 badge gate removed | Verified | 0-badge path toward Union Cave |
| Mahogany rocket arc skipped | Verified | Town accessible on load |

Reusable recipes for badge gates, ferry NPCs, and story NPC removal live in **`documentation/HACK-NOTES.md`**.

### Not yet started (core design priorities)

- Badge-scaled Gym and trainer difficulty (§§5–7).
- Starting city selection (§4).
- Living trainers, dynamic rosters, universal PC, collection-based HMs.

The basic development loop is proven:

> **edit source/data → Docker build → test.nds → DeSmuME → verify**

Docker remains the known-good build path.

---

# 31. Open Design Questions

The following are intentionally unresolved.

- Exact starter system.
- Exact selectable starting cities.
- Who determines trainer battle size.
- Exact trainer generation algorithms.
- How aggressively NPCs counter-pick.
- Whether generated trainers have persistent full collections or generate unrevealed Pokémon on demand.
- Exact Gym roster generation.
- Exact badge-by-badge level-cap curve between Lv.10 and Lv.70.
- Exact EXP formula.
- Whether fainted Pokémon's lost EXP is redistributed.
- Exact wild encounter scaling/gating model.
- Exact HM progression order.
- Exact transportation prices.
- Exact Pokémon Center service list.
- Exact accelerated-time resting mechanics.
- Included Pokémon generations/content.
- Scope and structure of traditional story content.

(Ball/Apricorn V2 questions: [`DESIGN2.md`](DESIGN2.md) §18. V3/V4 deferred scope also in DESIGN2.)

These questions should remain open until deliberately resolved.

---

# 32. Deferred Scope (V2–V4)

Features deliberately outside **core** scope are documented in [`DESIGN2.md`](DESIGN2.md):

- **V2** — Apricorn economy and Poké Ball rebalance
- **V3** — Full Moon world system and Moon Ball
- **V4** — Unlimited learned moves (anime-style move retention)

These should not influence initial core architecture unless doing so is inexpensive and clearly prevents future incompatibility.

---

# 33. One-Sentence Game Identity

> **Pokémon Wandering Heart is an open-world HGSS journey where the player builds a collection rather than a fixed party, travels freely through Johto and Kanto, challenges all 16 scaling Gyms in any order, and encounters other trainers undertaking dynamic journeys of their own.**