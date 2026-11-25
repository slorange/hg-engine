"""Replace the gatehouse cinematic with a silent grant for existing saves."""

import struct
import sys
from pathlib import Path

from tools.append_scr_seq_script import script_offset


def main() -> None:
    path = Path(sys.argv[1])
    data = bytearray(path.read_bytes())
    start = script_offset(data, 0)
    if data[start:start + 6] != bytes.fromhex("61 02 60 00 14 00"):
        raise ValueError(f"{path}: unexpected opening commands for VS Recorder scene")

    recorder = 465
    result = 0x800C
    # HasItem, Compare, and GoToIfNe over the eight-byte silent GiveItem.
    replacement = struct.pack("<8HBi", 128, recorder, 1, result, 17, result, 0, 28, 5, 8)
    replacement += struct.pack("<8H", 125, recorder, 1, result, 41, 0x4132, 1, 2)
    data[start:start + len(replacement)] = replacement
    path.write_bytes(data)
    print(f"Skipped the Violet gatehouse VS Recorder scene in {path}")


if __name__ == "__main__":
    main()
