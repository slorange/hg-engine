# Pokémon Wandering Heart — Release TODO

Work that must ship before **initial release**. [DESIGN-FUTURE.md](DESIGN-FUTURE.md) is intentionally out of scope here.

**Policy** (why we remove vanilla content): [DESIGN-STORY.md § Story-3](DESIGN-STORY.md#story-3-story-and-script-policy). **Recipes:** [HACK-NOTES.md](HACK-NOTES.md).

Once a change has been user tested and commit ready, remove it from this file and update [CHANGELOG.md](../CHANGELOG.md) if player-visible.

---

## Known bugs

Regressions in the **current ROM** (not incomplete design from domain sections).

| ID | Symptom | Notes |
| -- | ------- | ----- |
| **KB-3** | Cherrygrove guide — Town Map / running-shoes tutorial cutscene still runs; guide NPC is invisible on new saves. | Mom already grants shoes + Town Map. Fix via guide triggers, not hide-flag alone. See [Vanilla cleanup — Mom / intro](#superseded-by-mom-cutscene--starting-grants). |
| **KB-6** | Mom (player house 1F) — after intro, seated Mom shows broken dialogue or wrong menus. | After open-world intro; [Story-1](DESIGN-STORY.md#story-1-starting-city-and-home), [Story-2](DESIGN-STORY.md#story-2-starter-pokémon-and-intro-flow). |
| **KB-8** | Ecruteak Gym — if you enter before Burned Tower, elder cutscene runs (walk, eject) but his “Morty is out” dialogue is **blank**. | Leader slot **1** only patched; likely `614.txt` vs vanilla elder msg index — member **922**, non-leader slot. |
| **KB-9** | Crash when leaving **Mahogany Gym** (returning to the field after exit). | Inconsistent — could not reproduce on retest. Potentially related to KB-23 |
| **KB-21** | **Mist** — when the **opponent** uses Mist, it starts **Sandstorm** (weather / message / field effect) instead of team Mist. **Player’s own Mist OK**. | Same data/scripts for both sides in source; suspect **enemy / trainer battle path** (party build, client IDs, or AI execution) — not `Moves.c` effect wiring. Repro vs trainers; compare `enemy_party` / battle controller for defender vs attacker. |
| **KB-22** | **Thunder Wave** — when the **opponent** uses it, appears to **miss every time** (or never paralyzes). **Player’s own Thunder Wave OK**. | Player path works; enemy path may differ (`BattleSystem_CheckMoveHit`, before-move checks, or trainer move data). Repro vs wild vs trainer; note target types (Ground = no effect, not miss). |
| **KB-23** | **Olivine Gym** — after Jasmine gives the Mineral Badge and you leave the gym, the player is stuck: no movement and no menu. | Reproduced as the **5th** Johto badge. That badge starts the Rocket event. Once the Radio Tower is under siege, Whitney cannot be unlocked. The Rocket `setvar` in `scr_seq_jasmine_gym_slot0.s` only runs when `count_badges` is exactly **3**, so it did not fire. At 5 badges the shared reward block grants HM02 Fly, then the TM menu. The lock is on the way out, so check Olivine’s on-transition / gym-exit script. |

---

## Needs testing

Implemented or suspected-fixed items that still need an in-game playtest before they can be removed.

| Item | Design | What to test |
| ---- | ------ | ------------ |
| **Thief / Covet loot to bag** | | **Thief / Covet** in a wild battle — stolen item goes to the bag, original held item re-equipped. |
| **Ruins of Alph and roaming Unown** | [World-6](DESIGN-WORLD.md#world-6-unown-collection-quest) | On a fresh run, solve all four picture puzzles and verify each records completion. Check that neither roamer appears before the fourth puzzle and that it unlocks both. Find level 45 `!` in Johto and `?` in Kanto. Verify fleeing, HP and status persistence, the catch cap, and that a knocked-out roamer returns after the next League clear while a caught one stays gone. |
| **Poké Ball catch rates** | [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) | Test all eight crafted balls plus Net and Repeat. Cover Fast and Heavy bracket boundaries, Fast’s legendary beast bonus, Level’s anchors and intermediate ratios, Dusk’s cave floors and outdoor day/night rates, Love’s gender and Egg Group cases, Friend’s family bonus and 200 friendship, Dream’s sleep and Comatose cases, Quick’s first and later turns, Net’s Water and Bug targets, and Repeat’s caught and uncaught species. Include non-qualifying controls. |
| **Ground & hidden item pickups** | [World-8](DESIGN-WORLD.md#ground-and-hidden-items) | Playtest a visible ball and hidden spot, then revisit after collecting. Check that a full Bag or Apricorn Box leaves the spot available and that a retry gives the same bundle. Verify Apricorn Box counts and pickup text, and spot-check the randomized Ice Path pickup and fixed Mt. Moon Moon Stone. |
| **Lansat Berry held effect** | [Items-5](DESIGN-ITEMS.md#items-5-berry-economy) | Lower a holder without Gluttony or Focus Energy to 25% HP or below. Verify that the berry is consumed and raises critical-hit rate. The held-item branch in `src/battle/battle_item.c` calls the generic sharp stat-raise script, while the Fling branch calls the dedicated crit-raise script. Check for an unintended stat change. |
| **Enigma Berry held effect** | [Items-5](DESIGN-ITEMS.md#items-5-berry-economy) | Survive a super-effective damaging hit and verify that the berry is consumed and restores one quarter of max HP, limited by missing HP. Use a neutral hit as a control. The hit handler in `src/individual/CheckDefenderItemEffectOnHit.c` selects the heal script without setting its HP calculation value. |

---

## Wilds ([DESIGN-WILDS.md](DESIGN-WILDS.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Wild ecology — remaining methods & specials** | [Wilds-6](DESIGN-WILDS.md#wilds-6-per-save-wild-ecology-shuffle) | **Still:** Swarms, Safari Zone |
| **Distance caps — Safari Zone** | [Wilds-1 § Encounter methods](DESIGN-WILDS.md#encounter-methods-poc-coverage) | **Not yet** hooked to distance table |

---

## World ([DESIGN-WORLD.md](DESIGN-WORLD.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Remove dev badge gate (Route 29 → 46)** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | PoC **2-badge** gatehouse must go before release |
| **Endgame badge guards** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | Ship **Route 26** (13 badges / Waterfall tier), **Route 23** + Victory Road / League, **Route 28** + Mt. Silver |
| **Dark Cave & Rock Tunnel (Flash)** | [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves) | Entrance message until Flash (1 badge). |

---

## Items ([DESIGN-ITEMS.md](DESIGN-ITEMS.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Pokéathlon prizes** | [Items-1](DESIGN-ITEMS.md#items-1-item-acquisition-channels) | Update the prize exchange to stock the planned Pokéathlon rewards. |
| **Additional Apricorn tree locations** | [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) | Add trees at new locations beyond the existing 60. |
| **Apricorn regrowth clock** | [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) | Tie tree regrowth to the accelerated clock so harvested trees refresh once per in-game day. |

---

## Story ([DESIGN-STORY.md](DESIGN-STORY.md))

### Intro and home

[Story-1](DESIGN-STORY.md#story-1-starting-city-and-home) design; step **1** complete.

| Step | Direction | Status |
| ---- | --------- | ------ |
| **2** | Start city outdoor home door → Mom interior | **Rolled back** — retarget on map load (v2 plan in Story-1) |
| **3** | New Bark house door (start ≠ New Bark) → displaced interior | **Not started** |
| **4** | Leave displaced interior → New Bark outdoor | **Not started** |

Displaced-interior NPC/script cleanup: [Vanilla cleanup](#vanilla-cleanup-backlog) (Copycat / Saffron home, etc.).

### Olivine Gym lighthouse-gossip NPCs

Mom intro skips the lighthouse fetch but **`clearflag FLAG_HIDE_OLIVINE_GYM_GENTLEMAN/GIRL` (476/477)** still reveals the two vanilla gym NPCs (zone_event **080**, scr_seq **913** scripts **2–3**, text **606**) — dialogue assumes Amphy / Jasmine at the lighthouse. **Hide flags alone do not disable interaction** (invisible ghost talk reported in testing). Need a verified fix on **`2_080`** / **913** / **606**: remove or replace NPCs, NOP talk scripts, or rewrite lines — not outdoor Olivine **074**. Recipe context: [HACK-NOTES § Olivine Secret Medicine](HACK-NOTES.md#olivine-secret-medicine-jasmine).

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
| Olivine Gym gossip NPCs (476/477) | Lighthouse fetch skipped on new saves | [Story § Olivine Gym](TODO.md#olivine-gym-lighthouse-gossip-npcs) — zone **080**, not city **074** |
| Copycat / S.S. Ticket story (partial) | Pass + Ticket from Mom; train patched | Displaced-interior scripts still vanilla ([Story-1](DESIGN-STORY.md#story-1-starting-city-and-home)) |
| Power Plant / Machine Part (partial) | Magnet Train open without quest | Test if power plant is in correct state |

### Superseded obstacles and NPC chains

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| SquirtBottle / Floria flower-shop chain | Route 36 Sudowoodo removed | Remove or flavour-only Goldenrod SquirtBottle girl |
| Sudowoodo encounter scripts (Route 36) | Tree hidden via Mom intro flag | Optional: relocate encounter elsewhere later |
| Stale badge-gate scripts (R32, R36, Mahogany, …) | Replaced by open travel | Scan coord triggers / talk scripts |
| Kurt’s house entry cutscene (Azalea Town) | Thanks the player for helping against Team Rocket after the Slowpoke Well story is skipped | Remove the entry cutscene and its Pokégear number offer. Keep Kurt’s regular retired-crafter dialogue. |

### Superseded HM and progression teaching

Target: Gym Leaders grant badge + TM + HM order ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| **HM fetch / delivery quests** (Bill's PC, SS Anne, etc.) | HMs from Gym Leaders | Remove or skip fetch chains |
| NPCs teaching Cut / Surf / etc. (Bill, HM tutors, story gates) | Leaders grant HMs | Remove teach scripts; keep HM-respecting obstacles |
| Whirlpool / Waterfall / Strength story gates on routes and dungeons | Badge-count unlock | Replace with badge checks or remove for open travel |
| Flash / Headbutt tutor & story acquisition | Gym badge order | Remove or skip vanilla tutor gates |
