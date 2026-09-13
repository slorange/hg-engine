#!/usr/bin/env python3
"""List scr_seq slots that reference a Gym Leader trainer id (vanilla baseline)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from patch_scr_seq_gym_falkner import extract_scripts

TRAINER_BATTLE = 213
LEADERS = [
    (859, "Falkner", 20, 1),
    (886, "Whitney", 30, 0),
    (913, "Jasmine", 33, 0),
    (922, "Morty", 31, 1),
    (932, "Pryce", 32, 1),
]

for member, name, trainer_id, expected_slot in LEADERS:
    data = Path(f"build/a012_vanilla/2_{member:03d}").read_bytes()
    scripts = extract_scripts(data)
    print(f"{name} ({member}): {len(scripts)} slots")
    for i, s in enumerate(scripts):
        idx = 0
        trainer = None
        while idx < len(s) - 4:
            if int.from_bytes(s[idx : idx + 2], "little") == TRAINER_BATTLE:
                trainer = int.from_bytes(s[idx + 2 : idx + 4], "little")
                break
            idx += 2
        if struct.pack("<H", trainer_id) in s:
            print(f"  slot {i}: {len(s)} bytes ** LEADER (trainer {trainer_id}) **")
        elif trainer is not None or len(s) > 80:
            extra = f" trainer={trainer}" if trainer is not None else ""
            print(f"  slot {i}: {len(s)} bytes{extra}")
    print(f"  (expected patch slot: {expected_slot})")
