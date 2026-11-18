#!/usr/bin/env python3
"""Verify the relocated guru, route script preservation, and unchanged door warps."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/build"))
sys.path.insert(0, str(ROOT / "tools"))
from patch_zone_event_r32pc_rod_guru import parse_zone_event, pack_object
from rod_guru_patch_checks import validate_rod_guru_body
from patch_r32_outdoor_rod_guru import OBJECT_ID, SCRIPT_ID, X, Z
from patch_center_relearner import relearner_object


def main():
    for member in (33, 163):
        name = f"2_{member:03d}"
        vanilla = parse_zone_event((ROOT / "build/a032_vanilla" / name).read_bytes())
        current = parse_zone_event((ROOT / "build/a032" / name).read_bytes())
        assert current[0] == vanilla[0], f"{name}: background events changed"
        assert current[2] == vanilla[2], f"{name}: door warps changed"
        if member == 163:
            assert current[1] == [o for o in vanilla[1] if struct.unpack_from("<H", o)[0] not in (4, 5)] + [relearner_object()]
            assert current[3] == vanilla[3]
        else:
            assert current[1] == [o for o in vanilla[1] if struct.unpack_from("<H", o)[0] != 1] + [pack_object(OBJECT_ID, SCRIPT_ID, 0, X, Z)]
            assert not current[3], "Route 32 badge gate must stay removed"

    # Recreate the existing badge patch, then require all original bytecode and
    # pointers to survive the insertion of the eleventh script table entry.
    vanilla = bytearray((ROOT / "build/a012_vanilla/2_232").read_bytes())
    nop = (ROOT / "build/r32_gate_nop_patch.bin").read_bytes()
    for offset in (592, 816):
        vanilla[offset:offset + len(nop)] = nop
    current = (ROOT / "build/a012/2_232").read_bytes()
    assert current[44:len(vanilla) + 4] == vanilla[40:]
    for slot in range(10):
        assert struct.unpack_from("<i", current, slot * 4)[0] == struct.unpack_from("<i", vanilla, slot * 4)[0] + 4
    start = 44 + struct.unpack_from("<i", current, 40)[0]
    assert start == len(vanilla) + 4
    validate_rod_guru_body(current[start:], "Route 32 outdoor guru")
    messages = (ROOT / "data/text/380.txt").read_text(encoding="utf-8").splitlines()
    assert len(messages) == 25
    assert messages[20:] == (ROOT / "data/text/381.txt").read_text(encoding="utf-8").splitlines()[12:17]
    print(f"OK: one outdoor guru at ({X}, {Z}), script {SCRIPT_ID}; interior cleared; original scripts and warps preserved")


if __name__ == "__main__":
    main()
