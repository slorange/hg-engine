#!/usr/bin/env python3
"""Find Mom openworld injection point in scr_seq 845 script 0."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from append_scr_seq_script import extract_scripts  # noqa: E402

FLAG_GOT_OPTIONS = 286
SEQ_KIRAKIRA = 1418


def main() -> None:
    path = ROOT / "build/a012/2_845"
    data = path.read_bytes()
    scripts = extract_scripts(data)
    body = scripts[0]
    print(f"script 0: {len(body)} bytes")

    needle = struct.pack("<HHHHH", 30, FLAG_GOT_OPTIONS, 78, SEQ_KIRAKIRA, 79)
    idx = body.find(needle)
    print(f"setflag286+fanfare @ {idx:#x}" if idx >= 0 else "needle not found")

    # closemsg after options msg (npc_msg id 5)
    for msg_id in range(8):
        pat = struct.pack("<HBH", 45, msg_id, 53)  # npc_msg, id, closemsg
        pos = body.find(pat)
        if pos >= 0:
            print(f"npc_msg {msg_id} + closemsg @ {pos:#x}, after closemsg: {body[pos+3:pos+20].hex()}")

    # wait 15 after options
    wait_pat = struct.pack("<HHH", 3, 15, 0x8004)  # wait 15, VAR_SPECIAL_x8004
    pos = body.find(wait_pat)
    print(f"wait 15 @ {pos:#x}" if pos >= 0 else "wait not found")
    if pos >= 0:
        print(f"bytes before wait: {body[pos-8:pos].hex()}")


if __name__ == "__main__":
    main()
