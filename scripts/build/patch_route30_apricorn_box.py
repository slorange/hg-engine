#!/usr/bin/env python3
"""Skip the Route 30 outdoor Apricorn Box cutscene and advance its scene."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from append_scr_seq_script import script_offset


path = Path(sys.argv[1])
data = bytearray(path.read_bytes())
start = script_offset(data, 2)
scene_end = bytes.fromhex("1e006d0029008c4001000200")  # Box flag, next scene, end
tail = data.index(scene_end, start)
if data[start:start + 6] != bytes.fromhex("610260003301"):
    raise ValueError(f"{path}: unexpected Route 30 cutscene entry")
# Jump directly to SetVar VAR_SCENE_ROUTE_30_OW, 1; End.
struct.pack_into("<Hi", data, start, 22, tail + 4 - (start + 6))
path.write_bytes(data)
