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
    if body.count(GIVE_ITEM) < 3:
        raise SystemExit("script 0 missing giveitem_no_check grants")
    if body[-8:] != b"\x00" * 8:
        raise SystemExit(f"script 0 tail not zero-padded ({body[-8:].hex()})")

    print("ok: vanilla init header + script 0 early setvar + inline grants")


if __name__ == "__main__":
    main()
