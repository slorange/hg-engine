#!/usr/bin/env python3
"""Move the Route 32 Center rod guru outdoors, preserving existing route scripts."""
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from patch_zone_event_r32pc_rod_guru import parse_zone_event, pack_object

OBJECT_ID = 19
SCRIPT_ID = 11
X, Z = 466, 419  # Beside the Center door (468, 419), clear of the exit.


def patch_scripts(target: Path) -> None:
    data = target.read_bytes()
    if struct.unpack_from("<H", data, 40)[0] != 0xFD13:
        raise ValueError("expected ten Route 32 scripts; run after vanilla extraction/badge patch")
    subprocess.check_call([str(ROOT / "tools/armips"), "armips/scr_seq/scr_seq_r32pc_rod_guru.s"], cwd=ROOT)
    body = (ROOT / "build/r32pc_rod_guru.bin").read_bytes()
    from rod_guru_patch_checks import validate_rod_guru_body
    validate_rod_guru_body(body, "Route 32 outdoor rod guru")
    # Keep the entire original body together: this member's script pointers are
    # not sorted, and scripts share relative branches/calls and movement data.
    out = bytearray(44)
    for slot in range(10):
        struct.pack_into("<i", out, slot * 4, struct.unpack_from("<i", data, slot * 4)[0] + 4)
    struct.pack_into("<i", out, 40, len(data) - 40)
    out.extend(data[40:])
    out.extend(body)
    assert out[44:44 + len(data) - 40] == data[40:]
    target.write_bytes(out)


def patch_events(directory: Path) -> None:
    route = directory / "2_033"
    bgs, objects, warps, coords = parse_zone_event(route.read_bytes())
    if any(struct.unpack_from("<H", obj)[0] == OBJECT_ID for obj in objects):
        raise ValueError("outdoor rod guru object ID already occupied")
    if any(struct.unpack_from("<HH", obj, 24) == (X, Z) for obj in objects):
        raise ValueError("outdoor rod guru tile already occupied")
    objects.append(pack_object(OBJECT_ID, SCRIPT_ID, 0, X, Z))
    write_events(route, bgs, objects, warps, coords)
    interior = directory / "2_163"
    bgs, objects, warps, coords = parse_zone_event(interior.read_bytes())
    # Retain the existing removal of the Apricorn NPC; remove the fisherman too.
    objects = [obj for obj in objects if struct.unpack_from("<H", obj)[0] not in (4, 5)]
    write_events(interior, bgs, objects, warps, coords)


def write_events(path, bgs, objects, warps, coords):
    path.write_bytes(struct.pack("<I", len(bgs) // 20) + bgs
                     + struct.pack("<I", len(objects)) + b"".join(objects)
                     + struct.pack("<I", len(warps) // 12) + warps
                     + struct.pack("<I", len(coords) // 16) + coords)


if __name__ == "__main__":
    if sys.argv[1] == "scripts":
        patch_scripts(Path(sys.argv[2]))
    elif sys.argv[1] == "events":
        patch_events(Path(sys.argv[2]))
    else:
        raise SystemExit("usage: patch_r32_outdoor_rod_guru.py scripts MEMBER | events DIRECTORY")
