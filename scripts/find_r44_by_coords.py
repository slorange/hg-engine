#!/usr/bin/env python3
"""Find zone_event members matching Route 44 geography near Route 42."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "build/a032"
FACES = ("N", "S", "W", "E")

# User hypothesis: R44 near R42 guru (426,177) across Mahogany ~100-200 steps east.
SEARCH_BOXES = (
    ("near_r42", 520, 680, 150, 210),
    ("r42_band", 400, 520, 150, 210),
    ("member090_band", 1020, 1060, 360, 490),
)


def parse_objects(data: bytes) -> list[dict[str, int]]:
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out: list[dict[str, int]] = []
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        out.append(
            {
                "id": f[0],
                "sprite": f[1],
                "mov": f[2],
                "type": f[3],
                "script": f[5],
                "face": f[6],
                "x": f[12],
                "z": f[13],
            }
        )
        pos += 32
    return out


def in_box(o: dict[str, int], xmin: int, xmax: int, zmin: int, zmax: int) -> bool:
    return xmin <= o["x"] <= xmax and zmin <= o["z"] <= zmax


def span(objs: list[dict[str, int]]) -> tuple[int, int, int, int]:
    xs = [o["x"] for o in objs]
    zs = [o["z"] for o in objs]
    return min(xs), max(xs), min(zs), max(zs)


def main() -> int:
    subprocess.check_call(
        [sys.executable, str(ROOT / "tools/extract_zone_event_vanilla.py"), str(ZONE)]
    )

    print("=== Members ranked by object count in near_r42 box (520-680 x, 150-210 z) ===")
    ranked: list[tuple[int, str, list[dict[str, int]]]] = []
    for path in sorted(ZONE.glob("2_*")):
        member = path.name[2:]
        try:
            objs = parse_objects(path.read_bytes())
        except Exception:
            continue
        hits = [o for o in objs if in_box(o, *SEARCH_BOXES[0][1:])]
        if hits:
            ranked.append((len(hits), member, hits))
    ranked.sort(key=lambda t: (-t[0], t[1]))
    for count, member, hits in ranked[:25]:
        xmin, xmax, zmin, zmax = span(hits)
        dx, dz = xmax - xmin, zmax - zmin
        print(f"  member {member:>3s}: {count:2d} objs  x={xmin}-{xmax} (Δ{dx:3d})  z={zmin}-{zmax} (Δ{dz:3d})")

    print("\n=== Detail: members with exactly 5-9 objects in near_r42 box ===")
    for count, member, hits in ranked:
        if not (5 <= count <= 9):
            continue
        xmin, xmax, zmin, zmax = span(hits)
        print(f"\n--- member {member} ({count} objects) ---")
        for o in sorted(hits, key=lambda row: (row["z"], row["x"])):
            face = FACES[o["face"]] if o["face"] < len(FACES) else "?"
            print(
                f"  obj {o['id']:2d} ({o['x']:4d},{o['z']:3d}) face={face} "
                f"sprite={o['sprite']:4d} script={o['script']:5d} type={o['type']}"
            )

    print("\n=== Compare known references ===")
    for label, member in (("Route 42 map", "041"), ("member 090 (old guess)", "090"), ("member 046", "046")):
        p = ZONE / f"2_{member}"
        if not p.is_file():
            continue
        objs = parse_objects(p.read_bytes())
        print(f"\n{label} member {member}: {len(objs)} total objects")
        if objs:
            xmin, xmax, zmin, zmax = span(objs)
            print(f"  full span x={xmin}-{xmax} (Δ{xmax-xmin}) z={zmin}-{zmax} (Δ{zmax-zmin})")

    # Also scan outdoor matrix members for same near_r42 box
    print("\n=== Any member (anywhere) with 6-8 objs ALL in near_r42 box ===")
    for path in sorted(ZONE.glob("2_*")):
        member = path.name[2:]
        try:
            objs = parse_objects(path.read_bytes())
        except Exception:
            continue
        if not (6 <= len(objs) <= 8):
            continue
        if all(in_box(o, *SEARCH_BOXES[0][1:]) for o in objs):
            xmin, xmax, zmin, zmax = span(objs)
            print(f"  member {member}: {len(objs)} objs x Δ={xmax-xmin} z Δ={zmax-zmin}")
            for o in sorted(objs, key=lambda row: (row["z"], row["x"])):
                print(f"    ({o['x']},{o['z']}) sprite={o['sprite']} script={o['script']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
