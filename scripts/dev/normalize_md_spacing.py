#!/usr/bin/env python3
"""Collapse accidental double-spacing (blank line after every line) in markdown."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def is_block_line(s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    if s.startswith(("- ", "* ", "|", ">", "#")):
        return True
    if re.match(r"^\d+\.", s):
        return True
    return s in ("---", "***", "___")


def normalize(lines: list[str]) -> list[str]:
    stripped = [l.rstrip() for l in lines if l.strip()]
    out: list[str] = []
    for line in stripped:
        if not out:
            out.append(line)
            continue
        prev = out[-1]
        if is_block_line(prev) and is_block_line(line):
            if prev.lstrip().startswith(("- ", "* ")) and line.lstrip().startswith(("- ", "* ")):
                out.append(line)
                continue
            if prev.lstrip().startswith("|") and line.lstrip().startswith("|"):
                out.append(line)
                continue
            if prev.lstrip().startswith(">") and line.lstrip().startswith(">"):
                out.append(line)
                continue
        if line.startswith("#") or line.strip() == "---":
            if out[-1] != "":
                out.append("")
        elif not is_block_line(prev) or not is_block_line(line):
            if out[-1] != "":
                out.append("")
        out.append(line)
    return out


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("DESIGN-BATTLES.md")
    lines = path.read_text(encoding="utf-8").splitlines()
    out = normalize(lines)
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"{path}: {len(lines)} -> {len(out)} lines")


if __name__ == "__main__":
    main()
