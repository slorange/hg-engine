"""Skip the outdoor Lyra/Ethan and Marill scene while advancing the house state."""

import struct
import sys
from pathlib import Path

from tools.patch_scr_seq_t20_mom import find_scrdef_end, script_offset


def main() -> None:
    target = Path(sys.argv[1])
    data = bytearray(target.read_bytes())
    _, script_count = find_scrdef_end(data)
    if script_count != 18:
        raise ValueError(f"Unexpected New Bark script count: {script_count}")

    start = script_offset(data, 3)
    # Preserve the final state of the original scene without moving any objects.
    replacement = bytearray()
    for object_id, hide_flag in ((3, 417), (4, 418)):  # Marill, Lyra/Ethan
        # CheckFlag, then branch over HidePerson and SetFlag if already hidden.
        replacement.extend(
            struct.pack("<HHHBi4H", 32, hide_flag, 28, 1, 8, 101, object_id, 30, hide_flag)
        )
    replacement.extend(struct.pack("<4H", 41, 0x4106, 2, 2))  # SetVar, End
    end = start + len(replacement)
    if data[start:start + 6] != bytes.fromhex("61 02 60 00 63 00"):
        raise ValueError("Unexpected opening commands in New Bark script T20_003")
    data[start:end] = replacement
    target.write_bytes(data)
    print(f"Skipped outdoor friend and Marill scene in {target}")


if __name__ == "__main__":
    main()
