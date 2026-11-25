"""Start the Ilex Forest Kimono Girl scene by talking to her."""

import struct
import sys
from pathlib import Path

from tools.append_scr_seq_script import script_offset
from tools.patch_zone_event_r32_badge import object_fields, pack_bg, parse_zone_event


def patch_events(path: Path) -> None:
    bgs, objects, warps, coords = parse_zone_event(path.read_bytes())
    girl = next(i for i, obj in enumerate(objects) if object_fields(obj)[0] == 12)
    actor = bytearray(objects[girl])
    if object_fields(actor)[4:6] != [573, 0]:
        raise ValueError(f"{path}: unexpected Ilex Kimono Girl object")
    struct.pack_into("<H", actor, 10, 16)
    objects[girl] = actor
    kept = [coord for coord in coords if coord != [16, 40, 20, 2, 1, 0, 0, 0x40E9]]
    if len(kept) != len(coords) - 1:
        raise ValueError(f"{path}: expected one Ilex Kimono Girl coordinate trigger")
    path.write_bytes(
        struct.pack("<I", len(bgs)) + b"".join(map(pack_bg, bgs))
        + struct.pack("<I", len(objects)) + b"".join(objects)
        + struct.pack("<I", len(warps) // 12) + warps
        + struct.pack("<I", len(kept)) + b"".join(struct.pack("<8H", *coord) for coord in kept)
    )


def patch_script(path: Path, scene: Path, tutor_gate: Path) -> None:
    data = bytearray(path.read_bytes())
    slot = 15
    start = script_offset(data, slot)
    if data[start:start + 8] != bytes.fromhex("61 02 60 00 14 00 13 08"):
        raise ValueError(f"{path}: unexpected original Ilex Kimono Girl script")
    if len(data) % 2:
        data.append(0)
    struct.pack_into("<i", data, slot * 4, len(data) - (slot + 1) * 4)
    data.extend(scene.read_bytes())

    tutor_slot = 2
    original_tutor = script_offset(data, tutor_slot)
    gate = tutor_gate.read_bytes()
    original_intro = bytes.fromhex("49 00 dc 05 60 00 68 00")
    if data[original_tutor:original_tutor + 11] != original_intro + bytes.fromhex("2d 00 0b"):
        raise ValueError(f"{path}: unexpected original Ilex Headbutt tutor script")
    jump = gate.index(struct.pack("<Hi", 22, -6))
    if len(data) % 2:
        data.append(0)
    struct.pack_into("<i", data, tutor_slot * 4, len(data) - (tutor_slot + 1) * 4)
    jump += len(data)
    data.extend(gate)
    struct.pack_into("<i", data, jump + 2, original_tutor + len(original_intro) - (jump + 6))
    path.write_bytes(data)


if __name__ == "__main__":
    mode, target, *args = sys.argv[1:]
    if mode == "events":
        patch_events(Path(target))
    elif mode == "scripts":
        patch_script(Path(target), *map(Path, args))
    else:
        raise ValueError(f"Unknown Ilex Kimono Girl patch mode: {mode}")
