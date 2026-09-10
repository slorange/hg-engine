#!/usr/bin/env python3
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE = ROOT / "build/a032"


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
                "type": f[3],
                "script": f[5],
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
    for member in ("041", "043"):
        objs = parse_objects((ZONE / f"2_{member}").read_bytes())
        print(f"=== member {member} ===")
        for o in sorted(objs, key=lambda r: (r["z"], r["x"])):
            print(
                f"  obj {o['id']:2d} ({o['x']:4d},{o['z']:3d}) "
                f"spr={o['sprite']:4d} script={o['script']:5d} type={o['type']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
