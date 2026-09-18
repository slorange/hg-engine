#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def script_offset(data: bytes, index: int) -> int:
    return index * 4 + 4 + struct.unpack_from("<i", data, index * 4)[0]


def count_scripts(data: bytes) -> int:
    pos = 0
    n = 0
    while pos + 2 <= len(data) and struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        n += 1
        pos += 4
    return n


def scan(path: Path) -> None:
    data = path.read_bytes()
    n = count_scripts(data)
    print(f"{path.name}: {n} scripts")
    for s in range(n):
        start = script_offset(data, s)
        end = script_offset(data, s + 1) if s + 1 < n else len(data)
        body = data[start:end]
        msgs = []
        i = 0
        while i + 4 <= len(body):
            op = struct.unpack_from("<H", body, i)[0]
            if op == 45:
                msgs.append(struct.unpack_from("<H", body, i + 2)[0])
            i += 2
        print(f"  script {s}: npc_msg ids {msgs}")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        scan(Path(arg))
