#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VMA = 0x0224855C
LOAD = 0x02245B80
o2 = ROOT / "base/overlay/overlay_0002.bin"
off = VMA - LOAD
blob = o2.read_bytes()[off : off + 96]
out = ROOT / "build/_addpoke.bin"
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
