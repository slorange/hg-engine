#!/usr/bin/env python3
"""Verify Route 44 rod guru object on zone_event member 043."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dump_member(data: bytes, label: str) -> None:
    pos = 0
    bg = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    found = False
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        if f[0] == 15:
            found = True
            if f[2] != 15 or f[3] != 0 or f[5] != 4 or f[12] != 568 or f[13] != 183:
                raise SystemExit(
                    f"FAIL {label}: id=15 mov={f[2]} type={f[3]} script={f[5]} "
                    f"x={f[12]} z={f[13]} (expected mov=15 type=0 script=4 at 568,183)"
                )
            print(
                f"  {label}: id=15 spr={f[1]} mov={f[2]} type={f[3]} "
                f"script={f[5]} x={f[12]} z={f[13]} face={f[6]}"
            )
        pos += 32
    if not found:
        raise SystemExit(f"FAIL: no obj 15 in {label}")


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build/a032/2_043"
    dump_member(target.read_bytes(), str(target))
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
