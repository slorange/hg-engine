# Changelog

Player-facing changes in **Pokémon Wandering Heart** (HG-Engine fork) compared to vanilla HeartGold/SoulSilver.

### New game & starting experience

- **Shortened Professor Oak intro** dialogue.
- **Starting city** — choose from **18 cities** at the start of the game
- **Starter selection** — choose three starters, **one per type**, from gens 1-4 at the start of the game
- **Mom’s grants** at intro — Running Shoes, Pokédex, S.S. Ticket, Magnet Train Pass, Apricorn Box, **5 Poké Balls**, Pokégear, Town Map card, Mom/Oak/Elm phone numbers
- **Dev testing grants from Mom** — 100 Rare Candies (silent) plus **HMs 01–08**, **5× Flash TM**, and **5× Headbutt TM** when dev testing grants are enabled
- **Broader story skip at Mom intro** — consolidated flag sweep on new saves (rival hidden, SS Aqua arrived, many Azalea/Mahogany rocket flags, Elm lab errand skipped, etc.)

### Travel & world access

- **HM field use** — once a Pokémon knows an HM, you can use it from the party menu without that move's vanilla Gym badge (matches badge-count gym HM grants; map/script gates like Flash caves unchanged).
- **Fly map (party menu HM02)** — the fly map scrolls to show **both Johto and Kanto** without beating the Elite Four or clearing the game; each city still needs its usual **fly point** (register at that Pokémon Center). Picking a fly spot in the **other** region while you stand in Johto or Kanto is **not** enabled yet.
- **Magnet Train** (Goldenrod ↔ Saffron) open from the start — no Power Plant / Machine Part quest.
- **S.S. Aqua** (Olivine ↔ Vermilion) — board any day with Mom’s ticket; no weekday lockout at the pier; gangplank no longer blocks after the boat-arrived story flag is set; you are not forced through the first-voyage missing-girl sequence (optional cabin dialogue may still appear if you talk to certain sailors).
- **Route 42 ferry** — fishermen on both shores; paid warp across the water without Surf.
- **Route 40 ↔ Cianwood ferry** — fishermen on the Olivine and Cianwood shores ($200); Route 40 Surf gate removed.
- **Route 31 ↔ Route 45 Dark Cave ferry** — hikers + static Quagsire companions outside both cave mouths ($200).
- **Route 46 → Route 45 ferry** — hiker + static Rhydon at the Route 46 gatehouse end; one-way paid warp to north Route 45 ($200).
- **Blackthorn ↔ Route 44 ferry** — hikers + static Piloswine companions; paid outdoor warp bypassing Ice Path ($200).
- **Kanto coastal ferry mesh** — fishermen + Lapras at Pallet Town south shore, Cinnabar Island beach, Seafoam cave mouth, and Route 19 ($200); 3-destination menu (Pallet Town / Cinnabar Island / Seafoam Island / Fuchsia City labels).
- **Mom intro** — west Kanto and Route 19 shore clearance so Fuchsia’s south beach is reachable from the start.
- **Route 4 ledge boost** — blackbelt + Machoke boost you over the ledge toward Mt. Moon for ¥100.
- **Route 36** — Sudowoodo roadblock removed
- **Route 32** — badge gate south toward Violet removed.
- **Ilex Forest** — main-path Cut tree removed; cross the forest without HM Cut (verified in playtest, Sep 2026).
- **Route 35** — one Cut tree removed for open-world travel; **not** part of Ilex Forest (same playtest).
- **Mahogany** — Team Rocket arc skipped on load; RageCandyBar salesman no longer blocks Route 44.
- **Route 29 → Route 46** — blocked until **2 badges** (Zephyr + Hive); guard-style gating proof of concept.

### Wild encounters

- **Distance-based level caps** — wild levels depend on how far the current area is from your **chosen starting city** (18-city menu index matches the distance table).
- **Endgame and HM-gated wild caps** — selected areas ignore a low distance-only cap: **Flash** dungeons (Dark Cave, Rock Tunnel) floor **14**; **Whirlpool** areas (Whirl Islands) floor **50**; **Waterfall** routes **26** and **27** floor **62**; **Victory Road** fixed **75**; **Route 28**, **Mt. Silver**, and **Cerulean Cave** fixed **85** (same for every start city).
- **Level rolls** — most encounters sit near the area cap; when the cap is high enough, there is a **15%** chance for a low “early route” band instead of a fully scaled level.
- **Stage and moves** — wild species and moves match the rolled level (including evolutions you would expect at that level).
- **Wild catch vs. badge cap** — if a wild Pokémon’s level is above your current badge level cap, the ball is deflected with “This Pokémon is too strong for you right now!”
- **Special evolution lines in the wild** — trade-, stone-, and similar lines can appear as their evolved forms at authored level thresholds in encounters (separate from player trade/stone QoL below).
- **Cinnabar Island** — walking wild encounters on the island (Slugma, Numel, Koffing, Torkoal, Magmar, rare Ditto and **Larvesta**);

### Fishing

- **Rod gurus** — fishermen in **Olivine City** and on **Route 44** (east bridge) grant **Old / Good / Super Rod** based on how many Pokémon you have caught from water encounters (no badge-gated fetch quest).

### Field & items

- **Rock Smash drops** — all breakable rocks use one shared loot table (shards, pearls, fossils, evolution stones, held evo items, etc.); **80%** item chance per rock (map-specific tables ignored). Pickup-style ability bonuses (Suction Cups, Magnet Pull, Keen Eye) still apply.

### Battles & QoL

- **Badge-based player level cap** — party Pokémon stop gaining levels from EXP at **10 + 4×badges** ( **80** at 16 badges; **100** after becoming Champion). **Rare Candies** can still raise level above the current cap; EXP does not.
- **Full heal after every battle** — HP, PP, and status restored for the party (wild and trainer).
- **Full-party EXP share (interim)** — every non-fainted party member receives the **full** EXP for each KO (not split); no Exp Share item required.
- **Post-battle field crash** — known issue when returning to the field after battle (KB-2); frequency varies by setup.

### Shops & items

- **Mart redesign** — dept stores emphasize status berries, EV power items, and vitamins over vanilla healing/X-item grind.
- **Renewable TMs** — Celadon dept TM floor and Goldenrod 5F sell fixed TM sets.
- **Game Corner prizes** — Goldenrod and Celadon coin-exchange **TM** and **held-item** menus retargeted. All prizes temporarily cost **50 Coins** (playtest shortcut until coin income ships).
- **TM05 Headbutt** — **TM05** teaches **Headbutt** in battle (replacing Roar). Species that could learn Headbutt from the HeartGold **move tutor** can also learn it from this TM.
- **Badge-gated dept 2F** — Goldenrod and Celadon first clerk unlock balls, repels, held items, Flash and Headbutt TM, and late-game gear by **badge count** (not vanilla potion progression). Shelves use **total Johto + Kanto badges** (matches trainer scaling)
- **Town specialty marts** — evolution stones, trade evo held items, and type-resist berries at themed cities (e.g. Moon Stone at Mt. Moon Square).
- **Trade evolution QoL** — trade-evo **held items** (Metal Coat, Up-Grade, etc.) work when **used on the Pokémon** like stones; **Linking Cord** replaces trade for Kadabra, Machoke, Graveler, Haunter, and similar lines. Buy Linking Cord at **Goldenrod dept 2F (lower)** and **Celadon dept 4F** (¥8000).
- **Olivine** — Secret Medicine remains on the **second** clerk; first clerk uses the badge shelf only.

### Trainer scaling

- **Trainer levels** scale to badge count (level band per badge tier).
- **Trainer Pokémon** use level-appropriate **moves** and **evolution stage** for their scaled level (same stage logic as wild encounters where applicable).
- **Special evolution lines on trainers** — the same authored trade/stone (and similar) stage thresholds as wild encounters apply to trainer teams; low-level trainers **devolve** authored finals (e.g. Alakazam → Abra) instead of keeping stone/trade forms at every level.
- **Gym Leaders** — every Pokémon on the Leader’s team is set to the **badge-tier level cap** for your current badge count (not a random level in the ordinary trainer band).

### Gyms & story

- **Lt. Surge & Erika** — Cut trees removed outside Gyms; Celadon Gym maze trees removed; Leaders reachable without Cut.
- **Jasmine** — Secret Medicine sold at Olivine Mart (¥500); pharmacy flow updated; Lighthouse works after purchase.
- **Johto Gym HM pilot (partial)** — **Falkner, Morty, Jasmine, and Pryce** use badge-count HM rewards after victory (field move + TM flow per open-world HM table). Falkner’s Gym also drops the Sprout Tower gate blocker. Still rough edges and not all Johto/Kanto Leaders.
