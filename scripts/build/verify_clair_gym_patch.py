#!/usr/bin/env python3
"""Verify Blackthorn Gym Clair: zone_event 137 + scr_seq 943 slot 0 (script 1)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from patch_scr_seq_gym_falkner import extract_scripts  # noqa: E402

MEMBER = 943
ZONE_MEMBER = 137
LEADER_SLOT = 0
CLAIR_SPRITE = 359
CLAIR_OBJ = 0
CLAIR_SCRIPT = 1
TRAINER_BATTLE = 0xD5
TRAINER_CLAIR = 35
CHECK_BATTLE_WON = 220
GIVE_JOHTO_BADGE = bytes([0xD0, 0x00, 0x03, 0x07, 0x00])
COUNT_BADGES = 296
MSG_BANK_GYM_REWARDS = 854
NON_NPC_MSG_EXTERN = 439


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_{MEMBER:03d}>", file=sys.stderr)
        return 1

    path = Path(argv[1])
    if path.name != f"2_{MEMBER:03d}":
        print(f"warning: expected 2_{MEMBER:03d}, got {path.name}", file=sys.stderr)

    data = path.read_bytes()
    scripts = extract_scripts(data)
    if LEADER_SLOT >= len(scripts):
        print(f"  FAIL: slot {LEADER_SLOT} missing")
        return 1

    s = scripts[LEADER_SLOT]
    print(f"{path.name}: {len(data)} bytes, slot{LEADER_SLOT}={len(s)} bytes")

    if GIVE_JOHTO_BADGE not in s:
        print(f"  FAIL: GiveJohtoBadgeOpenWorld not in slot {LEADER_SLOT}")
        return 1

    extern_cap = struct.pack("<HHH", NON_NPC_MSG_EXTERN, MSG_BANK_GYM_REWARDS, 0)
    if struct.pack("<H", COUNT_BADGES) not in s or extern_cap not in s:
        print(f"  FAIL: badge-count HM / level-cap block missing in slot {LEADER_SLOT}")
        return 1

    found_battle = False
    i = 0
    while i + 7 < len(s):
        if s[i] == TRAINER_BATTLE and s[i + 1] == 0:
            tid = struct.unpack_from("<H", s, i + 2)[0]
            if tid == TRAINER_CLAIR:
                found_battle = True
                a1 = struct.unpack_from("<H", s, i + 4)[0]
                a2, a3 = s[i + 6], s[i + 7]
                if a1 != 0 or a2 != 0 or a3 != 0:
                    print(f"  FAIL: Clair battle @{i} not Morty-style args")
                    return 1
                tail = s[i + 8 : i + 8 + 4]
                if len(tail) < 4 or struct.unpack_from("<H", tail, 0)[0] != CHECK_BATTLE_WON:
                    print(f"  FAIL: Clair battle @{i} missing check_battle_won tail")
                    return 1
                print(f"  OK: slot {LEADER_SLOT} Morty-style Clair battle @{i}")
            i += 8
        else:
            i += 1

    if not found_battle:
        print(f"  FAIL: no trainer_battle for Clair ({TRAINER_CLAIR}) in slot {LEADER_SLOT}")
        return 1

    print(f"  OK: Rising Badge + HM reward block in slot {LEADER_SLOT}")

    zone = ROOT / f"build/a032/2_{ZONE_MEMBER:03d}"
    if zone.is_file():
        zdata = zone.read_bytes()
        pos = 0
        bg = struct.unpack_from("<I", zdata, 0)[0]
        pos += 4 + bg * 20
        oc = struct.unpack_from("<I", zdata, pos)[0]
        pos += 4 + CLAIR_OBJ * 32
        if oc <= CLAIR_OBJ:
            print(f"  FAIL: zone {ZONE_MEMBER} missing Clair obj")
            return 1
        fields = struct.unpack_from("<14H", zdata, pos)
        if fields[1] != CLAIR_SPRITE:
            print(f"  FAIL: obj{CLAIR_OBJ} sprite {fields[1]}, expected {CLAIR_SPRITE}")
            return 1
        if fields[5] != CLAIR_SCRIPT:
            print(f"  FAIL: Clair script {fields[5]}, expected {CLAIR_SCRIPT}")
            return 1
        print(f"  OK: zone {ZONE_MEMBER:03d} Clair obj{CLAIR_OBJ} script {CLAIR_SCRIPT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
