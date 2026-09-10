#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

d = Path(sys.argv[1]).read_bytes()
pos = 4
bg = struct.unpack_from("<I", d, 0)[0]
pos += 4 + bg * 20
oc = struct.unpack_from("<I", d, pos)[0]
pos += 4
for i in range(oc):
    o = d[pos + i * 32 : pos + (i + 1) * 32]
    fields = struct.unpack_from("<14HI", o)
    print(
        f"obj{i}: id={fields[0]} sprite={fields[1]} flag={fields[4]} "
        f"script={fields[5]} x={fields[12]} z={fields[13]}"
    )
