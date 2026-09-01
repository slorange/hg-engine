#!/usr/bin/env python3
"""Bedroom scr_seq 846: leave vanilla (starter pick lives in Mom script 845)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
MEMBER_INDEX = 846
HDR_INDEX = 619
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
VANILLA_HDR = ROOT / f"build/a012_vanilla/2_{HDR_INDEX:03d}"


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    hdr_target = target.parent / f"2_{HDR_INDEX:03d}"
    if not VANILLA_MEMBER.is_file() or not VANILLA_HDR.is_file():
        raise FileNotFoundError("missing vanilla bedroom scr_seq or header; extract first")

    target.write_bytes(VANILLA_MEMBER.read_bytes())
    hdr_target.write_bytes(VANILLA_HDR.read_bytes())
    note = "starter in Mom 845" if openworld_enabled() else "OPENWORLD off"
    print(f"left vanilla bedroom scr_seq in {target} ({note})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
