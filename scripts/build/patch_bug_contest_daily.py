#!/usr/bin/env python3
"""Open both National Park reception gates and contest registration every day.

Patch in place: preserve all script pointers, daily-entry flags, and RTC behavior.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

# member, file offset, expected original bytes, replacement bytes
# Gate initialization takes the existing active-contest NPC configuration.
# Registration uses a local Tuesday selector for vanilla opponent initialization;
# this does not alter the calendar, timer, or once-per-day entry flag.
PATCHES = (
    (242, 0xF0, bytes.fromhex("e40100401100"), struct.pack("<Hi", 22, 0x101 - 0xF6)),
    (245, 0x0E, bytes.fromhex("e40100401100"), struct.pack("<Hi", 22, 0x1F - 0x14)),
    (151, 0x11F, bytes.fromhex("e40100401100004002001c00"),
     struct.pack("<HHHHi", 41, 0x4000, 2, 22, 0x130 - 0x12B)),
)


def patch_member(member: int, data: bytes, verify: bool = False) -> bytes:
    result = bytearray(data)
    for index, offset, original, replacement in PATCHES:
        if index != member:
            continue
        actual = data[offset:offset + len(original)]
        if verify:
            if actual != replacement:
                raise ValueError(f"member {member}: daily contest patch missing at {offset:#x}")
        elif actual == original:
            result[offset:offset + len(original)] = replacement
        elif actual != replacement:
            raise ValueError(f"member {member}: unexpected bytes at {offset:#x}: {actual.hex()}")
    assert len(result) == len(data)
    return bytes(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    for member, _, _, _ in PATCHES:
        path = args.directory / f"2_{member:03}"
        patched = patch_member(member, path.read_bytes(), args.verify)
        if not args.verify:
            path.write_bytes(patched)
    print("Bug-Catching Contest: daily gate setup and registration verified (151, 242, 245)")


if __name__ == "__main__":
    main()
