#!/usr/bin/env python3
"""Azalea Town scr_seq member 866: open-world well + rival script fixes."""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
CONFIG = ROOT / "include/config.h"
GATE_NOP_ASM = ROOT / "armips/scr_seq/scr_seq_t23_gate_nop_patch.s"
GATE_NOP_BIN = ROOT / "build/t23_gate_nop_patch.bin"

MEMBER = 866
# Coord script: vanilla setflag 415 @83 blocks Slowpoke Well; flip to clearflag 415.
WELL_GUARD_SETFLAG_OFFSET = 83
# Post–rocket rival staging (check FLAG_BEAT_AZALEA_ROCKETS then spawn battle).
RIVAL_SCRIPT_OFFSETS = (868, 903, 936)

SETFLAG_415 = struct.pack("<HH", 30, 415)
CLEARFLAG_415 = struct.pack("<HH", 31, 415)


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER:03d}>", file=sys.stderr)
        return 1

    if not openworld_enabled():
        return 0

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    if data[WELL_GUARD_SETFLAG_OFFSET : WELL_GUARD_SETFLAG_OFFSET + 4] != SETFLAG_415:
        got = data[WELL_GUARD_SETFLAG_OFFSET : WELL_GUARD_SETFLAG_OFFSET + 4].hex()
        raise ValueError(f"{target}: expected setflag 415 @ {WELL_GUARD_SETFLAG_OFFSET}, got {got}")

    data[WELL_GUARD_SETFLAG_OFFSET : WELL_GUARD_SETFLAG_OFFSET + 4] = CLEARFLAG_415
    print(f"patched well guard setflag→clearflag 415 @{WELL_GUARD_SETFLAG_OFFSET}")

    GATE_NOP_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(GATE_NOP_ASM)])
    gate_nop = GATE_NOP_BIN.read_bytes()

    for off in RIVAL_SCRIPT_OFFSETS:
        if off + len(gate_nop) > len(data):
            raise ValueError(f"rival script @{off} overflows file")
        data[off : off + len(gate_nop)] = gate_nop
        print(f"patched T23 rival script @{off}")

    target.write_bytes(data)
    print(f"patched Azalea open-world scr_seq in {target} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
