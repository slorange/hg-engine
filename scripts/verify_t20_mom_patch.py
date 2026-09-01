#!/usr/bin/env python3
"""Verify Mom openworld patches in scr_seq init header 618 and member 845."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from patch_scr_seq_t20_mom import extract_scripts  # noqa: E402

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
    if body.count(GIVE_ITEM) < 4:
        raise SystemExit("script 0 missing giveitem_no_check grants (expect ticket/pass/apricorn/HM02)")
    if UPGRADE_POKEGEAR not in body:
        raise SystemExit("script 0 missing UpgradePokegear(1)")
    if TOWN_MAP_SCREEN in body:
        raise SystemExit("script 0 must not call town_map/WorldMapScreen (cutscene softlock)")
    if REGISTER_GEAR_MOM not in body:
        raise SystemExit("script 0 missing register_gear_number Mom")
    if REGISTER_GEAR_ELM not in body:
        raise SystemExit("script 0 missing register_gear_number Elm")
    if REGISTER_GEAR_OAK not in body:
        raise SystemExit("script 0 missing register_gear_number Oak")
    if HM02_ITEM_ID not in body:
        raise SystemExit("script 0 missing ITEM_HM02 (421) grant")

    print("ok: vanilla init header + script 0 open-world grants (pokegear, town map, phones, HM02)")


if __name__ == "__main__":
    main()
