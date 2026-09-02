#!/usr/bin/env python3
"""Patch overlay 53 Oak intro: skip filler msgs, skip gender/name confirms."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.restore_overlay53_baseline import (  # noqa: E402
    ensure_vanilla_comp,
    jump_table_garbage,
    restore_jump_table,
)

CONFIG = ROOT / "include/config.h"
OVERLAY = ROOT / "base/overlay/overlay_0053.bin"
Y9TABLE = ROOT / "base/overarm9.bin"
VANILLA_COMP = ROOT / "build/ov_rom/overlay_0053.bin"
OVERLAY_ID = 53

# file offset -> bytes (thumb), verified against overlay 53 @ load 0x021E5900
PATCHES: dict[int, bytes] = {
    # Skip state 49 (msg 6 ".") by going straight to state 50 after the drill line
    0x1D7C: bytes.fromhex("3220"),
    # Skip PrintDialogMsg for msg 34: movs r0, #1; b.n over the bl to cmp
    0x1DAC: bytes.fromhex("0120 E7FF"),
    # Skip PrintDialogMsg for msg 36
    0x1EFE: bytes.fromhex("0120 E7FF"),
    # After gender portrait: state 94 (name prompt) instead of 67 (Boy?/Girl? confirm)
    0x201A: bytes.fromhex("5E20"),
    # After naming: state 103 (good luck) instead of 97 (name confirm)
    0x21FC: bytes.fromhex("6720"),
    # Skip name-confirm setup still in the state 95 handler tail
    0x2200: bytes.fromhex("FBE0"),
}

MSG6_BL_OFF = 0x1D86
MSG6_BL_ORIG = bytes.fromhex("FEF749FD")


def skip_tutorial_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return bool(re.search(r"^#define\s+SKIP_TUTORIAL_INFO\b", text, re.MULTILINE))


def overlay_load_addr() -> int:
    table = Y9TABLE.read_bytes()
    off = OVERLAY_ID * 0x20 + 4
    return struct.unpack_from("<I", table, off)[0]


def mark_overlay_uncompressed() -> None:
    with Y9TABLE.open("r+b") as table:
        table.seek(OVERLAY_ID * 0x20 + 0x1C)
        table.write(b"\x00\x00\x00\x00")


def restore_msg6_bl(data: bytearray, van: bytes | None) -> None:
    if MSG6_BL_OFF + len(MSG6_BL_ORIG) > len(data):
        return
    if van is not None and MSG6_BL_OFF + len(MSG6_BL_ORIG) <= len(van):
        data[MSG6_BL_OFF : MSG6_BL_OFF + len(MSG6_BL_ORIG)] = van[
            MSG6_BL_OFF : MSG6_BL_OFF + len(MSG6_BL_ORIG)
        ]
        return
    data[MSG6_BL_OFF : MSG6_BL_OFF + len(MSG6_BL_ORIG)] = MSG6_BL_ORIG


def apply_patches() -> None:
    if not OVERLAY.is_file():
        raise FileNotFoundError(f"missing {OVERLAY}")

    van = ensure_vanilla_comp()
    data = bytearray(OVERLAY.read_bytes())
    jt_changed = restore_jump_table(data, van)
    garbage = jump_table_garbage(data)
    if garbage:
        raise RuntimeError(f"jump table still corrupt at {[hex(o) for o in garbage]}")

    restore_msg6_bl(data, van)

    for off, patch in PATCHES.items():
        if off + len(patch) > len(data):
            raise ValueError(f"patch at 0x{off:X} exceeds overlay size 0x{len(data):X}")
        data[off : off + len(patch)] = patch

    OVERLAY.write_bytes(data)
    mark_overlay_uncompressed()
    if jt_changed:
        print("restored jump table before applying flow patches")


def verify_patches() -> None:
    data = OVERLAY.read_bytes()
    failed = []
    for off, expected in PATCHES.items():
        got = data[off : off + len(expected)]
        if got != expected:
            failed.append((off, expected.hex(), got.hex()))
    if data[MSG6_BL_OFF : MSG6_BL_OFF + len(MSG6_BL_ORIG)] != MSG6_BL_ORIG:
        failed.append((MSG6_BL_OFF, MSG6_BL_ORIG.hex(), data[MSG6_BL_OFF : MSG6_BL_OFF + 4].hex()))
    garbage = jump_table_garbage(data)
    if garbage:
        failed.append((garbage[0], "no garbage", data[garbage[0] : garbage[0] + 2].hex()))
    if failed:
        for off, exp, got in failed:
            print(f"FAIL 0x{off:X}: expected {exp} got {got}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if not skip_tutorial_enabled():
        print("SKIP_TUTORIAL_INFO off; leaving overlay 53 vanilla")
        return

    apply_patches()
    verify_patches()
    load = overlay_load_addr()
    print(f"patched Oak intro in overlay 53 (load 0x{load:08X}, {len(PATCHES)} sites)")


if __name__ == "__main__":
    main()
