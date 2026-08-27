#!/usr/bin/env python3
import struct
from pathlib import Path

d = Path("build/a012/2_930").read_bytes()
start = 38
i = start
while True:
    op = struct.unpack_from("<H", d, i)[0]
    i += 2
    if op == 2:
        print(f"patched OK, script length {i - start} bytes")
        break
    if op == 0:
        print(f"patched OK (scr_end), script length {i - start} bytes")
        break
    if op == 30:
        f = struct.unpack_from("<H", d, i)[0]
        i += 2
        print(f"setflag {f}")
    elif op == 31:
        f = struct.unpack_from("<H", d, i)[0]
        i += 2
        print(f"clearflag {f}")
    elif op == 41:
        v = struct.unpack_from("<H", d, i)[0]
        val = struct.unpack_from("<H", d, i + 2)[0]
        i += 4
        print(f"setvar {v:#x}={val}")
    else:
        print(f"unexpected op {op} @{i - 2}")
        break

patch = Path("build/t28_005_patch.bin")
if patch.exists():
    print(f"patch bin size: {patch.stat().st_size} bytes (slot span 773)")
