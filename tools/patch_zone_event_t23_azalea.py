#!/usr/bin/env python3
"""Azalea Town (zone_event 071): remove Slowpoke Well entrance blocker (obj 0 @ 434,461).

Open-world rocket skip sets FLAG_UNK_19F at Mom but obj 0 stays visible/collidable; drop the object.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
MEMBER = "071"
# obj_id, script, world x, world z (well entrance — DSPRE map 34 local ~18,13)
WELL_ENTRANCE_BLOCKER = (0, 1, 434, 461)


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS\b", text, re.MULTILINE) is not None


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
    return fields[0] == obj_id and fields[5] == script and fields[12] == x and fields[13] == z


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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_{MEMBER}>", file=sys.stderr)
        return 1

    if not openworld_enabled():
        return 0

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    bgs, objects, warps, coords = parse_zone_event(data)

    removed = False
    new_objects: list[bytes] = []
    for obj in objects:
        fields = object_fields(obj)
        y = struct.unpack_from("<I", obj, 28)[0]
        if matches(fields, WELL_ENTRANCE_BLOCKER):
            removed = True
            print(
                f"removed well entrance blocker: id={fields[0]} script={fields[5]} "
                f"flag={fields[4]} sprite={fields[1]} @ ({fields[12]},{fields[13]})"
            )
            continue
        new_objects.append(pack_object(fields, y))

    if not removed:
        raise ValueError(f"{target}: well entrance obj 0 @ (434,461) not found")

    data[:] = rebuild(bgs, new_objects, warps, coords)
    target.write_bytes(data)
    print(f"patched Azalea zone_event in {target} ({len(objects)} -> {len(new_objects)} objects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
