#!/usr/bin/env python3
"""Preserve ELF function/data types for imports from the resident overlay.

Plain linker assignments lose Thumb function metadata for direct BL calls.
Absolute symbols in this assembly object retain it, including for compiler
helpers, and keep imported data addresses even rather than treating them as code.
"""
import argparse
from pathlib import Path
import struct


def symbols(path):
    data = path.read_bytes()
    off = struct.unpack_from('<I', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 46)
    sections = [struct.unpack_from('<10I', data, off+i*size) for i in range(count)]
    result = {}
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        names = data[strings[4]:strings[4]+strings[5]]
        for pos in range(section[4], section[4]+section[5], section[9]):
            name, value, length, info, _, index = struct.unpack_from('<IIIBBH', data, pos)
            if info >> 4 not in (1, 2):
                continue
            name = names[name:].split(b'\0',1)[0].decode()
            result[name] = (value, info & 15, index)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resident', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('objects', type=Path, nargs='+')
    args = parser.parse_args()
    root = symbols(args.resident)
    defined, needed = set(), set()
    for obj in args.objects:
        for name, (_, _, index) in symbols(obj).items():
            (defined if index else needed).add(name)
    lines = ['.syntax unified', '.thumb', '']
    for name in sorted(needed-defined):
        if name not in root:
            raise SystemExit(f'Missing resident import: {name}')
        value, kind, _ = root[name]
        thumb = kind == 2 and value & 1
        # Native ROM bindings are absolute NOTYPE symbols; odd addresses are
        # Thumb functions. Resident OBJECT globals keep their exact address.
        if kind == 0 and value & 1 and 0x02000000 <= value < 0x02400000:
            kind, thumb = 2, True
        lines.append(f'.global {name}')
        if kind in (1, 2):
            lines.append(f'.type {name}, %'+('function' if kind == 2 else 'object'))
        lines.append(f'{".thumb_set" if thumb else ".equ"} {name}, 0x{value:08X}')
    args.output.write_text('\n'.join(lines)+'\n')
    print(f'Generated {len(needed-defined)} typed resident imports: {args.output}')


if __name__ == '__main__':
    main()
