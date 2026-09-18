# Pokémon Wandering Heart — Design Index

> Source of truth for **Pokémon Wandering Heart** core design. Detailed specs live in sub-documents with prefixed section IDs (`Vision-1`, `World-2`, `Battle-4`, …).
>
> **This index is NOT permission to implement everything described in the sub-docs.**

## Document map


| Document                                                     | Prefix     | Topics                                                           |
| ------------------------------------------------------------ | ---------- | ---------------------------------------------------------------- |
| `[DESIGN-VISION.md](DESIGN-VISION.md)`                       | `Vision-*` | Core vision, open-world rules, starting city/starter |
| `[DESIGN-WORLD.md](DESIGN-WORLD.md)`                         | `World-*`  | Travel, gating, HMs, living trainers, shops, Centers, TMs, evolution   |
| `[DESIGN-WILDS.md](DESIGN-WILDS.md)`                         | `Wilds-*`  | Ecology seed, wild levels, fishing, content scope                |
| `[DESIGN-BATTLES.md](DESIGN-BATTLES.md)`                     | `Battle-*` | Gyms, level caps, trainer generation, battle rosters, EXP, QoL  |
| `[DESIGN-STORY.md](DESIGN-STORY.md)`                         | `Story-*`  | Story policy, vanilla cleanup backlog                            |
| `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)`                       | `Future-*` | Deferred addons (balls/Apricorns, Full Moon, moves, maps, …)     |
| `[documentation/HACK-NOTES.md](documentation/HACK-NOTES.md)` | —          | Implementation recipes, IDs, verified patches                    |

## Sections in this document

| Section |
| ------- |
| [Index-1. Instructions for Coding Agents](#index-1-instructions-for-coding-agents) |
| [Index-2. Current Technical Baseline](#index-2-current-technical-baseline) |
| [Index-3. Open Design Questions](#index-3-open-design-questions) |
| [Index-4. Game Identity](#index-4-game-identity) |
| [Index-5. Known Bugs](#index-5-known-bugs) |

---



# Index-1. Instructions for Coding Agents

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
- **Git is read-only for agents** unless the user explicitly asks otherwise: do not commit, push, checkout, stash, rebase, reset, or otherwise change repo state. Using `log`, `status`, `diff`, and `show` for context is fine.
- **The user relies on agents to run builds** when verifying work. Follow [Build and verification](documentation/HACK-NOTES.md#build-and-verification) in HACK-NOTES. First-time toolchain setup: [README.md](README.md).

The design statuses used in this document are:

**DECIDED** — Current intended design. Numbers may still be balanced later.

**TBD** — The design has deliberately not been decided yet.

**TECHNICAL UNKNOWN** — Desired behaviour is understood, but feasibility/implementation in HGSS/HG-Engine needs investigation.

**IMPLEMENTED** — In the ROM and verified in-game (or enabled via config with a documented hook). Details in [Index-2](DESIGN.md#index-2-current-technical-baseline), [`CHANGELOG.md`](CHANGELOG.md), or `HACK-NOTES.md`.

**PARTIALLY IMPLEMENTED** — Some of the design ships today (often a v1/PoC or phased milestone); the section or Index-2 notes what remains.

**FUTURE / PARKING LOT** — Deferred to [`DESIGN-FUTURE.md`](DESIGN-FUTURE.md) (`Future-*`); not initial core scope.

Broken or incorrect behaviour in the current ROM is tracked in [Index-5](#index-5-known-bugs), not as design status or incomplete features.

---

---



# Index-2. Current Technical Baseline

As of September 2026:

### Build and toolchain

- HG-Engine builds reliably via **Docker** (`make -j24` → `test.nds`; DeSmuME verification). See [Build and verification](documentation/HACK-NOTES.md#build-and-verification).
- Field scripting workflow is established (see HACK-NOTES).
- Map identity pitfalls (`map header ≠ scr_seq member ≠ zone_event member`) are documented in HACK-NOTES.



### Core battle / QoL (verified in-game)


| Feature                         | Status   | Design ref |
| ------------------------------- | -------- | ---------- |
| Post-battle heal (HP/PP/status) | Verified — [KB-2 tentatively resolved](DESIGN.md#monitoring-tentatively-resolved) | [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition) |
| Full-party EXP share (interim)  | Partial | [Battle-6](DESIGN-BATTLES.md#battle-6-exp-share) |


Hooks and patches: [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md) (Heal after every battle, Full party EXP share).

### Open-world shell (verified or implemented)


| Feature | Status | Design ref |
| ------- | ------ | ---------- |
| Mom starting grants (Ticket, Pass, Apricorn Box, shoes, dex) | Verified | [Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon) |
| Starting city picker (18 cities; home doors + runtime routing) | Verified | [Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon) |
| Starter pick (12-option menu, gens 1–4) | Verified | [Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon) |
| Dev-only testing grants (e.g. Fly from Mom) | Implemented | Disable before release — see HACK-NOTES |
| Magnet Train (Goldenrod ↔ Saffron) | Verified | [World-1](DESIGN-WORLD.md#world-1-world-transportation) |
| Route 42 paid ferry | Verified | [World-1](DESIGN-WORLD.md#paid-ferry-npcs) |
| Route 40 ↔ Cianwood paid ferry | Verified | [World-1](DESIGN-WORLD.md#paid-ferry-npcs) |
| Route 31 ↔ Route 45 Dark Cave paid ferry | Implemented | [World-1](DESIGN-WORLD.md#paid-ferry-npcs) |
| Route 4 ledge boost ($100 hiker) | Verified | [World-1](DESIGN-WORLD.md#world-1-world-transportation) |
| Route 29→46 gate (2 badges) | PoC | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) — template only |
| Route 36 Sudowoodo removed | Verified after re-enter — [first-visit bug](DESIGN.md#index-5-known-bugs) | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Route 32 badge gate removed | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Mahogany Rocket arc skipped | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Surge / Erika Cut trees removed | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Jasmine / Olivine Lighthouse (Secret Medicine) | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |


Field recipes: [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md).

### Trainer scaling (verified or enabled)

| Feature | Status | Design ref |
| ------- | ------ | ---------- |
| Badge-band trainer levels | Verified | [Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented) |
| Level-appropriate moves | Verified | [Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented) |
| Same-line stage adjust | Verified | [Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented) |
| Gym Leaders at level cap | Partial | [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters) — Gym trainer type filter → [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties) |
| Random species / dynamic battles / living trainers | Deferred | [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties), [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc), [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions) |

Implementation: [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md) § **Trainer level scaling**.




### Story and script policy

See [Story-1](DESIGN-STORY.md#story-1-story-and-script-content). Surge/Erika/Jasmine verified; remaining gym rows (Bugsy, Clair, Misty, Blue, **Blaine**), opening strip, **rival removal**, HM quest cleanup, and Rocket extension still open. **Paid ferry NPCs:** [World-1](DESIGN-WORLD.md#paid-ferry-npcs). Obsolete vanilla leftovers tracked in [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog).

### Initial release scope (finish PoCs + polish)

Work toward a shippable ROM without [DESIGN-FUTURE.md](DESIGN-FUTURE.md) north-star systems (generated parties, [Future-8](DESIGN-FUTURE.md#future-8-dynamic-battle-rosters--universal-pc), [Future-5](DESIGN-FUTURE.md#future-5-per-save-wild-ecology-shuffle), [Future-10](DESIGN-FUTURE.md#future-10-living-trainers--interactions), etc.).

- **Gym trainer type filter** (remainder of release scaling) — [Future-7](DESIGN-FUTURE.md#future-7-generated-trainer--gym-parties); Leader cap done ([Battle-4](DESIGN-BATTLES.md#trainer-scaling-implemented)).
- **New Bark door swap** when start city ≠ New Bark ([Vision-3](DESIGN-VISION.md#vision-3-starting-location-and-pokémon), [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)).
- Collection-based HMs + Gym Leader grants ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)) — HM pilot partial.
- **Shop pass** — **implemented** in `src/field/mart.c` ([World-7](DESIGN-WORLD.md#world-7-shops)); verify in playtest. Still open: **Headbutt TM** slot, Link Cable shelves, Mom resist berries.
- **Game Corner Coin income** — prize TMs wired; earning Coins still requires Voltorb Flip ([World-5 § Coin income](DESIGN-WORLD.md#coin-income-not-implemented)).
- Level caps (`IMPLEMENT_LEVEL_CAP`) — after scaling prototype is stable in playtesting.
- **Wilds-1** + **Wilds-2** — near complete; remaining hooks (Safari, Contest, etc.).
- **Paid ferry NPCs** — [World-1](DESIGN-WORLD.md#paid-ferry-npcs).
- Story implementation pass ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)) — opening skip, rival removal, Rocket extension, remaining gym rows.
- **Vanilla cleanup pass** ([Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)) — strip superseded NPCs, quests, HM fetch chains, and HM-teaching scripts.
- Known bugs [Index-5](#index-5-known-bugs).

The basic development loop is proven:

> **edit source/data → Docker build → test.nds → DeSmuME → verify**

Docker remains the known-good build path.

---

---



# Index-3. Open Design Questions

The following are intentionally unresolved.

- Exact starter system — **v1 twelve-option menu implemented**; long-term pools TBD.
- Displaced-interior **story/NPC cleanup** ([Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)) — home-door warps route correctly; vanilla scripts inside old houses may still confuse players.
- Exact Pokémon Center service list ([World-4](DESIGN-WORLD.md#world-4-pokmon-centers)).
- Per-mart **tuning** after the first `mart.c` pass ([World-7 § What’s left](DESIGN-WORLD.md#whats-left-to-do)).
- **Game Corner Coin source** — replace or supplement Voltorb Flip ([World-5 § Coin income](DESIGN-WORLD.md#coin-income-not-implemented)); exchange rate / UI TBD.
- **Headbutt TM slot**, tutor removal, learnset audit, and badge-gated shop stock for Flash / Headbutt ([World-3](DESIGN-WORLD.md#headbutt--flash--battle-teaching-vanilla-vs-target)) — vanilla has **no** Headbutt TM.
- **Kanto Fly map** — enable Kanto fly destinations when visiting Kanto early (Magnet Train / open world); vanilla UI stays Johto-only until likely E4 clear or SS Aqua story ([HACK-NOTES § Fly map](documentation/HACK-NOTES.md#fly-map--kanto-destinations-not-yet)).
- Clair Dragon's Den: remove trial vs HM-free path ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)).
- Trade evolutions without items: Link Cable vs fixed levels ([World-6](DESIGN-WORLD.md#world-6-evolution-methods-trade--stones)).
- Special-trainer roster (Red ~100 / Pikachu buff, E4 first-clear levels) vs badge-tier cap at 80 ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps)).

(Deferred systems and addons: [`DESIGN-FUTURE.md`](DESIGN-FUTURE.md) — [Future-1](DESIGN-FUTURE.md#future-1-apricorn-economy--poké-ball-rebalance) through [Future-13](DESIGN-FUTURE.md#future-13-expanded-stone-mechanics).)

These questions should remain open until deliberately resolved.

---

# Index-4. Game Identity

**Pokémon Wandering Heart** is HeartGold and SoulSilver reimagined as a trainer’s road trip: you are one of many travelers, not the center of a scripted plot—free to roam Johto and Kanto, grow a roster far beyond six Pokémon, and take on all sixteen Gyms when you are ready, in an order that fits your route.

**Initial Release:** Pick a starting city and a starter, then play through a stripped-down HGSS where major story gates and fetch quests are gone or shortened. Wild levels scale with distance from the starting city, and trainer levels scale with your badge progress. Post-battle healing and no items from either side for fair battles, EXP Share to reduce grinding, and badge-based level caps to ensure difficulty. HMs awarded by Gym leaders rather than quests. Shops sell renewable TMs and evolution items. The playable dex is Generations I–IV plus a few additions.

**Future Plans:** Per-save **wild ecology** so runs feel different; **generated trainer and Gym parties** and smarter Gym scaling; **living trainers** who move and rematch; **dynamic battles** where you pull from the full PC instead of a fixed party of six; a faster **day/night clock** and **Apricorn crafting** economy; **unlimited moves** and **map connectivity** edits

---

# Index-5. Known Bugs

Regressions and incorrect behaviour in the **current ROM**. This is not [Index-2](#index-2-current-technical-baseline) incomplete work, [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog) cleanup, or open design in [Index-3](#index-3-open-design-questions).

When a bug is fixed, remove its row here and note the fix in [`CHANGELOG.md`](CHANGELOG.md) if player-visible.

| ID | Symptom | Notes |
| -- | ------- | ----- |
| **KB-1** | **Route 36 Sudowoodo** still blocks the road the **first** time you enter the route after load. Leaving and re-entering hides the tree as intended. | Hide flag runs on map load (`scr_seq_R36_010` / `FLAG_HIDE_ROUTE_36_SUDOWOODO`); object visibility likely applies one visit late. Recipe: `documentation/HACK-NOTES.md` § **Remove Sudowoodo block (Route 36)**. |

### Monitoring (tentatively resolved)

| ID | Former symptom | Notes |
| -- | -------------- | ----- |
| **KB-2** | Intermittent crash when returning to the field after a battle (historically very rare; roughly once per 70–80+ encounters). | Tentatively fixed Sep 2026: `heal_after_battle.c` with `fight_end_flag` and pointer guards at `Battle_End`. 100+ battle ends without repro; not statistically proven. Recipe: [Heal after every battle](documentation/HACK-NOTES.md#heal-after-every-battle). Design: [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition). |

---

