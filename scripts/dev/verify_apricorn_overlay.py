#!/usr/bin/env python3
"""Check packed field service placement and execute its resident dispatcher."""
import struct
import ndspy.rom
from verify_abra_travel_arm import Machine, ROOT, REGS, PROFILE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_CPSR


class CraftMachine(Machine):
    def __init__(self, rom, loaded):
        super().__init__()
        self.loaded, self.calls = loaded, []
        entry = struct.unpack_from('<8I', rom.arm9OverlayTable, 129*32)
        self.uc.mem_write(entry[1], bytes(rom.files[entry[6]]))
        self.target = self.r32(self.symbols['ApricornCraftFieldAddr'])

    def hook(self, uc, addr, size, unused):
        args = [uc.reg_read(r) for r in REGS]
        if addr == (self.symbols['IsOverlayLoaded'] & ~1):
            assert args[0] == 131
            result = self.loaded
        elif addr == (self.target & ~1):
            self.calls.append(args)
            self.w32(args[2], 27)  # Outputs are u16; buffer has spare space.
            self.w32(args[3], 3)
            result = 0
        else:
            return super().hook(uc, addr, size, unused)
        uc.reg_write(UC_ARM_REG_R0, result)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))


class TransactionMachine(CraftMachine):
    """Run real packed field code and real memcpy/memset/division helpers."""
    BAG, BOX = 0x030A0000, 0x030B0000

    def __init__(self, rom, funds=1000, full=False):
        super().__init__(rom, True)
        field = struct.unpack_from('<8I', rom.arm9OverlayTable, 131*32)
        self.uc.mem_write(field[1], bytes(rom.files[field[6]]))
        self.uc.mem_write(self.BOX, bytes([27, 0, 0, 0, 0, 0, 0, 77]))
        self.w32(PROFILE + 0x14, funds)
        self.full, self.added, self.checked = full, [], set()

    def hook(self, uc, addr, size, unused):
        # These calls must reach the Thumb entries, never an ARM trampoline
        # that branches into their halfword instructions in ARM state.
        names = ('Bag_GetQuantity', 'Bag_AddItem', 'Bag_TakeItem',
                 'memcpy', 'memset', '__aeabi_uidiv')
        name = next((n for n in names if addr == (self.symbols[n] & ~1)), None)
        if name:
            assert uc.reg_read(UC_ARM_REG_CPSR) & 32, f'{name} entered in ARM state'
            self.checked.add(name)
        args = [uc.reg_read(r) for r in REGS]
        if addr == (self.target & ~1):
            return  # Run the relocated implementation, not the dispatcher mock.
        if addr == 0x0207879C:
            result = self.BAG
        elif addr == 0x02031B14:
            result = self.BOX
        elif name == 'Bag_GetQuantity':
            result = 0
        elif name == 'Bag_AddItem':
            self.added.append((args[1], args[2]))
            result = not self.full
        elif name == 'Bag_TakeItem':
            raise AssertionError('Box-only scenario must not remove bag items')
        else:
            return super().hook(uc, addr, size, unused)
        uc.reg_write(UC_ARM_REG_R0, result)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))


def main():
    rom = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / 'test.nds'))
    field = struct.unpack_from('<8I', rom.arm9OverlayTable, 131*32)
    root = struct.unpack_from('<8I', rom.arm9OverlayTable, 129*32)
    assert field[1] + field[2] + field[3] <= root[1], 'field overlaps resident code'
    assert root[1] == 0x023D6000 and root[2] + root[3] <= 0xA000
    for loaded in (False, True):
        for commit in (False, True):
            m = CraftMachine(rom, loaded)
            assert 'ApricornCraft_Exchange' not in m.symbols
            assert m.target & 1 and field[1] <= (m.target & ~1) < field[1]+field[2]
            actual = bytes(rom.files[field[6]])
            assert actual == (ROOT / 'base/overlay/overlay_0131.bin').read_bytes()
            total, fee = 0x030E0000, 0x030E0100
            m.w32(total, 999); m.w32(fee, 999)
            result = m.call('ApricornCraft_Run', 0x030D0000, commit, total, fee)
            assert result == (0 if loaded else 4)
            assert m.calls == ([[0x030D0000, commit, total, fee]] if loaded else [])
            assert (m.r32(total), m.r32(fee)) == ((27, 3) if loaded else (0, 0))
            m.w32(m.symbols['ApricornCraftFieldAddr'], 0)
            m.calls.clear()
            assert m.call('ApricornCraft_Run', 0x030D0000, commit, total, fee) == 4
            assert not m.calls
    for commit, funds, full, status in ((False,1000,False,0), (True,1000,False,0),
                                        (True,299,False,2), (True,1000,True,3)):
        m = TransactionMachine(rom, funds, full)
        total, fee = 0x030E0000, 0x030E0100
        assert m.call('ApricornCraft_Run', 0x030D0000, commit, total, fee) == status
        assert (m.r32(total), m.r32(fee)) == (27, 3)
        paid = commit and status == 0
        assert m.r32(PROFILE+0x14) == funds - (300 if paid else 0)
        assert bytes(m.uc.mem_read(m.BOX,8)) == bytes([0 if paid else 27,0,0,0,0,0,0,77])
        assert {'Bag_GetQuantity','__aeabi_uidiv'} <= m.checked
        if funds >= 300:
            assert {'memcpy','Bag_AddItem'} <= m.checked
            assert len(m.added) == 1 and m.added[0][1] == 27
        if paid:
            assert 'memset' in m.checked
    print(f'OK: packed field transaction quote/commit/failures, Thumb helper calls, dispatcher loaded/unloaded/null guards, no overlap; overlay 129 {root[2]} bytes, {0xA000-root[2]} free')


if __name__ == '__main__':
    main()
