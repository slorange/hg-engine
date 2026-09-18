#!/usr/bin/env python3
"""Remove Route 40 Surf gate (middleman + coord pushback).

Vanilla HGSS blocks the Olivine shoreline unless the player has Surf.
The gate is a middleman NPC plus a coord script on zone_event member 091
(Route 40 / MAP_W40). Olivine outdoors (074) has a matrix duplicate sprite
at the same world tile (script 65535).

See pret 091_W40.json / 074_T26.json and scr_seq_0962_W40.s slot 8.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

# Route 40 (member 091): obj_W40_gsmiddleman1 + scr_seq_W40_008 coord gate.
W40_MIDDLEMAN = (5, 8, 252, 271)
W40_SURF_COORD = (9, 252, 265)

# Olivine outdoors (074): display-only duplicate visible from the city side.
OLIVINE_MATRIX_MIDDLEMAN = (65535, 252, 271)


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


def matches_object(fields: list[int], spec: tuple[int, int, int, int]) -> bool:
    obj_id, script, x, z = spec
    return (
        fields[0] == obj_id
        and fields[5] == script
        and fields[12] == x
        and fields[13] == z
    )


def matches_matrix_middleman(fields: list[int]) -> bool:
    script, x, z = OLIVINE_MATRIX_MIDDLEMAN
    return fields[5] == script and fields[12] == x and fields[13] == z


def matches_coord(fields: list[int], spec: tuple[int, int, int]) -> bool:
    script, x, z = spec
    return fields[0] == script and fields[1] == x and fields[2] == z


def rebuild(
    bgs: bytes,
    objects: list[bytes],
    warps: bytes,
    coords: list[list[int]],
) -> bytearray:
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


def patch_w40(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    removed_middleman = False
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if matches_object(fields, W40_MIDDLEMAN):
            removed_middleman = True
            continue
        new_objects.append(pack_object(fields, y))

    new_coords = [c for c in coords if not matches_coord(c, W40_SURF_COORD)]
    removed_coord = len(new_coords) < len(coords)

    if not removed_middleman:
        raise ValueError("Route 40 Surf gate middleman not found in zone_event 091")
    if not removed_coord:
        raise ValueError("Route 40 Surf gate coord script not found in zone_event 091")

    data[:] = rebuild(bgs, new_objects, warps, new_coords)
    print(
        f"091: removed Surf gate middleman + coord, "
        f"objects {len(objects)}->{len(new_objects)}, "
        f"coords {len(coords)}->{len(new_coords)}"
    )


def patch_olivine_duplicate(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    removed = False
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if matches_matrix_middleman(fields):
            removed = True
            continue
        new_objects.append(pack_object(fields, y))

    if not removed:
        print("074: Surf gate matrix duplicate already absent (ok)")
        return

    data[:] = rebuild(bgs, new_objects, warps, coords)
    print(
        f"074: removed Surf gate matrix duplicate, "
        f"objects {len(objects)}->{len(new_objects)}"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032>", file=sys.stderr)
        return 1

    zone_dir = Path(argv[1])
    w40 = zone_dir / "2_091"
    olivine = zone_dir / "2_074"
    if not w40.is_file() or not olivine.is_file():
        print(f"missing {w40} or {olivine}", file=sys.stderr)
        return 1

    w40_data = bytearray(w40.read_bytes())
    patch_w40(w40_data)
    w40.write_bytes(w40_data)

    olivine_data = bytearray(olivine.read_bytes())
    patch_olivine_duplicate(olivine_data)
    olivine.write_bytes(olivine_data)

    print(f"patched Route 40 Surf gate in {zone_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
