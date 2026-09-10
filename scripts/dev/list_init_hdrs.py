#!/usr/bin/env python3
import struct
from pathlib import Path

TYPES = {1: "OnFrame", 2: "OnTransition", 3: "OnResume", 4: "OnLoad"}


def parse_hdr(data: bytes) -> list[tuple[str, int]]:
    pos = 0
    entries = []
    while pos + 4 <= len(data):
        t, sid = struct.unpack_from("<HH", data, pos)
        if t == 0xFD13:
            break
        if t == 0 and sid == 0:
            break
        entries.append((TYPES.get(t, f"t{t}"), sid))
        pos += 4
    return entries


for path in sorted(Path("build/a012").glob("2_*")):
    data = path.read_bytes()
    if len(data) > 32:
        continue
    entries = parse_hdr(data)
    if any(k == "OnLoad" for k, _ in entries):
        print(f"{path.name} ({len(data)}): {entries}")
