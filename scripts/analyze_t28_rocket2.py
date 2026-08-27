#!/usr/bin/env python3
"""Deep dive: shop, route43 gate, gym blocker flags."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A012 = ROOT / "build/a012"
A032 = ROOT / "build/a032"


def script_offset(data: bytes, index: int) -> int:
    rel = struct.unpack_from("<i", data, index * 4)[0]
    return index * 4 + 4 + rel


def scr_slot_count(data: bytes) -> int:
    pos = 0
    count = 0
    while pos + 2 <= len(data):
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return count
        count += 1
        pos += 4
    return count


def scan_ops(data: bytes, start: int, limit: int = 300) -> None:
    i = start
    end = min(len(data), start + limit)
    while i < end:
        op = struct.unpack_from("<H", data, i)[0]
        pos = i
        i += 2
        if op in (0, 2):
            print(f"  @{pos}: {'end' if op == 0 else 'scr_end'}")
            return
        if op == 30:
            print(f"  @{pos}: setflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 31:
            print(f"  @{pos}: clearflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 32:
            print(f"  @{pos}: checkflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 41:
            v, vv = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  @{pos}: setvar {v:#x}={vv}")
        elif op == 17:
            v, vv = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  @{pos}: cmpvar {v:#x}=={vv}")
        elif op == 28:
            c = data[i]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            i += 5
            print(f"  @{pos}: goto_if cond={c} rel={rel}")
        elif op == 45:
            print(f"  @{pos}: msg {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 73:
            print(f"  @{pos}: callstd 73 (mart?)")
        else:
            print(f"  @{pos}: op {op}")
            return


def find_members_with(checks: list[tuple[int, int]]) -> None:
    for path in sorted(A012.glob("2_*")):
        data = path.read_bytes()
        for op, arg in checks:
            pat = struct.pack("<HH", op, arg)
            if pat in data:
                print(f"{path.name} ({len(data)}b): op{op} arg={arg}")


def decode_zone(path: Path) -> None:
    data = path.read_bytes()
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
    (n,) = struct.unpack_from("<I", data, pos - 4)
    print(f"\n{path.name} ({n} objs, {len(data)}b)")
    for i in range(n):
        v = struct.unpack_from("<14H", data, pos)
        print(
            f"  obj{i}: id={v[0]} spr={v[1]} mov={v[2]} evflag={v[4]} scr={v[5]} "
            f"x={v[12]} z={v[13]}"
        )
        pos += 32


print("=== Members referencing shop/rocket flags ===")
for fid in [487, 498, 504, 369, 2459, 505, 506, 507, 488, 489, 517]:
    find_members_with([(32, fid), (30, fid), (31, fid)])

print("\n=== Members with cmp 0x4077 and checkflag 506 ===")
for path in sorted(A012.glob("2_*")):
    d = path.read_bytes()
    if b"\x77\x40" in d and (b"\xfa\x01" in d or b"\xfb\x01" in d):
        print(f"  {path.name} ({len(d)}b)")

print("\n=== scr_seq 090 OnLoad / rocket shop scripts ===")
d = (A012 / "2_090").read_bytes()
count = scr_slot_count(d)
print(f"slots={count}")
for i in range(min(count, 15)):
    s = script_offset(d, i)
    print(f"\n-- slot {i} @ {s} --")
    scan_ops(d, s, 200)

print("\n=== Route43 gate candidates (1000 fee, flags 506/507) ===")
for idx in [85, 119, 122, 123, 124, 256, 803, 804, 906, 910]:
    p = A012 / f"2_{idx:03d}"
    if not p.is_file():
        continue
    data = p.read_bytes()
    has_fee = b"\xe8\x03" in data
    has506 = struct.pack("<HH", 32, 506) in data or struct.pack("<HH", 30, 506) in data
    has507 = struct.pack("<HH", 31, 507) in data or struct.pack("<HH", 32, 507) in data
    if has_fee or has506 or has507:
        print(f"\n2_{idx:03d} size={len(data)} fee={has_fee} chk506={has506} fl507={has507}")
        count = scr_slot_count(data)
        for i in range(min(count, 6)):
            s = script_offset(data, i)
            print(f"  slot{i}@{s}:")
            scan_ops(data, s, 80)

for ze in sorted(A032.glob("2_*")):
    data = ze.read_bytes()
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
    (n,) = struct.unpack_from("<I", data, pos - 4)
    pos -= 4
    for i in range(n):
        pos += 4
        v = struct.unpack_from("<14H", data, pos)
        if v[4] in (506, 507, 505, 487, 498, 504):
            print(f"  {ze.name} obj{i}: evflag={v[4]} scr={v[5]} spr={v[1]} x={v[12]} z={v[13]}")
        pos += 28

print("\n=== zone_event 090 149 256 (shop/gate) ===")
for ze in ["090", "149", "256", "119", "122", "255"]:
    p = A032 / f"2_{ze}"
    if p.is_file():
        decode_zone(p)

print("\n=== scr_seq 255 R43R0101 gate ===")
p255 = A012 / "2_255"
if p255.is_file():
    d = p255.read_bytes()
    count = scr_slot_count(d)
    print(f"size={len(d)} slots={count}")
    for i in range(count):
        s = script_offset(d, i)
        print(f"\n-- slot {i} @ {s} --")
        scan_ops(d, s, 120)

print("\n=== scr_seq 937 shop talk ===")
p937 = A012 / "2_937"
if p937.is_file():
    d = p937.read_bytes()
    for i in range(scr_slot_count(d)):
        s = script_offset(d, i)
        print(f"\n-- slot {i} @ {s} --")
        scan_ops(d, s, 80)

print("\n=== scr_seq 088 hideout/shop setup ===")
p088 = A012 / "2_088"
if p088.is_file():
    d = p088.read_bytes()
    count = scr_slot_count(d)
    print(f"size={len(d)} slots={count}")
    for i in range(min(count, 12)):
        s = script_offset(d, i)
        print(f"\n-- slot {i} @ {s} --")
        scan_ops(d, s, 100)

print("\n=== scr_seq 149 onload? ===")
p149 = A012 / "2_149"
if p149.is_file():
    d = p149.read_bytes()
    s = script_offset(d, 0)
    scan_ops(d, s, 200)

# search hideout cleared flag id
print("\n=== search checkflag 198 199 200 201 in 255/254/256 ===")
for idx in [254, 255, 256, 499, 500, 501]:
    p = A012 / f"2_{idx:03d}"
    if not p.is_file():
        continue
    d = p.read_bytes()
    for fid in range(195, 215):
        if struct.pack("<HH", 32, fid) in d:
            print(f"  2_{idx:03d}: checkflag {fid}")
