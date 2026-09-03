#!/usr/bin/env python3
"""List canonical hg-engine species by generation (national dex)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
species_h = (ROOT / "include/constants/species.h").read_text(encoding="utf-8")

GEN_RANGES = [
    ("Gen 1", 1, 151),
    ("Gen 2", 152, 251),
    ("Gen 3", 252, 386),
    ("Gen 4", 387, 493),
    ("Gen 5", 494, 649),
    ("Gen 6", 650, 721),
    ("Gen 7", 722, 809),
    ("Gen 8", 810, 905),
    ("Gen 9", 906, 1025),
]

SKIP = {"NONE", "EGG", "BAD_EGG"}


def species_id_to_natdex(sid: int) -> int | None:
    if 1 <= sid <= 493:
        return sid
    if sid >= 544:
        return sid - 50
    return None  # 494-543 placeholders


def gen_for_natdex(n: int) -> str:
    for name, lo, hi in GEN_RANGES:
        if lo <= n <= hi:
            return name
    return "Other"


entries: list[tuple[int, str, int]] = []
for m in re.finditer(r"#define SPECIES_([A-Z0-9_]+)\s+(\d+)\s*$", species_h, re.M):
    name, sid = m.group(1), int(m.group(2))
    if name in SKIP or re.fullmatch(r"\d+", name):
        continue
    if sid > 1075:  # MAX_CANONICAL_MON_NUM
        continue
    nat = species_id_to_natdex(sid)
    if nat is None:
        continue
    entries.append((nat, name, sid))

entries.sort()
by_gen: dict[str, list[tuple[int, str]]] = {g[0]: [] for g in GEN_RANGES}
for nat, name, _sid in entries:
    g = gen_for_natdex(nat)
    if g in by_gen:
        by_gen[g].append((nat, name))

for gname, lo, hi in GEN_RANGES:
    mons = by_gen[gname]
    print(f"\n=== {gname} (#{lo}-#{hi}): {len(mons)} species in engine ===")
    if gname in ("Gen 1", "Gen 2", "Gen 3", "Gen 4"):
        continue  # skip printing full gen 1-4
    for nat, name in mons:
        print(f"  #{nat:4d}  {name.replace('_', ' ').title()}")

print(f"\nTotal canonical base species (excl. forms): {len(entries)}")
print(f"Through national dex #{max(n for n, _, _ in entries)}")
