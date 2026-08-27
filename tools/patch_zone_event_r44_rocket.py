#!/usr/bin/env python3
"""Route 44 zone_event: remove RageCandyBar-related NPCs for rocket-skip."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

# Route 44 map objects (member 046).
R44_BLOCKER = (0, 1, 1040, 367)
R44_BIGMAN = (1, 2, 1044, 380)
R44_LOOKALIKE = (2, 7, 1031, 371)

# Outdoor matrix duplicate objects (member 090) at the same junction.
MATRIX_BIGMAN = (1, 65535, 1044, 380)
MATRIX_MIDDLEMAN = (12, 1, 1043, 415)

MEMBER_SPECS: dict[str, tuple[tuple[int, int, int, int], ...]] = {
    "046": (R44_BLOCKER, R44_BIGMAN, R44_LOOKALIKE),
    "090": (MATRIX_BIGMAN, MATRIX_MIDDLEMAN),
}


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


def patch_member(data: bytearray, remove_specs: tuple[tuple[int, int, int, int], ...], label: str) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    removed: list[str] = []
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if any(matches(fields, spec) for spec in remove_specs):
            removed.append(f"id{fields[0]}/script{fields[5]}/sprite{fields[1]}")
            continue
        new_objects.append(pack_object(fields, y))

    if not removed:
        raise ValueError(f"{label}: RageCandyBar NPCs not found in zone_event")

    out = bytearray()
    out.extend(struct.pack("<I", len(bgs) // 20))
    out.extend(bgs)
    out.extend(struct.pack("<I", len(new_objects)))
    out.extend(b"".join(new_objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(coords)))
    for c in coords:
        out.extend(struct.pack("<8H", *c))

    data[:] = out
    print(f"removed from {label}: {', '.join(removed)}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032>", file=sys.stderr)
        return 1

    zone_dir = Path(argv[1])
    if not zone_dir.is_dir():
        print(f"missing {zone_dir}", file=sys.stderr)
        return 1

    for member, specs in MEMBER_SPECS.items():
        target = zone_dir / f"2_{member}"
        if not target.is_file():
            print(f"missing {target}", file=sys.stderr)
            return 1
        data = bytearray(target.read_bytes())
        patch_member(data, specs, f"zone_event {member}")
        target.write_bytes(data)

    print(f"patched Route 44 RageCandyBar NPCs in {zone_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
