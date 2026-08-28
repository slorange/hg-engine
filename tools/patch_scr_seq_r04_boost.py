#!/usr/bin/env python3
"""Append Route 4 ledge-boost script to scr_seq member 178.

Route 4 ID cheat sheet (pret names in parentheses):
  MAP_R04 map header     = 12
  zone_event member      = 009  (009_R04.json) — NOT 178
  scr_seq member         = 178  (scr_seq_0178_R04.s) — NOT 009
  msg bank               = 328  (msg_0328_R04)
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
MEMBER_INDEX = 178
VANILLA_MEMBER = ROOT / f"build/a012_vanilla/2_{MEMBER_INDEX:03d}"
PATCH_ASM = ROOT / "armips/scr_seq/scr_seq_r04_boost.s"
PATCH_BIN = ROOT / "build/r04_boost.bin"

VANILLA_SCRIPT_COUNT = 1
BOOST_SLOT = 1
MAX_HEALTHY_SIZE = 4096
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER_INDEX}>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    PATCH_BIN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(ARMIPS), str(PATCH_ASM)])
    boost = PATCH_BIN.read_bytes()
    if not boost:
        raise ValueError(f"empty patch blob {PATCH_BIN}")

    vanilla = load_vanilla_member()
    scripts = extract_scripts(vanilla)
    if len(scripts) != VANILLA_SCRIPT_COUNT:
        raise ValueError(f"expected {VANILLA_SCRIPT_COUNT} vanilla scripts, got {len(scripts)}")

    scripts.append(boost)
    data = build_scr_seq(scripts, scrdef_word(vanilla))
    if len(data) > MAX_HEALTHY_SIZE:
        raise ValueError(f"patched scr_seq member is unexpectedly large ({len(data)} bytes)")

    target.write_bytes(data)
    print(
        f"Route 4 ledge boost script patched into {target} "
        f"({len(data)} bytes, scriptId {BOOST_SLOT + 1})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
