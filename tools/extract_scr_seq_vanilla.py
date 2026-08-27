#!/usr/bin/env python3
"""Populate build/a012 from clean scr_seq extracted from rom.nds."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
ROM = ROOT / "rom.nds"
VANILLA_DIR = ROOT / "build/a012_vanilla"
VANILLA_NARC = ROOT / "build/vanilla_rom_root/a/0/1/2"


def ensure_vanilla_scr_seq() -> None:
    if not ROM.is_file():
        raise FileNotFoundError(f"missing {ROM}")

    if not VANILLA_NARC.is_file():
        vanilla_root = ROOT / "build/vanilla_rom_root"
        vanilla_root.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [
                str(ROOT / "tools/ndstool"),
                "-x",
                str(ROM),
                "-9",
                str(vanilla_root / "arm9.bin"),
                "-7",
                str(vanilla_root / "arm7.bin"),
                "-y9",
                str(vanilla_root / "overarm9.bin"),
                "-y7",
                str(vanilla_root / "overarm7.bin"),
                "-d",
                str(vanilla_root),
                "-y",
                str(vanilla_root / "overlay"),
                "-t",
                str(vanilla_root / "banner.bin"),
                "-h",
                str(vanilla_root / "header.bin"),
            ],
            cwd=ROOT,
        )

    py = str(PYTHON if PYTHON.is_file() else sys.executable)
    subprocess.check_call(
        [
            py,
            str(ROOT / "tools/narcpy.py"),
            "extract",
            str(VANILLA_NARC),
            "-o",
            str(VANILLA_DIR),
            "-nf",
        ],
        cwd=ROOT,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012>", file=sys.stderr)
        return 1

    out_dir = Path(argv[1])
    ensure_vanilla_scr_seq()

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(VANILLA_DIR, out_dir)

    gym = out_dir / "2_932"
    if gym.stat().st_size < 100:
        raise ValueError(f"{gym} looks corrupt after vanilla extract")

    print(f"seeded {out_dir} from rom.nds scr_seq ({len(list(out_dir.glob('2_*')))} members)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
