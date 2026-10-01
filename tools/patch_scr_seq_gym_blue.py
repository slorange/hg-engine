#!/usr/bin/env python3
"""Viridian Gym Blue: open-world without 7 Kanto badges.

- Slot 2 (OnLoad): keep vanilla init; force show Blue (setflag 758 -> clearflag 758).
- Slot 3 (coord / upper floor): skip badge lecture softlock; set FLAG_UNK_13A (314).
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

from patch_scr_seq_gym_falkner import ROM, extract_scripts, patch_script_slot

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
ARMIPS = ROOT / "tools/armips"
MEMBER_INDEX = 743
SLOT_ONLOAD = 2
SLOT_COORD = 3
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
PYTHON = ROOT / ".venv/bin/python"
SLOT3_ASM = ROOT / "armips/scr_seq/scr_seq_blue_gym_slot3.s"
SLOT3_BIN = ROOT / "build/blue_gym_slot3.bin"
FLAG_HIDE_VIRIDIAN_GYM_BLUE = 758


def openworld_story_skip() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def load_vanilla_member() -> bytearray:
    if VANILLA_MEMBER.is_file():
        return bytearray(VANILLA_MEMBER.read_bytes())
    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and {VANILLA_MEMBER}")
    vanilla_narc = ROOT / "build/vanilla_rom_root/a/0/1/2"
    if not vanilla_narc.is_file():
        raise FileNotFoundError(f"extract vanilla scr_seq first ({vanilla_narc})")
    py = str(PYTHON if PYTHON.is_file() else sys.executable)
    subprocess.check_call(
        [
            py,
            str(ROOT / "tools/narcpy.py"),
            "extract",
            str(vanilla_narc),
            "-o",
            str(ROOT / "build/a012_vanilla"),
            "-nf",
        ],
        cwd=ROOT,
    )
    if not VANILLA_MEMBER.is_file():
        raise FileNotFoundError(f"missing vanilla member {VANILLA_MEMBER}")
    return bytearray(VANILLA_MEMBER.read_bytes())


def patch_onload_show_blue(slot: bytearray) -> int:
    set_hide = struct.pack("<HH", 30, FLAG_HIDE_VIRIDIAN_GYM_BLUE)
    clr_hide = struct.pack("<HH", 31, FLAG_HIDE_VIRIDIAN_GYM_BLUE)
    count = slot.count(set_hide)
    if count == 0:
        raise ValueError("Viridian OnLoad: expected setflag 758 in slot 2")
    slot[:] = slot.replace(set_hide, clr_hide)
    return count


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX:03d}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    vanilla = load_vanilla_member()

    if not openworld_story_skip():
        target.write_bytes(vanilla)
        print(f"OPENWORLD_STORY_SKIP off; left vanilla scr_seq in {target}")
        return 0

    SLOT3_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(SLOT3_ASM)])
    slot3_blob = SLOT3_BIN.read_bytes()
    if not slot3_blob:
        raise ValueError(f"empty slot blob {SLOT3_BIN}")

    data = bytearray(vanilla)
    scripts = extract_scripts(data)
    onload = bytearray(scripts[SLOT_ONLOAD])
    n = patch_onload_show_blue(onload)
    patch_script_slot(data, SLOT_ONLOAD, bytes(onload))
    patch_script_slot(data, SLOT_COORD, slot3_blob)

    target.write_bytes(data)
    print(
        f"patched Viridian Gym in {target} ({len(data)} bytes): "
        f"OnLoad {n}x setflag758->clearflag758, coord slot {len(slot3_blob)}b"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
