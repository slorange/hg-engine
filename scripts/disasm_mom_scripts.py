#!/usr/bin/env python3
"""Disassemble scr_seq scripts for Mom item-give investigation."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from append_scr_seq_script import extract_scripts  # noqa: E402

WATCH = {107, 109, 156, 283}


def disasm(body: bytes, limit: int = 80) -> list[str]:
    i = 0
    lines: list[str] = []
    while i + 2 <= len(body) and len(lines) < limit:
        cmd = struct.unpack_from("<H", body, i)[0]
        extra = ""
        if cmd == 30 and i + 4 <= len(body):
            flag = struct.unpack_from("<H", body, i + 2)[0]
            extra = f" flag={flag}"
            i += 4
        elif cmd == 291:
            extra = " GivePokedex"
            i += 2
        elif cmd == 293:
            extra = " give_running_shoes"
            i += 2
        elif cmd in (32, 33) and i + 4 <= len(body):
            extra = f" arg={struct.unpack_from('<H', body, i + 2)[0]}"
            i += 4
        elif cmd == 0xFD13:
            break
        else:
            i += 2
        lines.append(f"  @{i - 2}: cmd={cmd}{extra}")
    return lines


def main() -> None:
    members = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [845, 962, 957, 834, 961]
    for mid in members:
        path = ROOT / f"build/a012/2_{mid}"
        if not path.is_file():
            print(f"missing {path}")
            continue
        data = path.read_bytes()
        scripts = extract_scripts(data)
        print(f"=== 2_{mid} ({len(data)} bytes, {len(scripts)} scripts) ===")
        for idx, body in enumerate(scripts):
            lines = disasm(body, 200)
            interesting = any(
                "GivePokedex" in l
                or "give_running_shoes" in l
                or any(f"flag={f}" in l for f in WATCH)
                for l in lines
            )
            if interesting or idx == 0:
                print(f" script {idx} ({len(body)} bytes):")
                for line in disasm(body, 80):
                    print(line)
                if len(body) > 160:
                    print("  ...")


if __name__ == "__main__":
    main()
