#!/usr/bin/env python3
"""Post-build check of Center coverage, return anchors, and installed hooks."""
import re
import struct
import subprocess
import sys
from pathlib import Path

import ndspy.rom
import ndspy.codeCompression

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from patch_zone_event_start_city import parse_zone_event

# Map-header eventsBank values: interior and exterior for each supported Center.
EVENTS = {
    69: (66, 64), 81: (78, 75), 158: (153, 70), 166: (160, 71),
    169: (163, 33), 185: (178, 73), 226: (212, 74), 236: (222, 72),
    246: (232, 84), 293: (264, 86), 358: (315, 51), 393: (350, 52),
    407: (363, 56), 428: (383, 49), 434: (389, 50), 466: (420, 15),
    475: (428, 48), 482: (435, 53), 501: (453, 47), 508: (460, 54),
    511: (463, 8), 514: (466, 87), 528: (480, 367), 534: (486, 168),
}


def main():
    source = (ROOT / "src/center_hub.c").read_text()
    doors = [tuple(map(int, m)) for m in re.findall(r"\{(\d+), (\d+), (\d+)\}", source)]
    assert len(doors) == 24 and {d[0] for d in doors} == set(EVENTS)
    assert 300 not in {d[0] for d in doors}, "Indigo must remain excluded"
    supported = {int(i) for n, i in re.findall(r"#define\s+(MAP_\w*PC0101)\s+(\d+)", (ROOT / "include/constants/maps.h").read_text()) if int(i) != 255}
    assert supported == set(EVENTS), "missing a reachable Center"
    for interior, exterior, anchor in doors:
        inner_member, outer_member = EVENTS[interior]
        inner = parse_zone_event((ROOT / f"build/a032_vanilla/2_{inner_member:03}").read_bytes())[2]
        outer = parse_zone_event((ROOT / f"build/a032_vanilla/2_{outer_member:03}").read_bytes())[2]
        assert inner[0][2:4] == (exterior, anchor), (interior, "wrong return destination")
        assert outer[anchor][2:4] == (interior, 0), (interior, "door is not reciprocal")
    # Map events and scripts for Indigo's outdoor map and lobby stay vanilla.
    for member in (55, 271):
        assert (ROOT / f"build/a032/2_{member:03}").read_bytes() == (ROOT / f"build/a032_vanilla/2_{member:03}").read_bytes()

    rom = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / "test.nds"))
    # The build packs the already decompressed ARM9 verbatim.
    packed_arm9 = rom.arm9
    arm9 = (ROOT / "base/arm9.bin").read_bytes()
    symbols = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", str(ROOT / "build/linked.o")], text=True).splitlines():
        fields = line.split()
        if len(fields) == 3:
            symbols[fields[2]] = int(fields[0], 16)
    for address, name in ((0x02052F94, "CenterHub_LoadMap"), (0x0203BB20, "CenterHub_GetBlackoutSpawn")):
        offset = address - 0x02000000
        assert arm9[offset:offset + 4] == bytes.fromhex("004b1847"), (name, "missing r3 jump")
        assert struct.unpack_from("<I", arm9, offset + 4)[0] == symbols[name] | 1
        assert packed_arm9[offset:offset + 8] == arm9[offset:offset + 8], (name, "ROM hook is stale")
    vanilla = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / "rom.nds"))
    vanilla_arm9 = ndspy.codeCompression.decompress(vanilla.arm9)
    assert struct.unpack_from("<I", vanilla_arm9, 0x3BB4C)[0] == 0x020F9E80
    assert arm9[0xF9E80:0xF9E80 + 30 * 18] == vanilla_arm9[0xF9E80:0xF9E80 + 30 * 18]
    print("OK: all 24 Center doors reciprocal; Indigo events untouched; installed ARM9 hooks match ROM and linked symbols; vanilla spawn table intact")


if __name__ == "__main__":
    main()
