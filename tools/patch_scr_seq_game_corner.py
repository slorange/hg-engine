#!/usr/bin/env python3
"""Retarget Game Corner TM and held-item prize menus (Goldenrod + Celadon).

Goldenrod scr_seq member 910 (T25SP0101):
  TMs: TM05, TM44, TM46, TM75, TM90, TM92
  Items: Bright Powder, Quick Claw, Wide Lens, Metronome

Celadon scr_seq member 804 (T07R0501 dept 5F):
  TMs: TM10, TM32, TM49, TM58, TM67, TM82
  Items: Focus Band, Zoom Lens, Scope Lens, Luck Incense

Each changed prize is patched at fixed offsets from vanilla HeartGold scr_seq extract.
All TM, held-item, and Pokémon prize costs are flattened to PRIZE_COIN_COST (temporary).

See documentation/HACK-NOTES.md § Game Corner TM prizes.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Temporary playtest shortcut until coin income + real pricing ship.
PRIZE_COIN_COST = 50

# offset, expected_item_id, new_item_id
ItemPatch = tuple[int, int, int]

# offset, expected_vanilla_cost, new_cost
CostPatch = tuple[int, int, int]


def tm_item(tm: int) -> int:
    return 328 + tm - 1


GOLDENROD_MEMBER = 910
GOLDENROD_PATCHES: list[ItemPatch] = [
    # TMs (two offsets each: purchase + not-enough-coins nav)
    (838, tm_item(90), tm_item(5)),
    (2894, tm_item(90), tm_item(5)),
    (1255, tm_item(35), tm_item(46)),
    (2969, tm_item(35), tm_item(46)),
    (1394, tm_item(13), tm_item(90)),
    (2994, tm_item(13), tm_item(90)),
    (1533, tm_item(24), tm_item(92)),
    (3019, tm_item(24), tm_item(92)),
    # Held items (one offset each in vanilla)
    (1672, 251, 213),  # Silk Scarf -> Bright Powder
    (1811, 265, 217),  # Wide Lens -> Quick Claw
    (1950, 276, 265),  # Zoom Lens -> Wide Lens
]

CELADON_MEMBER = 804
CELADON_PATCHES: list[ItemPatch] = [
    (1075, tm_item(29), tm_item(49)),
    (2532, tm_item(29), tm_item(49)),
    (1214, tm_item(74), tm_item(67)),
    (2557, tm_item(74), tm_item(67)),
    (1353, tm_item(68), tm_item(82)),
    (2582, tm_item(68), tm_item(82)),
    (1492, 251, 230),  # Silk Scarf -> Focus Band
    (1631, 265, 276),  # Wide Lens -> Zoom Lens
    (1770, 276, 232),  # Zoom Lens -> Scope Lens
    (1909, 277, 319),  # Metronome -> Luck Incense
]

# Compare VAR_SPECIAL_x8006 + TakeCoins pairs per prize block (vanilla costs).
GOLDENROD_COST_PATCHES: list[CostPatch] = [
    (915, 2000, PRIZE_COIN_COST),
    (933, 2000, PRIZE_COIN_COST),
    (1054, 4000, PRIZE_COIN_COST),
    (1072, 4000, PRIZE_COIN_COST),
    (1193, 6000, PRIZE_COIN_COST),
    (1211, 6000, PRIZE_COIN_COST),
    (1332, 10000, PRIZE_COIN_COST),
    (1350, 10000, PRIZE_COIN_COST),
    (1471, 10000, PRIZE_COIN_COST),
    (1489, 10000, PRIZE_COIN_COST),
    (1610, 10000, PRIZE_COIN_COST),
    (1628, 10000, PRIZE_COIN_COST),
    (1749, 1000, PRIZE_COIN_COST),
    (1767, 1000, PRIZE_COIN_COST),
    (1888, 1000, PRIZE_COIN_COST),
    (1906, 1000, PRIZE_COIN_COST),
    (2027, 1000, PRIZE_COIN_COST),
    (2045, 1000, PRIZE_COIN_COST),
    (2166, 1000, PRIZE_COIN_COST),
    (2184, 1000, PRIZE_COIN_COST),
    (2633, 200, PRIZE_COIN_COST),
    (2787, 200, PRIZE_COIN_COST),
    (2669, 700, PRIZE_COIN_COST),
    (2705, 700, PRIZE_COIN_COST),
    (2810, 700, PRIZE_COIN_COST),
    (2833, 700, PRIZE_COIN_COST),
    (2728, 2100, PRIZE_COIN_COST),
    (2843, 2100, PRIZE_COIN_COST),
]

CELADON_COST_PATCHES: list[CostPatch] = [
    (735, 2000, PRIZE_COIN_COST),
    (753, 2000, PRIZE_COIN_COST),
    (874, 4000, PRIZE_COIN_COST),
    (892, 4000, PRIZE_COIN_COST),
    (1013, 6000, PRIZE_COIN_COST),
    (1031, 6000, PRIZE_COIN_COST),
    (1152, 10000, PRIZE_COIN_COST),
    (1170, 10000, PRIZE_COIN_COST),
    (1291, 10000, PRIZE_COIN_COST),
    (1309, 10000, PRIZE_COIN_COST),
    (1430, 15000, PRIZE_COIN_COST),
    (1448, 15000, PRIZE_COIN_COST),
    (1569, 1000, PRIZE_COIN_COST),
    (1587, 1000, PRIZE_COIN_COST),
    (1708, 1000, PRIZE_COIN_COST),
    (1726, 1000, PRIZE_COIN_COST),
    (1847, 1000, PRIZE_COIN_COST),
    (1865, 1000, PRIZE_COIN_COST),
    (1986, 1000, PRIZE_COIN_COST),
    (2004, 1000, PRIZE_COIN_COST),
    (2209, 3333, PRIZE_COIN_COST),
    (2284, 3333, PRIZE_COIN_COST),
    (2402, 3333, PRIZE_COIN_COST),
    (2320, 6666, PRIZE_COIN_COST),
    (2425, 6666, PRIZE_COIN_COST),
    (2343, 9999, PRIZE_COIN_COST),
    (2435, 9999, PRIZE_COIN_COST),
]

MEMBERS: dict[int, list[ItemPatch]] = {
    GOLDENROD_MEMBER: GOLDENROD_PATCHES,
    CELADON_MEMBER: CELADON_PATCHES,
}

COST_MEMBERS: dict[int, list[CostPatch]] = {
    GOLDENROD_MEMBER: GOLDENROD_COST_PATCHES,
    CELADON_MEMBER: CELADON_COST_PATCHES,
}


def read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def write_u16(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<H", data, offset, value)


def apply_patches(data: bytearray, patches: list[ItemPatch]) -> None:
    for offset, expected, new in patches:
        actual = read_u16(data, offset)
        if actual != expected:
            raise ValueError(
                f"offset {offset}: expected item {expected}, got {actual} "
                "(wrong ROM or scr_seq revision?)"
            )
        write_u16(data, offset, new)


def apply_cost_patches(data: bytearray, patches: list[CostPatch]) -> None:
    for offset, expected, new in patches:
        actual = read_u16(data, offset)
        if actual != expected:
            raise ValueError(
                f"offset {offset}: expected cost {expected}, got {actual} "
                "(wrong ROM or scr_seq revision?)"
            )
        write_u16(data, offset, new)


def validate_patches(data: bytes, patches: list[ItemPatch], label: str) -> None:
    for offset, _expected, new in patches:
        actual = read_u16(data, offset)
        if actual != new:
            raise ValueError(
                f"{label}: offset {offset} expected item {new}, got {actual}"
            )


def validate_cost_patches(data: bytes, patches: list[CostPatch], label: str) -> None:
    for offset, _expected, new in patches:
        actual = read_u16(data, offset)
        if actual != new:
            raise ValueError(
                f"{label}: offset {offset} expected cost {new}, got {actual}"
            )


def patch_file(path: Path, member: int) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)

    patches = MEMBERS[member]
    cost_patches = COST_MEMBERS[member]
    vanilla_size = path.stat().st_size
    data = bytearray(path.read_bytes())

    apply_patches(data, patches)
    apply_cost_patches(data, cost_patches)
    validate_patches(bytes(data), patches, f"2_{member}")
    validate_cost_patches(bytes(data), cost_patches, f"2_{member}")

    if len(data) != vanilla_size:
        raise ValueError(f"2_{member} size changed {vanilla_size} -> {len(data)}")

    path.write_bytes(data)
    writes = len(patches) + len(cost_patches)
    print(
        f"patched Game Corner prizes in {path} ({len(data)} bytes, "
        f"{writes} offset writes)"
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} <build/a012/2_910> [<build/a012/2_804> ...]", file=sys.stderr)
        return 1

    for arg in argv[1:]:
        path = Path(arg)
        try:
            member = int(path.name.split("_", 1)[1])
        except (IndexError, ValueError) as exc:
            raise ValueError(f"unexpected scr_seq path {path}") from exc
        if member not in MEMBERS:
            raise ValueError(f"unsupported scr_seq member {member} in {path}")
        patch_file(path, member)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
