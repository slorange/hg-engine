#!/usr/bin/env python3
"""Verify Gym Leader scr_seq contains badge-count HM grant bytecode (slot 0 or 1)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

GIVEITEM = 125
GIVEITEM_VERBOSE = 2033
COUNT_BADGES = 296
NON_NPC_MSG_EXTERN = 439
MSG_BANK_GYM_REWARDS = 854
ITEM_HM01 = 420
ITEM_HM02 = 421
PLAY_FANFARE = 78
SEQ_ME_WAZA = 1190
MAX_TABLE_SCAN = 512


def find_scrdef_end(data: bytes) -> int:
    pos, count = 0, 0
    while pos + 2 <= len(data) and pos < MAX_TABLE_SCAN:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return count
        count += 1
        pos += 4
    raise ValueError("scrdef_end not found")


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def script_body(data: bytes, index: int) -> bytes:
    count = find_scrdef_end(data)
    start = script_offset(data, index)
    end = script_offset(data, index + 1) if index + 1 < count else len(data)
    return data[start:end]


def find_leader_slot(data: bytes) -> int | None:
    count = find_scrdef_end(data)
    extern_msg = struct.pack("<HHH", NON_NPC_MSG_EXTERN, MSG_BANK_GYM_REWARDS, 0)
    for index in range(count):
        body = script_body(data, index)
        if struct.pack("<H", COUNT_BADGES) in body and extern_msg in body:
            return index
    return None


def verify(path: Path) -> int:
    data = path.read_bytes()
    slot_index = find_leader_slot(data)
    if slot_index is None:
        print(f"{path}: {len(data)} bytes")
        print("FAIL: no script slot with badge-count HM grant bytecode")
        return 1

    slot = script_body(data, slot_index)
    print(f"{path}: {len(data)} bytes, slot{slot_index}={len(slot)} bytes")

    if struct.pack("<H", COUNT_BADGES) not in slot:
        print(f"FAIL: count_badges opcode missing in slot {slot_index}")
        return 1

    extern_msg = struct.pack("<HHH", NON_NPC_MSG_EXTERN, MSG_BANK_GYM_REWARDS, 0)
    if extern_msg not in slot:
        print(f"FAIL: shared gym level-cap message (bank 854) missing in slot {slot_index}")
        return 1

    if struct.pack("<H", GIVEITEM) not in slot:
        print(f"FAIL: silent giveitem missing in slot {slot_index}")
        return 1

    if struct.pack("<HH", PLAY_FANFARE, SEQ_ME_WAZA) not in slot:
        print(f"FAIL: SEQ_ME_WAZA fanfare missing in slot {slot_index}")
        return 1

    hm_items = (
        ITEM_HM01,
        ITEM_HM02,
        422,
        423,
        424,
        425,
        426,
        427,
    )
    if not any(struct.pack("<H", item_id) in slot for item_id in hm_items):
        print(f"FAIL: no HM item id in slot {slot_index}")
        return 1

    print("OK")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} <build/a012/2_NNN> [...]", file=sys.stderr)
        return 1

    rc = 0
    for arg in argv[1:]:
        if verify(Path(arg)) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
