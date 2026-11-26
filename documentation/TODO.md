# Pokémon Wandering Heart — Release TODO

Work that must ship before **initial release**. [DESIGN-FUTURE.md](DESIGN-FUTURE.md) is intentionally out of scope here.

**Policy** (why we remove vanilla content): [DESIGN-STORY.md § Story-3](DESIGN-STORY.md#story-3-story-and-script-policy). **Recipes:** [HACK-NOTES.md](HACK-NOTES.md).

Once a change has been user tested and commit ready, remove it from this file and update [CHANGELOG.md](../CHANGELOG.md) if player-visible.

---

## Known bugs

Regressions in the **current ROM** (not incomplete design from domain sections).

| ID | Symptom | Notes |
| -- | ------- | ----- |
| **KB-8** | Ecruteak Gym — if you enter before Burned Tower, elder cutscene runs (walk, eject) but his “Morty is out” dialogue is **blank**. | Leader slot **1** only patched; likely `614.txt` vs vanilla elder msg index — member **922**, non-leader slot. |

---

## Needs testing

Implemented or suspected-fixed items that still need an in-game playtest before they can be removed.

| Item | Design | What to test |
| ---- | ------ | ------------ |
| **KB-9: Mahogany Gym exit crash** | | Retest leaving Mahogany Gym after the Goldenrod Rocket takeover removal. |
| **KB-23: Olivine Gym exit softlock** | | Earn Jasmine's badge as the fifth Johto badge. After exiting, verify movement and menu access with the takeover removed. |
| **Gym ecology hints above the catch cap** | [Battle-3 § Pokémon hints](DESIGN-BATTLES.md#pokémon-hints) | Choose a wild hint whose lowest ordinary encounter level exceeds the current catch cap. Verify that the Leader gives the correct minimum badge count. After reaching that count, request the same hint on a rematch and verify that the badge warning is gone. |
| **Power Plant / Machine Part** | | Verify that the Power Plant is in the expected state when the Magnet Train is available without the quest. |
| **Ruins of Alph and roaming Unown** | [World-6](DESIGN-WORLD.md#world-6-unown-collection-quest) | On a fresh run, solve all four picture puzzles and verify each records completion. Check that neither roamer appears before the fourth puzzle and that it unlocks both. Find level 45 `!` in Johto and `?` in Kanto. Verify fleeing, HP and status persistence, the catch cap, and that a knocked-out roamer returns after the next League clear while a caught one stays gone. |
| **Poké Ball catch rates** | [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) | Test changed balls. Cover Fast and Heavy bracket boundaries, Fast’s legendary beast bonus, Level’s anchors and intermediate ratios, Dusk’s cave floors and outdoor day/night rates, Love’s gender and Egg Group cases, Friend’s family bonus and 200 friendship, Dream’s sleep. Include non-qualifying controls. |

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
| **Unown roamer map markers** | [World-6](DESIGN-WORLD.md#world-6-unown-collection-quest) | Show the current routes of Unown `!` in Johto and Unown `?` in Kanto on the Pokégear map using the same marker behavior as other roamers. |
| **Remove dev badge gate (Route 29 → 46)** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | PoC **2-badge** gatehouse must go before release |
| **Endgame badge guards** | [World-2](DESIGN-WORLD.md#world-2-routes-and-content-gating) | Ship **Route 26** (13 badges / Waterfall tier), **Route 23** + Victory Road / League, **Route 28** + Mt. Silver |
| **Dark Cave & Rock Tunnel (Flash)** | [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves) | Entrance message until Flash (1 badge). |
| **Post-battle party heal timing** | [Battle-1](DESIGN-BATTLES.md#recovery) | Healing currently waits for the first overworld step to avoid battle-overlay crashes. Move recovery to the end of battle when returning to the field. Verify that the party and follower recover immediately when turning in place or going straight into another trainer battle. |

---

## Items ([DESIGN-ITEMS.md](DESIGN-ITEMS.md))

| Item | Design | Notes |
| ---- | ------ | ----- |
| **Pokéathlon prizes** | [Items-1](DESIGN-ITEMS.md#items-1-item-acquisition-channels) | Update the prize exchange to stock the planned Pokéathlon rewards. |
| **Additional Apricorn tree locations** | [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) | Add trees at new locations beyond the existing 60. |
| **Apricorn regrowth clock** | [Items-6](DESIGN-ITEMS.md#items-6-apricorn-economy--poké-ball-rebalance) | Tie tree regrowth to the accelerated clock so harvested trees refresh once per in-game day. |

---

## Story Cleanup ([DESIGN-STORY.md](DESIGN-STORY.md))

### Remaining rival events

| Vanilla content | Cleanup |
|-----------------|---------|
| Ecruteak City – Burned Tower | Remove rival battle and encounter. |
| Goldenrod City – Radio Tower | Remove disguise exposure cutscene. |
| Goldenrod City – Underground | Remove rival battle and encounter. |
| Victory Road – Near exit | Remove rival battle and trigger. |
| Mt. Moon – Entrance | Remove rival battle and trigger. |
| Dragon's Den – Lance and Clair | Remove rival multi-battle event. |
| Dragon's Den – Weekly training | Remove recurring rival NPC. |
| Indigo Plateau – Weekly rematches | Remove recurring rival battles. |

### Remaining Team Rocket

| Vanilla content | Cleanup |
|-----------------|---------|
| Ecruteak City – Dance Theater | Remove Rocket Grunt battle and HM reward |
| Mahogany Town – Rocket Hideout | Prevent entry to the hideout. |

### Services and items

| Vanilla content  | Cleanup |
|-----------------|---------|
| Cianwood pharmacy free Secret Medicine | Remove free give; optional flavour dialogue only |
| Olivine Gym gossip NPCs (476/477) | [Story § Olivine Gym](TODO.md#olivine-gym-lighthouse-gossip-npcs) — zone **080**, not city **074** |
| Copycat / S.S. Ticket story (partial) | Displaced-interior scripts still vanilla ([Story-1](DESIGN-STORY.md#story-1-starting-city-and-home)) |
| Steven (Gen 3 Champion) scenes | https://chatgpt.com/c/6b06fca4-b518-83ea-bfc7-d409947410ea |

### HM and progression teaching

Target: Gym Leaders grant badge + TM + HM order ([Battle-3](DESIGN-BATTLES.md#first-defeat-rewards), [World-3](DESIGN-WORLD.md#world-3-hms-and-field-moves)).

| Vanilla acquisition | Cleanup |
|---------------------|---------|
| Fly – Chuck's wife in Cianwood | Remove or Replace HM reward script. |
| Surf – Ecruteak Dance Theater | Remove Rocket Grunt event and HM reward. |
| Strength – Hiker on Route 42 | Remove HM reward script. |
| Rock Climb – Professor Oak in Pallet Town | Remove HM reward script. |
