#!/usr/bin/env python3
"""Append one compiled script blob to a scr_seq member."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

MAX_TABLE_SCAN = 512


def find_scrdef_end(data: bytes) -> tuple[int, int]:
    pos = 0
    count = 0
    while pos + 2 <= len(data) and pos < MAX_TABLE_SCAN:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return pos, count
        count += 1
        pos += 4
    raise ValueError("scrdef_end not found")


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def extract_scripts(data: bytes) -> list[bytes]:
    _, count = find_scrdef_end(data)
    scripts: list[bytes] = []
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else len(data)
        scripts.append(data[start:end])
    return scripts


def build_scr_seq(script_bodies: list[bytes], scrdef: int) -> bytes:
    n = len(script_bodies)
    table_bytes = (n + 1) * 4
    script_start = table_bytes - 2

    abs_starts: list[int] = []
    pos = script_start
    for body in script_bodies:
        abs_starts.append(pos)
        pos += len(body)

    out = bytearray(table_bytes)
    for i in range(n):
        rel = abs_starts[i] - (i * 4 + 4)
        struct.pack_into("<i", out, i * 4, rel)
    struct.pack_into("<I", out, n * 4, scrdef)

    body = b"".join(script_bodies)
    out[script_start : script_start + len(body)] = body
    return bytes(out)


def append_script(data: bytearray, patch: bytes) -> int:
    fd_pos, count = find_scrdef_end(data)
    scrdef = struct.unpack_from("<I", data, fd_pos)[0]
    scripts = extract_scripts(data)
    scripts.append(patch)
    data[:] = build_scr_seq(scripts, scrdef)
    return count


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(f"usage: {argv[0]} <scr_seq_member> <patch.bin> <slot_name>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    patch = Path(argv[2]).read_bytes()
    data = bytearray(target.read_bytes())
    slot = append_script(data, patch)
    target.write_bytes(data)
    print(f"appended script slot {slot} to {target} ({len(patch)} bytes) as {argv[3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
