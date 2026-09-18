#!/usr/bin/env python3
"""Add Kanto coastal ferry fishermen + Lapras companions to Routes 19/20/21 and Pallet Town."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

SPRITE_FISHING_2 = 347
SPRITE_STATIC_LAPRAS = 1023
MOVEMENT_STAND = 15
TYPE_NPC = 0
FLAG_NOTHING = 0
FACING_SOUTH = 1

STOPS = [
    {
        "label": "Route 19 (Fuchsia)",
        "script_id": 7,
        "fisher_id": 18,
        "companion_id": 19,
        "fisher_x": 1203,
        "fisher_z": 469,
        "companion_x": 1203,
        "companion_z": 470,
    },
    {
        "label": "Route 20 (Seafoam)",
        "script_id": 3,
        "fisher_id": 12,
        "companion_id": 13,
        "fisher_x": 1125,
        "fisher_z": 504,
        "companion_x": 1124,
        "companion_z": 504,
    },
    {
        "label": "Pallet Town (south shore)",
        "script_id": 9,
        "fisher_id": 3,
        "companion_id": 4,
        "fisher_x": 1036,
        "fisher_z": 375,
        "companion_x": 1036,
        "companion_z": 376,
    },
    {
        "label": "Route 21 (Cinnabar)",
        "script_id": 3,
        "fisher_id": 16,
        "companion_id": 17,
        "fisher_x": 1030,
        "fisher_z": 503,
        "companion_x": 1030,
        "companion_z": 504,
    },
]

# Cinnabar beach: zone_event 054, scr_seq 815 (scriptId 6), msg bank 519.
CINNABAR_BEACH = {
    "label": "Cinnabar Island (beach)",
    "script_id": 6,
    "fisher_id": 3,
    "companion_id": 4,
    "fisher_x": 1030,
    "fisher_z": 503,
    "companion_x": 1030,
    "companion_z": 504,
}

MEMBER_STOPS = {
    "2_046": [STOPS[2]],
    "2_054": [CINNABAR_BEACH],
    "2_088": [STOPS[0]],
    "2_089": [STOPS[1]],
    "2_090": [],
}

RETired_OBJECT_IDS = {14, 15, 16, 17}


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


def patch_member(data: bytearray, stops: list[dict]) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    remove_ids = set()
    for stop in stops:
        remove_ids.add(stop["fisher_id"])
        remove_ids.add(stop["companion_id"])
    remove_ids.update(RETired_OBJECT_IDS)

    kept = [obj for obj in objects if object_id(obj) not in remove_ids]
    removed = len(objects) - len(kept)
    if removed:
        print(f"removed {removed} existing Kanto ferry object(s)")

    new_objects = list(kept)
    for stop in stops:
        new_objects.append(
            pack_object(
                stop["fisher_id"],
                SPRITE_FISHING_2,
                stop["script_id"],
                FACING_SOUTH,
                stop["fisher_x"],
                stop["fisher_z"],
            )
        )
        new_objects.append(
            pack_object(
                stop["companion_id"],
                SPRITE_STATIC_LAPRAS,
                0,
                FACING_SOUTH,
                stop["companion_x"],
                stop["companion_z"],
            )
        )
        print(
            f"installed {stop['label']} at ({stop['fisher_x']}, {stop['fisher_z']}) + "
            f"Lapras at ({stop['companion_x']}, {stop['companion_z']})"
        )

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
    if len(argv) != 6:
        print(
            f"usage: {argv[0]} <2_046> <2_054> <2_088> <2_089> <2_090>",
            file=sys.stderr,
        )
        return 1

    for arg in argv[1:]:
        target = Path(arg)
        key = target.name
        if key not in MEMBER_STOPS:
            print(f"unknown member {key}", file=sys.stderr)
            return 1
        if not target.is_file():
            print(f"missing {target}", file=sys.stderr)
            return 1
        data = bytearray(target.read_bytes())
        patch_member(data, MEMBER_STOPS[key])
        target.write_bytes(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
