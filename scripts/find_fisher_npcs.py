#!/usr/bin/env python3
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def objects(data: bytes) -> list[tuple[int, int, int, int, int]]:
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    ob = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(ob):
        v = struct.unpack_from("<14H", data, pos)
        out.append((v[0], v[1], v[5], v[12], v[13]))
        pos += 32
    return out


def main() -> None:
    for path in sorted((ROOT / "build/a032_vanilla").glob("2_*")):
        for row in objects(path.read_bytes()):
            if row[1] == 347:
                mid = int(path.name.split("_", 1)[1])
                print(f"2_{mid:03d} id={row[0]} script={row[2]} sprite=347 at ({row[3]},{row[4]})")


if __name__ == "__main__":
    main()
