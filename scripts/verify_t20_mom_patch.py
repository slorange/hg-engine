#!/usr/bin/env python3
"""Verify Mom openworld patches in scr_seq init header 618 and member 845."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from patch_scr_seq_t20_mom import extract_scripts, config_flag  # noqa: E402

GIVE_ITEM = bytes.fromhex("f107")
EARLY_SETVAR = bytes.fromhex("290006410100")
COMPARE_SCENE = bytes.fromhex("110006410000")
VANILLA_ONFRAME_LOOP = bytes.fromhex("064100000100")
UPGRADE_POKEGEAR = bytes.fromhex("910001")  # UpgradePokegear 1
TOWN_MAP_SCREEN = bytes.fromhex("9d00")  # WorldMapScreen — must NOT appear in script 0
REGISTER_GEAR_MOM = bytes.fromhex("920000")
REGISTER_GEAR_ELM = bytes.fromhex("920001")
REGISTER_GEAR_OAK = bytes.fromhex("920002")
HM02_ITEM_ID = bytes.fromhex("a501")  # ITEM_HM02 = 421
GIVE_MON = bytes.fromhex("8900")  # give_mon (cmd 137)
SHOW_LIST = bytes.fromhex("4700")  # ShowList (cmd 71)
ADD_LIST_OPTION = bytes.fromhex("4600")  # AddListOption (cmd 70)
NPC_MSG_CITY = bytes.fromhex("2d0002")  # npc_msg 2 (city prompt)
NPC_MSG_STARTER = bytes.fromhex("2d0006")  # npc_msg 6 (starter prompt)
COPYVAR_START_CITY = bytes.fromhex("2a0031400c80")  # copyvar VAR_PLAYER_START_CITY, VAR_SPECIAL_RESULT
SET_DYNAMIC_WARP = bytes.fromhex("f000")  # set_dynamic_warp (cmd 240)
MIN_CITY_LIST_OPTIONS = 3
MIN_STARTER_LIST_OPTIONS = 12


def has_town_map_call(body: bytes) -> bool:
    """Detect WorldMapScreen (cmd 157 / 0x009d), not the same bytes in goto offsets."""
    i = 0
    while True:
        i = body.find(TOWN_MAP_SCREEN, i)
        if i < 0:
            return False
        # goto_if_eq embeds a 32-bit offset after 0x001c 0x0001
        if i >= 3 and body[i - 3 : i] == b"\x1c\x00\x01":
            i += 2
            continue
        return True


def main() -> None:
    vanilla_hdr_path = ROOT / "build/a012_vanilla/2_618"
    hdr_path = ROOT / "build/a012/2_618"
    if not vanilla_hdr_path.is_file():
        raise SystemExit("missing build/a012_vanilla/2_618; run extract_scr_seq_vanilla first")

    vanilla_hdr = vanilla_hdr_path.read_bytes()
    hdr = hdr_path.read_bytes()
    if hdr != vanilla_hdr:
        raise SystemExit(f"init header 618 changed ({hdr.hex()}); keep vanilla OnFrame layout")
    if VANILLA_ONFRAME_LOOP not in hdr:
        raise SystemExit("init header 618 missing expected OnFrame var==0 row")

    body = extract_scripts((ROOT / "build/a012/2_845").read_bytes())[0]

    if not body.startswith(bytes.fromhex("61026000")):
        raise SystemExit("script 0 missing scrcmd_609 + lockall")
    if COMPARE_SCENE not in body[:20]:
        raise SystemExit("script 0 missing early scene compare")
    if EARLY_SETVAR not in body[:32]:
        raise SystemExit("script 0 missing early setvar (OnFrame loop guard)")
    min_give_items = 4 if config_flag("OPENWORLD_TESTING_GRANTS") else 3
    if body.count(GIVE_ITEM) < min_give_items:
        raise SystemExit(
            f"script 0 missing giveitem_no_check grants (expect at least {min_give_items})"
        )
    if UPGRADE_POKEGEAR not in body:
        raise SystemExit("script 0 missing UpgradePokegear(1)")
    if has_town_map_call(body):
        raise SystemExit("script 0 must not call town_map/WorldMapScreen (cutscene softlock)")
    if REGISTER_GEAR_MOM not in body:
        raise SystemExit("script 0 missing register_gear_number Mom")
    if REGISTER_GEAR_ELM not in body:
        raise SystemExit("script 0 missing register_gear_number Elm")
    if REGISTER_GEAR_OAK not in body:
        raise SystemExit("script 0 missing register_gear_number Oak")
    if GIVE_MON not in body:
        raise SystemExit("script 0 missing give_mon (open-world starter pick)")
    if NPC_MSG_CITY not in body:
        raise SystemExit("script 0 missing npc_msg 2 (city prompt)")
    if COPYVAR_START_CITY not in body:
        raise SystemExit("script 0 missing copyvar VAR_PLAYER_START_CITY")
    if SET_DYNAMIC_WARP not in body:
        raise SystemExit("script 0 missing set_dynamic_warp after city pick")
    if body.count(SHOW_LIST) < 2:
        raise SystemExit("script 0 missing ShowList (city + starter menus)")
    if body.count(ADD_LIST_OPTION) < MIN_CITY_LIST_OPTIONS + MIN_STARTER_LIST_OPTIONS:
        raise SystemExit(
            f"script 0 missing AddListOption entries "
            f"(expect at least {MIN_CITY_LIST_OPTIONS + MIN_STARTER_LIST_OPTIONS})"
        )
    if NPC_MSG_STARTER not in body:
        raise SystemExit("script 0 missing npc_msg 6 (starter prompt)")
    if config_flag("OPENWORLD_TESTING_GRANTS"):
        if HM02_ITEM_ID not in body:
            raise SystemExit("script 0 missing ITEM_HM02 (421) grant (OPENWORLD_TESTING_GRANTS)")
    elif HM02_ITEM_ID in body:
        raise SystemExit("script 0 must not grant HM02 when OPENWORLD_TESTING_GRANTS is off")

    print("ok: vanilla init header + script 0 open-world grants (pokegear, phones, key items)")


if __name__ == "__main__":
    main()
