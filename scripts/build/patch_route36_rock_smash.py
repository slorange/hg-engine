"""Replace Route 36's HM06 gift with the Rock Smash tip."""

import sys
from pathlib import Path

from tools.append_scr_seq_script import script_offset


def main() -> None:
    path = Path(sys.argv[1])
    data = bytearray(path.read_bytes())
    # Object script ID 9 points to slot 8. Keep its greeting and use message 3.
    start = script_offset(data, 8)
    prefix = bytes.fromhex("49 00 dc 05 60 00 68 00")
    if not data[start:].startswith(prefix + bytes.fromhex("9d 02 a9 01 0c 80")):
        raise ValueError(f"{path}: unexpected Route 36 HM06 gift entry")
    dialogue = prefix + bytes.fromhex("2d 00 03 32 00 35 00 61 00 02 00")
    data[start:start + len(dialogue)] = dialogue
    path.write_bytes(data)
    print("Replaced the Route 36 HM06 gift with a Rock Smash tip")


if __name__ == "__main__":
    main()
