#!/usr/bin/env python3
"""Add Route 42 ferry NPCs to zone_event member 041.

See documentation/HACK-NOTES.md § "Paid ferry / local bypass NPCs".
Copy this file when adding ferry object NPCs on other maps.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPRITE_FISHING_2 = 347
MOVEMENT_STAND = 15
TYPE_NPC = 0
FLAG_NOTHING = 0

# scriptId = scr_seq slot + 1 (see tools/patch_scr_seq_r42_ferry.py).
WEST_SCRIPT_ID = 7
EAST_SCRIPT_ID = 8

FERRY_NPCS = [
    # id, scriptId, facing, x, z
    (13, WEST_SCRIPT_ID, 3, 429, 177),  # west shore, east of sign at 427
    (14, EAST_SCRIPT_ID, 2, 502, 172),  # east shore, west of sign at 504
]


def pack_object(
    obj_id: int,
    script_id: int,
    facing: int,
    x: int,
    z: int,
) -> bytes:
    return struct.pack(
        "<14HI",
        obj_id,
        SPRITE_FISHING_2,
        MOVEMENT_STAND,
        TYPE_NPC,
        FLAG_NOTHING,
        script_id,
        facing,
        0,
        0,
        0,
        0,
        0,
        x,
        z,
        0,
    )


def read_u16s(data: bytes, pos: int, count: int) -> tuple[list[int], int]:
    vals = list(struct.unpack_from(f"<{count}H", data, pos))
    return vals, pos + count * 2


def parse_zone_event(data: bytes) -> tuple[bytes, list[bytes], bytes, bytes]:
    pos = 0

    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    bgs = data[pos : pos + bg_count * 20]
    pos += bg_count * 20

    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    objects: list[bytes] = []
    for _ in range(obj_count):
        objects.append(data[pos : pos + 32])
        pos += 32

    (warp_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    warps = data[pos : pos + warp_count * 12]
    pos += warp_count * 12

    (coord_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    coords = data[pos : pos + coord_count * 16]
    pos += coord_count * 16

    if pos != len(data):
        raise ValueError(f"unexpected trailing data: parsed {pos}, file {len(data)}")

    return bgs, objects, warps, coords


def object_id(obj: bytes) -> int:
    return struct.unpack_from("<H", obj, 0)[0]


def patch_member(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    kept = [obj for obj in objects if object_id(obj) < 13]
    removed = len(objects) - len(kept)
    if removed:
        print(f"removed {removed} existing ferry object(s)")

    new_objects = kept + [pack_object(*npc) for npc in FERRY_NPCS]

    out = bytearray()
    out.extend(struct.pack("<I", len(bgs) // 20))
    out.extend(bgs)
    out.extend(struct.pack("<I", len(new_objects)))
    out.extend(b"".join(new_objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(coords) // 16))
    out.extend(coords)

    data[:] = out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_041>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(f"installed {len(FERRY_NPCS)} ferry NPCs in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
