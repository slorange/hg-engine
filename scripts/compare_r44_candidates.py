#!/usr/bin/env python3
"""Compare zone_event members against Route 44 headbutt coords."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "build/a032"

# From Headbutt.c route44.treeCoords envelope
HB_X = (550, 624)
HB_Z = (162, 184)


def parse_objects(path: Path) -> list[dict[str, int]]:
    data = path.read_bytes()
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        out.append(
            {
                "id": f[0],
                "sprite": f[1],
                "type": f[3],
                "script": f[5],
                "face": f[6],
                "x": f[12],
                "z": f[13],
            }
        )
        pos += 32
    return out


def main() -> int:
    subprocess.check_call(
        [sys.executable, str(ROOT / "tools/extract_zone_event_vanilla.py"), str(ZONE)]
    )

    print("Route 44 headbutt tree envelope from Headbutt.c: x=550-624 z=162-184")
    print("Route 42 member 041 envelope: x=430-501 z=166-184\n")

    for member in ("041", "043", "086", "046", "090"):
        objs = parse_objects(ZONE / f"2_{member}")
        xs = [o["x"] for o in objs]
        zs = [o["z"] for o in objs]
        in_hb = [o for o in objs if HB_X[0] <= o["x"] <= HB_X[1] and HB_Z[0] <= o["z"] <= HB_Z[1]]
        fishermen = [o for o in objs if o["sprite"] == 347]
        psychics = [o for o in objs if o["sprite"] in (323, 324, 327)]
        print(f"=== member {member}: {len(objs)} objects ===")
        print(
            f"  span x={min(xs)}-{max(xs)} (dX={max(xs)-min(xs)}) "
            f"z={min(zs)}-{max(zs)} (dZ={max(zs)-min(zs)})"
        )
        print(f"  in headbutt envelope: {len(in_hb)}")
        print(f"  fishermen (spr 347): {len(fishermen)}")
        for o in fishermen:
            print(f"    obj {o['id']} ({o['x']},{o['z']}) script={o['script']}")
        print(f"  psychics (323/324/327): {len(psychics)}")
        for o in psychics:
            print(f"    obj {o['id']} ({o['x']},{o['z']}) script={o['script']}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
