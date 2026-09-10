#!/usr/bin/env python3
"""Probe which map headers / zone_event members cover Route 44 bridge coords."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE_DIR = ROOT / "build/a032"
HDR_PATH = ROOT / "base/root/a/0/4/1"
MATRIX_PATH = ROOT / "base/root/a/0/4/3"


def ensure_zone() -> None:
    if not (ZONE_DIR / "2_090").is_file():
        subprocess.check_call(
            [sys.executable, str(ROOT / "tools/extract_zone_event_vanilla.py"), str(ZONE_DIR)]
        )


def parse_header(index: int) -> dict[str, int]:
    raw = HDR_PATH.read_bytes()
    size = 24
    off = index * size
    u16 = struct.unpack_from("<12H", raw, off)
    # pret MapHeader: mapsec, cb_model, cb_world, fly, matrix_id, scripts_id, level_id, bgs_id, ...
    return {
        "idx": index,
        "matrix": u16[4],
        "scripts": u16[5],
        "level": u16[6],
        "bgs": u16[7],
    }


def dump_zone_member(member: str) -> list[tuple[int, int, int, int, int]]:
    data = (ZONE_DIR / f"2_{member}").read_bytes()
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out: list[tuple[int, int, int, int, int]] = []
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        out.append((f[0], f[1], f[5], f[12], f[13]))
        pos += 32
    return out


def main() -> int:
    ensure_zone()
    print("=== Map headers 44-51 (scripts_id ≈ scr_seq / zone_event member) ===")
    for i in range(44, 52):
        h = parse_header(i)
        print(
            f"  header {i}: matrix={h['matrix']} scripts={h['scripts']} "
            f"level={h['level']} bgs={h['bgs']}"
        )

    print("\n=== zone_event 046 (map) objects ===")
    for row in dump_zone_member("046"):
        print(f"  id={row[0]} spr={row[1]} script={row[2]} x={row[3]} z={row[4]}")

    print("\n=== zone_event 090 (matrix) objects near bridge (z 400-420) ===")
    for row in dump_zone_member("090"):
        if 400 <= row[4] <= 420:
            print(f"  id={row[0]} spr={row[1]} script={row[2]} x={row[3]} z={row[4]}")

    # Find zone_event members that reference coords near bridge
    bridge_x, bridge_z = 1048, 412
    print(f"\n=== zone_event members with objects within 20 tiles of ({bridge_x},{bridge_z}) ===")
    for path in sorted(ZONE_DIR.glob("2_*")):
        member = path.name[2:]
        try:
            objs = dump_zone_member(member)
        except Exception:
            continue
        hits = [
            o
            for o in objs
            if abs(o[3] - bridge_x) <= 20 and abs(o[4] - bridge_z) <= 20
        ]
        if hits:
            print(f"  member {member}:")
            for o in hits:
                print(f"    id={o[0]} spr={o[1]} script={o[2]} x={o[3]} z={o[4]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
