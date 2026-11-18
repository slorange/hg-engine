#!/usr/bin/env python3
"""Add the entrance Abra handler and native-map travel script."""
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from patch_zone_event_r32pc_rod_guru import parse_zone_event
from patch_r32_outdoor_rod_guru import write_events


def abra_objects():
    def obj(id, sprite, script, x, z):
        return struct.pack("<14HI", id, sprite, 14, 0, 0, script, 0, 0, 0, 0, 0, 0, x, z, 0)
    # SPRITE_MYSTERY_2 is the HGSS Psychic. Movement 14 forces north;
    # movement 15 forces south regardless of the initial direction field.
    return [obj(7, 351, 7, 10, 19), obj(8, 2500 + 63, 8, 11, 19)]


def patch_scripts(path):
    data = path.read_bytes()
    assert struct.unpack_from("<H", data, 24)[0] == 0xFD13, "run after crafting append"
    subprocess.check_call([str(ROOT / "tools/armips"), "armips/scr_seq/scr_seq_center_abra.s"], cwd=ROOT)
    bodies = [(ROOT / "build" / name).read_bytes() for name in ("center_abra.bin", "center_abra_mon.bin")]
    out = bytearray(32)
    for slot in range(6):
        struct.pack_into("<i", out, slot * 4, struct.unpack_from("<i", data, slot * 4)[0] + 8)
    start = len(data) + 8
    for slot, body in zip((6, 7), bodies):
        struct.pack_into("<i", out, slot * 4, start - (slot * 4 + 4))
        start += len(body)
    out.extend(data[24:])
    for body in bodies:
        out.extend(body)
    path.write_bytes(out)


def patch_events(path):
    bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
    for new in abra_objects():
        assert all(struct.unpack_from("<H", o)[0] != struct.unpack_from("<H", new)[0] for o in objects)
        assert all(struct.unpack_from("<HH", o, 24) != struct.unpack_from("<HH", new, 24) for o in objects)
        objects.append(new)
    write_events(path, bgs, objects, warps, coords)


if __name__ == "__main__":
    {"scripts": patch_scripts, "events": patch_events}[sys.argv[1]](Path(sys.argv[2]))
