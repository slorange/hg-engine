#!/usr/bin/env python3
"""Patch New Bark player house init header 618: OnTransition once, not OnFrame loop."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
MEMBER_INDEX = 618
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"

# INIT_SCRIPT_ON_TRANSITION=2, script 1 (scr slot 0); frame table: var 3 -> script 7 only.
PATCHED_HDR = bytes(
    [
        0x02,
        0x01,
        0x00,
        0x00,
        0x00,  # OnTransition -> Mom cutscene (scriptId 1)
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,  # OnFrameTable @ byte 10
        0x06,
        0x41,
        0x03,
        0x00,
        0x07,
        0x00,  # scene==3 -> script 7 (post-E4 return)
        0x00,
        0x00,  # InitScriptFrameTableEnd
        0x00,  # InitScriptEntryEnd
        0x00,  # InitScriptEnd
    ]
)


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not VANILLA_MEMBER.is_file():
        raise FileNotFoundError(f"missing vanilla header {VANILLA_MEMBER}")

    vanilla = VANILLA_MEMBER.read_bytes()
    if not openworld_enabled():
        target.write_bytes(vanilla)
        print(f"OPENWORLD_STARTING_ITEMS disabled; left vanilla header in {target}")
        return 0

    if vanilla == PATCHED_HDR:
        target.write_bytes(vanilla)
        print(f"header already patched in {target}")
        return 0

    target.write_bytes(PATCHED_HDR)
    print(f"patched Mom init header in {target} (OnTransition + no OnFrame var==0 loop)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
