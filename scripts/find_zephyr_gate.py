#!/usr/bin/env python3
"""Find scr_seq members that check BADGE_ZEPHYR (0)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A012 = ROOT / "build/a012"
A032 = ROOT / "build/a032"


def decode(data: bytes, start: int, limit: int = 30) -> None:
    i = start
    end = min(len(data), start + 120)
    n = 0
    while i < end and n < limit:
        op = struct.unpack_from("<H", data, i)[0]
        i += 2
        n += 1
        if op in (0, 2):
            print("  end")
            return
        if op == 294:
            badge, var = struct.unpack_from("<HH", data, i)
            i += 4
            print(f"  check_badge {badge} -> var {var}")
        elif op == 296:
            var = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  count_badges -> var {var}")
        elif op == 17:
            var, val = struct.unpack_from("<HI", data, i)
            i += 6
            print(f"  cmpvar {var:#x} == {val}")
        elif op == 28:
            cond = struct.unpack_from("<B", data, i)[0]
            rel = struct.unpack_from("<i", data, i + 1)[0]
            i += 5
            print(f"  goto_if cond={cond} rel={rel}")
        elif op == 45:
            msg = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  npc_msg {msg}")
        elif op == 101:
            pid = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  hide_person {pid}")
        elif op == 30:
            fid = struct.unpack_from("<H", data, i)[0]
            i += 2
            print(f"  setflag {fid}")
        else:
            print(f"  op {op}")
            return


def main() -> None:
    pat = struct.pack("<HH", 294, 0)
    for p in sorted(A012.glob("2_*")):
        data = p.read_bytes()
        if pat not in data or len(data) > 20000:
            continue
        print(f"\n=== scr_seq {p.name} ({len(data)}b) ===")
        idx = 0
        while True:
            i = data.find(pat, idx)
            if i < 0:
                break
            decode(data, max(0, i - 8))
            idx = i + 1

    print("\n=== zone_event Route 32 area (038?) ===")
    for name in ("038", "039", "040", "041", "042"):
        ze = A032 / f"2_{name}"
        if not ze.is_file():
            continue
        data = ze.read_bytes()
        pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20 + 4
        ob = struct.unpack_from("<I", data, pos - 4)[0]
        pos -= 4
        print(f"\n{name}: {ob} objects")
        for i in range(ob):
            pos += 4
            f = struct.unpack_from("<14H", data, pos)
            if f[1] in (328, 330, 332, 347) or f[5] < 20:
                print(
                    f"  obj{i}: id={f[0]} spr={f[1]} flag={f[4]} scr={f[5]} "
                    f"x={f[12]} z={f[13]}"
                )
            pos += 28


if __name__ == "__main__":
    main()
