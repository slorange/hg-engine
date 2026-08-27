#!/usr/bin/env python3
"""Dump scr_seq script bodies and scan for flag/item opcodes."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from append_scr_seq_script import extract_scripts, find_scrdef_end  # noqa: E402

CMD_SETFLAG = 30
CMD_GIVEPDEX = 291
CMD_GIVE_SHOES = 293

WATCH_FLAGS = {107, 156, 283}


def scan_script(body: bytes, label: str) -> None:
    hits: list[str] = []
    i = 0
    while i + 4 <= len(body):
        cmd = struct.unpack_from("<H", body, i)[0]
        if cmd == CMD_SETFLAG:
            flag = struct.unpack_from("<H", body, i + 2)[0]
            if flag in WATCH_FLAGS:
                hits.append(f"setflag {flag} @{i}")
        elif cmd == CMD_GIVEPDEX:
            hits.append(f"GivePokedex @{i}")
        elif cmd == CMD_GIVE_SHOES:
            hits.append(f"give_running_shoes @{i}")
        i += 2
        # skip operands crudely for known cmds
        if cmd == CMD_SETFLAG:
            i += 2
        elif cmd in (CMD_GIVEPDEX, CMD_GIVE_SHOES):
            pass
    if hits:
        print(f"  {label}: {', '.join(hits)}")


def main() -> None:
    members = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [957, 962, 834, 961]
    for mid in members:
        path = ROOT / f"build/a012/2_{mid}"
        if not path.is_file():
            print(f"missing {path}")
            continue
        data = path.read_bytes()
        try:
            scripts = extract_scripts(data)
        except ValueError as e:
            print(f"2_{mid}: skip ({e})")
            continue
        print(f"=== 2_{mid} ({len(data)} bytes, {len(scripts)} scripts) ===")
        for idx, body in enumerate(scripts):
            scan_script(body, f"script {idx}")


if __name__ == "__main__":
    main()
