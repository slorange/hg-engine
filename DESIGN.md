# Pokémon Wandering Heart — Design Index

> Source of truth for **Pokémon Wandering Heart** core design. Detailed specs live in sub-documents with prefixed section IDs (`World-0`, `World-2`, `Battle-2`, `Story-3`, …).
>
> **This index is NOT permission to implement everything described in the sub-docs.**

## Document map

| Document | Prefix | Topics |
| -------- | ------ | ------ |
| [DESIGN-WORLD.md](DESIGN-WORLD.md) | `World-*` | Open-world principles, travel, gating, HMs, shops, TMs, evolution |
| [DESIGN-WILDS.md](DESIGN-WILDS.md) | `Wilds-*` | Ecology seed, wild levels, fishing, content scope |
| [DESIGN-BATTLES.md](DESIGN-BATTLES.md) | `Battle-*` | Fair trainer fights, badge caps, Gyms, EXP |
| [DESIGN-STORY.md](DESIGN-STORY.md) | `Story-*` | Intro (Story-1/2), script policy (Story-3) |
| [DESIGN-FUTURE.md](DESIGN-FUTURE.md) | `Future-*` | Deferred addons |
| CHANGELOG.md | — | Shipped behavior vs vanilla (player-facing; no doc links) |
| TODO.md | — | **Release blockers** — known bugs, vanilla cleanup, Gym gates, intro/home gaps (not Future scope) |
| documentation/HACK-NOTES.md | — | Implementation recipes (see `.cursor/rules/agents.mdc`) |

## Sections in this document

| Section |
| ------- |
| [Index-1. Instructions for Coding Agents](#index-1-instructions-for-coding-agents) |
| [Index-2. Game Identity](#index-2-game-identity) |

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
- **The user relies on agents to run builds** when verifying work. Follow `.cursor/rules/agents.mdc` (points to **HACK-NOTES** for recipes). First-time toolchain setup: [README (HG-Engine).md](README%20(HG-Engine).md).
- **`DESIGN-*.md` = design only** — intent, rules, player-facing behavior; **link to other `DESIGN-*` sections only**. No paths, tools, or IDs in design bodies. **Do not link** to `TODO.md`, `CHANGELOG.md`, or `documentation/HACK-NOTES.md` from design files.
- **`TODO.md`**, **`HACK-NOTES.md`**, and **`CHANGELOG.md`** sit outside design; they **may link to `DESIGN-*`**. Find them via the document map above, `.cursor/rules/agents.mdc`, or grep by section id (e.g. `Wilds-4`, `Story-3`).
- **Do not edit `CHANGELOG.md`** unless the user asks — finished, tested, player-visible changes when they are about to commit.
- **`TODO.md`** — release blockers only (not [DESIGN-FUTURE.md](DESIGN-FUTURE.md) scope). Remove rows when done; do not move Future items into TODO.

---

# Index-2. Game Identity

**Pokémon Wandering Heart** is HeartGold and SoulSilver reimagined as a trainer’s road trip: you are one of many travelers, not the center of a scripted plot—free to roam Johto and Kanto, grow a roster far beyond six Pokémon, and take on all sixteen Gyms when you are ready, in an order that fits your route.

**Initial Release:** Pick a starting city and a starter, then play through a stripped-down HGSS where major story gates and fetch quests are gone or shortened. Wild levels scale with distance from the starting city, and trainer levels scale with your badge progress. Post-battle healing and no items from either side for fair battles, EXP Share to reduce grinding, and badge-based level caps to ensure difficulty. HMs awarded by Gym leaders rather than quests. Shops sell renewable TMs and evolution items. The playable dex is Generations I–IV plus a few additions.

**Future Plans:** Per-save **wild ecology** so runs feel different; **generated trainer and Gym parties** and smarter Gym scaling; **living trainers** who move and rematch; **dynamic battles** where you pull from the full PC instead of a fixed party of six; a faster **day/night clock** and **Apricorn crafting** economy; **unlimited moves** and **map connectivity** edits — see [DESIGN-FUTURE.md](DESIGN-FUTURE.md). Release blockers are tracked in **TODO.md** (document map).

---
