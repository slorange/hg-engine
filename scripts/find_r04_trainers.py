#!/usr/bin/env python3
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Picnicker Hope trainer script on Route 4 (from built 2_009 obj0).
ROUTE4_TRAINER_SCRIPT = 3151


def objects(data: bytes) -> list[tuple[int, int, int, int]]:
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    ob = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(ob):
        v = struct.unpack_from("<14H", data, pos)
        out.append((v[0], v[5], v[12], v[13]))
        pos += 32
    return out


def main() -> None:
    print(f"Searching script={ROUTE4_TRAINER_SCRIPT} (Route 4 Picnicker Hope):")
    for path in sorted((ROOT / "build/a032_vanilla").glob("2_*")):
        hits = [o for o in objects(path.read_bytes()) if o[1] == ROUTE4_TRAINER_SCRIPT]
        if hits:
            mid = int(path.name.split("_", 1)[1])
            print(f"  2_{mid:03d}: {hits}")


if __name__ == "__main__":
    main()
