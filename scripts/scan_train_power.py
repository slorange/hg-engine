#!/usr/bin/env python3
"""Scan train scr_seq members for FLAG_RESTORED_POWER (280) checks."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKFLAG = 32
GOTO_IF = 28
GOTO = 22
END = 2
FLAG_RESTORED_POWER = 280


def script_offset(data: bytes, index: int) -> int:
    wp = index * 4
    rel = struct.unpack_from("<i", data, wp)[0]
    return wp + 4 + rel


def find_slot(data: bytes, off: int, count: int) -> tuple[int, int] | None:
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else len(data)
        if start <= off < end:
            return i, off - start
    return None


def patch_goto_if_set_to_goto(data: bytearray, off: int) -> None:
    """Replace checkflag+goto_if(1) with unconditional goto to same target."""
    if struct.unpack_from("<H", data, off)[0] != CHECKFLAG:
        raise ValueError(f"@{off}: expected checkflag")
    if struct.unpack_from("<H", data, off + 2)[0] != FLAG_RESTORED_POWER:
        raise ValueError(f"@{off}: expected flag 280")
    if struct.unpack_from("<H", data, off + 4)[0] != GOTO_IF:
        raise ValueError(f"@{off+4}: expected goto_if")
    if data[off + 6] != 1:
        raise ValueError(f"@{off+6}: expected condition 1")
    rel = struct.unpack_from("<i", data, off + 7)[0]
    target = off + 11 + rel
    new_rel = target - (off + 6)
    data[off : off + 10] = b"\x00\x00" * 5
    struct.pack_into("<H", data, off, GOTO)
    struct.pack_into("<i", data, off + 2, new_rel)


def main() -> None:
    for mid in (893, 834):
        path = ROOT / f"build/a012_vanilla/2_{mid}"
        data = path.read_bytes()
        count = 0
        pos = 0
        while pos + 2 <= len(data) and pos < 512:
            if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
                count = pos // 4
                break
            pos += 4

        pat = struct.pack("<HH", CHECKFLAG, FLAG_RESTORED_POWER)
        hits: list[int] = []
        i = 0
        while True:
            j = data.find(pat, i)
            if j < 0:
                break
            hits.append(j)
            i = j + 1

        print(f"=== 2_{mid} ({len(data)} bytes, {count} scripts) ===")
        for off in hits:
            slot = find_slot(data, off, count)
            print(f"  checkflag280 @{off} slot={slot}")


if __name__ == "__main__":
    main()
