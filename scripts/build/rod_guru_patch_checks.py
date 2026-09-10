#!/usr/bin/env python3
"""Shared bytecode checks for rod guru scr_seq patches."""

from __future__ import annotations

import struct

STD_GIVE_ITEM_VERBOSE = 2033


def walk_opcodes(body: bytes) -> list[tuple[int, int]]:
    ops: list[tuple[int, int]] = []
    i = 0
    while i + 1 < len(body):
        op = struct.unpack_from("<H", body, i)[0]
        ops.append((i, op))
        if op == 0:
            break
        i += 2
        if op == 17:
            i += 4
        elif op == 22:
            i += 4
        elif op == 28:
            i += 5
        elif op in (36, 37):
            i += 6
        elif op == 45:
            i += 1
        elif op == 63:
            i += 2
        elif op == 125:
            i += 6
        elif op == 128:
            i += 6
        elif op == 20:
            i += 2
        elif op in (30, 32, 41, 73):
            i += 4 if op in (41, 73) else 2
        elif op == 40:
            i += 4
        elif op == 198:
            i += 3
        elif op == 208:
            i += 3
        elif op in (50, 52, 53, 96, 97, 104):
            pass
        else:
            i += 2
    return ops


def validate_rod_guru_body(body: bytes, label: str) -> None:
    walked = walk_opcodes(body)
    ops = {op for _, op in walked}
    if 63 in ops:
        raise ValueExit(f"FAIL: {label} contains yesno opcode")
    if 125 in ops:
        raise ValueExit(f"FAIL: {label} uses silent giveitem opcode")
    callstds = {
        struct.unpack_from("<H", body, i + 2)[0]
        for i, op in walked
        if op == 20 and i + 3 < len(body)
    }
    if STD_GIVE_ITEM_VERBOSE not in callstds:
        raise ValueExit(f"FAIL: {label} missing giveitem_no_check (std_give_item_verbose)")
    if struct.pack("<H", 445) not in body:
        raise ValueExit(f"FAIL: {label} missing Old Rod item id (445)")


class ValueExit(SystemExit):
    pass
