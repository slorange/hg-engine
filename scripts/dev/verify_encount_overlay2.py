#!/usr/bin/env python3
"""Verify field overlay 2 wild encounter hook sites (SetEncountData / modify_species).

Run after ``make test.nds`` (needs ``base/overlay/overlay_0002.bin`` and ``build/linked.o``).

See HACK-NOTES KB-12.
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "include/config.h"
HOOKS = ROOT / "hooks"
ROM = ROOT / "rom.nds"
NDSTOOL = ROOT / "tools/ndstool"
Y9 = ROOT / "base/overarm9.bin"
O2 = ROOT / "base/overlay/overlay_0002.bin"
LINKED = ROOT / "build/linked.o"

SETENCOUNT_DATA_VMA = 0x02247B64
MODIFY_SPECIES_VMA = 0x02247B42
OVERLAY_INDEX = 2
COMPARE_LEN = 8
BL_HOOK_STUB_LEN = 0x18

# Pret US HeartGold reference (sanity only — compare uses rom.nds extract)
REF_US_SETENCOUNT_PROLOGUE = bytes.fromhex("042cf7db381c0121")


def ecology_generation_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    if re.search(r"^//#define\s+IMPLEMENT_ECOLOGY_GENERATION\b", text, re.MULTILINE):
        return False
    return bool(re.search(r"^#define\s+IMPLEMENT_ECOLOGY_GENERATION\b", text, re.MULTILINE))


def overlay_load_address(index: int) -> int:
    if not Y9.is_file():
        raise SystemExit(f"missing {Y9} — run make first")
    data = Y9.read_bytes()
    off = index * 0x20 + 4
    if off + 4 > len(data):
        raise SystemExit(f"overarm9.bin too small for overlay {index}")
    return struct.unpack_from("<I", data, off)[0]


def nm_thumb_entry(elf: Path, symbol: str) -> int:
    out = subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True)
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[2] == symbol:
            addr = int(parts[0], 16)
            return addr | 1
    raise SystemExit(f"symbol {symbol} not found in {elf}")


def parse_overlay2_hooks() -> dict[int, tuple[str, int]]:
    """Map hook VMA -> (symbol name, register index 0-7 or -1 for bl stub)."""
    if not HOOKS.is_file():
        return {}
    wanted: dict[int, tuple[str, int]] = {}
    for line in HOOKS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 3 or parts[0] != "0002":
            continue
        symbol = parts[1]
        vma = int(parts[2], 16)
        reg = int(parts[3]) if len(parts) >= 4 else 255
        wanted[vma] = (symbol, reg)
    return wanted


def decode_bl_hook_target(stub: bytes, hook_vma: int) -> int:
    """Match scripts/build/make.py Hook(register=255) bl immediate → thumb entry."""
    if len(stub) < 14:
        raise SystemExit("bl hook stub too short")
    if stub[0:2] != bytes([0x60, 0xB4]):
        raise SystemExit(f"expected push {{r4-r6}} at bl hook, got {stub[0:2].hex()}")
    bl_off = 10
    hi = stub[bl_off] | ((stub[bl_off + 1] & 0x07) << 8)
    lo = stub[bl_off + 2] | ((stub[bl_off + 3] & 0x07) << 8)
    immediate = (hi << 11) | lo
    if immediate & 0x400000:
        immediate -= 0x800000
    return (hook_vma + 0xE) + (immediate * 2)


def read_bl_hook(stub: bytes, hook_vma: int) -> tuple[int, bytes]:
    target = decode_bl_hook_target(stub, hook_vma)
    return target | 1, stub


def file_offset(vma: int, load: int) -> int:
    return vma - load


def read_hook_pointer(o2: bytes, vma: int, reg: int, load: int) -> tuple[int, bytes]:
    """Return (thumb target, raw bytes patched at hook site)."""
    hook_at = vma - 1 if (vma & 1) else vma
    off = hook_at - load
    if off < 0 or off + 10 > len(o2):
        raise SystemExit(f"hook VMA {vma:#x} out of range in overlay_0002.bin")

    if reg == 255:
        off = hook_at - load
        if off < 0 or off + BL_HOOK_STUB_LEN > len(o2):
            raise SystemExit(f"bl hook VMA {vma:#x} out of range in overlay_0002.bin")
        raw = o2[off : off + BL_HOOK_STUB_LEN]
        return read_bl_hook(raw, hook_at)

    if hook_at % 4:
        stub = o2[off : off + 6]
        ptr = struct.unpack_from("<I", o2, off + 6)[0]
        raw = o2[off : off + 10]
    else:
        stub = o2[off : off + 4]
        ptr = struct.unpack_from("<I", o2, off + 4)[0]
        raw = o2[off : off + 8]

    expect_bx = bytes([0x00 | (reg << 3), 0x47])
    if stub[2:4] != expect_bx:
        raise SystemExit(
            f"unexpected stub at {vma:#x} (reg r{reg}): {raw.hex()} "
            f"(expected bx r{reg} in halfwords 2-3)"
        )
    if stub[1] != (0x48 | reg):
        raise SystemExit(f"unexpected ldr at {vma:#x}: {stub.hex()} (expected ldr r{reg}, [pc, ...])")

    return ptr, raw


def is_ldr_bx_stub(chunk: bytes) -> bool:
    if len(chunk) < 4:
        return False
    return chunk[2] == 0x47 and (chunk[1] & 0xF8) == 0x48


def is_bl_hook_stub(chunk: bytes) -> bool:
    return len(chunk) >= 2 and chunk[0:2] == bytes([0x60, 0xB4])


def rom_nds_overlay2_bytes() -> bytes | None:
    if not ROM.is_file() or not NDSTOOL.is_file():
        return None
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            [str(NDSTOOL), "-x", str(ROM), "-y", td],
            check=True,
            capture_output=True,
        )
        path = Path(td) / "overlay_0002.bin"
        if not path.is_file():
            return None
        return path.read_bytes()


def main() -> None:
    if not ecology_generation_enabled():
        print("IMPLEMENT_ECOLOGY_GENERATION off — skip verify_encount_overlay2")
        return

    for path in (O2, LINKED):
        if not path.is_file():
            raise SystemExit(f"missing {path} — run make test.nds first")

    load = overlay_load_address(OVERLAY_INDEX)
    o2 = O2.read_bytes()
    rom_o2 = rom_nds_overlay2_bytes()
    rom_se_ref: bytes | None = None
    if rom_o2 is not None:
        rom_off = file_offset(SETENCOUNT_DATA_VMA, load)
        if 0 <= rom_off + COMPARE_LEN <= len(rom_o2):
            rom_se_ref = rom_o2[rom_off : rom_off + COMPARE_LEN]

    hooks = parse_overlay2_hooks()
    ok = True

    def fail(msg: str) -> None:
        nonlocal ok
        print(f"FAIL: {msg}")
        ok = False

    # --- SetEncountData @ 7B64 ---
    se_off = file_offset(SETENCOUNT_DATA_VMA, load)
    se_chunk = o2[se_off : se_off + COMPARE_LEN]
    se_hook = hooks.get(SETENCOUNT_DATA_VMA)

    if se_hook is None:
        if is_bl_hook_stub(se_chunk[:BL_HOOK_STUB_LEN]) or is_ldr_bx_stub(se_chunk):
            fail(
                f"stale hook at SetEncountData {SETENCOUNT_DATA_VMA:#x}: {se_chunk.hex()} — "
                "not listed in hooks; re-extract overlay 2 from rom.nds or restore bytes (KB-12)"
            )
        elif rom_se_ref is not None:
            if se_chunk != rom_se_ref:
                fail(
                    f"SetEncountData {SETENCOUNT_DATA_VMA:#x}: base overlay {se_chunk.hex()} "
                    f"!= rom.nds extract {rom_se_ref.hex()} (run make clean && make test.nds)"
                )
            else:
                print(f"OK   SetEncountData @ {SETENCOUNT_DATA_VMA:#x} matches rom.nds ({se_chunk.hex()})")
        elif se_chunk[: len(REF_US_SETENCOUNT_PROLOGUE)] == REF_US_SETENCOUNT_PROLOGUE:
            print(f"OK   SetEncountData @ {SETENCOUNT_DATA_VMA:#x} US retail prologue")
        else:
            fail(
                f"SetEncountData {SETENCOUNT_DATA_VMA:#x}: {se_chunk.hex()} "
                f"(no rom.nds — expected US ref {REF_US_SETENCOUNT_PROLOGUE.hex()})"
            )
        if rom_se_ref and rom_se_ref != REF_US_SETENCOUNT_PROLOGUE:
            print(
                f"note: rom.nds SetEncountData prologue {rom_se_ref.hex()} "
                f"differs from pret US ref {REF_US_SETENCOUNT_PROLOGUE.hex()}"
            )
    else:
        sym, reg = se_hook
        try:
            got_ptr, raw = read_hook_pointer(o2, SETENCOUNT_DATA_VMA, reg, load)
            expect_ptr = nm_thumb_entry(LINKED, sym)
        except SystemExit as e:
            fail(str(e))
            got_ptr = expect_ptr = 0
        if got_ptr != expect_ptr:
            fail(
                f"{sym} @ {SETENCOUNT_DATA_VMA:#x}: pointer {got_ptr:#010x}, "
                f"expected {expect_ptr:#010x} from linked.o"
            )
        else:
            print(f"OK   {sym} @ {SETENCOUNT_DATA_VMA:#x} -> {got_ptr:#010x} ({raw.hex()})")

    # --- modify_species @ 7B42 (required on ecology builds) ---
    ms_hook = hooks.get(MODIFY_SPECIES_VMA)
    if ms_hook is None:
        fail(f"modify_species hook missing from hooks for {MODIFY_SPECIES_VMA:#x}")
    else:
        sym, reg = ms_hook
        try:
            got_ptr, raw = read_hook_pointer(o2, MODIFY_SPECIES_VMA, reg, load)
            expect_ptr = nm_thumb_entry(LINKED, sym)
        except SystemExit as e:
            fail(str(e))
            got_ptr = expect_ptr = 0
        if got_ptr != expect_ptr:
            fail(
                f"{sym} @ {MODIFY_SPECIES_VMA:#x}: pointer {got_ptr:#010x}, "
                f"expected {expect_ptr:#010x} from linked.o (re-run make.py / make test.nds)"
            )
        else:
            print(f"OK   {sym} @ {MODIFY_SPECIES_VMA:#x} -> {got_ptr:#010x} ({raw.hex()})")

    if not ok:
        sys.exit(1)
    print("verify_encount_overlay2: OK")


if __name__ == "__main__":
    main()
