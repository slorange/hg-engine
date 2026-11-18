#!/usr/bin/env python3
"""Bypass only the six badge checks in the shared overworld HM scripts."""

import argparse
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAG = "OPENWORLD_FIELD_MOVES_NO_BADGE_GATE"
# Member 146: (file offset, expected badge, interaction script slot).
CHECKS = ((105, 1, 0), (674, 0, 1), (1327, 2, 2),
          (1873, 15, 3), (2402, 7, 5), (2559, 6, 16))


def patch_member(data: bytes, enabled: bool, verify: bool = False) -> bytes:
    result = bytearray(data)
    for offset, badge, slot in CHECKS:
        start = slot * 4 + 4 + struct.unpack_from("<I", data, slot * 4)[0]
        if not start <= offset < start + 80:
            raise ValueError(f"HM slot {slot}: unexpected script layout")
        original = struct.pack("<HHH", 294, badge, 0x800C)  # CheckBadge
        replacement = struct.pack("<HHH", 41, 0x800C, 1)  # SetVar TRUE
        expected = replacement if enabled else original
        actual = data[offset:offset + 6]
        if verify:
            if actual != expected:
                raise ValueError(f"HM slot {slot}: badge patch verification failed")
        elif actual not in (original, expected):
            raise ValueError(f"HM slot {slot}: unexpected bytes at {offset:#x}")
        result[offset:offset + 6] = expected
    return bytes(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    config = (ROOT / "include/config.h").read_text(encoding="utf-8")
    enabled = re.search(rf"^#define\s+{FLAG}\b", config, re.MULTILINE) is not None
    path = args.directory / "2_146"
    data = patch_member(path.read_bytes(), enabled, args.verify)
    patch_member(data, enabled, verify=True)
    if not args.verify:
        path.write_bytes(data)
    print(f"Shared HM interaction badge checks verified (bypass {'on' if enabled else 'off'})")


if __name__ == "__main__":
    main()
