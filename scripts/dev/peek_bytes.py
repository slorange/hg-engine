#!/usr/bin/env python3
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = path.read_bytes()
for label, off in [(a, int(b)) for a, b in (x.split("@") for x in sys.argv[2:])]:
    off = int(off)
    print(f"--- {label} @{off} ---")
    print(data[max(0, off - 16) : off + 24].hex())

if __name__ == "__main__":
    pass
