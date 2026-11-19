#!/usr/bin/env python3
"""Replace the three shared Center link attendants with dialogue-only researchers."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from patch_zone_event_r32pc_rod_guru import parse_zone_event
sys.path.insert(0,str(ROOT/'scripts/build'))
from patch_r32_outdoor_rod_guru import write_events


def researcher_objects(objects):
    result=[]
    for obj in objects:
        fields=list(struct.unpack('<14HI',obj))
        if fields[0] in (0,1,2):
            fields[1]=338  # SPRITE_GSASSISTANTM: lab-coated researcher.
            fields[5]=9+fields[0]
        result.append(struct.pack('<14HI',*fields))
    return result


def patch_scripts(path):
    data=path.read_bytes()
    assert struct.unpack_from('<H',data,32)[0]==0xFD13,'run after rest/Abra'
    out=bytearray(44)
    for slot in range(8):
        struct.pack_into('<i',out,slot*4,struct.unpack_from('<i',data,slot*4)[0]+12)
    start=len(data)+12
    scripts=[]
    for slot,message in zip(range(8,11),range(46,49)):
        # Select sound, lock, face player, message, wait, close, release, end.
        body=struct.pack('<HHHHHBHHHH',73,1500,96,104,45,message,50,53,97,2)
        scripts.append(body)
        struct.pack_into('<i',out,slot*4,start-(slot*4+4))
        start+=len(body)
    out.extend(data[32:])
    for body in scripts:out.extend(body)
    path.write_bytes(out)


def patch_events(path):
    bg,objects,warps,coords=parse_zone_event(path.read_bytes())
    assert {struct.unpack_from('<H',o)[0] for o in objects}>={0,1,2}
    write_events(path,bg,researcher_objects(objects),warps,coords)


if __name__=='__main__':
    {'scripts':patch_scripts,'events':patch_events}[sys.argv[1]](Path(sys.argv[2]))
