#!/usr/bin/env python3
"""Blackthorn Gym (MAP_T30GYM0101): verify Clair object on zone_event member 137.

pret: zone_event/137_T30GYM0101.json — Clair is obj0 (SPRITE_GSLEADER8), script slot 1.
Member 024 is a different map; do not patch it for this gym.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

CLAIR_OBJECT_INDEX = 0
CLAIR_SPRITE_GSLEADER8 = 359
CLAIR_LEADER_SCRIPT = 1


def patch_member(data: bytearray) -> None:
    pos = 0
    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4 + bg_count * 20
    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    if obj_count <= CLAIR_OBJECT_INDEX:
        raise ValueError(f"expected Clair obj{CLAIR_OBJECT_INDEX}, got {obj_count} objects")

    obj_start = pos
    obj_off = obj_start + CLAIR_OBJECT_INDEX * 32
    fields = list(struct.unpack_from("<14H", data, obj_off))
    if fields[1] != CLAIR_SPRITE_GSLEADER8:
        raise ValueError(f"obj{CLAIR_OBJECT_INDEX} is not Clair (sprite={fields[1]})")
    fields[5] = CLAIR_LEADER_SCRIPT
    y = struct.unpack_from("<I", data, obj_off + 28)[0]
    data[obj_off : obj_off + 28] = struct.pack("<14H", *fields)
    struct.pack_into("<I", data, obj_off + 28, y)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_137>", file=sys.stderr)
        return 1
    target = Path(argv[1])
    if target.name != "2_137":
        print(f"warning: expected 2_137, got {target.name}", file=sys.stderr)
    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(f"Clair obj{CLAIR_OBJECT_INDEX} script -> {CLAIR_LEADER_SCRIPT} in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
