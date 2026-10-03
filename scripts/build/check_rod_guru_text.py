#!/usr/bin/env python3
"""Fail if rod guru dialogue still embeds a Yes/No prompt."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    ROOT / "data/text/404.txt",
    ROOT / "data/text/604.txt",
    ROOT / "data/text/384.txt",
    ROOT / "data/text/452.txt",
    ROOT / "data/text/483.txt",
    ROOT / "data/text/348.txt",
    ROOT / "data/text/512.txt",
    ROOT / "data/text/362.txt",
    ROOT / "data/text/363.txt",
    ROOT / "data/text/381.txt",
)


def main() -> int:
    failed = False
    for path in FILES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            failed = True
            continue
        text = path.read_text(encoding="utf-8")
        marker = "Here, take this Old Rod"
        if marker in text:
            text = text[text.index(marker) :]
        if "{YESNO" in text.upper():
            print(f"FAIL: {path} still contains Yes/No prompt", file=sys.stderr)
            failed = True
        if "{STRVAR_1 50," in text or "{STRVAR_1 51," in text:
            print(f"FAIL: {path} uses wrong STRVAR formatter (50/51)", file=sys.stderr)
            failed = True
    if failed:
        return 1
    print("rod guru text OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
