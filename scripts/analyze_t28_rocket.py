#!/usr/bin/env python3
"""Analyze Mahogany rocket skip patch gaps."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def scr_slot_count(data: bytes) -> int:
    pos = 0
    count = 0
    while pos + 2 <= len(data):
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return count
        count += 1
        pos += 4
    return count


def decode_script(data: bytes, start: int, end: int, label: str) -> None:
    print(f"\n=== {label} [{start}:{end}] ({end - start}b) ===")
    i = start
    while i < min(end, len(data)):
        op = struct.unpack_from("<H", data, i)[0]
        i += 2
        if op in (0, 2):
            print(f"  {'end' if op == 0 else 'scr_end'}")
            return
        if op == 30:
            print(f"  setflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 31:
            print(f"  clearflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 32:
            print(f"  checkflag {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        elif op == 41:
            v, vv = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  setvar {v:#x}={vv}")
        elif op == 17:
            v, vv = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  cmpvar {v:#x}=={vv}")
        elif op == 28:
            c = data[i]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            i += 5
            print(f"  goto_if cond={c} rel={rel}")
        elif op == 11:
            print("  lock")
        elif op == 12:
            print("  release")
        elif op == 45:
            print(f"  msg {struct.unpack_from('<H', data, i)[0]}")
            i += 2
        else:
            print(f"  op {op} @{i - 2}")
            return


def dump_slots(path: Path, label: str) -> None:
    data = path.read_bytes()
    count = scr_slot_count(data)
    print(f"\n### {label} {path.name} size={len(data)} scripts={count}")
    end0 = script_offset(data, 0)
    for i in range(count):
        start = script_offset(data, i)
        end = script_offset(data, i + 1) if i + 1 < count else end0
        print(f"  slot {i} (scriptId {i+1}): {start}-{end} ({end-start}b)")


def decode_objects(path: Path) -> None:
    data = path.read_bytes()
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
    (obj_count,) = struct.unpack_from("<I", data, pos - 4)
    print(f"\n### zone_event {path.name} objects={obj_count}")
    for i in range(obj_count):
        vals = struct.unpack_from("<14H", data, pos)
        print(
            f"  obj{i}: id={vals[0]} spr={vals[1]} mov={vals[2]} type={vals[3]} "
            f"p4={vals[4]} scr={vals[5]} face={vals[6]} p7={vals[7]} flag={vals[8]} "
            f"x={vals[12]} z={vals[13]}"
        )
        pos += 32


def find_var_checks(root: Path, var_id: int) -> None:
    needle = struct.pack("<H", 17) + struct.pack("<H", var_id)
    print(f"\n### cmpvar {var_id:#x} in scr_seq")
    for path in sorted(root.glob("2_*")):
        data = path.read_bytes()
        if needle not in data:
            continue
        idx = 0
        while True:
            i = data.find(needle, idx)
            if i < 0:
                break
            vv = struct.unpack_from("<H", data, i + 4)[0]
            print(f"  {path.name} @{i}: cmp {var_id:#x}=={vv}")
            idx = i + 1


def find_flag_checks(root: Path, flag_id: int) -> None:
    for op, name in ((32, "checkflag"), (30, "setflag"), (31, "clearflag")):
        needle = struct.pack("<H", op) + struct.pack("<H", flag_id)
        hits = []
        for path in sorted(root.glob("2_*")):
            if needle in path.read_bytes():
                hits.append(path.name)
        if hits:
            print(f"  {name} {flag_id}: {', '.join(hits[:20])}" + (" ..." if len(hits) > 20 else ""))


def find_scr_end(data: bytes, start: int) -> int:
    i = start
    while i + 2 <= len(data):
        op = struct.unpack_from("<H", data, i)[0]
        if op == 2:
            return i + 2
        if op == 0:
            return i + 2
        i += 2
        # skip common operand sizes
        if op in (30, 31, 32, 45):
            i += 2
        elif op in (17, 41):
            i += 4
        elif op == 28:
            i += 5
        elif op >= 100:
            i += 2  # rough skip
    return len(data)


def dump_offset_table(path: Path) -> None:
    data = path.read_bytes()
    print(f"\n### offset table {path.name}")
    for i in range(scr_slot_count(data)):
        rel = struct.unpack_from("<i", data, i * 4)[0]
        print(f"  slot{i}: rel={rel} abs={i * 4 + 4 + rel}")


def main() -> None:
    a012 = ROOT / "build/a012"
    a032 = ROOT / "build/a032"
    vanilla = ROOT / "build/a012_vanilla/2_930"

    dump_offset_table(a012 / "2_930")
    dump_slots(a012 / "2_930", "T28 Mahogany")
    if vanilla.is_file():
        dump_slots(vanilla, "T28 vanilla")
        v = vanilla.read_bytes()
        p = (a012 / "2_930").read_bytes()
        vs = script_offset(v, 5)
        ve = script_offset(v, 6)
        print(f"\nVanilla slot5 span: {vs}-{ve} ({ve-vs}b)")
        print(f"Patched slot5 start: {script_offset(p, 5)}")

    decode_objects(a032 / "2_084")

    d930 = (a012 / "2_930").read_bytes()
    for slot, name in [(0, "obj0 script1"), (2, "obj1 script3 gym blocker?"), (3, "obj3 script4"), (4, "obj2 script5 rage?"), (5, "OnLoad slot5")]:
        s = script_offset(d930, slot)
        e = find_scr_end(d930, s)
        decode_script(d930, s, e, f"T28 slot{slot} {name}")

    for idx, label in [(932, "Gym T28GYM"), (937, "Shop T28R0201?"), (938, "R43 gate?"), (90, "shop/onload 090"), (149, "149"), (885, "885 rocket hub")]:
        p = a012 / f"2_{idx:03d}"
        if not p.is_file():
            continue
        data = p.read_bytes()
        if len(data) < 20:
            continue
        print(f"\n### scr_seq {idx} ({label}) size={len(data)}")
        count = min(scr_slot_count(data), 8)
        for i in range(count):
            s = script_offset(data, i)
            e = find_scr_end(data, s)
            if i < 3 or idx in (90, 938):
                decode_script(data, s, e, f"  slot{i}")

    # Route 43 gate - search members referencing flags 506/507 or 1000 money
    print("\n### Flag 439-444, 506, 507, 487, 498 usage")
    for fid in range(439, 445):
        find_flag_checks(a012, fid)
    for fid in [487, 498, 504, 506, 507, 369, 2459, 488, 489]:
        find_flag_checks(a012, fid)

    find_var_checks(a012, 0x4077)

    # Find Route 43 gate scr_seq by scanning for FLAG_HIDE_ROUTE_43
    for path in sorted(a012.glob("2_*")):
        data = path.read_bytes()
        if b"\xfa\x01" in data or struct.pack("<H", 32) + struct.pack("<H", 506) in data:
            if 506 in [struct.unpack_from("<H", data, i + 2)[0]
                       for i in range(len(data) - 4)
                       if struct.unpack_from("<H", data, i)[0] == 32]:
                print(f"  Route43 flag check in {path.name} ({len(data)}b)")

    # Scan for 1000 (0x03E8) submoney / hasenoughmoney
    print("\n### Members with 1000 (0x03E8) immediate")
    for path in sorted(a012.glob("2_*")):
        data = path.read_bytes()
        if b"\xe8\x03" in data:
            print(f"  {path.name} ({len(data)}b)")

    # init headers for key members
    print("\n### init headers")
    for idx in [703, 930, 932, 937, 938, 90, 149, 885, 85]:
        p = a012 / f"2_{idx:03d}"
        if p.is_file() and p.stat().st_size <= 200:
            data = p.read_bytes()
            pos = 0
            entries = []
            while pos + 4 <= len(data):
                if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
                    break
                t, sid = struct.unpack_from("<HH", data, pos)
                entries.append((t, sid))
                pos += 4
            print(f"  {p.name} ({p.stat().st_size}b): {entries}")

    decode_objects(a032 / "2_090" if (a032 / "2_090").is_file() else a032 / "2_084")
    for ze in ["085", "090", "142", "938"]:
        p = a032 / f"2_{ze}"
        if p.is_file():
            decode_objects(p)


if __name__ == "__main__":
    main()
