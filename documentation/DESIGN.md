# Pokémon Wandering Heart — Design Index

> Source of truth for **Pokémon Wandering Heart** core design. Detailed specs live in sub-documents with prefixed section IDs (`World-0`, `World-2`, `Battle-2`, `Story-3`, …).
>
> **This index is NOT permission to implement everything described in the sub-docs.**

**Coding agents:** build, git, design boundaries, and doc map usage — [`.cursor/rules/agents.mdc`](../.cursor/rules/agents.mdc).

## Document map

| Document | Prefix | Topics |
| -------- | ------ | ------ |
| [DESIGN-WORLD.md](DESIGN-WORLD.md) | `World-*` | Open-world principles, travel, gating, HMs, shops, berries, TMs, evolution |
| [DESIGN-WILDS.md](DESIGN-WILDS.md) | `Wilds-*` | Ecology seed, wild levels, fishing, content scope |
| [DESIGN-BATTLES.md](DESIGN-BATTLES.md) | `Battle-*` | Fair trainer fights, badge caps, Gyms, EXP |
| [DESIGN-STORY.md](DESIGN-STORY.md) | `Story-*` | Intro (Story-1/2), script policy (Story-3) |
| [DESIGN-FUTURE.md](DESIGN-FUTURE.md) | `Future-*` | Deferred addons |
| [CHANGELOG.md](../CHANGELOG.md) | — | Shipped behavior vs vanilla (player-facing; no doc links) |
| [TODO.md](TODO.md) | — | **Release blockers** — known bugs, vanilla cleanup, Gym gates, intro/home gaps (not Future scope) |
| [HACK-NOTES.md](HACK-NOTES.md) | — | Implementation recipes (see `.cursor/rules/agents.mdc`) |

# Index-2. Game Identity

**Pokémon Wandering Heart** is HeartGold and SoulSilver reimagined as a trainer’s road trip: you are one of many travelers, not the center of a scripted plot—free to roam Johto and Kanto, grow a roster far beyond six Pokémon, and take on all sixteen Gyms when you are ready, in an order that fits your route.

**Initial Release:** Pick a starting city and a starter, then play through a stripped-down HGSS where major story gates and fetch quests are gone or shortened. Wild levels scale with distance from the starting city, and trainer levels scale with your badge progress. Post-battle healing and no items from either side for fair battles, EXP Share to reduce grinding, and badge-based level caps to ensure difficulty. HMs awarded by Gym leaders rather than quests. Shops sell renewable TMs and evolution items. The playable dex is Generations I–IV plus a few additions.

**Future Plans:** Per-save **wild ecology** so runs feel different; **generated trainer and Gym parties** and smarter Gym scaling; **living trainers** who move and rematch; **dynamic battles** where you pull from the full PC instead of a fixed party of six; a faster **day/night clock** and **Apricorn crafting** economy; **unlimited moves** and **map connectivity** edits — see [DESIGN-FUTURE.md](DESIGN-FUTURE.md). Release blockers are tracked in **TODO.md** (document map).

---
