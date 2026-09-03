#!/usr/bin/env python3
"""Count Gen 1-4 species with Fairy typing in data/Species.c."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
species_c = (ROOT / "data/Species.c").read_text(encoding="utf-8")
species_h = (ROOT / "include/constants/species.h").read_text(encoding="utf-8")

ids: dict[str, int] = {}
for m in re.finditer(r"#define SPECIES_([A-Z0-9_]+)\s+(\d+)\s*$", species_h, re.M):
    name, num = m.group(1), int(m.group(2))
    if num <= 493:
        ids[name] = num

blocks = re.split(r"\[SPECIES_([A-Z0-9_]+)\]\s*=\s*\{", species_c)
fairy_mons: list[tuple[int, str, str, str, str]] = []
for i in range(1, len(blocks), 2):
    name = blocks[i]
    body = blocks[i + 1]
    if name not in ids:
        continue
    tm = re.search(r"\.types\s*=\s*\{\s*(TYPE_[A-Z_]+)\s*,\s*(TYPE_[A-Z_]+)\s*\}", body)
    if not tm:
        continue
    t1, t2 = tm.group(1), tm.group(2)
    if "TYPE_FAIRY" not in (t1, t2):
        continue
    display = re.search(r'\.name\s*=\s*"([^"]+)"', body)
    fairy_mons.append((ids[name], name, display.group(1) if display else name, t1, t2))

fairy_mons.sort()
pure = [m for m in fairy_mons if m[3] == m[4] == "TYPE_FAIRY"]
dual = [m for m in fairy_mons if m not in pure]

print(f"Gen 1-4 (national dex 1-493) with Fairy typing: {len(fairy_mons)}")
print(f"  Pure Fairy: {len(pure)}")
print(f"  Fairy + other: {len(dual)}")
print()
for dex, _const, disp, t1, t2 in fairy_mons:
    if t1 == t2:
        types = t1.replace("TYPE_", "")
    else:
        types = f"{t1.replace('TYPE_', '')}/{t2.replace('TYPE_', '')}"
    print(f"{dex:3d}  {disp:16s}  {types}")
