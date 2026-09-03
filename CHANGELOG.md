# Changelog

Player-facing changes in **Pokémon Wandering Heart** (HG-Engine fork) compared to vanilla HeartGold/SoulSilver.

Implementation details and IDs: `[documentation/HACK-NOTES.md](documentation/HACK-NOTES.md)`. Design baseline: `[DESIGN.md](DESIGN.md#index-2-current-technical-baseline)`.

### New game & starting experience

- **Starting city** — choose New Bark, Goldenrod, or Saffron in Mom’s cutscene (before starter pick); dynamic home exit warp to chosen city.
- **Starter selection** — 12-option text menu in Mom’s cutscene (gens 1–4 starters); not vanilla 3-ball UI.
- **Shortened Professor Oak intro** dialogue.
- **Mom’s grants** at intro — Running Shoes, Pokédex, S.S. Ticket, Magnet Train Pass, Apricorn Box, Pokégear, Town Map card, Mom/Oak/Elm phone numbers.
- **HM02 Fly from Mom** — dev/testing grant only (`OPENWORLD_TESTING_GRANTS`); disable before release builds.



### Travel & world access

- **Magnet Train** (Goldenrod ↔ Saffron) open from the start — no Power Plant / Machine Part quest.
- **Route 42 ferry** — fishermen on both shores; paid warp across the water without Surf.
- **Route 4 ledge boost** — hiker boosts you over the ledge toward Mt. Moon for ¥100.
- **Route 36** — Sudowoodo roadblock removed (Violet ↔ Goldenrod open at 0 badges).
- **Route 32** — badge gate south toward Violet removed.
- **Mahogany** — Team Rocket arc skipped on load; RageCandyBar salesman no longer blocks Route 44.
- **Route 29 → Route 46** — blocked until **2 badges** (Zephyr + Hive); guard-style gating proof of concept.



### Battles & QoL

- **Full heal after every battle** — HP, PP, and status restored for the party (wild and trainer).
- **Full-party EXP share (interim)** — every non-fainted party member receives the **full** EXP for each KO (not split); no Exp Share item required.



### Trainer scaling

- **Trainer levels** scale to badge count (level band per badge tier).
- **Trainer Pokémon** use level-appropriate **moves** and **evolution stage** for their scaled level.



### Gyms & story

- **Lt. Surge & Erika** — Cut trees removed outside Gyms; Celadon Gym maze trees removed; Leaders reachable without Cut.
- **Jasmine** — Secret Medicine sold at Olivine Mart (¥500); pharmacy flow updated; Lighthouse works after purchase.

