#!/usr/bin/env python3
"""Parse scr_seq init header members and print OnLoad script IDs."""
import struct
import sys
from pathlib import Path


def parse_hdr(data: bytes) -> list[tuple[str, int]]:
    pos = 0
    entries: list[tuple[str, int]] = []
    while pos + 4 <= len(data):
        word = struct.unpack_from("<I", data, pos)[0]
        if word & 0xFFFF == 0xFD13:
            break
        # InitScriptEntry: u16 type, u16 scriptId
        etype = word & 0xFFFF
        script_id = (word >> 16) & 0xFFFF
        names = {0: "OnLoad", 1: "OnTransition", 2: "OnFrame", 3: "OnWarp"}
        entries.append((names.get(etype, f"type{etype}"), script_id))
        pos += 4
    return entries


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "build/a012")
    want = {int(x) for x in sys.argv[2:]} if len(sys.argv) > 2 else set()
    for path in sorted(root.glob("2_*")):
        data = path.read_bytes()
        if len(data) > 200 or len(data) < 16:
            continue
        if struct.unpack_from("<H", data, min(4, len(data) - 2))[0] != 0xFD13 and not any(
            struct.unpack_from("<H", data, i)[0] == 0xFD13 for i in range(0, min(len(data), 64), 4)
        ):
            continue
        entries = parse_hdr(data)
        if not entries:
            continue
        idx = int(path.stem.split("_", 1)[1])
        if want and idx not in want:
            continue
        onload = next((sid for kind, sid in entries if kind == "OnLoad"), None)
        print(f"{path.name} ({len(data)}b): {entries}")


if __name__ == "__main__":
    main()
