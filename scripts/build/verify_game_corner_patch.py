#!/usr/bin/env python3
"""Verify Game Corner TM and held-item prize scr_seq patches."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from patch_scr_seq_game_corner import (  # noqa: E402
    CELADON_COST_PATCHES,
    CELADON_PATCHES,
    GOLDENROD_COST_PATCHES,
    GOLDENROD_PATCHES,
    validate_cost_patches,
    validate_patches,
)


def check(path: Path, patches, cost_patches, label: str) -> bool:
    data = path.read_bytes()
    print(f"{path.name}: {len(data)} bytes ({label})")
    try:
        validate_patches(data, patches, label)
        validate_cost_patches(data, cost_patches, label)
    except ValueError as exc:
        print(f"  FAIL: {exc}")
        return False
    print("  OK")
    return True


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(f"usage: {argv[0]} <2_910> <2_804>", file=sys.stderr)
        return 1

    ok = True
    ok &= check(
        Path(argv[1]), GOLDENROD_PATCHES, GOLDENROD_COST_PATCHES, "Goldenrod"
    )
    ok &= check(Path(argv[2]), CELADON_PATCHES, CELADON_COST_PATCHES, "Celadon")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
