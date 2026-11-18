#!/usr/bin/env python3
"""Build a portable browser viewer with a snapshot of actual ROM overlay ranges."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import struct

import ndspy.rom

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', nargs='?', type=Path, default=ROOT / 'test.nds')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/overlay-memory-viewer.html')
    args = parser.parse_args()
    rom = ndspy.rom.NintendoDSRom.fromFile(str(args.rom))
    rows = []
    for p in range(0, len(rom.arm9OverlayTable), 32):
        ident, start, size, bss, _, _, _, _ = struct.unpack_from('<8I', rom.arm9OverlayTable, p)
        rows.append(dict(id=ident, start=start, size=size, bss=bss, end=start+size+bss))
    stamp = datetime.fromtimestamp(args.rom.stat().st_mtime).isoformat(sep=' ', timespec='seconds')
    metadata = json.loads(Path(__file__).with_name('overlay_descriptions.json').read_text(encoding='utf-8'))
    data = json.dumps(dict(source=f'{args.rom.name} · built {stamp}', rows=rows, metadata=metadata)).replace('<', '\\u003c')
    template = Path(__file__).with_name('overlay_memory_viewer.html').read_text(encoding='utf-8')
    assert template.count('__OVERLAY_DATA__') == 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(template.replace('__OVERLAY_DATA__', data), encoding='utf-8')
    print(f'Wrote {args.output} ({len(rows)} overlays)')


if __name__ == '__main__':
    main()
