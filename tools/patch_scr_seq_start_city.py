#!/usr/bin/env python3
"""No-op placeholder — interior exit is not patched via scr_seq (see HACK-NOTES)."""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <build/a012/2_845>", file=sys.stderr)
        return 1
    print(f"start-city scr_seq: no interior patches ({Path(argv[1]).name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
