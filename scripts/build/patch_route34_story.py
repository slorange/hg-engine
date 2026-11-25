"""Skip the Day Care introduction and change the Route 34 sisters' reward."""

import struct
import sys
from pathlib import Path

from scripts.build.patch_route30_story import replace_entry
from tools.append_scr_seq_script import script_offset
from tools.patch_zone_event_r32_badge import object_fields, pack_bg, parse_zone_event


def patch_events(path: Path, actor_ids: set[int]) -> None:
    bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
    actors = [obj for obj in objects if object_fields(obj)[0] in actor_ids]
    if {object_fields(obj)[0] for obj in actors if object_fields(obj)[4] == 557} != actor_ids:
        raise ValueError(f"{path}: expected the Day Care cutscene actors")
    objects = [obj for obj in objects if obj not in actors]
    if path.name == "2_035":
        kept = [coord for coord in coords if (coord[0], coord[7]) != (4, 0x408E)]
        if len(kept) != len(coords) - 1:
            raise ValueError(f"{path}: expected one Day Care introduction trigger")
        coords = kept
    path.write_bytes(
        struct.pack("<I", len(bgs)) + b"".join(map(pack_bg, bgs))
        + struct.pack("<I", len(objects)) + b"".join(objects)
        + struct.pack("<I", len(warps) // 12) + warps
        + struct.pack("<I", len(coords)) + b"".join(struct.pack("<8H", *coord) for coord in coords)
    )


def main() -> None:
    mode, directory = sys.argv[1:]
    directory = Path(directory)
    if mode == "events":
        patch_events(directory / "2_035", {11, 12})
        patch_events(directory / "2_302", {1, 2})
    elif mode == "scripts":
        route = directory / "2_237"
        daycare = directory / "2_238"
        finish = struct.pack("<4H", 41, 0x408E, 3, 2)
        # Stop both automatic follow-up scenes, including saves between scenes.
        route.write_bytes(replace_entry(route, 1, "61 02 60 00 5e 00 0a 00", finish))
        daycare.write_bytes(replace_entry(daycare, 1, "61 02 60 00 5a 02 00 00", finish))
        route_data = bytearray(replace_entry(route, 3, "61 02 60 00 84 00 24 29", finish))
        # Kate's victory dialogue is followed by SetVar VAR_8004, ITEM_POWER_HERB.
        reward = struct.pack("<HB3H", 45, 30, 41, 0x8004, 271)
        offset = route_data.index(reward, script_offset(route_data, 5))
        struct.pack_into("<H", route_data, offset + len(reward) - 2, 644)  # ITEM_PIXIE_PLATE
        route.write_bytes(route_data)
    else:
        raise ValueError(f"Unknown Route 34 patch mode: {mode}")


if __name__ == "__main__":
    main()
