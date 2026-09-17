#!/usr/bin/env python3
"""Verify open-world starting-city zone_event patches."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "include/config.h"
ZONE_DIR = ROOT / "build/a032"

MAP_T20R0201 = 63
DYNAMIC_WARP_HEADER = 0xFFF
DYNAMIC_WARP_ANCHOR = 0x100

# (label, member, warp index, x, z)
EXPECTED_DOORS: list[tuple[str, int, int, int, int]] = [
    ("Goldenrod", 73, 14, 376, 335),
    ("Saffron", 56, 14, 1323, 242),
    ("Fuchsia", 53, 8, 1200, 439),
    ("Violet", 70, 8, 459, 254),
    ("Azalea", 71, 4, 419, 468),
    ("Ecruteak", 75, 1, 375, 173),
    ("Olivine", 74, 6, 287, 241),
    ("Cianwood", 72, 7, 167, 335),
    ("Mahogany", 84, 4, 537, 174),
    ("Blackthorn", 86, 4, 684, 168),
    ("Pallet", 46, 0, 1033, 363),
    ("Viridian", 47, 1, 1034, 244),
    ("Pewter", 48, 5, 1037, 111),
    ("Cerulean", 49, 2, 1304, 131),
    ("Lavender", 50, 2, 1414, 249),
    ("Celadon", 52, 6, 1225, 261),
    ("Vermilion", 51, 3, 1301, 309),
]


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def parse_zone_event(data: bytes):
    pos = 0
    (bg_count,) = struct.unpack_from("<I", data, pos)
    pos += 4 + bg_count * 20
    (obj_count,) = struct.unpack_from("<I", data, pos)
    pos += 4 + obj_count * 32
    (warp_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    warps = [struct.unpack_from("<HHHHHH", data, pos + i * 12) for i in range(warp_count)]
    return warps


def main() -> None:
    if not openworld_enabled():
        print("ok: OPENWORLD_STARTING_ITEMS off (start-city patches skipped)")
        return

    vanilla_interior = ROOT / "build/a032_vanilla/2_060"
    needed = {member for _, member, _, _, _ in EXPECTED_DOORS}
    needed.add(60)
    for member in sorted(needed):
        path = ZONE_DIR / f"2_{member:03d}"
        if not path.is_file():
            raise SystemExit(f"missing {path}; rebuild zone_event first")
    if not vanilla_interior.is_file():
        raise SystemExit("missing build/a032_vanilla/2_060; rebuild zone_event first")

    for label, member, idx, x, z in EXPECTED_DOORS:
        warps = parse_zone_event((ZONE_DIR / f"2_{member:03d}").read_bytes())
        wx, wz, header, _, _, _ = warps[idx]
        if (wx, wz, header) != (x, z, MAP_T20R0201):
            raise SystemExit(f"{label} home door warp wrong: {(wx, wz, header)}")

    interior = ZONE_DIR / "2_060"
    warps = parse_zone_event(interior.read_bytes())
    if len(warps) != 2:
        raise SystemExit(f"interior 060 must keep 2 warps, got {len(warps)}")

    exit_wx, exit_wz, exit_hdr, exit_anc, _, _ = warps[0]
    if (exit_wx, exit_wz, exit_hdr, exit_anc) != (3, 10, DYNAMIC_WARP_HEADER, DYNAMIC_WARP_ANCHOR):
        raise SystemExit(
            f"interior exit warp 0 wrong: {(exit_wx, exit_wz, exit_hdr, exit_anc)} "
            f"(expected dynamic header/anchor)"
        )

    stair_wx, stair_wz, stair_hdr, stair_anc, _, _ = warps[1]
    if (stair_wx, stair_wz, stair_hdr, stair_anc) != (3, 3, 64, 0):
        raise SystemExit(f"interior stairs warp 1 wrong: {(stair_wx, stair_wz, stair_hdr, stair_anc)}")

    print(f"ok: {len(EXPECTED_DOORS)} outdoor home doors patched; interior exit dynamic; stairs intact")


if __name__ == "__main__":
    main()
