#!/usr/bin/env python3
"""Patch the player house intro and restore seated Mom's savings dialogue."""

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
MEMBER_INDEX = 845
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
SCRIPT0_ASM = ROOT / "armips/scr_seq/scr_seq_t20_mom_script0.s"
SCRIPT0_BIN = ROOT / "build/t20_mom_script0.bin"
MAX_TABLE_SCAN = 512


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def config_flag(name: str) -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(rf"^#define\s+{name}\b", text, re.MULTILINE) is not None


def config_define_int(name: str, default: int) -> int:
    text = CONFIG.read_text(encoding="utf-8")
    m = re.search(rf"^#define\s+{name}\s+(\d+)\b", text, re.MULTILINE)
    return int(m.group(1)) if m else default


def armips_flags() -> list[str]:
    flags: list[str] = []
    flags.extend(
        ["-equ", "OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS", "1" if openworld_enabled() else "0"]
    )
    flags.extend(
        ["-equ", "OPENWORLD_TESTING_GRANTS", "1" if config_flag("OPENWORLD_TESTING_GRANTS") else "0"]
    )
    flags.extend(
        [
            "-equ",
            "IMPLEMENT_ECOLOGY_GENERATION",
            "1" if config_flag("IMPLEMENT_ECOLOGY_GENERATION") else "0",
        ]
    )
    sweep = config_flag("OPENWORLD_STORY_FLAG_SWEEP")
    flags.extend(["-equ", "OPENWORLD_STORY_FLAG_SWEEP", "1" if sweep else "0"])
    if not sweep:
        flags.extend(["-equ", "OPENWORLD_STORY_FLAG_SWEEP_START", "0", "-equ", "OPENWORLD_STORY_FLAG_SWEEP_END", "0"])
    if sweep:
        start = config_define_int("OPENWORLD_STORY_FLAG_SWEEP_START", 100)
        end = config_define_int("OPENWORLD_STORY_FLAG_SWEEP_END", 399)
        flags.extend(
            [
                "-equ",
                "OPENWORLD_STORY_FLAG_SWEEP_START",
                str(start),
                "-equ",
                "OPENWORLD_STORY_FLAG_SWEEP_END",
                str(end),
            ]
        )
    return flags


def find_scrdef_end(data: bytes) -> tuple[int, int]:
    pos = 0
    count = 0
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
    starts = [script_offset(data, slot) for slot in range(count)]
    ordered = sorted(set(starts + [len(data)]))
    ends = dict(zip(ordered, ordered[1:]))
    return [data[start:ends[start]] for start in starts]


def load_vanilla_member() -> bytearray:
    if VANILLA_MEMBER.is_file():
        return bytearray(VANILLA_MEMBER.read_bytes())

    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and {VANILLA_MEMBER}")

    vanilla_root = ROOT / "build/vanilla_rom_root"
    vanilla_narc = vanilla_root / "a/0/1/2"
    if not vanilla_narc.is_file():
        raise FileNotFoundError(f"extract vanilla scr_seq first ({vanilla_narc})")

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
    return bytearray(VANILLA_MEMBER.read_bytes())


def patch_script0(data: bytearray, script0: bytes) -> None:
    if find_scrdef_end(data)[1] != 7 or script_offset(data, 1) != 0x126:
        raise ValueError("Unexpected player house script table")

    # Keep the original bytecode addresses: slot 6 branches back into the
    # original intro body, and the furniture entries sit before it in the table.
    if len(data) % 2:
        data.append(0)
    struct.pack_into("<i", data, 0, len(data) - 4)
    data.extend(script0)

    # The intro grants the S.S. Ticket and Pokégear. Skip the vanilla
    # referrals to Elm and go directly to Mom's savings conversation.
    dispatch = script_offset(data, 1)
    if data[dispatch:dispatch + 11] != bytes.fromhex("20 00 64 09 1c 00 01 2b 00 00 00"):
        raise ValueError("Unexpected seated Mom story check")
    struct.pack_into("<Hi", data, dispatch, 22, 0x205 - (dispatch + 6))

    # The open-world dialogue bank shifts the stock savings and furniture text
    # by 30. Patch the known command operands, including the local menu labels.
    savings_messages = {
        0x22B: 15, 0x237: 16, 0x259: 17, 0x266: 18, 0x275: 20,
        0x38D: 26, 0x398: 25, 0x3B5: 17, 0x3C2: 18, 0x3D5: 21,
        0x3EF: 24, 0x406: 23, 0x411: 21, 0x420: 22, 0x42F: 27, 0x43E: 28,
    }
    messages = savings_messages | {
        script_offset(data, slot) + 6: 33 + slot for slot in range(2, 6)
    }
    for offset, message in messages.items():
        if data[offset:offset + 3] != struct.pack("<HB", 45, message):
            raise ValueError(f"Unexpected player house dialogue at {offset:#x}")
        data[offset + 2] = message + 30

    for choice in range(4):
        offset = 0x288 + 8 * choice
        label = 29 + choice
        if data[offset:offset + 8] != struct.pack("<4H", 751, label, 255, choice):
            raise ValueError(f"Unexpected Mom savings menu choice {choice}")
        struct.pack_into("<H", data, offset + 2, label + 30)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    vanilla = load_vanilla_member()
    if not openworld_enabled():
        target.write_bytes(vanilla)
        print(f"OPENWORLD_STORY_SKIP_AND_STARTING_ITEMS disabled; left vanilla scr_seq in {target}")
        return 0

    SCRIPT0_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), *armips_flags(), str(SCRIPT0_ASM)])
    script0 = SCRIPT0_BIN.read_bytes()
    if not script0:
        raise ValueError(f"empty script0 blob {SCRIPT0_BIN}")

    data = bytearray(vanilla)
    patch_script0(data, script0)
    target.write_bytes(data)
    print(
        f"patched Mom script 0 in {target} ({len(data)} bytes, "
        f"{len(script0)}-byte intro, corrected seated Mom and furniture text)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
