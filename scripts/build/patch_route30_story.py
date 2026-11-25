"""Skip the first Mr. Pokémon visit and Mom's Route 30 phone call."""

import struct
import sys
from pathlib import Path

from tools.append_scr_seq_script import script_offset


def replace_entry(path: Path, slot: int, prefix: str, replacement: bytes) -> bytes:
    data = bytearray(path.read_bytes())
    start = script_offset(data, slot)
    expected = bytes.fromhex(prefix)
    if data[start:start + len(expected)] != expected:
        raise ValueError(f"{path}: unexpected opening commands for script slot {slot}")
    data[start:start + len(replacement)] = replacement
    return bytes(data)


def main() -> None:
    route, house = map(Path, sys.argv[1:])
    skip_call = struct.pack(
        "<6H",
        41, 0x4095, 0,  # SetVar VAR_SCENE_ROUTE_30_PHONE_CALL, 0
        30, 167,        # SetFlag FLAG_TALKED_TO_MOM_AFTER_NAMING_RIVAL
        2,              # End
    )
    skip_visit = (
        # CheckFlag and branch over HidePerson and SetFlag if Oak is already hidden.
        struct.pack("<HHHBi4H", 32, 405, 28, 1, 8, 101, 1, 30, 405)
        # Resolve the errand so repeat dialogue does not ask the player to deliver the Egg.
        + struct.pack("<4H", 41, 0x4107, 2, 2)
    )
    route_data = replace_entry(route, 4, "61 02 60 00 29 00 04 80", skip_call)
    house_data = replace_entry(house, 1, "61 02 60 00 5e 00 00 00", skip_visit)
    route.write_bytes(route_data)
    house.write_bytes(house_data)
    print("Skipped Mom's Route 30 call and the first Mr. Pokémon visit")


if __name__ == "__main__":
    main()
