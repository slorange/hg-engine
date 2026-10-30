#!/usr/bin/env python3
"""Disassemble overlay2 SetEncountData @ 0x02247B64 from rom.nds extract."""
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOAD = 0x02245B80
VMA = 0x02247B64
N = 256


def main() -> int:
    ndstool = ROOT / "tools/ndstool"
    rom = ROOT / "rom.nds"
    if not ndstool.is_file() or not rom.is_file():
        print("need rom.nds and tools/ndstool")
        return 1
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([str(ndstool), "-x", str(rom), "-y", td], check=True, capture_output=True)
        data = (Path(td) / "overlay_0002.bin").read_bytes()
    off = VMA - LOAD
    blob = data[off : off + N]
    out = ROOT / "build" / "_setencount_data.bin"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    subprocess.run(
        [
            "arm-none-eabi-objdump",
            "-D",
            "-b",
            "binary",
            "-m",
            "arm",
            "-M",
            "force-thumb",
            f"--adjust-vma={VMA:#x}",
            str(out),
        ],
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
