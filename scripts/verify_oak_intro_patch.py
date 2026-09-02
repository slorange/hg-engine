#!/usr/bin/env python3
"""Verify overlay 53 Oak intro patches from tools/patch_overlay_oak_intro.py."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATCHES: dict[int, bytes] = {
    0x1D7C: bytes.fromhex("3220"),
    0x1DAC: bytes.fromhex("0120E7FF"),
    0x1EFE: bytes.fromhex("0120E7FF"),
    0x201A: bytes.fromhex("5E20"),
    0x21FC: bytes.fromhex("6720"),
    0x2200: bytes.fromhex("FBE0"),
}

JUMP_TABLE: dict[int, bytes] = {
    0x1790: bytes.fromhex("3C0A"),
    0x17B0: bytes.fromhex("6420"),
}

MSG6_BL_OFF = 0x1D86
MSG6_BL_ORIG = bytes.fromhex("FEF749FD")


def main() -> None:
    ov_path = ROOT / "base/overlay/overlay_0053.bin"
    if not ov_path.is_file():
        print(f"missing {ov_path}", file=sys.stderr)
        sys.exit(1)

    data = ov_path.read_bytes()
    failed = False
    for off, expected in {**PATCHES, **JUMP_TABLE}.items():
        got = data[off : off + len(expected)]
        if got != expected:
            print(f"FAIL offset 0x{off:X}: expected {expected.hex()} got {got.hex()}")
            failed = True
        else:
            print(f"OK   offset 0x{off:X}: {expected.hex()}")

    got = data[MSG6_BL_OFF : MSG6_BL_OFF + len(MSG6_BL_ORIG)]
    if got != MSG6_BL_ORIG:
        print(f"FAIL offset 0x{MSG6_BL_OFF:X}: expected {MSG6_BL_ORIG.hex()} got {got.hex()}")
        failed = True
    else:
        print(f"OK   offset 0x{MSG6_BL_OFF:X}: {MSG6_BL_ORIG.hex()} (msg6 bl restored)")

    if failed:
        sys.exit(1)
    print("Oak intro overlay patches verified.")


if __name__ == "__main__":
    main()
