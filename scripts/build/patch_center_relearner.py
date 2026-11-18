#!/usr/bin/env python3
"""Append the shared Center's cash Move Relearner without relocating old code."""
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from patch_zone_event_r32pc_rod_guru import parse_zone_event
from patch_r32_outdoor_rod_guru import write_events

OBJECT_ID, SCRIPT_ID = 4, 5
X, Z = 4, 15


def relearner_object():
    # Match the actual Blackthorn Move Maniac sprite; stand facing south.
    return struct.pack("<14HI", OBJECT_ID, 332, 15, 0, 0, SCRIPT_ID,
                       0, 0, 0, 0, 0, 0, X, Z, 0)


def patch_scripts(path):
    data = path.read_bytes()
    assert struct.unpack_from("<H", data, 16)[0] == 0xFD13, "expected four original scripts"
    subprocess.check_call([str(ROOT / "tools/armips"), "armips/scr_seq/scr_seq_center_relearner.s"], cwd=ROOT)
    body = (ROOT / "build/center_relearner.bin").read_bytes()
    out = bytearray(20)
    for slot in range(4):
        struct.pack_into("<i", out, slot * 4, struct.unpack_from("<i", data, slot * 4)[0] + 4)
    struct.pack_into("<i", out, 16, len(data) - 16)
    out.extend(data[16:])
    out.extend(body)
    path.write_bytes(out)


def patch_events(path):
    bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
    assert all(struct.unpack_from("<H", o)[0] != OBJECT_ID for o in objects), "run after fisherman removal"
    assert all(struct.unpack_from("<HH", o, 24) != (X, Z) for o in objects), "NPC tile occupied"
    objects.append(relearner_object())
    write_events(path, bgs, objects, warps, coords)


if __name__ == "__main__":
    {"scripts": patch_scripts, "events": patch_events}[sys.argv[1]](Path(sys.argv[2]))
