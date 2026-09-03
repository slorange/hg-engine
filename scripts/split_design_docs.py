#!/usr/bin/env python3
"""One-shot splitter: DESIGN.md -> index + 5 sub-docs with prefixed section IDs."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "DESIGN.md"

# old_section_num -> (filename, prefix, new_num, investigations_key or None)
# investigations_key: which ## blocks from old §32 to append at end
SECTION_MAP: dict[int, tuple[str, str, int, str | None]] = {
    2: ("DESIGN-VISION.md", "Vision", 1, None),
    3: ("DESIGN-VISION.md", "Vision", 2, None),
    4: ("DESIGN-VISION.md", "Vision", 3, None),
    19: ("DESIGN-WORLD.md", "World", 1, "world"),
    20: ("DESIGN-WORLD.md", "World", 2, None),
    21: ("DESIGN-WORLD.md", "World", 3, "world"),
    24: ("DESIGN-WORLD.md", "World", 4, None),
    27: ("DESIGN-WILDS.md", "Wilds", 1, "wilds"),
    28: ("DESIGN-WILDS.md", "Wilds", 2, None),
    29: ("DESIGN-WILDS.md", "Wilds", 3, None),
    22: ("DESIGN-WILDS.md", "Wilds", 4, None),
    30: ("DESIGN-WILDS.md", "Wilds", 5, None),
    5: ("DESIGN-BATTLES.md", "Battle", 1, None),
    6: ("DESIGN-BATTLES.md", "Battle", 2, None),
    7: ("DESIGN-BATTLES.md", "Battle", 3, None),
    8: ("DESIGN-BATTLES.md", "Battle", 4, "battles"),
    9: ("DESIGN-BATTLES.md", "Battle", 5, "battles"),
    10: ("DESIGN-BATTLES.md", "Battle", 6, None),
    11: ("DESIGN-BATTLES.md", "Battle", 7, None),
    12: ("DESIGN-BATTLES.md", "Battle", 8, "battles"),
    13: ("DESIGN-BATTLES.md", "Battle", 9, None),
    14: ("DESIGN-BATTLES.md", "Battle", 10, "battles"),
    15: ("DESIGN-BATTLES.md", "Battle", 11, None),
    16: ("DESIGN-BATTLES.md", "Battle", 12, None),
    17: ("DESIGN-BATTLES.md", "Battle", 13, "battles"),
    18: ("DESIGN-BATTLES.md", "Battle", 14, None),
    23: ("DESIGN-BATTLES.md", "Battle", 15, None),
    25: ("DESIGN-BATTLES.md", "Battle", 16, None),
    37: ("DESIGN-STORY.md", "Story", 1, None),
    39: ("DESIGN-STORY.md", "Story", 2, None),
}

INDEX_SECTIONS = {1, 34, 35, 38}
SKIP_SECTIONS = {26, 32}  # §26 -> index pointer; §32 split manually

INVESTIGATIONS = {
    "battles": [
        "Dynamic battle rosters",
        "Living trainers",
        "Badge-scaled Gyms and trainers",
        "Universal PC",
        "Automatic restoration",
    ],
    "wilds": ["Open-world encounter structure"],
    "world": ["Accelerated clock", "HM progression"],
}

DOC_HEADERS = {
    "DESIGN-VISION.md": """# Pokémon Wandering Heart — Vision & Principles

> Core vision, open-world philosophy, and starting location.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Wilds:** [`DESIGN-WILDS.md`](DESIGN-WILDS.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md) · **Story:** [`DESIGN-STORY.md`](DESIGN-STORY.md) · **Future:** [`DESIGN-FUTURE.md`](DESIGN-FUTURE.md)

""",
    "DESIGN-WORLD.md": """# Pokémon Wandering Heart — World & Travel

> Transportation, route gating, HMs, field moves, and accelerated time.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Vision:** [`DESIGN-VISION.md`](DESIGN-VISION.md) · **Wilds:** [`DESIGN-WILDS.md`](DESIGN-WILDS.md)

""",
    "DESIGN-WILDS.md": """# Pokémon Wandering Heart — Wild Encounters & Ecology

> Seeded ecology, wild level ranges, distance caps, fishing, and content scope.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **World:** [`DESIGN-WORLD.md`](DESIGN-WORLD.md) · **Battles:** [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md)

""",
    "DESIGN-BATTLES.md": """# Pokémon Wandering Heart — Battles, Trainers & Progression

> Gyms, badges, level caps, trainer generation, battle systems, and QoL.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Vision:** [`DESIGN-VISION.md`](DESIGN-VISION.md) · **Wilds:** [`DESIGN-WILDS.md`](DESIGN-WILDS.md)

""",
    "DESIGN-STORY.md": """# Pokémon Wandering Heart — Story & Cleanup

> Story/script policy and vanilla content removal backlog.
>
> **Index:** [`DESIGN.md`](DESIGN.md) · **Implementation recipes:** [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md)

""",
}


def parse_sections(text: str) -> dict[int, tuple[str, str]]:
    """Return {section_num: (title, body)} for top-level # N. headers."""
    pattern = re.compile(r"^# (\d+)\. (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: dict[int, tuple[str, str]] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].lstrip("\n")
        sections[num] = (title, body)
    return sections


def parse_investigation_blocks(text: str) -> dict[str, str]:
    sec32 = parse_sections(text).get(32)
    if not sec32:
        return {}
    _, body = sec32
    blocks: dict[str, str] = {}
    parts = re.split(r"\n## ", body)
    for part in parts:
        if not part.strip():
            continue
        lines = part.split("\n", 1)
        name = lines[0].strip()
        content = lines[1] if len(lines) > 1 else ""
        blocks[name] = content
    return blocks


def slug(prefix: str, num: int, title: str) -> str:
    t = title.lower()
    t = re.sub(r"[^\w\s-]", "", t)
    t = re.sub(r"\s+", "-", t.strip())
    return f"{prefix.lower()}-{num}-{t}"


def build_ref_map(sections: dict[int, tuple[str, str]]) -> dict[int, tuple[str, str, str]]:
    """old_num -> (file, label, anchor)"""
    refs: dict[int, tuple[str, str, str]] = {}
    for old, (fname, prefix, new, _) in SECTION_MAP.items():
        title = sections[old][0]
        label = f"{prefix}-{new}"
        anchor = slug(prefix, new, title)
        refs[old] = (fname, label, anchor)
    refs[1] = ("DESIGN.md", "Index-1", "index-1-instructions-for-coding-agents")
    refs[34] = ("DESIGN.md", "Index-2", "index-2-current-technical-baseline")
    refs[35] = ("DESIGN.md", "Index-3", "index-3-open-design-questions")
    refs[38] = ("DESIGN.md", "Index-4", "index-4-game-identity")
    return refs


def link_for(old: int, refs: dict[int, tuple[str, str, str]]) -> str:
    fname, label, anchor = refs[old]
    if fname == "DESIGN.md":
        return f"[{label}](DESIGN.md#{anchor})"
    return f"[{label}]({fname}#{anchor})"


def rewrite_refs(content: str, refs: dict[int, tuple[str, str, str]]) -> str:
    def sub_section(m: re.Match[str]) -> str:
        n = int(m.group(1))
        if n not in refs:
            return m.group(0)
        return link_for(n, refs)

    # [§27](#27-...) or [§37](#37-story...)
    content = re.sub(
        r"\[§(\d+)\]\(#\d+[^)]*\)",
        sub_section,
        content,
    )
    # bare [§27] or [§§27–29]
    content = re.sub(
        r"\[§§(\d+)–(\d+)\]",
        lambda m: f"[{refs[int(m.group(1))][1]}–{refs[int(m.group(2))][1]}]"
        if int(m.group(1)) in refs and int(m.group(2)) in refs
        else m.group(0),
        content,
    )
    content = re.sub(r"\[§(\d+)\]", sub_section, content)
    # (§9 Phase 6) style - keep phase anchor, fix section part
    content = re.sub(
        r"\(§(\d+)\s",
        lambda m: f"({link_for(int(m.group(1)), refs)} "
        if int(m.group(1)) in refs
        else m.group(0),
        content,
    )
    content = re.sub(
        r"DESIGN2\.md",
        "DESIGN-FUTURE.md",
        content,
    )
    return content


def investigations_appendix(
    blocks: dict[str, str], keys: list[str], prefix: str, start_num: int, refs: dict
) -> str:
    if not keys:
        return ""
    out = f"\n---\n\n# {prefix}-{start_num}. Technical Investigations\n\n"
    out += "Open engineering questions for this area (from the former monolithic design doc).\n\n"
    for key in keys:
        if key not in blocks:
            continue
        out += f"## {key}\n\n"
        out += rewrite_refs(blocks[key], refs)
        if not out.endswith("\n"):
            out += "\n"
        out += "\n"
    return out


def main() -> None:
    text = DESIGN.read_text(encoding="utf-8")
    sections = parse_sections(text)
    inv_blocks = parse_investigation_blocks(text)
    refs = build_ref_map(sections)

    files_content: dict[str, list[str]] = {h: [] for h in DOC_HEADERS}
    index_parts: list[str] = []

    # Process mapped sections in stable order per file
    by_file: dict[str, list[tuple[int, str, str, str | None]]] = {}
    for old, meta in SECTION_MAP.items():
        by_file.setdefault(meta[0], []).append((meta[2], old, meta[1], meta[3]))

    for fname, items in by_file.items():
        items.sort(key=lambda x: x[0])
        max_num = max(i[0] for i in items)
        inv_num = max_num + 1
        prefix = items[0][2]
        inv_key = None
        for _, _, p, ik in items:
            if ik:
                inv_key = ik

        for new_num, old, prefix, _ in items:
            title, body = sections[old]
            header = f"# {prefix}-{new_num}. {title}\n\n"
            body = rewrite_refs(body, refs)
            files_content[fname].append(header + body + "\n---\n\n")

        if inv_key and inv_key in INVESTIGATIONS:
            appendix = investigations_appendix(
                inv_blocks, INVESTIGATIONS[inv_key], prefix, inv_num, refs
            )
            if appendix.strip():
                files_content[fname].append(appendix)

    # Index sections
    index_titles = {
        1: ("Index-1", "Instructions for Coding Agents"),
        34: ("Index-2", "Current Technical Baseline"),
        35: ("Index-3", "Open Design Questions"),
        38: ("Index-4", "Game Identity"),
    }
    for old in [1, 34, 35, 38]:
        prefix, default_title = index_titles[old]
        title, body = sections[old]
        header = f"# {prefix}. {title}\n\n"
        body = rewrite_refs(body, refs)
        index_parts.append(header + body + "\n---\n\n")

    # Write sub-docs
    for fname, header in DOC_HEADERS.items():
        path = ROOT / fname
        content = header + "".join(files_content[fname])
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        print(f"Wrote {fname} ({len(content.splitlines())} lines)")

    # Write new DESIGN.md index
    index_header = """# Pokémon Wandering Heart — Design Index

> Source of truth for **Pokémon Wandering Heart** core design. Detailed specs live in sub-documents with prefixed section IDs (`Vision-1`, `World-2`, `Battle-5`, …).
>
> **This index is NOT permission to implement everything described in the sub-docs.**

## Document map

| Document | Prefix | Topics |
|----------|--------|--------|
| [`DESIGN-VISION.md`](DESIGN-VISION.md) | `Vision-*` | Core vision, open-world rules, starting city/starter |
| [`DESIGN-WORLD.md`](DESIGN-WORLD.md) | `World-*` | Travel, gating, HMs, field moves, day/night |
| [`DESIGN-WILDS.md`](DESIGN-WILDS.md) | `Wilds-*` | Ecology seed, wild levels, fishing, content scope |
| [`DESIGN-BATTLES.md`](DESIGN-BATTLES.md) | `Battle-*` | Gyms, trainers, level caps, battle systems, QoL |
| [`DESIGN-STORY.md`](DESIGN-STORY.md) | `Story-*` | Story policy, vanilla cleanup backlog |
| [`DESIGN-FUTURE.md`](DESIGN-FUTURE.md) | `Future-*` | V2–V4 addons (balls, Full Moon, unlimited moves) |
| [`documentation/HACK-NOTES.md`](documentation/HACK-NOTES.md) | — | Implementation recipes, IDs, verified patches |

---

"""
    index_body = index_header + "".join(index_parts)
    DESIGN.write_text(index_body.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote DESIGN.md index ({len(index_body.splitlines())} lines)")

    # Backup note: old monolithic content replaced
    print("Done. Review cross-links and delete scripts/split_design_docs.py if no longer needed.")


if __name__ == "__main__":
    main()
