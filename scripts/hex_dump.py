#!/usr/bin/env python3
import sys
from pathlib import Path

for arg in sys.argv[1:]:
    data = Path(arg).read_bytes()
    print(f"{arg} ({len(data)}): {data.hex()}")
