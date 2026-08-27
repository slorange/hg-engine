#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
pos = 0
(bg_count,) = struct.unpack_from("<I", data, pos)
pos += 4
pos += bg_count * 20
(oc,) = struct.unpack_from("<I", data, pos)
pos += 4
for i in range(oc):
    vals = struct.unpack_from("<14H", data, pos)
    pos += 28
    pos += 4
    print(
        f"obj{i}: id={vals[0]} flag={vals[4]} script={vals[5]} "
        f"sprite={vals[1]} x={vals[12]} z={vals[13]}"
    )
