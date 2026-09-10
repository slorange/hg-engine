#!/usr/bin/env python3
"""List all vanilla Route 44 NPCs from zone_event extract."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "build/a032"
FACES = ("N", "S", "W", "E")

# Envelope covering all known R44 objects in members 046/090.
R44_X = (1020, 1060)
R44_Z = (360, 490)


def parse_objects(data: bytes) -> list[dict[str, int]]:
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out: list[dict[str, int]] = []
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        y = struct.unpack_from("<I", data, pos + 28)[0]
        out.append(
            {
                "id": f[0],
                "sprite": f[1],
                "mov": f[2],
                "type": f[3],
                "flag": f[4],
                "script": f[5],
                "face": f[6],
                "x": f[12],
                "z": f[13],
                "y": y,
            }
        )
        pos += 32
    return out


def fmt_obj(o: dict[str, int]) -> str:
    face = FACES[o["face"]] if o["face"] < len(FACES) else str(o["face"])
    return (
        f"  obj {o['id']:2d}  ({o['x']:4d},{o['z']:3d})  face={face}  "
        f"sprite={o['sprite']:4d}  script={o['script']:5d}  "
        f"mov={o['mov']:2d} type={o['type']}"
    )


def main() -> int:
    subprocess.check_call(
        [sys.executable, str(ROOT / "tools/extract_zone_event_vanilla.py"), str(ZONE)]
    )

    print("=== ROUTE 44 zone_event NPCs (vanilla rom.nds extract) ===")
    print(
        "Note: x/z are world coords on the Johto outdoor matrix — NOT comparable to "
        "Route 42 numbers directly.\n"
        "Route 42 (member 041) uses x~430-500 z~166-184.\n"
        "Route 44 (member 090) uses x~1030-1050 z~406-477.\n"
    )

    for member in ("046", "090"):
        objs = parse_objects((ZONE / f"2_{member}").read_bytes())
        print(f"--- member {member} ({len(objs)} objects) ---")
        for o in sorted(objs, key=lambda row: (row["z"], row["x"])):
            print(fmt_obj(o))
        print()

    print(f"=== All zone_event members with objects in x={R44_X} z={R44_Z} ===")
    hits: list[tuple[str, dict[str, int]]] = []
    for path in sorted(ZONE.glob("2_*")):
        member = path.name[2:]
        try:
            objs = parse_objects(path.read_bytes())
        except Exception:
            continue
        for o in objs:
            if R44_X[0] <= o["x"] <= R44_X[1] and R44_Z[0] <= o["z"] <= R44_Z[1]:
                hits.append((member, o))

    for member, o in sorted(hits, key=lambda t: (t[1]["z"], t[1]["x"], t[0])):
        print(f"  member {member:>3s}  " + fmt_obj(o).strip())

    # Route 42 reference point
    r42 = parse_objects((ZONE / "2_041").read_bytes())
    guru_x, guru_z = 426, 177
    print("\n=== Route 42 reference (member 041) ===")
    print(f"  Rod guru target (verified in-game): ({guru_x},{guru_z})")
    near = [o for o in r42 if abs(o["x"] - guru_x) <= 5 and abs(o["z"] - guru_z) <= 5]
    for o in sorted(near, key=lambda row: (row["z"], row["x"])):
        print(fmt_obj(o))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
