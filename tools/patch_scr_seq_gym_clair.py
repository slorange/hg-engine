#!/usr/bin/env python3
"""Blackthorn Gym Clair: fork trainer id + slot-13 Leader script (Rising Badge in gym).

Clair's NPC uses script 13 (see patch_zone_event_blackthorn_gym_clair.py). Vanilla
slot 0 uses trainer_battle(..., VAR_4094, 1, 0), which shows msg 631 and does not
continue into a givebadge tail in practice.
"""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

from patch_scr_seq_gym_falkner import ARMIPS, ROM, extract_scripts, patch_script_slot

ROOT = Path(__file__).resolve().parents[1]
MEMBER_INDEX = 938
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
SLOT13_ASM = ROOT / "armips/scr_seq/scr_seq_clair_gym_slot13.s"
SLOT13_BIN = ROOT / "build/clair_gym_slot13.bin"
PYTHON = ROOT / ".venv/bin/python"
TRAINER_BATTLE = 0x00D5
TRAINER_VANILLA_CLAIR = 39
TRAINER_FORK_CLAIR = 35
LEADER_SCRIPT_SLOT = 13


def load_vanilla_member(path: Path) -> bytearray:
    if path.is_file():
        return bytearray(path.read_bytes())
    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and {path}")
    vanilla_narc = ROOT / "build/vanilla_rom_root/a/0/1/2"
    if not vanilla_narc.is_file():
        raise FileNotFoundError(f"extract vanilla scr_seq first ({vanilla_narc})")
    py = str(PYTHON if PYTHON.is_file() else sys.executable)
    subprocess.check_call(
        [
            py,
            str(ROOT / "tools/narcpy.py"),
            "extract",
            str(vanilla_narc),
            "-o",
            str(ROOT / "build/a012_vanilla"),
            "-nf",
        ],
        cwd=ROOT,
    )
    if not path.is_file():
        raise FileNotFoundError(f"missing vanilla member {path}")
    return bytearray(path.read_bytes())


def replace_trainer_battle_ids(data: bytearray, old_id: int, new_id: int) -> int:
    count = 0
    i = 0
    while i + 7 < len(data):
        if data[i] == TRAINER_BATTLE & 0xFF and data[i + 1] == TRAINER_BATTLE >> 8:
            tid = data[i + 2] | (data[i + 3] << 8)
            if tid == old_id:
                struct.pack_into("<H", data, i + 2, new_id)
                count += 1
            i += 8
        else:
            i += 1
    return count


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX:03d}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if target.name != f"2_{MEMBER_INDEX:03d}":
        print(f"warning: expected 2_{MEMBER_INDEX:03d}, got {target.name}", file=sys.stderr)

    data = load_vanilla_member(VANILLA_MEMBER)
    tb_fix = replace_trainer_battle_ids(data, TRAINER_VANILLA_CLAIR, TRAINER_FORK_CLAIR)

    SLOT13_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(SLOT13_ASM)])
    slot13 = SLOT13_BIN.read_bytes()
    if not slot13:
        raise ValueError(f"empty {SLOT13_BIN}")

    patch_script_slot(data, LEADER_SCRIPT_SLOT, slot13)
    target.write_bytes(data)

    vanilla_940 = ROOT / "build/a012_vanilla/2_940"
    patched_940 = target.parent / "2_940"
    if vanilla_940.is_file() and patched_940.is_file():
        patched_940.write_bytes(vanilla_940.read_bytes())

    scripts = extract_scripts(data)
    print(
        f"patched {target}: Clair leader script slot {LEADER_SCRIPT_SLOT} "
        f"({len(slot13)} bytes); {tb_fix} trainer_battle "
        f"{TRAINER_VANILLA_CLAIR}->{TRAINER_FORK_CLAIR}; slot0={len(scripts[0])} bytes vanilla"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
