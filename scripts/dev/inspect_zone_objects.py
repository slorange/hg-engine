#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = path.read_bytes()
pos = 0
bg = struct.unpack_from("<I", data, pos)[0]
pos += 4 + bg * 20
n = struct.unpack_from("<I", data, pos)[0]
pos += 4
for i in range(n):
    o = data[pos : pos + 32]
    pos += 32
    fields = struct.unpack_from("<14HI", o)
    print(
        f"obj {i}: id={fields[0]} spr={fields[1]} move={fields[2]} type={fields[3]} "
        f"flag={fields[4]} script={fields[5]} face={fields[6]} x={fields[12]} z={fields[13]}"
    )
