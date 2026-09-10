#!/usr/bin/env python3
"""Find scr_seq member for Route 44 by scanning npc_msg indices and script counts."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "build/a012"


def slot_body(data: bytes, slot: int) -> bytes:
    pos = 0
    count = 0
    while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        count += 1
        pos += 4
    start = struct.unpack_from("<i", data, slot * 4)[0] + slot * 4 + 4
    starts = [struct.unpack_from("<i", data, j * 4)[0] + j * 4 + 4 for j in range(count)]
    end = min((s for s in starts if s > start), default=len(data))
    return data[start:end]


def npc_msg_indices(body: bytes) -> list[int]:
    indices: list[int] = []
    i = 0
    while i + 1 < len(body):
        op = struct.unpack_from("<H", body, i)[0]
        i += 2
        if op == 0:
            break
        if op == 45:
            indices.append(body[i])
            i += 1
        elif op in (17, 41, 40):
            i += 4
        elif op == 22:
            i += 4
        elif op == 28:
            i += 5
        elif op in (36, 37):
            i += 6
        elif op in (125, 128):
            i += 6
        elif op == 20:
            i += 2
        else:
            i += 2
    return indices


def count_scripts(data: bytes) -> int:
    pos = 0
    count = 0
    while pos + 2 <= len(data) and pos < 512:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return count
        count += 1
        pos += 4
    return count


def main() -> int:
    subprocess.check_call(
        [sys.executable, str(ROOT / "tools/extract_scr_seq_vanilla.py"), str(SCR)]
    )

    # Route 44 sign text in data/text/404.txt starts with Ice Path / Rt. 44
    print("Scan scr_seq 248-265 for sign-like npc_msg patterns:\n")
    for m in range(248, 266):
        p = SCR / f"2_{m:03d}"
        if not p.is_file():
            continue
        data = p.read_bytes()
        n = count_scripts(data)
        all_msgs: list[list[int]] = []
        for slot in range(n):
            all_msgs.append(npc_msg_indices(slot_body(data, slot)))
        nonempty = [i for i, msgs in enumerate(all_msgs) if msgs]
        if not nonempty and n <= 2:
            continue
        print(f"member {m:3d}: {n} scripts, {len(data)} bytes")
        for slot in range(n):
            msgs = all_msgs[slot]
            if msgs or len(slot_body(data, slot)) > 4:
                print(f"  slot {slot} (scriptId {slot+1}): msgs={msgs} size={len(slot_body(data, slot))}")

    print("\nRoute 42 reference: member 252, 6 vanilla scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
