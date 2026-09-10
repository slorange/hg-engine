#!/usr/bin/env python3
"""Parse HGSS map headers (pret layout) for Route 44 area."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HDR = ROOT / "base/root/a/0/4/1"


def read_header(index: int) -> dict[str, int]:
    off = index * 24
    b = HDR.read_bytes()[off : off + 24]
    return {
        "idx": index,
        "mapsec": b[0],
        "cb_model": b[1],
        "cb_world": b[2],
        "fly": b[3],
        "matrix_id": struct.unpack_from("<H", b, 4)[0],
        "scripts_id": struct.unpack_from("<H", b, 6)[0],
        "levelscript_id": struct.unpack_from("<H", b, 8)[0],
        "bg_events_id": struct.unpack_from("<H", b, 10)[0],
        "connect_id": struct.unpack_from("<H", b, 12)[0],
        "return_header": struct.unpack_from("<H", b, 14)[0],
        "sound_id": struct.unpack_from("<H", b, 16)[0],
        "weather": struct.unpack_from("<H", b, 18)[0],
        "camera": struct.unpack_from("<H", b, 20)[0],
        "name_id": struct.unpack_from("<H", b, 22)[0],
    }


def main() -> None:
    print("Route 42 reference (verified guru):")
    for i in (44,):
        h = read_header(i)
        print(f"  header {i}: scripts={h['scripts_id']} bg_events={h['bg_events_id']} matrix={h['matrix_id']}")

    print("\nRoute 44 headers 46-48:")
    for i in (46, 47, 48):
        h = read_header(i)
        print(
            f"  header {i}: scripts={h['scripts_id']} bg_events={h['bg_events_id']} "
            f"matrix={h['matrix_id']} name={h['name_id']}"
        )


if __name__ == "__main__":
    main()
