#!/usr/bin/env python3
"""Add Apricorn tree objects beside the original trees."""

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from patch_zone_event_r32pc_rod_guru import parse_zone_event

TREE_SCRIPT = 2800
FIRST_NEW_SLOT = 31
OBJECT = struct.Struct("<14HI")

# Zone event member, original tree slot, and (right, up) tile offsets.
PLACEMENTS = (
    (30, 5, ((2, -1), (4, 0))),     # Route 29
    (45, 25, ((0, 1), (1, 0))),     # Route 46, yellow
    (44, 23, ((-2, 0), (-1, 0))),   # Route 45
    (31, 7, ((1, 0),)),             # Route 30, pink
    (32, 8, ((-1, 0),)),            # Route 31
    (70, 29, ((-1, 0),)),           # Violet City
    (34, 9, ((-1, 0),)),            # Route 33, left tree
    (71, 30, ((-2, 1),)),           # Azalea Town
    (36, 11, ((-1, 0),)),           # Route 35
    (37, 12, ((-1, 0),)),           # Route 36
    (38, 13, ((2, 1),)),            # Route 37, top-left tree
    (39, 16, ((0, -2),)),           # Route 38
    (40, 17, ((2, 0),)),            # Route 39
    (41, 18, ((-1, 0),)),           # Route 42, left tree
    (42, 21, ((1, 0),)),            # Route 43
    (43, 22, ((1, 0),)),            # Route 44
    (27, 4, ((-1, 0),)),            # Route 26
    (6, 0, ((1, 0),)),              # Route 1
    (370, 1, ((-1, 0),)),           # Route 2
    (48, 26, ((-1, -2), (1, -2))),  # Pewter City, blue
    (13, 2, ((-2, 0), (2, 0))),     # Route 8
    (16, 3, ((1, 0),)),             # Route 11
    (53, 28, ((2, 0), (4, 0))),     # Fuchsia City
)


def patch_trees(directory: Path) -> None:
    slot = FIRST_NEW_SLOT
    for member, anchor_slot, offsets in PLACEMENTS:
        path = directory / f"2_{member:03}"
        bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
        fields = [OBJECT.unpack(obj) for obj in objects]
        anchors = [obj for obj in fields if obj[5] == TREE_SCRIPT and obj[7] == anchor_slot]
        if len(anchors) != 1:
            raise ValueError(f"{path}: expected one tree at slot {anchor_slot}")
        anchor = anchors[0]
        occupied = {obj[12:14] for obj in fields}
        occupied.update(bg[2:4] for bg in struct.iter_unpack("<HHIIII", bgs))
        occupied.update(warp[:2] for warp in struct.iter_unpack("<HHHHI", warps))
        next_id = max(obj[0] for obj in fields) + 1

        for dx, up in offsets:
            # The ROM's world Z increases southward.
            x, z = anchor[12] + dx, anchor[13] - up
            if (x, z) in occupied:
                raise ValueError(f"{path}: tree target ({x}, {z}) is occupied")
            obj = list(anchor)
            obj[0], obj[7], obj[12], obj[13] = next_id, slot, x, z
            objects.append(OBJECT.pack(*obj))
            occupied.add((x, z))
            next_id += 1
            slot += 1

        path.write_bytes(
            struct.pack("<I", len(bgs) // 20) + bgs
            + struct.pack("<I", len(objects)) + b"".join(objects)
            + struct.pack("<I", len(warps) // 12) + warps
            + struct.pack("<I", len(coords) // 16) + coords
        )


if __name__ == "__main__":
    patch_trees(Path(sys.argv[1]))
