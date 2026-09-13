#!/usr/bin/env python3
"""Violet Gym (zone_event 365): remove Sprout Tower gate NPC blocking the elevator."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMBER = "2_365"

# obj1 in vanilla: id=1, sprite=324, script=3 — blocks elevator until Sprout Tower.
GATE_OBJECT_ID = 1
GATE_SCRIPT_ID = 3


def parse_zone_event(data: bytes) -> tuple[list[bytes], list[bytes], bytes, list[bytes]]:
    pos = 0
    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    bgs = [data[pos + i * 20 : pos + (i + 1) * 20] for i in range(bg_count)]
    pos += bg_count * 20

    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    objects = [data[pos + i * 32 : pos + (i + 1) * 32] for i in range(obj_count)]
    pos += obj_count * 32

    (warp_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    warps = data[pos : pos + warp_count * 12]
    pos += warp_count * 12

    (coord_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    coords = [data[pos + i * 16 : pos + (i + 1) * 16] for i in range(coord_count)]
    pos += coord_count * 16

    if pos != len(data):
        raise ValueError(f"trailing zone_event bytes: parsed {pos}, file {len(data)}")
    return bgs, objects, warps, coords


def pack_zone_event(
    bgs: list[bytes], objects: list[bytes], warps: bytes, coords: list[bytes]
) -> bytes:
    out = bytearray()
    out.extend(struct.pack("<I", len(bgs)))
    out.extend(b"".join(bgs))
    out.extend(struct.pack("<I", len(objects)))
    out.extend(b"".join(objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(coords)))
    out.extend(b"".join(coords))
    return bytes(out)


def patch_member(data: bytearray) -> int:
    bgs, objects, warps, coords = parse_zone_event(data)
    kept: list[bytes] = []
    removed = 0
    for obj in objects:
        fields = struct.unpack_from("<14H", obj)
        if fields[0] == GATE_OBJECT_ID and fields[5] == GATE_SCRIPT_ID:
            removed += 1
            continue
        kept.append(obj)
    if removed == 0:
        raise ValueError("Violet Gym elevator gate NPC (obj 1 script 3) not found")
    rebuilt = pack_zone_event(bgs, kept, warps, coords)
    data[:] = rebuilt
    return removed


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/{MEMBER}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    data = bytearray(target.read_bytes())
    removed = patch_member(data)
    target.write_bytes(data)
    print(
        f"removed Violet Gym elevator gate NPC from {target} "
        f"({removed} object(s), {len(data)} bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
