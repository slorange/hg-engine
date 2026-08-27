#!/usr/bin/env python3
"""Scan vanilla zone_event for Route 32 / Violet gate NPCs."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VANILLA = ROOT / "build/a032_vanilla"


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
    if pos + 4 > len(data):
        return objs, []
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


def main() -> None:
    print("=== sprite 328 / gate coords near Violet ===")
    for path in sorted(VANILLA.glob("2_*")):
        objs, coords = parse(path.read_bytes())
        for f in objs:
            if f[1] == 328 and 250 <= f[12] <= 290 and 160 <= f[13] <= 215:
                print(
                    f"obj {path.name}: id={f[0]} spr={f[1]} flag={f[4]} "
                    f"scr={f[5]} x={f[12]} z={f[13]}"
                )
            if f[1] == 1035 and 255 <= f[12] <= 285 and 165 <= f[13] <= 185:
                print(
                    f"barrier {path.name}: id={f[0]} spr={f[1]} flag={f[4]} "
                    f"scr={f[5]} x={f[12]} z={f[13]}"
                )
        for c in coords:
            if 265 <= c[1] <= 285 and 165 <= c[2] <= 180:
                print(f"coord {path.name}: {c}")


if __name__ == "__main__":
    main()
