#!/usr/bin/env python3
"""Verify NPC/script preservation and exercise the compiled cash-payment flow."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/build"))
from patch_center_relearner import relearner_object
from patch_center_apricorn import craft_objects
from patch_center_abra import abra_objects
from center_service_checks import body as slot_body, table
from patch_zone_event_r32pc_rod_guru import parse_zone_event


def simulate(body, *, money=1000, decline=False, slot=0, species=25, eligible=1, result=0):
    pc, compared, locked, taught, charges = 0, False, False, 0, []
    window_open = False
    variables, messages = {}, []

    def read(fmt):
        nonlocal pc
        value = struct.unpack_from("<" + fmt, body, pc)[0]
        pc += struct.calcsize("<" + fmt)
        return value

    for _ in range(200):
        op = read("H")
        if op == 2:  # End
            assert not locked
            return money, taught, charges, messages
        if op == 17:  # Compare variable to literal
            var, value = read("H"), read("H")
            compared = variables[var] == value
        elif op == 22:
            offset = read("i")
            pc += offset
        elif op == 28:
            condition, offset = read("B"), read("i")
            assert condition in (1, 5)
            if compared == (condition == 1):
                pc += offset
        elif op == 45:
            messages.append(read("B"))
            window_open = True
        elif op == 63:
            variables[read("H")] = int(decline)
        elif op == 73:
            read("H")
        elif op == 96:
            locked = True
        elif op == 97:
            locked = False
        elif op == 111:
            cost = read("I")
            assert taught == 1, "charged before a successful move"
            charges.append(cost)
            money -= cost
        elif op == 112:
            var, cost = read("H"), read("I")
            variables[var] = int(money >= cost)
        elif op == 174:
            for _ in range(4):
                read("H")
        elif op == 351:
            variables[read("H")] = slot
        elif op == 354:
            read("H")
            variables[read("H")] = species
        elif op == 466:
            var = read("H")
            read("H")
            variables[var] = eligible
        elif op == 467:
            read("H")
            taught += int(result == 0)
        elif op == 469:
            variables[read("H")] = result
        elif op == 53:
            assert window_open, "CloseMsg after returning from an application without reopening the window"
            window_open = False
        elif op == 150:
            window_open = False
        elif op in (50, 104, 175, 349):
            pass
        else:
            raise AssertionError(f"unexpected opcode {op} at {pc - 2}")
    raise AssertionError("script did not terminate")


def main():
    vanilla = (ROOT / "build/a012_vanilla/2_233").read_bytes()
    current = (ROOT / "build/a012/2_233").read_bytes()
    fd, starts = table(current)
    shift = fd - 16
    assert current[fd:len(vanilla) + shift] == vanilla[16:], "original code changed"
    for slot in range(4):
        assert struct.unpack_from("<i", current, slot * 4)[0] == struct.unpack_from("<i", vanilla, slot * 4)[0] + shift
    assert starts[4] == len(vanilla) + shift
    body = slot_body(current, 4)
    assert body == (ROOT / "build/center_relearner.bin").read_bytes()
    assert simulate(body)[:3] == (700, 1, [300])
    assert simulate(body, money=300)[:3] == (0, 1, [300])
    for options in ({"decline": True}, {"slot": 255}, {"species": 0},
                    {"eligible": 0}, {"result": 255}):
        assert simulate(body, **options)[:3] == (1000, 0, [])
    assert simulate(body, money=299)[:3] == (299, 0, [])
    original = parse_zone_event((ROOT / "build/a032_vanilla/2_163").read_bytes())
    events = parse_zone_event((ROOT / "build/a032/2_163").read_bytes())
    assert events[1] == craft_objects([o for o in original[1] if struct.unpack_from("<H", o)[0] not in (4, 5)] + [relearner_object()]) + abra_objects()
    assert (events[0], events[2], events[3]) == (original[0], original[2], original[3])
    assert len((ROOT / "data/text/381.txt").read_text(encoding="utf-8").splitlines()) == 38
    print("OK: Center relearner NPC; message-window lifecycle; original scripts/warps preserved; $300 only on success; exact funds, insufficient funds, refusal, party/move cancellation, Egg and no-moves paths")


if __name__ == "__main__":
    main()
