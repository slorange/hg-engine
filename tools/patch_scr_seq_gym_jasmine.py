#!/usr/bin/env python3
"""Patch Olivine Gym Jasmine (scr_seq 913): badge-count HM before TM grant."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from patch_scr_seq_gym_falkner import (
    ARMIPS,
    ROM,
    armips_args,
    config_flag,
    patch_script_slot,
)

ROOT = Path(__file__).resolve().parents[1]
MEMBER_INDEX = 913
SCRIPT_SLOT = 0
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
PYTHON = ROOT / ".venv/bin/python"
SLOT_ASM = ROOT / "armips/scr_seq/scr_seq_jasmine_gym_slot0.s"
SLOT_BIN = ROOT / "build/jasmine_gym_slot0.bin"


def load_vanilla_member() -> bytearray:
    if VANILLA_MEMBER.is_file():
        return bytearray(VANILLA_MEMBER.read_bytes())
    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and {VANILLA_MEMBER}")
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
    if not VANILLA_MEMBER.is_file():
        raise FileNotFoundError(f"missing vanilla member {VANILLA_MEMBER}")
    return bytearray(VANILLA_MEMBER.read_bytes())


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    vanilla = load_vanilla_member()

    if not config_flag("GYM_BADGE_COUNT_FIELD_REWARDS"):
        target.write_bytes(vanilla)
        print(f"GYM_BADGE_COUNT_FIELD_REWARDS disabled; left vanilla scr_seq in {target}")
        return 0

    SLOT_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), *armips_args(), str(SLOT_ASM)])
    slot_blob = SLOT_BIN.read_bytes()
    if not slot_blob:
        raise ValueError(f"empty slot blob {SLOT_BIN}")

    data = bytearray(vanilla)
    patch_script_slot(data, SCRIPT_SLOT, slot_blob)
    target.write_bytes(data)
    print(
        f"patched Jasmine gym slot {SCRIPT_SLOT} in {target} ({len(data)} bytes, "
        f"{len(slot_blob)}-byte leader script, badge-count HM table)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
