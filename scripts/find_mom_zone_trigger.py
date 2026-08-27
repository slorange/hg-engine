#!/usr/bin/env python3
"""Find zone_event coord triggers for player house Mom cutscene."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE_DIR = ROOT / "build/a032"


def parse_coords(data: bytes) -> list[list[int]]:
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
    objn = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + objn * 32 + 4
    wn = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + wn * 12 + 4
    cn = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    coords: list[list[int]] = []
    for _ in range(cn):
        coords.append(list(struct.unpack_from("<8H", data, pos)))
        pos += 16
    return coords


def main() -> None:
    for path in sorted(ZONE_DIR.glob("2_*")):
        data = path.read_bytes()
        if len(data) < 32:
            continue
        try:
            coords = parse_coords(data)
        except struct.error:
            continue
        for c in coords:
            script_id, x, z, w, h, y, var, val, vx, vy = c
            if script_id in (1, 65535) or var in (0x4106, 0x4000, 0x4001):
                if script_id <= 10 or var == 0x4106:
                    print(
                        f"{path.name}: script={script_id} rect=({x},{z},{w},{h}) "
                        f"var={var:#x} val={val} elev=({y},{vy})"
                    )


if __name__ == "__main__":
    main()
