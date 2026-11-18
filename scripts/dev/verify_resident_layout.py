#!/usr/bin/env python3
"""Verify the expanded resident region, loader entry, prefix and packed ranges."""
from pathlib import Path
import struct

import ndspy.rom
import ndspy.codeCompression
from verify_abra_travel_arm import Machine, ROOT, REGS
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4, UC_ARM_REG_PC, UC_ARM_REG_SP

BASE, LIMIT, PREFIX = 0x023D6000, 0x023E0000, 0x60


def main():
    rom = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / 'test.nds'))
    entries = [struct.unpack_from('<8I', rom.arm9OverlayTable, p)
               for p in range(0, len(rom.arm9OverlayTable), 32)]
    root = entries[129]
    assert root[1] == BASE and root[1]+root[2]+root[3] <= LIMIT
    data = bytes(rom.files[root[6]])
    blob = (ROOT / 'build/output.bin').read_bytes()
    assert data[PREFIX:] == blob and len(data) == root[2]
    assert data.startswith(b'hg-engine rocks!')
    for table in (rom.arm9OverlayTable, rom.arm7OverlayTable):
        for p in range(0, len(table), 32):
            ident, start, size, bss, *_ = struct.unpack_from('<8I', table, p)
            if table is rom.arm9OverlayTable and ident == 129:
                continue
            assert not (start < LIMIT and start+size+bss > BASE), ('resident overlap', ident)
    for ident, start, capacity in ((130,0x023C4000,0x12000),(131,0x023C8000,0xE000)):
        entry = entries[ident]
        assert entry[1] == start and entry[2]+entry[3] <= capacity

    # Native trainer-AI BLs must now land inside the relocated 96-byte prefix.
    ai_entry = entries[10]
    ai = bytes(rom.files[ai_entry[6]])
    if ai_entry[7] & 0x1000000:
        ai = ndspy.codeCompression.decompress(ai)
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    dis = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for off in (0x3E8,0xDFC,0xF04,0xF30,0x1278,0x180C):
        ins = next(dis.disasm(ai[off:off+4], ai_entry[1]+off))
        assert ins.mnemonic == 'bl'
        target = int(ins.op_str.lstrip('#'), 16)
        assert BASE <= target < BASE+PREFIX, ('AI prefix target', hex(target))

    class BootMachine(Machine):
        def __init__(self):
            super().__init__()
            self.loaded = False
            self.uc.mem_write(rom.arm9RamAddress, bytes(rom.arm9))

        def hook(self, uc, addr, size, unused):
            if addr == 0x02007000:
                assert uc.reg_read(UC_ARM_REG_R0) == 129
                assert uc.reg_read(UC_ARM_REG_R4) == 2
                assert uc.reg_read(UC_ARM_REG_R1) == 0xFFFFFFFF
                uc.mem_write(BASE, data)
                self.loaded = True
                uc.reg_write(UC_ARM_REG_R0, 1)
                # The native loader's skipped prologue pushed r3-r7/lr.
                sp = uc.reg_read(UC_ARM_REG_SP)
                saved = struct.unpack('<6I', uc.mem_read(sp,24))
                uc.reg_write(UC_ARM_REG_SP,sp+24)
                uc.reg_write(UC_ARM_REG_PC,saved[-1])
                return
            return super().hook(uc, addr, size, unused)

    m = BootMachine()
    m.call(0x02110334)
    assert m.loaded and bytes(m.uc.mem_read(BASE,len(data))) == data
    assert m.call('CenterHub_GetOrigin',0x030F0000) == 5
    print(f'OK: relocated boot loader, resident execution, AI prefix branches, packed bytes and all overlay/BSS ranges; 129 {root[2]} used / {LIMIT-BASE} capacity, {LIMIT-BASE-root[2]} free')


if __name__ == '__main__':
    main()
