#!/usr/bin/env python3
"""Restore overlay 53 Oak intro code to hg-engine baseline (no flow patches).

Fixes jump-table corruption from earlier bad patch attempts, reverts all
Oak intro flow patches, keeps SKIP_TUTORIAL_INFO byte at 0x16BA intact.
"""

from __future__ import annotations

import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "base/overlay/overlay_0053.bin"
REF_SNAPSHOT = ROOT / "build/overlay_0053_ref.bin"
Y9TABLE = ROOT / "base/overarm9.bin"
VANILLA_COMP = ROOT / "build/ov_rom/overlay_0053.bin"
ROM = ROOT / "rom.nds"
NDSTOOL = ROOT / "tools/ndstool"
OVERLAY_ID = 53

# Oak speech auxiliary dispatch table (halfword offsets, not Thumb code).
JUMP_TABLE_START = 0x1700
JUMP_TABLE_END = 0x1800

# hg-engine expanded overlay differs from vanilla HG at these halfwords only.
HG_ENGINE_JUMP_OVERRIDES: dict[int, bytes] = {
    0x1790: bytes.fromhex("3C0A"),
    0x17B0: bytes.fromhex("6420"),
}

# Flow patches to revert (file offset -> length), restored from vanilla when possible.
REVERT_RANGES: list[tuple[int, int]] = [
    (0x1D7C, 2),
    (0x1DAC, 4),
    (0x1EFE, 4),
    (0x201A, 2),
    (0x21FC, 2),
    (0x2200, 2),
]

# Thumb opcodes written by failed flow patches into the dispatch table.
JUMP_TABLE_GARBAGE = frozenset(
    {
        bytes.fromhex("0022"),  # movs r2, #0
        bytes.fromhex("0120"),  # movs r0, #1
        bytes.fromhex("5D20"),  # movs r0, #93
        bytes.fromhex("5E20"),  # movs r0, #94
        bytes.fromhex("6720"),  # movs r0, #103
    }
)


def ensure_vanilla_comp() -> bytes | None:
    if not VANILLA_COMP.is_file() and ROM.is_file() and NDSTOOL.is_file():
        VANILLA_COMP.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [str(NDSTOOL), "-x", str(ROM), "-y", str(VANILLA_COMP.parent)],
            check=False,
            capture_output=True,
        )
    if not VANILLA_COMP.is_file():
        return None
    try:
        import ndspy.codeCompression

        return ndspy.codeCompression.decompress(VANILLA_COMP.read_bytes())
    except Exception:
        return None


def jump_table_reference(van: bytes | None) -> bytes | None:
    if REF_SNAPSHOT.is_file():
        ref = REF_SNAPSHOT.read_bytes()
        if len(ref) >= JUMP_TABLE_END:
            return ref[JUMP_TABLE_START:JUMP_TABLE_END]
    if van is None or len(van) < JUMP_TABLE_END:
        return None
    table = bytearray(van[JUMP_TABLE_START:JUMP_TABLE_END])
    for off, hw in HG_ENGINE_JUMP_OVERRIDES.items():
        rel = off - JUMP_TABLE_START
        table[rel : rel + 2] = hw
    return bytes(table)


def restore_jump_table(data: bytearray, van: bytes | None) -> bool:
    ref = jump_table_reference(van)
    if ref is None:
        return False
    before = bytes(data[JUMP_TABLE_START:JUMP_TABLE_END])
    data[JUMP_TABLE_START:JUMP_TABLE_END] = ref
    return before != ref


def jump_table_garbage(data: bytes) -> list[int]:
    bad: list[int] = []
    end = min(JUMP_TABLE_END, len(data))
    for off in range(JUMP_TABLE_START, end, 2):
        hw = bytes(data[off : off + 2])
        if hw in JUMP_TABLE_GARBAGE:
            bad.append(off)
    return bad


def mark_overlay_uncompressed() -> None:
    with Y9TABLE.open("r+b") as table:
        table.seek(OVERLAY_ID * 0x20 + 0x1C)
        table.write(b"\x00\x00\x00\x00")


def save_reference_snapshot() -> None:
    """Call after armips/make.py, before Oak intro patches, to capture a clean JT."""
    if not OVERLAY.is_file():
        return
    REF_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OVERLAY, REF_SNAPSHOT)


def main() -> None:
    if not OVERLAY.is_file():
        print(f"missing {OVERLAY}", file=sys.stderr)
        sys.exit(1)

    van = ensure_vanilla_comp()
    data = bytearray(OVERLAY.read_bytes())
    reverted = 0

    if van:
        for off, size in REVERT_RANGES:
            if off + size <= len(van) and off + size <= len(data):
                data[off : off + size] = van[off : off + size]
                reverted += 1
    else:
        print("warning: vanilla overlay unavailable; only fixing jump table", file=sys.stderr)

    jt_changed = restore_jump_table(data, van)
    garbage = jump_table_garbage(data)
    if garbage:
        print(f"error: jump table still has garbage at {[hex(o) for o in garbage]}", file=sys.stderr)
        sys.exit(1)

    OVERLAY.write_bytes(data)
    mark_overlay_uncompressed()
    load = struct.unpack_from("<I", Y9TABLE.read_bytes(), OVERLAY_ID * 0x20 + 4)[0]
    print(
        f"restored overlay 53 baseline ({reverted} flow sites reverted"
        f"{', jump table restored' if jt_changed else ''})"
    )
    print(f"load addr 0x{load:08X}, size 0x{len(data):X}")


if __name__ == "__main__":
    main()
