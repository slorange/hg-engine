#!/usr/bin/env python3
"""Calculate shortest connection distance from each starting city to every location.

Input formats
-------------
connections.txt: tab-separated rows
    FromLocation<TAB>ToLocation<TAB>[One way]

    Normal rows are traversable in both directions.
    Rows whose third column is "One way" are traversable only from the first
    location to the second.

starting_cities.txt: one starting city per line.

Output
------
A tab-separated table with one row per location and one distance column per
starting city. Unreachable locations are written as -1.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict, deque
from pathlib import Path


def load_connections(path: Path):
    """Return adjacency list plus locations in first-seen order."""
    graph: dict[str, set[str]] = defaultdict(set)
    locations: list[str] = []
    seen: set[str] = set()

    def remember(location: str) -> None:
        if location not in seen:
            seen.add(location)
            locations.append(location)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for line_number, row in enumerate(reader, start=1):
            # Ignore completely blank lines.
            if not row or not any(cell.strip() for cell in row):
                continue

            # Allow the final third column to be omitted.
            row = [cell.strip() for cell in row]
            if len(row) < 2 or not row[0] or not row[1]:
                raise ValueError(
                    f"Invalid connection on line {line_number}: expected at least "
                    f"two tab-separated locations"
                )

            source, target = row[0], row[1]
            connection_type = row[2] if len(row) >= 3 else ""

            remember(source)
            remember(target)

            graph[source].add(target)
            graph[target]  # Ensure target exists as a node even if it has no outgoing edges.

            if connection_type.casefold() != "one way":
                graph[target].add(source)

    return graph, locations


def load_starting_cities(path: Path) -> list[str]:
    cities: list[str] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            city = line.strip()
            if city:
                cities.append(city)
    return cities


def shortest_distances(graph: dict[str, set[str]], start: str) -> dict[str, int]:
    """Breadth-first search shortest distances from start."""
    distances = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        next_distance = distances[current] + 1

        for neighbor in graph[current]:
            if neighbor not in distances:
                distances[neighbor] = next_distance
                queue.append(neighbor)

    return distances


def write_distances(
    path: Path,
    graph: dict[str, set[str]],
    locations: list[str],
    starting_cities: list[str],
) -> None:
    missing = [city for city in starting_cities if city not in graph]
    if missing:
        raise ValueError(
            "Starting cities not found in the connections file: " + ", ".join(missing)
        )

    distances_by_city = {
        city: shortest_distances(graph, city) for city in starting_cities
    }

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["Location", *starting_cities])

        for location in locations:
            writer.writerow(
                [
                    location,
                    *[
                        distances_by_city[city].get(location, -1)
                        for city in starting_cities
                    ],
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate shortest graph distance from each starting city to every "
            "location in a connection file."
        )
    )
    parser.add_argument(
        "connections",
        nargs="?",
        type=Path,
        default=Path("connections.txt"),
        help="Tab-separated connections file (default: connections.txt)",
    )
    parser.add_argument(
        "starting_cities",
        nargs="?",
        type=Path,
        default=Path("starting_cities.txt"),
        help="One-starting-city-per-line file (default: starting_cities.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("location_distances.txt"),
        help="Output TSV file (default: location_distances.txt)",
    )
    args = parser.parse_args()

    graph, locations = load_connections(args.connections)
    starting_cities = load_starting_cities(args.starting_cities)
    write_distances(args.output, graph, locations, starting_cities)

    print(
        f"Wrote {len(locations)} locations x {len(starting_cities)} starting cities "
        f"to {args.output}"
    )


if __name__ == "__main__":
    main()
