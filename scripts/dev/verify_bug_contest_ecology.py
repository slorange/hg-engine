#!/usr/bin/env python3
"""Verify the shared park roster, generated worlds, and packaged contest hooks.

Run inside the build environment after make test.nds and building tools/ecologygen.
"""

from __future__ import annotations

import csv
import struct
import subprocess
import tempfile
import sys
from pathlib import Path

import ndspy.rom
import ndspy.narc

from verify_encount_overlay2 import decode_bl_hook_target, read_hook_pointer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/build"))
from patch_bug_contest_daily import PATCHES as DAILY_PATCHES, patch_member
GROUP = "National Park Bug Catching Contest"
HOOKS = (
    (2, 0x02247ED8, "BugContest_GenerateEcologyEncounter", "78b583b00e1c1d1c"),
    (24, 0x02259DF0, "BugContest_InitEcologyEntries", "70b592b0051c00a8"),
    (24, 0x02259E60, "BugContest_JudgeEcologyMon", "f8b5041ce07d0027"),
)


def symbols(elf: str) -> dict[str, int]:
    lines = subprocess.check_output(["arm-none-eabi-nm", str(ROOT / elf)], text=True)
    return {parts[2]: int(parts[0], 16) for line in lines.splitlines()
            if len(parts := line.split()) == 3}


def main() -> None:
    with (ROOT / "data/ecology/ecology_families.tsv").open(encoding="utf-8-sig") as f:
        expected = {r["Name"] for r in csv.DictReader(f, delimiter="\t")
                    if r["Bug Catching Contest"] == "BCC"}
    assert len(expected) == 17, expected
    with (ROOT / "data/ecology/ecology_locations.tsv").open(encoding="utf-8-sig") as f:
        parks = [r for r in csv.DictReader(f, delimiter="\t") if "National Park" in r["Name"]]
    assert len(parks) == 1 and parks[0]["Name"] == GROUP
    assert set(parks[0]["Location"].split(", ")) == {
        "D22R0101_NATIONAL_PARK", "D22R0102_NATIONAL_PARK_BUG_CATCHING_CONTEST"}

    previous = None
    with tempfile.TemporaryDirectory() as tmp:
        for seed in (1, 2, 3, 42, 12345, 0xC0FFEE, 0xDEADBEEF, 0xFFFFFFFF):
            out = Path(tmp) / "assignment.tsv"
            subprocess.run([str(ROOT / "tools/ecologygen"), "--seed", str(seed),
                            "--out", str(out)], check=True, capture_output=True)
            with out.open() as f:
                rows = list(csv.DictReader(f, delimiter="\t"))
            park = [r for r in rows if r["group_name"] == GROUP and r["method"] == "Land"]
            names = [r["family_name"] for r in park]
            assert len(names) == 17 and set(names) == expected, (seed, names)
            assert not any(r["group_name"] == "National Park" for r in rows)
            for period in ("Morning", "Day", "Night"):
                assert any(not r["land_time"] or period in r["land_time"] for r in park)
            if previous is not None:
                assert park == previous
            previous = park
    print("OK: all 17 unique families across eight seeds; every period populated")

    original = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / "rom.nds"))
    built = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / "test.nds"))
    original_scripts = ndspy.narc.NARC(original.getFileByName("a/0/1/2"))
    built_scripts = ndspy.narc.NARC(built.getFileByName("a/0/1/2"))
    for member, _, _, _ in DAILY_PATCHES:
        expected = patch_member(member, original_scripts.files[member])
        assert built_scripts.files[member] == expected, f"daily contest script {member}"
    print("OK: packed daily registration and both gates; surrounding script bytes preserved")
    original_overlays = original.loadArm9Overlays({2, 24})
    built_overlays = built.loadArm9Overlays({2, 24, 129, 131})
    linked = symbols("build/linked.o")
    for index, address, symbol, signature in HOOKS:
        original_overlay = original_overlays[index]
        offset = address - original_overlay.ramAddress
        assert original_overlay.data[offset:offset + len(bytes.fromhex(signature))] == bytes.fromhex(signature), symbol
        overlay = built_overlays[index]
        offset = address - overlay.ramAddress
        target = decode_bl_hook_target(overlay.data[offset:offset + 24], address)
        assert target == linked[symbol], (symbol, hex(target), hex(linked[symbol]))
        print(f"OK: packed overlay {index} {address:08X} -> {symbol}")

    # Prize replacement is a tail hook, not a complete function replacement.
    # Its pop must match the native judging prologue's saved registers.
    retail = original_overlays[24]
    assert retail.data[0x02259940 - retail.ramAddress:0x02259942 - retail.ramAddress] == bytes.fromhex("f8b5")
    offset = 0x022599FA - retail.ramAddress
    assert retail.data[offset:offset + 12] == bytes.fromhex("e07d0106890e04d0012916d0")
    overlay = built_overlays[24]
    target, _ = read_hook_pointer(overlay.data, 0x022599FA, 3, overlay.ramAddress)
    assert target == linked["BugContest_AssignPrize_hook"] | 1
    engine = built_overlays[129]
    offset = linked["BugContest_AssignPrize_hook"] - engine.ramAddress
    stub = engine.data[offset:offset + 8]
    assert stub[:2] == bytes.fromhex("201c") and stub[6:8] == bytes.fromhex("f8bd")
    print("OK: packed prize hook and native judging stack frame match")

    field_symbols = symbols("build/field_linked.o")
    field = built_overlays[131]
    cap_offset = field_symbols["sWildLevelCaps"] - field.ramAddress
    caps = field.data[cap_offset:cap_offset + 18 * 143]
    for start in range(18):
        assert caps[start * 143 + 23] == caps[start * 143 + 24] >= 5
    engine = built_overlays[129]
    offset = linked["WildLevelCapsFieldAddr"] - engine.ramAddress
    assert struct.unpack_from("<I", engine.data, offset)[0] == field_symbols["sWildLevelCaps"]
    assert len(engine.data) + engine.bssSize <= 0x8000
    print("OK: both park maps share the cap for all 18 starts; engine overlay fits")
    print("verify_bug_contest_ecology: OK")


if __name__ == "__main__":
    main()
