#!/usr/bin/env python3
"""Verify Olivine rod guru object on zone_event member 074."""
import struct
import sys
from pathlib import Path

ROD_GURU_OBJECT_ID = 8
ROD_GURU_X = 273
ROD_GURU_Z = 248
ROD_GURU_SCRIPT_ID = 14
SPRITE_FISHING_2 = 347


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_074>", file=sys.stderr)
        return 1

    data = Path(argv[1]).read_bytes()
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4

    found = False
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        pos += 32
        if f[0] == ROD_GURU_OBJECT_ID:
            found = True
            if (
                f[1] != SPRITE_FISHING_2
                or f[2] != 15
                or f[3] != 0
                or f[5] != ROD_GURU_SCRIPT_ID
                or f[12] != ROD_GURU_X
                or f[13] != ROD_GURU_Z
            ):
                raise SystemExit(
                    f"FAIL: id={ROD_GURU_OBJECT_ID} spr={f[1]} mov={f[2]} type={f[3]} "
                    f"scr={f[5]} @({f[12]},{f[13]}) expected spr={SPRITE_FISHING_2} "
                    f"scr={ROD_GURU_SCRIPT_ID} @({ROD_GURU_X},{ROD_GURU_Z})"
                )
            print(
                f"OK: obj {ROD_GURU_OBJECT_ID} spr={f[1]} script={f[5]} "
                f"@({f[12]},{f[13]})"
            )

    if not found:
        raise SystemExit(f"FAIL: object id {ROD_GURU_OBJECT_ID} not found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
