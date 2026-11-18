#!/usr/bin/env python3
"""Check appended handler/Abra scripts and the menu/field transition contract."""
from pathlib import Path
import struct
from center_service_checks import body

ROOT = Path(__file__).resolve().parents[2]


def simulate(data, money=1000, decline=False, selected=True):
    pc, result, compared = 0, 0, False
    window, locked, app, black, travelling = False, False, False, False, False
    stage = -1
    def read(fmt):
        nonlocal pc
        value = struct.unpack_from('<' + fmt, data, pc)[0]
        pc += struct.calcsize('<' + fmt)
        return value
    for _ in range(200):
        op = read('H')
        if op == 2:
            assert not window and not locked and not app
            return money, travelling
        if op == 45: read('B'); window = True
        elif op == 53: assert window; window = False
        elif op == 63: read('H'); result = int(decline)
        elif op == 112:
            read('H'); fare = read('I'); assert fare == 400
            result = int(money >= fare)
        elif op == 17: read('H'); compared = result == read('H')
        elif op == 28:
            condition, offset = read('B'), read('i')
            assert condition in (1,5)
            if compared == (condition == 1): pc += offset
        elif op == 22:
            offset = read('i'); pc += offset
        elif op == 208:
            assert read('B') == 6
            stage = read('H')
            if stage == 0:
                assert black and not window and not app
                app = True
            elif stage == 1:
                assert app
                app = False; result = int(selected)
            elif stage == 2:
                assert not black and not window and not app and selected
                money -= 400; travelling = True; result = 1
            else: raise AssertionError(stage)
        elif op == 150: assert stage == 1 and not app
        elif op == 174:
            read('H'); read('H'); direction = read('H'); read('H')
            black = direction == 0
        elif op == 73: read('H')
        elif op == 96: locked = True
        elif op == 97: locked = False
        elif op in (50,104,175): pass
        else: raise AssertionError((pc-2,op))
    raise AssertionError('script did not end')


def main():
    member = (ROOT / 'build/a012/2_233').read_bytes()
    handler, abra = body(member,6), body(member,7)
    assert handler == (ROOT / 'build/center_abra.bin').read_bytes()
    assert abra == (ROOT / 'build/center_abra_mon.bin').read_bytes()
    assert simulate(handler) == (600,True)
    assert simulate(handler,money=400) == (0,True)
    assert simulate(handler,money=399) == (399,False)
    assert simulate(handler,decline=True) == (1000,False)
    assert simulate(handler,selected=False) == (1000,False)
    print('OK: compiled Abra fare, exact/insufficient funds, refusal/map cancellation, paired message windows, map args consumed before field restore, departure after returning to field')


if __name__ == '__main__': main()
