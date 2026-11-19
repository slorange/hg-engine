#!/usr/bin/env python3
"""Replace only the shared Center Nurse's entry; preserve other scripts/data."""
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def patch(path):
    data = bytearray(path.read_bytes())
    assert struct.unpack_from('<H',data,32)[0] == 0xFD13, 'run after Abra append'
    subprocess.check_call([str(ROOT/'tools/armips'),'armips/scr_seq/scr_seq_center_rest.s'],cwd=ROOT)
    # Object 3 (Nurse Joy) already uses scriptId 1. Only repoint slot zero;
    # original code remains at its old offset, including all relative branches.
    struct.pack_into('<i',data,0,len(data)-4)
    data.extend((ROOT/'build/center_rest.bin').read_bytes())
    path.write_bytes(data)


if __name__=='__main__':
    patch(Path(sys.argv[1]))
