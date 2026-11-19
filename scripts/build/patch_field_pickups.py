#!/usr/bin/env python3
"""Route field-pickup capacity checks and grants through the reward picker."""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from append_scr_seq_script import script_offset

GOTO = 22
RUN_NEW_COMMAND = 208
FIELD_PICKUP_COMMAND = 8
CHECK_GROUND, CHECK_HIDDEN, GRANT = range(3)
CHECK_SPACE = struct.pack("<4H", 127, 0x8004, 0x8005, 0x800C)
GIVE_ITEM = struct.pack("<4H", 125, 0x8004, 0x8005, 0x800C)


def jump(source: int, destination: int) -> bytes:
    return struct.pack("<Hi", GOTO, destination - source - 6)


def replace_command(data: bytearray, offset: int, action: int) -> None:
    # Run the new command out of line so the original branches stay valid.
    entry = len(data)
    command = struct.pack("<HBH", RUN_NEW_COMMAND, FIELD_PICKUP_COMMAND, action)
    data[offset:offset + 8] = jump(offset, entry) + b"\0\0"
    data.extend(command + jump(entry + len(command), offset + 8))


def patch_bank(path: Path, slots: tuple[int, ...], *, hidden: bool = False) -> None:
    data = bytearray(path.read_bytes())
    starts = set()
    for slot in slots:
        start = script_offset(data, slot)
        if not hidden:
            # Visible pickups initialize item and quantity, then jump to the shared grant.
            if struct.unpack_from("<HH", data, start) == (41, 0x4001):
                start += 6
            first, item_var, _, second, qty_var, _, opcode, delta = struct.unpack_from(
                "<7Hi", data, start
            )
            if (first, item_var, second, qty_var, opcode) != (41, 0x8008, 41, 0x8009, GOTO):
                raise ValueError(f"{path}: unexpected item initializer in slot {slot}")
            start += 18 + delta
        starts.add(start)
    if len(starts) != 1:
        raise ValueError(f"{path}: pickup scripts do not share a grant")
    start = starts.pop()

    check = start + (22 if hidden else 24)
    if data[check:check + len(CHECK_SPACE)] != CHECK_SPACE:
        raise ValueError(f"{path}: unexpected capacity command at {check}")
    give = data.find(GIVE_ITEM, check + len(CHECK_SPACE))
    if give < 0 or data.find(GIVE_ITEM, give + len(GIVE_ITEM)) != -1:
        raise ValueError(f"{path}: expected one shared give-item command after capacity check")

    replace_command(data, check, CHECK_HIDDEN if hidden else CHECK_GROUND)
    replace_command(data, give, GRANT)
    if len(data) % 2:
        data.append(0)
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script_dir", type=Path)
    args = parser.parse_args()

    patch_bank(args.script_dir / "2_141", tuple(range(255)))
    patch_bank(args.script_dir / "2_145", tuple(range(231)), hidden=True)
    patch_bank(args.script_dir / "2_938", (14, 15, 16))  # Lake of Rage
    # Mt. Moon's recurring Clefairy event keeps its fixed Moon Stone.


if __name__ == "__main__":
    main()
