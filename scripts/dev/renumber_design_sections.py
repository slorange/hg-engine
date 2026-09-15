#!/usr/bin/env python3
"""One-off: renumber Wilds/World/Battle sections after Future doc split. Idempotent-safe via placeholders."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS = sorted(
    set(ROOT.glob("DESIGN*.md"))
    | {ROOT / "documentation" / "HACK-NOTES.md", ROOT / "CHANGELOG.md"}
    | {ROOT / "scripts" / "README.md", ROOT / "scripts" / "dev" / "fix_design_refs.py"}
)


def renumber(text: str) -> str:
    for i in range(6, 1, -1):
        text = text.replace(f"Wilds-{i}", f"__WILD{i}__")
    for old, new in ((2, 1), (3, 2), (4, 3), (5, 4), (6, 5)):
        text = text.replace(f"__WILD{old}__", f"Wilds-{new}")
    for i in range(6, 1, -1):
        text = text.replace(f"wilds-{i}-", f"__wild{i}__")
    for old, new in ((2, 1), (3, 2), (4, 3), (5, 4), (6, 5)):
        text = text.replace(f"__wild{old}__", f"wilds-{new}-")

    for i in range(11, 6, -1):
        text = text.replace(f"World-{i}", f"__WORLD{i}__")
    for old, new in ((7, 4), (8, 5), (9, 6), (10, 7), (11, 8)):
        text = text.replace(f"__WORLD{old}__", f"World-{new}")
    for i in range(11, 6, -1):
        text = text.replace(f"world-{i}-", f"__world{i}__")
    for old, new in ((7, 4), (8, 5), (9, 6), (10, 7), (11, 8)):
        text = text.replace(f"__world{old}__", f"world-{new}-")

    text = text.replace("Battle-6", "Battle-6")
    text = text.replace("battle-6-", "battle-6-")
    return text


def main() -> None:
    for path in PATHS:
        if path.name == "DESIGN2.md":
            continue
        original = path.read_text(encoding="utf-8")
        updated = renumber(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
