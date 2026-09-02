#!/usr/bin/env python3
"""Open-world starting city: patch outdoor home doors only (Goldenrod / Saffron).

Interior member 060 must keep both warps — bedroom 2F links to 1F via warp slot 1
(anchor 1). Removing the front-door warp shifts indices and breaks the stairs.

See documentation/HACK-NOTES.md § "Home = bidirectional door + interior swap".
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"

MAP_T20R0201 = 63
MAP_T25R0801 = 205
MAP_T11R0501 = 399

GOLDENROD_DOOR = (73, 14, 376, 335, MAP_T25R0801)
SAFFRON_DOOR = (56, 14, 1323, 242, MAP_T11R0501)
INTERIOR_EXIT = (60, 0, 3, 10, 60, 1)  # member, warp index, x, z, old header, old anchor
DYNAMIC_WARP_HEADER = 0xFFF
DYNAMIC_WARP_ANCHOR = 0x100


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def parse_zone_event(data: bytes) -> tuple[list[list[int]], list[bytes], list[tuple[int, int, int, int, int, int]], list[list[int]]]:
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
    warps: list[tuple[int, int, int, int, int, int]] = []
    for _ in range(warp_count):
        warps.append(struct.unpack_from("<HHHHHH", data, pos))
        pos += 12

    (coord_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    coords: list[list[int]] = []
    for _ in range(coord_count):
        coords.append(list(struct.unpack_from("<8H", data, pos)))
        pos += 16

    if pos != len(data):
        raise ValueError(f"unexpected trailing data: parsed {pos}, file {len(data)}")

    return bgs, objects, warps, coords


def rebuild(bgs, objects, warps, coords) -> bytes:
    out = bytearray()
    out.extend(struct.pack("<I", len(bgs)))
    for bg in bgs:
        out.extend(struct.pack("<10H", *bg))
    out.extend(struct.pack("<I", len(objects)))
    out.extend(b"".join(objects))
    out.extend(struct.pack("<I", len(warps)))
    for warp in warps:
        out.extend(struct.pack("<HHHHHH", *warp))
    out.extend(struct.pack("<I", len(coords)))
    for coord in coords:
        out.extend(struct.pack("<8H", *coord))
    return bytes(out)


def patch_city_door_warp(data: bytearray, member: int, warp_index: int, x: int, z: int, old_header: int) -> None:
    bgs, objects, warps, coords = parse_zone_event(data)
    if warp_index >= len(warps):
        raise ValueError(f"member {member}: warp index {warp_index} missing (have {len(warps)})")

    wx, wz, header, anchor, dest_x, dest_z = warps[warp_index]
    if (wx, wz, header) != (x, z, old_header):
        raise ValueError(
            f"member {member}: warp {warp_index} expected ({x},{z})->{old_header}, "
            f"got ({wx},{wz})->{header}"
        )

    warps[warp_index] = (wx, wz, MAP_T20R0201, anchor, dest_x, dest_z)
    data[:] = rebuild(bgs, objects, warps, coords)
    print(f"member {member}: warp {warp_index} at ({x},{z}) now -> {MAP_T20R0201}")


def patch_interior_exit_warp(data: bytearray) -> None:
    """Retarget front-door warp slot 0 to dynamicWarp without reindexing stairs (slot 1)."""
    bgs, objects, warps, coords = parse_zone_event(data)

    member, warp_index, x, z, old_header, old_anchor = INTERIOR_EXIT
    if warp_index >= len(warps):
        raise ValueError(f"member {member}: exit warp index {warp_index} missing")

    wx, wz, header, anchor, dest_x, dest_z = warps[warp_index]
    if (wx, wz, header, anchor) != (x, z, old_header, old_anchor):
        raise ValueError(
            f"member {member}: exit warp expected ({x},{z})->{old_header} anchor {old_anchor}, "
            f"got ({wx},{wz})->{header} anchor {anchor}"
        )

    warps[warp_index] = (wx, wz, DYNAMIC_WARP_HEADER, DYNAMIC_WARP_ANCHOR, dest_x, dest_z)
    data[:] = rebuild(bgs, objects, warps, coords)
    print(
        f"member {member}: exit warp {warp_index} at ({x},{z}) "
        f"now dynamic (header {DYNAMIC_WARP_HEADER}, anchor {DYNAMIC_WARP_ANCHOR})"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032>", file=sys.stderr)
        return 1

    zone_dir = Path(argv[1])
    if not zone_dir.is_dir():
        print(f"missing zone_event dir {zone_dir}", file=sys.stderr)
        return 1

    if not openworld_enabled():
        print("OPENWORLD_STARTING_ITEMS disabled; skipping start-city zone_event patches")
        return 0

    goldenrod = zone_dir / "2_073"
    saffron = zone_dir / "2_056"
    interior = zone_dir / "2_060"
    for path in (goldenrod, saffron, interior):
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1

    m, idx, x, z, old = GOLDENROD_DOOR
    data = bytearray(goldenrod.read_bytes())
    patch_city_door_warp(data, m, idx, x, z, old)
    goldenrod.write_bytes(data)

    m, idx, x, z, old = SAFFRON_DOOR
    data = bytearray(saffron.read_bytes())
    patch_city_door_warp(data, m, idx, x, z, old)
    saffron.write_bytes(data)

    data = bytearray(interior.read_bytes())
    patch_interior_exit_warp(data)
    interior.write_bytes(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
