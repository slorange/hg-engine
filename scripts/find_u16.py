#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
needle = struct.pack("<H", int(sys.argv[2]))
idx = 0
while True:
    i = data.find(needle, idx)
    if i < 0:
        break
    print(f"@{i}: {data[i-4:i+16].hex()}")
    idx = i + 1
