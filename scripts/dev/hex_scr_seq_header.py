#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
print(f"file {len(data)} bytes")
for off in range(0, 48, 4):
    w = struct.unpack_from("<I", data, off)[0]
    h = struct.unpack_from("<H", data, off)[0]
    print(f"  @{off:02d}: word={w:08x} u16={h:04x}")

print("script0@", struct.unpack_from("<i", data, 0)[0] + 4)
for i in range(6):
    rel = struct.unpack_from("<i", data, i * 4)[0]
    print(f"slot{i} -> {i*4+4+rel}")
