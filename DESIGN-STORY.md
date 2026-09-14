# Pokémon Wandering Heart — Story & Cleanup

> Story/script policy and vanilla content removal backlog.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Implementation recipes:** [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md)

# Story-1. Story and Script Content

**Status: DECIDED**

Field scripts, NPCs, and map obstacles that assume vanilla story order or a New Bark start are removed or rewritten. Target: **any starting city**, **any-order Gyms**.

## Opening and tutorial — remove

Mom cutscene ([Vision-3](DESIGN-VISION.md#vision-3-starting-location), [Index-2](DESIGN.md#index-2-current-technical-baseline)) **replaces** the vanilla New Bark opening for city pick, starter, and starting grants. **Vanilla leftovers still present** until cleaned up — see [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog):

- Elm errand (Mom post-cutscene dialogue still references Elm; lab scripts active)
- Rival intro, naming, and early battles ([Rival — remove](#rival--remove))
- Oak visit chain
- Togepi egg fetch from Mr. Pokémon
- Cherrygrove guide (Town Map, running shoes tutorial)
- Route 30 Apricorn Box NPC (Apricorn Box now from Mom)

No replacement fetch quests at other cities unless optional flavour, not service gates.

## Team Rocket — remove

Rocket grunts, hideouts, Radio Tower arc, and related roadblocks must not gate travel, Gyms, or items. Mahogany post-clear on load is the verified pattern (`HACK-NOTES.md`); extend to Goldenrod basement, Radio Tower, etc.

## Rival — remove

**Status: DECIDED**

Remove the rival entirely: no naming, no scripted intro, no mandatory early battles, no badge-tier rematch arc. Strip rival NPCs, battle triggers, and dialogue that assume a persistent rival companion. Optional one-off trainer NPCs may reuse rival-adjacent maps later, but there is **no rival character** in the open-world design.

## Gyms — access and story policy

**Rules (all Leaders):**

1. **City-local events only** — pre/post-battle flavour OK if it stays in the Gym town; cut anything that sends the player elsewhere and expects a return.
2. **No story-gated Gym approach** — no Cut/Surf/Strength/Whirlpool (or Rocket/badge-count) blocking the Gym door or Leader; HMs are granted by Gym Leaders per badge order ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves), [Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)). HM/Flash/dungeon gating ([World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)) still applies outside Gyms. Wild **levels** use [Wilds-3](DESIGN-WILDS.md#wilds-3-starting-city-distance-based-wild-level-caps), not badge guard tiles.
3. **Internal Gym puzzles** — trash cans, maze, etc. stay unless they hard-require an HM.

### Required changes

| Leader | Change |
|--------|--------|
| **Bugsy** (Azalea) | Remove Team Rocket. |
| **Clair** (Blackthorn) | Drop 7-badge + Goldenrod Rocket gates. Drop or HM-free the Dragon's Den trial before the badge (Den currently needs Surf + Whirlpool). |
| **Misty** (Cerulean) | Drop Power Plant / Machine Part / Route 25 chain; Leader available in Gym without leaving town. |
| **Blue** (Viridian) | Drop “7 Kanto badges first” gate; challengeable at any badge tier. |
| **Blaine** (Seafoam B4F) | Gym is **not** in a town — no story gates on the Leader once Seafoam is entered. Island reach: [World-1 — paid ferry NPCs](DESIGN-WORLD.md#paid-ferry-npcs). |

### Verified

| Leader | Notes |
|--------|--------|
| **Jasmine** (Olivine) | Secret Medicine sold at Olivine Mart (¥500); Lighthouse works after purchase. **Cleanup:** redundant Cianwood pharmacy — [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog). |
| **Lt. Surge** (Vermilion) | Cut tree outside Gym removed; internal trash-can puzzle unchanged. |
| **Erika** (Celadon) | City + Gym maze Cut trees removed; Leader reachable without Cut. |
| **Pryce** (Mahogany) | Rocket skip on load (see above). |

Verified in-game Aug–Sep 2026. Field recipes: `documentation/HACK-NOTES.md`.

### OK as-is (city-local or no external gate)

Falkner, Whitney, Morty (Burned Tower is Ecruteak-local), Chuck, Sabrina, Janine, Brock.

After a row is **verified**, check [Story-2](DESIGN-STORY.md#story-2-vanilla-cleanup-backlog) for redundant vanilla content to strip. Implementation uses flag-on-load and script skips — same toolchain as HACK-NOTES field recipes; starting city ([Vision-3](DESIGN-VISION.md#vision-3-starting-location)) must not depend on Elm/rival/New Bark flags.

---


---

# Story-2. Vanilla Cleanup Backlog

**Status: living checklist**

Track vanilla content that is **obsolete** because we replaced it elsewhere, granted it at game start, or changed the design. These are not new features — they are **removals or script skips** so players do not see duplicate or contradictory content.

Implementation: same toolchain as [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) (`scr_seq`, `zone_event`, text banks, flag-on-load). Prefer disabling a script branch or removing an object over deleting assets.

## Superseded by Mom cutscene / starting grants

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Cherrygrove guide (Town Map, running-shoes tutorial) | Mom grants shoes + Town Map card | Skip or shorten guide NPC scripts |
| Route 30 Apricorn Box NPC | Mom grants Apricorn Box + flag 109 | Remove NPC or make flavour-only |
| Mom post-cutscene Elm errand line | Open-world intro has no Elm fetch | Edit `data/text/545.txt` string 6+; skip Elm lab gate scripts |
| Vanilla New Bark bedroom starter flow | Starters chosen in Mom script **0** | Bedroom scr_seq **846** already vanilla — verify no `choose_starter` hook |

## Opening / rival / egg (still mostly vanilla)

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Professor Elm lab errand and waiting NPCs | No linear New Bark opening | Flag-on-load or script skip in Elm lab scr_seq |
| Rival intro, naming, Route 22/30 battles | Rival removed ([Story-1](DESIGN-STORY.md#story-1-story-and-script-content)) | Strip rival NPCs, naming flow, and battle scripts |
| Mr. Pokémon / Togepi egg quest | Not part of open-world start | Skip egg give; adjust Violet City references if needed |
| Professor Oak visit chain | Superseded by direct bedroom wake | Skip Oak trigger scripts on Route 29 / lab |

## Superseded services and items

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Cianwood pharmacy free Secret Medicine | Medicine sold in Olivine Mart (`sOlivineMart` in `src/field/mart.c`); Cianwood mart list already excludes it | Remove pharmacist **giveitem** scr_seq branch; optional flavour dialogue only |
| Copycat / S.S. Ticket story (partial) | Pass + Ticket from Mom; train patched | Copycat house repurposed as Saffron home door — displaced-interior scripts still vanilla ([Vision-3](DESIGN-VISION.md#vision-3-starting-location)) |
| Power Plant / Machine Part (partial) | Magnet Train open without quest | Misty Gym still gated — see [Story-1](DESIGN-STORY.md#story-1-story-and-script-content); strip remaining Cerulean/Route 25 hooks when Misty row is done |

## Superseded obstacles and NPC chains

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| SquirtBottle / Floria flower-shop chain | Route 36 Sudowoodo removed; bottle only existed for that block | Remove or flavour-only the Goldenrod SquirtBottle girl; no functional gate |
| Sudowoodo encounter scripts (Route 36) | Tree hidden on load | Optional: relocate encounter elsewhere later |
| Badge gates already patched (R32, R36, Mahogany, …) | Replaced by open travel | Scan for stale coord triggers or talk scripts referencing removed blockers |

## Superseded HM and progression teaching

**Target design:** Gym Leaders grant badge + TM + **next HM in badge order** + family location hint ([Battle-5](DESIGN-BATTLES.md#battle-5-gym-rosters)); field use from collection ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)). Until that ships, dev testing may use `OPENWORLD_TESTING_GRANTS` (HM02 from Mom).

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Vanilla per-Leader HM gifts (wrong move / wrong Leader) | Replaced by badge-order HM table ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)) | Rewrite Leader defeat scripts to grant the correct HM for this badge count |
| **HM fetch / delivery quests** (Bill's PC, SS Anne, etc.) | HMs come from Gym Leaders, not errands | Remove or skip fetch chains; no NPC should gate an HM behind a side quest |
| NPCs teaching Cut / Surf / etc. (Bill, HM tutors, story gates) | Leaders grant HMs; collection-based field use | Remove teach scripts; keep obstacles that respect unlocked HM flags |
| Whirlpool / Waterfall / Strength story gates on routes and dungeons | Badge-count unlock | Replace with badge checks or remove where travel must stay open |
| Flash / Headbutt tutor & story acquisition | Unlocked via Gym badge order + collection field use ([World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)) | Remove or skip vanilla tutor gates and Flash/Headbutt quest NPCs |

## Interior / warp leftovers (starting city)

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| New Bark player-house door when start ≠ New Bark | Should enter **displaced** interior, not Mom cutscene | [Vision-3](DESIGN-VISION.md#vision-3-starting-location) — not started |
| Goldenrod / Saffron displaced house interiors | Outdoor door now warps to canonical Mom house | Vanilla NPCs inside old interiors may confuse players — strip or redirect |

## How to use this section

- When a feature in [Index-2](DESIGN.md#index-2-current-technical-baseline) or [Story-1](DESIGN-STORY.md#story-1-story-and-script-content) is marked **verified**, check whether vanilla duplicates belong here.
- When implementing a row here, note the scr_seq / zone_event member in `documentation/HACK-NOTES.md` (same as other field recipes).
- Do **not** treat this as permission to implement [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves) — HM order is tentatively decided there; implementation still open.
---
