#!/usr/bin/env python3
"""Exercise the compiled ARM Abra command with deterministic engine adapters.

Requires unicorn (the session-local scripts/local/_relearner_deps is supported).
This tests native argument layouts/task wiring, not the rendered map or effects.
"""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/local/_relearner_deps"))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP

REGS = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
FS, CTX, LOCAL, MISC, PROFILE, SLOT, APP, FLAGS, TASK, AVATAR = [0x03000000 + i * 0x1000 for i in range(10)]
STOP = 0x02001000


class Machine:
    def __init__(self):
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.uc.mem_map(0x02000000, 0x400000)
        self.uc.mem_map(0x03000000, 0x200000)
        self.uc.mem_write(0x02000000, (ROOT / "base/arm9.bin").read_bytes())
        elf = (ROOT / "build/linked.o").read_bytes()
        shoff = struct.unpack_from("<I", elf, 32)[0]
        size, count = struct.unpack_from("<HH", elf, 46)
        sections = [struct.unpack_from("<10I", elf, shoff + i * size) for i in range(count)]
        self.symbols = {}
        for s in sections:
            _, kind, flags, addr, off, length, link, _, _, stride = s
            if flags & 2 and kind != 8:
                self.uc.mem_write(addr, elf[off:off + length])
            if kind == 2:
                strings = sections[link]
                names = elf[strings[4]:strings[4] + strings[5]]
                for pos in range(off, off + length, stride):
                    name, value = struct.unpack_from("<II", elf, pos)
                    text = names[name:].split(b'\0', 1)[0].decode()
                    self.symbols[text] = value
        self.variables, self.visited, self.sounds, self.freed = {}, set(), [], []
        self.wait_callback = self.task_callback = self.task_env = 0
        self.app_running = False
        self.allocated = 0x03010000
        self.effects, self.arrival = [], None
        self.fail_alloc = False
        self.payment_playing = False
        self.w32(CTX + 0x80, FS); self.w32(CTX + 0x74, TASK)
        self.w32(FS + 0x40, AVATAR); self.w32(AVATAR + 0x30, 0x0300E000)
        self.w32(PROFILE + 0x14, 1000)
        self.uc.mem_write(MISC + 0x2DD, b'CH\x0d') # Saffron origin.
        self.uc.mem_write(LOCAL + 80, struct.pack('<5i', 59, -1, 1323, 242, 1))
        self.uc.mem_write(LOCAL + 104, struct.pack('<H', 23)) # lastSpawn.
        self.uc.hook_add(UC_HOOK_CODE, self.hook)

    def w32(self, addr, value): self.uc.mem_write(addr, struct.pack('<I', value))
    def r32(self, addr): return struct.unpack('<I', self.uc.mem_read(addr, 4))[0]
    def call(self, symbol, *args):
        addr = self.symbols[symbol] if isinstance(symbol, str) else symbol
        self.uc.reg_write(UC_ARM_REG_SP, 0x031FF000)
        self.uc.reg_write(UC_ARM_REG_LR, STOP | 1)
        for reg, value in zip(REGS, args): self.uc.reg_write(reg, value)
        for i, value in enumerate(args[4:]): self.w32(0x031FF000 + i * 4, value)
        self.uc.emu_start(addr | 1, STOP, count=100000)
        assert self.uc.reg_read(UC_ARM_REG_PC) == STOP, "ARM routine failed to return"
        return self.uc.reg_read(UC_ARM_REG_R0)

    def hook(self, uc, addr, size, unused):
        r0, r1, r2, r3 = [uc.reg_read(r) for r in REGS]
        result = 0
        if addr == 0x0203B9C4: result = LOCAL
        elif addr == 0x0202A954: result = MISC
        elif addr == 0x02028E9C: result = PROFILE
        elif addr == 0x020402F0:
            assert r1 == 20
            result = SLOT
        elif addr == 0x0203EAB0:
            assert r0 == FS and r1 == 0
            self.uc.mem_write(APP, bytes(0x2C)); result = APP
        elif addr == 0x0203FD58: self.wait_callback = r1
        elif addr == 0x020505A0: result = int(self.app_running)
        elif addr == 0x020503D0: result = FLAGS
        elif addr == 0x020665AC: result = int(r1 in self.visited)
        elif addr == (self.symbols['SetScriptVar'] & ~1): self.variables[r0] = r1
        elif addr == 0x0201AA8C:
            if not self.fail_alloc:
                result = self.allocated; self.allocated += 0x1000
                self.uc.mem_write(result, bytes(r1))
        elif addr == 0x0201AB0C:
            assert r0 not in self.freed, "double free"
            self.freed.append(r0)
        elif addr == 0x0200604C: self.sounds.append(r0)
        elif addr == 0x02006184:
            assert r0 == 1603
            result = int(self.payment_playing)
        elif addr == 0x02205D68: assert r0 == FS
        elif addr == 0x02050530:
            assert r0 == TASK
            self.task_callback, self.task_env = r1, r2
        elif addr == 0x02050650: result = self.task_env
        elif addr == 0x0205064C: result = FS
        elif addr in (0x0224C71C, 0x0224C75C, 0x0224C7D4):
            self.effects.append(addr)
            self.w32(r2, self.r32(r2) + 1)
        elif addr == 0x02053B04:
            assert r0 == TASK and r2 == 2, "must use Teleport arrival, not Fly"
            self.arrival = struct.unpack('<5i', self.uc.mem_read(r1, 20))
        else:
            return
        uc.reg_write(UC_ARM_REG_R0, result)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def select(self, map_id=67, selected=True):
        self.call('AbraTravel_Command', CTX, 0)
        assert self.r32(SLOT) == APP
        assert self.uc.mem_read(APP + 0x22, 2) == bytes((1323 // 32, 242 // 32))
        assert self.r32(APP + 8) == 28 * 32 and self.r32(APP + 12) == 6 * 32
        self.app_running = True
        assert self.call(self.wait_callback, CTX) == 0
        self.app_running = False
        assert self.call(self.wait_callback, CTX) == 1
        self.w32(APP + 0x14, int(selected))
        self.uc.mem_write(APP + 0x20, struct.pack('<H', map_id))
        self.call('AbraTravel_Command', CTX, 1)
        assert APP in self.freed and self.r32(SLOT) == 0


def main():
    # Inspect the actual packed native movement data, independently of the
    # task adapters below. 0x3C adds a pause between facing changes.
    import ndspy.rom
    import ndspy.codeCompression
    rom = ndspy.rom.NintendoDSRom.fromFile(str(ROOT / 'test.nds'))
    overlay = struct.unpack_from('<8I', rom.arm9OverlayTable, 2 * 32)
    data = rom.files[overlay[6]]
    if overlay[7] & 0x1000000:
        data = ndspy.codeCompression.decompress(data)
    def pauses(address, length):
        pairs = struct.iter_unpack('<HH', data[address-overlay[1]:address-overlay[1]+length])
        return [count for action, count in pairs if action == 0x3C]
    assert pauses(0x02253820, 100) == [2]*4 + [1]*4, 'departure speeds up'
    assert pauses(0x02253884, 104) == [1]*4 + [2,3,4,5], 'arrival slows down'
    m = Machine()
    m.visited.add(0x9B0 + 12) # Cherrygrove.
    m.select()
    assert m.variables[0x800C] == 1 and m.r32(PROFILE + 0x14) == 1000
    assert m.call('AbraTravel_Command', CTX, 2) == 1
    assert m.r32(PROFILE + 0x14) == 600 and m.sounds == [1603]
    m.payment_playing = True
    for _ in range(10): m.call(m.task_callback, TASK)
    assert not m.effects and m.arrival is None, 'payment must finish before Teleport'
    m.payment_playing = False
    m.call(m.task_callback, TASK)
    for _ in range(4): m.call(m.task_callback, TASK)
    assert m.effects == [0x0224C71C, 0x0224C75C, 0x0224C7D4]
    assert m.arrival == (67, -1, 564, 392, 1)
    assert struct.unpack('<H', m.uc.mem_read(LOCAL + 104, 2))[0] == 23
    assert m.uc.mem_read(MISC + 0x2DD, 3) == b'CH\x0d'
    for selected, visited, funds, expected in ((False, True, 1000, 0), (True, False, 1000, 0), (True, True, 399, 2)):
        m = Machine()
        if visited: m.visited.add(0x9BC)
        m.select(selected=selected)
        m.w32(PROFILE + 0x14, funds)
        m.call('AbraTravel_Command', CTX, 2)
        assert m.variables[0x800C] == expected
        assert m.r32(PROFILE + 0x14) == funds and not m.sounds and not m.task_callback
    m = Machine(); m.visited.add(0x9BC); m.select(); m.visited.clear()
    m.call('AbraTravel_Command', CTX, 2)
    assert m.variables[0x800C] == 0 and m.r32(PROFILE + 0x14) == 1000
    m = Machine(); m.visited.add(0x9BC); m.select(); m.w32(PROFILE + 0x14, 400)
    m.call('AbraTravel_Command', CTX, 2)
    assert m.r32(PROFILE + 0x14) == 0 and m.task_callback
    m = Machine(); m.visited.add(0x9BC); m.select(); m.fail_alloc = True
    m.call('AbraTravel_Command', CTX, 2)
    assert m.variables[0x800C] == 3 and m.r32(PROFILE + 0x14) == 1000 and not m.sounds
    # Every native Fly landing entry, including both regions and special sites.
    m = Machine()
    for i in range(30):
        flags, _, _, map_id, x, z, smap, sx, sz = struct.unpack('<9H', m.uc.mem_read(0x020F9E80 + i * 18, 18))
        m.visited = {0x9B0 + (flags & 255)}
        ok = m.call('AbraTravel_Resolve', 0x020F9E80, FLAGS, map_id, 0x030D0000, 0x030D0100)
        assert bool(ok) == bool(flags & 0x200)
        if ok:
            assert struct.unpack('<5i',m.uc.mem_read(0x030D0000,20)) == (map_id,-1,x,z,1)
            assert struct.unpack('<5i',m.uc.mem_read(0x030D0100,20)) == (smap,-1,sx,sz,1)
        m.visited.clear()
        assert not m.call('AbraTravel_Resolve', 0x020F9E80, FLAGS, map_id, 0x030D0000, 0x030D0100)
    print('OK: packed accelerating/decelerating spin sequences; compiled ARM map-argument layout, originating marker, both-region context, application wait/free, visited-only selection, cancellation, $400 charge, payment sound completion before departure, insufficient funds, stale-visit recheck, native Teleport departure/arrival wiring, unchanged blackout and hub origin')


if __name__ == '__main__': main()
