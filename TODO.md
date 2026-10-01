# Pokémon Wandering Heart — Release TODO

Work that must ship before **initial release**. [DESIGN-FUTURE.md](DESIGN-FUTURE.md) is intentionally out of scope here.

**Policy** (why we remove vanilla content): [DESIGN-STORY.md § Story-3](DESIGN-STORY.md#story-3-story-and-script-policy). **Recipes:** [documentation/HACK-NOTES.md](documentation/HACK-NOTES.md).

Once a change has been user tested and commit ready, remove it from this file and update [CHANGELOG.md](CHANGELOG.md) if player-visible.

---

## Known bugs

Regressions in the **current ROM** (not incomplete design from domain sections).

| ID | Symptom | Notes |
| -- | ------- | ----- |
| **KB-2** | Crash when returning to the field after a battle (freeze or hard crash on fade to overworld). | Open again (Sep 2026); repro is asymmetric across testers. Related: [Battle-1](DESIGN-BATTLES.md#recovery) post-battle heal. |
| **KB-3** | Cherrygrove guide — Town Map / running-shoes tutorial cutscene still runs; guide NPC is invisible on new saves. | Mom already grants shoes + Town Map. Fix via guide triggers, not hide-flag alone. See [Vanilla cleanup — Mom / intro](#superseded-by-mom-cutscene--starting-grants). |
| **KB-4** | Slowpoke Well (Azalea) — one Team Rocket grunt still blocks the entrance | Policy: [Story-3 — Team Rocket](DESIGN-STORY.md#team-rocket--remove). |
| **KB-5** | Mahogany Gym — crash entering the last (Pryce) room of the ice puzzle. | Repro when entering the room, not on battle start. |
| **KB-6** | Mom (player house 1F) — after intro, seated Mom shows broken dialogue or wrong menus. | After open-world intro; [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home), [Story-2](DESIGN-STORY.md#story-2-starter-pokémon-and-intro-flow). |
| **KB-7** | Violet Gym (Falkner) — Leader unreachable; elevator broken after HM-grant scr_seq patches. | [Gym HM rewards](documentation/HACK-NOTES.md#gym-leader-hm-rewards-johto-pilot); slots **859** / zone_event **365**. |

---

## Battles ([DESIGN-BATTLES.md](DESIGN-BATTLES.md))

Release gaps from design status and partial sections (Future-7/8 excluded).

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Gym defeat rewards (HM + TM choice)** | [Battle-3 § First defeat rewards](DESIGN-BATTLES.md#first-defeat-rewards), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Johto HM pilot partial; Flash / Headbutt field flow incomplete; Gym TM pools + choice UI **not implemented** |

---

## Wilds ([DESIGN-WILDS.md](DESIGN-WILDS.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Distance caps — Safari Zone** | [Wilds-1 § Encounter methods](DESIGN-WILDS.md#encounter-methods-poc-coverage) | **Not yet** hooked to distance table |
| **Distance caps — Bug Catching Contest** | [Wilds-1 § Encounter methods](DESIGN-WILDS.md#encounter-methods-poc-coverage) | **Not yet** hooked |
| **Fishing guru network** | [Wilds-4](DESIGN-WILDS.md#wilds-4-fishing-rod-progression) | Route 44 + Olivine done; Route 32 PC, Viridian, Vermilion, Fuchsia, Route 12 **planned** |
| **Synthetic stage deferrals** | [Wilds-3 § Synthetic evolution](DESIGN-WILDS.md#synthetic-evolution-stages) | Eevee, Tyrogue, Shedinja, gendered lines — authoring deferred |

---

## World ([DESIGN-WORLD.md](DESIGN-WORLD.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Cross-region Fly (Johto ↔ Kanto)** | [World-1](DESIGN-WORLD.md#world-1-world-transportation), [Fly map § cross-region attempts](documentation/HACK-NOTES.md#cross-region-fly-attempts-pinned) | Kanto scroll works (`OPENWORLD_FLY_MAP` arm9 hook); destination filter still vanilla; overlay 101 patch sites tried in Sep 2026 all failed or no-op (see HACK-NOTES) |
| **Abra Pokémon Center travel** | [World-1 § Abra fast travel](DESIGN-WORLD.md#abra-fast-travel) | **Not implemented** — visited-cities-only fast travel before Fly |
| **Remove dev badge gate (Route 29 → 46)** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | PoC **2-badge** gatehouse must go before release |
| **Endgame badge guards** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | Ship **Route 26** (13 badges / Waterfall tier), **Route 23** + Victory Road / League, **Route 28** + Mt. Silver |
| **Gym Leader HM grants (all rows)** | [World-3](DESIGN-WORLD.md#badge--field-abilities-single-reference), [Battle-3](DESIGN-BATTLES.md#first-defeat-rewards) | Badge-order table decided; rewrite Leader scripts — [Vanilla cleanup § HM](#superseded-hm-and-progression-teaching) |
| **Gym TM choice pools** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Per-Leader pools authored; **minimum badge per TM** + defeat/rematch **choice UI** not implemented |
| **Violet / Fuchsia shard traders** | [World-7 § Rare battle berries](DESIGN-WORLD.md#world-7-berry-economy) | Liechi–Rowap via shard exchange menus |

---

## Story ([DESIGN-STORY.md](DESIGN-STORY.md))

### Gym Leaders — story gates

Per [Story-3 Gym policy](DESIGN-STORY.md#gyms--access-and-story-policy).

| Leader | Change |
|--------|--------|
| **Clair** (Blackthorn) | Grant **Rising Badge** after win — [HACK-NOTES § Clair](documentation/HACK-NOTES.md#blackthorn-gym--clair-rising-badge) (battle works with 0 badges; post-win grant still broken). |
| **Misty** (Cerulean) | Drop Power Plant / Machine Part / Route 25 chain; Leader available in Gym without leaving town. |
| **Blue** (Viridian) | Drop “7 Kanto badges first” gate; challengeable at any badge tier. |

Slowpoke Well grunt ([KB-4](#known-bugs)) is tracked under **Known bugs**, not a Leader row.

---

### Intro and home

[Story-1](DESIGN-STORY.md#story-1-starting-city-and-home) design; step **1** complete.

| Step | Direction | Status |
| ---- | --------- | ------ |
| **2** | Start city outdoor home door → Mom interior | **Rolled back** — retarget on map load (v2 plan in Story-1) |
| **3** | New Bark house door (start ≠ New Bark) → displaced interior | **Not started** |
| **4** | Leave displaced interior → New Bark outdoor | **Not started** |

Displaced-interior NPC/script cleanup: [Vanilla cleanup](#vanilla-cleanup-backlog) (Copycat / Saffron home, etc.).

---

## Vanilla cleanup backlog

Removals or script skips for obsolete vanilla content. Prefer disabling a branch or removing an object over deleting assets.

**Story flags:** pret **100–399** — track as skips are mapped.

### Superseded by Mom cutscene / starting grants

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Cherrygrove guide (Town Map, running-shoes tutorial) | Mom grants shoes + Town Map card | Skip or shorten guide **trigger scripts** ([KB-3](#known-bugs)) |
| Route 30 Apricorn Box NPC | Mom grants Apricorn Box + flag 109 | Remove NPC or make flavour-only |
| Mom post-cutscene Elm errand line | Open-world intro has no Elm fetch | Replace Elm-fetch dialogue; skip Elm lab gate scripts |
| Mom **seated** talk after intro | Intro cutscene replaces vanilla Mom flow | Broken menus/dialogue ([KB-6](#known-bugs)) |
| Vanilla New Bark bedroom starter flow | Starters chosen in Mom cutscene | Bedroom must not re-run vanilla three-ball picker |

### Opening / rival / egg (still mostly vanilla)

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Professor Elm lab errand and waiting NPCs | No linear New Bark opening | Flag-on-load or script skip in Elm lab |
| Rival intro, naming, Route 22/30 battles | Rival removed ([Story-3](DESIGN-STORY.md#rival--remove)) | Strip rival NPCs, naming flow, and battle scripts |
| Mr. Pokémon / Togepi egg quest | Not part of open-world start | Skip egg give; adjust Violet City references if needed |
| Professor Oak visit chain | Superseded by direct bedroom wake | Skip Oak trigger scripts on Route 29 / lab |

### Superseded services and items

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Cianwood pharmacy free Secret Medicine | Medicine sold in Olivine Mart | Remove free give; optional flavour dialogue only |
| Copycat / S.S. Ticket story (partial) | Pass + Ticket from Mom; train patched | Displaced-interior scripts still vanilla ([Story-1](DESIGN-STORY.md#story-1-starting-city-and-home)) |
| Power Plant / Machine Part (partial) | Magnet Train open without quest | Strip Cerulean/Route 25 hooks when Misty gate row is done |

### Superseded obstacles and NPC chains

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| SquirtBottle / Floria flower-shop chain | Route 36 Sudowoodo removed | Remove or flavour-only Goldenrod SquirtBottle girl |
| Sudowoodo encounter scripts (Route 36) | Tree hidden via Mom intro flag | Optional: relocate encounter elsewhere later |
| Stale badge-gate scripts (R32, R36, Mahogany, …) | Replaced by open travel | Scan coord triggers / talk scripts |

### Superseded HM and progression teaching

Target: Gym Leaders grant badge + TM + HM order ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Vanilla per-Leader HM gifts (wrong move / wrong Leader) | Badge-order HM table | Rewrite Leader defeat scripts |
| **HM fetch / delivery quests** (Bill's PC, SS Anne, etc.) | HMs from Gym Leaders | Remove or skip fetch chains |
| NPCs teaching Cut / Surf / etc. (Bill, HM tutors, story gates) | Leaders grant HMs | Remove teach scripts; keep HM-respecting obstacles |
| Whirlpool / Waterfall / Strength story gates on routes and dungeons | Badge-count unlock | Replace with badge checks or remove for open travel |
| Flash / Headbutt tutor & story acquisition | Gym badge order | Remove or skip vanilla tutor gates |