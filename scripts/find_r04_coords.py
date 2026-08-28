#!/usr/bin/env python3
"""Find zone_event members whose objects use Route 4 world coordinates."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def objects(data: bytes) -> list[tuple[int, int, int, int]]:
    pos = 0
    bg_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg_count * 20
    obj_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(obj_count):
        vals = struct.unpack_from("<14H", data, pos)
        out.append((vals[0], vals[5], vals[12], vals[13]))
        pos += 32
    return out


def main() -> None:
    for path in sorted((ROOT / "build/a032_vanilla").glob("2_*")):
        mid = int(path.name.split("_", 1)[1])
        for oid, scr, x, z in objects(path.read_bytes()):
            if 1180 <= x <= 1260 and 100 <= z <= 130:
                print(f"2_{mid:03d} obj id={oid} script={scr} ({x},{z})")


if __name__ == "__main__":
    main()
