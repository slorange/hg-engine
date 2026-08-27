#!/usr/bin/env python3
"""Patch Mahogany Town scr_seq member 930: skip rocket takeover on map load."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
PYTHON = ROOT / ".venv/bin/python"
ROM = ROOT / "rom.nds"
MEMBER_INDEX = 930
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
ONLOAD_OFFSET = 38
SLOT0_OFFSET = 101
PATCH_ASM = ROOT / "armips/scr_seq/scr_seq_t28_005_patch.s"
PATCH_BIN = ROOT / "build/t28_005_patch.bin"


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def load_vanilla_member() -> bytes:
    if VANILLA_MEMBER.is_file():
        data = VANILLA_MEMBER.read_bytes()
        if script_offset(data, 0) == SLOT0_OFFSET:
            return data

    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and uncorrupted {VANILLA_MEMBER}")

    vanilla_root = ROOT / "build/vanilla_rom_root"
    vanilla_narc = vanilla_root / "a/0/1/2"
    if not vanilla_narc.is_file():
        vanilla_root.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [
                str(ROOT / "tools/ndstool"),
                "-x",
                str(ROM),
                "-9",
                str(vanilla_root / "arm9.bin"),
                "-7",
                str(vanilla_root / "arm7.bin"),
                "-y9",
                str(vanilla_root / "overarm9.bin"),
                "-y7",
                str(vanilla_root / "overarm7.bin"),
                "-d",
                str(vanilla_root),
                "-y",
                str(vanilla_root / "overlay"),
                "-t",
                str(vanilla_root / "banner.bin"),
                "-h",
                str(vanilla_root / "header.bin"),
            ],
            cwd=ROOT,
        )

    out_dir = ROOT / "build/a012_vanilla"
    py = str(PYTHON if PYTHON.is_file() else sys.executable)
    subprocess.check_call(
        [
            py,
            str(ROOT / "tools/narcpy.py"),
            "extract",
            str(vanilla_narc),
            "-o",
            str(out_dir),
            "-nf",
        ],
        cwd=ROOT,
    )
    if not VANILLA_MEMBER.is_file():
        raise FileNotFoundError(f"missing vanilla member {VANILLA_MEMBER}")
    data = VANILLA_MEMBER.read_bytes()
    if script_offset(data, 0) != SLOT0_OFFSET:
        raise ValueError(f"{VANILLA_MEMBER}: unexpected slot 0 offset {script_offset(data, 0)}")
    return data


def patch_member(vanilla: bytes, patch: bytes) -> bytes:
    # Overlapping entry points (slot 5 @38, slot 0 @101): append patch, call from OnLoad.
    append_offset = len(vanilla)
    word_pos = ONLOAD_OFFSET + 2
    rel = append_offset - (word_pos - 4)
    stub = struct.pack("<HiH", 26, rel, 2)

    if ONLOAD_OFFSET + len(stub) > SLOT0_OFFSET:
        raise ValueError(
            f"OnLoad stub ({len(stub)} bytes) overlaps slot 0 entry @{SLOT0_OFFSET}"
        )

    data = bytearray(vanilla)
    data[ONLOAD_OFFSET : ONLOAD_OFFSET + len(stub)] = stub
    data.extend(patch)
    return bytes(data)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])

    PATCH_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(PATCH_ASM)])
    patch = PATCH_BIN.read_bytes()

    vanilla = load_vanilla_member()
    patched = patch_member(vanilla, patch)

    if script_offset(patched, 0) != SLOT0_OFFSET:
        raise ValueError("slot 0 offset moved after patch")
    if patched[SLOT0_OFFSET : SLOT0_OFFSET + 4] == b"\x00\x00\x00\x00":
        raise ValueError("slot 0 script looks zeroed")

    target.write_bytes(patched)
    print(f"patched Mahogany rocket-skip OnLoad in {target} ({len(patched)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
