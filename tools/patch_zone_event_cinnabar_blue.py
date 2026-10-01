#!/usr/bin/env python3
"""Cinnabar Island (zone_event 054): remove overworld Blue (obj 0, spr 375, script 1).

Blue belongs in Viridian Gym in open-world; vanilla keeps him here until the gym gate clears.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
MEMBER = "2_054"
BLUE_OBJECT_ID = 0
BLUE_SPRITE = 375
BLUE_SCRIPT = 1


def openworld_story_skip() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def parse_zone_event(data: bytes) -> tuple[list[bytes], list[bytes], bytes, list[bytes]]:
    pos = 0
    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    bgs = [data[pos + i * 20 : pos + (i + 1) * 20] for i in range(bg_count)]
    pos += bg_count * 20

    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    objects = [data[pos + i * 32 : pos + (i + 1) * 32] for i in range(obj_count)]
    pos += obj_count * 32

    (warp_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    warps = data[pos : pos + warp_count * 12]
    pos += warp_count * 12

    (coord_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    coords = [data[pos + i * 16 : pos + (i + 1) * 16] for i in range(coord_count)]
    pos += coord_count * 16

    if pos != len(data):
        raise ValueError(f"trailing zone_event bytes: parsed {pos}, file {len(data)}")
    return bgs, objects, warps, coords


def pack_zone_event(
    bgs: list[bytes], objects: list[bytes], warps: bytes, coords: list[bytes]
) -> bytes:
    out = bytearray()
    out.extend(struct.pack("<I", len(bgs)))
    out.extend(b"".join(bgs))
    out.extend(struct.pack("<I", len(objects)))
    out.extend(b"".join(objects))
    out.extend(struct.pack("<I", len(warps) // 12))
    out.extend(warps)
    out.extend(struct.pack("<I", len(coords)))
    out.extend(b"".join(coords))
    return bytes(out)


def patch_member(data: bytearray) -> int:
    bgs, objects, warps, coords = parse_zone_event(data)
    kept: list[bytes] = []
    removed = 0
    for obj in objects:
        fields = struct.unpack_from("<14H", obj)
        if fields[0] == BLUE_OBJECT_ID and fields[1] == BLUE_SPRITE and fields[5] == BLUE_SCRIPT:
            removed += 1
            continue
        kept.append(obj)
    if removed == 0:
        raise ValueError("Cinnabar Blue NPC (obj 0 spr 375 script 1) not found")
    data[:] = pack_zone_event(bgs, kept, warps, coords)
    return removed


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/{MEMBER}>", file=sys.stderr)
        return 1
    if not openworld_story_skip():
        print(f"OPENWORLD_STORY_SKIP off; skip {MEMBER}")
        return 0

    path = Path(argv[1])
    data = bytearray(path.read_bytes())
    n = patch_member(data)
    path.write_bytes(data)
    print(f"removed {n} Blue object(s) from {path} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
