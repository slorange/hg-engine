#!/usr/bin/env python3
"""Search decoded msg banks for a substring (requires base/root/a/0/2/7)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MSG_ROOT = ROOT / "base/root/a/0/2/7"
MSGENC = ROOT / "tools/msgenc"


def decode(path: Path) -> str | None:
    r = subprocess.run(
        [str(MSGENC), "-d", "-c", str(ROOT / "charmap.txt"), str(path)],
        capture_output=True,
        text=True,
    )
    return r.stdout if r.returncode == 0 else None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("needle", help="substring to search (case insensitive)")
    ap.add_argument("--bank", type=int, help="only search one bank number")
    args = ap.parse_args(argv[1:])

    if not MSG_ROOT.is_dir():
        print(f"missing {MSG_ROOT} — build/extract rom first", file=sys.stderr)
        return 1

    needle = args.needle.lower()
    paths = sorted(MSG_ROOT.glob("7_*"))
    if args.bank is not None:
        paths = [MSG_ROOT / f"7_{args.bank:03d}"]

    for path in paths:
        text = decode(path)
        if not text or needle not in text.lower():
            continue
        bank = path.name.split("_", 1)[1]
        print(f"bank {bank}:")
        for i, line in enumerate(text.splitlines()):
            if needle in line.lower():
                print(f"  [{i}] {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
