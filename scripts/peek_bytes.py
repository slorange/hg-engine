#!/usr/bin/env python3
import sys
from pathlib import Path

for label in sys.argv[1:]:
    data = Path(label).read_bytes()
    print(label, "bytes 20-45:", data[20:45].hex())
