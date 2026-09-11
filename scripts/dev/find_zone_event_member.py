#!/usr/bin/env python3
"""Find zone_event member(s) for a placement target.

Map header ID from include/constants/maps.h is NOT the zone_event member.
Look up pret src/data/map_headers.h: eventsBank, scriptsBank, msgBank per map.

Usage:
  # World point — which members' object bboxes contain it?
  python3 scripts/dev/find_zone_event_member.py --world 273 248

  # Inspect a specific member (from pret eventsBank)
  python3 scripts/dev/find_zone_event_member.py --member 74

See documentation/HACK-NOTES.md § "World placement (DSPRE)".
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VANILLA = ROOT / "build/a032_vanilla"

WORLD_SCALE_MIN = 200  # members with object x > this use world coords


def parse_objects(data: bytes) -> list[tuple[int, ...]]:
    if len(data) < 8:
        return []
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    if pos + 4 > len(data):
        return []
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out: list[tuple[int, ...]] = []
    for _ in range(n):
        if pos + 32 > len(data):
            break
        out.append(struct.unpack_from("<14H", data, pos))
        pos += 32
    return out


def member_stats(member: int, objs: list[tuple[int, ...]]) -> dict:
    if not objs:
        return {"member": member, "count": 0, "scale": "empty"}
    xs = [o[12] for o in objs]
    zs = [o[13] for o in objs]
    scale = "world" if max(xs) >= WORLD_SCALE_MIN else "local"
    return {
        "member": member,
        "count": len(objs),
        "scale": scale,
        "x_min": min(xs),
        "x_max": max(xs),
        "z_min": min(zs),
        "z_max": max(zs),
    }


def load_members(root: Path) -> list[tuple[int, list[tuple[int, ...]]]]:
    rows: list[tuple[int, list[tuple[int, ...]]]] = []
    for p in sorted(root.glob("2_*")):
        member = int(p.name.split("_", 1)[1])
        rows.append((member, parse_objects(p.read_bytes())))
    return rows


def contains(stats: dict, x: int, z: int) -> bool:
    return stats["count"] and stats["x_min"] <= x <= stats["x_max"] and stats["z_min"] <= z <= stats["z_max"]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--world", nargs=2, type=int, metavar=("X", "Z"), help="world tile to search")
    ap.add_argument("--member", type=int, metavar="N", help="zone_event member index (pret eventsBank)")
    ap.add_argument("--near", nargs=2, type=int, metavar=("X", "Z"), help="with --member: list objs within 8 tiles")
    ap.add_argument("--root", type=Path, default=VANILLA, help="zone_event dir (default: build/a032_vanilla)")
    args = ap.parse_args(argv[1:])

    if not args.root.is_dir():
        print(f"missing {args.root} — run a build first", file=sys.stderr)
        return 1

    members = load_members(args.root)

    if args.member is not None:
        member = args.member
        objs = next((o for m, o in members if m == member), None)
        if objs is None:
            print(f"member 2_{member:03d} not found", file=sys.stderr)
            return 1
        stats = member_stats(member, objs)
        print(f"zone_event 2_{member:03d} ({stats['scale']}-scale, {stats['count']} objs)")
        print(f"  bbox: x={stats['x_min']}-{stats['x_max']} z={stats['z_min']}-{stats['z_max']}")
        if args.near:
            nx, nz = args.near
            near = [o for o in objs if abs(o[12] - nx) <= 8 and abs(o[13] - nz) <= 8]
            print(f"  objects within 8 of ({nx}, {nz}):")
            for o in near:
                print(f"    id={o[0]} spr={o[1]} scr={o[5]} @({o[12]},{o[13]})")
            if not near:
                print("    (none)")
        print()
        print("Confirm this member matches pret map_headers.h eventsBank for your map.")

    if args.world:
        wx, wz = args.world
        print(f"World point ({wx}, {wz}) — members whose object bbox contains it:")
        hits = []
        for member, objs in members:
            stats = member_stats(member, objs)
            if contains(stats, wx, wz):
                hits.append(stats)
        if not hits:
            print("  (none)")
        for s in sorted(hits, key=lambda x: x["member"]):
            print(
                f"  2_{s['member']:03d}: {s['scale']}-scale, "
                f"x={s['x_min']}-{s['x_max']} z={s['z_min']}-{s['z_max']} ({s['count']} objs)"
            )
        print()
        print("Cross-check the hit with pret map_headers.h eventsBank — do not assume member == map header id.")

    if args.member is None and args.world is None:
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
