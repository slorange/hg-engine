#!/usr/bin/env python3
"""Append Kanto coastal ferry scripts to Pallet, Cinnabar, Route 19, and Route 20 scr_seq members."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMIPS = ROOT / "tools/armips"
PYTHON = ROOT / ".venv/bin/python"
ROM = ROOT / "rom.nds"
MAX_HEALTHY_SIZE = 8192
MAX_TABLE_SCAN = 512

PATCHES = [
    {
        "member": 735,
        "vanilla_count": 8,
        "sources": [
            (ROOT / "armips/scr_seq/scr_seq_t01_kanto_ferry_pallet.s", ROOT / "build/kanto_ferry_t01_pallet.bin"),
        ],
        "label": "Pallet Town",
    },
    {
        "member": 958,
        "vanilla_count": 6,
        "sources": [
            (ROOT / "armips/scr_seq/scr_seq_w19_kanto_ferry.s", ROOT / "build/kanto_ferry_w19.bin"),
        ],
        "label": "Route 19",
    },
    {
        "member": 960,
        "vanilla_count": 2,
        "sources": [
            (ROOT / "armips/scr_seq/scr_seq_w20_kanto_ferry.s", ROOT / "build/kanto_ferry_w20.bin"),
        ],
        "label": "Route 20",
    },
    {
        "member": 961,
        "vanilla_count": 2,
        "sources": [
            (ROOT / "armips/scr_seq/scr_seq_w21_kanto_ferry_cinnabar.s", ROOT / "build/kanto_ferry_w21_cinnabar.bin"),
        ],
        "label": "Route 21",
    },
    {
        "member": 815,
        "vanilla_count": 5,
        "sources": [
            (ROOT / "armips/scr_seq/scr_seq_t09_kanto_ferry_cinnabar.s", ROOT / "build/kanto_ferry_t09_cinnabar.bin"),
        ],
        "label": "Cinnabar Island",
    },
]


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


def load_vanilla_member(member: int) -> bytearray:
    vanilla_member = ROOT / f"build/a012_vanilla/2_{member:03d}"
    if vanilla_member.is_file():
        return bytearray(vanilla_member.read_bytes())

    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM} and {vanilla_member}")

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
        [py, str(ROOT / "tools/narcpy.py"), "extract", str(vanilla_narc), "-o", str(out_dir), "-nf"],
        cwd=ROOT,
    )
    if not vanilla_member.is_file():
        raise FileNotFoundError(f"missing vanilla member {vanilla_member}")
    return bytearray(vanilla_member.read_bytes())


def patch_member(target: Path, patch: dict) -> None:
    for asm, out in patch["sources"]:
        subprocess.check_call([str(ARMIPS), str(asm)])
        if not out.is_file():
            raise FileNotFoundError(out)

    vanilla = load_vanilla_member(patch["member"])
    scripts = extract_scripts(vanilla)
    if len(scripts) != patch["vanilla_count"]:
        raise ValueError(
            f"{patch['label']} member {patch['member']}: expected "
            f"{patch['vanilla_count']} vanilla scripts, got {len(scripts)}"
        )

    for _, out in patch["sources"]:
        scripts.append(out.read_bytes())

    data = build_scr_seq(scripts, scrdef_word(vanilla))
    if len(data) > MAX_HEALTHY_SIZE:
        raise ValueError(f"{patch['label']} patched scr_seq is unexpectedly large ({len(data)} bytes)")

    target.write_bytes(data)
    first_id = patch["vanilla_count"] + 1
    ids = list(range(first_id, first_id + len(patch["sources"])))
    print(
        f"{patch['label']} ferry script(s) patched into {target} "
        f"({len(data)} bytes, scriptIds {ids})"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 6:
        print(
            f"usage: {argv[0]} <2_735> <2_958> <2_960> <2_961> <2_815>",
            file=sys.stderr,
        )
        return 1

    targets = [Path(p) for p in argv[1:]]
    for target, patch in zip(targets, PATCHES, strict=True):
        if not target.is_file():
            print(f"missing {target}", file=sys.stderr)
            return 1
        patch_member(target, patch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
