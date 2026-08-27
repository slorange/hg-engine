#!/usr/bin/env python3
"""Search scr_seq member for Mom item-give patterns."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
base = ROOT / "build/a012"

# giveitem_no_check uses callstd std_give_item_verbose after item_vars
# GivePokedex = halfword 291 (0x123)
# give_running_shoes = halfword 293
# setflag patterns

ITEM_SS_TICKET = 456
ITEM_PASS = 480
ITEM_APRICORN_BOX = 468

needles = {
    struct.pack("<H", 291): "GivePokedex",
    struct.pack("<H", 293): "give_running_shoes",
    struct.pack("<HH", 456, 1): None,  # item id in script varies
}

for path in sorted(base.glob("2_*")):
    data = path.read_bytes()
    hits = []
    if struct.pack("<H", 291) in data:
        hits.append("GivePokedex")
    if struct.pack("<H", 293) in data:
        hits.append("running_shoes")
    # Pokegear registration fanfare / flag 156 - search setflag for 156 = 0x9C
    if b"\x9c\x00" in data or struct.pack("<H", 156) in data:
        if "156" not in str(hits):
            hits.append("flag156?")
    if hits and any(x in path.name for x in ["60", "61", "62", "957", "962", "834"]):
        print(path.name, hits)

print("--- members with GivePokedex ---")
for path in sorted(base.glob("2_*")):
    data = path.read_bytes()
    if struct.pack("<H", 291) in data:
        idx = data.find(struct.pack("<H", 291))
        print(f"{path.name}: GivePokedex @ {idx:#x}, size {len(data)}")
