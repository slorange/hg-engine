#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "build/a012")
needles = {
    bytes.fromhex("e301"): "483 HIDE_RED_GYARADOS",
    bytes.fromhex("6a01"): "362 CAUGHT_RED_GYARADOS",
    bytes.fromhex("ca00"): "202 flag",
    bytes.fromhex("7101"): "369 MART_MAHOGANY",
    bytes.fromhex("f201"): "498 HIDE_SHADY",
    bytes.fromhex("3b09"): "2459 ROCKET_TAKEOVER",
}
for path in sorted(root.glob("2_*")):
    data = path.read_bytes()
    hits = []
    for needle, label in needles.items():
        if needle in data:
            hits.append(f"{label}@{data.index(needle)}")
    if hits:
        print(f"{path.name} ({len(data)}): {hits}")
