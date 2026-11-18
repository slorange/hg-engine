#!/usr/bin/env python3
"""Dump actual loaded overlay ranges (initialized data plus BSS), not limits."""
import argparse
from pathlib import Path
import struct

import ndspy.rom

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', nargs='?', type=Path, default=ROOT / 'test.nds')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/overlay_memory_ranges.txt')
    args = parser.parse_args()
    rom = ndspy.rom.NintendoDSRom.fromFile(str(args.rom))
    lines = [f'Overlay memory ranges from {args.rom.name}',
             'All addresses are hexadecimal. End addresses are exclusive.',
             'Used range = [start, start + initialized size + BSS size).',
             'Initialized size is the decompressed code/data footprint, not compressed ROM storage.',
             'These are actual overlay footprints, not linker allocations or growth limits.',
             'Overlapping ranges can belong to overlays loaded at different times.', '']
    for cpu, table in [('ARM9', rom.arm9OverlayTable), ('ARM7', rom.arm7OverlayTable)]:
        assert len(table) % 32 == 0
        lines += [f'{cpu}: {len(table)//32} overlays',
                  ' ID  Start       Code/data end  Used end    Code/data bytes  BSS bytes  Total bytes']
        for offset in range(0, len(table), 32):
            ident, start, size, bss, _, _, _, _ = struct.unpack_from('<8I', table, offset)
            lines.append(f'{ident:3d}  0x{start:08X}  0x{start+size:08X}  0x{start+size+bss:08X}'
                         f'  {size:15d}  {bss:9d}  {size+bss:11d}')
        lines.append('')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
