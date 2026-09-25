#!/usr/bin/env python3
"""Remove the Cut tree on Route 35 (unrelated to Ilex Forest interior; open-travel cleanup)."""

from __future__ import annotations

import sys
from pathlib import Path

# Reuse gym cut-tree stripper (sprite 86 + script 10000 only).
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from patch_zone_event_gym_cut_trees import patch_member  # noqa: E402

ROUTE_35_MEMBER = "2_036"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a032/2_036>", file=sys.stderr)
        return 1

    target = Path(argv[1])
    if not target.is_file():
        print(f"missing {target}", file=sys.stderr)
        return 1

    print(f"patching {target.name}:")
    data = bytearray(target.read_bytes())
    removed = patch_member(data)
    target.write_bytes(data)
    print(f"patched Route 35 cut tree ({removed} removed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
