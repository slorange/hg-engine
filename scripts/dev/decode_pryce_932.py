#!/usr/bin/env python3
"""Decode scr_seq 932 (Mahogany Gym) and scan goto targets."""
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
    73: "callstd?",
    213: "trainer_battle",
    294: "check_badge",
}


def scan_gotos(data: bytes, start: int, end: int) -> None:
    i = start
    while i < end - 2:
        op = struct.unpack_from("<H", data, i)[0]
        pos = i
        i += 2
        if op == 28 and i + 5 <= end:
            rel = struct.unpack_from("<i", data, i + 1)[0]
            target = pos + 7 + rel
            print(f"  goto_if @{pos} -> {target} (in-prefix={10 <= target < 190}, in-tail={190 <= target < 528})")
            i += 5
        elif op in (0, 2):
            break
        elif op in (30, 31, 32, 45, 294):
            i += 2
        elif op == 17:
            i += 6
        elif op == 213:
            i += 2
        else:
            i += 2


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "build/a012_vanilla/2_932")
    data = path.read_bytes()
    print(f"file {path} size={len(data)}")
    for i in range(3):
        rel = struct.unpack_from("<i", data, i * 4)[0]
        print(f"  word{i}: abs={i * 4 + 4 + rel}")
    print("\nGotos in [190,528) (ice entry region, vanilla layout):")
    scan_gotos(data, 190, min(528, len(data)))
    print("\nGotos in [10,190) (leader prefix, vanilla layout):")
    if len(data) >= 190:
        scan_gotos(data, 10, 190)
    if len(data) > 528:
        print("\nGotos in patched slot0 [10,348):")
        scan_gotos(data, 10, 348)
        print("\nGotos in patched slot1 [348,...] first 200b:")
        scan_gotos(data, 348, min(348 + 200, len(data)))


if __name__ == "__main__":
    main()
