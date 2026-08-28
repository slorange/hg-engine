#!/usr/bin/env python3
"""Patch Magnet Train station scr_seq members: skip FLAG_RESTORED_POWER gates.

Goldenrod T25R0501 (893) and Saffron T11R0601 (834). Assumes Pass and Ticket
are already granted at Mom (OPENWORLD_STARTING_ITEMS); coord gates keep vanilla
HasItem ITEM_PASS checks.

Replaces each checkflag FLAG_RESTORED_POWER + goto_if(1) with an unconditional
goto to the same target (in-place; no scr_seq table rebuild).
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
ROM = ROOT / "rom.nds"
CONFIG = ROOT / "include/config.h"
VANILLA_DIR = ROOT / "build/a012_vanilla"
TRAIN_MEMBERS = (893, 834)

CHECKFLAG = 32
GOTO_IF = 28
GOTO = 22
FLAG_RESTORED_POWER = 280
MAX_TABLE_SCAN = 512


def openworld_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return re.search(r"^#define\s+OPENWORLD_STARTING_ITEMS\b", text, re.MULTILINE) is not None


def load_vanilla_member(index: int) -> bytearray:
    path = VANILLA_DIR / f"2_{index:03d}"
    if path.is_file():
        return bytearray(path.read_bytes())

    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and {path}")

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
            str(VANILLA_DIR),
            "-nf",
        ],
        cwd=ROOT,
    )
    if not path.is_file():
        raise FileNotFoundError(f"missing vanilla member {path}")
    return bytearray(path.read_bytes())


def find_power_checks(data: bytes) -> list[int]:
    pat = struct.pack("<HH", CHECKFLAG, FLAG_RESTORED_POWER)
    hits: list[int] = []
    i = 0
    while True:
        j = data.find(pat, i)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
    return hits


def patch_goto_if_set_to_goto(data: bytearray, off: int) -> int:
    """Replace checkflag+goto_if(1) with unconditional goto; return jump target."""
    if struct.unpack_from("<H", data, off)[0] != CHECKFLAG:
        raise ValueError(f"@{off}: expected checkflag")
    if struct.unpack_from("<H", data, off + 2)[0] != FLAG_RESTORED_POWER:
        raise ValueError(f"@{off}: expected FLAG_RESTORED_POWER")
    if struct.unpack_from("<H", data, off + 4)[0] != GOTO_IF:
        raise ValueError(f"@{off + 4}: expected goto_if")
    if data[off + 6] != 1:
        raise ValueError(f"@{off + 6}: expected goto_if condition 1")
    rel = struct.unpack_from("<i", data, off + 7)[0]
    target = off + 11 + rel
    new_rel = target - (off + 6)
    data[off : off + 10] = b"\x00\x00" * 5
    struct.pack_into("<H", data, off, GOTO)
    struct.pack_into("<i", data, off + 2, new_rel)
    return target


def patch_member(data: bytearray, index: int) -> list[tuple[int, int]]:
    checks = find_power_checks(data)
    if not checks:
        raise ValueError(f"2_{index:03d}: no FLAG_RESTORED_POWER checks found")
    applied: list[tuple[int, int]] = []
    for off in checks:
        target = patch_goto_if_set_to_goto(data, off)
        applied.append((off, target))
    if find_power_checks(data):
        raise ValueError(f"2_{index:03d}: FLAG_RESTORED_POWER checks remain after patch")
    return applied


def already_patched(data: bytes, vanilla: bytes, index: int) -> bool:
    if data == vanilla:
        return False
    if find_power_checks(data):
        return False
    expected = find_power_checks(vanilla)
    if not expected:
        return False
    for off in expected:
        if struct.unpack_from("<H", data, off)[0] != GOTO:
            return False
    return True


def patch_file(target: Path, index: int) -> None:
    vanilla = load_vanilla_member(index)
    expected = find_power_checks(vanilla)
    if not expected:
        raise ValueError(f"2_{index:03d}: vanilla has no FLAG_RESTORED_POWER checks")

    if target.is_file():
        current = target.read_bytes()
        if already_patched(current, vanilla, index):
            print(f"Magnet Train 2_{index:03d}: already patched in {target}")
            return
        if current != vanilla and find_power_checks(current):
            data = bytearray(current)
        else:
            data = bytearray(vanilla)
    else:
        data = bytearray(vanilla)

    applied = patch_member(data, index)
    if len(applied) != len(expected):
        raise ValueError(f"2_{index:03d}: patch count mismatch")
    target.write_bytes(data)
    sites = ", ".join(f"{off:#x}->{tgt:#x}" for off, tgt in applied)
    print(f"Magnet Train 2_{index:03d}: patched {len(applied)} power gate(s) in {target} ({sites})")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            f"usage: {argv[0]} <build/a012/2_893> [<build/a012/2_834> ...]",
            file=sys.stderr,
        )
        return 1

    targets = [Path(p) for p in argv[1:]]
    for target in targets:
        try:
            index = int(target.name.split("_", 1)[1])
        except (IndexError, ValueError) as exc:
            print(f"cannot parse scr_seq member index from {target.name}", file=sys.stderr)
            raise SystemExit(1) from exc
        if index not in TRAIN_MEMBERS:
            print(f"warning: {target.name} is not a known train member", file=sys.stderr)

        vanilla = load_vanilla_member(index)
        if not openworld_enabled():
            target.write_bytes(vanilla)
            print(f"OPENWORLD_STARTING_ITEMS disabled; left vanilla scr_seq in {target}")
            continue

        patch_file(target, index)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
