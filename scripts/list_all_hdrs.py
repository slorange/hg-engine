#!/usr/bin/env python3
from pathlib import Path
import struct

TYPES = {0: "OnLoad", 1: "OnTransition", 2: "OnFrame", 3: "OnWarp", 6: "?"}

for path in sorted(Path("build/a012").glob("2_*")):
    data = path.read_bytes()
    if len(data) > 64 or len(data) < 8:
        continue
    pos = 0
    entries = []
    while pos + 4 <= len(data):
        t, sid = struct.unpack_from("<HH", data, pos)
        if t == 0xFD13:
            break
        entries.append((TYPES.get(t, f"t{t}"), sid))
        pos += 4
    if entries:
        print(f"{path.name} ({len(data)}b): {entries}")
