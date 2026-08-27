#!/usr/bin/env python3
"""Detailed decode of Route 32 scr_seq gate scripts."""
from __future__ import annotations

import struct
import sys
from pathlib import Path


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def decode_chunk(data: bytes, start: int, end: int, label: str) -> None:
    print(f"\n=== {label} @{start}-{end} ===")
    i = start
    while i + 1 < end and i < start + 300:
        op = struct.unpack_from("<H", data, i)[0]
        pos = i
        i += 2
        if op == 0:
            print(f"  @{pos}: end")
            return
        if op == 294:
            badge = struct.unpack_from("<H", data, i)[0]
            i += 4
            print(f"  @{pos}: check_badge {badge}")
        elif op == 296:
            i += 2
            print(f"  @{pos}: count_badges")
        elif op == 609:
            print(f"  @{pos}: scrcmd_609")
        elif op == 45:
            msg = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: npc_msg {msg}")
        elif op == 17:
            var, val = struct.unpack_from("<HI", data, i)
            i += 6
            print(f"  @{pos}: cmpvar {var:#x}={val}")
        elif op == 28:
            i += 5
            print(f"  @{pos}: goto_if")
        elif op == 30:
            flag = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: setflag {flag}")
        elif op == 101:
            pid = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: hide_person {pid}")
        elif op == 102:
            pid = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: show_person {pid}")
        elif op == 20:
            std = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: callstd {std}")
        elif op == 73:
            std = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: callstd {std}")
        else:
            print(f"  @{pos}: op {op} next={data[i:i+6].hex()}")


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "build/a012/2_225")
    data = path.read_bytes()
    for slot in range(9):
        start = script_offset(data, slot)
        end = script_offset(data, slot + 1) if slot + 1 < 9 else len(data)
        if end <= start:
            end = min(start + 250, len(data))
        decode_chunk(data, start, end, f"slot {slot} scriptId {slot+1}")


if __name__ == "__main__":
    main()
