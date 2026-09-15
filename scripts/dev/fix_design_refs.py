#!/usr/bin/env python3
"""Fix remaining §N cross-refs across design docs."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# old § number -> (file, Label-N, anchor slug without #)
REF = {
    1: ("DESIGN.md", "Index-1", "index-1-instructions-for-coding-agents"),
    2: ("DESIGN-VISION.md", "Vision-1", "vision-1-core-vision"),
    3: ("DESIGN-VISION.md", "Vision-2", "vision-2-open-world-philosophy"),
    4: ("DESIGN-VISION.md", "Vision-3", "vision-3-starting-location-and-pokémon"),
    5: ("DESIGN-BATTLES.md", "Battle-1", "battle-1-gyms-and-badges"),
    6: ("DESIGN-BATTLES.md", "Battle-5", "battle-5-gym-rosters"),
    7: ("DESIGN-BATTLES.md", "Battle-4", "battle-4-badge-based-level-caps"),
    8: ("DESIGN-FUTURE.md", "Future-10", "future-10-living-trainers--interactions"),
    9: ("DESIGN-BATTLES.md", "Battle-4", "trainer-scaling-implemented"),
    10: ("DESIGN-FUTURE.md", "Future-10", "future-10-living-trainers--interactions"),
    11: ("DESIGN-BATTLES.md", "Battle-3", "battle-3-core-trainer-battle-philosophy"),
    12: ("DESIGN-FUTURE.md", "Future-8", "future-8-dynamic-battle-rosters--universal-pc"),
    13: ("DESIGN-FUTURE.md", "Future-8", "future-8-dynamic-battle-rosters--universal-pc"),  # was counter-picking — merged
    14: ("DESIGN-FUTURE.md", "Future-8", "future-8-dynamic-battle-rosters--universal-pc"),  # was PC access — merged
    15: ("DESIGN-FUTURE.md", "Future-8", "future-8-dynamic-battle-rosters--universal-pc"),  # was field party — merged
    16: ("DESIGN-BATTLES.md", "Battle-6", "battle-6-exp-share"),
    17: ("DESIGN-BATTLES.md", "Battle-2", "battle-2-healing-and-attrition"),
    18: ("DESIGN-WORLD.md", "World-4", "world-4-pokmon-centers"),
    19: ("DESIGN-WORLD.md", "World-1", "world-1-world-transportation"),
    20: ("DESIGN-WORLD.md", "World-2", "world-2-routes-and-content-gating"),
    21: ("DESIGN-WORLD.md", "World-3", "world-3-hms-and-field-moves"),
    22: ("DESIGN-WILDS.md", "Wilds-3", "wilds-3-fishing-rod-progression"),
    23: ("DESIGN-WORLD.md", "World-5", "world-5-tms"),
    24: ("DESIGN-FUTURE.md", "Future-9", "future-9-accelerated-daynight-cycle"),
    25: ("DESIGN-WORLD.md", "World-6", "world-6-evolution-methods-trade--stones"),
    27: ("DESIGN-FUTURE.md", "Future-5", "future-5-per-save-wild-ecology-shuffle"),
    28: ("DESIGN-WILDS.md", "Wilds-1", "wilds-1-increased-wild-pokmon-level-range"),
    29: ("DESIGN-WILDS.md", "Wilds-2", "wilds-2-starting-city-distance-based-wild-level-caps"),
    30: ("DESIGN-WILDS.md", "Wilds-4", "wilds-4-pokmon-generations--content-scope"),
    31: ("DESIGN-VISION.md", "Vision-1", "vision-1-core-vision"),  # was §31 Design Principles — removed
    33: ("DESIGN-VISION.md", "Vision-1", "vision-1-core-vision"),  # was §33 Initial Development Philosophy — removed
    34: ("DESIGN.md", "Index-2", "index-2-current-technical-baseline"),
    35: ("DESIGN.md", "Index-3", "index-3-open-design-questions"),
    36: ("DESIGN-FUTURE.md", "Future-1", "future-1-apricorn-economy--poké-ball-rebalance"),
    37: ("DESIGN-STORY.md", "Story-1", "story-1-story-and-script-content"),
    38: ("DESIGN.md", "Index-4", "index-4-game-identity"),
    39: ("DESIGN-STORY.md", "Story-2", "story-2-vanilla-cleanup-backlog"),
}


def md_link(n: int) -> str:
    fname, label, anchor = REF[n]
    return f"[{label}]({fname}#{anchor})"


def fix(text: str) -> str:
    text = text.replace("DESIGN2.md", "DESIGN-FUTURE.md")
    text = re.sub(r"DESIGN2\b", "DESIGN-FUTURE", text)

    # [§9 Phase 6](#phase-...) -> [Battle-4 trainer scaling](#trainer-scaling-implemented)
    def phase_link(m: re.Match[str]) -> str:
        n = int(m.group(1))
        phase = m.group(2)
        label = REF[n][1]
        return f"[{label} {phase}](#{phase.lower().replace(' ', '-')})"

    text = re.sub(
        r"\[§(\d+)\s+(Phase\s+\d+)\]\(#([^)]+)\)",
        phase_link,
        text,
    )

    # [`§9`](#9-trainer-generation) broken leftovers
    text = re.sub(
        r"\[`§(\d+)`\]\(#\d+[^)]*\)",
        lambda m: md_link(int(m.group(1))),
        text,
    )

    # [§27](#27-...)
    text = re.sub(
        r"\[§(\d+)\]\(#\d+[^)]*\)",
        lambda m: md_link(int(m.group(1))),
        text,
    )

    # [§§27–29](#...)
    text = re.sub(
        r"\[§§(\d+)–(\d+)\]\([^)]*\)",
        lambda m: f"[{REF[int(m.group(1))][1]}–{REF[int(m.group(2))][1]}]",
        text,
    )

    # bare §N in prose (careful: not in words)
    for n in sorted(REF, reverse=True):
        label = REF[n][1]
        text = re.sub(rf"§{n}\b", label, text)

    return text


def main() -> None:
    for path in sorted(ROOT.glob("DESIGN*.md")):
        if path.name in ("DESIGN2.md", "DESIGN-FUTURE.md"):
            continue
        original = path.read_text(encoding="utf-8")
        updated = fix(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"Updated {path.name}")


if __name__ == "__main__":
    main()
