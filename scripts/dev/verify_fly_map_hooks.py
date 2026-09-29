#!/usr/bin/env python3
"""Verify Fly map open-world hooks (post-make stub check + vanilla prologue)."""

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
ARM9 = ROOT / "base/arm9.bin"
ROM = ROOT / "rom.nds"
Y9 = ROOT / "base/overarm9.bin"
OV101 = ROOT / "base/overlay/overlay_0101.bin"

HOOK_STUB = bytes.fromhex("00490847")
HOOK_STUB_ALIGNED = bytes.fromhex("00480047")
GET_MAP_UNLOCK_ADDR = 0x0202EE70
GET_MAP_UNLOCK_SIG = bytes.fromhex("406800c00f8006000e004770")
STALE_ARM9_HOOK = 0x0202EE84


def openworld_fly_map_enabled() -> bool:
    text = CONFIG.read_text(encoding="utf-8")
    return bool(re.search(r"^#define\s+OPENWORLD_FLY_MAP\b", text, re.MULTILINE))


def arm9_get_map_unlock_hook_wanted() -> bool:
    if not HOOKS.is_file():
        return False
    return "Pokegear_GetMapUnlockLevel_hook" in HOOKS.read_text(encoding="utf-8")


def overlay101_hook_wanted() -> bool:
    if not HOOKS.is_file():
        return False
    return "0101 ov101_021EA7E4_hook" in HOOKS.read_text(encoding="utf-8")


def has_hook_stub(arm9: bytes, addr: int) -> bool:
    off = addr - 0x02000000
    if arm9[off : off + 4] == HOOK_STUB_ALIGNED:
        return True
    if arm9[off : off + 4] == HOOK_STUB:
        return True
    if off > 0 and arm9[off - 1 : off + 3] == HOOK_STUB:
        return True
    return False


def main() -> None:
    if not openworld_fly_map_enabled():
        print("OPENWORLD_FLY_MAP off — skip verify")
        return

    if not ARM9.is_file():
        raise SystemExit(f"missing {ARM9} — run make first")

    arm9 = ARM9.read_bytes()
    get_off = GET_MAP_UNLOCK_ADDR - 0x02000000

    if arm9_get_map_unlock_hook_wanted():
        if not has_hook_stub(arm9, GET_MAP_UNLOCK_ADDR):
            get_off = GET_MAP_UNLOCK_ADDR - 0x02000000
            raise SystemExit(
                f"Pokegear_GetMapUnlockLevel hook stub missing at {GET_MAP_UNLOCK_ADDR:#x} "
                f"(got {arm9[get_off:get_off+4].hex()})"
            )
    else:
        if arm9[get_off : get_off + len(GET_MAP_UNLOCK_SIG)] != GET_MAP_UNLOCK_SIG:
            raise SystemExit(
                f"unexpected bytes at {GET_MAP_UNLOCK_ADDR:#x} "
                f"(got {arm9[get_off:get_off+len(GET_MAP_UNLOCK_SIG)].hex()})"
            )

    stale_off = STALE_ARM9_HOOK - 0x02000000
    if has_hook_stub(arm9, STALE_ARM9_HOOK):
        raise SystemExit(
            "stale arm9 hook at 0x0202EE84 — wrong site; use 0x0202EE70 only"
        )

    if overlay101_hook_wanted():
        if not Y9.is_file() or not OV101.is_file():
            raise SystemExit("overlay 101 hook enabled but base overlay missing")
        base = struct.unpack_from("<I", Y9.read_bytes(), 101 * 0x20 + 4)[0]
        region_off = 0x021EA7E4 - base
        ov = OV101.read_bytes()
        if ov[region_off : region_off + len(HOOK_STUB)] != HOOK_STUB:
            raise SystemExit(f"overlay 101 hook stub missing at 0x021EA7E4")

    if arm9_get_map_unlock_hook_wanted():
        print("Fly map hook verified (arm9 Pokegear_GetMapUnlockLevel @ 0202EE70).")
    else:
        print("Fly map: OPENWORLD_FLY_MAP on but arm9 hook disabled.")


if __name__ == "__main__":
    main()
