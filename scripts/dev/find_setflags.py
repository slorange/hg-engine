#!/usr/bin/env python3
from pathlib import Path

flags = list(range(439, 445)) + [369, 487, 488, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 197]
for fid in flags:
    b = fid.to_bytes(2, "little")
    hits = [p.name for p in Path("build/a012").glob("2_*") if bytes([0x1E, 0x00]) + b in p.read_bytes()]
    if hits:
        print(f"setflag {fid}: {hits[:5]}")
