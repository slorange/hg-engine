# Pokémon Wandering Heart — Design Data

Bulk reference lists for the design. Rules and rationale remain in [World & Travel](DESIGN-WORLD.md), [Wild Encounters & Ecology](DESIGN-WILDS.md), and [Battles, Trainers & Progression](DESIGN-BATTLES.md).

## Sections

- [Data-1. Game Corner prize pools](#data-1-game-corner-prize-pools)
- [Data-2. Gym Leader TM pools](#data-2-gym-leader-tm-pools)
- [Data-3. Move-known evolution thresholds](#data-3-move-known-evolution-thresholds)
- [Data-4. Evolution changes](#data-4-evolution-changes)
- [Data-5. Shop inventories](#data-5-shop-inventories)
- [Data-6. Generated trainer party tables](#data-6-generated-trainer-party-tables)

# Data-1. Game Corner prize pools

Renewable coin prizes at each Game Corner's prize clerks.

## Goldenrod Game Corner

| Category | Prizes |
| -------- | ------ |
| Pokémon | Rotom, Wobbuffet, Smeargle |
| TMs | TM43, TM44, TM46, TM64, TM83, TM90 |
| Held Items | Bright Powder, Quick Claw, Wide Lens, Metronome |

## Celadon Game Corner

| Category | Prizes |
| -------- | ------ |
| Pokémon | Porygon, Eevee, Castform |
| TMs | TM10, TM41, TM49, TM58, TM67, TM82 |
| Held Items | Focus Band, Zoom Lens, Scope Lens, Luck Incense |

---

# Data-2. Gym Leader TM pools

| Leader | TM pool |
| ------ | ------- |
| **Falkner** | TM40, TM51, TM88 |
| **Bugsy** | TM62, TM81, TM89 |
| **Whitney** | TM15, TM27, TM42, TM45, TM68 |
| **Morty** | TM30, TM56, TM65, TM66, TM79 |
| **Chuck** | TM01, TM08, TM31, TM52, TM60 |
| **Jasmine** | TM23, TM47, TM74, TM91 |
| **Pryce** | TM07, TM13, TM14, TM72 |
| **Clair** | TM02, TM59 |
| **Brock** | TM26, TM37, TM39, TM69, TM71, TM80 |
| **Misty** | TM03, TM18, TM55 |
| **Lt. Surge** | TM24, TM25, TM34, TM57, TM73 |
| **Erika** | TM09, TM19, TM22, TM53, TM86 |
| **Janine** | TM06, TM36, TM84 |
| **Sabrina** | TM04, TM29, TM48, TM77, TM85 |
| **Blaine** | TM11, TM35, TM38, TM50, TM61 |
| **Blue** | TM20, TM32, TM75, TM87, TM92 |

---

# Data-3. Move-known evolution thresholds

Minor adjustments made to the learnset to adjust evolution levels:

- Aipom → Ambipom: Double Hit at **28**; 
- Lickitung → Lickilicky: Rollout at **30**.
- Stantler → Wyrdeer: Psyshield Bash at **31**.
- Tangela → Tangrowth: AncientPower at **32**; 
- Girafarig → Farigiraf: Twin Beam at **32**; 
- Dunsparce → Dudunsparce: Hyper Drill at **32**.
- Yanma → Yanmega: AncientPower at **33**; 
- Primeape → Annihilape: Rage Fist at **35**.
- Piloswine → Mamoswine: AncientPower at **36**

---

# Data-4. Evolution changes

Alongside the [item-use rules](DESIGN-ITEMS.md#items-3-evolution-methods-trade--stones), the following families have additional methods or changed evolution timing:

- **Feebas → Milotic:** **Prism Scale** can be used directly.
- **Swinub → Piloswine:** level **22**, reduced from 33.
- **Eevee’s added item options:** Leaf Stone → Leafeon; Ice Stone → Glaceon; Dawn or Sun Stone → Espeon; Dusk or Moon Stone → Umbreon; Shiny Stone → Sylveon.
- **Eevee’s location options:** level up in **Ilex Forest or Viridian Forest** for Leafeon, **Ice Path B3F or Seafoam Islands B4F** for Glaceon, or **Route 10** for Jolteon.
- **Route 10 (outside Power Plant):** leveling up there evolves Magneton → Magnezone, Nosepass → Probopass, and Eevee → Jolteon. **Thunder Stone** also works anywhere for all three.
- **Nosepass → Probopass:** **Metal Coat** also works.

---

# Data-5. Shop inventories

## Badge-gated shelf (most shops)

Poké / Great / Ultra / Net / Repeat / Timer Balls; Repels; Escape Rope; Poké Doll; Sitrus & Lum Berries; **Flash and Headbutt TMs**; Cleanse Tag; held battle items through Life Orb — each row gated by **minimum badge count** (0–12).

## Goldenrod & Celadon department stores

| Floor | Stock |
| ----- | ----- |
| **2F (upper)** | **Goldenrod:** Poké Balls, Repels, Escape Rope, Doll, Cheri → Persim berries — **Celadon:** same berry aisle as vanilla-style upper 2F |
| **2F (lower)** | **Goldenrod:** **Linking Cord**, Chilan Berry, Silk Scarf, Roseli Berry, Fairy Feather — **Celadon:** Poké Balls, Repels, Escape Rope, Doll |
| **TM floor** | **Celadon 3F:** TM12, 21, 28, 76, 78 — **Goldenrod 5F:** TM16, 17, 33, 54, 63 |
| **Battle items** | **Celadon 5F left / Goldenrod 3F:** Power Bracer–Weight + Macho Brace (replaces X items) |
| **Vitamins** | Protein–HP Up + **Rare Candy**, **PP Up**, **PP Max** |
| **Celadon 4F** | **Linking Cord**, Sun & Leaf Stones, Rindo Berry, Miracle Seed |
| **Goldenrod herbs** | Pomeg, Kelpsy, Qualot, Hondew, Grepa, Tamato Berries (replaces powders/roots) |

## Town / route specialty clerks

Themed Evolution items, held items, resist berries:

| Location | Items (summary) |
| -------- | ----------------- |
| Azalea | King's Rock, Silver Powder, Tanga Berry |
| Violet | Razor Fang, Sharp Beak, Coba Berry |
| Ecruteak | Fire Stone, Charcoal, Occa Berry, Magmarizer, Flame Orb |
| Olivine | Secret Medicine, Metal Coat, Babiri Berry |
| Cianwood pharmacy clerk | Poké Ball, Dawn Stone, Black Belt, Chople Berry |
| Vermilion / Safari | Thunder Stone, Electirizer, Magnet, Wacan Berry |
| Cerulean | Water Stone, DeepSea Tooth/Scale, Mystic Water, Passho Berry |
| Lavender | Dusk Stone, Reaper Cloth, Black Glasses, Spell Tag, Kasib, Colbur Berries |
| Saffron | Up-Grade, Dubious Disc, Twisted Spoon, Payapa Berry |
| Fuchsia | Shiny Stone, Poison Barb, Kebia Berry, Toxic Orb, Black Sludge |
| Pewter | Black Augurite, Hard Stone, Charti Berry |
| Viridian | Peat Block, Protector, Soft Sand, Shuca Berry |
| Blackthorn / Battle Frontier | Dragon Scale, Dragon Fang, Haban Berry |
| Mt. Moon Square | Moon Stone |
| Mahogany | Poké Ball, Ice Stone, Never-Melt Ice, Yache Berry, Razor Claw |
| Indigo Plateau | Ultra & Timer Balls, Max Repel, Lum Berry, Leftovers, Shell Bell, Focus Sash, Choice Band / Specs / Scarf, Life Orb |

---

# Data-6. Generated trainer party tables

See [Battle-5](DESIGN-BATTLES.md#battle-5-generated-trainer--gym-parties) for the generation rules.

## Gym and League roster filters

| Leader | Gym type filter | Leader | Exception |
|--------|--------------------------------|--------------|--------|
| Whitney | Normal + Fairy | Jasmine | Mareep line |
| Morty | Ghost + Dark | Misty | Togepi line |
| Clair | Dragon + Water | Blaine | Rhyhorn line |
| Brock | Rock + Ground | Brock | Vulpix line |
| Blue | **All Types** | Pryce | Seel line |
| Lance | Dragon + Flying  | Sabrina | Venonat line |
| |  | Karen | Oddish and Gastly line |
| |  | Koga | Pineco line |
| |  | Bruno | Onix line | 

## Trainer class type pools

| Trainer class | Eligible types or species |
| ------------- | ------------------------- |
| Bug Catcher | Bug |
| Guitarist | Electric |
| Black Belt | Fighting |
| Firebreather | Fire |
| Bird Keeper | Flying |
| Medium | Ghost |
| Boarder, Skier | Ice |
| Burglar, Team Rocket | Fire, Poison, Dark |
| Biker | Poison, Steel |
| Psychic | Psychic |
| Juggler | Psychic or the Voltorb family |
| Sage | Psychic, Ghost |
| Hiker | Rock, Ground |
| Fisherman, Swimmer | Water |
| Sailor | Water, Fighting |
| Beauty | Fairy, Grass |
| Lass | Normal, Fairy |
| Scientist, Super Nerd | Electric, Steel |
| Kimono Girl | Eevee family only |

## Trainer held-item unlocks

| Minimum badges | Items added |
| -------------- | ----------- |
| 0 | Cheri, Chesto, Pecha, Rawst, Aspear, Oran, and Persim Berries. Species gear where compatible. |
| 2 | Type boosters and type resist berries. |
| 3 | Mental Herb. |
| 4 | Sitrus Berry. |
| 5 | Muscle Band, Wise Glasses, Metronome, Quick Claw, Focus Band. |
| 6 | Lum, Liechi, Petaya, Salac, and Starf Berries. |
| 7 | Expert Belt. |
| 8 | Scope Lens, Razor Claw, King’s Rock, Razor Fang. |
| 9 | Leftovers, Bright Powder. |
| 10 | Shell Bell, Focus Sash. |
| 12 | Life Orb. |

## Trainer damaging moves

Moves in this table have a level-up source at level 80 or below, an eligible trainer TM, or an unlocked HM compatible with a species in the generated trainer pool. Base damage is the listed base power. A base power of 1 can be a placeholder for fixed or variable damage. The effect column uses the ROM’s battle-effect labels. The modifier is the trainer’s scoring adjustment before STAB, with accuracy applied separately as described in [Battle-5](DESIGN-BATTLES.md#tms-hms-and-generated-movesets). An entry of ×1 uses the listed power as-is.

Many of these moves have not yet been considered and need a modifier. This is a work in progress.

| Damage move | Base damage | Effect | Modifier |
| ----------- | ----------- | ------ | -------- |
| Absorb | 20 | recover half damage dealt | ×1 |
| Acid | 40 | lower sp def hit | ×1 |
| Acid Spray | 40 | lower sp def 2 hit | ×1 |
| Acrobatics | 55 | double power without item | ×1 |
| Aerial Ace | 60 | bypass accuracy | ×1 |
| Air Cutter | 60 | high critical | ×1 |
| Air Slash | 75 | flinch hit | ×1 |
| Ancient Power | 60 | raise all stats hit | ×1 |
| Aqua Cutter | 70 | high critical | ×1 |
| Aqua Jet | 40 | priority 1 | ×1.4 |
| Aqua Tail | 90 | hit | ×1 |
| Arm Thrust | 15 | multi hit | ×3 |
| Assurance | 60 | double power if target hit | ×1 |
| Astonish | 30 | flinch hit | ×1 |
| Attack Order | 90 | high critical | ×1 |
| Aura Sphere | 80 | bypass accuracy | ×1 |
| Aurora Beam | 65 | lower attack hit | ×1 |
| Avalanche | 60 | double damage if hit | ×1 |
| Axe Kick | 120 | confuse hit crash on miss | ×0.9 |
| Beat Up | 1 | beat up | Use 40 power |
| Bind | 15 | bind hit | ×1 |
| Bite | 60 | flinch hit | ×1 |
| Blaze Kick | 85 | high critical burn hit | ×1 |
| Blizzard | 110 | blizzard | ×1 |
| Body Slam | 85 | paralyze hit | ×1 |
| Bone Rush | 30 | multi hit | ×3 |
| Bonemerang | 50 | hit twice | ×2 |
| Boomburst | 140 | hit | ×1 |
| Bounce | 85 | bounce | ×0.4 |
| Brave Bird | 120 | recoil third | ×0.85 |
| Brick Break | 75 | remove screens | ×1 |
| Brine | 65 | double power when below half | ×1 |
| Bubble Beam | 65 | lower speed hit | ×1 |
| Bug Bite | 60 | eat berry | ×1 |
| Bug Buzz | 90 | lower sp def hit | ×1 |
| Bulldoze | 60 | lower speed hit | ×1 |
| Bullet Punch | 40 | priority 1 | ×1.4 |
| Bullet Seed | 25 | multi hit | ×3 |
| Charge Beam | 50 | raise sp atk hit | ×1 |
| Chatter | 65 | confuse hit | ×1 |
| Clear Smog | 50 | clear smog | ×1 |
| Close Combat | 120 | user def sp def down hit | ×0.9 |
| Comeuppance | 1 | metal burst | ×1 |
| Confusion | 50 | confuse hit | ×1 |
| Counter | 1 | counter | ×1 |
| Covet | 60 | steal held item | ×1 |
| Crabhammer | 100 | high critical | ×1 |
| Cross Chop | 100 | high critical | ×1 |
| Cross Poison | 70 | high critical poison hit | ×1 |
| Crunch | 80 | lower defense hit | ×1 |
| Crush Claw | 75 | lower defense hit | ×1 |
| Cut | 50 | hit | ×1 |
| Dark Pulse | 80 | flinch hit | ×1 |
| Dazzling Gleam | 80 | hit | ×1 |
| Dig | 80 | dig | ×0.4 |
| Disarming Voice | 40 | bypass accuracy | ×1 |
| Discharge | 80 | paralyze hit | ×1 |
| Dive | 80 | dive | ×0.4 |
| Double Hit | 35 | hit twice | ×2 |
| Double Kick | 30 | hit twice | ×2 |
| Double-Edge | 120 | recoil third | ×0.85 |
| Dragon Breath | 60 | paralyze hit | ×1 |
| Dragon Claw | 80 | hit | ×1 |
| Dragon Pulse | 85 | hit | ×1 |
| Dragon Rush | 100 | flinch hit | ×1 |
| Dragon Tail | 60 | force switch hit | ×1 |
| Drain Punch | 75 | recover half damage dealt | ×1 |
| Draining Kiss | 50 | recover three quarters damage dealt | ×1 |
| Drill Peck | 80 | hit | ×1 |
| Drill Run | 80 | high critical | ×1 |
| Dual Chop | 40 | hit twice | ×2 |
| Dual Wingbeat | 40 | hit twice | ×2 |
| Dynamic Punch | 100 | confuse hit | ×1 |
| Earth Power | 90 | lower sp def hit | ×1 |
| Earthquake | 100 | double damage dig | ×1 |
| Electro Ball | 1 | hit | ×1 |
| Ember | 40 | burn hit | ×1 |
| Endeavor | 1 | set hp equal to user | ×1 |
| Energy Ball | 90 | lower sp def hit | ×1 |
| Eruption | 150 | decrease power with less user hp | ×0.7 |
| Explosion | 250 | halve defense | Damage score 0 |
| Extrasensory | 80 | flinch hit | ×1 |
| Extreme Speed | 80 | priority 1 | ×1 |
| Facade | 70 | double power when statused | ×1 |
| Fairy Wind | 40 | hit | ×1 |
| Fake Out | 40 | always flinch first turn only | ×1.4 |
| False Swipe | 40 | leave with 1 hp | ×1 |
| Feint | 30 | remove protect | ×1.4 |
| Fell Stinger | 50 | fell stinger | ×1 |
| Fiery Dance | 80 | raise sp atk hit | ×1 |
| Final Gambit | 1 | final gambit | ×1 |
| Fire Blast | 110 | burn hit | ×1 |
| Fire Fang | 65 | flinch burn hit | ×1 |
| Fire Punch | 75 | burn hit | ×1 |
| Fire Spin | 35 | bind hit | ×1 |
| Flail | 1 | increase power with less hp | ×1 |
| Flame Charge | 50 | raise speed hit | ×1.2 |
| Flame Wheel | 60 | thaw and burn hit | ×1 |
| Flamethrower | 90 | burn hit | ×1 |
| Flare Blitz | 120 | recoil burn hit | ×0.85 |
| Flash Cannon | 80 | lower sp def hit | ×1 |
| Fling | 1 | fling | ×1 |
| Fly | 90 | fly | ×0.4 |
| Focus Blast | 120 | lower sp def hit | ×1 |
| Focus Punch | 150 | hit last whiff if hit | ×0.4 |
| Force Palm | 60 | paralyze hit | ×1 |
| Foul Play | 95 | hit | ×1 |
| Freeze-Dry | 70 | freeze hit | ×1.2 |
| Frost Breath | 60 | always critical | ×1 |
| Frustration | 1 | power based on low friendship | ×1 |
| Fury Attack | 15 | multi hit | ×3 |
| Fury Cutter | 40 | double power each turn | ×1 |
| Fury Swipes | 18 | multi hit | ×3 |
| Future Sight | 120 | hit in 3 turns | ×0.6 |
| Giga Drain | 75 | recover half damage dealt | ×1 |
| Giga Impact | 150 | recharge after | ×0.6 |
| Grass Knot | 1 | increase power with weight | Use 70 power |
| Gunk Shot | 120 | poison hit | ×1 |
| Gust | 40 | double damage fly or bounce | ×1 |
| Gyro Ball | 1 | power based on low speed | Use 70 power |
| Hammer Arm | 100 | user speed down hit | ×0.9 |
| Head Smash | 150 | recoil half | ×0.7 |
| Headbutt | 70 | flinch hit | ×1 |
| Headlong Rush | 120 | user def sp def down hit | ×0.9 |
| Heat Wave | 95 | burn hit | ×1 |
| Heavy Slam | 1 | heavy slam | Use 70 power |
| Hex | 65 | double damage on status | ×1 |
| High Horsepower | 95 | hit | ×1 |
| High Jump Kick | 130 | crash on miss | ×0.9 |
| Horn Attack | 65 | hit | ×1 |
| Hurricane | 110 | hurricane | ×1 |
| Hydro Pump | 110 | hit | ×1 |
| Hyper Beam | 150 | recharge after | ×0.6 |
| Hyper Drill | 120 | hit | ×1 |
| Hyper Voice | 90 | hit | ×1 |
| Ice Beam | 90 | freeze hit | ×1 |
| Ice Fang | 65 | flinch freeze hit | ×1 |
| Ice Punch | 75 | freeze hit | ×1 |
| Ice Shard | 40 | priority 1 | ×1.4 |
| Icicle Crash | 85 | flinch hit | ×1 |
| Icicle Spear | 25 | multi hit | ×3 |
| Icy Wind | 55 | lower speed hit | ×1.2 |
| Incinerate | 60 | incinerate | ×1 |
| Inferno | 100 | burn hit | ×1 |
| Infestation | 20 | bind hit | ×1 |
| Iron Head | 80 | flinch hit | ×1 |
| Iron Tail | 100 | lower defense hit | ×1 |
| Knock Off | 65 | remove held item | ×1.25 |
| Last Resort | 140 | fail if not used all other moves | ×0.35 |
| Lava Plume | 80 | burn hit | ×1 |
| Leaf Blade | 90 | high critical | ×1 |
| Leaf Storm | 130 | user sp atk down 2 | ×0.75 |
| Leaf Tornado | 65 | lower accuracy hit | ×1 |
| Leafage | 40 | hit | ×1 |
| Leech Life | 80 | recover half damage dealt | ×1 |
| Lick | 30 | paralyze hit | ×1 |
| Liquidation | 85 | lower defense hit | ×1 |
| Low Kick | 1 | increase power with weight | Use 70 power |
| Low Sweep | 65 | lower speed hit | ×1 |
| Lunge | 80 | lower attack hit | ×1 |
| Mach Punch | 40 | priority 1 | ×1.4 |
| Magical Leaf | 60 | bypass accuracy | ×1 |
| Mega Drain | 40 | recover half damage dealt | ×1 |
| Mega Kick | 120 | hit | ×1 |
| Mega Punch | 80 | hit | ×1 |
| Megahorn | 120 | hit | ×1 |
| Metal Burst | 1 | metal burst | ×1 |
| Metal Claw | 50 | raise attack hit | ×1 |
| Meteor Mash | 90 | raise attack hit | ×1 |
| Mirror Coat | 1 | mirror coat | ×1 |
| Moonblast | 95 | lower sp atk hit | ×1 |
| Mud Shot | 55 | lower speed hit | ×1 |
| Mud-Slap | 20 | lower accuracy hit | ×1 |
| Muddy Water | 90 | lower accuracy hit | ×1 |
| Mystical Fire | 75 | lower sp atk hit | ×1 |
| Natural Gift | 1 | natural gift | ×1 |
| Night Shade | 1 | level damage flat | Use attacker’s level |
| Night Slash | 70 | high critical | ×1 |
| Nuzzle | 20 | paralyze hit | ×1 |
| Octazooka | 65 | lower accuracy hit | ×1 |
| Outrage | 120 | continue and confuse self | ×0.8 |
| Overheat | 130 | user sp atk down 2 | ×0.75 |
| Pay Day | 40 | increase prize money | ×1 |
| Payback | 50 | double power if hit | ×1 |
| Peck | 35 | hit | ×1 |
| Petal Blizzard | 90 | hit | ×1 |
| Petal Dance | 120 | continue and confuse self | ×0.8 |
| Phantom Force | 90 | shadow force | ×0.4 |
| Pin Missile | 25 | multi hit | ×3 |
| Play Rough | 90 | lower attack hit | ×1 |
| Pluck | 60 | eat berry | ×1 |
| Poison Fang | 50 | badly poison hit | ×1 |
| Poison Jab | 80 | poison hit | ×1 |
| Poison Sting | 15 | poison hit | ×1 |
| Poison Tail | 50 | high critical poison hit | ×1 |
| Pound | 40 | hit | ×1 |
| Powder Snow | 40 | freeze hit | ×1 |
| Power Gem | 80 | hit | ×1 |
| Power Trip | 20 | hit | ×1 |
| Power Whip | 120 | hit | ×1 |
| Present | 1 | random power maybe heal | ×1 |
| Psybeam | 65 | confuse hit | ×1 |
| Psychic | 90 | lower sp def hit | ×1 |
| Psycho Cut | 70 | high critical | ×1 |
| Psyshield Bash | 90 | raise def hit | ×1.1 |
| Psyshock | 80 | hit | ×1 |
| Quick Attack | 40 | priority 1 | ×1.4 |
| Rage Fist | 50 | hit | ×1 |
| Raging Bull | 90 | remove screens | ×1 |
| Raging Fury | 120 | continue and confuse self | ×0.8 |
| Rapid Spin | 50 | remove hazards and binding | ×1.3 |
| Razor Leaf | 55 | high critical | ×1 |
| Razor Shell | 75 | lower defense hit | ×1 |
| Retaliate | 70 | hit | ×1 |
| Return | 1 | power based on friendship | ×1 |
| Revenge | 60 | double damage if hit | ×1 |
| Reversal | 1 | increase power with less hp | ×1 |
| Rock Blast | 25 | multi hit | ×3 |
| Rock Climb | 90 | confuse hit | ×1 |
| Rock Slide | 75 | flinch hit | ×1 |
| Rock Smash | 40 | lower defense hit | ×1 |
| Rock Throw | 50 | hit | ×1 |
| Rock Tomb | 60 | lower speed hit | ×1.2 |
| Rock Wrecker | 150 | recharge after | ×0.6 |
| Rollout | 30 | double power each turn lock into | ×2 |
| Sacred Sword | 90 | hit | ×1 |
| Sand Tomb | 35 | bind hit | ×1 |
| Scratch | 40 | hit | ×1 |
| Secret Power | 70 | secret power | ×1 |
| Seed Bomb | 80 | hit | ×1 |
| Seismic Toss | 1 | level damage flat | Use attacker’s level |
| Self-Destruct | 200 | halve defense | Damage score 0 |
| Shadow Ball | 80 | lower sp def hit | ×1 |
| Shadow Claw | 70 | high critical | ×1 |
| Shadow Punch | 60 | bypass accuracy | ×1 |
| Shadow Sneak | 40 | priority 1 | ×1.4 |
| Shock Wave | 60 | bypass accuracy | ×1 |
| Silver Wind | 60 | raise all stats hit | ×1 |
| Sky Attack | 140 | charge turn high crit flinch | ×0.4 |
| Slam | 80 | hit | ×1 |
| Slash | 70 | high critical | ×1 |
| Sludge | 65 | poison hit | ×1 |
| Sludge Bomb | 90 | poison hit | ×1 |
| Sludge Wave | 95 | poison hit | ×1 |
| Smart Strike | 70 | bypass accuracy | ×1 |
| Smog | 30 | poison hit | ×1 |
| Snarl | 55 | lower sp atk hit | ×1.2 |
| Solar Beam | 120 | charge turn sun skips | ×0.4 |
| Spark | 65 | paralyze hit | ×1 |
| Spit Up | 1 | spit up | ×1 |
| Steel Wing | 70 | raise def hit | ×1 |
| Stomp | 65 | flinch minimize double hit | ×1 |
| Stomping Tantrum | 75 | hit | ×1 |
| Stone Axe | 65 | stealth rock hit | ×1 |
| Stone Edge | 100 | high critical | ×1 |
| Stored Power | 20 | hit | ×1 |
| Storm Throw | 60 | always critical | ×1 |
| Strength | 80 | hit | ×1 |
| Struggle Bug | 50 | lower sp atk hit | ×1 |
| Submission | 80 | recoil quarter | ×0.9 |
| Sucker Punch | 70 | hit first if target attacking | ×1 |
| Super Fang | 1 | halve hp | ×1 |
| Superpower | 120 | user atk def down hit | ×0.8 |
| Surf | 90 | double damage dive | ×1 |
| Swift | 60 | bypass accuracy | ×1 |
| Tackle | 40 | hit | ×1 |
| Take Down | 90 | recoil quarter | ×0.9 |
| Thief | 60 | steal held item | ×1 |
| Thrash | 120 | continue and confuse self | ×0.8 |
| Throat Chop | 80 | throat chop | ×1 |
| Thunder | 110 | thunder | ×1 |
| Thunder Fang | 65 | flinch paralyze hit | ×1 |
| Thunder Punch | 75 | paralyze hit | ×1 |
| Thunder Shock | 40 | paralyze hit | ×1 |
| Thunderbolt | 90 | paralyze hit | ×1 |
| Tri Attack | 80 | random primary status hit | ×1 |
| Triple Kick | 10 | hit three times increment base power 10 | Use 60 power |
| Twin Beam | 40 | hit twice | ×2 |
| Twister | 40 | flinch double damage fly or bounce | ×1 |
| U-turn | 70 | switch hit | ×1.1 |
| Uproar | 90 | uproar | ×1 |
| Vacuum Wave | 40 | priority 1 | ×1.4 |
| Venoshock | 65 | double power on poisoned | ×1 |
| Vine Whip | 45 | hit | ×1 |
| Vise Grip | 55 | hit | ×1 |
| Vital Throw | 70 | priority neg 1 bypass accuracy | ×1 |
| Volt Switch | 70 | switch hit | ×1.1 |
| Water Gun | 40 | hit | ×1 |
| Water Pulse | 60 | confuse hit | ×1 |
| Water Spout | 150 | decrease power with less user hp | ×0.7 |
| Waterfall | 80 | flinch hit | ×1 |
| Wave Crash | 120 | recoil third | ×0.85 |
| Weather Ball | 50 | change type with weather | ×1 |
| Whirlpool | 35 | whirlpool | ×1 |
| Wild Charge | 90 | recoil third | ×0.85 |
| Wing Attack | 60 | hit | ×1 |
| Wood Hammer | 120 | recoil third | ×0.85 |
| Wrap | 15 | bind hit | ×1 |
| X-Scissor | 80 | hit | ×1 |
| Zap Cannon | 120 | paralyze hit | ×1 |
| Zen Headbutt | 80 | flinch hit | ×1 |

## Trainer status move tiers

These are all assigned tiers, including damaging moves that can occupy a status slot. Explosion and Self-Destruct use their status tier and have a zero damage score. Availability still depends on the Pokémon’s legal sources.

| Tier | Moves |
| ---- | ----- |
| S | Belly Drum, Cotton Guard, Dragon Dance, Fake Out, Glare, Leech Seed, Milk Drink, Minimize, Nasty Plot, Nuzzle, Quiver Dance, Recover, Roost, Shell Smash, Slack Off, Soft-Boiled, Spiky Shield, Spore, Stone Axe, Strength Sap, Swords Dance, Tail Glow |
| A | Acid Armor, Agility, Amnesia, Autotomize, Bulk Up, Calm Mind, Charm, Coil, Confuse Ray, Cosmic Power, Curse, Detect, Disable, Double Team, Eerie Impulse, Encore, Explosion, Fake Tears, Feather Dance, Hone Claws, Iron Defense, Light Screen, Lovely Kiss, Moonlight, Morning Sun, Reflect, Rock Polish, Sleep Powder, Stun Spore, Synthesis, Take Heart, Taunt, Thunder Wave, Toxic, Will-O-Wisp, Wish, Yawn |
| B | Aqua Ring, Aromatherapy, Aurora Veil, Baby-Doll Eyes, Baton Pass, Captivate, Cotton Spore, Defend Order, Defog, Destiny Bond, Electric Terrain, Endure, Focus Energy, Gastro Acid, Grassy Terrain, Gravity, Hail, Haze, Heal Bell, Hypnosis, Ingrain, Life Dew, Magnet Rise, Metal Sound, Noble Roar, Poison Gas, Poison Powder, Protect, Rain Dance, Rest, Safeguard, Sandstorm, Scary Face, Screech, Self-Destruct, Snowscape, Spikes, Stealth Rock, Sticky Web, Stockpile, String Shot, Substitute, Sunny Day, Sweet Kiss, Tailwind, Teeter Dance, Tickle, Torment, Toxic Spikes, Toxic Thread, Trick Room, Venom Drench, Work Up |
| C | Acupressure, Attract, Charge, Conversion, Conversion 2, Copycat, Dark Void, Defense Curl, Entrainment, Flash, Flatter, Growl, Growth, Harden, Heart Swap, Howl, Leer, Lock-On, Metronome, Mind Reader, Pain Split, Play Nice, Power Trick, Psycho Shift, Role Play, Sand Attack, Simple Beam, Sing, Skill Swap, Smokescreen, Soak, Supersonic, Swagger, Swallow, Tail Whip, Tearful Look, Transform, Withdraw, Worry Seed |

## Trainer status move categories

The generator allows at most one move from each shared category. A move listed in multiple categories occupies each of them. Moves with no shared category can appear together. This table includes damaging moves that can fill a status slot.

| Category | Moves |
| -------- | ----- |
| Setup | Acid Armor, Acupressure, Agility, Amnesia, Autotomize, Belly Drum, Bulk Up, Calm Mind, Charge, Coil, Cosmic Power, Cotton Guard, Curse, Defend Order, Defense Curl, Double Team, Dragon Dance, Focus Energy, Growth, Harden, Hone Claws, Howl, Iron Defense, Minimize, Nasty Plot, Quiver Dance, Rock Polish, Shell Smash, Stockpile, Swords Dance, Tail Glow, Take Heart, Withdraw, Work Up |
| Sleep | Dark Void, Hypnosis, Lovely Kiss, Sing, Sleep Powder, Spore, Yawn |
| Recovery | Aqua Ring, Ingrain, Life Dew, Milk Drink, Moonlight, Morning Sun, Pain Split, Recover, Rest, Roost, Slack Off, Soft-Boiled, Strength Sap, Swallow, Synthesis, Wish |
| Paralysis | Glare, Nuzzle, Stun Spore, Thunder Wave |
| Poison | Poison Gas, Poison Powder, Toxic, Toxic Thread |
| Protect | Detect, Endure, Protect, Spiky Shield |
| Confusion | Confuse Ray, Flatter, Supersonic, Swagger, Sweet Kiss, Teeter Dance |
| Lower Attack | Baby-Doll Eyes, Charm, Feather Dance, Growl, Noble Roar, Play Nice, Tearful Look, Tickle, Venom Drench |
| Lower Sp. Atk | Captivate, Eerie Impulse, Noble Roar, Tearful Look, Venom Drench |
| Lower Defense | Leer, Screech, Tail Whip, Tickle |
| Lower Sp. Def | Fake Tears, Metal Sound |
| Lower Speed | Cotton Spore, Scary Face, String Shot, Toxic Thread, Venom Drench |
| Lower Accuracy | Flash, Sand Attack, Smokescreen |
| Weather | Hail, Rain Dance, Sandstorm, Snowscape, Sunny Day |
| Terrain | Electric Terrain, Grassy Terrain |
| Entry hazards | Spikes, Stealth Rock, Sticky Web, Stone Axe, Toxic Spikes |
| Status cure | Aromatherapy, Heal Bell |
| Aim (guaranteed hit) | Lock-On, Mind Reader |
| Ability | Entrainment, Gastro Acid, Role Play, Simple Beam, Skill Swap, Worry Seed |
| Physical screen | Aurora Veil, Reflect |
| Special screen | Aurora Veil, Light Screen |
| Self-KO | Explosion, Self-Destruct |
| No shared category | Attract, Baton Pass, Conversion, Conversion 2, Copycat, Defog, Destiny Bond, Disable, Encore, Fake Out, Gravity, Haze, Heart Swap, Leech Seed, Magnet Rise, Metronome, Power Trick, Psycho Shift, Safeguard, Soak, Substitute, Tailwind, Taunt, Torment, Transform, Trick Room, Will-O-Wisp |
