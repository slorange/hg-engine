#!/usr/bin/env python3
"""Find scr_seq members containing a script command halfword."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cmd = int(sys.argv[1]) if len(sys.argv) > 1 else 293
needle = struct.pack("<H", cmd)
base = ROOT / "build/a012"
for path in sorted(base.glob("2_*")):
    data = path.read_bytes()
    if needle in data:
        print(f"{path.name}: cmd {cmd} at offsets {[hex(i) for i in range(len(data) - 1) if data[i : i + 2] == needle][:5]}")
