#!/usr/bin/env python3
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = (ROOT / "base/arm9.bin").read_bytes()
BASE = 0x02000000


def thumb_bl_dest(off: int) -> int | None:
    if off + 4 > len(data):
        return None
    hw1 = struct.unpack_from("<H", data, off)[0]
    hw2 = struct.unpack_from("<H", data, off + 2)[0]
    if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xD000) != 0xD000:
        return None
    s = (hw1 & 0x800) >> 10
    imm10 = hw1 & 0x7FF
    imm11 = hw2 & 0x7FF
    imm32 = (imm10 << 12) | (imm11 << 1)
    if s:
        imm32 |= ~0xFFFFF
    return (off + BASE + 4 + imm32) & 0xFFFFFFFF


targets = {
    0x020274A8: "Save_InitDynamicRegion",
    0x02027FA8: "Save_InitDynamicRegion_Internal",
}

for target, name in targets.items():
    hits = []
    for off in range(0, len(data) - 4, 2):
        dest = thumb_bl_dest(off)
        if dest == target:
            hits.append(off + BASE)
    print(f"{name}: {len(hits)} callers")
    for addr in hits[:8]:
        print(f"  from {addr:#x}")
