#!/usr/bin/env python3
"""Probe Route 44 NARC member indices (zone_event, scr_seq, text)."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE_DIR = ROOT / "build/a032"
SCR_DIR = ROOT / "build/a012"
HDR_DIR = ROOT / "build/map_headers"


def ensure_extracted() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "tools/extract_zone_event_vanilla.py"), str(ZONE_DIR)])
    subprocess.check_call([sys.executable, str(ROOT / "tools/extract_scr_seq_vanilla.py"), str(SCR_DIR)])
    if not HDR_DIR.is_dir():
        subprocess.check_call(
            [sys.executable, str(ROOT / "tools/narcpy.py"), "extract", str(ROOT / "base/root/a/0/4/1"), "-o", str(HDR_DIR), "-nf"]
        )


def dump_objects(member: str) -> None:
    data = (ZONE_DIR / f"2_{member}").read_bytes()
    pos = 0
    bg_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4 + bg_count * 20
    obj_count = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    print(f"\nzone_event member {member}: {obj_count} objects, {len(data)} bytes")
    for _ in range(obj_count):
        fields = struct.unpack_from("<14H", data, pos)
        print(
            f"  id={fields[0]:3d} sprite={fields[1]:4d} script={fields[5]:4d} "
            f"facing={fields[6]} x={fields[12]} z={fields[13]}"
        )
        pos += 32


def slot_body(data: bytes, slot: int) -> bytes:
    pos = 0
    count = 0
    while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        count += 1
        pos += 4
    start = struct.unpack_from("<i", data, slot * 4)[0] + slot * 4 + 4
    starts = [struct.unpack_from("<i", data, j * 4)[0] + j * 4 + 4 for j in range(count)]
    end = min((s for s in starts if s > start), default=len(data))
    return data[start:end]


def npc_msg_indices(body: bytes) -> list[int]:
    indices: list[int] = []
    i = 0
    while i + 1 < len(body):
        op = struct.unpack_from("<H", body, i)[0]
        i += 2
        if op == 0:
            break
        if op == 45:
            indices.append(body[i])
            i += 1
        elif op in (17, 41, 40):
            i += 4
        elif op == 22:
            i += 4
        elif op == 28:
            i += 5
        elif op in (36, 37):
            i += 6
        elif op in (125, 128):
            i += 6
        elif op == 20:
            i += 2
        else:
            i += 2
    return indices


def count_scr_scripts(member: int) -> int:
    data = (SCR_DIR / f"2_{member:03d}").read_bytes()
    pos = 0
    count = 0
    while pos + 2 <= len(data) and pos < 512:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return count
        count += 1
        pos += 4
    return -1


def read_map_header_index(index: int) -> tuple[int, bytes] | None:
    raw = (ROOT / "base/root/a/0/4/1").read_bytes()
    # HGSS map headers are stored sequentially, 24 bytes each (pret fielddata).
    size = 24
    if len(raw) % size != 0:
        return None
    off = index * size
    if off + size > len(raw):
        return None
    return off, raw[off : off + size]


def main() -> int:
    ensure_extracted()
    print("MAP_R44 header index (maps.h):", 46)
    print("DSPRE map list index 102 is NOT the same as map header / NARC member indices.")
    for member in ("046", "090"):
        dump_objects(member)

    n46 = count_scr_scripts(46)
    print(f"\nscr_seq 046: {n46} vanilla scripts → append slot {n46} (scriptId {n46 + 1})")
    scr = (SCR_DIR / "2_046").read_bytes()
    for slot in range(n46):
        msgs = npc_msg_indices(slot_body(scr, slot))
        print(f"  slot {slot} (scriptId {slot + 1}): npc_msg indices {msgs}")

    parsed = read_map_header_index(46)
    if parsed:
        off, hdr = parsed
        u16 = struct.unpack_from("<12H", hdr)
        print(f"\nmap header 46 @ byte {off} u16: {u16}")
        # pret order: matrix, area, ... events @ index varies; scr @ 5, events @ 6 in some dumps
        print(f"  fields[4..7]: events={u16[4]}, scripts={u16[5]}, textures={u16[6]}, ?={u16[7]}")
    else:
        print("\nmap header 46: could not parse sequential header table")

    print(
        "\nPlacement note: vanilla junction NPCs exist in BOTH zone_event 046 and matrix 090 "
        "at the same world coords. Fishing NPCs along the route body live in 090 with shared "
        "outdoor scripts (3000+), not scr_seq 046."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
