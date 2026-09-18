#!/usr/bin/env python3
"""Add Route 40 → Cianwood ferry fisherman + Lapras to zone_event member 091."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

SPRITE_FISHING_2 = 347
SPRITE_STATIC_LAPRAS = 1023
MOVEMENT_STAND = 15
TYPE_NPC = 0
FLAG_NOTHING = 0

FERRY_SCRIPT_ID = 11
FERRY_OBJECT_ID = 7
LAPRAS_OBJECT_ID = 8
# Face south toward the beach (pret: DIR_SOUTH = 1).
FACING_SOUTH = 1

FERRY_X = 248
FERRY_Z = 277
LAPRAS_X = 248
LAPRAS_Z = 278


def pack_object(
    obj_id: int,
    sprite: int,
    script_id: int,
    facing: int,
    x: int,
    z: int,
) -> bytes:
    return struct.pack(
        "<14HI",
        obj_id,
        sprite,
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

    ferry_ids = {FERRY_OBJECT_ID, LAPRAS_OBJECT_ID}
    kept = [obj for obj in objects if object_id(obj) not in ferry_ids]
    removed = len(objects) - len(kept)
    if removed:
        print(f"removed {removed} existing Route 40 ferry object(s)")

    new_objects = kept + [
        pack_object(
            FERRY_OBJECT_ID,
            SPRITE_FISHING_2,
            FERRY_SCRIPT_ID,
            FACING_SOUTH,
            FERRY_X,
            FERRY_Z,
        ),
        pack_object(
            LAPRAS_OBJECT_ID,
            SPRITE_STATIC_LAPRAS,
            0,
            FACING_SOUTH,
            LAPRAS_X,
            LAPRAS_Z,
        ),
    ]

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
        print(f"usage: {argv[0]} <build/a032/2_091>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(
        f"installed Route 40 ferry at ({FERRY_X}, {FERRY_Z}) + Lapras at ({LAPRAS_X}, {LAPRAS_Z}) "
        f"in {target}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
