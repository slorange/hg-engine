"""Replace Union Cave's Lapras with a one-time visible Splash Plate pickup."""

import struct
import sys
from pathlib import Path

from tools.patch_zone_event_r32_badge import object_fields, pack_bg, pack_object, parse_zone_event


def patch_events(path: Path) -> None:
    bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
    for index, obj in enumerate(objects):
        fields = object_fields(obj)
        if (fields[0], fields[1], fields[4], fields[5]) == (3, 390, 778, 1):
            # Copy the floor's standard item-ball settings and retain Lapras's position.
            ball = next(object_fields(entry) for entry in objects if object_fields(entry)[5] == 7039)
            ball[0], ball[4] = fields[0], 1359
            ball[12:14] = fields[12:14]
            objects[index] = pack_object(ball, struct.unpack_from("<I", obj, 28)[0])
            break
    else:
        raise ValueError(f"{path}: expected the Union Cave Lapras object")

    path.write_bytes(
        struct.pack("<I", len(bgs)) + b"".join(map(pack_bg, bgs))
        + struct.pack("<I", len(objects)) + b"".join(objects)
        + struct.pack("<I", len(warps) // 12) + warps
        + struct.pack("<I", len(coords)) + b"".join(struct.pack("<8H", *c) for c in coords)
    )


def main() -> None:
    mode, target = sys.argv[1:]
    path = Path(target)
    if mode == "events":
        patch_events(path)
    elif mode == "header":
        if path.read_bytes() != bytes.fromhex("02 03 00 00 00 04 02 00 00 00 00 00"):
            raise ValueError(f"{path}: unexpected Union Cave Lapras map script header")
        path.write_bytes(bytes(4))
    else:
        raise ValueError(f"Unknown Union Cave patch mode: {mode}")


if __name__ == "__main__":
    main()
