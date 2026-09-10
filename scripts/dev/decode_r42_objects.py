#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
(obj_count,) = struct.unpack_from("<I", data, pos - 4)
print(f"objects: {obj_count}")
for i in range(obj_count):
    vals = struct.unpack_from("<14H", data, pos)
    height = struct.unpack_from("<i", data, pos + 28)[0]
    print(
        f"  {i}: id={vals[0]} spr={vals[1]} mov={vals[2]} type={vals[3]} "
        f"scr={vals[5]} face={vals[6]} eye={vals[7]} x={vals[12]} y={vals[13]} h={height}"
    )
    pos += 32
