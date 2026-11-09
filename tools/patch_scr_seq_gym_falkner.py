#!/usr/bin/env python3
"""Patch Violet Gym Falkner (scr_seq 859): badge-count HM before TM grant.

Pilot for GYM_BADGE_COUNT_FIELD_REWARDS — replaces Leader script slot 1 only.
See documentation/HACK-NOTES.md and documentation/DESIGN-WORLD.md (HM progression).
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
SCRIPT_TERMINATORS = (b"\x00\x00", b"\x02\x00")
# Guide hide flags + hide_person 1 (opcode 101) after violet_gym_init — init needs obj1 in zone_event.
OPENWORLD_ONLOAD_PREFIX = struct.pack("<HHHH", 30, 740, 30, 739)
HIDE_PERSON_1 = struct.pack("<HH", 101, 1)
VIOLET_GYM_INIT_OPCODE = 324
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
    # Vanilla slot bodies are often stored out of table order (e.g. 943: slot 0 after slot 1).
    _, count = find_scrdef_end(data)
    starts = [script_offset(data, i) for i in range(count)]
    scripts: list[bytes] = []
    for start in starts:
        end = min((s for s in starts if s > start), default=len(data))
        scripts.append(data[start:end])
    return scripts


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


def patch_slot0_openworld(data: bytearray) -> None:
    """Keep vanilla OnLoad (violet_gym_init + phone rematch); hide Sprout guide NPC."""
    scripts = extract_scripts(data)
    body = scripts[0]
    if len(body) < 2 or struct.unpack_from("<H", body, 0)[0] != VIOLET_GYM_INIT_OPCODE:
        raise ValueError("Falkner slot 0 must start with violet_gym_init (324)")
    patched = bytearray(OPENWORLD_ONLOAD_PREFIX)
    patched.extend(body[:2])
    patched.extend(HIDE_PERSON_1)
    patched.extend(body[2:])
    if len(patched) >= 2 and bytes(patched[-2:]) in SCRIPT_TERMINATORS:
        patched = patched[:-2] + HIDE_PERSON_1 + patched[-2:]
    else:
        patched.extend(HIDE_PERSON_1)
        patched.extend(b"\x02\x00")
    patch_script_slot(data, 0, bytes(patched))


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
    # Append and repoint only this slot: vanilla code is never moved, so cross-slot
    # relative jumps / movement pointers in other slots stay valid.
    new_start = len(data)
    data.extend(slot_blob)
    struct.pack_into("<i", data, slot_index * 4, new_start - (slot_index * 4 + 4))


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
    patch_slot0_openworld(data)
    for slot_index, blob in slot_blobs.items():
        patch_script_slot(data, slot_index, blob)
    target.write_bytes(data)
    print(
        f"patched Falkner gym slots 0-5 in {target} ({len(data)} bytes, "
        f"slot0 init+hide obj1 slot1={len(slot_blobs[1])}b slot4/5 elevator)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
