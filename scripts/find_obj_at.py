#!/usr/bin/env python3
"""Find zone_event objects near a world coordinate."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse(data: bytes) -> list[list[int]]:
    if len(data) < 8:
        return []
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    if pos + 4 > len(data):
        return []
    ob = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    objs: list[list[int]] = []
    for _ in range(ob):
        if pos + 32 > len(data):
            break
        objs.append(list(struct.unpack_from("<14H", data, pos)))
        pos += 32
    return objs


def main() -> None:
    x = int(sys.argv[1]) if len(sys.argv) > 1 else 277
    z = int(sys.argv[2]) if len(sys.argv) > 2 else 177
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    root = Path(sys.argv[4]) if len(sys.argv) > 4 else ROOT / "build/a032_vanilla"

    for p in sorted(root.glob("2_*")):
        for f in parse(p.read_bytes()):
            if abs(f[12] - x) <= tol and abs(f[13] - z) <= tol:
                print(
                    f"{p.name} id={f[0]} spr={f[1]} scr={f[5]} "
                    f"flag={f[4]} @({f[12]},{f[13]})"
                )


if __name__ == "__main__":
    main()
