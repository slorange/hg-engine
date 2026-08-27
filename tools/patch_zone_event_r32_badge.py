#!/usr/bin/env python3
"""Route 32 zone_event member 033: remove Zephyr Badge gate south of Violet City."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

# Gate NPC (sprite 328 / GSMIDDLEMAN1) and walk-past coord — pret 033_R32.
BLOCKER_NPC = (1, 2, 477, 305)
EXIT_COORD = (3, 475, 305)

REMOVE_SPECS = (BLOCKER_NPC,)


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


def matches(fields: list[int], spec: tuple[int, int, int, int]) -> bool:
    obj_id, script, x, z = spec
    return (
        fields[0] == obj_id
        and fields[5] == script
        and fields[12] == x
        and fields[13] == z
    )


def patch_member(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    removed: list[str] = []
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if any(matches(fields, spec) for spec in REMOVE_SPECS):
            removed.append(f"id{fields[0]}/script{fields[5]}/sprite{fields[1]}")
            continue
        new_objects.append(pack_object(fields, y))

    script, x, z = EXIT_COORD
    new_coords = [c for c in coords if not (c[0] == script and c[1] == x and c[2] == z)]
    removed_coord = len(new_coords) < len(coords)

    if not removed:
        raise ValueError("Route 32 badge gate object not found in zone_event 033")
    if not removed_coord:
        raise ValueError("Route 32 badge gate coord trigger not found in zone_event 033")

    out = bytearray()
    out.extend(struct.pack("<I", len(bgs)))
    for bg in bgs:
        out.extend(pack_bg(bg))
    out.extend(struct.pack("<I", len(new_objects)))
    out.extend(b"".join(new_objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(new_coords)))
    for c in new_coords:
        out.extend(struct.pack("<8H", *c))

    data[:] = out
    print(
        f"removed Route 32 gate: {', '.join(removed)}, coord={removed_coord}, "
        f"objects {len(objects)}->{len(new_objects)}"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_033>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(f"patched Route 32 badge gate in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
