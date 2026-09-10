#!/usr/bin/env python3
import struct
from pathlib import Path


def decode(data: bytes, start: int, end: int) -> None:
    i = start
    while i < end:
        op = struct.unpack_from("<H", data, i)[0]
        i += 2
        if op == 0:
            print("  end")
            return
        if op == 30:
            f = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  setflag {f}")
        elif op == 31:
            f = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  clearflag {f}")
        elif op == 41:
            v = struct.unpack_from("<H", data, i)[0]
            val = struct.unpack_from("<H", data, i + 2)[0]
            i += 4
            print(f"  setvar {v:#x}={val}")
        elif op == 28:
            cond = data[i]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            i += 5
            print(f"  goto_if {cond} +{rel}")
        elif op == 17:
            v = struct.unpack_from("<H", data, i)[0]
            val = struct.unpack_from("<H", data, i + 2)[0]
            i += 4
            print(f"  cmp {v:#x}=={val}")
        elif op == 32:
            f = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  checkflag {f}")
        elif op == 45:
            msg = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  msg {msg}")
        else:
            print(f"  op {op} @{i - 2}")
            return


if __name__ == "__main__":
    gym = Path("build/a012/2_932").read_bytes()
    print("=== gym slot 1 from 10 ===")
    decode(gym, 10, 200)

    shop = Path("build/a012/2_937").read_bytes()
    print("=== shop flag checks ===")
    for fid in [498, 197, 369, 487]:
        pat = struct.pack("<H", 32) + struct.pack("<H", fid)
        idx = 0
        while True:
            i = shop.find(pat, idx)
            if i < 0:
                break
            print(f"  checkflag {fid} @{i}")
            idx = i + 1
