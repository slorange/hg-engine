#!/usr/bin/env python3
"""Regenerate documentation/HGSS-STORY-FLAGS.md from embedded pret story-flag snapshot."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "documentation" / "HGSS-STORY-FLAGS.md"

# Snapshot from pret include/constants/flags.h (story flags 0x64..0x18F)
PRET_DEFINES = """
#define FLAG_NURSE_NOTICED_CARD                         0x64
#define FLAG_WAS_TOLD_ABOUT_POKERUS                     0x65
#define FLAG_UNK_066                                    0x66
#define FLAG_UNK_067                                    0x67
#define FLAG_UNK_068                                    0x68
#define FLAG_UNK_069                                    0x69
#define FLAG_GOT_STARTER                                0x6A
#define FLAG_GOT_POKEDEX                                0x6B
#define FLAG_EXCHANGED_RED_SCALE                        0x6C
#define FLAG_GOT_APRICORN_BOX                           0x6D
#define FLAG_GOT_TM05_FROM_ROUTE_32_MAN                 0x6E
#define FLAG_UNK_06F                                    0x6F
#define FLAG_GOT_EGG_FROM_ELMS_ASSISTANT                0x70
#define FLAG_TRADE_VIOLET_CITY_BELLSPROUT_ONIX          0x71
#define FLAG_UNK_072                                    0x72
#define FLAG_GOT_TM51_FROM_FALKNER                      0x73
#define FLAG_UNK_074                                    0x74
#define FLAG_GOT_OLD_ROD                                0x75
#define FLAG_UNK_076                                    0x76
#define FLAG_UNK_077                                    0x77
#define FLAG_UNK_078                                    0x78
#define FLAG_GAVE_RIVAL_NAME_TO_OFFICER                 0x79
#define FLAG_GOT_KINGS_ROCK_FROM_SLOWPOKE_WELL_MAN      0x7A
#define FLAG_BEAT_AZALEA_ROCKETS                        0x7B
#define FLAG_UNK_07C                                    0x7C
#define FLAG_FOUND_FIRST_FARFETCHD                      0x7D
#define FLAG_FOUND_SECOND_FARFETCHD                     0x7E
#define FLAG_GOT_TM89_FROM_BUGSY                        0x7F
#define FLAG_GOT_HM01                                   0x80
#define FLAG_GOT_CHARCOAL_FROM_AZALEA_TOWN_MAN          0x81
#define FLAG_UNK_082                                    0x82
#define FLAG_GOT_TM12_FROM_ILEX_FOREST_GATE_WOMAN       0x83
#define FLAG_UNK_084                                    0x84
#define FLAG_GOT_TM45_FROM_WHITNEY                      0x85
#define FLAG_UNK_086                                    0x86
#define FLAG_UNK_087                                    0x87
#define FLAG_UNK_088                                    0x88
#define FLAG_UNK_089                                    0x89
#define FLAG_GOT_RADIO_CARD                             0x8A
#define FLAG_UNK_08B                                    0x8B
#define FLAG_UNK_08C                                    0x8C
#define FLAG_TRADE_GOLDENROD_CITY_DROWZEE_MACHOP        0x8D
#define FLAG_UNK_08E                                    0x8E
#define FLAG_GOT_TM11_FROM_RADIO_TOWER_WOMAN            0x8F
#define FLAG_UNK_090                                    0x90
#define FLAG_GOT_BRIGHTPOWDER_FROM_MARY                 0x91
#define FLAG_UNK_092                                    0x92
#define FLAG_UNK_093                                    0x93
#define FLAG_UNK_094                                    0x94
#define FLAG_GOT_EEVEE_FROM_BILL                        0x95
#define FLAG_UNK_096                                    0x96
#define FLAG_UNK_097                                    0x97
#define FLAG_UNK_098                                    0x98
#define FLAG_MET_PASSERBY_BOY                           0x99
#define FLAG_UNK_09A                                    0x9A
#define FLAG_OPENED_GOLDENROD_PURPLE_GATE               0x9B
#define FLAG_GOT_POKEGEAR                               0x9C
#define FLAG_UNK_09D                                    0x9D
#define FLAG_UNK_09E                                    0x9E
#define FLAG_GOT_PICK_UP_EGG_CALL_FROM_ELM              0x9F
#define FLAG_UNK_0A0                                    0xA0
#define FLAG_UNK_0A1                                    0xA1
#define FLAG_GOT_HM03                                   0xA2
#define FLAG_GOT_DOWSING_MACHINE                        0xA3
#define FLAG_ENGAGING_STATIC_POKEMON                    0xA4
#define FLAG_GOT_MAGNET_FROM_SUNNY                      0xA5
#define FLAG_GOT_TM30_FROM_MORTY                        0xA6
#define FLAG_TALKED_TO_MOM_AFTER_NAMING_RIVAL           0xA7
#define FLAG_UNK_0A8                                    0xA8
#define FLAG_UNK_0A9                                    0xA9
#define FLAG_UNK_0AA                                    0xAA
#define FLAG_GOT_TM83_FROM_MOOMOO_FARM_WOMAN            0xAB
#define FLAG_UNK_0AC                                    0xAC
#define FLAG_UNK_0AD                                    0xAD
#define FLAG_UNK_0AE                                    0xAE
#define FLAG_UNK_0AF                                    0xAF
#define FLAG_UNK_0B0                                    0xB0
#define FLAG_GOT_HARD_STONE_FROM_ARTHUR                 0xB1
#define FLAG_UNK_0B2                                    0xB2
#define FLAG_UNK_0B3                                    0xB3
#define FLAG_UNK_0B4                                    0xB4
#define FLAG_UNK_0B5                                    0xB5
#define FLAG_UNK_0B6                                    0xB6
#define FLAG_UNK_0B7                                    0xB7
#define FLAG_UNK_0B8                                    0xB8
#define FLAG_GOT_SECRETPOTION                           0xB9
#define FLAG_GOT_TM01_FROM_CHUCK                        0xBA
#define FLAG_GOT_HM02                                   0xBB
#define FLAG_UNK_0BC                                    0xBC
#define FLAG_GOT_GOOD_ROD                               0xBD
#define FLAG_TRADE_OLIVINE_CITY_KRABBY_VOLTORB          0xBE
#define FLAG_GOT_LOAN_SHUCKLE                           0xBF
#define FLAG_UNK_0C0                                    0xC0
#define FLAG_RETURNED_OR_INHERITED_LOAN_SHUCKLE         0xC1
#define FLAG_GOT_TM23_FROM_JASMINE                      0xC2
#define FLAG_UNK_0C3                                    0xC3
#define FLAG_UNK_0C4                                    0xC4
#define FLAG_UNK_0C5                                    0xC5
#define FLAG_BEAT_RADIO_TOWER_ROCKETS                   0xC6
#define FLAG_GOT_TM10_FROM_LAKE_OF_RAGE_MAN             0xC7
#define FLAG_UNK_0C8                                    0xC8
#define FLAG_GOT_RED_SCALE                              0xC9
#define FLAG_ROCKET_HIDEOUT_CLEARED                     0xCA
#define FLAG_REMOVED_ROCKET_HIDEOUT_B3F_ELECTRODE_1     0xCB
#define FLAG_REMOVED_ROCKET_HIDEOUT_B3F_ELECTRODE_2     0xCC
#define FLAG_REMOVED_ROCKET_HIDEOUT_B3F_ELECTRODE_3     0xCD
#define FLAG_GOT_TM36_FROM_ROUTE_43_GUARD               0xCE
#define FLAG_UNK_0CF                                    0xCF
#define FLAG_TRADE_BLACKTHORN_CITY_DRAGONAIR_DODRIO     0xD0
#define FLAG_UNK_0D1                                    0xD1
#define FLAG_GOT_TM07_FROM_PRYCE                        0xD2
#define FLAG_UNK_0D3                                    0xD3
#define FLAG_GOT_SOFT_SAND_FROM_SANTOS                  0xD4
#define FLAG_GOT_BLACK_BELT_FROM_WESLEY                 0xD5
#define FLAG_UNK_0D6                                    0xD6
#define FLAG_GOT_SHARP_BEAK_FROM_MONICA                 0xD7
#define FLAG_GOT_TWISTEDSPOON_FROM_TUSCANY              0xD8
#define FLAG_GOT_POISON_BARB_FROM_FRIEDA                0xD9
#define FLAG_GOT_TM59_FROM_CLAIR                        0xDA
#define FLAG_FAILED_DRAGONS_DEN_QUIZ                    0xDB
#define FLAG_GOT_DRATINI_FROM_MASTER_JUST_NOW           0xDC
#define FLAG_GOT_DRATINI_FROM_MASTER_LONG_AGO           0xDD
#define FLAG_UNK_0DE                                    0xDE
#define FLAG_GOT_BLACKGLASSES_FROM_DARK_CAVE_MAN        0xDF
#define FLAG_UNK_0E0                                    0xE0
#define FLAG_UNK_0E1                                    0xE1
#define FLAG_UNK_0E2                                    0xE2
#define FLAG_UNK_0E3                                    0xE3
#define FLAG_DEFEATED_WILL                              0xE4
#define FLAG_DEFEATED_KOGA                              0xE5
#define FLAG_DEFEATED_BRUNO                             0xE6
#define FLAG_DEFEATED_KAREN                             0xE7
#define FLAG_UNK_0E8                                    0xE8
#define FLAG_GOT_TM37_FROM_ROUTE_27_WOMAN               0xE9
#define FLAG_UNK_0EA                                    0xEA
#define FLAG_BOAT_ARRIVED                               0xEB
#define FLAG_UNK_0EC                                    0xEC
#define FLAG_UNK_0ED                                    0xED
#define FLAG_GOT_ELMS_PANIC_CALL                        0xEE
#define FLAG_UNK_0EF                                    0xEF
#define FLAG_UNK_0F0                                    0xF0
#define FLAG_UNK_0F1                                    0xF1
#define FLAG_GOT_SS_TICKET_FROM_ELM                     0xF2
#define FLAG_GOT_MYSTIC_WATER_FROM_CHERRYGROVE_CITY_MAN 0xF3
#define FLAG_UNK_0F4                                    0xF4
#define FLAG_UNK_0F5                                    0xF5
#define FLAG_UNK_0F6                                    0xF6
#define FLAG_GOT_PP_MAX_FROM_VERMILLION_CITY_MAN        0xF7
#define FLAG_GOT_RARE_CANDY_FROM_FAN_CLUB_CHAIRMAN      0xF8
#define FLAG_SNORLAX_MEET                               0xF9
#define FLAG_UNK_0FA                                    0xFA
#define FLAG_UNK_0FB                                    0xFB
#define FLAG_UNK_0FC                                    0xFC
#define FLAG_GOT_ALL_FOUR_FRONTIER_PRINTS               0xFD
#define FLAG_MET_HALL_STREAK_TRACKER_DUDE               0xFE
#define FLAG_GOT_SCRATCH_CARD_INFO                      0xFF
#define FLAG_UNK_100                                    0x100
#define FLAG_UNK_101                                    0x101
#define FLAG_UNK_102                                    0x102
#define FLAG_UNK_103                                    0x103
#define FLAG_UNK_104                                    0x104
#define FLAG_UNK_105                                    0x105
#define FLAG_UNK_106                                    0x106
#define FLAG_UNK_107                                    0x107
#define FLAG_UNK_108                                    0x108
#define FLAG_UNK_109                                    0x109
#define FLAG_UNK_10A                                    0x10A
#define FLAG_UNK_10B                                    0x10B
#define FLAG_GOT_TYROGUE_FROM_KARATE_KING               0x10C
#define FLAG_BEAT_KARATE_KING                           0x10D
#define FLAG_GOT_QUICK_CLAW_FROM_NATIONAL_PARK_WOMAN    0x10E
#define FLAG_UNK_10F                                    0x10F
#define FLAG_GOT_UNOWN_REPORT                           0x110
#define FLAG_UNK_111                                    0x111
#define FLAG_UNK_112                                    0x112
#define FLAG_UNK_113                                    0x113
#define FLAG_UNK_114                                    0x114
#define FLAG_UNK_115                                    0x115
#define FLAG_CAUGHT_HO_OH                               0x116
#define FLAG_CAUGHT_LUGIA                               0x117
#define FLAG_RESTORED_POWER                             0x118
#define FLAG_UNK_119                                    0x119
#define FLAG_GOT_EVERSTONE_FROM_ELM                     0x11A
#define FLAG_GOT_BAG                                    0x11B
#define FLAG_GOT_TRAINER_CARD                           0x11C
#define FLAG_GOT_SAVE_BUTTON                            0x11D
#define FLAG_GOT_OPTIONS_BUTTON                         0x11E
#define FLAG_GOT_EXPN_CARD                              0x11F
#define FLAG_GOT_POWER_PLANT_MANAGERS_STORY             0x120
#define FLAG_TRADE_POWER_PLANT_DUGTRIO_MAGNETON         0x121
#define FLAG_GOT_NUGGET_FROM_ACE_TRAINER_M_KEVIN        0x122
#define FLAG_UNK_123                                    0x123
#define FLAG_GOT_TM19_FROM_ERIKA                        0x124
#define FLAG_FARFETCHD_NOTICED_YOU                      0x125
#define FLAG_UNK_126                                    0x126
#define FLAG_UNK_127                                    0x127
#define FLAG_UNK_128                                    0x128
#define FLAG_UNK_129                                    0x129
#define FLAG_UNK_12A                                    0x12A
#define FLAG_UNLOCKED_MT_SILVER                         0x12B
#define FLAG_UNLOCKED_WEST_KANTO                        0x12C
#define FLAG_GOT_TM84_FROM_JANINE                       0x12D
#define FLAG_GOT_TM85_FROM_VIRIDIAN_CITY_MAN            0x12E
#define FLAG_GOT_TM29_FROM_MR_PSYCHIC                   0x12F
#define FLAG_GOT_UPGRADE_FROM_SAFFRON_CITY_GUARD        0x130
#define FLAG_GOT_CLEANSE_TAG_FROM_ROUTE_5_GRANDMA       0x131
#define FLAG_UNK_132                                    0x132
#define FLAG_TRADE_PEWTER_CITY_HAUNTER_XATU             0x133
#define FLAG_GOT_NUGGET_FROM_ROUTE_2_MAN                0x134
#define FLAG_GOT_SACRED_ASH_FROM_ROUTE_2_LAB_AIDE       0x135
#define FLAG_UNK_136                                    0x136
#define FLAG_GOT_TM47_FROM_ROUTE_28_CELEBRITY           0x137
#define FLAG_UNK_138                                    0x138
#define FLAG_UNK_139                                    0x139
#define FLAG_UNK_13A                                    0x13A
#define FLAG_UNK_13B                                    0x13B
#define FLAG_UNK_13C                                    0x13C
#define FLAG_UNK_13D                                    0x13D
#define FLAG_UNK_13E                                    0x13E
#define FLAG_UNK_13F                                    0x13F
#define FLAG_UNK_140                                    0x140
#define FLAG_WON_THIS_BUG_CONTEST                       0x141
#define FLAG_UNK_142                                    0x142
#define FLAG_SAW_JOHTO_DEX_CERTIFICATE                  0x143
#define FLAG_SAW_NATIONAL_DEX_CERTIFICATE               0x144
#define FLAG_UNK_145                                    0x145
#define FLAG_UNK_146                                    0x146
#define FLAG_UNK_147                                    0x147
#define FLAG_UNK_148                                    0x148
#define FLAG_UNK_149                                    0x149
#define FLAG_CAUGHT_ZAPDOS                              0x14A
#define FLAG_UNK_14B                                    0x14B
#define FLAG_UNK_14C                                    0x14C
#define FLAG_UNK_14D                                    0x14D
#define FLAG_UNK_14E                                    0x14E
#define FLAG_GOT_JUDGE_EXPLANATION                      0x14F
#define FLAG_UNK_150                                    0x150
#define FLAG_MET_ROUTE_47_EMBEDDED_TOWER_HIKER          0x151
#define FLAG_UNK_152                                    0x152
#define FLAG_UNK_153                                    0x153
#define FLAG_UNK_154                                    0x154
#define FLAG_UNK_155                                    0x155
#define FLAG_UNK_156                                    0x156
#define FLAG_UNK_157                                    0x157
#define FLAG_GOT_SPELL_TAG_FROM_CELADON_CITY_MAN        0x158
#define FLAG_GOT_MAREEP_EGG_FROM_PRIMO                  0x159
#define FLAG_GOT_WOOPER_EGG_FROM_PRIMO                  0x15A
#define FLAG_GOT_SLUGMA_EGG_FROM_PRIMO                  0x15B
#define FLAG_GOT_LUCKY_PUNCH_FROM_ROUTE_14_WOMAN        0x15C
#define FLAG_UNK_15D                                    0x15D
#define FLAG_MET_MOVE_MANIAC                            0x15E
#define FLAG_BUG_CONTEST_OTHER_POKES_HELD               0x15F
#define FLAG_ELMS_LAB_PREVENT_PLAYER_ESCAPE             0x160
#define FLAG_SHOWED_FRIEND_A_SHINY_LEAF                 0x161
#define FLAG_TRADE_LT_SURGE_PIKACHU                     0x162
#define FLAG_GOT_RAGECANDYBAR                           0x163
#define FLAG_UNK_164                                    0x164
#define FLAG_TRADE_BROCK_BONSLY_RHYHORN                 0x165
#define FLAG_TRADE_JASMINE_STEELIX                      0x166
#define FLAG_TRADE_STEVEN_FORRETRESS_BELDUM             0x167
#define FLAG_UNK_168                                    0x168
#define FLAG_CAUGHT_SUDOWOODO                           0x169
#define FLAG_CAUGHT_RED_GYARADOS                        0x16A
#define FLAG_CAUGHT_MEWTWO                              0x16B
#define FLAG_CAUGHT_ARTICUNO                            0x16C
#define FLAG_CAUGHT_MOLTRES                             0x16D
#define FLAG_UNK_16E                                    0x16E
#define FLAG_SPECIAL_MART_PHARMACY                      0x16F
#define FLAG_SPECIAL_MART_BITTER                        0x170
#define FLAG_SPECIAL_MART_MAHOGANY_GOOD                 0x171
#define FLAG_UNK_172                                    0x172
#define FLAG_CAUGHT_SNORLAX                             0x173
#define FLAG_GOT_LURE_BALL_FROM_ROUTE_32_KURT_FAN       0x174
#define FLAG_CAUGHT_SUICUNE                             0x175
#define FLAG_UNK_176                                    0x176
#define FLAG_GOT_HOENN_STARTER_FROM_STEVEN              0x177
#define FLAG_UNK_178                                    0x178
#define FLAG_CAUGHT_GROUDON                             0x179
#define FLAG_CAUGHT_KYOGRE                              0x17A
#define FLAG_CAUGHT_RAYQUAZA                            0x17B
#define FLAG_UNK_17C                                    0x17C
#define FLAG_GOT_TM50_FROM_BLAINE                       0x17D
#define FLAG_GOT_TM92_FROM_BLUE                         0x17E
#define FLAG_GOT_TM80_FROM_BROCK                        0x17F
#define FLAG_GOT_TM03_FROM_MISTY                        0x180
#define FLAG_GOT_TM34_FROM_LT_SURGE                     0x181
#define FLAG_GOT_TM48_FROM_SABRINA                      0x182
#define FLAG_UNK_183                                    0x183
#define FLAG_UNK_184                                    0x184
#define FLAG_GOT_HM08                                   0x185
#define FLAG_UNK_186                                    0x186
#define FLAG_UNK_187                                    0x187
#define FLAG_UNK_188                                    0x188
#define FLAG_UNK_189                                    0x189
#define FLAG_SPECIAL_MART_MT_MOON                       0x18A
#define FLAG_BEAT_OR_ESCAPED_FROM_GROUDON_OR_KYOGRE     0x18B
#define FLAG_UNK_18C                                    0x18C
#define FLAG_UNK_18D                                    0x18D
#define FLAG_UNK_18E                                    0x18E
#define FLAG_UNK_18F                                    0x18F
"""

PAT = re.compile(r"#define\s+(\S+)\s+(0x[0-9A-Fa-f]+)")

# Wandering Heart usage (repo + HACK-NOTES). Keys = decimal story-flag index.
WANDERING_HEART_NOTES: dict[int, str] = {
    100: "Patched commonscript nurse: `setflag` (`FLAG_NURSE_NOTICED_TRAINER_CARD` in armips).",
    101: "Patched commonscript: `setflag` (`FLAG_UNK_065` / pret pokerus notice).",
    106: "Mom intro: starter menu → `setflag` ([HACK-NOTES § Open-world inventory](HACK-NOTES.md#open-world-starting-inventory-new-saves)).",
    107: "Mom intro: Pokédex (`GivePokedex` + flag); `include/constants/event_flags.h`.",
    109: "Mom intro: Apricorn Box grant + `setflag`.",
    115: "Falkner gym patch: TM51 reward `setflag`.",
    117: "Olivine + Route 44 rod gurus; `src/fishing_rod.c` gates rods on this flag.",
    154: "Mom intro: `setflag` — gates mart `ITEM_POKE_BALL` sales (HACK-NOTES § Mart Poké Ball).",
    156: "Mom intro: Pokégear + fanfare.",
    450: "Mom intro: `setflag` hide Route 36 Sudowoodo (`scr_seq_t20_mom_script0.s`).",
    166: "Morty gym patch: TM30 reward `setflag`.",
    185: "Olivine Secret Medicine: lighthouse scene + `Bag_AddItem` sets flag ([HACK-NOTES](HACK-NOTES.md)).",
    189: "Rod gurus Good Rod tier; `src/fishing_rod.c`.",
    194: "Jasmine gym patch: TM23 reward `setflag`.",
    197: "Mahogany Rocket skip: `clearflag` (`scr_seq_t28_005_patch.s`).",
    198: "Mahogany Rocket skip: `setflag` (beat radio tower).",
    201: "Mahogany skip: **do not set** — keeps Red Gyarados chain (HACK-NOTES).",
    202: "Mahogany Rocket skip: `setflag` hideout cleared (pret name; not Gyarados hide).",
    210: "Pryce gym patch: TM07 reward `setflag`.",
    244: "Falkner gym patch: vanilla side-effect `setflag` (`FLAG_UNK_0F4`).",
    253: "Patched commonscript: Frontier prints → unlock path.",
    280: "Magnet Train: `checkflag` bypass in `tools/patch_scr_seq_train.py` (HACK-NOTES).",
    283: "Mom intro: bag / Pokémon menu unlock.",
    284: "Mom intro: trainer card unlock.",
    285: "Mom intro: save button unlock.",
    286: "Mom intro: options button unlock.",
    367: "Commonscript `special_mart` routing when pharmacy mart active (vanilla).",
    368: "Commonscript `special_mart` routing when bitter mart active (vanilla).",
    369: "Mahogany Rocket skip: `setflag` → Mahogany good mart stock.",
    394: "Commonscript `special_mart` routing when Mt. Moon mart active (vanilla).",
}


def _md_cell(text: str) -> str:
    return text.replace("|", "\\|")


def main() -> None:
    rows: list[tuple[int, str, str]] = []
    for line in PRET_DEFINES.strip().splitlines():
        m = PAT.match(line.strip())
        if not m:
            continue
        name, hx = m.group(1), m.group(2)
        dec = int(hx, 16)
        rows.append((dec, f"0x{dec:X}", name))

    lines = [
        "# HGSS story flags (pret)",
        "",
        "Working index for **Wandering Heart** story skips ([DESIGN-STORY.md](../DESIGN-STORY.md)). "
        "The **Wandering Heart** column lists fork usage from [HACK-NOTES.md](HACK-NOTES.md) and patched scripts.",
        "",
        "**Canonical in this repo:** `armips/include/flags.s` (`// Story Flags`, decimal **100–399**). "
        "This table uses **pret symbol names** for readability "
        "([pret `flags.h`](https://github.com/pret/pokeheartgold/blob/master/include/constants/flags.h) — same indices; a few names differ, e.g. nurse card). "
        "No new flag IDs from pret — only naming / cross-reference.",
        "",
        "**PKHeX:** event-flag editor uses the **decimal** index (e.g. 107 = Pokédex). "
        "Subset of names in "
        "[PKHeX `flags_hgss_en.txt`](https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Resources/text/script/gen4/flags_hgss_en.txt).",
        "",
        "Regenerate: `python tools/gen_story_flags_doc.py` (edit `WANDERING_HEART_NOTES` in that script).",
        "",
        "| Dec | Hex | pret symbol | Wandering Heart |",
        "| --- | --- | ----------- | --------------- |",
    ]
    for dec, hx, name in rows:
        note = _md_cell(WANDERING_HEART_NOTES.get(dec, ""))
        lines.append(f"| {dec} | {hx} | `{name}` | {note} |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} flags)")


if __name__ == "__main__":
    main()
