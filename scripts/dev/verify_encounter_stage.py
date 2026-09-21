#!/usr/bin/env python3
"""Sanity-check AdjustEncounterSpeciesForLevel logic for known trade/stone lines."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_H = ROOT / "include/constants/species.h"
EVOLUTIONS_C = ROOT / "data/Evolutions.c"
TSV = ROOT / "data/synthetic_evolution_thresholds.tsv"

SPECIES_RE = re.compile(r"#define\s+(SPECIES_[A-Z0-9_]+)\s+(\d+)")
MAX_SPECIES_COUNT_RE = re.compile(r"#define\s+MAX_SPECIES_INCLUDING_FORMS\b.*//\s*(\d+)")
BLOCK_RE = re.compile(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{", re.MULTILINE)
EVO_LEVEL_RE = re.compile(r"\{\s*EVO_LEVEL,\s*(\d+),\s*(SPECIES_[A-Z0-9_]+)\s*\}")


def load_species(path: Path) -> tuple[dict[str, int], int]:
    species: dict[str, int] = {}
    max_species = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        count_match = MAX_SPECIES_COUNT_RE.match(line.strip())
        if count_match:
            max_species = int(count_match.group(1))
            continue
        match = SPECIES_RE.match(line.strip())
        if match:
            name, value = match.group(1), int(match.group(2))
            if "_START" in name or name.endswith("_H"):
                continue
            species[name] = value
            max_species = max(max_species, value)
    if max_species == 0 and species:
        max_species = max(species.values())
    return species, max_species + 1


def parse_level_up_evolutions(path: Path) -> list[tuple[str, int, str]]:
    text = path.read_text(encoding="utf-8")
    evolutions: list[tuple[str, int, str]] = []
    for block in BLOCK_RE.finditer(text):
        species = block.group(1)
        start = block.end()
        next_block = BLOCK_RE.search(text, start)
        end = next_block.start() if next_block else len(text)
        chunk = text[start:end]
        for match in EVO_LEVEL_RE.finditer(chunk):
            evolutions.append((species, int(match.group(1)), match.group(2)))
            break
    return evolutions


def build_level_up_tables(species_map: dict[str, int], slot_count: int, evolutions):
    prevo = [0] * slot_count
    evo_target = [0] * slot_count
    min_stage_level = [1] * slot_count
    for source, level, target in evolutions:
        if source not in species_map or target not in species_map:
            continue
        src_id = species_map[source]
        tgt_id = species_map[target]
        evo_target[src_id] = tgt_id
        if prevo[tgt_id] == 0:
            prevo[tgt_id] = src_id
        min_stage_level[tgt_id] = level
    return prevo, evo_target, min_stage_level


def display_name_to_enum(name: str) -> str:
    cleaned = name.strip().replace(".", "").replace("-", " ")
    return "SPECIES_" + "_".join(part.upper() for part in cleaned.split())


def parse_synthetic_edges(path: Path, species_map: dict[str, int]) -> list[tuple[int, int, int]]:
    edges: list[tuple[int, int, int]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    col = {name: idx for idx, name in enumerate(header)}
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        from_enum = display_name_to_enum(parts[col["from"]].strip())
        to_enum = display_name_to_enum(parts[col["to"]].strip())
        min_level = int(parts[col["min_level"]].strip())
        edges.append((species_map[from_enum], species_map[to_enum], min_level))
    return edges


def find_synthetic_prevo(species: int, edges: list[tuple[int, int, int]]) -> int:
    for from_id, to_id, _ in edges:
        if to_id == species:
            return from_id
    return 0


def find_encounter_chain_base(species: int, prevo, synth_edges) -> int:
    for _ in range(16):
        level_up_prevo = prevo[species]
        synth_prevo = find_synthetic_prevo(species, synth_edges)
        if level_up_prevo:
            species = level_up_prevo
            continue
        if synth_prevo:
            species = synth_prevo
            continue
        break
    return species


def pick_synthetic_step(species: int, level: int, edges: list[tuple[int, int, int]]) -> int:
    best_to = 0
    best_min = 0
    for from_id, to_id, min_level in edges:
        if from_id != species or level < min_level:
            continue
        if min_level >= best_min:
            best_min = min_level
            best_to = to_id
    return best_to or species


def walk_encounter_stage_for_level(species: int, level: int, evo_target, min_stage_level, synth_edges) -> int:
    cur = species
    for _ in range(8):
        advanced = False
        next_level = evo_target[cur]
        if next_level and level >= min_stage_level[next_level]:
            cur = next_level
            advanced = True
        next_synth = pick_synthetic_step(cur, level, synth_edges)
        if next_synth != cur:
            cur = next_synth
            advanced = True
        if not advanced:
            break
    return cur


def adjust_encounter_species_for_level(species: int, level: int, prevo, evo_target, min_stage_level, synth_edges) -> int:
    species = find_encounter_chain_base(species, prevo, synth_edges)
    return walk_encounter_stage_for_level(species, level, evo_target, min_stage_level, synth_edges)


def main() -> int:
    species_map, slot_count = load_species(SPECIES_H)
    id_to_name = {v: k for k, v in species_map.items()}
    evolutions = parse_level_up_evolutions(EVOLUTIONS_C)
    prevo, evo_target, min_stage_level = build_level_up_tables(species_map, slot_count, evolutions)
    synth_edges = parse_synthetic_edges(TSV, species_map)

    cases = [
        ("SPECIES_ALAKAZAM", 10, "SPECIES_ABRA"),
        ("SPECIES_ALAKAZAM", 20, "SPECIES_KADABRA"),
        ("SPECIES_ALAKAZAM", 40, "SPECIES_ALAKAZAM"),
        ("SPECIES_VILEPLUME", 10, "SPECIES_ODDISH"),
        ("SPECIES_VILEPLUME", 25, "SPECIES_GLOOM"),
        ("SPECIES_VILEPLUME", 40, {"SPECIES_VILEPLUME", "SPECIES_BELLOSSOM"}),
        ("SPECIES_GENGAR", 10, "SPECIES_GASTLY"),
        ("SPECIES_ARCANINE", 10, "SPECIES_GROWLITHE"),
    ]

    failed = 0
    for authored, level, expected in cases:
        got = adjust_encounter_species_for_level(species_map[authored], level, prevo, evo_target, min_stage_level, synth_edges)
        got_name = id_to_name[got]
        if isinstance(expected, set):
            ok = got_name in expected
            expected_label = " or ".join(sorted(expected))
        else:
            ok = got_name == expected
            expected_label = expected
        status = "ok" if ok else "FAIL"
        print(f"{status}: {authored} @ Lv{level} -> {got_name} (expected {expected_label})")
        if not ok:
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
