#!/usr/bin/env python3
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
for off in map(int, sys.argv[2:]):
    print(f"@{off}: {data[off-24:off+32].hex()}")
