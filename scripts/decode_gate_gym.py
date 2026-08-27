#!/usr/bin/env python3
"""Decode scr_seq 231 (R43 gate) and T28 slot1 coord script."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def script_offset(data: bytes, index: int) -> int:
    return index * 4 + 4 + struct.unpack_from("<i", data, index * 4)[0]


def scr_count(data: bytes) -> int:
    pos = 0
    n = 0
    while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        n += 1
        pos += 4
    return n


def disasm(data: bytes, start: int, limit: int = 400) -> None:
    i = start
    end = min(len(data), start + limit)
    while i < end:
        op = struct.unpack_from("<H", data, i)[0]
        pos = i
        i += 2
        if op in (0, 2):
            print(f"  @{pos}: {'end' if op == 0 else 'scr_end'}")
            return
        if op == 30:
            print(f"  @{pos}: setflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 31:
            print(f"  @{pos}: clearflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 32:
            print(f"  @{pos}: checkflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 41:
            v, vv = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  @{pos}: setvar {v:#x}={vv}")
        elif op == 17:
            v, vv = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  @{pos}: cmpvar {v:#x}=={vv}")
        elif op == 28:
            c = data[i]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            i += 5
            print(f"  @{pos}: goto_if cond={c} rel={rel} -> {i+rel}")
        elif op == 45:
            print(f"  @{pos}: msg {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 68:
            amt = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: hasenoughmoney {amt}")
        elif op == 69:
            amt = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: submoney {amt}")
        elif op == 73:
            print(f"  @{pos}: callstd {struct.unpack_from('<H', data, i)[0] if i+2<=len(data) else 0}")
            i += 2
        else:
            extra = data[i : i + 8].hex()
            print(f"  @{pos}: op {op} extra={extra}")
            return


def main() -> None:
    d231 = (ROOT / "build/a012/2_231").read_bytes()
    print("=== scr_seq 231 R43R0101 ===")
    for s in range(scr_count(d231)):
        off = script_offset(d231, s)
        print(f"\n-- slot {s} (scriptId {s+1}) @ {off} --")
        disasm(d231, off)

    d256 = (ROOT / "build/a012/2_256").read_bytes()
    print("\n=== scr_seq 256 R43R0201 ===")
    for s in range(min(scr_count(d256), 4)):
        off = script_offset(d256, s)
        print(f"\n-- slot {s} @ {off} --")
        disasm(d256, off, 200)

    d930 = (ROOT / "build/a012/2_930").read_bytes()
    print("\n=== T28 slot1 coord script (scriptId 2) ===")
    disasm(d930, script_offset(d930, 1), 200)

    print("\n=== T28 slot2 gym blocker talk (scriptId 3) ===")
    disasm(d930, script_offset(d930, 2), 80)

    d937 = (ROOT / "build/a012/2_937").read_bytes()
    print("\n=== shop 937 slot1 ===")
    disasm(d937, script_offset(d937, 1), 80)

    # search 1000 in 231
    for pat in [b"\xe8\x03", b"\x03\xe8"]:
        idx = d231.find(pat)
        if idx >= 0:
            print(f"\n231 found 1000 pattern @ {idx}: {d231[idx-4:idx+6].hex()}")


if __name__ == "__main__":
    main()
