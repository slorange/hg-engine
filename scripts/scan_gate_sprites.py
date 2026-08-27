#!/usr/bin/env python3
"""Scan zone_event for Route 32 north-gate NPCs and duplicates."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VANILLA = ROOT / "build/a032_vanilla"
PATCHED = ROOT / "build/a032"


def parse(data: bytes) -> tuple[list[list[int]], list[list[int]]]:
    if len(data) < 8:
        return [], []
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    if pos + 4 > len(data):
        return [], []
    ob = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    objs: list[list[int]] = []
    for _ in range(ob):
        if pos + 32 > len(data):
            break
        objs.append(list(struct.unpack_from("<14H", data, pos)))
        pos += 32
    pos += 4
    wa = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + wa * 12
    if pos + 4 > len(data):
        return objs, []
    co = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    coords: list[list[int]] = []
    for _ in range(co):
        if pos + 16 > len(data):
            break
        coords.append(list(struct.unpack_from("<8H", data, pos)))
        pos += 16
    return objs, coords


def scan(root: Path, label: str) -> None:
    print(f"\n=== {label} ===")
    print("sprite 351:")
    for p in sorted(root.glob("2_*")):
        objs, coords = parse(p.read_bytes())
        for f in objs:
            if f[1] == 351:
                print(
                    f"  {p.name} id={f[0]} scr={f[5]} flag={f[4]} "
                    f"@({f[12]},{f[13]})"
                )
        for c in coords:
            if c[0] in (2, 3) and 265 <= c[1] <= 285 and 160 <= c[2] <= 220:
                print(f"  {p.name} coord {c}")

    print("sprite 328 north gate (z 160-220, x 250-290):")
    for p in sorted(root.glob("2_*")):
        objs, _ = parse(p.read_bytes())
        for f in objs:
            if f[1] == 328 and 160 <= f[13] <= 220 and 250 <= f[12] <= 290:
                print(
                    f"  {p.name} id={f[0]} scr={f[5]} flag={f[4]} "
                    f"@({f[12]},{f[13]})"
                )


def main() -> None:
    scan(VANILLA, "VANILLA")
    if PATCHED.is_dir():
        scan(PATCHED, "PATCHED")


if __name__ == "__main__":
    main()
