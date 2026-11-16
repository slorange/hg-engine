#!/usr/bin/env python3
"""Saffron Poké Mart (zone_event 365 / T11FS0101) keeps both clerks.

Member 365 is not Violet Gym. A gym object-removal patch once matched the
specialty clerk (obj 3, script 2) and deleted him. Violet Gym is member 131.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

SPRITE_SHOP = 334
# (obj id, script id, x, z) — script id is 1-based slot.
CLERKS = (
    (0, 1, 2, 6),
    (3, 2, 2, 4),
)


def objects(data: bytes) -> list[tuple[int, ...]]:
    pos = 0
    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4 + bg_count * 20
    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    rows = []
    for _ in range(obj_count):
        rows.append(struct.unpack_from("<14H", data, pos))
        pos += 32
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_365>", file=sys.stderr)
        return 1

    path = Path(argv[1])
    if path.name != "2_365":
        raise SystemExit(f"FAIL: expected zone_event 2_365 (Saffron mart), got {path.name}")

    rows = objects(path.read_bytes())
    by_id = {row[0]: row for row in rows}
    for obj_id, script_id, x, z in CLERKS:
        row = by_id.get(obj_id)
        if row is None:
            raise SystemExit(f"FAIL: Saffron mart obj {obj_id} missing")
        if (row[1], row[5], row[12], row[13]) != (SPRITE_SHOP, script_id, x, z):
            raise SystemExit(
                f"FAIL: obj {obj_id} sprite={row[1]} script={row[5]} @({row[12]},{row[13]}); "
                f"expected sprite={SPRITE_SHOP} script={script_id} @({x},{z})"
            )
        print(f"OK: clerk obj {obj_id} script={script_id} @({x},{z})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
