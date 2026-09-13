#!/usr/bin/env python3
"""Patch Violet Gym Falkner (scr_seq 859): badge-count HM before TM grant.

Pilot for GYM_BADGE_COUNT_FIELD_REWARDS — replaces Leader script slot 1 only.
See documentation/HACK-NOTES.md and DESIGN-WORLD.md (HM progression).
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
PYTHON = ROOT / ".venv/bin/python"
ROM = ROOT / "rom.nds"
CONFIG = ROOT / "include/config.h"
MEMBER_INDEX = 859
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
SLOT1_ASM = ROOT / "armips/scr_seq/scr_seq_falkner_gym_slot1.s"
SLOT1_BIN = ROOT / "build/falkner_gym_slot1.bin"
SLOT2_ASM = ROOT / "armips/scr_seq/scr_seq_falkner_gym_slot2.s"
SLOT2_BIN = ROOT / "build/falkner_gym_slot2.bin"
SLOT3_ASM = ROOT / "armips/scr_seq/scr_seq_falkner_gym_slot3.s"
SLOT3_BIN = ROOT / "build/falkner_gym_slot3.bin"
SLOT4_ASM = ROOT / "armips/scr_seq/scr_seq_falkner_gym_slot4.s"
SLOT4_BIN = ROOT / "build/falkner_gym_slot4.bin"
SLOT5_ASM = ROOT / "armips/scr_seq/scr_seq_falkner_gym_slot5.s"
SLOT5_BIN = ROOT / "build/falkner_gym_slot5.bin"
SCRIPT_SLOT = 1
MAX_TABLE_SCAN = 512


def config_flag(name: str) -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(rf"^#define\s+{name}\b", text, re.MULTILINE) is not None


def armips_args() -> list[str]:
    return ["-equ", "GYM_BADGE_COUNT_FIELD_REWARDS", "1"]


def find_scrdef_end(data: bytes) -> tuple[int, int]:
    pos, count = 0, 0
    while pos + 2 <= len(data) and pos < MAX_TABLE_SCAN:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return pos, count
        count += 1
        pos += 4
    raise ValueError("scrdef_end not found")


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def extract_scripts(data: bytes) -> list[bytes]:
    _, count = find_scrdef_end(data)
    scripts: list[bytes] = []
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else len(data)
        scripts.append(data[start:end])
    return scripts


def scrdef_word(data: bytes) -> int:
    fd_pos, _ = find_scrdef_end(data)
    return struct.unpack_from("<I", data, fd_pos)[0]


def build_scr_seq(script_bodies: list[bytes], scrdef: int) -> bytes:
    n = len(script_bodies)
    table_bytes = (n + 1) * 4
    script_start = table_bytes - 2

    abs_starts: list[int] = []
    pos = script_start
    for body in script_bodies:
        abs_starts.append(pos)
        pos += len(body)

    out = bytearray(table_bytes)
    for i in range(n):
        rel = abs_starts[i] - (i * 4 + 4)
        struct.pack_into("<i", out, i * 4, rel)
    struct.pack_into("<I", out, n * 4, scrdef)

    body = b"".join(script_bodies)
    out[script_start : script_start + len(body)] = body
    return bytes(out)


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


def patch_script_slot(data: bytearray, slot_index: int, slot_blob: bytes) -> None:
    scripts = extract_scripts(data)
    if slot_index >= len(scripts):
        raise ValueError(f"script slot {slot_index} missing (only {len(scripts)} scripts)")
    vanilla_slot = scripts[slot_index]
    max_slot = max(len(vanilla_slot) * 8, 1200)
    if len(slot_blob) > max_slot:
        raise ValueError(
            f"slot {slot_index} grew suspiciously large "
            f"({len(slot_blob)} vs vanilla {len(vanilla_slot)}, max {max_slot})"
        )
    scripts[slot_index] = slot_blob
    rebuilt = build_scr_seq(scripts, scrdef_word(data))
    data[:] = rebuilt


def patch_slot1(data: bytearray, slot1: bytes) -> None:
    patch_script_slot(data, SCRIPT_SLOT, slot1)


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

    SLOT1_BIN.parent.mkdir(parents=True, exist_ok=True)
    for asm in (SLOT1_ASM, SLOT2_ASM, SLOT3_ASM, SLOT4_ASM, SLOT5_ASM):
        subprocess.check_call([str(ARMIPS), *armips_args(), str(asm)])

    slot_blobs = {
        1: SLOT1_BIN.read_bytes(),
        2: SLOT2_BIN.read_bytes(),
        3: SLOT3_BIN.read_bytes(),
        4: SLOT4_BIN.read_bytes(),
        5: SLOT5_BIN.read_bytes(),
    }
    for slot_index, blob in slot_blobs.items():
        if not blob:
            raise ValueError(f"empty slot {slot_index} blob")

    data = bytearray(vanilla)
    for slot_index, blob in slot_blobs.items():
        patch_script_slot(data, slot_index, blob)
    target.write_bytes(data)
    print(
        f"patched Falkner gym slots 1-5 in {target} ({len(data)} bytes, "
        f"slot1={len(slot_blobs[1])}b slot5={len(slot_blobs[5])}b elevator)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
