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
- Field scripting workflow is established (see HACK-NOTES).
- Map identity pitfalls (`map header ≠ scr_seq member ≠ zone_event member`) are documented in HACK-NOTES.



### Core battle / QoL (verified in-game)


| Feature                         | Status   | Design ref |
| ------------------------------- | -------- | ---------- |
| Post-battle heal (HP/PP/status) | Verified | [Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition) |
| Full-party EXP share (interim)  | Verified | [Battle-7](DESIGN-BATTLES.md#battle-7-exp-share) |


Hooks and patches: [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md) (Heal after every battle, Full party EXP share).

### Open-world shell (verified or implemented)


| Feature | Status | Design ref |
| ------- | ------ | ---------- |
| Mom starting grants (Ticket, Pass, Apricorn Box, shoes, dex) | Verified | [Vision-3](DESIGN-VISION.md#vision-3-starting-location) |
| Starting city picker (18 decided; 3 in ROM PoC) | Partial | [Vision-3](DESIGN-VISION.md#vision-3-starting-location) |
| Starter pick (12-option menu, gens 1–4) | Verified | [Vision-3](DESIGN-VISION.md#vision-3-starting-location) |
| Dev-only testing grants (e.g. Fly from Mom) | Implemented | Disable before release — see HACK-NOTES |
| Magnet Train (Goldenrod ↔ Saffron) | Verified | [World-1](DESIGN-WORLD.md#world-1-world-transportation) |
| Route 42 paid ferry | Verified | [World-1](DESIGN-WORLD.md#paid-ferry-npcs) |
| Route 4 ledge boost ($100 hiker) | Verified | [World-1](DESIGN-WORLD.md#world-1-world-transportation) |
| Route 29→46 gate (2 badges) | PoC | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) — template only |
| Route 36 Sudowoodo removed | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Route 32 badge gate removed | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Mahogany Rocket arc skipped | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Surge / Erika Cut trees removed | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |
| Jasmine / Olivine Lighthouse (Secret Medicine) | Verified | [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) |


Field recipes: [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md).

### Trainer scaling (verified or enabled)


| Phase | Status | Design ref |
| ----- | ------ | ---------- |
| 1 — Rescale vanilla levels by badge band | Verified | [Battle-8](DESIGN-BATTLES.md#battle-8-implementation) |
| 2 — Level-appropriate moves | Verified | [Battle-8](DESIGN-BATTLES.md#battle-8-implementation) |
| 3 — Same-line stage adjust | Verified | [Battle-8](DESIGN-BATTLES.md#battle-8-implementation) |
| 6 — Gym Leaders at level cap | Partial | [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters) — Gym trainer type filter still open |
| 4–5, 7–12 | Not started | [Battle-8](DESIGN-BATTLES.md#battle-8-implementation) |


Implementation: HACK-NOTES § **Trainer level scaling**.




### Story and script policy

See [Story-1](DESIGN-STORY.md#story-1-story-and-script-content). Surge/Erika/Jasmine verified; remaining gym rows (Bugsy, Clair, Misty, Blue, **Blaine**), opening strip, **rival removal**, HM quest cleanup, and Rocket extension still open. **Paid ferry NPCs:** [World-1](DESIGN-WORLD.md#paid-ferry-npcs). Obsolete vanilla leftovers tracked in [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog).

### Not yet started (core design priorities)

- **Gym scaling phase 6 (remainder)** — Gym trainer type filter; Leader curated exceptions.
- **Battle systems phases 7–9** — agreed size, dynamic rosters, counter-picking.
- **New Bark door swap** when start city ≠ New Bark ([Vision-3](DESIGN-VISION.md#vision-3-starting-location), [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)).
- Living trainers ([World-5](DESIGN-WORLD.md#world-5-living-trainers)), dynamic rosters, universal PC ([Battle-6](DESIGN-BATTLES.md#battle-6-dynamic-battle-rosters)), collection-based HMs + Gym Leader grants ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).
- **Gym Leader family location hints** ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)) — requires [Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology).
- Level caps (`IMPLEMENT_LEVEL_CAP`) — after scaling prototype is stable in playtesting.
- **Wild ecology seed** ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)) — not started; **Wilds-2** level range + **Wilds-3** distance caps implemented (PoC).
- **Paid ferry NPCs** — [World-1](DESIGN-WORLD.md#paid-ferry-npcs).
- Story implementation pass ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)) — opening skip, rival removal, Rocket extension, remaining gym rows.
- **Vanilla cleanup pass** ([Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog)) — strip superseded NPCs, quests, HM fetch chains, and HM-teaching scripts.

The basic development loop is proven:

> **edit source/data → Docker build → test.nds → DeSmuME → verify**

Docker remains the known-good build path.

---

---



# Index-3. Open Design Questions

The following are intentionally unresolved.

- Exact starter system — **v1 twelve-option menu implemented**; long-term pools TBD.
- Per-city home door wiring for **15 of 18** starting cities (3-city PoC in ROM; full list in [Vision-3](DESIGN-VISION.md#vision-3-starting-location)).
- Who determines trainer battle size.
- Exact trainer generation algorithms.
- How aggressively NPCs counter-pick.
- Whether generated trainers have persistent full collections or generate unrevealed Pokémon on demand.
- Exact Gym roster generation.
- Exact EXP formula.
- Whether fainted Pokémon's lost EXP is redistributed.
- Wild ecology: habitat tags, family assignment algorithm, special/static encounter policy ([Wilds-1](DESIGN-WILDS.md#wilds-1-randomized-wild-pokémon-ecology)).
- Wild level distribution curves within area caps ([Wilds-2](DESIGN-WILDS.md#wilds-2-increased-wild-pokémon-level-range)).
- Wild level progression: **Wilds-3 distance caps** — **decided / implemented**; World-2 guard/tile gating **not** used for wild levels ([Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps), [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating)).
- Gym Leader **family hint menus** — curated species lists per Leader ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)).
- Exact transportation prices.
- Exact Pokémon Center service list ([World-7](DESIGN-WORLD.md#world-7-pokmon-centers)).
- Per-mart shop inventories and held-item tiers ([World-10](DESIGN-WORLD.md#world-10-shops)).
- Exact accelerated-time resting mechanics.
- Long-term Pokémon generation cutoff beyond **Gen I–IV + Volcarona line** ([Wilds-5](DESIGN-WILDS.md#wilds-5-pokémon-generations--content-scope)).
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

