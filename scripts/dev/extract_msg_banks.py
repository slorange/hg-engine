#!/usr/bin/env python3
"""Extract selected msg banks from vanilla msg_data.narc to data/text/."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MSG_NARC = ROOT / "base/root/a/0/2/7"
MSGENC = ROOT / "tools/msgenc"
CHARMAP = ROOT / "charmap.txt"
OUT_DIR = ROOT / "data/text"
EXTRACT_DIR = ROOT / "build/msg_extract"


def main() -> None:
    banks = [int(x) for x in sys.argv[1:]]
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    subprocess.check_call(
        [py, str(ROOT / "tools/narcpy.py"), "extract", str(MSG_NARC), str(EXTRACT_DIR), "-nf"],
        cwd=ROOT,
    )
    for bank in banks:
        src = EXTRACT_DIR / f"7_{bank}"
        if not src.is_file():
            raise FileNotFoundError(src)
        out = OUT_DIR / f"{bank}.txt"
        tmp = EXTRACT_DIR / f"{bank}.txt"
        subprocess.check_call(
            [str(MSGENC), "-d", "-c", str(CHARMAP), str(src), str(tmp)],
            cwd=ROOT,
        )
        text = tmp.read_text(encoding="utf-8")
        out.write_text(text, encoding="utf-8")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        print(f"wrote {out} ({len(lines)} messages)")


if __name__ == "__main__":
    main()
