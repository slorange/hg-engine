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
| **KB-9** | Crash when leaving **Mahogany Gym** (returning to the field after exit). | Inconsistent — could not reproduce on retest. |
| **KB-15** | Game Corner **Pokémon** prizes — clerk says “Your party’s full!” even when the party has fewer than six Pokémon. | Goldenrod scr_seq **910** / Celadon **804**; TM and held-item prizes may still work. [HACK-NOTES § KB-15](HACK-NOTES.md#kb-15--game-corner-pokémon-prizes-partys-full). |
| **KB-18** | **Saffron City Poké Mart** — the **second shop teller** (specialty clerk) is **missing** from the interior; only the badge-tier clerk remains. | `MAP_T11FS0101` / scr_seq **409**; specialty shelf **`sSaffronMart`** (mart index **15**). [HACK-NOTES § KB-18](HACK-NOTES.md#kb-18--saffron-mart-second-clerk-vanished). |
| **KB-21** | **Mist** — when the **opponent** uses Mist, it starts **Sandstorm** (weather / message / field effect) instead of team Mist. **Player’s own Mist OK**. | Same data/scripts for both sides in source; suspect **enemy / trainer battle path** (party build, client IDs, or AI execution) — not `Moves.c` effect wiring. Repro vs trainers; compare `enemy_party` / battle controller for defender vs attacker. |
| **KB-22** | **Thunder Wave** — when the **opponent** uses it, appears to **miss every time** (or never paralyzes). **Player’s own Thunder Wave OK**. | Player path works; enemy path may differ (`BattleSystem_CheckMoveHit`, before-move checks, or trainer move data). Repro vs wild vs trainer; note target types (Ground = no effect, not miss). |
---

## Needs testing

Implemented or suspected-fixed items that still need an in-game playtest before they can be removed.

| Item | Design | What to test |
| ---- | ------ | ------------ |
| **Brock — Gym TM choice menu** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Pewter Gym post-defeat TM picker: labels match unlock order then TM number; badge minimums per [`gym_tm_pools.tsv`](../data/gym_tms/gym_tm_pools.tsv); menu selections map correctly (values **0–5**); rematch TM flow. [HACK-NOTES § Pewter Gym](HACK-NOTES.md#pewter-gym--brock--gym-tm-choice-pool-prototype). |
| **Janine — Gym TM (single option skips menu)** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Fuchsia: under **6** badges, Toxic is given with no menu. At **6** badges, Toxic + Poison Jab menu. At **8**, Sludge Bomb is added. Rematch uses the same rule. [HACK-NOTES § Fuchsia Gym](HACK-NOTES.md#fuchsia-gym--janine--gym-tm-choice-pool). |
| **Blue — Gym TM choice** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Viridian: under **2** badges, Swagger is given with no menu. Then Safeguard (**2**), Double Team (**4**), Swords Dance (**6**), Trick Room (**8**). Rematch uses the same rule. [HACK-NOTES § Viridian Gym](HACK-NOTES.md#viridian-gym--blue--gym-tm-choice-pool). |
| **Erika — Gym TM choice** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Celadon: under **2** badges, Bullet Seed is given with no menu. Then Grass Knot (**2**), Giga Drain (**4**), Solar Beam and Energy Ball (**8**). Rematch uses the same rule. [HACK-NOTES § Celadon Gym](HACK-NOTES.md#celadon-gym--erika--gym-tm-choice-pool). |
| **Sabrina — Gym TM choice** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Saffron: Skill Swap and Psych Up are both available from the first badge, so the menu always opens. Then Calm Mind (**4**), Dream Eater (**6**), Psychic (**10**). Rematch uses the same rule. [HACK-NOTES § Saffron Gym](HACK-NOTES.md#saffron-gym--sabrina--gym-tm-choice-pool). |
| **Blaine — Gym TM choice** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | Cinnabar cave gym: under **2** badges, Sunny Day is given with no menu. Then Will-O-Wisp (**2**), Fire Blast and Overheat (**8**), Flamethrower (**10**). Rematch uses the same rule. [HACK-NOTES § Cinnabar Gym](HACK-NOTES.md#cinnabar-gym--blaine--gym-tm-choice-pool). |
| **Day Care respects level cap** | [Battle-2](DESIGN-BATTLES.md#battle-2-badge-level-caps) | Day Care EXP must not raise Pokémon above the current badge-based player cap. Unconfirmed, needs investigation or testing |
| **Thief / Covet loot to bag** | | **Thief / Covet** in a wild battle — stolen item goes to the bag, original held item re-equipped. |

---

## Gyms ([DESIGN-BATTLES.md](DESIGN-BATTLES.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Gym Leader HM grants (all rows)** | [World-3](DESIGN-WORLD.md#badge--field-abilities-single-reference), [Battle-3](DESIGN-BATTLES.md#first-defeat-rewards) | Badge-order table decided; rewrite Leader scripts — [Vanilla cleanup § HM](#superseded-hm-and-progression-teaching) |
| **Gym TM choice pools** | [World-4 § Gym TMs](DESIGN-WORLD.md#gym-tms) | In tree: Brock, Misty, Lt. Surge, Erika, Janine, Sabrina, Blaine, Blue (one unlocked TM skips the menu). Badge minimums: [`data/gym_tms/gym_tm_pools.tsv`](../data/gym_tms/gym_tm_pools.tsv). Remaining: Johto Leaders |

---

## Wilds ([DESIGN-WILDS.md](DESIGN-WILDS.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Wild ecology — remaining methods & specials** | [Wilds-6](DESIGN-WILDS.md#wilds-6-per-save-wild-ecology-shuffle) | **Still:** Swarms, Safari Zone, Bug Contest, gifts, legendaries, static overworld |
| **Distance caps — Safari Zone** | [Wilds-1 § Encounter methods](DESIGN-WILDS.md#encounter-methods-poc-coverage) | **Not yet** hooked to distance table |
| **Distance caps — Bug Catching Contest** | [Wilds-1 § Encounter methods](DESIGN-WILDS.md#encounter-methods-poc-coverage) | **Not yet** hooked |

---

## World ([DESIGN-WORLD.md](DESIGN-WORLD.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Cross-region Fly (Johto ↔ Kanto)** | [World-1](DESIGN-WORLD.md#world-1-world-transportation), [Fly map § cross-region attempts](HACK-NOTES.md#cross-region-fly-attempts-pinned) | Kanto scroll works (`OPENWORLD_FLY_MAP` arm9 hook); destination filter still vanilla; overlay 101 patch sites tried in Sep 2026 all failed or no-op (see HACK-NOTES) |
| **Abra Pokémon Center travel** | [World-1 § Abra fast travel](DESIGN-WORLD.md#abra-fast-travel) | **Not implemented** — visited-cities-only fast travel before Fly |
| **Remove dev badge gate (Route 29 → 46)** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | PoC **2-badge** gatehouse must go before release |
| **Endgame badge guards** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | Ship **Route 26** (13 badges / Waterfall tier), **Route 23** + Victory Road / League, **Route 28** + Mt. Silver |
| **Violet / Fuchsia shard traders** | [World-7 § Rare battle berries](DESIGN-WORLD.md#world-7-berry-economy) | Liechi–Rowap via shard exchange menus |
| **Move relearner — easy access** | | **Every Pokémon Center** is the target UX. Architecture choice: (1) one hub Center + warps with tracked return + dynamic exit, (2) patch every Center when adding features, or (3) hook Nurse Joy / PC interaction globally (may not cover new NPCs e.g. Abra teleporter). |
| **Ground & hidden item pickups** | [World-8](DESIGN-WORLD.md#world-8-item-acquisition-channels) | Replace static per-spot item lists with random generation from the curated rare-item list |

---

## Battles & Pokémon systems ([DESIGN-BATTLES.md](DESIGN-BATTLES.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Hidden Ability rates** | | Wild **10%** HA; ordinary trainers **20%**; Gym trainers **30%** |
| **Trainer IVs / EVs** | [Battle-2](DESIGN-BATTLES.md#battle-2-badge-level-caps) | Scale trainer **EVs** with badges; **higher IVs** for Gym Leaders |
| **HM removal via move replace** | [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves) | HMs removable through normal move replacement, not only the Move Deleter |

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

### Superseded HM and progression teaching

Target: Gym Leaders grant badge + TM + HM order ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

| Vanilla content | Why obsolete | Cleanup |
|-----------------|--------------|---------|
| Vanilla per-Leader HM gifts (wrong move / wrong Leader) | Badge-order HM table | Rewrite Leader defeat scripts |
| **HM fetch / delivery quests** (Bill's PC, SS Anne, etc.) | HMs from Gym Leaders | Remove or skip fetch chains |
| NPCs teaching Cut / Surf / etc. (Bill, HM tutors, story gates) | Leaders grant HMs | Remove teach scripts; keep HM-respecting obstacles |
| Whirlpool / Waterfall / Strength story gates on routes and dungeons | Badge-count unlock | Replace with badge checks or remove for open travel |
| Flash / Headbutt tutor & story acquisition | Gym badge order | Remove or skip vanilla tutor gates |