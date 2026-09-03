#!/usr/bin/env python3
"""Renumber Battle-* and World-* design section IDs to match document order."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# old_id -> new_id (document order)
BATTLE = {
    1: 1,
    13: 2,
    7: 3,
    3: 4,
    5: 5,
    2: 6,
    8: 7,
    12: 8,
    17: 9,
}

WORLD = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    6: 5,
    7: 6,
    8: 7,
    9: 8,
    10: 9,
    5: 10,
}

FILES = [
    ROOT / "DESIGN-BATTLES.md",
    ROOT / "DESIGN-WORLD.md",
    ROOT / "DESIGN.md",
    ROOT / "DESIGN-WILDS.md",
    ROOT / "DESIGN-FUTURE.md",
    ROOT / "DESIGN-STORY.md",
    ROOT / "documentation/HACK-NOTES.md",
    ROOT / "scripts/fix_design_refs.py",
    ROOT / "scripts/create_design_future.py",
    ROOT / "src/field/enemy_party.c",
]


def battle_slug(n: int) -> str:
    slugs = {
        1: "battle-1-gyms-and-badges",
        2: "battle-2-healing-and-attrition",
        3: "battle-3-core-trainer-battle-philosophy",
        4: "battle-4-badge-based-level-caps",
        5: "battle-5-gym-rosters",
        6: "battle-6-dynamic-battle-rosters",
        7: "battle-7-exp-share",
        8: "battle-8-implementation",
        9: "battle-9-technical-investigations",
    }
    return slugs[n]


def world_slug(n: int) -> str:
    slugs = {
        1: "world-1-world-transportation",
        2: "world-2-routes-and-content-gating",
        3: "world-3-hms-and-field-moves",
        4: "world-4-accelerated-daynight-cycle",
        5: "world-5-living-trainers",
        6: "world-6-trainer-interactions",
        7: "world-7-pokmon-centers",
        8: "world-8-tms",
        9: "world-9-evolution-methods-trade--stones",
        10: "world-10-shops",
        11: "world-11-technical-investigations",
    }
    return slugs[n]


def renumber_mapping(mapping: dict[int, int], prefix: str, slug_fn) -> str:
    """Two-pass via __TMP__ placeholders to avoid collision."""
    def apply(text: str) -> str:
        for old, new in sorted(mapping.items(), key=lambda x: x[0], reverse=True):
            if old == new:
                continue
            text = re.sub(
                rf"\b{prefix}-{old}\b",
                f"__{prefix}_TMP_{new}__",
                text,
            )
            text = re.sub(
                rf"#{prefix.lower()}-{old}-",
                f"#__{prefix.lower()}_tmp_{new}__-",
                text,
            )
        for old, new in mapping.items():
            if old == new:
                continue
            text = text.replace(f"__{prefix}_TMP_{new}__", f"{prefix}-{new}")
            text = text.replace(f"#__{prefix.lower()}_tmp_{new}__-", f"#{slug_fn(new).split('-', 1)[0]}-{new}-")
        # fix full anchor slugs for changed ids
        for new in set(mapping.values()):
            slug = slug_fn(new)
            text = re.sub(
                rf"#{prefix.lower()}-{new}-[a-z0-9-]*",
                f"#{slug}",
                text,
            )
            # also fix DESIGN-BATTLES.md#battle-N-... links that got partial replace
            text = re.sub(
                rf"DESIGN-BATTLES\.md#{prefix.lower()}-{new}(?!-)",
                f"DESIGN-BATTLES.md#{slug}",
                text,
            )
            text = re.sub(
                rf"DESIGN-WORLD\.md#{prefix.lower()}-{new}(?!-)",
                f"DESIGN-WORLD.md#{slug}",
                text,
            )
        return text

    return apply


def fix_battle_anchors(text: str) -> str:
    for new, slug in {
        1: battle_slug(1),
        2: battle_slug(2),
        3: battle_slug(3),
        4: battle_slug(4),
        5: battle_slug(5),
        6: battle_slug(6),
        7: battle_slug(7),
        8: battle_slug(8),
        9: battle_slug(9),
    }.items():
        text = re.sub(
            rf"(DESIGN-BATTLES\.md#)battle-{new}-[a-z0-9-]+",
            rf"\1{slug}",
            text,
        )
        text = re.sub(
            rf"\(#\)battle-{new}-[a-z0-9-]+",
            rf"(#{slug})",
            text,
        )
    return text


def fix_world_anchors(text: str) -> str:
    for new, slug in {
        1: world_slug(1),
        2: world_slug(2),
        3: world_slug(3),
        4: world_slug(4),
        5: world_slug(5),
        6: world_slug(6),
        7: world_slug(7),
        8: world_slug(8),
        9: world_slug(9),
        10: world_slug(10),
    }.items():
        text = re.sub(
            rf"(DESIGN-WORLD\.md#)world-{new}-[a-z0-9-]+",
            rf"\1{slug}",
            text,
        )
    return text


def renumber(text: str) -> str:
    # Battle headers and inline refs (high -> low via tmp)
    for old in sorted(BATTLE, reverse=True):
        new = BATTLE[old]
        if old == new:
            continue
        text = re.sub(rf"# Battle-{old}\.", f"# __BHDR_{new}__.", text)
        text = re.sub(rf"\bBattle-{old}\b", f"__BREF_{new}__", text)
        text = re.sub(rf"#battle-{old}-", f"#__banchor_{new}__-", text)
    for new in set(BATTLE.values()):
        text = text.replace(f"# __BHDR_{new}__.", f"# Battle-{new}.")
        text = re.sub(rf"\b__BREF_{new}__\b", f"Battle-{new}", text)
        slug = battle_slug(new)
        text = re.sub(rf"#__banchor_{new}__-[a-z0-9-]+", f"#{slug}", text)

    # World headers and inline refs
    for old in sorted(WORLD, reverse=True):
        new = WORLD[old]
        if old == new:
            continue
        text = re.sub(rf"# World-{old}\.", f"# __WHDR_{new}__.", text)
        text = re.sub(rf"\bWorld-{old}\b", f"__WREF_{new}__", text)
        text = re.sub(rf"#world-{old}-", f"#__wanchor_{new}__-", text)
    for new in set(WORLD.values()):
        text = text.replace(f"# __WHDR_{new}__.", f"# World-{new}.")
        text = re.sub(rf"\b__WREF_{new}__\b", f"World-{new}", text)
        slug = world_slug(new)
        text = re.sub(rf"#__wanchor_{new}__-[a-z0-9-]+", f"#{slug}", text)

    text = fix_battle_anchors(text)
    text = fix_world_anchors(text)

    # prose references like "Battle-3" in trainer level band heading
    text = re.sub(
        r"same badge ladder as Battle-(\d+)",
        lambda m: f"same badge ladder as Battle-{BATTLE.get(int(m.group(1)), m.group(1))}"
        if int(m.group(1)) in BATTLE
        else m.group(0),
        text,
    )

    return text


def main() -> None:
    for path in FILES:
        if not path.exists():
            print(f"skip missing {path}")
            continue
        original = path.read_text(encoding="utf-8")
        updated = renumber(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"updated {path.relative_to(ROOT)}")
        else:
            print(f"unchanged {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
