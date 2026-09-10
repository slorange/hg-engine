#!/usr/bin/env python3
"""Verify rod guru script in scr_seq 257 slot 3 (scriptId 4)."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rod_guru_patch_checks import validate_rod_guru_body, ValueExit

GURU_SLOT = 3


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


path = Path(sys.argv[1])
data = path.read_bytes()
print(f"{path}: {len(data)} bytes")

body = slot_body(data, GURU_SLOT)
print(f"  slot {GURU_SLOT} (scriptId {GURU_SLOT + 1}): {len(body)}b")

try:
    validate_rod_guru_body(body, f"slot {GURU_SLOT}")
except ValueExit as exc:
    raise SystemExit(str(exc)) from exc

print("OK")
