#!/usr/bin/env python3
"""Run packed overlay 152 with native adapters and check its synchronous lifetime."""
import re
import struct
import sys

import ndspy.rom
import ndspy.narc
from verify_abra_travel_arm import Machine, ROOT, REGS, FS, PROFILE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_CPSR

sys.path.insert(0, str(ROOT / 'scripts/build'))
from gen_overlay_imports import symbols

SERVICE, ECO, BLOB, MON, SETUP, PARTY = 0x023C0400, 0x03040000, 0x03050000, 0x030A0000, 0x030C0000, 0x030D0000


def mon_fields():
    text = (ROOT / 'include/pokemon.h').read_text()
    text = text[text.index('MON_DATA_PERSONALITY = 0'):]
    result, value = {}, 0
    for name, number in re.findall(r'^\s*(MON_DATA_\w+)(?:\s*=\s*(\d+))?,',text,re.M):
        if number:
            value = int(number)
        result[name] = value
        value += 1
    return result


F = mon_fields()


class EncounterMachine(Machine):
    def __init__(self, rom):
        super().__init__()
        self.rom, self.loaded, self.fail_load = rom, False, False
        self.events, self.mons, self.added, self.random = [], {}, [], 12345
        self.fail_mon = self.repel = False
        self.checked = set()
        self.bank = 23  # National Park, shared normal/contest roster.
        self.uc.mem_write(rom.arm9RamAddress, bytes(rom.arm9))
        for ident in (129,131):
            entry = struct.unpack_from('<8I',rom.arm9OverlayTable,ident*32)
            self.uc.mem_write(entry[1], bytes(rom.files[entry[6]]))
        self.entry = struct.unpack_from('<8I',rom.arm9OverlayTable,152*32)
        self.payload = bytes(rom.files[self.entry[6]])
        self.worker = symbols(ROOT / 'build/encounter_linked.o')
        self.native = {name: value & ~1 for name,value in self.symbols.items()}
        blob = bytes(ndspy.narc.NARC(rom.getFileByName('a/0/2/8')).files[19])
        off_family, off_groups, off_banks = struct.unpack_from('<3I',blob,20)
        off_slots = struct.unpack_from('<I',blob,52)[0]
        groups = struct.unpack_from('<H',blob,10)[0]
        self.banks = []
        for method in range(7):
            group = next(g for g in range(groups) if blob[off_slots+g*7+method])
            bank_offset = struct.unpack_from('<H',blob,off_groups+group*6)[0]
            self.banks.append(blob[off_banks+bank_offset])
        self.base_species = struct.unpack_from('<H',blob,off_family)[0]
        self.uc.mem_write(BLOB,blob)
        assert self.call('EcologyCompatBindBlob',BLOB) == 1
        slots = int(re.search(r'#define ECOLOGY_GEN_TOTAL_SLOTS (\d+)',(ROOT/'include/constants/generated/ecology_compat.h').read_text()).group(1))
        self.uc.mem_write(ECO, struct.pack('<IIIHH',0x314F4345,0,99,slots,0)+bytes(slots+196))
        self.w32(PROFILE+16,0x12345678)
        self.w32(SETUP+4+3*4,PARTY)  # BATTLE_PARAM.poke_party[3].

    def load(self):
        self.uc.mem_write(SERVICE,self.payload)
        self.loaded = True

    def hook(self, uc, addr, size, unused):
        args = [uc.reg_read(r) for r in REGS]
        r0,r1,r2,r3 = args
        name = next((n for n in ('GetMonData','SetMonData','__aeabi_uidiv','__aeabi_uidivmod',
                    'EcologyGenBuildSlotLayout','EcologySaveIsValid','UpdatePassiveForms')
                     if addr == self.native.get(n)),None) if hasattr(self,'native') else None
        if name:
            assert uc.reg_read(UC_ARM_REG_CPSR)&32, f'{name} entered in ARM state'
            self.checked.add(name)
        if not hasattr(self,'native'):
            return super().hook(uc,addr,size,unused)
        def at(name):
            return addr == self.native.get(name)
        result = 0
        if at('IsOverlayLoaded'):
            assert r0 == 152
            result = self.loaded
        elif at('HandleLoadOverlay'):
            assert (r0,r1)==(152,2) and not self.loaded
            if not self.fail_load:
                self.events.append('load'); self.load(); result=1
        elif at('UnloadOverlayByID'):
            assert r0==152 and self.loaded
            self.events.append('unload');self.loaded=False
            uc.mem_write(SERVICE,bytes([0xDE])*len(self.payload))
        elif at('gf_rand'):
            self.random = (self.random*1103515245+12345)&0xFFFFFFFF
            result = self.random>>16
        elif at('SaveBlock2_get'):
            result = 0x03030000
        elif at('EcologySaveGetMutable'):
            result = ECO
        elif at('EcologyCompatSessionEnsure'):
            result = 1
        elif at('EncounterResolveMapId'):
            uc.mem_write(r0,struct.pack('<H',66));result=1
        elif at('MapHeader_GetWildEncounterBank'):
            result = self.bank
        elif at('GetScriptVar'):
            assert r0==0x4031;result=0
        elif at('GF_RTC_GetTimeOfDayWildParam'):
            result = 1
        elif at('SaveData_GetPlayerPartyPtr'):
            result = 0  # No Compound Eyes lead in these fixtures.
        elif at('Sav2_PlayerData_GetProfileAddr'):
            result = PROFILE
        elif at('AllocMonZeroed'):
            if not self.fail_mon:
                result=MON;self.mons[MON]={};uc.mem_write(MON,bytes(1024))
        elif at('PokeParaSet'):
            self.mons[r0]={F['MON_DATA_SPECIES']:r1,F['MON_DATA_LEVEL']:r2,
                           F['MON_DATA_FORM']:0,F['MON_DATA_PERSONALITY']:123456,F['MON_DATA_STATUS']:0}
        elif at('GetMonData'):
            result=self.mons.setdefault(r0,{}).get(r1,0)
        elif at('SetMonData'):
            widths={F['MON_DATA_SPECIES']:2,F['MON_DATA_HELD_ITEM']:2,F['MON_DATA_FORM']:1,
                    F['MON_DATA_LEVEL']:1,F['MON_DATA_GENDER']:1}
            value=int.from_bytes(bytes(uc.mem_read(r2,widths.get(r1,4))),'little') if r2 else 0
            self.mons.setdefault(r0,{})[r1]=value
        elif at('GrabSexFromSpeciesAndForm'):
            result=0
        elif at('PokeLevelExpGet'):
            result=r1**3
        elif at('RecalcPartyPokemonStats') or at('ResetPartyPokemonAbility'):
            pass
        elif at('InitBoxMonMoveset'):
            self.events.append('moves')
        elif at('BugContest_DoesRepelSuppress'):
            result=self.repel
        elif at('PokeParty_Add'):
            self.added.append((r0,r1));result=1
        elif at('sys_FreeMemoryEz') and r0==MON:
            self.events.append('free mon')
        else:
            return super().hook(uc,addr,size,unused)
        uc.reg_write(UC_ARM_REG_R0,result)
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))


def main():
    rom=ndspy.rom.NintendoDSRom.fromFile(str(ROOT/'test.nds'))
    m=EncounterMachine(rom)
    assert m.entry[1]==SERVICE and m.entry[2]<=0x3C00
    assert m.payload==(ROOT/'build/output_encounter.bin').read_bytes()
    magic,*pointers=struct.unpack_from('<19I',m.payload)
    assert magic==0x454E4301
    assert all(p&1 and SERVICE<=(p&~1)<SERVICE+len(m.payload) for p in pointers)
    # Imported data must be the exact resident object address, not address|1.
    for name in ('gEcologyCompatView','WildLevelCapsFieldAddr','LevelUpEvoTablesFieldAddr'):
        assert m.worker[name][0]==m.symbols[name]
    for cap in (2,5,9,10,30,70):
        baby=0x030F0000
        level=m.call('RollWildLevel',cap,baby)
        assert 2<=level<=cap and not m.loaded
        assert m.events[-2:]==['load','unload']
    m.load();m.events.clear()
    assert 2<=m.call('RollWildLevel',20,0x030F0000)<=20 and m.loaded
    assert not m.events, 'borrowed service must remain loaded'
    m.loaded=False;m.fail_load=True
    sentinel=bytes([0xA7])*len(m.payload)
    m.uc.mem_write(SERVICE,sentinel)
    assert m.call('CreateEcologyWildMon',0,0,31)==0 and not m.loaded
    assert bytes(m.uc.mem_read(SERVICE,len(sentinel)))==sentinel, 'load failure must not overwrite another overlay'
    m.fail_load=False
    # Every supported method runs real ecology selection, stage/level, held
    # items and finalization against the packed field tables and compat blob.
    for method,rod in ((0,0),(1,0),(2,0),(2,1),(2,2),(3,0),(4,0)):
        ecology_method = (0,1,2+rod,5,6)[method]
        m.bank=m.banks[ecology_method]
        assert m.call('EcologyRollSpeciesForEncounterBank',m.bank,ecology_method)==m.base_species
        cap=m.call('GetWildLevelCapForEncounterBank',m.bank)
        m.w32(m.symbols['sWildCapCache'],0)
        m.events.clear()
        assert m.call('CreateEcologyWildMon',method,rod,31)==MON
        mon=m.mons[MON]
        wooloo=int(re.search(r'#define SPECIES_WOOLOO\s+(\d+)',(ROOT/'include/constants/species.h').read_text()).group(1))
        assert mon[F['MON_DATA_SPECIES']] != wooloo, 'Wooloo placeholder survived'
        assert 2<=mon[F['MON_DATA_LEVEL']]<=max(2,cap)
        assert mon[F['MON_DATA_OTID']]==0x12345678
        assert m.events[0]=='load' and m.events[-1]=='unload'
        assert m.events.count('load')==m.events.count('unload')==1
        assert 'moves' in m.events and not m.loaded
    # Both seven-argument entry points must preserve battler/setup stack args.
    lead=0x030E0000
    m.uc.mem_write(lead,bytes([0xA5])*256)
    for fn in ('SetEncountData_Ecology','BugContest_GenerateEcologyEncounter'):
        m.events.clear();m.added.clear();m.bank=m.banks[0]
        if fn=='SetEncountData_Ecology':
            args=(lead,0,0,0,0,3,SETUP)
        else:
            args=(FS,lead,0,0,0,3,SETUP)
        assert m.call(fn,*args)==1 and m.added==[(PARTY,MON)]
        assert m.events.count('load')==m.events.count('unload')==1 and not m.loaded
        assert bytes(m.uc.mem_read(lead,256))==bytes([0xA5])*256
    m.repel=True;m.added.clear()
    assert m.call('BugContest_GenerateEcologyEncounter',FS,lead,0,0,0,3,SETUP)==0
    assert not m.added and not m.loaded
    m.repel=False;m.fail_mon=True
    assert m.call('SetEncountData_Ecology',lead,0,0,0,0,3,SETUP)==0 and not m.loaded
    assert {'GetMonData','SetMonData','EcologyGenBuildSlotLayout','EcologySaveIsValid','UpdatePassiveForms'}<=m.checked
    print(f'OK: packed overlay 152 ({len(m.payload)} bytes); typed imports; real level rolls and finalization for land/surf/three rods/rock smash/headbutt; seven-argument generation ABI, lead preservation, contest Repel and allocation failure, ownership and unload-before-return')


if __name__=='__main__':
    main()
