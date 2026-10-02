#!/usr/bin/env python3
"""Olivine City outdoors (zone_event 074): remove gym-area story coord trigger.

Vanilla: coord script 2 at world (272, 239), VAR_UNK_4078 (0x4078) == 0.

See documentation/HACK-NOTES.md § Olivine gym story skip.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

GYM_STORY_COORD = (2, 272, 239)


def parse_zone_event(data: bytes) -> tuple[list[list[int]], list[bytes], bytes, list[list[int]]]:
    pos = 0

    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    bgs: list[list[int]] = []
    for _ in range(bg_count):
        bgs.append(list(struct.unpack_from("<10H", data, pos)))
        pos += 20

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


def pack_bg(fields: list[int]) -> bytes:
    return struct.pack("<10H", *fields)


def patch_member(data: bytearray) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)

    script, x, z = GYM_STORY_COORD
    new_coords = [c for c in coords if not (c[0] == script and c[1] == x and c[2] == z)]
    if len(new_coords) == len(coords):
        if not coords:
            print("074: no coord events (already stripped)")
            return
        raise ValueError(
            f"Olivine gym story coord ({script}, {x}, {z}) not found in zone_event 074"
        )

    out = bytearray()
    out.extend(struct.pack("<I", len(bgs)))
    for bg in bgs:
        out.extend(pack_bg(bg))
    out.extend(struct.pack("<I", len(objects)))
    out.extend(b"".join(objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(new_coords)))
    for c in new_coords:
        out.extend(struct.pack("<8H", *c))

    data[:] = out
    print(
        f"removed Olivine gym story coord ({script}, {x}, {z}), "
        f"coords {len(coords)}->{len(new_coords)}"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_074>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
