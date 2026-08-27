#!/usr/bin/env python3
"""Map shop/gate zone_event to scr_seq members."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A012 = ROOT / "build/a012"
A032 = ROOT / "build/a032"


def parse_hdr(path: Path) -> list[tuple[int, int]]:
    data = path.read_bytes()
    pos = 0
    out = []
    while pos + 4 <= len(data):
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            break
        t, sid = struct.unpack_from("<HH", data, pos)
        out.append((t, sid))
        pos += 4
    return out


def script_offset(data: bytes, index: int) -> int:
    return index * 4 + 4 + struct.unpack_from("<i", data, index * 4)[0]


def scan_money_and_flags(path: Path) -> None:
    d = path.read_bytes()
    hits = []
    for i in range(len(d) - 4):
        op = struct.unpack_from("<H", d, i)[0]
        if op == 32:
            f = struct.unpack_from("<H", d, i + 2)[0]
            if f in (506, 507, 487, 498, 504, 369, 197, 198, 202, 206, 488, 489, 505):
                hits.append(f"chk{f}@{i}")
        if op == 17:
            v = struct.unpack_from("<H", d, i + 2)[0]
            if v == 0x4077:
                vv = struct.unpack_from("<H", d, i + 4)[0]
                hits.append(f"cmp4077={vv}@{i}")
    if b"\xe8\x03" in d:
        hits.append("has1000")
    if hits:
        print(f"  {path.name} ({len(d)}b): {', '.join(hits[:12])}")


print("=== Key file sizes ===")
for idx in [84, 113, 149, 231, 255, 256, 88, 90, 149, 255, 500, 710, 930, 937, 254]:
    for base in [A012, A032]:
        p = base / f"2_{idx:03d}"
        if p.is_file():
            print(f"  {base.name}/{p.name}: {p.stat().st_size}b")

print("\n=== Init headers ===")
for idx in [500, 710, 499, 703, 149, 231, 113, 255]:
    p = A012 / f"2_{idx:03d}"
    if p.is_file() and p.stat().st_size <= 64:
        print(f"  {p.name}: {parse_hdr(p)}")

print("\n=== scr_seq flag/money scan (113,231,254,255,256,88,90,937) ===")
for idx in [113, 231, 254, 255, 256, 88, 90, 937, 885, 34]:
    p = A012 / f"2_{idx:03d}"
    if p.is_file():
        scan_money_and_flags(p)

print("\n=== zone_event 113 shop interior ===")
data = (A032 / "2_113").read_bytes()
pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
(n,) = struct.unpack_from("<I", data, pos - 4)
for i in range(n):
    v = struct.unpack_from("<14H", data, pos)
    print(f"  obj{i}: spr={v[1]} evflag={v[4]} scr={v[5]} x={v[12]} z={v[13]}")
    pos += 32

print("\n=== zone_event 231 R43 gate ===")
data = (A032 / "2_231").read_bytes()
pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
(n,) = struct.unpack_from("<I", data, pos - 4)
for i in range(n):
    v = struct.unpack_from("<14H", data, pos)
    print(f"  obj{i}: spr={v[1]} evflag={v[4]} scr={v[5]} x={v[12]} z={v[13]}")
    pos += 32

# decode 113 scr_seq onload if exists
for idx in [113, 231, 254]:
    p = A012 / f"2_{idx:03d}"
    if not p.is_file() or p.stat().st_size > 5000:
        continue
    d = p.read_bytes()
    pos = 0
    count = 0
    while struct.unpack_from("<H", d, pos)[0] != 0xFD13:
        count += 1
        pos += 4
    print(f"\n=== scr_seq {idx} slots={count} ===")
    for s in range(min(count, 8)):
        start = script_offset(d, s)
        chunk = d[start : start + 60]
        print(f"  slot{s}@{start}: {chunk[:40].hex()}")
