#!/usr/bin/env python3
"""Report visible and hidden field pickups from a built Wandering Heart ROM."""

from __future__ import annotations

import argparse
import csv
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

from ndspy.narc import NARC
from ndspy.rom import NintendoDSRom

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from append_scr_seq_script import script_offset
from zone_event_enc import load_defines

# US HeartGold map headers. The fork keeps the table at the original address.
MAP_HEADERS = 0x020F6BE0
MAP_HEADER_SIZE = 24
ITEM_BALL_SPRITE = 87
ITEM_BALL_SCRIPT_BASE = 7000
HIDDEN_SCRIPT_BASE = 8000


def names_from_bank(data: bytes, characters: dict[int, str]) -> list[str]:
    """Decode plain name strings using the same keys as tools/msgenc."""
    count, seed = struct.unpack_from("<HH", data)
    names = []
    for index in range(1, count + 1):
        key = (765 * index * seed) & 0xFFFF
        key |= key << 16
        offset, length = struct.unpack_from("<II", data, 4 + 8 * (index - 1))
        offset ^= key
        length ^= key
        name = []
        for position, (code,) in enumerate(struct.iter_unpack("<H", data[offset:offset + 2 * length])):
            code ^= (index * 596947 + position * 18749) & 0xFFFF
            if code == 0xFFFF:
                break
            name.append(characters.get(code, "�"))
        names.append("".join(name))
    return names


def item_ball_reward(bank: bytes, slot: int, *, local: bool) -> tuple[int, int]:
    start = script_offset(bank, slot)
    # The scripted pickups may set a selector in VAR_4001 before the reward.
    if local and struct.unpack_from("<HH", bank, start) == (41, 0x4001):
        start += 6
    set_item, item_var, item, set_quantity, quantity_var, quantity, jump = struct.unpack_from(
        "<7H", bank, start
    )
    if (set_item, item_var, set_quantity, quantity_var, jump) != (41, 0x8008, 41, 0x8009, 22):
        raise ValueError(f"unrecognized item ball reward in script slot {slot}")
    return item, quantity


def report_rows(rom_path: Path) -> list[dict]:
    rom = NintendoDSRom.fromFile(rom_path)
    events = NARC(rom.getFileByName("a/0/3/2")).files
    scripts = NARC(rom.getFileByName("a/0/1/2")).files
    addons = NARC(rom.getFileByName("a/0/2/8")).files
    messages = NARC(rom.getFileByName("a/0/2/7")).files
    characters = {
        int(code, 16): character
        for code, character in re.findall(
            r"^([0-9A-Fa-f]{4})=(.*)$", (ROOT / "charmap.txt").read_text(encoding="utf-8"), re.M
        )
    }
    map_names = names_from_bank(messages[279], characters)
    item_names = names_from_bank(messages[222], characters)
    item_symbols = {
        value: name.removeprefix("ITEM_")
        for name, value in load_defines(ROOT / "include/constants/item.h").items()
        if name.startswith("ITEM_")
    }
    hidden = {
        index: (item, quantity)
        for item, quantity, _, _, index in struct.iter_unpack("<HBBHH", addons[18])
    }
    map_defines = load_defines(ROOT / "include/constants/maps.h")
    maps = defaultdict(list)
    for symbol, map_id in map_defines.items():
        if not 0 <= map_id < map_defines["MAP_ID_MAX"]:
            continue
        start = MAP_HEADERS - rom.arm9RamAddress + MAP_HEADER_SIZE * map_id
        script_bank, = struct.unpack_from("<H", rom.arm9, start + 6)
        event_bank, map_section = struct.unpack_from("<HB", rom.arm9, start + 16)
        maps[event_bank].append((symbol.removeprefix("MAP_"), script_bank, map_section))
    if maps[30][0][0] != "R29" or maps[43][0][0] != "R44":
        raise ValueError("ROM does not have the expected Wandering Heart map header layout")

    pickups = defaultdict(dict)
    for bank, data in enumerate(events):
        bg_count, = struct.unpack_from("<I", data)
        for offset in range(4, 4 + 20 * bg_count, 20):
            script, event_type, x, z = struct.unpack_from("<HHii", data, offset)
            if event_type != 2:
                continue
            index = script - HIDDEN_SCRIPT_BASE
            item, quantity = hidden[index]
            for code, _, section in maps.get(bank) or [(f"Event bank {bank}", 0, 0)]:
                location = f"{map_names[section]} [{code}] ({x}, {z})"
                pickups[item].setdefault(("Hidden", index), {})[location] = quantity

        start = 4 + 20 * bg_count
        object_count, = struct.unpack_from("<I", data, start)
        for offset in range(start + 4, start + 4 + 32 * object_count, 32):
            object_id, sprite, _, _, flag, script = struct.unpack_from("<6H", data, offset)
            x, z = struct.unpack_from("<HH", data, offset + 24)
            standard = ITEM_BALL_SCRIPT_BASE <= script < HIDDEN_SCRIPT_BASE
            if not standard and (sprite != ITEM_BALL_SPRITE or script == 0):
                continue
            if bank not in maps:
                raise ValueError(f"item ball at ({x}, {z}) has no map for event bank {bank}")
            for code, script_bank, section in maps[bank]:
                try:
                    if standard:
                        item, quantity = item_ball_reward(
                            scripts[141], script - ITEM_BALL_SCRIPT_BASE, local=False
                        )
                    else:
                        item, quantity = item_ball_reward(scripts[script_bank], script - 1, local=True)
                except (struct.error, ValueError) as error:
                    raise ValueError(f"{code} ({x}, {z}), script {script}: {error}") from error
                location = f"{map_names[section]} [{code}] ({x}, {z})"
                reward_key = flag if flag else (bank, object_id)
                pickups[item].setdefault(("Ground", reward_key), {})[location] = quantity

    rows = []
    for item, rewards in pickups.items():
        symbol = item_symbols.get(item, f"ID {item}")
        name = item_names[item] if item < len(item_names) else ""
        locations = []
        total = 0
        for (kind, _), spots in rewards.items():
            quantities = set(spots.values())
            if len(quantities) != 1:
                raise ValueError(f"shared {symbol} pickup has differing quantities: {spots}")
            quantity = quantities.pop()
            total += quantity
            if len(rewards) < 5:
                places = " or ".join(sorted(spots))
                locations.append(f"{kind}: {places}" + (f" ×{quantity}" if quantity != 1 else ""))
        rows.append({
            "Item": name if name and "�" not in name else symbol.replace("_", " ").title(),
            "Item ID": item,
            "Pickups": len(rewards),
            "Ground": sum(kind == "Ground" for kind, _ in rewards),
            "Hidden": sum(kind == "Hidden" for kind, _ in rewards),
            "Total quantity": total,
            "Locations (under 5 pickups)": " | ".join(sorted(locations)),
        })
    return sorted(rows, key=lambda row: (row["Pickups"], row["Item"].casefold(), row["Item ID"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, nargs="?", default=ROOT / "test.nds")
    parser.add_argument("-o", "--output", type=Path, help="write CSV to this file instead of stdout")
    args = parser.parse_args()
    rows = report_rows(args.rom)
    if not rows:
        parser.error("no field pickups found")
    if args.output is None:
        write_csv(sys.stdout, rows)
        return
    with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
        write_csv(stream, rows)


def write_csv(stream, rows: list[dict]) -> None:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()
