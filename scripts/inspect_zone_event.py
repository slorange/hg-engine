#!/usr/bin/env python3
"""Print zone_event member layout."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


def read_u16s(data: bytes, pos: int, count: int) -> tuple[list[int], int]:
    vals = list(struct.unpack_from(f"<{count}H", data, pos))
    return vals, pos + count * 2


def main(argv: list[str]) -> int:
    data = Path(argv[1]).read_bytes()
    pos = 0

    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    print(f"bgs: {bg_count}")
    for i in range(bg_count):
        vals, pos = read_u16s(data, pos, 2)
        rest = struct.unpack_from("<IIII", data, pos)
        pos += 16
        print(f"  bg {i}: script={vals[0]} type={vals[1]} x={rest[0]} z={rest[1]} y={rest[2]} dir={rest[3]}")

    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    print(f"objects: {obj_count}")
    for i in range(obj_count):
        vals, pos = read_u16s(data, pos, 14)
        (y,) = struct.unpack_from("<I", data, pos)
        pos += 4
        print(
            f"  obj {i}: id={vals[0]} sprite={vals[1]} script={vals[5]} "
            f"x={vals[12]} z={vals[13]} y={y}"
        )

    (warp_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    print(f"warps: {warp_count}")
    pos += warp_count * 12

    (coord_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    print(f"coords: {coord_count}")
    for i in range(coord_count):
        vals, pos = read_u16s(data, pos, 8)
        print(f"  coord {i}: script={vals[0]} x={vals[1]} z={vals[2]} w={vals[3]} h={vals[4]} var={vals[7]} val={vals[6]}")

    print(f"total size: {len(data)}, parsed to: {pos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
