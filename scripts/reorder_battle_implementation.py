#!/usr/bin/env python3
"""Reorder Battle sections: Implementation (ex Trainer Generation) -> Battle-8."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# old Battle-N -> new Battle-N
REMAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 8, 6: 5, 7: 6, 8: 7, 9: 9}

NEW_TITLES = {
    1: "Gyms and Badges",
    2: "Healing and Attrition",
    3: "Core Trainer-Battle Philosophy",
    4: "Badge-Based Level Caps",
    5: "Gym Rosters",
    6: "Dynamic Battle Rosters",
    7: "EXP Share",
    8: "Implementation",
    9: "Technical Investigations",
}

NEW_SLUGS = {
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

# document order (by old id)
DOC_ORDER = [1, 2, 3, 4, 6, 7, 8, 5, 9]

FILES = [
    ROOT / "DESIGN-BATTLES.md",
    ROOT / "DESIGN.md",
    ROOT / "DESIGN-WILDS.md",
    ROOT / "DESIGN-WORLD.md",
    ROOT / "documentation/HACK-NOTES.md",
    ROOT / "scripts/fix_design_refs.py",
    ROOT / "scripts/renumber_design_sections.py",
]


def parse_sections(text: str) -> tuple[str, dict[int, str]]:
    """Return preamble and {old_id: body} including header line."""
    parts = re.split(r"(?m)^# Battle-(\d+)\.[^\n]*\n", text)
    preamble = parts[0]
    sections: dict[int, str] = {}
    for i in range(1, len(parts), 2):
        old_id = int(parts[i])
        sections[old_id] = parts[i + 1]
    return preamble, sections


def remap_battle_refs(text: str) -> str:
    # headers and labels via temp placeholders (reverse order to avoid collisions)
    for old in sorted(REMAP, reverse=True):
        new = REMAP[old]
        if old == new:
            continue
        text = re.sub(rf"\bBattle-{old}\b", f"__BATTLE_TMP_{new}__", text)
        text = re.sub(rf"#battle-{old}-", f"#__btmp_{new}__-", text)
    for new in set(REMAP.values()):
        text = text.replace(f"__BATTLE_TMP_{new}__", f"Battle-{new}")
        slug = NEW_SLUGS[new]
        text = re.sub(rf"#__btmp_{new}__-[a-z0-9-]+", f"#{slug}", text)
    # fix any remaining old slugs on remapped ids
    for new, slug in NEW_SLUGS.items():
        text = re.sub(
            rf"(DESIGN-BATTLES\.md#)battle-{new}-[a-z0-9-]+",
            rf"\1{slug}",
            text,
        )
    return text


def rebuild_battles_md(text: str) -> str:
    preamble, sections = parse_sections(text)
    preamble = re.sub(
        r"trainer generation, battle systems",
        "battle systems, implementation phases",
        preamble,
        count=1,
    )
    out = [preamble.rstrip(), ""]
    for old_id in DOC_ORDER:
        new_id = REMAP[old_id]
        body = remap_battle_refs(sections[old_id])
        out.append(f"# Battle-{new_id}. {NEW_TITLES[new_id]}")
        out.append("")
        out.append(body.rstrip())
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    battles = ROOT / "DESIGN-BATTLES.md"
    original = battles.read_text(encoding="utf-8")
    battles.write_text(rebuild_battles_md(original), encoding="utf-8", newline="\n")
    print(f"updated {battles.relative_to(ROOT)}")

    for path in FILES[1:]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        updated = remap_battle_refs(text)
        if path.name == "fix_design_refs.py":
            updated = updated.replace(
                '"Battle-6", "battle-6-gym-leader-rosters"',
                '"Battle-5", "battle-5-gym-rosters"',
            )
            updated = updated.replace(
                '"Battle-5", "battle-5-trainer-generation"',
                '"Battle-8", "battle-8-implementation"',
            )
            updated = updated.replace(
                '"Battle-7", "battle-7-dynamic-battle-rosters"',
                '"Battle-6", "battle-6-dynamic-battle-rosters"',
            )
            updated = updated.replace(
                '"Battle-8", "battle-8-exp-share"',
                '"Battle-7", "battle-7-exp-share"',
            )
            updated = updated.replace(
                "# [§9 Phase 6](#phase-...) -> [Battle-5 Phase 6]",
                "# [§9 Phase 6](#phase-...) -> [Battle-8 Phase 6]",
            )
        if path.name == "renumber_design_sections.py":
            updated = re.sub(
                r"5: \"battle-5-trainer-generation\"",
                '5: "battle-5-gym-rosters"',
                updated,
            )
            updated = re.sub(
                r"6: \"battle-6-gym-leader-rosters\"",
                '6: "battle-6-dynamic-battle-rosters"',
                updated,
            )
            updated = re.sub(
                r"7: \"battle-7-dynamic-battle-rosters\"",
                '7: "battle-7-exp-share"',
                updated,
            )
            updated = re.sub(
                r"8: \"battle-8-exp-share\"",
                '8: "battle-8-implementation"',
                updated,
            )
            # fix battle_slug dict in same file - read and patch manually
            old_slugs_block = '''        5: "battle-5-trainer-generation",
        6: "battle-6-gym-leader-rosters",
        7: "battle-7-dynamic-battle-rosters",
        8: "battle-8-exp-share",'''
            new_slugs_block = '''        5: "battle-5-gym-rosters",
        6: "battle-6-dynamic-battle-rosters",
        7: "battle-7-exp-share",
        8: "battle-8-implementation",'''
            updated = updated.replace(old_slugs_block, new_slugs_block)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"updated {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
