#!/usr/bin/env python3
"""Remove Cut trees blocking Vermilion / Celadon Gym access (Surge, Erika)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

# pret: 051_T06, 052_T07, 352_T07GYM0101
GYM_CUT_TREE_MEMBERS = (
    "2_051",  # Vermilion City — tree in front of Gym
    "2_052",  # Celadon City — tree blocking Gym approach
    "2_352",  # Celadon Gym — interior maze trees
)

SPRITE_TREE = 86
STD_FIELD_CUT = 10000


def parse_zone_event(data: bytes) -> tuple[list[list[int]], list[bytes], bytes, list[list[int]]]:
    pos = 0

    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    bgs: list[list[int]] = []
    for _ in range(bg_count):
        vals = list(struct.unpack_from("<10H", data, pos))
        pos += 20
        bgs.append(vals)

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
    coords: list[list[int]] = []
    for _ in range(coord_count):
        coords.append(list(struct.unpack_from("<8H", data, pos)))
        pos += 16

    if pos != len(data):
        raise ValueError(f"unexpected trailing data: parsed {pos}, file {len(data)}")

    return bgs, objects, warps, coords


def object_fields(obj: bytes) -> list[int]:
    return list(struct.unpack_from("<14H", obj))


def pack_object(fields: list[int], y: int) -> bytes:
    return struct.pack("<14HI", *fields, y)


def pack_bg(fields: list[int]) -> bytes:
    return struct.pack("<10H", *fields)


def is_cut_tree(fields: list[int]) -> bool:
    return fields[1] == SPRITE_TREE and fields[5] == STD_FIELD_CUT


def patch_member(data: bytearray) -> int:
    bgs, objects, warps, coords = parse_zone_event(data)

    removed = 0
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if is_cut_tree(fields):
            removed += 1
            print(
                f"  remove cut tree id={fields[0]} flag={fields[4]} "
                f"at ({fields[12]}, {fields[13]})"
            )
            continue
        new_objects.append(pack_object(fields, y))

    if removed == 0:
        raise ValueError("no cut tree objects matched (sprite 86, script 10000)")

    out = bytearray()
    out.extend(struct.pack("<I", len(bgs)))
    for bg in bgs:
        out.extend(pack_bg(bg))
    out.extend(struct.pack("<I", len(new_objects)))
    out.extend(b"".join(new_objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(coords)))
    for c in coords:
        out.extend(struct.pack("<8H", *c))

    data[:] = out
    print(f"  objects {len(objects)} -> {len(new_objects)} ({removed} cut tree(s) removed)")
    return removed


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} <build/a032/2_051> [<build/a032/2_052> ...]", file=sys.stderr)
        return 1

    zone_dir = Path(argv[1]).parent
    targets = [Path(p) for p in argv[1:]]
    if len(targets) == 1 and targets[0].name == "a032":
        targets = [zone_dir / member for member in GYM_CUT_TREE_MEMBERS]

    total = 0
    for target in targets:
        if not target.is_file():
            print(f"missing {target}", file=sys.stderr)
            return 1
        print(f"patching {target.name}:")
        data = bytearray(target.read_bytes())
        total += patch_member(data)
        target.write_bytes(data)

    print(f"patched {len(targets)} zone_event member(s), {total} cut tree(s) total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
