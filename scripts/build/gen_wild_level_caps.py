#!/usr/bin/env python3
"""Generate wild level cap tables from Route Levels graph distances."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE_LEVELS = ROOT / "scripts/dev/Route Levels"
DISTANCES_TSV = ROUTE_LEVELS / "location_distances.txt"
STARTING_CITIES = ROUTE_LEVELS / "starting_cities.txt"
ENCOUNTER_GRAPH = ROUTE_LEVELS / "encounter_area_graph.tsv"
CAP_POSTPROCESS_TSV = ROUTE_LEVELS / "cap_postprocess.tsv"
ENCOUNTER_TABLES_H = ROOT / "include/constants/encounter_tables.h"
OUT_C = ROOT / "src/field/wild_level_caps_data.c"
OUT_H = ROOT / "include/constants/generated/wild_level_caps.h"

WILD_LEVEL_MIN = 5
# PoC distance formula still tops out at 60; post-process can raise selected areas higher.
WILD_LEVEL_DISTANCE_MAX = 60
WILD_LEVEL_ROM_MAX = 90
WILD_LEVEL_NUMERATOR = WILD_LEVEL_DISTANCE_MAX - WILD_LEVEL_MIN  # 55


def load_starting_cities(path: Path) -> list[str]:
    cities: list[str] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        city = line.strip()
        if city:
            cities.append(city)
    return cities


def load_distances(path: Path) -> tuple[list[str], list[int], dict[str, list[int]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))

    if len(rows) < 2:
        raise ValueError(f"{path} must contain a header and MaxDistance row")

    header = rows[0]
    starting_cities = header[1:]
    max_row = rows[1]
    if max_row[0] != "MaxDistance":
        raise ValueError(f"{path} row 2 must be MaxDistance, got {max_row[0]!r}")

    max_distances = [int(value) for value in max_row[1:]]
    if len(max_distances) != len(starting_cities):
        raise ValueError("MaxDistance column count does not match starting cities")

    location_distances: dict[str, list[int]] = {}
    for row in rows[2:]:
        if not row or not row[0]:
            continue
        location = row[0]
        values = [int(value) for value in row[1:]]
        if len(values) != len(starting_cities):
            raise ValueError(f"Distance row for {location!r} has wrong column count")
        location_distances[location] = values

    return starting_cities, max_distances, location_distances


def load_encounter_graph(path: Path) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            raise ValueError(f"{path}:{line_number}: expected id<TAB>location")
        enc_id, graph_location = parts
        mapping[int(enc_id)] = graph_location.strip()
    return mapping


def parse_max_encounter_area_id(path: Path) -> int:
    values: list[int] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*ENCDATA_[A-Z0-9_]+\s*=\s*(\d+)", line)
        if match:
            values.append(int(match.group(1)))
    if not values:
        raise ValueError(f"No ENCDATA entries found in {path}")
    return max(values)


def compute_level_cap(distance: int, max_distance: int) -> int:
    """levelCap = 55 * max(0, d-1) / (max_d-1) + 5; distance-only caps in [5, 60]."""
    distance -= 1
    max_distance -= 1
    if distance < 0 or max_distance <= 0:
        return WILD_LEVEL_MIN
    if distance >= max_distance:
        return WILD_LEVEL_DISTANCE_MAX
    return (WILD_LEVEL_NUMERATOR * distance) // max_distance + WILD_LEVEL_MIN


def load_cap_postprocess(path: Path) -> tuple[dict[str, int], dict[str, int]]:
    """Return (fixed_cap_by_location, floor_by_location) from cap_postprocess.tsv."""
    fixed: dict[str, int] = {}
    floors: dict[str, int] = {}
    if not path.is_file():
        return fixed, floors

    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            raise ValueError(f"{path}:{line_number}: expected kind<TAB>graph_location<TAB>value")
        kind, graph_location, value_text = parts
        graph_location = graph_location.strip()
        value = int(value_text.strip())
        if value < WILD_LEVEL_MIN or value > WILD_LEVEL_ROM_MAX:
            raise ValueError(f"{path}:{line_number}: value {value} out of range")
        if kind == "fixed":
            if graph_location in fixed:
                raise ValueError(f"{path}:{line_number}: duplicate fixed row for {graph_location!r}")
            fixed[graph_location] = value
        elif kind == "floor":
            if graph_location in floors:
                raise ValueError(f"{path}:{line_number}: duplicate floor row for {graph_location!r}")
            floors[graph_location] = value
        else:
            raise ValueError(f"{path}:{line_number}: unknown kind {kind!r} (use fixed or floor)")
    return fixed, floors


def apply_cap_postprocess(cap: int, graph_location: str, fixed: dict[str, int], floors: dict[str, int]) -> int:
    if graph_location in fixed:
        return fixed[graph_location]
    if graph_location in floors:
        cap = max(cap, floors[graph_location])
    return cap


def format_row(values: list[int], width: int = 4) -> str:
    return ", ".join(f"{value:{width}d}" for value in values)


def generate(
    starting_cities: list[str],
    max_distances: list[int],
    location_distances: dict[str, list[int]],
    encounter_graph: dict[int, str],
    max_encounter_area_id: int,
    fixed_caps: dict[str, int],
    floor_caps: dict[str, int],
) -> tuple[str, str, int]:
    num_cities = len(starting_cities)
    num_areas = max_encounter_area_id + 1

    graph_locations = [""] * num_areas
    caps = [[WILD_LEVEL_MIN] * num_areas for _ in range(num_cities)]

    for enc_id, graph_location in encounter_graph.items():
        if enc_id >= num_areas:
            raise ValueError(f"Encounter area id {enc_id} exceeds max {max_encounter_area_id}")
        graph_locations[enc_id] = graph_location
        if graph_location not in location_distances:
            raise ValueError(
                f"Encounter area {enc_id} maps to unknown graph location {graph_location!r}"
            )
        distances = location_distances[graph_location]
        for city_index, distance in enumerate(distances):
            cap = compute_level_cap(distance, max_distances[city_index])
            caps[city_index][enc_id] = apply_cap_postprocess(
                cap, graph_location, fixed_caps, floor_caps
            )

    shipped_max = WILD_LEVEL_MIN
    for city_caps in caps:
        for cap in city_caps:
            if cap > shipped_max:
                shipped_max = cap
    if shipped_max > WILD_LEVEL_ROM_MAX:
        raise ValueError(f"Table contains cap {shipped_max} above WILD_LEVEL_ROM_MAX")

    header_guard = "CONSTANTS_GENERATED_WILD_LEVEL_CAPS_H"
    header = f"""#ifndef {header_guard}
#define {header_guard}

#define WILD_LEVEL_CAP_MIN {WILD_LEVEL_MIN}
#define WILD_LEVEL_CAP_MAX {shipped_max}
#define WILD_LEVEL_CAP_NUM_START_CITIES {num_cities}
#define WILD_LEVEL_CAP_NUM_ENCOUNTER_AREAS {num_areas}

#endif
"""

    cap_rows = []
    for city_index, city_caps in enumerate(caps):
        cap_rows.append(f"    // {starting_cities[city_index]}")
        # One brace pair per city row in a [cities][encAreas] table. Line-wrap
        # only; extra { } every N values would be separate top-level rows in C.
        cap_rows.append("    {")
        for start in range(0, num_areas, 16):
            chunk = city_caps[start : start + 16]
            cap_rows.append(f"        {format_row(chunk)},")
        cap_rows.append("    },")

    source = f"""#include "types.h"
#include "constants/generated/wild_level_caps.h"

// Generated by scripts/build/gen_wild_level_caps.py — do not edit.

const u8 sWildLevelCaps[WILD_LEVEL_CAP_NUM_START_CITIES][WILD_LEVEL_CAP_NUM_ENCOUNTER_AREAS] = {{
{chr(10).join(cap_rows)}
}};
"""
    return source, header, shipped_max


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--distances",
        type=Path,
        default=DISTANCES_TSV,
        help="location_distances.txt path",
    )
    parser.add_argument(
        "--starting-cities",
        type=Path,
        default=STARTING_CITIES,
        help="starting_cities.txt path",
    )
    parser.add_argument(
        "--encounter-graph",
        type=Path,
        default=ENCOUNTER_GRAPH,
        help="encounter_area_graph.tsv path",
    )
    parser.add_argument(
        "--cap-postprocess",
        type=Path,
        default=CAP_POSTPROCESS_TSV,
        help="cap_postprocess.tsv path (fixed caps and HM floors)",
    )
    args = parser.parse_args()

    _ = load_starting_cities(args.starting_cities)
    starting_cities, max_distances, location_distances = load_distances(args.distances)
    encounter_graph = load_encounter_graph(args.encounter_graph)
    fixed_caps, floor_caps = load_cap_postprocess(args.cap_postprocess)
    max_encounter_area_id = parse_max_encounter_area_id(ENCOUNTER_TABLES_H)

    source, header, shipped_max = generate(
        starting_cities,
        max_distances,
        location_distances,
        encounter_graph,
        max_encounter_area_id,
        fixed_caps,
        floor_caps,
    )

    OUT_H.parent.mkdir(parents=True, exist_ok=True)
    OUT_C.write_text(source, encoding="utf-8", newline="\n")
    OUT_H.write_text(header, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_C}")
    print(f"Wrote {OUT_H} (shipped max cap {shipped_max})")


if __name__ == "__main__":
    main()
