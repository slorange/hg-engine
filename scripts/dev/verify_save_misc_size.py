#!/usr/bin/env python3
"""After make build/save.o: print Sav2_Misc_sizeof from the hooked return constant."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SAVE_O = REPO / "build" / "save.o"


def sav2_misc_sizeof_from_objdump() -> int:
    if not SAVE_O.is_file():
        raise SystemExit(f"Missing {SAVE_O}; run make build/save.o first")
    out = subprocess.check_output(
        ["arm-none-eabi-objdump", "-d", str(SAVE_O)],
        text=True,
        cwd=REPO,
    )
    block = out.split("Sav2_Misc_sizeof>:")[1].split("\n\n")[0]
    m = re.search(r"movs\s+r0,\s+#(\d+)", block)
    if m:
        imm = int(m.group(1))
        shift = re.search(r"lsls\s+r0,\s+r0,\s+#(\d+)", block)
        if shift:
            return imm << int(shift.group(1))
        return imm
    m = re.search(r"\.word\s+(0x[0-9A-Fa-f]+|\d+)", block)
    if m:
        return int(m.group(1), 0)
    raise SystemExit("Could not decode Sav2_Misc_sizeof from objdump")


def main() -> int:
    size = sav2_misc_sizeof_from_objdump()
    print(f"Sav2_Misc_sizeof (from save.o) = {size} (0x{size:X})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
