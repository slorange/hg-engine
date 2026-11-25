#!/usr/bin/env python3
"""Skip Azalea's rival battle and Kurt's welcome scene in open-world mode."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path
from append_scr_seq_script import script_offset

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
# Coord script: vanilla setflag 415 @83 blocks Slowpoke Well; flip to clearflag 415.
WELL_GUARD_SETFLAG_OFFSET = 83

SETFLAG_415 = struct.pack("<HH", 30, 415)
CLEARFLAG_415 = struct.pack("<HH", 31, 415)


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def patch_entry(data: bytearray, slot: int, prefix: str, replacement: bytes) -> None:
    start = script_offset(data, slot)
    expected = bytes.fromhex(prefix)
    if data[start:start + len(expected)] != expected:
        raise ValueError(f"Unexpected Azalea script opening for slot {slot}")
    data[start:start + len(replacement)] = replacement


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <town scr_seq 866> <Kurt's house scr_seq 874>", file=sys.stderr)
        return 1

    if not openworld_enabled():
        return 0

    town_path, house_path = map(Path, argv[1:])
    data = bytearray(town_path.read_bytes())
    house = bytearray(house_path.read_bytes())
    if data[WELL_GUARD_SETFLAG_OFFSET : WELL_GUARD_SETFLAG_OFFSET + 4] != SETFLAG_415:
        got = data[WELL_GUARD_SETFLAG_OFFSET : WELL_GUARD_SETFLAG_OFFSET + 4].hex()
        raise ValueError(f"{town_path}: expected setflag 415 @ {WELL_GUARD_SETFLAG_OFFSET}, got {got}")

    data[WELL_GUARD_SETFLAG_OFFSET : WELL_GUARD_SETFLAG_OFFSET + 4] = CLEARFLAG_415
    # Advance only the town scene. The rival's original script also arms puzzle sticks.
    patch_entry(data, 2, "61 02 60 00 54 00", struct.pack("<4H", 41, 0x4075, 2, 2))
    # Mark the welcome scene complete and give Kurt only his retired-crafter line.
    patch_entry(house, 5, "61 02 60 00 29 00 80 40", struct.pack("<4H", 41, 0x4080, 4, 2))
    retired_dialogue = bytes.fromhex("49 00 dc 05 60 00 68 00 2d 00 03 32 00 35 00 61 00 02 00")
    patch_entry(house, 1, "20 00 7c 00 1c 00", retired_dialogue)

    # Keep the granddaughter's post-story dialogue and bypass the number offer.
    granddaughter = script_offset(house, 2)
    branch = granddaughter + 8  # After PlaySE, LockAll, and FacePlayer.
    if house[branch:branch + 4] != bytes.fromhex("20 00 77 00"):
        raise ValueError("Unexpected opening flag check in Kurt's granddaughter's script")
    end = script_offset(house, 3)
    post_story = house.index(bytes.fromhex("20 00 64 09 1c 00 01"), branch, end)
    struct.pack_into("<Hi", house, branch, 22, post_story - (branch + 6))

    town_path.write_bytes(data)
    house_path.write_bytes(house)
    print("Skipped Azalea's rival fight and Kurt's house cutscene")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
