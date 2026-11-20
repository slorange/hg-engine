#!/usr/bin/env python3
"""Check packed field service placement and execute its resident dispatcher."""
import struct
from collections import Counter
import re
import ndspy.narc
import ndspy.rom
from verify_abra_travel_arm import Machine, ROOT, REGS, PROFILE, CTX, FS, STOP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R5, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_CPSR

TREE_TAGS = (262, *range(263, 270), 428, 429)
FRUIT_TAGS = (270, *range(270, 277), 430, 431)
APRICORN_ITEMS = (*range(485, 492), 2685, 2686)


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

    def __init__(self, rom, colour, room, ripe=True, roll=0):
        super().__init__(rom, True)
        self.colour, self.room, self.ripe = colour, room, ripe
        self.capacity_checks = []
        self.roll = roll
        self.roll_calls = 0
        self.w32(self.OBJECT_PTR, self.OBJECT)
        self.w32(CTX + 8, self.SCRIPT)
        self.uc.mem_write(self.SCRIPT, bytes((9, 0, 0)))

    def hook(self, uc, addr, size, unused):
        args = [uc.reg_read(r) for r in REGS]
        if addr == (self.symbols['FieldSysGetAttrAddr'] & ~1):
            assert args[:2] == [FS, 10]
            result = self.OBJECT_PTR
        elif addr == (self.symbols['GetVarPointer'] & ~1):
            assert args[0] == FS and args[1] in (0x8004, 0x8005, 0x800C)
            result = self.VARS + (args[1] - 0x8000) * 4
        elif addr == (self.symbols['MapObject_GetGfxID'] & ~1):
            assert args[0] == self.OBJECT
            result = TREE_TAGS[self.colour + 1] if self.colour is not None else TREE_TAGS[0]
        elif addr == (self.symbols['FieldSystem_ApricornTree_IsRipe'] & ~1):
            assert args[:2] == [FS, self.OBJECT]
            assert self.colour is not None
            result = self.ripe
        elif addr == (self.symbols['FieldSystem_ApricornTree_GetApricorn'] & ~1):
            assert args[:2] == [FS, self.OBJECT] and self.colour is not None
            result = self.colour
        elif addr == (self.symbols['Sav2_Bag_get'] & ~1):
            result = TransactionMachine.BAG
        elif addr == (self.symbols['gf_rand'] & ~1):
            self.roll_calls += 1
            result = self.roll
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
            assert m.added == [(492, 27)]
    for colour in (None, *range(len(APRICORN_ITEMS))):
        for room in (False, True):
            roll = (colour or 0) + 1
            m = HarvestMachine(rom, colour, room, roll=roll)
            assert m.call('Script_RunNewCmd', CTX) == 0
            assert m.r32(m.VARS + 0xC * 4) == (0 if colour is None else 1 if room else 2)
            if colour is None:
                assert not m.capacity_checks and not m.roll_calls
            else:
                item = APRICORN_ITEMS[colour]
                quantity = 3 + roll % 3
                assert m.roll_calls == 1 and m.capacity_checks == [(item, quantity, 11)]
                assert m.r32(m.VARS + 5 * 4) == quantity
                assert m.r32(m.VARS + 4 * 4) == item
    for colour in (7, 8):
        m = HarvestMachine(rom, colour, True, ripe=False)
        assert m.call('Script_RunNewCmd', CTX) == 0
        assert m.r32(m.VARS + 0xC * 4) == 0 and not m.capacity_checks
    verify_tree_colours(rom)
    print('OK: packed tree preflight, ripe and empty trees, and Bag capacity for all nine colours')
    print(f'OK: packed field transaction quote/commit/failures, Thumb helper calls, dispatcher loaded/unloaded/null guards, no overlap; overlay 129 {root[2]} bytes, {0xA000-root[2]} free')


def verify_tree_colours(rom):
    count = int(re.search(r'^#define NUM_APRICORN_TREE (\d+)', (ROOT / 'include/save.h').read_text(), re.M)[1])
    slots = []
    for member in ndspy.narc.NARC(rom.getFileByName('a/0/3/2')).files:
        if len(member) < 8:
            continue
        object_offset = 4 + 20 * struct.unpack_from('<I', member)[0]
        object_count = struct.unpack_from('<I', member, object_offset)[0]
        for i in range(object_count):
            obj = struct.unpack_from('<14HI', member, object_offset + 4 + 32 * i)
            if obj[5] == 2800:
                slots.append(obj[7])
    assert sorted(slots) == list(range(count)), slots

    m = CraftMachine(rom, True)
    for addr, name in ((0x020557A0, 'ApricornTree_GetType'), (0x020557C0, 'ApricornTree_GetApricorn')):
        assert struct.unpack_from('<I', rom.arm9, addr - 0x02000000 + 4)[0] == m.symbols[name] | 1

    tree = HarvestMachine.OBJECT
    layouts = {}
    extra_colours = set()
    for seed in (0, 1, 0x12345678, 0xFFFF0001, 0):
        m.w32(PROFILE + 0x10, seed)
        layout = []
        for slot in range(count):
            m.w32(tree + 0x38, slot)  # LocalMapObject param0
            colour = m.call(0x020557A0, FS, tree)
            assert m.call(0x020557C0, FS, tree) == colour - 1
            layout.append(colour)
        layout = tuple(layout)
        frequencies = Counter(layout)
        assert frequencies.keys() == {1, 2, 3, 4, 5, 7, 8, 9}
        low, extra = divmod(count, len(frequencies))
        assert sorted(frequencies.values()) == [low] * (8 - extra) + [low + 1] * extra
        extra_colours.add(tuple(sorted(colour for colour, total in frequencies.items() if total > low)))
        assert layout == layouts.setdefault(seed, layout)
    assert len(set(layouts.values())) == len(layouts)
    assert not count % 8 or len(extra_colours) > 1
    print(f'OK: {count} packed tree slots, balanced per-save colours, and matching harvest lookups')

    for colour, tag in enumerate(TREE_TAGS[1:], 1):
        assert m.call(0x020640A4, colour, 1) == tag
        assert m.call(0x020640A4, colour, 0) == TREE_TAGS[0]

    _, base, _, _, _, _, file_id, _ = struct.unpack_from('<8I', rom.arm9OverlayTable, 32)
    ov1 = rom.files[file_id]
    m.uc.mem_write(base, bytes(ov1))
    assert m.r32(0x02204AA0) == m.symbols['gApricornFruitTags']
    spawned = []

    def capture_fruit_spawn(uc, addr, size, unused):
        spawned.append(tuple(uc.reg_read(reg) for reg in REGS))
        uc.reg_write(UC_ARM_REG_PC, STOP)

    m.uc.hook_add(UC_HOOK_CODE, capture_fruit_spawn, begin=0x02204AAC, end=0x02204AAC)
    m.uc.reg_write(UC_ARM_REG_R5, FS)
    m.w32(FS + 0x3C, 0x0300E000)
    for colour, tag in enumerate(FRUIT_TAGS[1:], 1):
        m.call(0x022049D0, colour, 0, 0, 0, 202, 401)
        assert spawned[-1] == (0x0300E000, tag, 401, 202)

    _, field_base, _, _, _, _, field_file, _ = struct.unpack_from('<8I', rom.arm9OverlayTable, 131*32)
    table_offset = m.r32(0x021FA280) - field_base
    field_data = rom.files[field_file]
    assert 0 <= table_offset < len(field_data)
    table = {}
    for offset in range(table_offset, len(field_data) - 5, 6):
        tag, index, callback = struct.unpack_from('<3H', field_data, offset)
        if tag == 0xFFFF:
            break
        table[tag] = (index, callback)
    overworlds = ndspy.narc.NARC(rom.getFileByName('a/0/8/1')).files
    for tag, index in ((428, 1858), (429, 1859), (430, 1860), (431, 1861)):
        assert table[tag] == (index, 0x5647 if tag <= 429 else 0x5826)
        assert overworlds[index] == (ROOT / f'build/pokemonow/4_{index}.btx0').read_bytes()
    for source in (ROOT / 'build/pokemonow').glob('3_*.btx0'):
        follower = int(source.stem.removeprefix('3_'))
        assert overworlds[297 + follower] == source.read_bytes()

    item_data = ndspy.narc.NARC(rom.getFileByName('a/0/1/7')).files
    item_gfx = ndspy.narc.NARC(rom.getFileByName('a/0/1/8')).files
    for item in APRICORN_ITEMS[-2:]:
        assert item_data[item] == item_data[APRICORN_ITEMS[0]]
        assert item_gfx[2 * item + 2] == (ROOT / f'build/a018/{item + 2}-00.NCGR').read_bytes()
        assert item_gfx[2 * item + 3] == (ROOT / f'build/a018/{item + 2}-01.NCLR').read_bytes()
    print('OK: tree and fruit sprite selection, Bag data/icons, and follower NARC indexes')


if __name__ == '__main__':
    main()
