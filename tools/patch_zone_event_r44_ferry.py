#!/usr/bin/env python3
"""Add Route 44 → Blackthorn ferry hiker + Piloswine to zone_event member 043."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

SPRITE_MOUNT_2 = 333
SPRITE_STATIC_PILOSWINE = 1051
MOVEMENT_STAND = 15
TYPE_NPC = 0
FLAG_NOTHING = 0

FERRY_SCRIPT_ID = 5
FERRY_OBJECT_ID = 16
PILOSWINE_OBJECT_ID = 17
FACING_NORTH = 0

FERRY_X = 627
FERRY_Z = 170
PILOSWINE_X = 626
PILOSWINE_Z = 170


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

    ferry_ids = {FERRY_OBJECT_ID, PILOSWINE_OBJECT_ID}
    kept = [obj for obj in objects if object_id(obj) not in ferry_ids]
    removed = len(objects) - len(kept)
    if removed:
        print(f"removed {removed} existing Route 44 ferry object(s)")

    new_objects = kept + [
        pack_object(
            FERRY_OBJECT_ID,
            SPRITE_MOUNT_2,
            FERRY_SCRIPT_ID,
            FACING_NORTH,
            FERRY_X,
            FERRY_Z,
        ),
        pack_object(
            PILOSWINE_OBJECT_ID,
            SPRITE_STATIC_PILOSWINE,
            0,
            FACING_NORTH,
            PILOSWINE_X,
            PILOSWINE_Z,
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
        print(f"usage: {argv[0]} <build/a032/2_043>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    if target.name != "2_043":
        print(f"warning: expected zone_event 2_043 (Route 44 matrix), got {target.name}", file=sys.stderr)

    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(
        f"installed Route 44 ferry at ({FERRY_X}, {FERRY_Z}) + "
        f"Piloswine at ({PILOSWINE_X}, {PILOSWINE_Z}) in {target}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
