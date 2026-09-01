#!/usr/bin/env python3
"""Verify bedroom scr_seq 846 stays vanilla (starter is in Mom 845)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from patch_scr_seq_t20_bedroom import openworld_enabled  # noqa: E402

CHOOSE_STARTER = bytes.fromhex("a700")


def main() -> None:
    path = ROOT / "build/a012/2_846"
    hdr = ROOT / "build/a012/2_619"
    vanilla = ROOT / "build/a012_vanilla/2_846"
    vanilla_hdr = ROOT / "build/a012_vanilla/2_619"
    if path.read_bytes() != vanilla.read_bytes():
        raise SystemExit("bedroom scr_seq 846 must stay vanilla")
    if hdr.read_bytes() != vanilla_hdr.read_bytes():
        raise SystemExit("bedroom init header 619 must stay vanilla")
    if CHOOSE_STARTER in path.read_bytes():
        raise SystemExit("bedroom scr_seq must not contain choose_starter")
    if openworld_enabled():
        print("ok: bedroom vanilla; starter hook is Mom script 845")
    else:
        print("ok: OPENWORLD disabled; bedroom scr_seq vanilla")


if __name__ == "__main__":
    main()
