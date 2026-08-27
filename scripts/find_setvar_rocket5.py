#!/usr/bin/env python3
from pathlib import Path

var = 0x4077
for val in range(0, 8):
    needle = bytes([0x29, 0x00]) + var.to_bytes(2, "little") + val.to_bytes(2, "little")
    hits = [p.name for p in Path("build/a012").glob("2_*") if needle in p.read_bytes()]
    if hits:
        print(f"setvar {var:#06x}={val}: {hits}")
