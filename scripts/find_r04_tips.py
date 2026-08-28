#!/usr/bin/env python3
"""Find zone_event member with Route 4 trainer-tips sign at (1197,114)."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bgs(data: bytes) -> list[tuple[int, int, int, int]]:
    pos = 0
    bg_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(bg_count):
        script, typ = struct.unpack_from("<HH", data, pos)
        x, z, y, d = struct.unpack_from("<IIII", data, pos + 4)
        out.append((script, typ, x, z))
        pos += 20
    return out


def main() -> None:
    for path in sorted((ROOT / "build/a032_vanilla").glob("2_*")):
        for script, typ, x, z in bgs(path.read_bytes()):
            if (x, z) == (1197, 114) or (script == 1 and typ == 1 and 1190 <= x <= 1200):
                mid = int(path.name.split("_", 1)[1])
                print(f"2_{mid:03d}: tips bg script={script} ({x},{z})")


if __name__ == "__main__":
    main()
