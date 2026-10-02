#!/usr/bin/env python3
"""Olivine Lighthouse top (scr_seq 66 / D27R0107): door + medicine-order fixes.

Vanilla GoToIfSet FLAG_GOT_SECRETPOTION skips the door-opening beat; buying
medicine at the mart traps the player after the heal scene. OnLoad script 4
shows a door stop when FLAG_UNK_1D8 is unset.

See documentation/HACK-NOTES.md § Olivine Secret Medicine (Jasmine).
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

# scr_seq 66 slot 4 — checkflag FLAG_UNK_1D8 (472) / door stop on load.
ONLOAD_SCRIPT_OFFSET = 30
ONLOAD_CHECKFLAG = bytes([0x20, 0x00, 0xD8, 0x01])
ONLOAD_PATCH = bytes([0x02, 0x00])  # end

# scr_seq 66 slot 0 — after checkflag FLAG_GOT_SECRETPOTION (185), goto_if rel.
POTION_CHECKFLAG_OFFSET = 55
POTION_CHECKFLAG = bytes([0x20, 0x00, 0xB9, 0x00])
POTION_GOTO_REL_OFFSET = 62
POTION_GOTO_REL_VANILLA = struct.pack("<i", 0x73)
POTION_GOTO_REL_PATCH = struct.pack("<i", 0)


def patch_onload(data: bytearray) -> None:
    if data[ONLOAD_SCRIPT_OFFSET : ONLOAD_SCRIPT_OFFSET + 2] == ONLOAD_PATCH:
        print("lighthouse OnLoad door stop already patched (ok)")
        return
    if data[ONLOAD_SCRIPT_OFFSET : ONLOAD_SCRIPT_OFFSET + len(ONLOAD_CHECKFLAG)] != ONLOAD_CHECKFLAG:
        raise ValueError(f"unexpected OnLoad checkflag @ {ONLOAD_SCRIPT_OFFSET} in 2_066")
    data[ONLOAD_SCRIPT_OFFSET : ONLOAD_SCRIPT_OFFSET + len(ONLOAD_PATCH)] = ONLOAD_PATCH
    print(f"patched lighthouse OnLoad door stop @{ONLOAD_SCRIPT_OFFSET}")


def patch_potion_goto(data: bytearray) -> None:
    rel = data[POTION_GOTO_REL_OFFSET : POTION_GOTO_REL_OFFSET + 4]
    if rel == POTION_GOTO_REL_PATCH:
        print("SECRETPOTION goto rel already patched (ok)")
        return
    if data[POTION_CHECKFLAG_OFFSET : POTION_CHECKFLAG_OFFSET + len(POTION_CHECKFLAG)] != (
        POTION_CHECKFLAG
    ):
        raise ValueError(f"unexpected SECRETPOTION checkflag @ {POTION_CHECKFLAG_OFFSET} in 2_066")
    if rel != POTION_GOTO_REL_VANILLA:
        raise ValueError(f"unexpected goto rel @ {POTION_GOTO_REL_OFFSET} in 2_066")
    data[POTION_GOTO_REL_OFFSET : POTION_GOTO_REL_OFFSET + 4] = POTION_GOTO_REL_PATCH
    print(f"patched SECRETPOTION goto rel @{POTION_GOTO_REL_OFFSET}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_066>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    data = bytearray(target.read_bytes())
    patch_onload(data)
    patch_potion_goto(data)
    target.write_bytes(data)
    print(f"patched Olivine lighthouse scripts in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
