#!/usr/bin/env python3
"""Encode HGSS zone_event JSON into the binary map-events format."""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPRITES = {
    "SPRITE_COUNTERM": 394,
    "SPRITE_GSBOY1": 146,
}

FLAGS = {
    "FLAG_NOTHING": 0,
}

VARS = {
    "VAR_TEMP_x400F": 0x400F,
}

MAP_ALIASES = {
    "MAP_ROUTE_29": "MAP_R29",
    "MAP_ROUTE_46": "MAP_R46",
}


def load_defines(path: Path) -> dict[str, int]:
    defines: dict[str, int] = {}
    if not path.is_file():
        return defines
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"#define\s+(\w+)\s+(\d+)", line.strip())
        if match:
            defines[match.group(1)] = int(match.group(2))
    return defines


def load_maps() -> dict[str, int]:
    maps = load_defines(ROOT / "include" / "constants" / "maps.h")
    for alias, target in MAP_ALIASES.items():
        if target in maps:
            maps[alias] = maps[target]
    return maps


def parse_script_expr(value: str, event_defs: dict[str, int]) -> int:
    match = re.fullmatch(r"(_EV_\w+)\s*\+\s*(\d+)", value.strip())
    if match:
        base = event_defs.get(match.group(1))
        if base is None:
            raise ValueError(f"unknown script symbol: {match.group(1)}")
        return base + int(match.group(2))
    if value in event_defs:
        return event_defs[value]
    raise ValueError(f"unsupported scriptId expression: {value}")


def resolve_value(value, *, maps: dict[str, int], event_defs: dict[str, int]) -> int:
    if isinstance(value, bool):
        raise TypeError("boolean values are not supported")
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise TypeError(f"unsupported value type: {type(value)!r}")

    if value in maps:
        return maps[value]
    if value in SPRITES:
        return SPRITES[value]
    if value in FLAGS:
        return FLAGS[value]
    if value in VARS:
        return VARS[value]
    if value in event_defs:
        return event_defs[value]
    if value.startswith("_EV_"):
        return parse_script_expr(value, event_defs)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    raise ValueError(f"unable to resolve constant: {value}")


def encode_zone_event(data: dict) -> bytes:
    maps = load_maps()
    header_path = ROOT / data["header"]
    event_defs = load_defines(header_path)

    out = bytearray()

    bgs = data.get("bgs", [])
    out.extend(struct.pack("<I", len(bgs)))
    for bg in bgs:
        out.extend(
            struct.pack(
                "<HHIIII",
                resolve_value(bg["scriptId"], maps=maps, event_defs=event_defs),
                resolve_value(bg["type"], maps=maps, event_defs=event_defs),
                resolve_value(bg["x"], maps=maps, event_defs=event_defs),
                resolve_value(bg["z"], maps=maps, event_defs=event_defs),
                resolve_value(bg["y"], maps=maps, event_defs=event_defs),
                resolve_value(bg["dir"], maps=maps, event_defs=event_defs),
            )
        )

    objects = data.get("objects", [])
    out.extend(struct.pack("<I", len(objects)))
    for obj in objects:
        out.extend(
            struct.pack(
                "<14HI",
                resolve_value(obj["id"], maps=maps, event_defs=event_defs),
                resolve_value(obj["spriteId"], maps=maps, event_defs=event_defs),
                resolve_value(obj["movement"], maps=maps, event_defs=event_defs),
                resolve_value(obj["type"], maps=maps, event_defs=event_defs),
                resolve_value(obj["eventFlag"], maps=maps, event_defs=event_defs),
                resolve_value(obj["scriptId"], maps=maps, event_defs=event_defs),
                resolve_value(obj["facingDirection"], maps=maps, event_defs=event_defs),
                resolve_value(obj["param0"], maps=maps, event_defs=event_defs),
                resolve_value(obj["param1"], maps=maps, event_defs=event_defs),
                resolve_value(obj["param2"], maps=maps, event_defs=event_defs),
                resolve_value(obj["xRange"], maps=maps, event_defs=event_defs),
                resolve_value(obj["yRange"], maps=maps, event_defs=event_defs),
                resolve_value(obj["x"], maps=maps, event_defs=event_defs),
                resolve_value(obj["z"], maps=maps, event_defs=event_defs),
                resolve_value(obj["y"], maps=maps, event_defs=event_defs),
            )
        )

    warps = data.get("warps", [])
    out.extend(struct.pack("<I", len(warps)))
    for warp in warps:
        out.extend(
            struct.pack(
                "<HHHHI",
                resolve_value(warp["x"], maps=maps, event_defs=event_defs),
                resolve_value(warp["z"], maps=maps, event_defs=event_defs),
                resolve_value(warp["header"], maps=maps, event_defs=event_defs),
                resolve_value(warp["anchor"], maps=maps, event_defs=event_defs),
                resolve_value(warp["y"], maps=maps, event_defs=event_defs),
            )
        )

    coords = data.get("coords", [])
    out.extend(struct.pack("<I", len(coords)))
    for coord in coords:
        out.extend(
            struct.pack(
                "<8H",
                resolve_value(coord["scriptId"], maps=maps, event_defs=event_defs),
                resolve_value(coord["x"], maps=maps, event_defs=event_defs),
                resolve_value(coord["z"], maps=maps, event_defs=event_defs),
                resolve_value(coord["w"], maps=maps, event_defs=event_defs),
                resolve_value(coord["h"], maps=maps, event_defs=event_defs),
                resolve_value(coord["y"], maps=maps, event_defs=event_defs),
                resolve_value(coord.get("val", 0), maps=maps, event_defs=event_defs),
                resolve_value(coord.get("var", 0), maps=maps, event_defs=event_defs),
            )
        )

    return bytes(out)


def narc_member_path(output_dir: Path, json_path: Path) -> Path:
    index = json_path.name.split("_", 1)[0]
    return output_dir / f"2_{index}"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <zone_event.json> <output_dir>", file=sys.stderr)
        return 1

    json_path = Path(argv[1])
    output_dir = Path(argv[2])
    data = json.loads(json_path.read_text(encoding="utf-8"))
    encoded = encode_zone_event(data)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = narc_member_path(output_dir, json_path)
    out_path.write_bytes(encoded)
    print(f"wrote {out_path} ({len(encoded)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
