#!/usr/bin/env python3
"""Mahogany Town zone_event tweaks for rocket-skip."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

FLAG_HIDE_ROCKET_TAKEOVER_1 = 439

GYM_BLOCKER = (1, 3, 523, 175)
# Middleman at east exit — blocks leaving town (script 1) on map 084.
MIDDLEMAN = (0, 1, 540, 175)
# Same middleman on outdoor matrix layer 043 (script 65535) — still visible from Route 44.
MATRIX_MIDDLEMAN = (0, 65535, 540, 175)
# Big man south of signs (script 5).
BIGMAN = (2, 5, 523, 184)
# coord script 2: blocks exit while VAR_UNK_407A == 0.
EXIT_COORD = (2, 540, 176)


def parse_zone_event(data: bytes) -> tuple[bytes, list[bytes], bytes, list[list[int]]]:
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


def matches(fields: list[int], spec: tuple[int, int, int, int]) -> bool:
    obj_id, script, x, z = spec
    return (
        fields[0] == obj_id
        and fields[5] == script
        and fields[12] == x
        and fields[13] == z
    )


def rebuild(bgs: bytes, objects: list[bytes], warps: bytes, coords: list[list[int]]) -> bytearray:
    out = bytearray()
    out.extend(struct.pack("<I", len(bgs) // 20))
    out.extend(bgs)
    out.extend(struct.pack("<I", len(objects)))
    out.extend(b"".join(objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(coords)))
    for c in coords:
        out.extend(struct.pack("<8H", *c))
    return out


def patch_town(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    gym_patched = False
    removed_middleman = False
    removed_bigman = False
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if matches(fields, MIDDLEMAN):
            removed_middleman = True
            continue
        if matches(fields, BIGMAN):
            removed_bigman = True
            continue
        if matches(fields, GYM_BLOCKER):
            fields[4] = FLAG_HIDE_ROCKET_TAKEOVER_1
            gym_patched = True
        new_objects.append(pack_object(fields, y))

    script, x, z = EXIT_COORD
    new_coords = [c for c in coords if not (c[0] == script and c[1] == x and c[2] == z)]
    removed_coord = len(new_coords) < len(coords)

    if not gym_patched:
        raise ValueError("gym blocker object not found in zone_event 084")
    if not removed_middleman:
        raise ValueError("east exit middleman object not found in zone_event 084")

    data[:] = rebuild(bgs, new_objects, warps, new_coords)
    print(
        f"084: removed middleman + bigman={removed_bigman}, exit coord={removed_coord}, "
        f"objects {len(objects)}->{len(new_objects)}"
    )


def patch_matrix(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    removed = False
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if matches(fields, MATRIX_MIDDLEMAN):
            removed = True
            continue
        new_objects.append(pack_object(fields, y))

    if not removed:
        raise ValueError("matrix middleman object not found in zone_event 043")

    data[:] = rebuild(bgs, new_objects, warps, coords)
    print(f"043: removed matrix middleman, objects {len(objects)}->{len(new_objects)}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032>", file=sys.stderr)
        return 1

    zone_dir = Path(argv[1])
    town = zone_dir / "2_084"
    matrix = zone_dir / "2_043"
    if not town.is_file() or not matrix.is_file():
        print(f"missing {town} or {matrix}", file=sys.stderr)
        return 1

    town_data = bytearray(town.read_bytes())
    patch_town(town_data)
    town.write_bytes(town_data)

    matrix_data = bytearray(matrix.read_bytes())
    patch_matrix(matrix_data)
    matrix.write_bytes(matrix_data)

    print(f"patched Mahogany zone_event in {zone_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
