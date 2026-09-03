#!/usr/bin/env python3
"""Create DESIGN-FUTURE.md from git-tracked DESIGN2.md with Future-N section IDs."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEADER = """# Pokémon Wandering Heart — Future & Addon Systems

> **V2–V4 scope:** Apricorn economy, ball rebalance, Full Moon, unlimited moves. Not required for the core ROM.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Core vision:** [`DESIGN-VISION.md`](DESIGN-VISION.md)
>
> **Scope:** Everything from [Future-2](#future-2-apricorn-economy) onward is **V2** unless marked otherwise. **V3** begins at [Future-15](#future-15-full-moon-system-v3). **V4** begins at [Future-16](#future-16-unlimited-learned-moves-v4). None of this is required for the core open-world ROM.
>
> **Dependency (V2 only):** Apricorn tree refresh assumes an accelerated in-game clock ([World-4](DESIGN-WORLD.md#world-4-accelerated-daynight-cycle)). That clock is core; the Apricorn economy is not.

"""


def main() -> None:
    result = subprocess.run(
        ["git", "show", "HEAD:DESIGN2.md"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    text = result.stdout.decode("utf-8")
    # Drop old title block through first ---
    text = re.sub(
        r"^# Pokémon Wandering Heart.*?(?=^---\n\n# 1\.)",
        "",
        text,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    text = re.sub(
        r"^# (\d+)\. (.+)$",
        lambda m: f"# Future-{m.group(1)}. {m.group(2)}",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"from \[§2\]\(#2-apricorn-economy\)",
        "from [Future-2](#future-2-apricorn-economy)",
        text,
    )
    text = re.sub(
        r"at \[§15\]\(#15-full-moon-system-v3\)",
        "at [Future-15](#future-15-full-moon-system-v3)",
        text,
    )
    text = re.sub(
        r"at \[§16\]\(#16-unlimited-learned-moves-v4\)",
        "at [Future-16](#future-16-unlimited-learned-moves-v4)",
        text,
    )
    # Drop duplicate old title block (keep Future-N sections only)
    text = re.sub(
        r"^# Pok[^\n]+\n\n> \*\*Scope:\*\*.*?(?=^---\n\n# Future-1\.)",
        "",
        text,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    text = text.replace(
        "[`DESIGN.md` §24](DESIGN.md#24-accelerated-daynight-cycle)",
        "[World-4](DESIGN-WORLD.md#world-4-accelerated-daynight-cycle)",
    )
    text = text.replace(
        "[`DESIGN.md` §17](DESIGN.md#17-healing-and-attrition)",
        "[Battle-2](DESIGN-BATTLES.md#battle-2-healing-and-attrition)",
    )
    text = text.replace("DESIGN2.md", "DESIGN-FUTURE.md")
    text = text.replace("DESIGN2", "DESIGN-FUTURE")
    out = HEADER + text.lstrip()
    path = ROOT / "DESIGN-FUTURE.md"
    path.write_text(out, encoding="utf-8")
    print(f"Wrote {path.name} ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
