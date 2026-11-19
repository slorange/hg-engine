#!/usr/bin/env python3
"""Execute the packed clock hooks and check Nurse Joy's compiled menu flow."""
import struct
import ndspy.rom
import ndspy.narc
from verify_abra_travel_arm import Machine, ROOT
from center_service_checks import body, table

RTC=0x021D1048
DATE=struct.pack('<4I',26,11,19,4)
TIME,OUTDATE=0x030E0000,0x030E0100


def clock_machine(rom,real_seconds=0):
    m=Machine()
    m.uc.mem_write(rom.arm9RamAddress,bytes(rom.arm9))
    e=struct.unpack_from('<8I',rom.arm9OverlayTable,129*32)
    m.uc.mem_write(e[1],bytes(rom.files[e[6]]))
    data=bytearray(88)
    struct.pack_into('<I',data,0,1)
    data[16:32]=data[44:60]=DATE
    struct.pack_into('<3I',data,32,13,14,15)
    struct.pack_into('<3I',data,60,real_seconds//3600,(real_seconds%3600)//60,real_seconds%60)
    m.uc.mem_write(RTC,bytes(data))
    return m


def seconds(m):
    m.call(0x02014708,OUTDATE,TIME)  # Run installed ARM9 jump, not just C entry.
    assert bytes(m.uc.mem_read(OUTDATE,16))==DATE
    hour,minute,second=struct.unpack('<3I',m.uc.mem_read(TIME,12))
    expected=hour*3600+minute*60+second
    m.call(0x0201474C,TIME)
    assert struct.unpack('<3I',m.uc.mem_read(TIME,12))==(hour,minute,second)
    assert m.call(0x020147A4)==expected
    return expected


def simulate(data,choice,available=True):
    pc=0;variables={};compared=False;window=black=locked=False
    calls=[];messages=[];menu=[];fades=[]
    def read(fmt):
        nonlocal pc
        value=struct.unpack_from('<'+fmt,data,pc)[0];pc+=struct.calcsize('<'+fmt);return value
    for _ in range(160):
        op=read('H')
        if op==2:
            assert not window and not black and not locked
            return calls,messages,fades
        if op==45:
            assert not window;messages.append(read('B'));window=True
        elif op==53:
            assert window;window=False
        elif op==750:
            assert window
            for _ in range(4):read('B')
            assert read('H')==0x800C
        elif op==751:menu.append((read('H'),read('H'),read('H')))
        elif op==752:
            assert menu==[(39,255,0),(40,255,1),(41,255,2),(42,255,3)]
            variables[0x800C]=choice
        elif op==17:
            var=read('H');compared=variables[var]==read('H')
        elif op==28:
            condition,offset=read('B'),read('i')
            assert condition in (1,5)
            if compared==(condition==1):pc+=offset
        elif op==22:
            offset=read('i');pc+=offset
        elif op==41:
            var,value=read('H'),read('H');variables[var]=value
        elif op==174:
            assert not window
            read('H');read('H');direction=read('H');read('H')
            fades.append(direction);black=direction==0
        elif op==208:
            assert black and not window and read('B')==7
            var=read('H');calls.append(variables[var]);variables[0x800C]=int(available)
        elif op==3:
            assert black and read('H')==30;read('H')
        elif op==73:read('H')
        elif op==96:locked=True
        elif op==97:locked=False
        elif op in (50,104,175,746,747):pass
        else:raise AssertionError((pc-2,op))
    raise AssertionError('rest script did not finish')


def main():
    rom=ndspy.rom.NintendoDSRom.fromFile(str(ROOT/'test.nds'))
    for real in (0,1,599,1799,86399):
        m=clock_machine(rom,real)
        assert seconds(m)==(real%1800)*48
        original=bytes(m.uc.mem_read(RTC,88))
        for hour in (4,10,20,4,20,10):
            assert m.call('GameClock_RestUntilHour',hour)==1
            assert seconds(m)==hour*3600
            assert bytes(m.uc.mem_read(RTC,88))==original,'rest must not rewrite real RTC/calendar'
        # One real second after rest advances exactly 48 game seconds.
        next_real=(real+1)%86400
        m.uc.mem_write(RTC+60,struct.pack('<3I',next_real//3600,(next_real%3600)//60,next_real%60))
        assert seconds(m)==10*3600+48
        assert m.call('GameClock_RestUntilHour',24)==0
        # Frozen scenes and an unavailable RTC do not consume or change offset.
        offset=m.r32(m.symbols['sGameClockOffsetSeconds'])
        m.w32(RTC+72,3);m.uc.mem_write(RTC+76,struct.pack('<3I',17,22,11))
        assert seconds(m)==17*3600+22*60+11
        assert m.call('GameClock_RestUntilHour',4)==0
        assert m.r32(m.symbols['sGameClockOffsetSeconds'])==offset
        m.w32(RTC+72,0)
        for field in (0,4):
            m.w32(RTC+field,0 if field==0 else 1)
            assert m.call('GameClock_RestUntilHour',4)==0
            assert m.r32(m.symbols['sGameClockOffsetSeconds'])==offset
            m.w32(RTC+field,1 if field==0 else 0)
        assert seconds(clock_machine(rom,real))==(real%1800)*48,'fresh boot resets offset'
    member=bytes(ndspy.narc.NARC(rom.getFileByName('a/0/1/2')).files[233])
    assert len(table(member)[1])==11
    nurse=body(member,0)
    assert nurse==(ROOT/'build/center_rest.bin').read_bytes()
    for choice,hour in enumerate((4,10,20)):
        assert simulate(nurse,choice)==([hour],[38,43],[0,1])
        assert simulate(nurse,choice,False)==([hour],[38,45],[0,1])
    for choice in (3,0xFFFE,0xFFFF):
        assert simulate(nurse,choice)==([],[38,44],[])
    print('OK: packed clock hooks, cumulative rests, midnight wraps, continued 48x ticking, unchanged RTC/date, frozen/invalid guards and fresh boot; Nurse menu/cancellation/window/fade flow')


if __name__=='__main__':main()
