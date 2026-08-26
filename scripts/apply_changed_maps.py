#!/usr/bin/env python3
"""Replace land_data.narc members from rawdata/changed_maps exports."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import ndspy.narc

ROOT = Path(__file__).resolve().parents[1]
LAND_DATA = ROOT / "base/root/a/0/6/5"
CHANGED_MAPS = ROOT / "rawdata/changed_maps"


def main() -> int:
    if not LAND_DATA.is_file():
        print(f"error: {LAND_DATA} not found — run a full build first", file=sys.stderr)
        return 1

    patches = sorted(CHANGED_MAPS.rglob("*.bin"))
    if not patches:
        print("no map patches found under rawdata/changed_maps/")
        return 0

    narc = ndspy.narc.NARC.fromFile(LAND_DATA)
    applied = 0

    for patch in patches:
        match = re.match(r"^(\d+)", patch.name)
        if not match:
            print(f"warning: skipping {patch} (filename must start with member index)", file=sys.stderr)
            continue

        index = int(match.group(1))
        if index >= len(narc.files):
            print(f"error: member {index} out of range for land_data ({len(narc.files)} files)", file=sys.stderr)
            return 1

        data = patch.read_bytes()
        narc.files[index] = data
        print(f"patched land_data member {index:03d} from {patch.relative_to(ROOT)} ({len(data)} bytes)")
        applied += 1

    if applied:
        narc.endiannessOfBeginning = ">"
        narc.saveToFile(LAND_DATA)

    print(f"applied {applied} map patch(es)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
