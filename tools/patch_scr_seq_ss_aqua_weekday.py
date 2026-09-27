#!/usr/bin/env python3
"""SS Aqua: every-day boarding + skip first-voyage onboard story.

Pier (152 / 154): weekday goto, Olivine game-clear fix, keep FLAG_BOAT_ARRIVED on embark.
Gangplank (153 / 155): neutralize GoToIfSet FLAG_BOAT_ARRIVED (Mom sets 235 for open-world).

In-place only — do not rebuild the scr_seq offset table.

See DESIGN-WORLD.md § SS Aqua.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

GET_WEEKDAY = bytes([0xE4, 0x01])
GOTO = 22
GOTO_IF = 28
CHECKFLAG = 32
SETFLAG = 30
CLEARFLAG = 31

FLAG_GAME_CLEAR = 2404
FLAG_BOAT_ARRIVED = 235

PIER_PATCHES: tuple[tuple[int, int, int, int, str], ...] = (
    (152, 2, 458, 618, "Olivine P01R0101 pier"),
    (154, 1, 65, 225, "Vermilion P01R0103 pier"),
)

GANGPLANK_PATCHES: tuple[tuple[int, int, str], ...] = (
    (153, 0, "Olivine P01R0102 gangplank"),
    (155, 0, "Vermilion P01R0104 gangplank"),
)

KEEP_BOAT_ARRIVED: tuple[tuple[int, int, tuple[int, ...]], ...] = (
    (152, 2, (442, 681)),
    (154, 1, (288,)),
)

OLIVINE_GAME_CLEAR_GOTO_IF = 275
OLIVINE_GAME_CLEAR_REL_OFF = 278

MAX_TABLE_SCAN = 512
GANGPLANK_SCAN = 64


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


def script_span(data: bytes, slot: int) -> tuple[int, int]:
    _, count = find_scrdef_end(data)
    if slot >= count:
        raise ValueError(f"slot {slot} missing (only {count} scripts)")
    start = script_offset(data, slot)
    end = script_offset(data, slot + 1) if slot + 1 < count else len(data)
    if end <= start:
        end = len(data)
    return start, end


def bypass_weekday_inplace(script: bytes, wd_off: int, allow_off: int, label: str) -> bytes:
    data = bytearray(script)
    if data[wd_off : wd_off + 2] != GET_WEEKDAY:
        raise ValueError(
            f"{label}: expected GetWeekday at {wd_off}, got {data[wd_off : wd_off + 4].hex()}"
        )
    rel = allow_off - (wd_off + 6)
    data[wd_off : wd_off + 6] = struct.pack("<Hi", GOTO, rel)
    if len(data) != len(script):
        raise ValueError(f"{label}: weekday patch must not change script size")
    return bytes(data)


def bypass_olivine_game_clear(script: bytes) -> bytes:
    data = bytearray(script)
    off = OLIVINE_GAME_CLEAR_GOTO_IF
    if struct.unpack_from("<H", data, off)[0] != GOTO_IF:
        raise ValueError(f"Olivine: expected goto_if @ {off}")
    if data[off + 2] != 0:
        raise ValueError(f"Olivine: expected unset (0) goto_if condition @ {off + 2}")
    if struct.unpack_from("<H", data, off - 4)[0] != CHECKFLAG:
        raise ValueError(f"Olivine: expected checkflag before goto_if")
    if struct.unpack_from("<H", data, off - 2)[0] != FLAG_GAME_CLEAR:
        raise ValueError(f"Olivine: expected FLAG_GAME_CLEAR")
    struct.pack_into("<i", data, OLIVINE_GAME_CLEAR_REL_OFF, 0)
    return bytes(data)


def keep_boat_arrived_on_embark(script: bytes, offsets: tuple[int, ...], label: str) -> bytes:
    data = bytearray(script)
    clear = struct.pack("<HH", CLEARFLAG, FLAG_BOAT_ARRIVED)
    for off in offsets:
        if data[off : off + 4] != clear:
            raise ValueError(
                f"{label}: expected clearflag {FLAG_BOAT_ARRIVED} @ {off}, "
                f"got {data[off : off + 4].hex()}"
            )
        struct.pack_into("<H", data, off, SETFLAG)
    return bytes(data)


def neutralize_boat_arrived_gangplank(script: bytes, label: str) -> bytes:
    """GoToIfSet FLAG_BOAT_ARRIVED -> block msg; force fall-through to boarding."""
    data = bytearray(script)
    check = struct.pack("<HH", CHECKFLAG, FLAG_BOAT_ARRIVED)
    for off in range(min(GANGPLANK_SCAN, len(data) - 11)):
        if data[off : off + 4] != check:
            continue
        if struct.unpack_from("<H", data, off + 4)[0] != GOTO_IF:
            continue
        if data[off + 6] != 1:
            continue
        struct.pack_into("<i", data, off + 7, 0)
        return bytes(data)
    raise ValueError(f"{label}: GoToIfSet FLAG_BOAT_ARRIVED not found in gangplank script")


def patch_pier_file(path: Path, slot: int, wd_off: int, allow_off: int, label: str, member: int) -> None:
    data = bytearray(path.read_bytes())
    start, end = script_span(data, slot)
    body = data[start:end]
    if member == 152:
        body = bypass_olivine_game_clear(bytes(body))
    body = bypass_weekday_inplace(body, wd_off, allow_off, label)
    for m, sl, offs in KEEP_BOAT_ARRIVED:
        if m == member and sl == slot:
            body = keep_boat_arrived_on_embark(body, offs, label)
            break
    if len(body) != end - start:
        raise ValueError(f"{label}: patched slot size changed")
    data[start:end] = body
    path.write_bytes(data)


def patch_gangplank_file(path: Path, slot: int, label: str) -> None:
    data = bytearray(path.read_bytes())
    start = script_offset(data, slot)
    scan_end = min(len(data), start + 400)
    body = bytearray(data[start:scan_end])
    patched = neutralize_boat_arrived_gangplank(bytes(body), label)
    data[start : start + len(patched)] = patched
    path.write_bytes(data)


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(
            f"usage: {argv[0]} <2_152> <2_154> <2_153> <2_155>",
            file=sys.stderr,
        )
        return 1

    pier_paths = [Path(argv[1]), Path(argv[2])]
    gang_paths = [Path(argv[3]), Path(argv[4])]

    for path, (member, slot, wd, allow, label) in zip(pier_paths, PIER_PATCHES, strict=True):
        if not path.is_file():
            print(f"missing {path} (run extract_scr_seq_vanilla first)", file=sys.stderr)
            return 1
        patch_pier_file(path, slot, wd, allow, label, member)
        print(f"SS Aqua pier patch: {label} -> {path}")

    for path, (member, slot, label) in zip(gang_paths, GANGPLANK_PATCHES, strict=True):
        if not path.is_file():
            print(f"missing {path} (run extract_scr_seq_vanilla first)", file=sys.stderr)
            return 1
        patch_gangplank_file(path, slot, label)
        print(f"SS Aqua gangplank patch: {label} -> {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
