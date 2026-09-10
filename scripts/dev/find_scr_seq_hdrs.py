#!/usr/bin/env python3
"""Find scr_seq init header members (contain InitScriptEntry pattern / FD13 at byte 8)."""
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "build/a012")
for path in sorted(root.glob("2_*")):
    data = path.read_bytes()
    if len(data) > 2000 or len(data) < 20:
        continue
    try:
        pos = 0
        count = 0
        while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
            count += 1
            pos += 4
            if pos > 64:
                break
        else:
            if count <= 3 and pos <= 16:
                print(f"{path.name}: {len(data)} bytes, {count} slots, fd@{pos}")
    except Exception:
        pass
