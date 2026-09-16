# Changelog

Player-facing changes in **Pokémon Wandering Heart** (HG-Engine fork) compared to vanilla HeartGold/SoulSilver.

Implementation details and IDs: `[documentation/HACK-NOTES.md](documentation/HACK-NOTES.md)`. Design baseline: `[DESIGN.md](DESIGN.md#index-2-current-technical-baseline)`. Known bugs: `[DESIGN.md § Index-5](DESIGN.md#index-5-known-bugs)`.

### New game & starting experience

- **Starting city** — choose New Bark, Goldenrod, or Saffron in Mom’s cutscene (before starter pick); dynamic home exit warp to chosen city.
- **Starter selection** — 12-option text menu in Mom’s cutscene (gens 1–4 starters); not vanilla 3-ball UI.
- **Shortened Professor Oak intro** dialogue.
- **Mom’s grants** at intro — Running Shoes, Pokédex, S.S. Ticket, Magnet Train Pass, Apricorn Box, **5 Poké Balls**, Pokégear, Town Map card, Mom/Oak/Elm phone numbers; **`FLAG_UNK_09A` (154)** so marts sell Poké Balls without Route 29 tutorial.
- **HM02 Fly from Mom** — dev/testing grant only (`OPENWORLD_TESTING_GRANTS`); disable before release builds.

### Travel & world access

- **Magnet Train** (Goldenrod ↔ Saffron) open from the start — no Power Plant / Machine Part quest.
- **Route 42 ferry** — fishermen on both shores; paid warp across the water without Surf.
- **Route 4 ledge boost** — hiker boosts you over the ledge toward Mt. Moon for ¥100.
- **Route 36** — Sudowoodo roadblock removed (Violet ↔ Goldenrod open at 0 badges). *First visit may still show the tree until you leave and re-enter — [KB-1](DESIGN.md#index-5-known-bugs).*
- **Route 32** — badge gate south toward Violet removed.
- **Mahogany** — Team Rocket arc skipped on load; RageCandyBar salesman no longer blocks Route 44.
- **Route 29 → Route 46** — blocked until **2 badges** (Zephyr + Hive); guard-style gating proof of concept.

### Wild encounters

- **Distance-based level caps** — wild levels depend on how far the current area is from your **chosen starting city** (same distance table supports all 18 planned start cities; the in-game city picker is still a 3-city PoC).
- **Level rolls** — most encounters sit near the area cap; when the cap is high enough, there is a **15%** chance for a low “early route” band instead of a fully scaled level.
- **Stage and moves** — wild species and moves match the rolled level (including evolutions you would expect at that level).
- **Special evolution lines in the wild** — trade-, stone-, and similar lines can appear as their evolved forms at authored level thresholds in encounters (player evolution rules unchanged).

### Fishing

- **Rod gurus** — fishermen in **Olivine City** and on **Route 44** (east bridge) grant **Old / Good / Super Rod** based on how many Pokémon you have caught from water encounters (no badge-gated fetch quest).

### Battles & QoL

- **Full heal after every battle** — HP, PP, and status restored for the party (wild and trainer).
- **Full-party EXP share (interim)** — every non-fainted party member receives the **full** EXP for each KO (not split); no Exp Share item required.
- **Post-battle field crash (interim fix)** — rare crash when returning to the field after battle; extra guards in the heal-after-battle hook (Sep 2026).

### Shops & items

- **Mart redesign** — under `MART_EXPANSION`, `src/field/mart.c` replaces most healing/potion and X-item shelves with **status berries**, **EV power items**, and **vitamins + Rare Candy / PP Up / PP Max** at Goldenrod and Celadon dept stores.
- **Renewable TMs** — Celadon dept TM floor and Goldenrod 5F sell fixed TM sets (see [World-7](DESIGN-WORLD.md#world-7-shops)).
- **Badge-gated dept 2F** — Goldenrod and Celadon first clerk unlock balls, repels, held items, **TM70 (Flash)**, and late-game gear by **badge count** (not vanilla potion progression).
- **Town specialty marts** — evolution stones, trade evo held items, and type-resist berries at themed cities (e.g. Moon Stone at Mt. Moon Square, stones/items per city table in design docs).
- **Olivine** — Secret Medicine remains on the **second** clerk; first clerk uses the badge shelf only.

### Trainer scaling

- **Trainer levels** scale to badge count (level band per badge tier).
- **Trainer Pokémon** use level-appropriate **moves** and **evolution stage** for their scaled level (same stage logic as wild encounters where applicable).
- **Special evolution lines on trainers** — the same authored trade/stone (and similar) stage thresholds as wild encounters can apply to trainer teams, not only wild rolls.
- **Gym Leaders** — every Pokémon on the Leader’s team is set to the **badge-tier level cap** for your current badge count (not a random level in the ordinary trainer band).

### Gyms & story

- **Lt. Surge & Erika** — Cut trees removed outside Gyms; Celadon Gym maze trees removed; Leaders reachable without Cut.
- **Jasmine** — Secret Medicine sold at Olivine Mart (¥500); pharmacy flow updated; Lighthouse works after purchase.
- **Johto Gym HM pilot (partial)** — **Falkner, Morty, Jasmine, and Pryce** use badge-count HM rewards after victory (field move + TM flow per open-world HM table). Falkner’s Gym also drops the Sprout Tower gate blocker. *Still rough edges and not all Johto/Kanto Leaders — see HACK-NOTES § Gym Leader HM rewards.*
