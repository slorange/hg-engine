"""Route pending Egg scenes to the Kimono Girl and change Sprout Tower's reward."""

import struct
import sys
from pathlib import Path

from tools.append_scr_seq_script import script_offset


def main() -> None:
    city_path, header_path, tower_path = map(Path, sys.argv[1:])
    city = bytearray(city_path.read_bytes())
    header = header_path.read_bytes()
    tower = bytearray(tower_path.read_bytes())

    phone_call = script_offset(city, 0)
    if city[phone_call:phone_call + 4] != bytes.fromhex("1e 00 9f 00"):
        raise ValueError("Unexpected opening commands in Violet City's Egg call")
    # Move pending saves from the phone call or Mart handoff to the Kimono Girl.
    skip_egg = struct.pack("<2H", 30, 407)  # Hide the Mart aide.
    # If hidden, clear the dancer's flag and show her on the current map.
    skip_egg += struct.pack("<HHHBi4H", 32, 568, 28, 0, 8, 31, 568, 100, 7)
    skip_egg += struct.pack("<4H", 41, 0x4074, 3, 2)
    city[phone_call:phone_call + len(skip_egg)] = skip_egg

    # Approach the Gym at x=479, then leave down the street past the Mart.
    kimono_scene = script_offset(city, 4)
    approach = city.index(bytes.fromhex("4b 00 01 00 0e 00 05 00 0c 00 01 00 fe 00 00 00"), kimono_scene)
    departure = city.index(bytes.fromhex("0d 00 02 00 0e 00 01 00 0d 00 07 00 fe 00 00 00"), approach)
    struct.pack_into("<H", city, approach + 4, 15)  # WalkNormalEast 5
    struct.pack_into("<8H", city, departure, 13, 1, 14, 11, 13, 8, 0xFE, 0)

    state_one = struct.pack("<3H", 0x4074, 1, 1)
    state_three = struct.pack("<3H", 0x4074, 3, 5)
    if header[6:] != state_one + state_three + b"\0\0":
        raise ValueError("Unexpected Violet City frame script table")
    state_two = struct.pack("<3H", 0x4074, 2, 1)

    # Call both grants before resuming the original completion flags and dialogue.
    reward = struct.pack("<8H", 41, 0x8004, 397, 41, 0x8005, 1, 20, 2033)
    offset = tower.index(reward, script_offset(tower, 2))
    call = struct.pack("<Hi", 26, len(tower) - (offset + 6))
    tower[offset:offset + len(reward)] = call.ljust(len(reward), b"\0")
    for item, quantity in ((50, 5), (78, 1)):  # Rare Candy, Escape Rope
        tower.extend(struct.pack("<8H", 41, 0x8004, item, 41, 0x8005, quantity, 20, 2033))
    tower.extend(struct.pack("<H", 27))  # Return

    city_path.write_bytes(city)
    header_path.write_bytes(header[:12] + state_two + header[12:])
    tower_path.write_bytes(tower)
    print("Skipped Violet's Egg quest and changed Sprout Tower's reward")


if __name__ == "__main__":
    main()
