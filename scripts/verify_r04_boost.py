#!/usr/bin/env python3
"""Verify Route 4 ledge-boost patch (zone_event 009, scr_seq 178)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE_MEMBER = 9
SCR_MEMBER = 178
BOOST_SCRIPT_ID = 2
BOOST_OBJECT_ID = 4
NPC_X = 1270
NPC_Z = 118
LAND_X = 1270
LAND_Z = 116


def zone_objects(data: bytes) -> list[tuple[int, int, int, int]]:
    pos = 0
    bg_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg_count * 20
    obj_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(obj_count):
        vals = struct.unpack_from("<14H", data, pos)
        out.append((vals[0], vals[5], vals[12], vals[13]))
        pos += 32
    return out


def scr_script_count(data: bytes) -> int:
    pos = 0
    while pos + 2 <= len(data) and pos < 512:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return pos // 4
        pos += 4
    raise ValueError("scrdef_end not found")


def main() -> int:
    ok = True

    ze = ROOT / f"build/a032/2_{ZONE_MEMBER:03d}"
    if not ze.is_file():
        print(f"FAIL: missing {ze}")
        return 1

    boost = [
        o for o in zone_objects(ze.read_bytes()) if o[0] == BOOST_OBJECT_ID and o[1] == BOOST_SCRIPT_ID
    ]
    if len(boost) != 1:
        print(f"FAIL: expected one boost object id={BOOST_OBJECT_ID}, found {boost}")
        ok = False
    else:
        _, _, x, z = boost[0]
        print(f"OK: zone_event 009 boost NPC at ({x},{z}) scriptId={BOOST_SCRIPT_ID}")
        if (x, z) != (NPC_X, NPC_Z):
            print(f"  note: coords differ from default ({NPC_X},{NPC_Z})")

    sq = ROOT / f"build/a012/2_{SCR_MEMBER}"
    if not sq.is_file():
        print(f"FAIL: missing {sq}")
        ok = False
    else:
        data = sq.read_bytes()
        count = scr_script_count(data)
        if count < 2:
            print(f"FAIL: scr_seq 178 has {count} script(s), expected >= 2")
            ok = False
        else:
            print(f"OK: scr_seq 178 ({len(data)} bytes, {count} scripts)")

    text = ROOT / "data/text/328.txt"
    if not text.is_file():
        print("FAIL: missing data/text/328.txt")
        ok = False
    else:
        lines = [ln for ln in text.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if len(lines) < 5:
            print(f"FAIL: 328.txt has {len(lines)} lines, need 5 (tips + 4 boost)")
            ok = False
        else:
            print(f"OK: data/text/328.txt ({len(lines)} lines)")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
