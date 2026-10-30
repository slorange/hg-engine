#!/usr/bin/env python3
"""Find EcologyWorldSave (ECO1) in a DeSmuME .dsv and print a short summary."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ECOLOGY_SAVE_MAGIC = 0x314F4345  # 'ECO1'
ECOLOGY_COMPAT_VERSION = 0xEE645521
ECOLOGY_GEN_TOTAL_SLOTS = 1012
ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX = 96
ECOLOGY_SAVE_FAMILY_EMPTY = 0xFF


def parse_ecology_at(data: bytes, off: int) -> dict | None:
    if off + 16 > len(data):
        return None
    magic_v, compat, seed = struct.unpack_from("<III", data, off)
    slot_count, _reserved = struct.unpack_from("<HH", data, off + 12)
    body = off + 16
    need = body + ECOLOGY_GEN_TOTAL_SLOTS + 4 + ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX * 2
    if need > len(data):
        return None
    family_ids = data[body : body + ECOLOGY_GEN_TOTAL_SLOTS]
    sparse_count = data[body + ECOLOGY_GEN_TOTAL_SLOTS]
    sparse_base = body + ECOLOGY_GEN_TOTAL_SLOTS + 4
    sparse: list[tuple[int, int]] = []
    for j in range(min(sparse_count, ECOLOGY_SAVE_LAND_TIME_SPARSE_MAX)):
        fid = data[sparse_base + j * 2]
        mask = data[sparse_base + j * 2 + 1]
        sparse.append((fid, mask))
    filled = sum(
        1
        for i in range(min(slot_count, ECOLOGY_GEN_TOTAL_SLOTS))
        if family_ids[i] != ECOLOGY_SAVE_FAMILY_EMPTY
    )
    return {
        "offset": off,
        "magic": magic_v,
        "compat": compat,
        "seed": seed,
        "slot_count": slot_count,
        "filled_slots": filled,
        "sparse_count": sparse_count,
        "sparse": sparse,
        "family_preview": list(family_ids[:24]),
    }


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "test.dsv")
    if not path.is_file():
        print(f"Missing file: {path}", file=sys.stderr)
        return 1
    data = path.read_bytes()
    print(f"File: {path}")
    print(f"Size: {len(data)} bytes ({len(data) / 1024 / 1024:.2f} MiB)")

    hits: list[int] = []
    start = 0
    while True:
        i = data.find(b"ECO1", start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1

    print(f"ECO1 string hits: {len(hits)}")
    if not hits:
        print("No ECO1 found.")
        return 2

    valid = 0
    for off in hits:
        p = parse_ecology_at(data, off)
        if p is None or p["magic"] != ECOLOGY_SAVE_MAGIC:
            continue
        valid += 1
        print("---")
        print(f"offset 0x{p['offset']:X}")
        ok_compat = p["compat"] == ECOLOGY_COMPAT_VERSION
        print(f"  compat 0x{p['compat']:08X} {'OK' if ok_compat else 'MISMATCH'}")
        print(f"  worldSeed {p['seed']} (0x{p['seed']:X})")
        print(f"  slotCount {p['slot_count']}")
        print(f"  assigned family slots (within slotCount): {p['filled_slots']}")
        print(f"  landTime sparse entries: {p['sparse_count']}")
        if p["sparse"]:
            print(f"  sparse (familyId, mask): {p['sparse'][:12]}{'...' if len(p['sparse']) > 12 else ''}")
        print(f"  first 24 familyIds: {p['family_preview']}")

    if valid == 0:
        print("ECO1 bytes found but no full EcologyWorldSave header parsed.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
