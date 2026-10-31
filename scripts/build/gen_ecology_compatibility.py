#!/usr/bin/env python3
"""Generate ecology compatibility tables from data/ecology/*.tsv (Future-5 prebuild)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILIES_TSV = ROOT / "data/ecology/ecology_families.tsv"
LOCATIONS_TSV = ROOT / "data/ecology/ecology_locations.tsv"
SPECIES_H = ROOT / "include/constants/species.h"
ENCOUNTER_H = ROOT / "include/constants/encounter_tables.h"
OUT_C = ROOT / "tools/source/ecologygen/ecology_compat_data.c"
OUT_H = ROOT / "include/constants/generated/ecology_compat.h"
OUT_DUMP_FAMILY = ROOT / "data/ecology/ecology_compat_by_family.tsv"
OUT_DUMP_GROUP = ROOT / "data/ecology/ecology_compat_by_group.tsv"
OUT_STRINGS_C = ROOT / "tools/source/ecologygen/ecology_strings_data.c"
OUT_STRINGS_H = ROOT / "include/constants/generated/ecology_strings.h"
OUT_BIN = ROOT / "build/ecology/ecology_compat.bin"

ECOLOGY_COMPAT_BLOB_MAGIC = 0x314F4345  # 'ECO1' little-endian

SPECIES_RE = re.compile(r"#define\s+(SPECIES_[A-Z0-9_]+)\s+(\d+)")
ENCOUNTER_RE = re.compile(r"\s*ENCDATA_([A-Z0-9_]+)\s*=\s*(\d+)")

ECOLOGY_TIME_MORNING = 1 << 0
ECOLOGY_TIME_DAY = 1 << 1
ECOLOGY_TIME_NIGHT = 1 << 2
ECOLOGY_TIME_ALL = ECOLOGY_TIME_MORNING | ECOLOGY_TIME_DAY | ECOLOGY_TIME_NIGHT

METHOD_LAND = 0
METHOD_SURF = 1
METHOD_OLD_ROD = 2
METHOD_GOOD_ROD = 3
METHOD_SUPER_ROD = 4
METHOD_ROCK_SMASH = 5
METHOD_HEADBUTT = 6

METHOD_NAMES = (
    "ECOLOGY_METHOD_LAND",
    "ECOLOGY_METHOD_SURF",
    "ECOLOGY_METHOD_OLD_ROD",
    "ECOLOGY_METHOD_GOOD_ROD",
    "ECOLOGY_METHOD_SUPER_ROD",
    "ECOLOGY_METHOD_ROCK_SMASH",
    "ECOLOGY_METHOD_HEADBUTT",
)
METHOD_COUNT = len(METHOD_NAMES)

ROD_METHODS = frozenset({METHOD_OLD_ROD, METHOD_GOOD_ROD, METHOD_SUPER_ROD})

HUMAN_METHOD_ORDER = ("Land", "Surf", "Fishing", "Rock Smash", "Headbutt")


def human_method_label(method: int) -> str:
    if method == METHOD_LAND:
        return "Land"
    if method == METHOD_SURF:
        return "Surf"
    if method in ROD_METHODS:
        return "Fishing"
    if method == METHOD_ROCK_SMASH:
        return "Rock Smash"
    if method == METHOD_HEADBUTT:
        return "Headbutt"
    return METHOD_NAMES[method]

RARITY_NORMAL = 0
RARITY_COMMON = 1
RARITY_RARE = 2
RARITY_VERY_RARE = 3

RARITY_MAP = {
    "": RARITY_NORMAL,
    "Common": RARITY_COMMON,
    "Rare": RARITY_RARE,
    "Very Rare": RARITY_VERY_RARE,
}

RARITY_LABELS = ("Normal", "Common", "Rare", "Very Rare")

HABITAT_COLUMNS = ("Field", "Mountain", "Forest", "Cave", "Ruins", "Tower")
LOCATION_HABITAT_TO_FAMILY_COL = {
    "Field": "Field",
    "Mountain": "Mountain",
    "Forest": "Forest",
    "Cave": "Cave",
    "Ruins": "Ruins",
    "Tower": "Tower",
}

WATER_WET = frozenset({"Fresh", "Salt", "Cave"})

ECOLOGY_WATER_DRY = 1 << 0
ECOLOGY_WATER_FRESH = 1 << 1
ECOLOGY_WATER_SALT = 1 << 2
ECOLOGY_WATER_CAVE = 1 << 3

WATER_TOKEN_TO_FLAG = {
    "Dry": ECOLOGY_WATER_DRY,
    "Fresh": ECOLOGY_WATER_FRESH,
    "Salt": ECOLOGY_WATER_SALT,
    "Cave": ECOLOGY_WATER_CAVE,
}

ECOLOGY_GROUP_FLAG_SHUFFLE = 1 << 0
ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE = 3

FAMILY_WATER_ALLOWED = {
    "Salt": frozenset({"Salt"}),
    "Fresh": frozenset({"Fresh"}),
    "Cave": frozenset({"Cave"}),
    "Fresh/Cave": frozenset({"Fresh", "Cave"}),
    "Salt/Cave": frozenset({"Salt", "Cave"}),
    "Fresh/Salt": frozenset({"Fresh", "Salt"}),
    "All 3": frozenset({"Fresh", "Salt", "Cave"}),
}

EDGE_TYPE_MATCH = 1 << 0
EDGE_REQUIRED_PIN = 1 << 1

ECOLOGY_FAMILY_NO_PARTNER = 0xFF

SKIP_GROUP_NAME_SUBSTRINGS = ("Bug Catching Contest",)

# Only the named family may appear on this ecology group (shuffle + fill).
EXCLUSIVE_GROUP_FAMILY: dict[str, str] = {
    "Ruins of Alph Inside": "Unown",
}


def load_species_enum(path: Path) -> dict[str, int]:
    enums: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = SPECIES_RE.match(line.strip())
        if match:
            enums[match.group(1)] = int(match.group(2))
    return enums


def load_encounter_enum(path: Path) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ENCOUNTER_RE.match(line)
        if match:
            mapping[match.group(1)] = int(match.group(2))
    return mapping


SPECIES_NAME_OVERRIDES = {
    "Nidoran♀": "SPECIES_NIDORAN_F",
    "Nidoran♂": "SPECIES_NIDORAN_M",
    "Farfetch'd": "SPECIES_FARFETCHD",
    "Mr. Mime": "SPECIES_MR_MIME",
}


def display_name_to_enum(name: str) -> str:
    override = SPECIES_NAME_OVERRIDES.get(name.strip())
    if override:
        return override
    cleaned = name.strip().replace(".", "").replace("-", " ").replace("'", "")
    parts = cleaned.split()
    return "SPECIES_" + "_".join(part.upper() for part in parts)


def parse_index(index_text: str) -> int:
    text = index_text.strip()
    if text.startswith("#"):
        text = text[1:]
    return int(text)


def parse_types(types_text: str) -> set[str]:
    if not (types_text or "").strip():
        return set()
    return {part.strip() for part in types_text.split(",") if part.strip()}


def parse_nocturnal_mask(text: str) -> int:
    s = (text or "").strip()
    if not s:
        return ECOLOGY_TIME_ALL
    if s == "Morning/Day":
        return ECOLOGY_TIME_MORNING | ECOLOGY_TIME_DAY
    if s == "Morning/Night":
        return ECOLOGY_TIME_MORNING | ECOLOGY_TIME_NIGHT
    if s == "Morning":
        return ECOLOGY_TIME_MORNING
    if s == "Night":
        return ECOLOGY_TIME_NIGHT
    return ECOLOGY_TIME_ALL


def stored_land_time_mask(family_mask: int) -> int:
    """0 in ROM means all time periods (7)."""
    if family_mask == ECOLOGY_TIME_ALL:
        return 0
    return family_mask


def compat_version(tsv_paths: list[Path]) -> int:
    digest = hashlib.sha256()
    for path in tsv_paths:
        digest.update(path.read_bytes())
    digest.update(
        f"slots:{ECOLOGY_LAND_SLOTS},{ECOLOGY_SURF_SLOTS},{ECOLOGY_OLD_ROD_SLOTS},"
        f"{ECOLOGY_GOOD_ROD_SLOTS},{ECOLOGY_SUPER_ROD_SLOTS},"
        f"{ECOLOGY_HEADBUTT_SLOTS},{ECOLOGY_ROCK_SMASH_SLOTS},"
        f"{ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE}\n".encode()
    )
    return int.from_bytes(digest.digest()[:4], "big")


def parse_encdata_symbols(location_cell: str, enc_enum: dict[str, int]) -> list[int]:
    raw = (location_cell or "").strip()
    if not raw:
        return []
    ids: list[int] = []
    for part in re.split(r",\s*", raw):
        part = part.strip()
        if not part or " to " in part.lower():
            raise ValueError(f"Unresolved location range syntax: {part!r}")
        if not re.match(r"^[A-Z0-9_]+$", part):
            continue
        sym = f"ENCDATA_{part}" if not part.startswith("ENCDATA_") else part
        key = sym.replace("ENCDATA_", "")
        if key not in enc_enum:
            raise ValueError(f"Unknown encounter symbol {part!r}")
        ids.append(enc_enum[key])
    return ids


def int_cell(row: dict[str, str], key: str) -> int:
    text = (row.get(key) or "").strip()
    if not text:
        return 0
    return int(text)


def parse_water_column(text: str) -> frozenset[str]:
    tokens = frozenset(part.strip() for part in text.split(",") if part.strip())
    if not tokens:
        raise ValueError("Water column must list at least one token (Dry, Fresh, Salt, Cave)")
    unknown = tokens - set(WATER_TOKEN_TO_FLAG)
    if unknown:
        raise ValueError(f"Unknown Water token(s): {', '.join(sorted(unknown))}")
    return tokens


def water_mask_from_tokens(tokens: frozenset[str]) -> int:
    mask = 0
    for token in tokens:
        mask |= WATER_TOKEN_TO_FLAG[token]
    return mask


# Shuffle slot budgets (Morning/Day/Night columns = which periods exist, not slot counts).
ECOLOGY_LAND_SLOTS = 8
ECOLOGY_SURF_SLOTS = 3
ECOLOGY_OLD_ROD_SLOTS = 2
ECOLOGY_GOOD_ROD_SLOTS = 1
ECOLOGY_SUPER_ROD_SLOTS = 1
ECOLOGY_HEADBUTT_SLOTS = 3
ECOLOGY_ROCK_SMASH_SLOTS = 2


def method_slot_counts(row: dict[str, str]) -> list[int]:
    has_land = any(int_cell(row, key) > 0 for key in ("Morning", "Day", "Night"))
    land = ECOLOGY_LAND_SLOTS if has_land else 0
    surf = ECOLOGY_SURF_SLOTS if int_cell(row, "Surf") > 0 else 0
    old_rod = ECOLOGY_OLD_ROD_SLOTS if int_cell(row, "Old Rod") > 0 else 0
    good_rod = ECOLOGY_GOOD_ROD_SLOTS if int_cell(row, "Good Rod") > 0 else 0
    super_rod = ECOLOGY_SUPER_ROD_SLOTS if int_cell(row, "Super Rod") > 0 else 0
    rock_smash = ECOLOGY_ROCK_SMASH_SLOTS if int_cell(row, "Rock Smash") > 0 else 0
    headbutt = ECOLOGY_HEADBUTT_SLOTS if int_cell(row, "Headbutt") > 0 else 0
    return [
        land,
        surf,
        old_rod,
        good_rod,
        super_rod,
        rock_smash,
        headbutt,
    ]


@dataclass
class RequiredRoute:
    family_id: int
    group_id: int


@dataclass
class Family:
    family_id: int
    index: int
    name: str
    base_species: int
    rarity: int
    partner_family_id: int
    pairing_name: str
    required_group_names: list[str]
    land_time_mask: int
    required_tag: str
    avoid_tags: set[str]
    wet_dry: str
    water_type: str
    fish_surf: str
    habitats: set[str]
    headbutt: bool
    rock_smash: bool
    types: set[str]
    pin_only: bool


@dataclass
class Group:
    group_id: int
    name: str
    encdata_ids: list[int]
    water_tokens: frozenset[str]
    water_mask: int
    habitat: str
    location_types: set[str]
    land_period_mask: int
    methods: set[int]
    method_slots: list[int]
    skip: bool


@dataclass
class Edge:
    family_id: int
    group_id: int
    method: int
    flags: int


def load_families(path: Path, species_enums: dict[str, int]) -> list[Family]:
    families: list[Family] = []
    for row in csv.DictReader(path.open(encoding="utf-8-sig"), delimiter="\t"):
        special = (row.get("Special") or "").strip()
        required_raw = (row.get("Required on Route") or "").strip()
        required_group_names = [part.strip() for part in required_raw.split(",") if part.strip()]
        if special and not required_group_names:
            continue
        pin_only = bool(special and required_group_names)

        enum_name = display_name_to_enum(row["Name"])
        if enum_name not in species_enums:
            raise ValueError(f"Species enum missing for {row['Name']!r} ({enum_name})")

        habitats = {col for col in HABITAT_COLUMNS if (row.get(col) or "").strip()}
        family_types = parse_types(row.get("Type1", "")) | parse_types(row.get("Type2", ""))
        vibe = (row.get("Type (Vibe)") or "").strip()
        if vibe:
            family_types.add(vibe)

        rarity_text = (row.get("Rarity") or "").strip()
        if rarity_text == "Special":
            rarity_text = ""
        rarity = RARITY_MAP.get(rarity_text)
        if rarity is None:
            raise ValueError(f"Unknown rarity {rarity_text!r} for {row['Name']}")

        families.append(
            Family(
                family_id=len(families),
                index=parse_index(row["Index"]),
                name=row["Name"],
                base_species=species_enums[enum_name],
                rarity=rarity,
                partner_family_id=ECOLOGY_FAMILY_NO_PARTNER,
                pairing_name=(row.get("Pairing") or "").strip(),
                required_group_names=required_group_names,
                land_time_mask=parse_nocturnal_mask(row.get("Nocturnal", "")),
                required_tag=(row.get("Required Tag") or "").strip(),
                avoid_tags=parse_types(row.get("Avoid Tag", "")),
                wet_dry=(row.get("Wet/Dry") or "").strip(),
                water_type=(row.get("Water type (Salt, Fresh, Cave)") or "").strip(),
                fish_surf=(row.get("Fishing / Surfing") or "").strip(),
                habitats=habitats,
                headbutt=bool((row.get("Headbutt") or "").strip()),
                rock_smash=bool((row.get("Rock Smash") or "").strip()),
                types=family_types,
                pin_only=pin_only,
            )
        )
    return families


def resolve_pairings(families: list[Family]) -> None:
    """Pairing column: this family requires its partner on the same group when placed.

    Mutual rows (each names the other) → both get partnerFamilyId (symmetric co-placement).
    One-way (e.g. Mantine → Remoraid only) → only the naming family gets partnerFamilyId.
    """
    name_to_id = {fam.name: fam.family_id for fam in families}
    for fam in families:
        if not fam.pairing_name:
            continue
        partner_id = name_to_id.get(fam.pairing_name)
        if partner_id is None:
            raise ValueError(f"Pairing target {fam.pairing_name!r} missing for {fam.name!r}")
        if partner_id == fam.family_id:
            raise ValueError(f"Self pairing for {fam.name!r}")
        fam.partner_family_id = partner_id

    for fam in families:
        if fam.partner_family_id == ECOLOGY_FAMILY_NO_PARTNER:
            continue
        partner = families[fam.partner_family_id]
        if partner.pairing_name == fam.name:
            partner.partner_family_id = fam.family_id
        elif partner.partner_family_id not in (
            ECOLOGY_FAMILY_NO_PARTNER,
            fam.family_id,
        ):
            raise ValueError(
                f"Pairing conflict: {fam.name!r} requires {partner.name!r}, "
                f"but {partner.name!r} already requires another partner"
            )


def load_groups(path: Path, enc_enum: dict[str, int]) -> list[Group]:
    groups: list[Group] = []
    for row in csv.DictReader(path.open(encoding="utf-8-sig"), delimiter="\t"):
        name = row["Name"].strip()
        skip = any(sub in name for sub in SKIP_GROUP_NAME_SUBSTRINGS)

        land_mask = 0
        if int_cell(row, "Morning") > 0:
            land_mask |= ECOLOGY_TIME_MORNING
        if int_cell(row, "Day") > 0:
            land_mask |= ECOLOGY_TIME_DAY
        if int_cell(row, "Night") > 0:
            land_mask |= ECOLOGY_TIME_NIGHT

        methods: set[int] = set()
        if land_mask:
            methods.add(METHOD_LAND)
        if int_cell(row, "Surf") > 0:
            methods.add(METHOD_SURF)
        if int_cell(row, "Old Rod") > 0:
            methods.add(METHOD_OLD_ROD)
        if int_cell(row, "Good Rod") > 0:
            methods.add(METHOD_GOOD_ROD)
        if int_cell(row, "Super Rod") > 0:
            methods.add(METHOD_SUPER_ROD)
        if int_cell(row, "Rock Smash") > 0:
            methods.add(METHOD_ROCK_SMASH)
        if int_cell(row, "Headbutt") > 0:
            methods.add(METHOD_HEADBUTT)

        enc_ids = parse_encdata_symbols(row.get("Location", ""), enc_enum)
        water_tokens = parse_water_column((row.get("Water") or "").strip())

        groups.append(
            Group(
                group_id=len(groups),
                name=name,
                encdata_ids=enc_ids,
                water_tokens=water_tokens,
                water_mask=water_mask_from_tokens(water_tokens),
                habitat=(row.get("Habitat") or "").strip(),
                location_types=parse_types(row.get("Types", "")),
                land_period_mask=land_mask,
                methods=methods,
                method_slots=method_slot_counts(row),
                skip=skip,
            )
        )
    return groups


def wet_dry_ok(family: Family, group: Group, method: int) -> bool:
    if method in (METHOD_SURF, METHOD_OLD_ROD, METHOD_GOOD_ROD, METHOD_SUPER_ROD):
        return True
    if not family.wet_dry:
        return True
    if family.wet_dry == "Wet":
        return bool(group.water_tokens & WATER_WET)
    if family.wet_dry == "Dry":
        return "Dry" in group.water_tokens
    return True


def required_tag_ok(family: Family, group: Group) -> bool:
    if not family.required_tag:
        return True
    return family.required_tag in group.location_types


def avoid_tag_ok(family: Family, group: Group) -> bool:
    if not family.avoid_tags or not group.location_types:
        return True
    return not bool(family.avoid_tags & group.location_types)


def habitat_ok(family: Family, group: Group) -> bool:
    col = LOCATION_HABITAT_TO_FAMILY_COL.get(group.habitat)
    if col is None:
        return False
    return col in family.habitats


def habitat_ok_required_land(family: Family, group: Group) -> bool:
    if habitat_ok(family, group):
        return True
    if group.habitat in ("Cave", "Tower") and "Field" in family.habitats:
        return True
    return False


def land_time_ok(family: Family, group: Group) -> bool:
    effective = family.land_time_mask & group.land_period_mask
    return effective != 0


def water_type_ok(family: Family, group: Group, method: int) -> bool:
    if method not in (METHOD_SURF, METHOD_OLD_ROD, METHOD_GOOD_ROD, METHOD_SUPER_ROD):
        return True
    if not family.water_type:
        return True
    allowed = FAMILY_WATER_ALLOWED.get(family.water_type)
    if not allowed:
        return True
    water_for_fish = group.water_tokens - {"Dry"}
    return bool(water_for_fish & allowed)


def fishing_ok(family: Family, method: int) -> bool:
    if method == METHOD_SURF:
        return family.fish_surf in ("Surf", "Both")
    if method in (METHOD_OLD_ROD, METHOD_GOOD_ROD, METHOD_SUPER_ROD):
        return family.fish_surf in ("Fish", "Both")
    return True


def type_match(family: Family, group: Group) -> bool:
    if not family.types or not group.location_types:
        return False
    return bool(family.types & group.location_types)


def group_has_method(group: Group, method: int) -> bool:
    return method in group.methods


def family_allowed_on_method_for_required(family: Family, method: int) -> bool:
    if method == METHOD_LAND:
        return True
    if method == METHOD_SURF:
        return family.fish_surf in ("Surf", "Both")
    if method in ROD_METHODS:
        return family.fish_surf in ("Fish", "Both")
    if method == METHOD_HEADBUTT:
        return family.headbutt
    if method == METHOD_ROCK_SMASH:
        return family.rock_smash
    return False


def required_methods_at_group(family: Family, group: Group) -> list[int]:
    """Methods that must be filled for Required on Route (rods → Old Rod only)."""
    methods: list[int] = []
    if group_has_method(group, METHOD_LAND) and habitat_ok_required_land(family, group):
        if wet_dry_ok(family, group, METHOD_LAND) and required_tag_ok(family, group):
            if land_time_ok(family, group):
                methods.append(METHOD_LAND)
    if group_has_method(group, METHOD_SURF):
        if (
            family_allowed_on_method_for_required(family, METHOD_SURF)
            and water_type_ok(family, group, METHOD_SURF)
        ):
            methods.append(METHOD_SURF)
    if any(group_has_method(group, m) for m in ROD_METHODS):
        if (
            group_has_method(group, METHOD_OLD_ROD)
            and family_allowed_on_method_for_required(family, METHOD_OLD_ROD)
            and water_type_ok(family, group, METHOD_OLD_ROD)
        ):
            methods.append(METHOD_OLD_ROD)
    if group_has_method(group, METHOD_ROCK_SMASH):
        if family.rock_smash and wet_dry_ok(family, group, METHOD_ROCK_SMASH):
            methods.append(METHOD_ROCK_SMASH)
    if group_has_method(group, METHOD_HEADBUTT):
        if family.headbutt and wet_dry_ok(family, group, METHOD_HEADBUTT):
            methods.append(METHOD_HEADBUTT)
    return methods


def edge_key(edge: Edge) -> tuple[int, int, int]:
    return (edge.family_id, edge.group_id, edge.method)


def add_edge(edges: list[Edge], edge_map: dict[tuple[int, int, int], Edge], edge: Edge) -> None:
    key = edge_key(edge)
    existing = edge_map.get(key)
    if existing is None:
        edge_map[key] = edge
        edges.append(edge)
        return
    existing.flags |= edge.flags


def add_required_pin_edges(
    families: list[Family], groups: list[Group], edges: list[Edge]
) -> None:
    group_by_name = {group.name: group for group in groups}
    edge_map = {edge_key(edge): edge for edge in edges}
    for fam in families:
        for group_name in fam.required_group_names:
            group = group_by_name.get(group_name)
            if group is None:
                raise ValueError(f"Unknown Required on Route group {group_name!r} for {fam.name}")
            if group.skip:
                raise ValueError(f"Required on Route targets non-shuffle group {group_name!r}")
            if not avoid_tag_ok(fam, group):
                raise ValueError(f"Avoid tag blocks required route {group_name!r} for {fam.name}")
            methods = required_methods_at_group(fam, group)
            if not methods:
                raise ValueError(
                    f"No compat methods for required route {group_name!r} ({fam.name})"
                )
            for method in methods:
                flags = EDGE_REQUIRED_PIN
                if method == METHOD_LAND and type_match(fam, group):
                    flags |= EDGE_TYPE_MATCH
                add_edge(
                    edges,
                    edge_map,
                    Edge(family_id=fam.family_id, group_id=group.group_id, method=method, flags=flags),
                )


def build_required_routes(families: list[Family], groups: list[Group]) -> list[RequiredRoute]:
    group_by_name = {group.name: group for group in groups}
    routes: list[RequiredRoute] = []
    for fam in families:
        for group_name in fam.required_group_names:
            group = group_by_name[group_name]
            routes.append(RequiredRoute(family_id=fam.family_id, group_id=group.group_id))
    return routes


def build_edges(families: list[Family], groups: list[Group]) -> list[Edge]:
    edges: list[Edge] = []
    for family in families:
        if family.pin_only:
            continue
        for group in groups:
            if group.skip:
                continue
            exclusive = EXCLUSIVE_GROUP_FAMILY.get(group.name)
            if exclusive is not None and family.name != exclusive:
                continue
            if not avoid_tag_ok(family, group):
                continue
            for method in group.methods:
                if method == METHOD_LAND:
                    if family.fish_surf == "Fish":
                        continue
                    if not habitat_ok(family, group):
                        continue
                    if not wet_dry_ok(family, group, method):
                        continue
                    if not required_tag_ok(family, group):
                        continue
                    if not land_time_ok(family, group):
                        continue
                elif method == METHOD_HEADBUTT:
                    if not family.headbutt:
                        continue
                    if not wet_dry_ok(family, group, method):
                        continue
                elif method == METHOD_ROCK_SMASH:
                    if not family.rock_smash:
                        continue
                    if not wet_dry_ok(family, group, method):
                        continue
                elif method in (METHOD_SURF, METHOD_OLD_ROD, METHOD_GOOD_ROD, METHOD_SUPER_ROD):
                    if not fishing_ok(family, method):
                        continue
                    if not water_type_ok(family, group, method):
                        continue
                else:
                    continue

                flags = EDGE_TYPE_MATCH if type_match(family, group) else 0
                edges.append(
                    Edge(
                        family_id=family.family_id,
                        group_id=group.group_id,
                        method=method,
                        flags=flags,
                    )
                )
    add_required_pin_edges(families, groups, edges)
    return edges


def format_route_method_list(group_methods: dict[str, set[str]]) -> str:
    """group_name -> method labels -> 'Route A: Land, Surf; Route B: Fishing'."""
    parts: list[str] = []
    for group_name in sorted(group_methods):
        methods = group_methods[group_name]
        ordered = [m for m in HUMAN_METHOD_ORDER if m in methods]
        parts.append(f"{group_name}: {', '.join(ordered)}")
    return "; ".join(parts)


def write_dumps(
    family_path: Path,
    group_path: Path,
    families: list[Family],
    groups: list[Group],
    edges: list[Edge],
) -> None:
    family_path.parent.mkdir(parents=True, exist_ok=True)
    fam_by_id = {f.family_id: f for f in families}
    grp_by_id = {g.group_id: g for g in groups}

    # By family: (family_id, type_match) -> group -> human methods
    family_buckets: dict[tuple[int, int], dict[str, set[str]]] = {}
    for edge in edges:
        type_match_flag = 1 if edge.flags & EDGE_TYPE_MATCH else 0
        key = (edge.family_id, type_match_flag)
        grp_name = grp_by_id[edge.group_id].name
        label = human_method_label(edge.method)
        family_buckets.setdefault(key, {}).setdefault(grp_name, set()).add(label)

    with family_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["family_name", "type_match", "rarity", "routes_and_methods"])
        for family in sorted(families, key=lambda fam: fam.index):
            for type_match_flag in (0, 1):
                group_methods = family_buckets.get((family.family_id, type_match_flag))
                if not group_methods:
                    continue
                w.writerow(
                    [
                        family.name,
                        type_match_flag,
                        RARITY_LABELS[family.rarity],
                        format_route_method_list(group_methods),
                    ]
                )

    # By group: (group_id, human method, type_match) -> family names
    group_buckets: dict[tuple[int, str, int], set[str]] = {}
    for edge in edges:
        type_match_flag = 1 if edge.flags & EDGE_TYPE_MATCH else 0
        label = human_method_label(edge.method)
        key = (edge.group_id, label, type_match_flag)
        group_buckets.setdefault(key, set()).add(fam_by_id[edge.family_id].name)

    with group_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["group_name", "encounter_type", "type_match", "families"])
        for group in sorted(groups, key=lambda g: g.name.lower()):
            for method_label in HUMAN_METHOD_ORDER:
                for type_match_flag in (0, 1):
                    names = group_buckets.get((group.group_id, method_label, type_match_flag))
                    if not names:
                        continue
                    w.writerow(
                        [
                            group.name,
                            method_label,
                            type_match_flag,
                            ", ".join(sorted(names, key=str.lower)),
                        ]
                    )


def write_header(
    path: Path,
    version: int,
    num_families: int,
    num_groups: int,
    num_edges: int,
    num_required_routes: int,
    max_slots_per_bucket: int,
    total_slots: int,
    max_family_edge_scratch: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""#ifndef CONSTANTS_GENERATED_ECOLOGY_COMPAT_H
#define CONSTANTS_GENERATED_ECOLOGY_COMPAT_H

#ifdef ECOLOGY_STANDALONE
#include "ecology/ecology_standalone_types.h"
#else
#include "types.h"
#endif

#define ECOLOGY_COMPAT_VERSION 0x{version:08X}u

#define ECOLOGY_TIME_MORNING  (1u << 0)
#define ECOLOGY_TIME_DAY      (1u << 1)
#define ECOLOGY_TIME_NIGHT    (1u << 2)
#define ECOLOGY_TIME_ALL      (ECOLOGY_TIME_MORNING | ECOLOGY_TIME_DAY | ECOLOGY_TIME_NIGHT)

#define ECOLOGY_LAND_TIME_ALL 0u

enum EcologyMethod {{
    ECOLOGY_METHOD_LAND = 0,
    ECOLOGY_METHOD_SURF,
    ECOLOGY_METHOD_OLD_ROD,
    ECOLOGY_METHOD_GOOD_ROD,
    ECOLOGY_METHOD_SUPER_ROD,
    ECOLOGY_METHOD_ROCK_SMASH,
    ECOLOGY_METHOD_HEADBUTT,
    ECOLOGY_METHOD_COUNT,
}};

enum EcologyRarity {{
    ECOLOGY_RARITY_NORMAL = 0,
    ECOLOGY_RARITY_COMMON,
    ECOLOGY_RARITY_RARE,
    ECOLOGY_RARITY_VERY_RARE,
}};

#define ECOLOGY_EDGE_TYPE_MATCH (1u << 0)
#define ECOLOGY_EDGE_REQUIRED_PIN (1u << 1)

#define ECOLOGY_FAMILY_NO_PARTNER 0xFFu

#define ECOLOGY_WATER_DRY   (1u << 0)
#define ECOLOGY_WATER_FRESH (1u << 1)
#define ECOLOGY_WATER_SALT  (1u << 2)
#define ECOLOGY_WATER_CAVE  (1u << 3)

#define ECOLOGY_GROUP_FLAG_SHUFFLE (1u << 0)

#define ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE {ECOLOGY_TYPED_LAND_SLOTS_PER_TYPE}u

#define ECOLOGY_GEN_MAX_SLOTS_PER_BUCKET {max_slots_per_bucket}u
#define ECOLOGY_GEN_TOTAL_SLOTS {total_slots}u
#define ECOLOGY_GEN_MAX_FAMILY_EDGE_SCRATCH {max_family_edge_scratch}u

typedef struct EcologyFamilyInfo {{
    u16 baseSpecies;
    u16 dexIndex;
    u8 rarity;
    u8 partnerFamilyId;
    u8 landTimeMask;
    u8 padding;
}} EcologyFamilyInfo;

typedef struct EcologyRequiredRoute {{
    u8 familyId;
    u8 groupId;
}} EcologyRequiredRoute;

typedef struct EcologyGroupInfo {{
    u16 encdataOffset;
    u8 encdataCount;
    u8 landPeriodMask;
    u8 methodMask;
    u8 waterMask;
}} EcologyGroupInfo;

typedef struct EcologyCompatEdge {{
    u8 groupId;
    u8 method;
    u8 flags;
    u8 padding;
}} EcologyCompatEdge;

typedef struct EcologyGroupLandEntry {{
    u16 familyId;
    u8 flags;
    u8 padding;
}} EcologyGroupLandEntry;

typedef struct EcologyGroupBucketEntry {{
    u16 familyId;
    u8 flags;
    u8 padding;
}} EcologyGroupBucketEntry;

#define ECOLOGY_NUM_FAMILIES {num_families}
#define ECOLOGY_NUM_GROUPS {num_groups}
#define ECOLOGY_NUM_EDGES {num_edges}
#define ECOLOGY_NUM_REQUIRED_ROUTES {num_required_routes}

extern const EcologyFamilyInfo sEcologyFamilyInfo[ECOLOGY_NUM_FAMILIES];
extern const EcologyRequiredRoute sEcologyRequiredRoutes[ECOLOGY_NUM_REQUIRED_ROUTES];
extern const EcologyGroupInfo sEcologyGroups[ECOLOGY_NUM_GROUPS];
extern const u8 sEcologyGroupEncdataIds[];
extern const EcologyGroupLandEntry sEcologyGroupLandEntries[];
extern const u16 sEcologyGroupLandOffsets[ECOLOGY_NUM_GROUPS + 1];
extern const EcologyGroupBucketEntry sEcologyGroupBucketEntries[];
extern const u16 sEcologyGroupBucketOffsets[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT + 1];
extern const u8 sEcologyGroupFlags[ECOLOGY_NUM_GROUPS];
extern const u8 sEcologyGroupMethodSlots[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT];
extern const u8 sEcologyGroupLocationTypeCount[ECOLOGY_NUM_GROUPS];

#endif
""",
        encoding="utf-8",
    )


def c_escape_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def write_strings_header(path: Path, num_families: int, num_groups: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""#ifndef CONSTANTS_GENERATED_ECOLOGY_STRINGS_H
#define CONSTANTS_GENERATED_ECOLOGY_STRINGS_H

#include "constants/generated/ecology_compat.h"

extern const char *const sEcologyGroupNames[ECOLOGY_NUM_GROUPS];
extern const char *const sEcologyFamilyNames[ECOLOGY_NUM_FAMILIES];

#endif
""",
        encoding="utf-8",
    )


def write_strings_source(path: Path, families: list[Family], groups: list[Group]) -> None:
    group_rows = [f'    "{c_escape_string(g.name)}",' for g in groups]
    family_rows = [f'    "{c_escape_string(f.name)}",' for f in families]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""#include "constants/generated/ecology_strings.h"

// Generated by scripts/build/gen_ecology_compatibility.py — host / debug labels only.

const char *const sEcologyGroupNames[ECOLOGY_NUM_GROUPS] = {{
{chr(10).join(group_rows)}
}};

const char *const sEcologyFamilyNames[ECOLOGY_NUM_FAMILIES] = {{
{chr(10).join(family_rows)}
}};
""",
        encoding="utf-8",
    )


def method_mask(methods: set[int]) -> int:
    mask = 0
    for method in methods:
        mask |= 1 << method
    return mask


def align4(offset: int) -> int:
    return (offset + 3) & ~3


@dataclass
class CompatTables:
    family_info: list[tuple[int, int, int, int, int, int]]
    group_info: list[tuple[int, int, int, int, int]]
    encdata_ids: list[int]
    land_entries: list[tuple[int, int, int]]
    land_offsets: list[int]
    bucket_entries: list[tuple[int, int, int]]
    bucket_offsets: list[int]
    group_flags: list[int]
    method_slots: list[int]
    location_type_count: list[int]
    max_slots: int
    total_slots: int


def max_family_edge_scratch_refs(
    families: list[Family],
    groups: list[Group],
    edges: list[Edge],
) -> int:
    """Upper bound for EcologyCollectFamilyEdges output (one family at a time)."""
    land_lists: list[list[Edge]] = [[] for _ in groups]
    bucket_lists: list[list[Edge]] = [[] for _ in groups for _ in range(METHOD_COUNT)]

    for edge in edges:
        if edge.method == METHOD_LAND:
            land_lists[edge.group_id].append(edge)
        else:
            bucket_lists[edge.group_id * METHOD_COUNT + edge.method].append(edge)

    max_count = 0
    for family in families:
        count = 0
        for group_id, group in enumerate(groups):
            if group.skip:
                continue
            for edge in land_lists[group_id]:
                if edge.family_id == family.family_id:
                    count += 1
            for method in range(METHOD_COUNT):
                if method == METHOD_LAND:
                    continue
                idx = group_id * METHOD_COUNT + method
                for edge in bucket_lists[idx]:
                    if edge.family_id == family.family_id:
                        count += 1
        max_count = max(max_count, count)
    return max(max_count, 1)


def prepare_compat_tables(
    families: list[Family],
    groups: list[Group],
    edges: list[Edge],
) -> CompatTables:
    land_lists: list[list[Edge]] = [[] for _ in groups]
    bucket_lists: list[list[Edge]] = [[] for _ in groups for _ in range(METHOD_COUNT)]

    for edge in edges:
        if edge.method == METHOD_LAND:
            land_lists[edge.group_id].append(edge)
        else:
            idx = edge.group_id * METHOD_COUNT + edge.method
            bucket_lists[idx].append(edge)

    land_entries: list[tuple[int, int, int]] = []
    land_offsets = [0]
    for land_edges in land_lists:
        for edge in sorted(land_edges, key=lambda e: e.family_id):
            land_entries.append((edge.family_id, edge.flags, 0))
        land_offsets.append(len(land_entries))

    bucket_entries: list[tuple[int, int, int]] = []
    bucket_offsets = [0]
    for bucket_edges in bucket_lists:
        for edge in sorted(bucket_edges, key=lambda e: e.family_id):
            bucket_entries.append((edge.family_id, edge.flags, 0))
        bucket_offsets.append(len(bucket_entries))

    encdata_ids: list[int] = []
    group_info: list[tuple[int, int, int, int, int]] = []
    enc_offset = 0
    for group in groups:
        for enc_id in group.encdata_ids:
            encdata_ids.append(enc_id)
        group_info.append(
            (
                enc_offset,
                len(group.encdata_ids),
                group.land_period_mask,
                method_mask(group.methods),
                group.water_mask,
            )
        )
        enc_offset += len(group.encdata_ids)

    group_flags = [ECOLOGY_GROUP_FLAG_SHUFFLE if not group.skip else 0 for group in groups]
    location_type_count = [len(group.location_types) for group in groups]
    method_slots: list[int] = []
    max_slots = 0
    total_slots = 0
    for group in groups:
        for slot_count in group.method_slots:
            method_slots.append(slot_count)
            max_slots = max(max_slots, slot_count)
            total_slots += slot_count

    family_info = [
        (
            fam.base_species,
            fam.index,
            fam.rarity,
            fam.partner_family_id,
            stored_land_time_mask(fam.land_time_mask),
            0,
        )
        for fam in families
    ]

    return CompatTables(
        family_info=family_info,
        group_info=group_info,
        encdata_ids=encdata_ids,
        land_entries=land_entries,
        land_offsets=land_offsets,
        bucket_entries=bucket_entries,
        bucket_offsets=bucket_offsets,
        group_flags=group_flags,
        method_slots=method_slots,
        location_type_count=location_type_count,
        max_slots=max_slots,
        total_slots=total_slots,
    )


def write_binary_blob(
    path: Path,
    version: int,
    families: list[Family],
    groups: list[Group],
    tables: CompatTables,
    required_routes: list[RequiredRoute],
) -> None:
    header_size = struct.calcsize("<IIHHHHHHIIIIIIIIIIHHI")

    family_bytes = b"".join(struct.pack("<HHBBBB", *row) for row in tables.family_info)
    group_bytes = b"".join(struct.pack("<HBBBB", *row) for row in tables.group_info)
    enc_bytes = bytes(tables.encdata_ids)
    land_bytes = b"".join(struct.pack("<HBB", *row) for row in tables.land_entries)
    land_off_bytes = struct.pack(f"<{len(tables.land_offsets)}H", *tables.land_offsets)
    bucket_bytes = b"".join(struct.pack("<HBB", *row) for row in tables.bucket_entries)
    bucket_off_bytes = struct.pack(f"<{len(tables.bucket_offsets)}H", *tables.bucket_offsets)
    flags_bytes = bytes(tables.group_flags)
    slots_bytes = bytes(tables.method_slots)
    type_count_bytes = bytes(tables.location_type_count)
    required_bytes = b"".join(
        struct.pack("<BB", route.family_id, route.group_id) for route in required_routes
    )

    section_data = [
        family_bytes,
        group_bytes,
        enc_bytes,
        land_bytes,
        land_off_bytes,
        bucket_bytes,
        bucket_off_bytes,
        flags_bytes,
        slots_bytes,
        type_count_bytes,
        required_bytes,
    ]

    cursor = header_size
    offsets: list[int] = []
    blob_pieces: list[bytes] = []
    for data in section_data:
        pad = align4(cursor) - cursor
        if pad:
            blob_pieces.append(b"\x00" * pad)
            cursor += pad
        offsets.append(cursor)
        blob_pieces.append(data)
        cursor += len(data)

    (
        off_family,
        off_groups,
        off_enc,
        off_land_entries,
        off_land_offsets,
        off_bucket_entries,
        off_bucket_offsets,
        off_flags,
        off_slots,
        off_type_count,
        off_required,
    ) = offsets

    header = struct.pack(
        "<IIHHHHHHIIIIIIIIIIHHI",
        ECOLOGY_COMPAT_BLOB_MAGIC,
        version,
        len(families),
        len(groups),
        len(tables.land_entries),
        len(tables.bucket_entries),
        len(enc_bytes),
        header_size,
        off_family,
        off_groups,
        off_enc,
        off_land_entries,
        off_land_offsets,
        off_bucket_entries,
        off_bucket_offsets,
        off_flags,
        off_slots,
        off_type_count,
        len(required_routes),
        0,
        off_required,
    )
    if len(header) != header_size:
        raise RuntimeError(f"Ecology compat header size {len(header)} != {header_size}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + b"".join(blob_pieces))


def write_source(
    path: Path,
    version: int,
    families: list[Family],
    groups: list[Group],
    edges: list[Edge],
    required_routes: list[RequiredRoute],
) -> tuple[int, int]:
    tables = prepare_compat_tables(families, groups, edges)

    group_land_rows = [f"        {{ {a}, {b}, {c} }}," for a, b, c in tables.land_entries]
    group_bucket_rows = [f"        {{ {a}, {b}, {c} }}," for a, b, c in tables.bucket_entries]
    encdata_flat = [f"    {enc_id}," for enc_id in tables.encdata_ids]
    group_info_rows = [
        "    { "
        f"{enc_off}, {enc_cnt}, {land_mask}, {meth_mask}, {water} }},"
        for enc_off, enc_cnt, land_mask, meth_mask, water in tables.group_info
    ]
    group_flag_rows = [f"    {flag}," for flag in tables.group_flags]
    group_type_count_rows = [f"    {count}," for count in tables.location_type_count]
    slot_rows = [f"    {count}," for count in tables.method_slots]
    family_info_rows = [
        "    { "
        f"{base}, {dex}, {rarity}, {partner}, {land_time}, {pad} }},"
        for base, dex, rarity, partner, land_time, pad in tables.family_info
    ]
    required_route_rows = [
        f"    {{ {route.family_id}, {route.group_id} }},"
        for route in required_routes
    ]

    def fmt_offset_array(values: list[int]) -> str:
        return ", ".join(str(v) for v in values)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""#include "constants/generated/ecology_compat.h"

// Generated by scripts/build/gen_ecology_compatibility.py — do not edit.

const EcologyFamilyInfo sEcologyFamilyInfo[ECOLOGY_NUM_FAMILIES] = {{
{chr(10).join(family_info_rows)}
}};

const EcologyRequiredRoute sEcologyRequiredRoutes[ECOLOGY_NUM_REQUIRED_ROUTES] = {{
{chr(10).join(required_route_rows) if required_route_rows else "    { 0, 0 },"}
}};

const EcologyGroupInfo sEcologyGroups[ECOLOGY_NUM_GROUPS] = {{
{chr(10).join(group_info_rows)}
}};

const u8 sEcologyGroupEncdataIds[] = {{
{chr(10).join(encdata_flat) if encdata_flat else "    0,"}
}};

const EcologyGroupLandEntry sEcologyGroupLandEntries[] = {{
{chr(10).join(group_land_rows) if group_land_rows else "        { 0, 0, 0 },"}
}};

const u16 sEcologyGroupLandOffsets[ECOLOGY_NUM_GROUPS + 1] = {{
    {fmt_offset_array(tables.land_offsets)}
}};

const EcologyGroupBucketEntry sEcologyGroupBucketEntries[] = {{
{chr(10).join(group_bucket_rows) if group_bucket_rows else "        { 0, 0, 0 },"}
}};

const u16 sEcologyGroupBucketOffsets[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT + 1] = {{
    {fmt_offset_array(tables.bucket_offsets)}
}};

const u8 sEcologyGroupFlags[ECOLOGY_NUM_GROUPS] = {{
{chr(10).join(group_flag_rows)}
}};

const u8 sEcologyGroupMethodSlots[ECOLOGY_NUM_GROUPS * ECOLOGY_METHOD_COUNT] = {{
{chr(10).join(slot_rows)}
}};

const u8 sEcologyGroupLocationTypeCount[ECOLOGY_NUM_GROUPS] = {{
{chr(10).join(group_type_count_rows)}
}};
""",
        encoding="utf-8",
    )
    return tables.max_slots, tables.total_slots


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--families", type=Path, default=FAMILIES_TSV)
    parser.add_argument("--locations", type=Path, default=LOCATIONS_TSV)
    parser.add_argument("--species-header", type=Path, default=SPECIES_H)
    parser.add_argument("--encounter-header", type=Path, default=ENCOUNTER_H)
    parser.add_argument("--out-c", type=Path, default=OUT_C)
    parser.add_argument("--out-h", type=Path, default=OUT_H)
    parser.add_argument("--dump-family", type=Path, default=OUT_DUMP_FAMILY)
    parser.add_argument("--dump-group", type=Path, default=OUT_DUMP_GROUP)
    args = parser.parse_args()

    species_enums = load_species_enum(args.species_header)
    enc_enum = load_encounter_enum(args.encounter_header)
    families = load_families(args.families, species_enums)
    resolve_pairings(families)
    groups = load_groups(args.locations, enc_enum)
    required_routes = build_required_routes(families, groups)
    edges = build_edges(families, groups)
    version = compat_version([args.families, args.locations])

    tables = prepare_compat_tables(families, groups, edges)
    max_family_edge_scratch = max_family_edge_scratch_refs(families, groups, edges)
    max_slots, total_slots = write_source(
        args.out_c, version, families, groups, edges, required_routes
    )
    write_binary_blob(OUT_BIN, version, families, groups, tables, required_routes)
    write_header(
        args.out_h,
        version,
        len(families),
        len(groups),
        len(edges),
        len(required_routes),
        max_slots,
        total_slots,
        max_family_edge_scratch,
    )
    write_strings_header(OUT_STRINGS_H, len(families), len(groups))
    write_strings_source(OUT_STRINGS_C, families, groups)
    write_dumps(args.dump_family, args.dump_group, families, groups, edges)

    print(f"Ecology compat version 0x{version:08X}")
    print(f"Shuffleable families: {len(families)}")
    print(f"Placement groups: {len(groups)}")
    print(f"Compatibility edges: {len(edges)}")
    print(f"Max family edge scratch: {max_family_edge_scratch}")
    print(f"Wrote {args.out_c}")
    print(f"Wrote {OUT_BIN} ({OUT_BIN.stat().st_size} bytes)")
    print(f"Wrote {args.out_h}")
    print(f"Wrote dumps {args.dump_family} and {args.dump_group}")
    print(f"Wrote {OUT_STRINGS_C} and {OUT_STRINGS_H}")
    print(f"Slot capacity: max per bucket={max_slots}, total={total_slots}")


if __name__ == "__main__":
    main()
