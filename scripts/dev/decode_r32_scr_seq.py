#!/usr/bin/env python3
"""Decode scr_seq Route 32 member 225 gate scripts."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

OPS = {
    0: "end",
    2: "scr_end",
    17: "cmpvar",
    28: "goto_if",
    30: "setflag",
    31: "clearflag",
    32: "checkflag",
    45: "npc_msg",
    101: "hide_person",
    102: "show_person",
    294: "check_badge",
    296: "count_badges",
    609: "scrcmd_609",
}


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def find_scrdef_end(data: bytes) -> int:
    pos = 0
    while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        pos += 4
    return pos


def decode(data: bytes, start: int, end: int, label: str) -> None:
    print(f"\n=== {label} @{start}-{end} ({end-start}b) ===")
    i = start
    n = 0
    while i < end and n < 50:
        op = struct.unpack_from("<H", data, i)[0]
        pos = i
        i += 2
        n += 1
        name = OPS.get(op, str(op))
        if op in (0, 2):
            print(f"  @{pos}: {name}")
            return
        if op == 294:
            badge, var = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  @{pos}: check_badge {badge} var {var}")
        elif op == 296:
            var = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: count_badges var {var}")
        elif op in (30, 31, 32, 101, 102):
            arg = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: {name} {arg}")
        elif op == 17:
            var, val = struct.unpack_from("<HI", data, i)
            i += 6
            print(f"  @{pos}: cmpvar {var:#x}={val}")
        elif op == 45:
            msg = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  @{pos}: npc_msg {msg}")
        elif op == 28:
            cond = struct.unpack_from("<B", data, i)[0]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            i += 5
            print(f"  @{pos}: goto_if cond={cond} -> {pos+5+rel}")
        else:
            print(f"  @{pos}: op {name}")
            return


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "build/a012/2_225")
    data = path.read_bytes()
    fd = find_scrdef_end(data)
    count = fd // 4
    print(f"size={len(data)} slots={count} fd@{fd}")
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else fd
        print(f"slot {i} scriptId {i+1}: @{start} len {end-start}")
    for slot in range(min(count, 9)):
        start = script_offset(data, slot)
        end = script_offset(data, slot + 1) if slot + 1 < count else min(start + 200, len(data))
        if end <= start:
            end = min(start + 200, len(data))
        decode(data, start, end, f"slot {slot} scriptId {slot+1}")


if __name__ == "__main__":
    main()
