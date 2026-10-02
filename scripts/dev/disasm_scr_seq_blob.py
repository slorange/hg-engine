#!/usr/bin/env python3
"""Disassemble scr_seq bytecode (partial opcode set)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

# From pret / HGSS — extend as needed
OP_NAMES: dict[int, str | tuple[str, int]] = {
    0: ("end", 0),
    2: ("scr_end", 0),
    17: ("cmpvar", 6),
    28: ("goto_if", 5),
    30: ("setflag", 2),
    31: ("clearflag", 2),
    32: ("checkflag", 2),
    41: ("setvar", 4),
    45: ("npc_msg", 2),
    73: ("play_se", 2),
    78: ("play_fanfare", 2),
    96: ("lockall", 0),
    97: ("releaseall", 0),
    98: ("wait_button", 0),
    99: ("closemsg", 0),
    104: ("faceplayer", 0),
    101: ("hide_person", 2),
    102: ("show_person", 2),
    125: ("giveitem", 6),
    213: ("trainer_battle", 2),
    294: ("check_badge", 4),
    295: ("givebadge", 2),
    439: ("non_npc_msg_extern", 4),
    296: ("count_badges", 2),
}


def disasm(data: bytes, start: int, end: int) -> None:
    i = start
    while i < end:
        if i + 2 > end:
            print(f"  @{i}: trunc")
            return
        op = struct.unpack_from("<H", data, i)[0]
        pos = i
        i += 2
        spec = OP_NAMES.get(op)
        if spec is None:
            print(f"  @{pos}: unknown op {op}")
            return
        name, extra = spec if isinstance(spec, tuple) else (spec, 0)
        if extra and i + extra > end:
            print(f"  @{pos}: {name} (trunc args)")
            return
        if op == 28:
            cond = data[i]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            target = pos + 7 + rel
            print(f"  @{pos}: goto_if {cond} -> {target}")
            i += 5
        elif extra:
            args = data[i : i + extra]
            if extra == 2:
                a = struct.unpack_from("<H", args, 0)[0]
                print(f"  @{pos}: {name} {a}")
            elif extra == 4:
                a, b = struct.unpack_from("<HH", args, 0)
                print(f"  @{pos}: {name} {a} {b}")
            elif extra == 6:
                print(f"  @{pos}: {name} {args.hex()}")
            i += extra
        else:
            print(f"  @{pos}: {name}")
        if op in (0, 2):
            return


def main() -> None:
    path = Path(sys.argv[1])
    start = int(sys.argv[2], 0)
    end = int(sys.argv[3], 0) if len(sys.argv) > 3 else len(path.read_bytes())
    data = path.read_bytes()
    print(f"{path} [{start},{end})")
    disasm(data, start, end)


if __name__ == "__main__":
    main()
