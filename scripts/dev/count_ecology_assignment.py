#!/usr/bin/env python3
"""Count family placements in build/ecology/ecology_assignment.tsv (Wilds-6 audit)."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSIGN = ROOT / "build/ecology/ecology_assignment.tsv"
DEFAULT_OUT = ROOT / "build/ecology/ecology_assignment_counts.tsv"
DEFAULT_FAMILIES = ROOT / "data/ecology/ecology_families.tsv"
DEFAULT_LOCATIONS = ROOT / "data/ecology/ecology_locations.tsv"

# Must match ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE in gen_ecology_compatibility.py
TYPED_LAND_SLOTS_PER_TYPE = 3

LAND_HABITAT_ORDER = (
    "Field",
    "Forest",
    "Mountain",
    "Cave",
    "Ruins",
    "Tower",
    "City",
    "Sea",
)

METHOD_ORDER = (
    "Land",
    "Surf",
    "Old Rod",
    "Good Rod",
    "Super Rod",
    "Rock Smash",
    "Headbutt",
)

# Short TSV / table headers (internal keys stay METHOD_ORDER names).
METHOD_HEADER: dict[str, str] = {
    "Old Rod": "Old",
    "Good Rod": "Good",
    "Super Rod": "Super",
    "Rock Smash": "Smash",
    "Headbutt": "Head",
}


def parse_location_types(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in (raw or "").split(",") if part.strip())


def load_group_habitat(path: Path) -> dict[str, str]:
    """Map ecology group display name → Habitat (Field, Cave, …) from locations TSV."""
    habitats: dict[str, str] = {}
    if not path.is_file():
        return habitats
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            name = (row.get("Name") or "").strip()
            if not name:
                continue
            habitats[name] = (row.get("Habitat") or "").strip() or "?"
    return habitats


def load_group_location_types(path: Path) -> dict[str, tuple[str, ...]]:
    """Map group name → location Type tokens (empty = untyped land fill)."""
    types_by_group: dict[str, tuple[str, ...]] = {}
    if not path.is_file():
        return types_by_group
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            name = (row.get("Name") or "").strip()
            if not name:
                continue
            types_by_group[name] = parse_location_types(row.get("Types") or "")
    return types_by_group


def load_land_type_match_by_group(path: Path) -> dict[str, tuple[int, int]]:
    """Per group: (land_slot_count, land_slots_with_type_match=1)."""
    by_group: dict[str, list[int]] = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if (row.get("method") or "").strip() != "Land":
                continue
            group = (row.get("group_name") or "").strip()
            if not group:
                continue
            matched = (row.get("type_match") or "").strip() in ("1", "true", "True")
            by_group[group].append(1 if matched else 0)
    return {
        group: (len(flags), sum(flags)) for group, flags in by_group.items()
    }


@dataclass
class RouteTypeMatchRow:
    group: str
    types_label: str
    themed_target: int
    themed_matched: int

    @property
    def theme_status(self) -> str:
        if self.themed_matched < self.themed_target:
            return "under"
        if self.themed_matched > self.themed_target:
            return "over"
        return "exact"


def build_route_type_match_rows(
    assignment_path: Path,
    locations_path: Path,
) -> list[RouteTypeMatchRow]:
    location_types = load_group_location_types(locations_path)
    land_stats = load_land_type_match_by_group(assignment_path)
    rows: list[RouteTypeMatchRow] = []
    for group in sorted(location_types):
        type_tokens = location_types[group]
        if not type_tokens:
            continue
        land_total, matched = land_stats.get(group, (0, 0))
        if land_total == 0:
            continue
        target = min(land_total, len(type_tokens) * TYPED_LAND_SLOTS_PER_TYPE)
        rows.append(
            RouteTypeMatchRow(
                group=group,
                types_label=", ".join(type_tokens),
                themed_target=target,
                themed_matched=matched,
            )
        )
    return rows


def format_type_match_report(rows: list[RouteTypeMatchRow], *, tsv: bool) -> str:
    if not rows:
        return ""

    total_target = sum(r.themed_target for r in rows)
    total_matched = sum(min(r.themed_matched, r.themed_target) for r in rows)
    n_exact = sum(1 for r in rows if r.theme_status == "exact")
    n_under = sum(1 for r in rows if r.theme_status == "under")
    n_over = sum(1 for r in rows if r.theme_status == "over")
    pct = (100.0 * total_matched / total_target) if total_target else 0.0

    lines: list[str] = []
    prefix = "# " if tsv else ""
    lines.append("")
    lines.append(f"{prefix}Typed land theme slots (target = min(land cap, {TYPED_LAND_SLOTS_PER_TYPE} × type count)):")
    if tsv:
        lines.append(
            "# route\ttypes\tthemed_target\tthemed_matched\tvs_target"
        )
        for row in rows:
            lines.append(
                f"# {row.group}\t{row.types_label}\t{row.themed_target}\t"
                f"{row.themed_matched}\t{row.theme_status}"
            )
        lines.append(
            f"# overall: themed_quota_filled={total_matched}/{total_target} "
            f"({pct:.1f}%), routes exact={n_exact} under={n_under} over={n_over}"
        )
    else:
        name_w = max(len("route"), max(len(r.group) for r in rows))
        lines.append(
            f"{'route':<{name_w}}  {'types':<24}  tgt  mtch  vs tgt"
        )
        lines.append("-" * (name_w + 44))
        for row in rows:
            types_short = row.types_label if len(row.types_label) <= 24 else row.types_label[:21] + "..."
            lines.append(
                f"{row.group:<{name_w}}  {types_short:<24}  {row.themed_target:3d}  "
                f"{row.themed_matched:4d}  {row.theme_status}"
            )
        lines.append("")
        lines.append(
            f"Themed quota filled: {total_matched}/{total_target} ({pct:.1f}%)  "
            f"|  Routes: exact={n_exact}  under={n_under}  over={n_over}"
        )
    return "\n".join(lines) + "\n"


def load_counts(
    path: Path,
    group_habitat: dict[str, str],
    *,
    split_land_by_habitat: bool,
) -> tuple[
    dict[str, int],
    dict[str, int],
    dict[str, dict[str, int]],
    dict[str, dict[str, int]],
    dict[str, int],
    set[str],
]:
    """Returns (slot totals, route counts, by_method, by_land_habitat, base_species, unknown groups)."""
    totals: dict[str, int] = defaultdict(int)
    routes: dict[str, set[str]] = defaultdict(set)
    by_method: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_land_habitat: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    species_by_name: dict[str, int] = {}
    unknown_groups: set[str] = set()

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not reader.fieldnames or "family_name" not in reader.fieldnames:
            raise SystemExit(f"Unexpected format in {path} (need family_name column)")

        method_col = "method"
        for row in reader:
            name = (row.get("family_name") or "").strip()
            if not name:
                continue
            method = (row.get(method_col) or "").strip() or "?"
            group = (row.get("group_name") or "").strip()
            totals[name] += 1
            if group:
                routes[name].add(group)
            by_method[name][method] += 1
            if method == "Land" and split_land_by_habitat:
                if group and group not in group_habitat:
                    unknown_groups.add(group)
                habitat = group_habitat.get(group, "?") if group else "?"
                by_land_habitat[name][habitat] += 1
            if name not in species_by_name and (row.get("base_species") or "").strip():
                species_by_name[name] = int(row["base_species"])

    route_totals = {name: len(groups) for name, groups in routes.items()}
    return (
        dict(totals),
        route_totals,
        dict(by_method),
        dict(by_land_habitat),
        species_by_name,
        unknown_groups,
    )


def load_rarity_by_name(families_tsv: Path) -> dict[str, str]:
    """Map eco-fam display name → rarity label (matches gen-compat / assignment weights)."""
    labels: dict[str, str] = {}
    if not families_tsv.is_file():
        return labels
    with families_tsv.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            name = (row.get("Name") or "").strip()
            if not name:
                continue
            rarity = (row.get("Rarity") or "").strip()
            if rarity == "Special":
                rarity = ""
            labels[name] = rarity if rarity else "Normal"
    return labels


def all_methods_seen(
    by_method: dict[str, dict[str, int]], *, include_land: bool
) -> list[str]:
    seen: set[str] = set()
    for methods in by_method.values():
        for method, count in methods.items():
            if count > 0:
                seen.add(method)
    order = METHOD_ORDER if include_land else tuple(m for m in METHOD_ORDER if m != "Land")
    ordered = [m for m in order if m in seen]
    for m in sorted(seen - set(ordered)):
        if not include_land and m == "Land":
            continue
        ordered.append(m)
    return ordered


def land_habitat_columns(by_land_habitat: dict[str, dict[str, int]]) -> list[str]:
    seen: set[str] = set()
    for habitats in by_land_habitat.values():
        for habitat, count in habitats.items():
            if count > 0:
                seen.add(habitat)
    ordered = [h for h in LAND_HABITAT_ORDER if h in seen]
    for h in sorted(seen - set(ordered)):
        ordered.append(h)
    return ordered


def column_header(kind: str, key: str) -> str:
    if kind == "habitat":
        return key
    return METHOD_HEADER.get(key, key)


def fmt_method_count(count: int) -> str:
    return "" if count == 0 else str(count)


def trim_trailing_empty(cells: list[str]) -> list[str]:
    out = list(cells)
    while len(out) > 5 and out[-1] == "":
        out.pop()
    return out


def format_table(
    totals: dict[str, int],
    route_totals: dict[str, int],
    by_method: dict[str, dict[str, int]],
    by_land_habitat: dict[str, dict[str, int]],
    species_by_name: dict[str, int],
    rarity_by_name: dict[str, str],
    *,
    tsv: bool,
    split_land_by_habitat: bool,
) -> str:
    split_land = split_land_by_habitat and bool(by_land_habitat)
    methods = all_methods_seen(by_method, include_land=not split_land)
    land_habs = land_habitat_columns(by_land_habitat) if split_land else []
    count_columns: list[tuple[str, str]] = [
        ("method", m) for m in methods
    ] + [("habitat", h) for h in land_habs]
    headers = [column_header(kind, key) for kind, key in count_columns]
    names = sorted(totals.keys(), key=lambda n: (-totals[n], n.lower()))

    def rarity_label(name: str) -> str:
        return rarity_by_name.get(name, "")

    def count_cell(name: str, kind: str, key: str) -> int:
        if kind == "habitat":
            return by_land_habitat.get(name, {}).get(key, 0)
        return by_method[name].get(key, 0)

    lines: list[str] = []
    if tsv:
        header = ["family", "sp", "rarity", "rt", "tot", *headers]
        lines.append("\t".join(header))
        for name in names:
            row = [
                name,
                str(species_by_name.get(name, "")),
                rarity_label(name),
                str(route_totals.get(name, 0)),
                str(totals[name]),
                *[
                    fmt_method_count(count_cell(name, kind, key))
                    for kind, key in count_columns
                ],
            ]
            lines.append("\t".join(trim_trailing_empty(row)))
        return "\n".join(lines) + "\n"

    method_width = max(len(c) for c in headers) if headers else 4
    name_width = max(len("family"), max((len(n) for n in names), default=0))
    rarity_width = max(len("rarity"), max((len(rarity_label(n)) for n in names), default=0))
    lines.append(
        f"{'family':<{name_width}}  {'rarity':<{rarity_width}}  {'rt':>2}  {'tot':>3}  "
        + " ".join(f"{c:>{method_width}}" for c in headers)
    )
    lines.append(
        "-" * (name_width + rarity_width + 10 + len(headers) * (method_width + 1))
    )
    for name in names:
        method_cells = []
        for kind, key in count_columns:
            text = fmt_method_count(count_cell(name, kind, key))
            method_cells.append(f"{text:>{method_width}}" if text else " " * method_width)
        lines.append(
            f"{name:<{name_width}}  {rarity_label(name):<{rarity_width}}  "
            f"{route_totals.get(name, 0):2d}  {totals[name]:3d}  "
            + " ".join(method_cells)
        )
    lines.append("")
    lines.append(f"Families: {len(names)}  Slot assignments: {sum(totals.values())}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Count Pokémon family placements in an ecology assignment TSV."
    )
    parser.add_argument(
        "assignment",
        type=Path,
        nargs="?",
        default=DEFAULT_ASSIGN,
        help=f"Assignment TSV (default: {DEFAULT_ASSIGN.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--tsv",
        action="store_true",
        help="Machine-readable tab-separated output",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"Write report to file (default with --tsv: {DEFAULT_OUT.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--min",
        type=int,
        default=0,
        metavar="N",
        help="Only show families with total placements >= N",
    )
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        metavar="NAME",
        help="Only show these family names (repeatable)",
    )
    parser.add_argument(
        "--families-tsv",
        type=Path,
        default=DEFAULT_FAMILIES,
        help="Rarity source (default: data/ecology/ecology_families.tsv)",
    )
    parser.add_argument(
        "--locations-tsv",
        type=Path,
        default=DEFAULT_LOCATIONS,
        help="Habitat lookup for Land breakdown (default: data/ecology/ecology_locations.tsv)",
    )
    parser.add_argument(
        "--aggregate-land",
        action="store_true",
        help="Single Land column instead of Land (Field), Land (Cave), …",
    )
    args = parser.parse_args()

    path = args.assignment if args.assignment.is_absolute() else ROOT / args.assignment
    if not path.is_file():
        print(f"Missing assignment file: {path}", file=sys.stderr)
        return 1

    locations_path = (
        args.locations_tsv if args.locations_tsv.is_absolute() else ROOT / args.locations_tsv
    )
    split_land = not args.aggregate_land
    group_habitat = load_group_habitat(locations_path) if split_land else {}
    (
        totals,
        route_totals,
        by_method,
        by_land_habitat,
        species_by_name,
        unknown_groups,
    ) = load_counts(path, group_habitat, split_land_by_habitat=split_land)
    if unknown_groups:
        for group in sorted(unknown_groups):
            print(
                f"Warning: group {group!r} not in {locations_path.name}; "
                "Land slots counted under ? habitat",
                file=sys.stderr,
            )
    families_path = args.families_tsv if args.families_tsv.is_absolute() else ROOT / args.families_tsv
    rarity_by_name = load_rarity_by_name(families_path)

    if args.family:
        keep = {n.strip() for n in args.family}
        totals = {k: v for k, v in totals.items() if k in keep}
        route_totals = {k: v for k, v in route_totals.items() if k in keep}
        by_method = {k: v for k, v in by_method.items() if k in keep}
        by_land_habitat = {k: v for k, v in by_land_habitat.items() if k in keep}
        missing = keep - set(totals)
        for name in sorted(missing):
            print(f"Warning: {name!r} not in assignment", file=sys.stderr)

    if args.min > 0:
        totals = {k: v for k, v in totals.items() if v >= args.min}
        route_totals = {k: v for k, v in route_totals.items() if k in totals}
        by_method = {k: v for k, v in by_method.items() if k in totals}
        by_land_habitat = {k: v for k, v in by_land_habitat.items() if k in totals}

    use_tsv = args.tsv or (args.out is not None and str(args.out).endswith(".tsv"))
    text = format_table(
        totals,
        route_totals,
        by_method,
        by_land_habitat,
        species_by_name,
        rarity_by_name,
        tsv=use_tsv,
        split_land_by_habitat=split_land,
    )
    type_match_rows = build_route_type_match_rows(path, locations_path)
    text += format_type_match_report(type_match_rows, tsv=use_tsv)

    out_path = args.out
    if out_path is None and args.tsv:
        out_path = DEFAULT_OUT
    if out_path is not None:
        out_path = out_path if out_path.is_absolute() else ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path}", file=sys.stderr)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
