#!/usr/bin/env python3
import struct
import sys
from pathlib import Path


def script_offset(d: bytes, i: int) -> int:
    w = i * 4
    return w + 4 + struct.unpack_from("<i", d, w)[0]


def fd_pos(d: bytes) -> tuple[int, int]:
    pos = 0
    while struct.unpack_from("<H", d, pos)[0] != 0xFD13:
        pos += 4
    return pos, pos // 4


def main() -> None:
    v = Path(sys.argv[1]).read_bytes()
    p = Path(sys.argv[2]).read_bytes()
    fd_v, count_v = fd_pos(v)
    fd_p, count_p = fd_pos(p)
    for i in range(6):
        vs = script_offset(v, i)
        ve = script_offset(v, i + 1) if i + 1 < count_v else len(v)
        ps = script_offset(p, i)
        pe = script_offset(p, i + 1) if i + 1 < count_p else len(p)
        ok = "OK" if v[vs:ve] == p[ps:pe] else "BAD"
        print(f"slot {i}: {ok} v={ve - vs}b p={pe - ps}b")
    print("slot2 sign head v", v[script_offset(v, 2) : script_offset(v, 2) + 4].hex())
    print("slot2 sign head p", p[script_offset(p, 2) : script_offset(p, 2) + 4].hex())
    print("slot6 ferry head p", p[script_offset(p, 6) : script_offset(p, 6) + 4].hex())


if __name__ == "__main__":
    main()
