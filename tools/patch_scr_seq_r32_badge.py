#!/usr/bin/env python3
"""Route 32 scr_seq member 232: disable Zephyr Badge gate scripts."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
GATE_NOP_ASM = ROOT / "armips/scr_seq/scr_seq_r32_gate_nop_patch.s"
GATE_NOP_BIN = ROOT / "build/r32_gate_nop_patch.bin"

# Verified offsets in vanilla member 232 (pret scr_seq_0232_R32).
GATE_SCRIPT_OFFSETS = (
    592,   # scriptId 2 — NPC talk, check_badge BADGE_ZEPHYR
    816,   # scriptId 3 — scrcmd_609 walk-past coord gate
)


def patch_at(data: bytearray, offset: int, patch: bytes, label: str) -> None:
    if offset + len(patch) > len(data):
        raise ValueError(f"{label}: patch at {offset} overflows file")
    if offset == 816 and data[offset : offset + 2] != struct.pack("<H", 609):
        raise ValueError(f"{label}: expected scrcmd_609 @ {offset}")
    if offset == 592 and data[offset : offset + 2] != struct.pack("<H", 73):
        raise ValueError(f"{label}: expected callstd @ {offset}")
    data[offset : offset + len(patch)] = patch
    print(f"patched {label} @{offset}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_232>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    GATE_NOP_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(GATE_NOP_ASM)])
    gate_nop = GATE_NOP_BIN.read_bytes()

    data = bytearray(target.read_bytes())
    for off in GATE_SCRIPT_OFFSETS:
        patch_at(data, off, gate_nop, f"gate@{off}")

    target.write_bytes(data)
    print(f"patched Route 32 badge gate scripts in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
