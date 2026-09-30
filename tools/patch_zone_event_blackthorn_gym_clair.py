#!/usr/bin/env python3
"""Blackthorn Gym: Clair uses dedicated Leader script slot 13 (Rising Badge in gym)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

CLAIR_LEADER_SCRIPT = 13


def object_fields(obj: bytes) -> list[int]:
    return list(struct.unpack_from("<14H", obj))


def pack_object(fields: list[int], y: int) -> bytes:
    return struct.pack("<14HI", *fields, y)


def patch_member(data: bytearray) -> None:
    pos = 0
    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4 + bg_count * 20
    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    if obj_count < 2:
        raise ValueError(f"expected at least 2 objects, got {obj_count}")
    obj_off = pos + 32
    obj = bytes(data[obj_off : obj_off + 32])
    fields = object_fields(obj)
    if fields[0] != 1 or fields[1] != 385:
        raise ValueError(f"obj1 is not Clair (id={fields[0]} sprite={fields[1]})")
    fields[5] = CLAIR_LEADER_SCRIPT
    y = struct.unpack_from("<I", obj, 28)[0]
    data[obj_off : obj_off + 32] = pack_object(fields, y)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_024>", file=sys.stderr)
        return 1
    target = Path(argv[1])
    data = bytearray(target.read_bytes())
    patch_member(data)
    target.write_bytes(data)
    print(f"Clair obj1 script -> {CLAIR_LEADER_SCRIPT} in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
