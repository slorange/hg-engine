#!/usr/bin/env python3
"""Verify the linked entry tables used by the resident evolution dispatchers."""
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def symbols(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[-1]: int(parts[0], 16) for line in output.splitlines()
            if len(parts := line.split()) >= 3}

def main():
    rom = (ROOT / "test.nds").read_bytes()
    overlay_offset = struct.unpack_from("<I", rom, 0x50)[0]
    fat_offset = struct.unpack_from("<I", rom, 0x48)[0]
    def packed_overlay(overlay_id, address):
        entry = struct.unpack_from("<8I", rom, overlay_offset + overlay_id * 32)
        assert entry[0] == overlay_id and entry[1] == address
        start, end = struct.unpack_from("<2I", rom, fat_offset + entry[6] * 8)
        return rom[start:end]
    names = ("GetMonEvolutionInternal", "GetStoneLevelEvolutionRequirementInternal",
             "PartyMenu_PrintEvoStoneCompatStringInternal")
    for variant, address, capacity, overlay_id in [("GetMonEvolutionInternal", 0x023C0400, 0x3C00, 133),
                                        ("GetMonEvolutionBattle", 0x021FBE60, 0xDD00, 134)]:
        table = symbols(ROOT / f"build/{variant}_linked.o")
        data = (ROOT / f"build/output_{variant}.bin").read_bytes()
        assert table["gEvolutionOverlayApi"] == address, (variant, table["gEvolutionOverlayApi"])
        assert len(data) <= capacity, (variant, len(data), capacity)
        pointers = struct.unpack_from("<3I", data)
        assert pointers == tuple(table[name] | 1 for name in names), (variant, pointers)
        assert all(address <= (pointer & ~1) < address + len(data) for pointer in pointers)
        assert packed_overlay(overlay_id, address) == data, (variant, "packed ROM differs")
        print(f"PASS: {variant} API at {address:#010x}, three valid Thumb entries, {len(data)}/{capacity} bytes.")
    root = symbols(ROOT / "build/linked.o")
    assert all(name not in root for name in names)
    assert all(name in root for name in ("OpenEvolutionOverlay", "CloseEvolutionOverlay",
                "GetMonEvolution", "GetStoneLevelEvolutionRequirement", "PartyMenu_PrintEvoStoneCompatString"))
    blob = (ROOT / "build/output.bin").stat().st_size
    packed_root = packed_overlay(129, 0x023D6000)
    assert packed_root[0x60:0x60 + blob] == (ROOT / "build/output.bin").read_bytes()
    assert blob <= 0xA000 - 0x60
    print(f"PASS: relocated implementations absent from overlay 129; resident blob {blob} bytes, {0xA000 - 0x60 - blob} bytes free.")

if __name__ == "__main__":
    main()
