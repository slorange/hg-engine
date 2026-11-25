"""Skip Goldenrod's linear story and update its everyday services."""

import struct
import sys
from pathlib import Path

from tools.append_scr_seq_script import script_offset


def write_at(data: bytearray, offset: int, expected: bytes, replacement: bytes) -> None:
    if not data[offset:].startswith(expected):
        raise ValueError(f"Unexpected Goldenrod script commands at {offset:#x}")
    data[offset:offset + len(replacement)] = replacement


def set_var(var: int, value: int) -> bytes:
    return struct.pack("<3H", 41, var, value)


def dialogue(message: int) -> bytes:
    return bytes.fromhex("49 00 dc 05 60 00 68 00 2d 00") + bytes((message,)) + bytes.fromhex(
        "32 00 35 00 61 00 02 00"
    )


def keep_post_takeover_state(data: bytearray, slot: int, prefix: str) -> None:
    start = script_offset(data, slot)
    original = bytes.fromhex(prefix)
    call = struct.pack("<Hi", 26, len(data) - (start + 6))
    write_at(data, start, original, call.ljust(len(original), b"\0"))
    # Restore the state before the vanilla initializer selects NPC visibility.
    data.extend(set_var(0x4077, 5))
    data.extend(struct.pack("<2H", 31, 2459))  # Clear active takeover.
    for flag in (198, 439, 440, 441, 442, 443, 444, 445, 792, 447, 144):
        data.extend(struct.pack("<2H", 30, flag))
    data.extend(original + struct.pack("<H", 27))


def main() -> None:
    directory = Path(sys.argv[1])
    maps = {
        member: bytearray((directory / f"2_{member:03}").read_bytes())
        for member in (29, 93, 94, 96, 885, 890, 896, 905)
    }

    for member, slot, prefix in (
        (885, 18, "1e 00 b9 01 1e 00 ba 01"),
        (29, 8, "1e 00 bc 01 1e 00 b8 01"),
        (94, 8, "1e 00 b0 01 1e 00 b1 01"),
        (96, 6, "1e 00 b7 01 11 00 77 40 04 00"),
    ):
        keep_post_takeover_state(maps[member], slot, prefix)

    end = struct.pack("<H", 2)
    for member, slot, prefix in (
        (885, 17, "61 02 60 00 5e 00 0f 00"),  # City Rocket ambush
        (29, 9, "61 02 60 00 53 01 05 00"),  # Silver exposes the disguise
        (94, 4, "61 02 60 00 5e 00 08 00"),  # Underground Rocket scene
    ):
        write_at(maps[member], script_offset(maps[member], slot), bytes.fromhex(prefix), end)
    write_at(maps[96], script_offset(maps[96], 4), bytes.fromhex("61 02 60 00 14 00 ef 07"),
             set_var(0x40A0, 1) + end)

    # The quiz can still grant the card on older saves, without moving Whitney.
    tower = maps[29]
    quiz_reward = bytes.fromhex("91 00 02 1e 00 8a 00")
    after_grant = tower.index(quiz_reward, script_offset(tower, 2)) + len(quiz_reward)
    write_at(tower, after_grant, bytes.fromhex("5a 02 00 00 5b 02"),
             struct.pack("<4H", 30, 792, 97, 2))

    # Older saves that missed Mom's grant get the Fashion Case silently on entry.
    tunnel = maps[93]
    fashion_case = struct.pack("<8HBi", 128, 435, 1, 0x800C, 17, 0x800C, 0, 28, 5, 8)
    fashion_case += struct.pack("<4H", 125, 435, 1, 0x800C)
    # Hide Lyra/Ethan and Marill only if their shared spawn flag is clear.
    fashion_case += struct.pack("<HHHBi6H", 32, 712, 28, 1, 12, 101, 2, 101, 3, 30, 712)
    tunnel_scene = script_offset(tunnel, 2)
    write_at(tunnel, tunnel_scene, bytes.fromhex("61 02 60 00 69 00 00 40"),
             struct.pack("<Hi", 22, len(tunnel) - (tunnel_scene + 6)))
    tunnel.extend(fashion_case + set_var(0x40F8, 1) + end)

    shops = maps[94]
    init = script_offset(shops, 8)
    # The first two flag commands live in the initializer's appended copy.
    herb_visibility = shops.rindex(struct.pack("<2H", 30, 433))
    struct.pack_into("<H", shops, herb_visibility, 31)
    monday_call = shops.index(struct.pack("<3H", 17, 0x4000, 1) + bytes.fromhex("1d 00 01"), init) + 6
    relative, = struct.unpack_from("<i", shops, monday_call + 3)
    monday_original = monday_call + 7 + relative
    monday_barber = len(shops)
    struct.pack_into("<i", shops, monday_call + 3, monday_barber - (monday_call + 7))
    # Open the older brother's counter on Mondays, then run the bargain shop's
    # existing hours check. The normal rotation stays in place on other days.
    shops.extend(struct.pack("<2HHi", 31, 434, 22, monday_original - (monday_barber + 10)))

    bike = maps[890]
    write_at(bike, script_offset(bike, 0), bytes.fromhex("49 00 dc 05 60 00 68 00 20 00 89 00"),
             dialogue(0))
    flower = maps[896]
    # Keep the pre-existing accessory-shop branch and Shaymin event.
    flower_tip = script_offset(flower, 0) + 11
    write_at(flower, flower_tip, bytes.fromhex("26 01 02 00 00 40"), dialogue(0))

    elevator = maps[905]
    # Choice 5 routes to the warehouse (map 200); choice 6 is the 6F atrium.
    basement_choice = struct.pack("<4H", 751, 122, 255, 5)
    choice = elevator.index(basement_choice, script_offset(elevator, 0))
    write_at(elevator, choice, basement_choice, bytes(len(basement_choice)))

    for member, data in maps.items():
        (directory / f"2_{member:03}").write_bytes(data)
    print("Patched Goldenrod story scenes, daily shops, and elevator choices")


if __name__ == "__main__":
    main()
