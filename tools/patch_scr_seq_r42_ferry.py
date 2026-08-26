#!/usr/bin/env python3
"""Patch Route 42 ferry scripts into scr_seq member 252.

See documentation/HACK-NOTES.md § "Paid ferry / local bypass NPCs".
Copy this file when adding ferries on other maps; keep build_scr_seq() rebuild logic.
"""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
PYTHON = ROOT / ".venv/bin/python"
ROM = ROOT / "rom.nds"
MEMBER_INDEX = 252
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
PATCH_SOURCES = [
    (ROOT / "armips/scr_seq/scr_seq_r42_ferry_west.s", ROOT / "build/r42_ferry_west.bin"),
    (ROOT / "armips/scr_seq/scr_seq_r42_ferry_east.s", ROOT / "build/r42_ferry_east.bin"),
]

VANILLA_SCRIPT_COUNT = 6
WEST_SLOT = 6
EAST_SLOT = 7
MAX_HEALTHY_SIZE = 8192
MAX_TABLE_SCAN = 512


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
    fd_pos, count = find_scrdef_end(data)
    scripts: list[bytes] = []
    for i in range(count):
        start = script_offset(data, i)
        if i + 1 < count:
            end = script_offset(data, i + 1)
        else:
            end = len(data)
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
    return bytearray(VANILLA_MEMBER.read_bytes())


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_252>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    for asm, out in PATCH_SOURCES:
        subprocess.check_call([str(ARMIPS), str(asm)])
        if not out.is_file():
            print(f"missing {out}", file=sys.stderr)
            return 1

    vanilla = load_vanilla_member()
    west_patch = PATCH_SOURCES[0][1].read_bytes()
    east_patch = PATCH_SOURCES[1][1].read_bytes()

    scripts = extract_scripts(vanilla)
    if len(scripts) != VANILLA_SCRIPT_COUNT:
        raise ValueError(f"expected {VANILLA_SCRIPT_COUNT} vanilla scripts, got {len(scripts)}")

    scripts.extend([west_patch, east_patch])
    data = build_scr_seq(scripts, scrdef_word(vanilla))

    if len(data) > MAX_HEALTHY_SIZE:
        raise ValueError(f"patched scr_seq member is unexpectedly large ({len(data)} bytes)")

    target.write_bytes(data)
    print(
        "Route 42 ferry scripts patched into "
        f"{target} ({len(data)} bytes, scriptIds {WEST_SLOT + 1}, {EAST_SLOT + 1})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
