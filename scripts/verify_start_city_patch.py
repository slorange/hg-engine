#!/usr/bin/env python3
"""Verify open-world starting-city zone_event patches."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
ZONE_DIR = ROOT / "build/a032"

MAP_T20R0201 = 63
DYNAMIC_WARP_HEADER = 0xFFF
DYNAMIC_WARP_ANCHOR = 0x100


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
    pos += warp_count * 12
    (coord_count,) = struct.unpack_from("<I", data, pos)
    pos += 4
    coords = [struct.unpack_from("<8H", data, pos + i * 16) for i in range(coord_count)]
    return warps, coords


def main() -> None:
    if not openworld_enabled():
        print("ok: OPENWORLD_STARTING_ITEMS off (start-city patches skipped)")
        return

    goldenrod = ZONE_DIR / "2_073"
    saffron = ZONE_DIR / "2_056"
    interior = ZONE_DIR / "2_060"
    vanilla_interior = ROOT / "build/a032_vanilla/2_060"
    for path in (goldenrod, saffron, interior, vanilla_interior):
        if not path.is_file():
            raise SystemExit(f"missing {path}; rebuild zone_event first")

    wx, wz, header, _, _, _ = parse_zone_event(goldenrod.read_bytes())[0][14]
    if (wx, wz, header) != (376, 335, MAP_T20R0201):
        raise SystemExit(f"Goldenrod home door warp wrong: {(wx, wz, header)}")

    wx, wz, header, _, _, _ = parse_zone_event(saffron.read_bytes())[0][14]
    if (wx, wz, header) != (1323, 242, MAP_T20R0201):
        raise SystemExit(f"Saffron home door warp wrong: {(wx, wz, header)}")

    warps, _ = parse_zone_event(interior.read_bytes())
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

    print("ok: outdoor home doors patched; interior exit dynamic; stairs intact")


if __name__ == "__main__":
    main()
