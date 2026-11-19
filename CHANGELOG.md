# Changelog

Player-facing changes in Pokémon Wandering Heart compared to vanilla HeartGold/SoulSilver.

### HG-Engine

Behavior inherited from HG-Engine.

- **Fast text** — dialogue prints nearly instantly, regardless of the text-speed setting.
- **60 FPS battles** — battles run at 60 frames per second. The overworld keeps the usual speed.
- **No overworld poison** — a poisoned Pokémon does not lose HP while walking.
- **PC boxes** — **30** boxes instead of 18.
- **Repel prompt** — when a Repel runs out, the game offers another: Max Repel, then Super Repel, then Repel.
- **Friendship evolutions** — need **160** friendship instead of 220.
- **Vitamins** — raise EVs up to **252** in a stat instead of stopping at 100.
- **No low-HP beep** — the critical-health warning sound is off.
- **Nature arrows** — the summary stats page marks which stats a nature raises and lowers.
- **Summary stats** — on a Pokémon’s summary stats page, **L** shows EVs, **R** shows IVs, and **Select** returns to the normal stats.
- **Fairy type and type chart** — Fairy is present. Steel does not resist Ghost or Dark.
- **Moves, abilities, and learnsets** — later-generation moves, abilities, and level-up learnsets.
- **Move values** — some moves use Pokémon Champions power, type, accuracy, or effect chance on top of Scarlet and Violet values. Move PP stays on the Scarlet and Violet numbers.
- **Scaled experience** — a higher-level Pokémon gains less experience from a weaker foe. Catching a wild Pokémon also awards experience.
- **Poké Ball rates** — most balls use current-generation catch rates. A Friend Ball sets friendship to **150**. Safari, Lure, and Sport Balls keep HeartGold rates.
- **HP bars** — drain and fill at a fixed speed.

### New game & starting experience

- **Shortened Professor Oak intro** dialogue.
- **Starting city** — choose from **18 cities** at the start of the game.
- **Starter selection** — choose three starters, **one per type**, from Gen 1–4 at the start of the game.
- After starter selection, the player receives — Running Shoes, Pokédex, S.S. Ticket, Magnet Train Pass, Bicycle, Apricorn Box, Berry Pots, 5 of each basic berry, 5 Poké Balls, Pokégear.
- **National Pokédex** — unlocked from the start

### Travel & world access

- **HMs** — vanilla gym badge requirements removed.
- **HM02 Fly map** — the fly map scrolls to show **both Johto and Kanto** without beating the Elite Four.
- **Magnet Train** — open from the start.
- **S.S. Aqua** — open from the start, no weekday lockout. First-voyage missing-girl sequence is optional.
- **Accelerated day/night** — 30 real minutes equals one in-game day. Applies to Pokégear clock, overworld lighting, and time-based wilds & evolutions.
- **Ferry NPCs** — NPCs give the player the option to cross sections they normally wouldn't be able to at the start of the game: Olivine to Cianwood, Across Dark Cave, Up Routes 46/45, Across Ice Cave, Pallet/Cinnabar/Seafoam/Fuchsia, up Route 4.
- West Kanto and Fuchsia’s south beach are reachable from the start.
- **Route 36** — Sudowoodo roadblock removed.
- **Route 32** — badge gate south toward Violet removed.
- **Cut trees removed** — Ilex Forest and Route 35.
- **Snorlax removed** — Outside Vermilion

### Pokémon Centers
- **Move relearner** — available in the shared Center for **$300 per move**
- **Apricorn crafting** — exchange all carried Apricorns for their corresponding Poké Balls immediately. The fee is **$100 per 10 Apricorns, rounded up** across the whole batch.
- **Abra transportation** — a Psychic and Abra offer travel to visited destinations in **either Johto or Kanto** for **$400**, without needing Fly.
- **Time Skip** — Nurse Joy gives options to reset until Morning, Day, or Night

### Wild encounters

- **Later-generation evolutions** — Sylveon, Kleavor, Wyrdeer, Ursaluna, Annihilape, Farigiraf, and Dudunsparce added to existing Gen I–IV families, with accessible evolution methods and items.
- **Distance-based level caps** — wild levels depend on how far the current area is from your **chosen starting city** (18-city menu index matches the distance table).
- **Level rolls** — most encounters sit near the area cap, but with a **15%** chance for a low level to help complete the dex.
- **Stage and moves** — wild Pokémon's evolution stage and moves match the rolled level
- **Wild catch vs. badge cap** — the player cannot catch a wild Pokémon whose level is above their level cap.
- **Special evolution lines in the wild** — trade, stone, and similar lines can appear as their evolved forms at set level thresholds.
- **Cinnabar Island** — walking wild encounters on the island
- **Wild held items** — species table rolls (**65%** common / **15%** rare / **20%** nothing); if still empty, **50%** chance of a random berry. With **Compound Eyes** lead: **70%** common / **30%** rare, then **always** a berry.
- **Per-save wild ecology** — Each new game builds a shuffled assignment of Pokémon families to habitats and encounter methods. Pokémon encounters draw from this list instead of static tables. Applies to grass, caves, Surf, fishing, Headbutt, and Rock Smash. This is not pure random, assignments are filtered based on Type, Encounter method, Rarity, etc.
- **Wild shinies** — Rate increased to **1/128**

### Bug-Catching Contest & National Park

- **Daily contests** — available every day instead of only Tuesday, Thursday, and Saturday.
- **Scoring** — the sum of maximum HP, Attack, Defense, Special Attack, Special Defense, and Speed replaces vanilla judging.
- **Prizes** — Ability Patches / Capsules, Bottle Caps, PP Up / Max, Rare Candies, Valuables

### Fishing

- **Rod progression** — **Old**, **Good**, and **Super Rod** tiers advance by catching distinct **Water-type evolutionary families** (Pokédex caught flags), not by badges or visit order. **Good Rod** at **5** families; **Super Rod** at **15**. Any guru can hand out the next rod you qualify for.
- **Rod gurus** — At Route 44, Route 34 (Day-Care), Olivine City, Route 32 Pokémon Center, Route 24, Viridian City, Vermilion City, Fuchsia City, and Route 12.

### Battles & QoL

- **Badge-based player level cap** — party Pokémon stop gaining levels from EXP at **10 + 4×badges** ( **80** at 16 badges; **100** after becoming Champion). **Rare Candies** can still raise level above the current cap.
- **Full-party EXP share** — every non-fainted party member receives the **full** EXP for each KO. Those same Pokémon also receive that KO’s **EVs**, including ones already at the level cap.
- **Full heal after every battle** — HP, PP, and status restored for the party (wild and trainer).
- **Consumable held items restored after battle** — if a party Pokémon had a held item at the start of the fight, it is restored when the battle ends, including berries.
- **HM moves** — can be replaced when a Pokémon learns a new move, without move deleter.

### Shops & items

- **Mart redesign** — dept stores replace vanilla healing/X-item with berries, held items, and EV power items.
- **Goldenrod herb lady** — sells **Pomeg through Tamato** berries (lower EVs, raise friendship) instead of Revival Herb and stat powders.
- **Game Corner** — Goldenrod and Celadon coin-exchange **TM** and **held-item** menus retargeted. Prize cost greatly reduced.
- **TM05 Headbutt** — Roar TM has been replaced by Headbutt.
- **Badge-gated shop items** — Regular shops unlock balls, repels, held items, Flash and Headbutt TM, and late-game gear by **badge count**.
- **Town specialty marts** — evolution stones, trade evo held items, and type-resist berries at themed cities.
- **Trade evolution QoL** — trade-evo **held items** (Metal Coat, Up-Grade, etc.) work when **used on the Pokémon** like stones; **Linking Cord** replaces trade for Kadabra, Machoke and similar lines.
- **Early Stone Evolutions** — For Pokémon that evolve by level up, a matching typed stone can be used to evolve them a few levels early. Example Quilava & fire stone at lv30+
- **Rock Smash drops** — Increased item chance and reworked loot table.

### Trainer scaling

- **Trainer levels** scale to badge count. Gym leaders at cap.
- **Trainer Pokémon** use level-appropriate **moves** and **evolution stage** for their scaled level (same stage logic as wild encounters).

### Gyms & story

- **Gym rewards** — All 16 Leaders give a badge, increase the level cap, and may give an HM based on badge count. The player then chooses a TM from that Leader’s pool, which expands based on badge count. Rematches offer the TM choice again.
- **Lt. Surge & Erika** — Cut trees removed outside Gyms; Celadon Gym maze trees removed; Leaders reachable without Cut.
- **Jasmine** — Secret Medicine sold at Olivine Mart.
- **Clair (Blackthorn)** — Battle Clair with no prior Gym badges or Rocket gates cleared; Dragon’s Den trial not required for the badge.
- **Misty (Cerulean)** — Power Plant and Route 25 date chain skipped; Misty in Cerulean Gym from the start.
- **Blue (Viridian)** — Seven Kanto badge gate removed; Blue in Viridian Gym from the start; overworld appearance on Cinnabar removed.
- **Broader story skip** — Azalea/Mahogany Rocket skipped, Elm lab errand skipped.
