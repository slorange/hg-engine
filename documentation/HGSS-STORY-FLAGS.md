# HGSS story flags (pret)

Working index for **Wandering Heart** story skips ([DESIGN-STORY.md](../DESIGN-STORY.md)). The **Wandering Heart** column lists fork usage from [HACK-NOTES.md](HACK-NOTES.md) and patched scripts.

**Canonical in this repo:** `armips/include/flags.s` (`// Story Flags`, decimal **100–399**). This table uses **pret symbol names** for readability ([pret `flags.h`](https://github.com/pret/pokeheartgold/blob/master/include/constants/flags.h) — same indices; a few names differ, e.g. nurse card). No new flag IDs from pret — only naming / cross-reference.

**PKHeX:** event-flag editor uses the **decimal** index (e.g. 107 = Pokédex). Subset of names in [PKHeX `flags_hgss_en.txt`](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Resources/text/script/gen4/flags_hgss_en.txt).

Regenerate: `python tools/gen_story_flags_doc.py` (edit `WANDERING_HEART_NOTES` in that script).

| Dec | Hex | pret symbol | Wandering Heart |
| --- | --- | ----------- | --------------- |
| 100 | 0x64 | `FLAG_NURSE_NOTICED_CARD` | Patched commonscript nurse: `setflag` (`FLAG_NURSE_NOTICED_TRAINER_CARD` in armips). |
| 101 | 0x65 | `FLAG_WAS_TOLD_ABOUT_POKERUS` | Patched commonscript: `setflag` (`FLAG_UNK_065` / pret pokerus notice). |
| 102 | 0x66 | `FLAG_UNK_066` |  |
| 103 | 0x67 | `FLAG_UNK_067` |  |
| 104 | 0x68 | `FLAG_UNK_068` |  |
| 105 | 0x69 | `FLAG_UNK_069` |  |
| 106 | 0x6A | `FLAG_GOT_STARTER` | Mom intro: starter menu → `setflag` ([HACK-NOTES § Open-world inventory](HACK-NOTES.md#open-world-starting-inventory-new-saves)). |
| 107 | 0x6B | `FLAG_GOT_POKEDEX` | Mom intro: Pokédex (`GivePokedex` + flag); `include/constants/event_flags.h`. |
| 108 | 0x6C | `FLAG_EXCHANGED_RED_SCALE` |  |
| 109 | 0x6D | `FLAG_GOT_APRICORN_BOX` | Mom intro: Apricorn Box grant + `setflag`. |
| 110 | 0x6E | `FLAG_GOT_TM05_FROM_ROUTE_32_MAN` |  |
| 111 | 0x6F | `FLAG_UNK_06F` |  |
| 112 | 0x70 | `FLAG_GOT_EGG_FROM_ELMS_ASSISTANT` |  |
| 113 | 0x71 | `FLAG_TRADE_VIOLET_CITY_BELLSPROUT_ONIX` |  |
| 114 | 0x72 | `FLAG_UNK_072` |  |
| 115 | 0x73 | `FLAG_GOT_TM51_FROM_FALKNER` | Falkner gym patch: TM51 reward `setflag`. |
| 116 | 0x74 | `FLAG_UNK_074` |  |
| 117 | 0x75 | `FLAG_GOT_OLD_ROD` | Olivine + Route 44 rod gurus; `src/fishing_rod.c` gates rods on this flag. |
| 118 | 0x76 | `FLAG_UNK_076` |  |
| 119 | 0x77 | `FLAG_UNK_077` |  |
| 120 | 0x78 | `FLAG_UNK_078` |  |
| 121 | 0x79 | `FLAG_GAVE_RIVAL_NAME_TO_OFFICER` |  |
| 122 | 0x7A | `FLAG_GOT_KINGS_ROCK_FROM_SLOWPOKE_WELL_MAN` |  |
| 123 | 0x7B | `FLAG_BEAT_AZALEA_ROCKETS` | Mom intro: post–Proton + **425/426**; member **866** clearflag **415** @ coord 83, NOP rival @868/903/936. |
| 124 | 0x7C | `FLAG_UNK_07C` |  |
| 125 | 0x7D | `FLAG_FOUND_FIRST_FARFETCHD` |  |
| 126 | 0x7E | `FLAG_FOUND_SECOND_FARFETCHD` |  |
| 127 | 0x7F | `FLAG_GOT_TM89_FROM_BUGSY` |  |
| 128 | 0x80 | `FLAG_GOT_HM01` |  |
| 129 | 0x81 | `FLAG_GOT_CHARCOAL_FROM_AZALEA_TOWN_MAN` |  |
| 130 | 0x82 | `FLAG_UNK_082` |  |
| 131 | 0x83 | `FLAG_GOT_TM12_FROM_ILEX_FOREST_GATE_WOMAN` |  |
| 132 | 0x84 | `FLAG_UNK_084` |  |
| 133 | 0x85 | `FLAG_GOT_TM45_FROM_WHITNEY` |  |
| 134 | 0x86 | `FLAG_UNK_086` |  |
| 135 | 0x87 | `FLAG_UNK_087` |  |
| 136 | 0x88 | `FLAG_UNK_088` |  |
| 137 | 0x89 | `FLAG_UNK_089` |  |
| 138 | 0x8A | `FLAG_GOT_RADIO_CARD` |  |
| 139 | 0x8B | `FLAG_UNK_08B` |  |
| 140 | 0x8C | `FLAG_UNK_08C` |  |
| 141 | 0x8D | `FLAG_TRADE_GOLDENROD_CITY_DROWZEE_MACHOP` |  |
| 142 | 0x8E | `FLAG_UNK_08E` |  |
| 143 | 0x8F | `FLAG_GOT_TM11_FROM_RADIO_TOWER_WOMAN` |  |
| 144 | 0x90 | `FLAG_UNK_090` |  |
| 145 | 0x91 | `FLAG_GOT_BRIGHTPOWDER_FROM_MARY` |  |
| 146 | 0x92 | `FLAG_UNK_092` |  |
| 147 | 0x93 | `FLAG_UNK_093` |  |
| 148 | 0x94 | `FLAG_UNK_094` |  |
| 149 | 0x95 | `FLAG_GOT_EEVEE_FROM_BILL` |  |
| 150 | 0x96 | `FLAG_UNK_096` |  |
| 151 | 0x97 | `FLAG_UNK_097` |  |
| 152 | 0x98 | `FLAG_UNK_098` |  |
| 153 | 0x99 | `FLAG_MET_PASSERBY_BOY` |  |
| 154 | 0x9A | `FLAG_UNK_09A` | Mom intro: `setflag` — gates mart `ITEM_POKE_BALL` sales (HACK-NOTES § Mart Poké Ball). |
| 155 | 0x9B | `FLAG_OPENED_GOLDENROD_PURPLE_GATE` |  |
| 156 | 0x9C | `FLAG_GOT_POKEGEAR` | Mom intro: Pokégear + fanfare. |
| 157 | 0x9D | `FLAG_UNK_09D` |  |
| 158 | 0x9E | `FLAG_UNK_09E` |  |
| 159 | 0x9F | `FLAG_GOT_PICK_UP_EGG_CALL_FROM_ELM` |  |
| 160 | 0xA0 | `FLAG_UNK_0A0` |  |
| 161 | 0xA1 | `FLAG_UNK_0A1` |  |
| 162 | 0xA2 | `FLAG_GOT_HM03` |  |
| 163 | 0xA3 | `FLAG_GOT_DOWSING_MACHINE` |  |
| 164 | 0xA4 | `FLAG_ENGAGING_STATIC_POKEMON` |  |
| 165 | 0xA5 | `FLAG_GOT_MAGNET_FROM_SUNNY` |  |
| 166 | 0xA6 | `FLAG_GOT_TM30_FROM_MORTY` | Morty gym patch: TM30 reward `setflag`. |
| 167 | 0xA7 | `FLAG_TALKED_TO_MOM_AFTER_NAMING_RIVAL` |  |
| 168 | 0xA8 | `FLAG_UNK_0A8` |  |
| 169 | 0xA9 | `FLAG_UNK_0A9` |  |
| 170 | 0xAA | `FLAG_UNK_0AA` |  |
| 171 | 0xAB | `FLAG_GOT_TM83_FROM_MOOMOO_FARM_WOMAN` |  |
| 172 | 0xAC | `FLAG_UNK_0AC` |  |
| 173 | 0xAD | `FLAG_UNK_0AD` |  |
| 174 | 0xAE | `FLAG_UNK_0AE` |  |
| 175 | 0xAF | `FLAG_UNK_0AF` |  |
| 176 | 0xB0 | `FLAG_UNK_0B0` |  |
| 177 | 0xB1 | `FLAG_GOT_HARD_STONE_FROM_ARTHUR` |  |
| 178 | 0xB2 | `FLAG_UNK_0B2` |  |
| 179 | 0xB3 | `FLAG_UNK_0B3` |  |
| 180 | 0xB4 | `FLAG_UNK_0B4` |  |
| 181 | 0xB5 | `FLAG_UNK_0B5` |  |
| 182 | 0xB6 | `FLAG_UNK_0B6` |  |
| 183 | 0xB7 | `FLAG_UNK_0B7` |  |
| 184 | 0xB8 | `FLAG_UNK_0B8` |  |
| 185 | 0xB9 | `FLAG_GOT_SECRETPOTION` | Olivine Secret Medicine: lighthouse scene + `Bag_AddItem` sets flag ([HACK-NOTES](HACK-NOTES.md)). |
| 186 | 0xBA | `FLAG_GOT_TM01_FROM_CHUCK` |  |
| 187 | 0xBB | `FLAG_GOT_HM02` |  |
| 188 | 0xBC | `FLAG_UNK_0BC` |  |
| 189 | 0xBD | `FLAG_GOT_GOOD_ROD` | Rod gurus Good Rod tier; `src/fishing_rod.c`. |
| 190 | 0xBE | `FLAG_TRADE_OLIVINE_CITY_KRABBY_VOLTORB` |  |
| 191 | 0xBF | `FLAG_GOT_LOAN_SHUCKLE` |  |
| 192 | 0xC0 | `FLAG_UNK_0C0` |  |
| 193 | 0xC1 | `FLAG_RETURNED_OR_INHERITED_LOAN_SHUCKLE` |  |
| 194 | 0xC2 | `FLAG_GOT_TM23_FROM_JASMINE` | Jasmine gym patch: TM23 reward `setflag`. |
| 195 | 0xC3 | `FLAG_UNK_0C3` |  |
| 196 | 0xC4 | `FLAG_UNK_0C4` |  |
| 197 | 0xC5 | `FLAG_UNK_0C5` | Mahogany Rocket skip: `clearflag` (Mom intro + `scr_seq_t28_005_patch.s` if starting items off). |
| 198 | 0xC6 | `FLAG_BEAT_RADIO_TOWER_ROCKETS` | Mahogany Rocket skip: `setflag` beat radio tower (Mom intro; OnLoad full patch if starting items off). |
| 199 | 0xC7 | `FLAG_GOT_TM10_FROM_LAKE_OF_RAGE_MAN` |  |
| 200 | 0xC8 | `FLAG_UNK_0C8` |  |
| 201 | 0xC9 | `FLAG_GOT_RED_SCALE` | Mahogany skip: **do not set** — keeps Red Gyarados chain (HACK-NOTES). |
| 202 | 0xCA | `FLAG_ROCKET_HIDEOUT_CLEARED` | Mahogany Rocket skip: `setflag` hideout cleared (Mom intro; OnLoad full patch if starting items off). |
| 203 | 0xCB | `FLAG_REMOVED_ROCKET_HIDEOUT_B3F_ELECTRODE_1` |  |
| 204 | 0xCC | `FLAG_REMOVED_ROCKET_HIDEOUT_B3F_ELECTRODE_2` |  |
| 205 | 0xCD | `FLAG_REMOVED_ROCKET_HIDEOUT_B3F_ELECTRODE_3` |  |
| 206 | 0xCE | `FLAG_GOT_TM36_FROM_ROUTE_43_GUARD` |  |
| 207 | 0xCF | `FLAG_UNK_0CF` |  |
| 208 | 0xD0 | `FLAG_TRADE_BLACKTHORN_CITY_DRAGONAIR_DODRIO` |  |
| 209 | 0xD1 | `FLAG_UNK_0D1` |  |
| 210 | 0xD2 | `FLAG_GOT_TM07_FROM_PRYCE` | Pryce gym patch: TM07 reward `setflag`. |
| 211 | 0xD3 | `FLAG_UNK_0D3` |  |
| 212 | 0xD4 | `FLAG_GOT_SOFT_SAND_FROM_SANTOS` |  |
| 213 | 0xD5 | `FLAG_GOT_BLACK_BELT_FROM_WESLEY` |  |
| 214 | 0xD6 | `FLAG_UNK_0D6` |  |
| 215 | 0xD7 | `FLAG_GOT_SHARP_BEAK_FROM_MONICA` |  |
| 216 | 0xD8 | `FLAG_GOT_TWISTEDSPOON_FROM_TUSCANY` |  |
| 217 | 0xD9 | `FLAG_GOT_POISON_BARB_FROM_FRIEDA` |  |
| 218 | 0xDA | `FLAG_GOT_TM59_FROM_CLAIR` |  |
| 219 | 0xDB | `FLAG_FAILED_DRAGONS_DEN_QUIZ` |  |
| 220 | 0xDC | `FLAG_GOT_DRATINI_FROM_MASTER_JUST_NOW` |  |
| 221 | 0xDD | `FLAG_GOT_DRATINI_FROM_MASTER_LONG_AGO` |  |
| 222 | 0xDE | `FLAG_UNK_0DE` |  |
| 223 | 0xDF | `FLAG_GOT_BLACKGLASSES_FROM_DARK_CAVE_MAN` |  |
| 224 | 0xE0 | `FLAG_UNK_0E0` |  |
| 225 | 0xE1 | `FLAG_UNK_0E1` |  |
| 226 | 0xE2 | `FLAG_UNK_0E2` |  |
| 227 | 0xE3 | `FLAG_UNK_0E3` |  |
| 228 | 0xE4 | `FLAG_DEFEATED_WILL` |  |
| 229 | 0xE5 | `FLAG_DEFEATED_KOGA` |  |
| 230 | 0xE6 | `FLAG_DEFEATED_BRUNO` |  |
| 231 | 0xE7 | `FLAG_DEFEATED_KAREN` |  |
| 232 | 0xE8 | `FLAG_UNK_0E8` |  |
| 233 | 0xE9 | `FLAG_GOT_TM37_FROM_ROUTE_27_WOMAN` |  |
| 234 | 0xEA | `FLAG_UNK_0EA` |  |
| 235 | 0xEB | `FLAG_BOAT_ARRIVED` | Mom intro: `FLAG_BOAT_ARRIVED` — SS Aqua post-first-voyage (pret). |
| 236 | 0xEC | `FLAG_UNK_0EC` |  |
| 237 | 0xED | `FLAG_UNK_0ED` |  |
| 238 | 0xEE | `FLAG_GOT_ELMS_PANIC_CALL` |  |
| 239 | 0xEF | `FLAG_UNK_0EF` |  |
| 240 | 0xF0 | `FLAG_UNK_0F0` |  |
| 241 | 0xF1 | `FLAG_UNK_0F1` |  |
| 242 | 0xF2 | `FLAG_GOT_SS_TICKET_FROM_ELM` | Mom intro: `FLAG_UNK_0F2` / pret `GOT_SS_TICKET_FROM_ELM` (S.S. Ticket item also from Mom). |
| 243 | 0xF3 | `FLAG_GOT_MYSTIC_WATER_FROM_CHERRYGROVE_CITY_MAN` |  |
| 244 | 0xF4 | `FLAG_UNK_0F4` | Falkner gym patch: vanilla side-effect `setflag` (`FLAG_UNK_0F4`). |
| 245 | 0xF5 | `FLAG_UNK_0F5` |  |
| 246 | 0xF6 | `FLAG_UNK_0F6` |  |
| 247 | 0xF7 | `FLAG_GOT_PP_MAX_FROM_VERMILLION_CITY_MAN` |  |
| 248 | 0xF8 | `FLAG_GOT_RARE_CANDY_FROM_FAN_CLUB_CHAIRMAN` |  |
| 249 | 0xF9 | `FLAG_SNORLAX_MEET` |  |
| 250 | 0xFA | `FLAG_UNK_0FA` |  |
| 251 | 0xFB | `FLAG_UNK_0FB` |  |
| 252 | 0xFC | `FLAG_UNK_0FC` |  |
| 253 | 0xFD | `FLAG_GOT_ALL_FOUR_FRONTIER_PRINTS` | Patched commonscript: Frontier prints → unlock path. |
| 254 | 0xFE | `FLAG_MET_HALL_STREAK_TRACKER_DUDE` |  |
| 255 | 0xFF | `FLAG_GOT_SCRATCH_CARD_INFO` |  |
| 256 | 0x100 | `FLAG_UNK_100` |  |
| 257 | 0x101 | `FLAG_UNK_101` |  |
| 258 | 0x102 | `FLAG_UNK_102` |  |
| 259 | 0x103 | `FLAG_UNK_103` |  |
| 260 | 0x104 | `FLAG_UNK_104` |  |
| 261 | 0x105 | `FLAG_UNK_105` |  |
| 262 | 0x106 | `FLAG_UNK_106` |  |
| 263 | 0x107 | `FLAG_UNK_107` |  |
| 264 | 0x108 | `FLAG_UNK_108` |  |
| 265 | 0x109 | `FLAG_UNK_109` |  |
| 266 | 0x10A | `FLAG_UNK_10A` |  |
| 267 | 0x10B | `FLAG_UNK_10B` |  |
| 268 | 0x10C | `FLAG_GOT_TYROGUE_FROM_KARATE_KING` |  |
| 269 | 0x10D | `FLAG_BEAT_KARATE_KING` |  |
| 270 | 0x10E | `FLAG_GOT_QUICK_CLAW_FROM_NATIONAL_PARK_WOMAN` |  |
| 271 | 0x10F | `FLAG_UNK_10F` |  |
| 272 | 0x110 | `FLAG_GOT_UNOWN_REPORT` |  |
| 273 | 0x111 | `FLAG_UNK_111` |  |
| 274 | 0x112 | `FLAG_UNK_112` |  |
| 275 | 0x113 | `FLAG_UNK_113` |  |
| 276 | 0x114 | `FLAG_UNK_114` |  |
| 277 | 0x115 | `FLAG_UNK_115` |  |
| 278 | 0x116 | `FLAG_CAUGHT_HO_OH` |  |
| 279 | 0x117 | `FLAG_CAUGHT_LUGIA` |  |
| 280 | 0x118 | `FLAG_RESTORED_POWER` | Magnet Train: `checkflag` bypass in `tools/patch_scr_seq_train.py` (HACK-NOTES). |
| 281 | 0x119 | `FLAG_UNK_119` |  |
| 282 | 0x11A | `FLAG_GOT_EVERSTONE_FROM_ELM` |  |
| 283 | 0x11B | `FLAG_GOT_BAG` | Mom intro: bag / Pokémon menu unlock. |
| 284 | 0x11C | `FLAG_GOT_TRAINER_CARD` | Mom intro: trainer card unlock. |
| 285 | 0x11D | `FLAG_GOT_SAVE_BUTTON` | Mom intro: save button unlock. |
| 286 | 0x11E | `FLAG_GOT_OPTIONS_BUTTON` | Mom intro: options button unlock. |
| 287 | 0x11F | `FLAG_GOT_EXPN_CARD` |  |
| 288 | 0x120 | `FLAG_GOT_POWER_PLANT_MANAGERS_STORY` |  |
| 289 | 0x121 | `FLAG_TRADE_POWER_PLANT_DUGTRIO_MAGNETON` |  |
| 290 | 0x122 | `FLAG_GOT_NUGGET_FROM_ACE_TRAINER_M_KEVIN` |  |
| 291 | 0x123 | `FLAG_UNK_123` |  |
| 292 | 0x124 | `FLAG_GOT_TM19_FROM_ERIKA` |  |
| 293 | 0x125 | `FLAG_FARFETCHD_NOTICED_YOU` |  |
| 294 | 0x126 | `FLAG_UNK_126` |  |
| 295 | 0x127 | `FLAG_UNK_127` |  |
| 296 | 0x128 | `FLAG_UNK_128` |  |
| 297 | 0x129 | `FLAG_UNK_129` |  |
| 298 | 0x12A | `FLAG_UNK_12A` |  |
| 299 | 0x12B | `FLAG_UNLOCKED_MT_SILVER` |  |
| 300 | 0x12C | `FLAG_UNLOCKED_WEST_KANTO` |  |
| 301 | 0x12D | `FLAG_GOT_TM84_FROM_JANINE` |  |
| 302 | 0x12E | `FLAG_GOT_TM85_FROM_VIRIDIAN_CITY_MAN` |  |
| 303 | 0x12F | `FLAG_GOT_TM29_FROM_MR_PSYCHIC` |  |
| 304 | 0x130 | `FLAG_GOT_UPGRADE_FROM_SAFFRON_CITY_GUARD` |  |
| 305 | 0x131 | `FLAG_GOT_CLEANSE_TAG_FROM_ROUTE_5_GRANDMA` |  |
| 306 | 0x132 | `FLAG_UNK_132` |  |
| 307 | 0x133 | `FLAG_TRADE_PEWTER_CITY_HAUNTER_XATU` |  |
| 308 | 0x134 | `FLAG_GOT_NUGGET_FROM_ROUTE_2_MAN` |  |
| 309 | 0x135 | `FLAG_GOT_SACRED_ASH_FROM_ROUTE_2_LAB_AIDE` |  |
| 310 | 0x136 | `FLAG_UNK_136` |  |
| 311 | 0x137 | `FLAG_GOT_TM47_FROM_ROUTE_28_CELEBRITY` |  |
| 312 | 0x138 | `FLAG_UNK_138` |  |
| 313 | 0x139 | `FLAG_UNK_139` |  |
| 314 | 0x13A | `FLAG_UNK_13A` |  |
| 315 | 0x13B | `FLAG_UNK_13B` |  |
| 316 | 0x13C | `FLAG_UNK_13C` |  |
| 317 | 0x13D | `FLAG_UNK_13D` |  |
| 318 | 0x13E | `FLAG_UNK_13E` |  |
| 319 | 0x13F | `FLAG_UNK_13F` |  |
| 320 | 0x140 | `FLAG_UNK_140` |  |
| 321 | 0x141 | `FLAG_WON_THIS_BUG_CONTEST` |  |
| 322 | 0x142 | `FLAG_UNK_142` |  |
| 323 | 0x143 | `FLAG_SAW_JOHTO_DEX_CERTIFICATE` |  |
| 324 | 0x144 | `FLAG_SAW_NATIONAL_DEX_CERTIFICATE` |  |
| 325 | 0x145 | `FLAG_UNK_145` |  |
| 326 | 0x146 | `FLAG_UNK_146` |  |
| 327 | 0x147 | `FLAG_UNK_147` |  |
| 328 | 0x148 | `FLAG_UNK_148` |  |
| 329 | 0x149 | `FLAG_UNK_149` |  |
| 330 | 0x14A | `FLAG_CAUGHT_ZAPDOS` |  |
| 331 | 0x14B | `FLAG_UNK_14B` |  |
| 332 | 0x14C | `FLAG_UNK_14C` |  |
| 333 | 0x14D | `FLAG_UNK_14D` |  |
| 334 | 0x14E | `FLAG_UNK_14E` |  |
| 335 | 0x14F | `FLAG_GOT_JUDGE_EXPLANATION` |  |
| 336 | 0x150 | `FLAG_UNK_150` |  |
| 337 | 0x151 | `FLAG_MET_ROUTE_47_EMBEDDED_TOWER_HIKER` |  |
| 338 | 0x152 | `FLAG_UNK_152` |  |
| 339 | 0x153 | `FLAG_UNK_153` |  |
| 340 | 0x154 | `FLAG_UNK_154` |  |
| 341 | 0x155 | `FLAG_UNK_155` |  |
| 342 | 0x156 | `FLAG_UNK_156` |  |
| 343 | 0x157 | `FLAG_UNK_157` |  |
| 344 | 0x158 | `FLAG_GOT_SPELL_TAG_FROM_CELADON_CITY_MAN` |  |
| 345 | 0x159 | `FLAG_GOT_MAREEP_EGG_FROM_PRIMO` |  |
| 346 | 0x15A | `FLAG_GOT_WOOPER_EGG_FROM_PRIMO` |  |
| 347 | 0x15B | `FLAG_GOT_SLUGMA_EGG_FROM_PRIMO` |  |
| 348 | 0x15C | `FLAG_GOT_LUCKY_PUNCH_FROM_ROUTE_14_WOMAN` |  |
| 349 | 0x15D | `FLAG_UNK_15D` |  |
| 350 | 0x15E | `FLAG_MET_MOVE_MANIAC` |  |
| 351 | 0x15F | `FLAG_BUG_CONTEST_OTHER_POKES_HELD` |  |
| 352 | 0x160 | `FLAG_ELMS_LAB_PREVENT_PLAYER_ESCAPE` |  |
| 353 | 0x161 | `FLAG_SHOWED_FRIEND_A_SHINY_LEAF` |  |
| 354 | 0x162 | `FLAG_TRADE_LT_SURGE_PIKACHU` |  |
| 355 | 0x163 | `FLAG_GOT_RAGECANDYBAR` |  |
| 356 | 0x164 | `FLAG_UNK_164` |  |
| 357 | 0x165 | `FLAG_TRADE_BROCK_BONSLY_RHYHORN` |  |
| 358 | 0x166 | `FLAG_TRADE_JASMINE_STEELIX` |  |
| 359 | 0x167 | `FLAG_TRADE_STEVEN_FORRETRESS_BELDUM` |  |
| 360 | 0x168 | `FLAG_UNK_168` |  |
| 361 | 0x169 | `FLAG_CAUGHT_SUDOWOODO` |  |
| 362 | 0x16A | `FLAG_CAUGHT_RED_GYARADOS` |  |
| 363 | 0x16B | `FLAG_CAUGHT_MEWTWO` |  |
| 364 | 0x16C | `FLAG_CAUGHT_ARTICUNO` |  |
| 365 | 0x16D | `FLAG_CAUGHT_MOLTRES` |  |
| 366 | 0x16E | `FLAG_UNK_16E` |  |
| 367 | 0x16F | `FLAG_SPECIAL_MART_PHARMACY` | Commonscript `special_mart` routing when pharmacy mart active (vanilla). |
| 368 | 0x170 | `FLAG_SPECIAL_MART_BITTER` | Commonscript `special_mart` routing when bitter mart active (vanilla). |
| 369 | 0x171 | `FLAG_SPECIAL_MART_MAHOGANY_GOOD` | Mahogany Rocket skip + Mom intro: `setflag` → Mahogany good mart stock. |
| 370 | 0x172 | `FLAG_UNK_172` |  |
| 371 | 0x173 | `FLAG_CAUGHT_SNORLAX` |  |
| 372 | 0x174 | `FLAG_GOT_LURE_BALL_FROM_ROUTE_32_KURT_FAN` |  |
| 373 | 0x175 | `FLAG_CAUGHT_SUICUNE` |  |
| 374 | 0x176 | `FLAG_UNK_176` |  |
| 375 | 0x177 | `FLAG_GOT_HOENN_STARTER_FROM_STEVEN` |  |
| 376 | 0x178 | `FLAG_UNK_178` |  |
| 377 | 0x179 | `FLAG_CAUGHT_GROUDON` |  |
| 378 | 0x17A | `FLAG_CAUGHT_KYOGRE` |  |
| 379 | 0x17B | `FLAG_CAUGHT_RAYQUAZA` |  |
| 380 | 0x17C | `FLAG_UNK_17C` |  |
| 381 | 0x17D | `FLAG_GOT_TM50_FROM_BLAINE` |  |
| 382 | 0x17E | `FLAG_GOT_TM92_FROM_BLUE` |  |
| 383 | 0x17F | `FLAG_GOT_TM80_FROM_BROCK` |  |
| 384 | 0x180 | `FLAG_GOT_TM03_FROM_MISTY` |  |
| 385 | 0x181 | `FLAG_GOT_TM34_FROM_LT_SURGE` |  |
| 386 | 0x182 | `FLAG_GOT_TM48_FROM_SABRINA` |  |
| 387 | 0x183 | `FLAG_UNK_183` |  |
| 388 | 0x184 | `FLAG_UNK_184` |  |
| 389 | 0x185 | `FLAG_GOT_HM08` |  |
| 390 | 0x186 | `FLAG_UNK_186` |  |
| 391 | 0x187 | `FLAG_UNK_187` |  |
| 392 | 0x188 | `FLAG_UNK_188` |  |
| 393 | 0x189 | `FLAG_UNK_189` |  |
| 394 | 0x18A | `FLAG_SPECIAL_MART_MT_MOON` | Commonscript `special_mart` routing when Mt. Moon mart active (vanilla). |
| 395 | 0x18B | `FLAG_BEAT_OR_ESCAPED_FROM_GROUDON_OR_KYOGRE` |  |
| 396 | 0x18C | `FLAG_UNK_18C` |  |
| 397 | 0x18D | `FLAG_UNK_18D` |  |
| 398 | 0x18E | `FLAG_UNK_18E` |  |
| 399 | 0x18F | `FLAG_UNK_18F` |  |
