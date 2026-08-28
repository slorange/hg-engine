#!/usr/bin/env python3
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_R04 = 12
MAP_T05 = 53


def all_warps(data: bytes) -> list[tuple[int, int, int, int, int]]:
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    ob = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + ob * 32
    if pos + 4 > len(data):
        return []
    wa = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    out = []
    for _ in range(wa):
        if pos + 12 > len(data):
            break
        x, z, hdr, anc = struct.unpack_from("<HHHH", data, pos)
        y = struct.unpack_from("<I", data, pos + 8)[0]
        out.append((x, z, hdr, anc, y))
        pos += 12
    return out


def main() -> None:
    print("Cerulean maps (53) warps:")
    for mid in range(385, 400):
        path = ROOT / f"build/a032_vanilla/2_{mid:03d}"
        if not path.is_file():
            continue
        ws = all_warps(path.read_bytes())
        if ws:
            print(f"  2_{mid:03d}: {ws}")
    print("Warps to MAP_R04 from any member:")
    for path in sorted((ROOT / "build/a032_vanilla").glob("2_*")):
        mid = int(path.name.split("_", 1)[1])
        for w in all_warps(path.read_bytes()):
            if w[2] == MAP_R04:
                print(f"  2_{mid:03d}: {w}")


if __name__ == "__main__":
    main()
