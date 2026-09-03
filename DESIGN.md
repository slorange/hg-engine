# Pokémon Wandering Heart — Design Index

> Source of truth for **Pokémon Wandering Heart** core design. Detailed specs live in sub-documents with prefixed section IDs (`Vision-1`, `World-2`, `Battle-8`, …).
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
| `[DESIGN-FUTURE.md](DESIGN-FUTURE.md)`                       | `Future-*` | V2–V4 addons (balls, Full Moon, unlimited moves)                 |
| `[documentation/HACK-NOTES.md](documentation/HACK-NOTES.md)` | —          | Implementation recipes, IDs, verified patches                    |


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

**V2 / PARKING LOT** — Interesting idea explicitly excluded from initial scope.

---

---



# Index-2. Current Technical Baseline

As of September 2026:

### Build and toolchain

- HG-Engine builds reliably via **Docker** (`make -j24` → `test.nds`; DeSmuME verification). See [Build and verification](documentation/HACK-NOTES.md#build-and-verification).
- Field scripting workflow is established: **scr_seq**, **zone_event**, **text banks**, Python patch tools, and `narcs.mk` hooks.
- Map identity pitfalls are documented (`map header ≠ scr_seq member ≠ zone_event member`) in `documentation/HACK-NOTES.md`.



### Core battle / QoL (verified in-game)


| Feature                         | Toggle / hook          | Design ref |
| ------------------------------- | ---------------------- | ---------- |
| Post-battle heal (HP/PP/status) | `HEAL_AFTER_BATTLE`    | Battle-2  |
| Full-party EXP share (interim)  | `FULL_PARTY_EXP_SHARE` | Battle-7  |




### Open-world shell (verified or implemented)


| Feature                                                      | Status         | Notes                                                                                                                               |
| ------------------------------------------------------------ | -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Mom starting grants (Ticket, Pass, Apricorn Box, shoes, dex) | Verified       | scr_seq **845**; `OPENWORLD_STARTING_ITEMS`                                                                                         |
| Starting city picker (New Bark / Goldenrod / Saffron)        | Verified (PoC) | Mom script **0**; `patch_zone_event_start_city.py`; dynamic home exit                                                               |
| Starter pick (12-option text menu, gens 1–4)                 | Verified       | Mom script **0**; `give_mon` per branch; not `choose_starter`                                                                       |
| Dev-only testing grants (HM02 Fly from Mom)                  | Implemented    | `OPENWORLD_TESTING_GRANTS` in `include/config.h` — **disable before builds for others or release candidates**                       |
| Magnet Train (Goldenrod ↔ Saffron)                           | Verified       | No power-plant gate; scr_seq **893** / **834**                                                                                      |
| Route 42 paid ferry                                          | Verified       | Reference recipe for paid bypass NPCs                                                                                               |
| Route 4 ledge boost ($100 hiker)                             | Verified       | `2_009` / `2_178`; coords (1270,118)→(1270,116)                                                                                     |
| Route 29→46 gate (2 badges)                                  | PoC verified   | Guard-style encounter gating template                                                                                               |
| Route 36 Sudowoodo removed                                   | Verified       | 0-badge Violet ↔ Goldenrod path                                                                                                     |
| Route 32 badge gate removed                                  | Verified       | 0-badge path toward Union Cave                                                                                                      |
| Mahogany rocket arc skipped                                  | Verified       | Town accessible on load; full Rocket removal per [Story-1](DESIGN-STORY.md#story-1-story-and-script-content)                        |
| Surge / Erika Cut trees removed                              | Verified       | `2_051`, `2_052`, `2_352`; `patch_zone_event_gym_cut_trees.py` — [Story-1](DESIGN-STORY.md#story-1-story-and-script-content)        |
| Jasmine / Olivine Lighthouse (Secret Medicine)               | Verified       | Olivine Mart special clerk (¥500); `FLAG_GOT_SECRETPOTION` on bag add — [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |


Reusable recipes for badge gates, ferry NPCs, and story NPC removal live in `documentation/HACK-NOTES.md`.

### Trainer scaling (verified or enabled)


| Phase                                    | Status            | Toggle / hook                                                                                                    |
| ---------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1 — Rescale vanilla levels by badge band | Verified          | `TRAINER_LEVEL_SCALING`                                                                                          |
| 2 — Level-appropriate moves              | Verified          | `TRAINER_LEVEL_APPROPRIATE_MOVES`                                                                                |
| 3 — Same-line stage adjust               | Verified          | `TRAINER_SPECIES_STAGE_ADJUST`                                                                                   |
| 6 — Gym Leaders at level cap             | Enabled (partial) | `TRAINER_GYM_LEADER_CAP_LEVEL`; Gym trainer type filter still open                                               |
| 4–5, 7–12                                | Not started       | Random species, evolution exclusions, battle size, dynamic rosters, counter-picking, items, TMs, living trainers |




### Story and script policy

See [Story-1](DESIGN-STORY.md#story-1-story-and-script-content). Surge/Erika/Jasmine verified; remaining gym rows (Bugsy, Clair, Misty, Blue, **Blaine**), opening/rival strip, and Rocket extension still open. **Cinnabar / Seafoam ferries:** [World-1](DESIGN-WORLD.md#kanto-island-ferries). Obsolete vanilla leftovers tracked in [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog).

### Not yet started (core design priorities)

- **Gym scaling phase 6 (remainder)** — Gym trainer type filter; Leader curated exceptions.
- **Battle systems phases 7–9** — agreed size, dynamic rosters, counter-picking.
- **New Bark door swap** when start city ≠ New Bark ([Vision-3](DESIGN-VISION.md#vision-3-starting-location), [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)).
- Living trainers ([World-5](DESIGN-WORLD.md#world-5-living-trainers)), dynamic rosters, universal PC ([Battle-6](DESIGN-BATTLES.md#battle-6-dynamic-battle-rosters)), collection-based HMs ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).
- Level caps (`IMPLEMENT_LEVEL_CAP`) — after scaling prototype is stable in playtesting.
- **Wild encounter systems** ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)–[Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps)) — ecology seed, broad level range, distance caps (TBD).
- **Kanto island ferries** (Cinnabar, Seafoam) — [World-1](DESIGN-WORLD.md#kanto-island-ferries).
- Story implementation pass ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)) — opening skip, rival, Rocket extension, remaining gym rows.
- **Vanilla cleanup pass** ([Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)) — strip superseded NPCs, quests, and HM-teaching scripts.

The basic development loop is proven:

> **edit source/data → Docker build → test.nds → DeSmuME → verify**

Docker remains the known-good build path.

---

---



# Index-3. Open Design Questions

The following are intentionally unresolved.

- Exact starter system — **v1 twelve-option menu implemented**; long-term pools TBD.
- Exact selectable starting cities — **v1 three-city picker implemented**; broader list TBD.
- Who determines trainer battle size.
- Exact trainer generation algorithms.
- How aggressively NPCs counter-pick.
- Whether generated trainers have persistent full collections or generate unrevealed Pokémon on demand.
- Exact Gym roster generation.
- Exact EXP formula.
- Whether fainted Pokémon's lost EXP is redistributed.
- Wild ecology: habitat tags, family assignment algorithm, special/static encounter policy ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)).
- Wild level distribution curves within area caps ([Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range)).
- Wild level progression model: **Wilds-3 distance caps** vs **World-2 guard/tile gating** vs hybrid ([Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps), [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)) — **likely Wilds-3 + light World-2** (Victory Road, HMs, endgame).
- Exact HM progression order.
- Exact transportation prices.
- Exact Pokémon Center service list ([World-7](DESIGN-WORLD.md#world-7-pokmon-centers)).
- Per-mart shop inventories and held-item tiers ([World-10](DESIGN-WORLD.md#world-10-shops)).
- Exact accelerated-time resting mechanics.
- Included Pokémon generations/content.
- Rival role ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)).
- Clair Dragon's Den: remove trial vs HM-free path ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)).
- Trade evolutions without items: Link Cable vs fixed levels ([World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones)).
- Whether expanded stone mechanics ([World-9](DESIGN-WORLD.md#world-9-evolution-methods-trade--stones)) ship at all.
- Special-trainer roster (Red ~100 / Pikachu buff, E4 first-clear levels) vs badge-tier cap at 80 ([Battle-4](DESIGN-BATTLES.md#battle-4-badge-based-level-caps)).

(Ball/Apricorn V2+ questions: [`DESIGN-FUTURE.md`](DESIGN-FUTURE.md) — V2 balls, V3 Full Moon, V4 unlimited moves.)

These questions should remain open until deliberately resolved.

---

# Index-4. Game Identity

**Pokémon Wandering Heart** is an open-world HeartGold/SoulSilver journey: build a **collection**, not a fixed party of six; travel freely across Johto and Kanto; challenge all **16 scaling Gyms** in any order; and meet trainers who feel like they are on journeys of their own.

**Battles** are deliberately fair — the same number of Pokémon on each side, **no bag items**, and rosters that form during the fight as you commit slots from your **entire PC**, not just the six in your party. **Wild Pokémon** use a **per-save randomized ecology** (families stay in sensible habitats, but locations shuffle); encounter **levels scale with your chosen starting city** and how far you have travelled from it, so the same map can be early-game or late-game depending on where you began.

---

