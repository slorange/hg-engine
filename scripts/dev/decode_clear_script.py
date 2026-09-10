#!/usr/bin/env python3
import struct
from pathlib import Path

data = Path("build/a012/2_034").read_bytes()
# slot 1 start at 47 per broken dump - find setvar manually
for i in range(len(data)-6):
    if data[i:i+2] == b"\x29\x00" and struct.unpack_from("<H", data, i+2)[0] == 0x4077:
        val = struct.unpack_from("<H", data, i+4)[0]
        print(f"setvar 4077={val} @{i}")
        print(data[i:i+100].hex())

print("--- slot0 ---")
print(data[10:47].hex())
