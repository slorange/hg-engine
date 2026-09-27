#!/usr/bin/env python3
"""Verify SS Aqua pier + gangplank in-place patches."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

GET_WEEKDAY = bytes([0xE4, 0x01])
GOTO_OP = 22
GOTO_IF = 28
CHECKFLAG = 32
SETFLAG = 30
CLEARFLAG = 31
FLAG_BOAT_ARRIVED = 235

PIER_CHECKS = (
    (152, 2, 458, 971, "Olivine P01R0101 pier"),
    (154, 1, 65, 490, "Vermilion P01R0103 pier"),
)

GANGPLANK_CHECKS = (
    (153, 0, "Olivine P01R0102 gangplank"),
    (155, 0, "Vermilion P01R0104 gangplank"),
)

OLIVINE_GAME_CLEAR_REL_OFF = 278
KEEP_BOAT_ARRIVED = (
    (152, 2, (442, 681)),
    (154, 1, (288,)),
)
GANGPLANK_BOAT_ARRIVED_REL = 15


def find_scrdef_end(data: bytes) -> int:
    pos = 0
    while pos + 2 <= len(data) and pos < 512:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return pos
        pos += 4
    raise ValueError("scrdef_end not found")


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def script_body(data: bytes, slot: int) -> bytes:
    fd = find_scrdef_end(data)
    count = fd // 4
    start = script_offset(data, slot)
    end = script_offset(data, slot + 1) if slot + 1 < count else len(data)
    if end <= start:
        end = len(data)
    return data[start:end]


def gangplank_prefix(data: bytes, slot: int) -> bytes:
    start = script_offset(data, slot)
    return data[start : start + 64]


def verify_table_unchanged(path: Path, label: str) -> bool:
    vanilla_path = Path(f"build/a012_vanilla/{path.name}")
    if not vanilla_path.is_file():
        return True
    data = path.read_bytes()
    vanilla = vanilla_path.read_bytes()
    if len(data) != len(vanilla):
        print(f"{label}: file size changed (table rebuild?)", file=sys.stderr)
        return False
    fd = find_scrdef_end(data)
    if data[: fd + 4] != vanilla[: fd + 4]:
        print(f"{label}: scr_seq offset table changed", file=sys.stderr)
        return False
    return True


def verify_pier(path: Path, member: int, slot: int, wd_off: int, vanilla_len: int, label: str) -> bool:
    if not verify_table_unchanged(path, label):
        return False
    body = script_body(path.read_bytes(), slot)
    if len(body) != vanilla_len:
        print(f"{label}: slot len {len(body)} != vanilla {vanilla_len}", file=sys.stderr)
        return False
    if body[wd_off : wd_off + 2] != struct.pack("<H", GOTO_OP):
        print(f"{label}: expected goto at {wd_off}", file=sys.stderr)
        return False
    if GET_WEEKDAY in body:
        print(f"{label}: GetWeekday still present", file=sys.stderr)
        return False
    if member == 152:
        rel = struct.unpack_from("<i", body, OLIVINE_GAME_CLEAR_REL_OFF)[0]
        if rel != 0:
            print(f"{label}: game-clear goto_if rel expected 0, got {rel}", file=sys.stderr)
            return False
    clear = struct.pack("<HH", CLEARFLAG, FLAG_BOAT_ARRIVED)
    setf = struct.pack("<HH", SETFLAG, FLAG_BOAT_ARRIVED)
    for m, sl, offs in KEEP_BOAT_ARRIVED:
        if m != member or sl != slot:
            continue
        for off in offs:
            if body[off : off + 4] != setf:
                print(f"{label}: expected setflag @ slot+{off}", file=sys.stderr)
                return False
            if clear in body:
                print(f"{label}: clearflag {FLAG_BOAT_ARRIVED} still in slot", file=sys.stderr)
                return False
    print(f"ok: {label} ({path.name})")
    return True


def verify_gangplank(path: Path, slot: int, label: str) -> bool:
    if not verify_table_unchanged(path, label):
        return False
    prefix = gangplank_prefix(path.read_bytes(), slot)
    check = struct.pack("<HH", CHECKFLAG, FLAG_BOAT_ARRIVED)
    if prefix[8:12] != check:
        print(f"{label}: expected checkflag {FLAG_BOAT_ARRIVED} @+8", file=sys.stderr)
        return False
    if struct.unpack_from("<H", prefix, 12)[0] != GOTO_IF or prefix[14] != 1:
        print(f"{label}: expected GoToIfSet @+12", file=sys.stderr)
        return False
    rel = struct.unpack_from("<i", prefix, GANGPLANK_BOAT_ARRIVED_REL)[0]
    if rel != 0:
        print(f"{label}: gangplank goto_if rel expected 0, got {rel}", file=sys.stderr)
        return False
    print(f"ok: {label} ({path.name})")
    return True


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(f"usage: {argv[0]} <2_152> <2_154> <2_153> <2_155>", file=sys.stderr)
        return 1

    pier_paths = argv[1:3]
    gang_paths = argv[3:5]

    ok = True
    for path_arg, (member, slot, wd_off, vanilla_len, label) in zip(pier_paths, PIER_CHECKS, strict=True):
        path = Path(path_arg)
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        ok = verify_pier(path, member, slot, wd_off, vanilla_len, label) and ok

    for path_arg, (member, slot, label) in zip(gang_paths, GANGPLANK_CHECKS, strict=True):
        path = Path(path_arg)
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        ok = verify_gangplank(path, slot, label) and ok

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
