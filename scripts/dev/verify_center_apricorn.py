#!/usr/bin/env python3
"""Verify the craft NPC and exercise the compiled confirmation/error paths."""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]


def simulate(body, quote=0, exchange=0, decline=False):
    pc, result, compared, commits = 0, 0, False, 0
    sounds = []
    fades = []
    def read(fmt):
        nonlocal pc
        value = struct.unpack_from("<" + fmt, body, pc)[0]
        pc += struct.calcsize("<" + fmt)
        return value
    for _ in range(150):
        op = read("H")
        if op == 2:
            return commits, sounds.count(1603)
        if op == 208:
            assert read("B") == 5
            mode = read("H")
            assert mode in (0, 1)
            commits += mode
            result = exchange if mode else quote
        elif op == 17:
            assert read("H") == 0x800C
            compared = result == read("H")
        elif op == 28:
            assert read("B") == 1
            offset = read("i")
            if compared: pc += offset
        elif op == 22:
            offset = read("i")
            pc += offset
        elif op == 73:
            sound = read("H")
            if sound == 1603:
                assert fades == [0, 1], "purchase sound before returning from the crafting fade"
            sounds.append(sound)
        elif op == 63:
            assert read("H") == 0x800C
            result = int(decline)
        elif op == 45:
            assert 25 <= read("B") <= 31
        elif op == 198:
            read("B"); read("H")
        elif op == 174:
            assert read("H") == 6
            read("H")
            fades.append(read("H"))
            assert read("H") == 0
        elif op == 3:
            assert fades == [0], "crafting pause must happen while black"
            assert read("H") == 30
            read("H")
        elif op in (50, 53, 96, 97, 104, 175):
            pass
        else:
            raise AssertionError(f"unexpected opcode {op} at {pc-2}")
    raise AssertionError("script did not finish")


def main():
    member = (ROOT / "build/a012/2_233").read_bytes()
    assert struct.unpack_from("<H", member, 24)[0] == 0xFD13
    start = 24 + struct.unpack_from("<i", member, 20)[0]
    body = member[start:]
    assert body == (ROOT / "build/center_apricorn.bin").read_bytes()
    assert simulate(body) == (1, 1)
    assert simulate(body, decline=True) == (0, 0)
    for failure in (1, 2, 3, 4):
        assert simulate(body, quote=failure) == (0, 0)
        assert simulate(body, exchange=failure) == (1, 0)
    print("OK: compiled craft confirmation, decline, all quote/commit failures, and purchase sound only on successful exchange")


if __name__ == "__main__":
    main()
