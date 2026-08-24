#!/usr/bin/env python3
"""Smoke-test zone event encoding for R29R0101."""

import struct
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
json_path = root / "data" / "zone_event" / "130_R29R0101.json"
output_dir = root / "build" / "a032_test"

subprocess.check_call(
    [sys.executable, str(root / "tools" / "zone_event_enc.py"), str(json_path), str(output_dir)]
)

encoded = (output_dir / "2_130").read_bytes()
if len(encoded) != 120:
    print(f"unexpected size: {len(encoded)}")
    raise SystemExit(1)

coord_count = struct.unpack_from("<I", encoded, 100)[0]
if coord_count != 1:
    print(f"unexpected coord_count: {coord_count}")
    raise SystemExit(1)

scr, x, z, w, h, y, val, var = struct.unpack_from("<8H", encoded, 104)
if (scr, x, z, w, h, y, val, var) != (1, 2, 8, 7, 1, 0, 0, 0x400F):
    print(f"unexpected coord event: {(scr, x, z, w, h, y, val, var)}")
    raise SystemExit(1)

print("ZONE_EVENT_ENCODE_OK")
