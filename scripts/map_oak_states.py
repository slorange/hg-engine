#!/usr/bin/env python3
"""Map Oak intro jump table entries to handler addresses."""
from __future__ import annotations

import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOAD = 0x021E5900
TABLE = 0x1700

ov = (ROOT / "base/overlay/overlay_0053.bin").read_bytes()

# Table base used by switch: find via disasm - common pattern is add pc after ldrh
# Try: target = LOAD + TABLE + 4 + (sign_extend(halfword) << 1)  (thumb switch table)
# Or: target = handler_base + (halfword << 1)

for state in range(55, 75):
    off = TABLE + state * 2
    if off + 2 > len(ov):
        break
    hw = struct.unpack_from("<h", ov, off)[0]
    # thumb switch: addr = table_base + 4 + (hw << 1) where table_base is start of tbh
    rel = (TABLE + 4) + (hw * 2)
    va = LOAD + rel
    print(f"state {state:3d} @0x{off:04X} hw=0x{struct.unpack_from('<H', ov, off)[0]:04X} -> file 0x{rel:04X} va 0x{va:08X}")

PY
