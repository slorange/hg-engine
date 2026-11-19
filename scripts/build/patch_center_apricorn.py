#!/usr/bin/env python3
"""Replace the remaining Center gift giver with immediate Apricorn crafting."""
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from patch_zone_event_r32pc_rod_guru import parse_zone_event
from patch_r32_outdoor_rod_guru import write_events


def craft_objects(objects):
    result = []
    found = False
    for obj in objects:
        if struct.unpack_from("<H", obj)[0] == 6:
            obj = bytearray(obj)
            struct.pack_into("<H", obj, 8, 0)  # Always visible, including old saves.
            struct.pack_into("<H", obj, 10, 6) # Crafting script; keep original sprite.
            struct.pack_into("<H", obj, 4, 16) # Native stationary face-left behavior.
            struct.pack_into("<H", obj, 12, 2) # Initial facing: left.
            struct.pack_into("<HH", obj, 24, 13, 17) # Block approach to basement stairs.
            obj = bytes(obj)
            found = True
        result.append(obj)
    assert found, "Center gift giver object 6 missing"
    return result


def patch_scripts(path):
    data = path.read_bytes()
    assert struct.unpack_from("<H", data, 20)[0] == 0xFD13, "run after relearner append"
    subprocess.check_call([str(ROOT / "tools/armips"), "armips/scr_seq/scr_seq_center_apricorn.s"], cwd=ROOT)
    out = bytearray(24)
    for slot in range(5):
        struct.pack_into("<i", out, slot * 4, struct.unpack_from("<i", data, slot * 4)[0] + 4)
    struct.pack_into("<i", out, 20, len(data) - 20)
    out.extend(data[20:])
    out.extend((ROOT / "build/center_apricorn.bin").read_bytes())
    path.write_bytes(out)


def patch_events(path):
    bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
    write_events(path, bgs, craft_objects(objects), warps, coords)


if __name__ == "__main__":
    {"scripts": patch_scripts, "events": patch_events}[sys.argv[1]](Path(sys.argv[2]))
