#!/usr/bin/env python3
"""Check packed field service placement and execute its resident dispatcher."""
import struct
import ndspy.rom
from verify_abra_travel_arm import Machine, ROOT, REGS, PROFILE, CTX, FS
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


class HarvestMachine(CraftMachine):
    OBJECT_PTR, OBJECT, SCRIPT, VARS = (0x030C0000, 0x030C0100, 0x030C0200, 0x030C0300)

    def __init__(self, rom, colour, room):
        super().__init__(rom, True)
        self.colour, self.room = colour, room
        self.capacity_checks = []
        self.w32(self.OBJECT_PTR, self.OBJECT)
        self.w32(CTX + 8, self.SCRIPT)
        self.uc.mem_write(self.SCRIPT, bytes((9, 0, 0)))

    def hook(self, uc, addr, size, unused):
        args = [uc.reg_read(r) for r in REGS]
        if addr == (self.symbols['FieldSysGetAttrAddr'] & ~1):
            assert args[:2] == [FS, 10]
            result = self.OBJECT_PTR
        elif addr == (self.symbols['GetVarPointer'] & ~1):
            assert args[0] == FS and args[1] in (0x8000, 0x8004, 0x800C)
            result = self.VARS + (args[1] - 0x8000) * 4
        elif addr == (self.symbols['FieldSystem_ApricornTree_HasFruit'] & ~1):
            assert args[:2] == [FS, self.OBJECT]
            result = self.colour is not None
        elif addr == (self.symbols['FieldSystem_ApricornTree_GetApricorn'] & ~1):
            assert args[:2] == [FS, self.OBJECT] and self.colour is not None
            result = self.colour
        elif addr == (self.symbols['Sav2_Bag_get'] & ~1):
            result = TransactionMachine.BAG
        elif addr == (self.symbols['Bag_HasSpaceForItem'] & ~1):
            assert args[0] == TransactionMachine.BAG
            self.capacity_checks.append(tuple(args[1:]))
            result = self.room
        else:
            return super().hook(uc, addr, size, unused)
        assert uc.reg_read(UC_ARM_REG_CPSR) & 32
        uc.reg_write(UC_ARM_REG_R0, result)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))


class TransactionMachine(CraftMachine):
    """Run real packed field code and real memcpy/division helpers."""
    BAG = 0x030A0000

    def __init__(self, rom, funds=1000, full=False):
        super().__init__(rom, True)
        field = struct.unpack_from('<8I', rom.arm9OverlayTable, 131*32)
        self.uc.mem_write(field[1], bytes(rom.files[field[6]]))
        self.uc.mem_write(self.BAG, struct.pack("<HH", 485, 27))
        self.w32(PROFILE + 0x14, funds)
        self.full, self.added, self.checked = full, [], set()

    def hook(self, uc, addr, size, unused):
        # These calls must reach the Thumb entries, never an ARM trampoline
        # that branches into their halfword instructions in ARM state.
        names = ('Bag_GetQuantity', 'Bag_AddItem', 'Bag_TakeItem',
                 'memcpy', '__aeabi_uidiv')
        name = next((n for n in names if addr == (self.symbols[n] & ~1)), None)
        if name:
            assert uc.reg_read(UC_ARM_REG_CPSR) & 32, f'{name} entered in ARM state'
            self.checked.add(name)
        args = [uc.reg_read(r) for r in REGS]
        if addr == (self.target & ~1):
            return  # Run the relocated implementation, not the dispatcher mock.
        if addr == 0x0207879C:
            result = self.BAG
        elif name == 'Bag_GetQuantity':
            item, count = struct.unpack('<HH', uc.mem_read(args[0], 4))
            result = count if args[1] == item else 0
        elif name == 'Bag_AddItem':
            self.added.append((args[1], args[2]))
            result = not self.full
        elif name == 'Bag_TakeItem':
            assert args[0] != self.BAG and tuple(args[1:3]) == (485, 27)
            assert bytes(uc.mem_read(args[0], 4)) == struct.pack('<HH', 485, 27)
            self.w32(args[0], 0)
            result = True
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
        assert m.r32(m.BAG) == (0 if paid else (27 << 16) | 485)
        assert {'Bag_GetQuantity','__aeabi_uidiv'} <= m.checked
        if funds >= 300:
            assert {'memcpy','Bag_TakeItem','Bag_AddItem'} <= m.checked
            assert len(m.added) == 1 and m.added[0][1] == 27
    for colour in (None, *range(7)):
        for room in (False, True):
            m = HarvestMachine(rom, colour, room)
            assert m.call('Script_RunNewCmd', CTX) == 0
            assert m.r32(m.VARS + 0xC * 4) == (0 if colour is None else 1 if room else 2)
            if colour is None:
                assert not m.capacity_checks
            else:
                assert m.capacity_checks == [(485 + colour, 1, 11)]
                assert m.r32(m.VARS) == colour
                assert m.r32(m.VARS + 4 * 4) == 485 + colour
    print('OK: packed tree preflight, empty trees, and Bag capacity for all seven colours')
    print(f'OK: packed field transaction quote/commit/failures, Thumb helper calls, dispatcher loaded/unloaded/null guards, no overlap; overlay 129 {root[2]} bytes, {0xA000-root[2]} free')


if __name__ == '__main__':
    main()
