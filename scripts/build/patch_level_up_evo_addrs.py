#!/usr/bin/env python3
"""Patch overlay 129 with the runtime address of field-overlay level-up tables."""

import argparse
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY129_LOAD = 0x023D8000
OVERLAY129_FILE_SKIP = 0x60
TABLE_SYMBOL = "sLevelUpEvoTablesData"
ADDR_SYMBOL = "LevelUpEvoTablesFieldAddr"


def nm_address(elf: Path, symbol: str) -> int:
    out = subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True)
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[2] == symbol:
            return int(parts[0], 16)
    raise SystemExit(f"Symbol {symbol} not found in {elf}")


def overlay129_bin_offset(vma: int) -> int:
    return vma - OVERLAY129_LOAD - OVERLAY129_FILE_SKIP


def patch_overlay_bin(bin_path: Path, var_vma: int, table_addr: int):
    offset = overlay129_bin_offset(var_vma)
    data = bytearray(bin_path.read_bytes())
    if offset < 0 or offset + 4 > len(data):
        raise SystemExit(f"Patch offset 0x{offset:X} out of range for {bin_path} ({len(data)} bytes)")
    struct.pack_into("<I", data, offset, table_addr)
    bin_path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--field-elf", type=Path, default=ROOT / "build/field_linked.o")
    parser.add_argument("--overlay-elf", type=Path, default=ROOT / "build/linked.o")
    parser.add_argument("--overlay-bin", type=Path, default=ROOT / "build/output.bin")
    args = parser.parse_args()

    for path in (args.field_elf, args.overlay_elf, args.overlay_bin):
        if not path.is_file():
            print(f"Skip level-up table patch: missing {path}", file=sys.stderr)
            return

    table_addr = nm_address(args.field_elf, TABLE_SYMBOL)
    var_vma = nm_address(args.overlay_elf, ADDR_SYMBOL)
    patch_overlay_bin(args.overlay_bin, var_vma, table_addr)
    print(f"Patched {args.overlay_bin}: {ADDR_SYMBOL} @ 0x{var_vma:08X} = 0x{table_addr:08X}")


if __name__ == "__main__":
    main()
