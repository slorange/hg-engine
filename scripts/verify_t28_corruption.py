#!/usr/bin/env python3
"""Verify T28 scr_seq patch preserves vanilla script entry points."""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLOT0_OFFSET = 101
ONLOAD_OFFSET = 38


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def main() -> int:
    vanilla_path = Path("build/a012_vanilla/2_930")
    if not vanilla_path.is_file():
        print("missing build/a012_vanilla/2_930")
        return 1

    vanilla = vanilla_path.read_bytes()
    if script_offset(vanilla, 0) != SLOT0_OFFSET:
        print("vanilla slot 0 not at 101")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "2_930"
        subprocess.check_call(
            [sys.executable, str(ROOT / "tools/patch_scr_seq_t28_rocket.py"), str(target)]
        )
        patched = target.read_bytes()

    ok = True
    for slot in range(9):
        before = script_offset(vanilla, slot)
        after = script_offset(patched, slot)
        if before != after:
            print(f"slot {slot}: offset moved {before} -> {after}")
            ok = False
        else:
            print(f"slot {slot}: entry @{before} unchanged")

    if patched[SLOT0_OFFSET : SLOT0_OFFSET + 8] != vanilla[SLOT0_OFFSET : SLOT0_OFFSET + 8]:
        print("slot 0 body modified")
        ok = False
    else:
        print(f"slot 0 body preserved: {patched[SLOT0_OFFSET : SLOT0_OFFSET + 8].hex()}")

    stub = patched[ONLOAD_OFFSET : ONLOAD_OFFSET + 8]
    print(f"OnLoad stub: {stub.hex()}")
    if struct.unpack_from("<H", stub, 0)[0] != 26:
        print("OnLoad missing call opcode")
        ok = False

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
