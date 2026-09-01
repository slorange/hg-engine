#!/usr/bin/env python3
"""Patch New Bark player house scr_seq 845: open-world grants in script 0."""

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
SCRIPT_SLOT = 0
MAX_TABLE_SCAN = 512


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def config_flag(name: str) -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(rf"^#define\s+{name}\b", text, re.MULTILINE) is not None


def armips_flags() -> list[str]:
    if config_flag("OPENWORLD_TESTING_GRANTS"):
        return ["-equ", "OPENWORLD_TESTING_GRANTS", "1"]
    return ["-equ", "OPENWORLD_TESTING_GRANTS", "0"]


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


def remap_vanilla_msg_indices(body: bytearray) -> None:
    """545.txt inserts six starter strings at index 9; shift vanilla npc_msg ids >= 9 by +6."""
    i = 0
    while i + 2 < len(body):
        if body[i] == 0x2D and body[i + 1] == 0x00:
            mid = body[i + 2]
            if mid >= 9:
                body[i + 2] = mid + 6
            i += 3
            continue
        i += 1


def patch_script0(data: bytearray, script0: bytes) -> None:
    scripts = extract_scripts(data)
    if SCRIPT_SLOT >= len(scripts):
        raise ValueError(f"script slot {SCRIPT_SLOT} missing (only {len(scripts)} scripts)")
    for idx in range(len(scripts)):
        if idx == SCRIPT_SLOT:
            scripts[idx] = script0
        else:
            remapped = bytearray(scripts[idx])
            remap_vanilla_msg_indices(remapped)
            scripts[idx] = bytes(remapped)
    rebuilt = build_scr_seq(scripts, scrdef_word(data))
    data[:] = rebuilt


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    vanilla = load_vanilla_member()
    if not openworld_enabled():
        target.write_bytes(vanilla)
        print(f"OPENWORLD_STARTING_ITEMS disabled; left vanilla scr_seq in {target}")
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
        f"{len(script0)}-byte script0, rebuilt offset table)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
