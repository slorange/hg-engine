#!/usr/bin/env python3
"""Print scr_seq member script slot layout."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def main(argv: list[str]) -> int:
    path = Path(argv[1])
    data = path.read_bytes()
    count = 0
    pos = 0
    while pos + 2 <= len(data):
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            print(f"scrdef_end at {pos}, total scripts: {count}")
            break
        count += 1
        pos += 4
    else:
        print("scrdef_end not found")
        return 1

    print(f"file size: {len(data)}")
    end0 = script_offset(data, 0)
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else end0
        print(f"slot {i}: {start}-{end} ({end - start} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
