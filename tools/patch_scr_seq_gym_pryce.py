#!/usr/bin/env python3
"""Patch Mahogany Gym Pryce (scr_seq 932): badge-count HM before TM grant.

Retail 932 layout must stay intact:
  slot 0 @ file 190 — ice puzzle + Pryce battle (do not rebuild offset table)
  slot 1 @ file 10  — short flag script

Leader defeat / badge / TM live in slot 0. Generic patch_slot1() breaks slot 0 entry.
We append HM+TM bytecode after the 528-byte retail blob and goto it from the
post-badge-fanfare site (replacing vanilla TM bytes only).
"""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

from patch_scr_seq_gym_falkner import ARMIPS, ROM, armips_args, config_flag

ROOT = Path(__file__).resolve().parents[1]
MEMBER_INDEX = 932
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
PYTHON = ROOT / ".venv/bin/python"
HM_EXT_ASM = ROOT / "armips/scr_seq/scr_seq_pryce_gym_hm_ext.s"
HM_EXT_BIN = ROOT / "build/pryce_gym_hm_ext.bin"

VANILLA_MEMBER_LEN = 528
PLAY_FANFARE = 78
WAIT_FANFARE = 79
SEQ_ME_BADGE = 1189
GOTO = 22
SCR_END = 2


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


def assert_vanilla_layout(vanilla: bytes) -> None:
    if len(vanilla) != VANILLA_MEMBER_LEN:
        raise ValueError(f"expected vanilla 932 size {VANILLA_MEMBER_LEN}, got {len(vanilla)}")
    rel0 = struct.unpack_from("<i", vanilla, 0)[0]
    rel1 = struct.unpack_from("<i", vanilla, 4)[0]
    if 4 + rel0 != 190 or 8 + rel1 != 10:
        raise ValueError(
            f"unexpected vanilla 932 layout (slot0@{4 + rel0}, slot1@{8 + rel1})"
        )


def find_post_badge_tm_start(vanilla: bytes) -> int:
    """First byte after SEQ_ME_BADGE play_fanfare + wait_fanfare in slot 0."""
    # Slot 0 entry is @190; scan byte-wise (retail ops are not always on even offsets).
    for i in range(190, len(vanilla) - 6):
        if struct.unpack_from("<H", vanilla, i)[0] != PLAY_FANFARE:
            continue
        if struct.unpack_from("<H", vanilla, i + 2)[0] != SEQ_ME_BADGE:
            continue
        j = i + 4
        if struct.unpack_from("<H", vanilla, j)[0] != WAIT_FANFARE:
            raise ValueError(f"expected wait_fanfare after badge fanfare @{i}")
        return j + 2
    raise ValueError("badge fanfare sequence not found in vanilla 932")


def make_goto_trampoline(from_offset: int, target_offset: int, pad_len: int) -> bytes:
    """Opcode 22 goto with 4-byte relative word (retail scr_seq branch format)."""
    if pad_len < 6:
        raise ValueError(f"trampoline pad too small ({pad_len})")
    after_instr = from_offset + 6
    rel = target_offset - after_instr
    out = bytearray(pad_len)
    struct.pack_into("<HI", out, 0, GOTO, rel)
    i = 6
    while i + 1 < pad_len:
        struct.pack_into("<H", out, i, SCR_END)
        i += 2
    if i < pad_len:
        out[i] = 0
    return bytes(out)


def patch_pryce_member(vanilla: bytes, hm_ext: bytes) -> bytes:
    assert_vanilla_layout(vanilla)
    tm_start = find_post_badge_tm_start(vanilla)
    if tm_start >= VANILLA_MEMBER_LEN:
        raise ValueError(f"TM patch start @{tm_start} beyond retail member")

    out = bytearray(vanilla)
    ext_start = VANILLA_MEMBER_LEN
    pad_len = VANILLA_MEMBER_LEN - tm_start
    out[tm_start:VANILLA_MEMBER_LEN] = make_goto_trampoline(tm_start, ext_start, pad_len)
    out.extend(hm_ext)
    return bytes(out)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    vanilla = bytes(load_vanilla_member())

    if not config_flag("GYM_BADGE_COUNT_FIELD_REWARDS"):
        target.write_bytes(vanilla)
        print(f"GYM_BADGE_COUNT_FIELD_REWARDS disabled; left vanilla scr_seq in {target}")
        return 0

    HM_EXT_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), *armips_args(), str(HM_EXT_ASM)])
    hm_ext = HM_EXT_BIN.read_bytes()
    if not hm_ext:
        raise ValueError(f"empty HM extension blob {HM_EXT_BIN}")

    patched = patch_pryce_member(vanilla, hm_ext)
    target.write_bytes(patched)
    tm_start = find_post_badge_tm_start(vanilla)
    print(
        f"patched Pryce gym in {target} ({len(patched)} bytes, "
        f"retail {VANILLA_MEMBER_LEN}b preserved, goto @{tm_start}->528, "
        f"hm_ext={len(hm_ext)}b)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
