#!/usr/bin/env python3
"""Verify build-time field pointer patches in overlay 129 output.bin."""

from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIELD_ELF = ROOT / "build/field_linked.o"
OVERLAY_ELF = ROOT / "build/linked.o"
OUTPUT_BIN = ROOT / "build/output.bin"
OVERLAY129_LOAD = 0x023D8000 + 0x60

PATCHES = (
    ("LevelUpEvoTablesFieldAddr", "sLevelUpEvoTablesData"),
    ("SyntheticEvoEdgesFieldAddr", "sSyntheticEvoEdgesData"),
    ("WildLevelCapsFieldAddr", "sWildLevelCaps"),
    ("WildSpeciesHeldCommonFieldAddr", "sWildSpeciesHeldCommon"),
    ("WildSpeciesHeldRareFieldAddr", "sWildSpeciesHeldRare"),
)


def nm_address(elf: Path, symbol: str) -> int:
    out = subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True)
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[2] == symbol:
            return int(parts[0], 16)
    raise SystemExit(f"Symbol {symbol} not found in {elf}")


def main() -> None:
    for path in (FIELD_ELF, OVERLAY_ELF, OUTPUT_BIN):
        if not path.is_file():
            print(f"verify_overlay129_field_addrs: missing {path}", file=sys.stderr)
            sys.exit(1)

    data = OUTPUT_BIN.read_bytes()
    ok = True
    for slot_sym, field_sym in PATCHES:
        slot_vma = nm_address(OVERLAY_ELF, slot_sym)
        field_addr = nm_address(FIELD_ELF, field_sym)
        offset = slot_vma - OVERLAY129_LOAD
        if offset < 0 or offset + 4 > len(data):
            print(f"FAIL {slot_sym}: patch offset 0x{offset:X} out of range (bin {len(data)} bytes)")
            ok = False
            continue
        got = struct.unpack_from("<I", data, offset)[0]
        if got != field_addr:
            print(
                f"FAIL {slot_sym} @ bin+0x{offset:X}: got 0x{got:08X}, expected 0x{field_addr:08X} ({field_sym})"
            )
            ok = False
        else:
            print(f"OK   {slot_sym} = 0x{field_addr:08X}")

    if not ok:
        sys.exit(1)
    print("verify_overlay129_field_addrs: OK")


if __name__ == "__main__":
    main()
