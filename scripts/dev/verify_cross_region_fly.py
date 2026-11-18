#!/usr/bin/env python3
"""Exercise the packed ARM9 Fly launcher and compiled replacement in Unicorn."""
import struct

import ndspy.rom

from verify_abra_travel_arm import Machine, ROOT, FS, APP, REGS
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_R0


class FlyMachine(Machine):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.launched = False

    def hook(self, uc, addr, size, unused):
        r0, r1, r2, r3 = [uc.reg_read(r) for r in REGS]
        if addr == 0x0203EAB0:
            return  # Execute the installed hook, not the Abra test adapter.
        if addr == 0x0201AACC:
            assert (r0, r1) == (11, 0x2C)
            result = APP
        elif addr == 0x02092D8C:
            assert (r0, r1) == (FS, APP)
            assert bytes(uc.mem_read(APP, 0x2C)) == bytes(0x2C)
            uc.mem_write(APP, self.source)
            result = 0
        elif addr == 0x0203EA5C:
            assert (r0, r1) == (FS, APP)
            self.launched = True
            result = 0
        else:
            return super().hook(uc, addr, size, unused)
        uc.reg_write(UC_ARM_REG_R0, result)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))


def main():
    rom = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / 'test.nds'))
    for x, z in ((564, 392), (1323, 242), (896, 192)):
        for kind in (0, 1):
            source = bytearray(range(0x2C))
            struct.pack_into('<ii', source, 8, x, z)
            source[0x22:0x24] = bytes((x // 32, z // 32))
            m = FlyMachine(bytes(source))
            m.uc.mem_write(0x02000000, bytes(rom.arm9))
            assert m.call(0x0203EAB0, FS, kind) == APP
            assert m.launched
            expected = bytearray(source)
            expected[0] = kind
            if kind == 0:
                struct.pack_into('<ii', expected, 8, 28*32, 6*32)
            assert bytes(m.uc.mem_read(APP, 0x2C)) == bytes(expected)
            # All marker, cursor/result, save pointer and visit data stay intact.
            assert m.uc.mem_read(APP + 0x22, 2) == source[0x22:0x24]
    overlay = struct.unpack_from('<8I', rom.arm9OverlayTable, 129*32)
    addr = m.symbols['PokegearTownMap_LaunchApp_hook'] & ~1
    assert rom.files[overlay[6]][addr-overlay[1]:addr-overlay[1]+64] == bytes(m.uc.mem_read(addr, 64))
    print('OK: packed ARM9 launcher hook; neutral Fly context from Johto/Kanto/Indigo; original source marker, result fields and save pointer preserved; ordinary town maps unchanged')


if __name__ == '__main__':
    main()
