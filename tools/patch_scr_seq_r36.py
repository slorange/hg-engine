#!/usr/bin/env python3
"""Patch Route 36 scr_seq member 243: hide Sudowoodo on map load."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR_SEQ_INDEX = 243
SCRIPT_SLOT = 10
PATCH_ASM = ROOT / "armips/scr_seq/scr_seq_r36_010_patch.s"
PATCH_BIN = ROOT / "build/r36_010_patch.bin"
ARMIPS = ROOT / "tools/armips"


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def patch_member(path: Path) -> None:
    data = bytearray(path.read_bytes())

    if struct.unpack_from("<H", data, 44)[0] != 0xFD13:
        raise ValueError(f"{path}: unexpected scrdef_end at offset 44")

    start = script_offset(data, SCRIPT_SLOT)
    end = script_offset(data, 0)
    if end <= start:
        raise ValueError(f"{path}: script {SCRIPT_SLOT} end ({end}) <= start ({start})")

    patch = PATCH_BIN.read_bytes()
    span = end - start
    if len(patch) > span:
        raise ValueError(f"patch ({len(patch)} bytes) exceeds script slot ({span} bytes)")

    data[start:end] = patch + bytes(span - len(patch))
    path.write_bytes(data)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_243>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    PATCH_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(PATCH_ASM)])

    patch_member(target)
    print(f"patched Sudowoodo OnLoad script in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
