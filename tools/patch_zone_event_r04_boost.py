#!/usr/bin/env python3
"""Add Route 4 paid ledge-boost NPC to zone_event member 009.

See documentation/HACK-NOTES.md § "Route 4 ledge boost".
Tune NPC_X/NPC_Z and LAND_X/LAND_Z after in-game positioning.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# scr_seq slot 1 → scriptId 2 (tools/patch_scr_seq_r04_boost.py).
BOOST_SCRIPT_ID = 2
BOOST_OBJECT_ID = 4

SPRITE_MOUNT_2 = 333  # pret SPRITE_MOUNT_2 — hiker / mountaineer
MOVEMENT_STAND = 0
TYPE_NPC = 0
FLAG_NOTHING = 0

# Cerulean-side ledge: Sharon (1250,112) is 20 west + 6 north of this tile.
NPC_X = 1270
NPC_Z = 118
LAND_X = NPC_X
LAND_Z = NPC_Z - 2
NPC_FACING = 1  # DIR_SOUTH — pret: 0=north, 1=south, 2=west, 3=east

BOOST_NPC = (BOOST_OBJECT_ID, BOOST_SCRIPT_ID, NPC_FACING, NPC_X, NPC_Z)


def pack_object(obj_id: int, script_id: int, facing: int, x: int, z: int) -> bytes:
    return struct.pack(
        "<14HI",
        obj_id,
        SPRITE_MOUNT_2,
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

    kept = [obj for obj in objects if object_id(obj) < BOOST_OBJECT_ID]
    removed = len(objects) - len(kept)
    if removed:
        print(f"removed {removed} existing boost object(s)")

    new_objects = kept + [pack_object(*BOOST_NPC)]

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
        print(f"usage: {argv[0]} <build/a032/2_009>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    if target.name != "2_009":
        print(f"warning: expected zone_event 2_009 (Route 4), got {target.name}", file=sys.stderr)

    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(
        f"installed Route 4 boost NPC id={BOOST_OBJECT_ID} at ({NPC_X},{NPC_Z}) "
        f"-> warp ({LAND_X},{LAND_Z}) scriptId={BOOST_SCRIPT_ID} in {target}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
