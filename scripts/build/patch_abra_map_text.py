"""Generate Abra's map bank from the shared Fly picker bank."""

import re
import struct
import sys
from pathlib import Path


def replace_prefix(bank, message, old, new):
    count, seed = struct.unpack_from("<HH", bank)
    if message >= count:
        raise ValueError(f"Missing map message {message}")
    index = message + 1
    entry = 4 + 8 * message
    key = (765 * index * seed) & 0xFFFF
    key |= key << 16
    offset, length = (value ^ key for value in struct.unpack_from("<II", bank, entry))

    def crypt(codes):
        return [code ^ ((index * 596947 + pos * 18749) & 0xFFFF)
                for pos, code in enumerate(codes)]

    codes = crypt(struct.unpack_from(f"<{length}H", bank, offset))
    if codes[:len(old)] != old:
        raise ValueError(f"Unexpected wording in map message {message}")
    codes = new + codes[len(old):]
    struct.pack_into("<II", bank, entry, len(bank) ^ key, len(codes) ^ key)
    bank.extend(struct.pack(f"<{len(codes)}H", *crypt(codes)))


def main(charmap, directory):
    glyphs = {char: int(code, 16) for code, char in re.findall(
        r"^([0-9A-Fa-f]{4})=([A-Za-z])$", charmap.read_text(encoding="utf-8"), re.M)}
    fly = [glyphs[char] for char in "Fly"]
    teleport = [glyphs[char] for char in "Teleport"]
    bank = bytearray((directory / "7_273").read_bytes())
    replace_prefix(bank, 5, fly, teleport)
    replace_prefix(bank, 7, fly, teleport)
    (directory / "7_855").write_bytes(bank)


if __name__ == "__main__":
    main(*map(Path, sys.argv[1:]))
