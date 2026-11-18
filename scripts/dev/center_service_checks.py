"""Script-table helpers for independently appended Center services."""
import struct


def table(data):
    pos = 0
    while pos < 256 and struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        pos += 4
    assert pos < 256
    return pos, [i * 4 + 4 + struct.unpack_from("<i", data, i * 4)[0] for i in range(pos // 4)]


def body(data, slot):
    _, starts = table(data)
    start = starts[slot]
    end = min((i for i in starts if i > start), default=len(data))
    return data[start:end]
