#!/usr/bin/env python3
import struct
import sys
from pathlib import Path


def script_offset(data: bytes, index: int) -> int:
    wp = index * 4
    rel = struct.unpack_from("<i", data, wp)[0]
    return wp + 4 + rel


def find_scrdef_end(data: bytes) -> int:
    pos = 0
    while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        pos += 4
    return pos


def main() -> None:
    data = Path(sys.argv[1]).read_bytes()
    fd = find_scrdef_end(data)
    count = fd // 4
    print(f"scrdef_end={fd} count={count} size={len(data)}")
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else fd
        print(
            f"slot {i} (scriptId {i + 1}): {start}-{end} ({end - start}b) "
            f"head={data[start : start + 8].hex()}"
        )


if __name__ == "__main__":
    main()
