#!/usr/bin/env python3
"""Verify Magnet Train scr_seq patches (893 Goldenrod, 834 Saffron)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = (893, 834)
CHECKFLAG = 32
FLAG_RESTORED_POWER = 280


def find_power_checks(data: bytes) -> list[int]:
    pat = struct.pack("<HH", CHECKFLAG, FLAG_RESTORED_POWER)
    hits: list[int] = []
    i = 0
    while True:
        j = data.find(pat, i)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
    return hits


def main() -> int:
    ok = True
    for mid in MEMBERS:
        path = ROOT / f"build/a012/2_{mid}"
        if not path.is_file():
            print(f"FAIL: missing {path}")
            ok = False
            continue
        data = path.read_bytes()
        checks = find_power_checks(data)
        if checks:
            print(f"FAIL: 2_{mid} still has FLAG_RESTORED_POWER @ {[hex(c) for c in checks]}")
            ok = False
        else:
            print(f"OK: 2_{mid} ({len(data)} bytes) — no power-plant gate checks")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
