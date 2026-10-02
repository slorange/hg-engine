#!/usr/bin/env python3
"""Olivine City outdoors (scr_seq 911): disable gym-area story coord script.

Vanilla coord script 2 @ zone_event 074 (272, 239) runs the Radio Tower / Elm
phone beat when VAR_UNK_4078 is 0. Hiding the rival NPC is not enough.

See documentation/HACK-NOTES.md § Olivine gym story skip.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
GATE_NOP_ASM = ROOT / "armips/scr_seq/scr_seq_r32_gate_nop_patch.s"
GATE_NOP_BIN = ROOT / "build/r32_gate_nop_patch.bin"

# scr_seq 911 slot 2 entry (zone_event coord scriptId 2).
GYM_STORY_SCRIPT_OFFSET = 60
GYM_STORY_SCRIPT_PREFIX = bytes([0x29, 0x00, 0x77, 0x40, 0x02, 0x00])


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_911>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    GATE_NOP_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(GATE_NOP_ASM)])
    gate_nop = GATE_NOP_BIN.read_bytes()

    data = bytearray(target.read_bytes())
    if data[GYM_STORY_SCRIPT_OFFSET : GYM_STORY_SCRIPT_OFFSET + len(GYM_STORY_SCRIPT_PREFIX)] != (
        GYM_STORY_SCRIPT_PREFIX
    ):
        if data[GYM_STORY_SCRIPT_OFFSET : GYM_STORY_SCRIPT_OFFSET + len(gate_nop)] == gate_nop:
            print(f"Olivine gym story script already neutralized in {target}")
            return 0
        raise ValueError(
            f"unexpected bytes @ {GYM_STORY_SCRIPT_OFFSET} in {target.name} "
            f"(expected vanilla gym coord script prefix)"
        )

    data[GYM_STORY_SCRIPT_OFFSET : GYM_STORY_SCRIPT_OFFSET + len(gate_nop)] = gate_nop
    target.write_bytes(data)
    print(f"patched Olivine gym story coord script @{GYM_STORY_SCRIPT_OFFSET} in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
