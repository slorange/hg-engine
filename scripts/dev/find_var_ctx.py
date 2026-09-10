#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

path = Path(sys.argv[1])
var = int(sys.argv[2], 0)
data = path.read_bytes()
pat = struct.pack("<H", var)
idx = 0
while True:
    i = data.find(pat, idx)
    if i < 0:
        break
    ctx = data[max(0, i - 4) : i + 8]
    print(f"@{i}: {ctx.hex()}")
    idx = i + 1
