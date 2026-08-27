#!/usr/bin/env python3
"""List sizes of ship-related scr_seq / zone_event NARC members."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = [153, 154, 155, 77, 54, 330, 386, 387, 113, 315, 490]
BASES = [
    ROOT / "build/a012_vanilla",
    ROOT / "build/a032_vanilla",
    ROOT / "build/a012",
    ROOT / "build/a032",
]


def member_path(base: Path, m: int) -> Path | None:
    for name in (f"2_{m:03d}", f"2_{m}"):
        p = base / name
        if p.is_file():
            return p
    return None


def main() -> None:
    hdr_script = ROOT / "scripts/list_init_hdrs.py"
    hdr_out = ""
    if hdr_script.is_file():
        try:
            hdr_out = subprocess.check_output(
                [sys.executable, str(hdr_script)], text=True, stderr=subprocess.DEVNULL, cwd=ROOT
            )
        except subprocess.CalledProcessError:
            pass

    for m in MEMBERS:
        print(f"=== 2_{m:03d} ===")
        for line in hdr_out.splitlines():
            if f"2_{m:03d}" in line or f"2_{m} " in line or line.endswith(f"2_{m}"):
                print(f"  hdr: {line.strip()}")
        for base in BASES:
            p = member_path(base, m)
            if p:
                print(f"  {p.relative_to(ROOT)}: {p.stat().st_size} bytes")
            else:
                print(f"  {base.relative_to(ROOT)}/2_{m}: (missing)")


if __name__ == "__main__":
    main()
