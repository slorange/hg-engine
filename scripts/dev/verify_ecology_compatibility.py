#!/usr/bin/env python3
"""Sanity-check ecology TSVs and regenerate compatibility tables."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "scripts/build/gen_ecology_compatibility.py"
DUMP = ROOT / "data/ecology/ecology_compat_by_family.tsv"


def main() -> int:
    proc = subprocess.run(
        [sys.executable, str(GEN)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode

    if not DUMP.is_file():
        print("Missing dump after generation", file=sys.stderr)
        return 1

    lines = DUMP.read_text(encoding="utf-8").splitlines()
    if len(lines) <= 1:
        print("No compatibility edges generated", file=sys.stderr)
        return 1

    import csv

    rows = list(csv.DictReader(lines[0:], delimiter="\t"))
    if not rows or "routes_and_methods" not in rows[0]:
        print("Unexpected by-family dump format (expected routes_and_methods column)", file=sys.stderr)
        return 1

    family_rows = len(rows)
    type_match_rows = sum(1 for r in rows if r.get("type_match") == "1")
    print(f"By-family summary rows: {family_rows} (type_match=1: {type_match_rows})")

    if family_rows < 50:
        print("Warning: unexpectedly few by-family summary rows", file=sys.stderr)
        return 1

    print("verify_ecology_compatibility: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
