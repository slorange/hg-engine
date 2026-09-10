#!/usr/bin/env python3
"""Analyze scr_seq member 260 contents for in-game mapping."""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR_V = ROOT / "build/a012_vanilla/2_260"
SCR_B = ROOT / "build/a012/2_260"
ZONE = ROOT / "build/a032/2_043"
ROM = ROOT / "rom.nds"


def slot_body(data: bytes, slot: int) -> tuple[bytes, int]:
    pos = 0
    count = 0
    while struct.unpack_from("<H", data, pos)[0] != 0xFD13:
        count += 1
        pos += 4
    start = struct.unpack_from("<i", data, slot * 4)[0] + slot * 4 + 4
    starts = [struct.unpack_from("<i", data, j * 4)[0] + j * 4 + 4 for j in range(count)]
    end = min((s for s in starts if s > start), default=len(data))
    return data[start:end], count


def scan_script(body: bytes) -> dict[str, object]:
    msgs: list[int] = []
    flags: list[int] = []
    ops: list[str] = []
    i = 0
    while i + 1 < len(body):
        op = struct.unpack_from("<H", body, i)[0]
        i += 2
        if op == 0:
            ops.append("end")
            break
        if op == 45:
            msgs.append(body[i])
            ops.append(f"npc_msg({body[i]})")
            i += 1
        elif op == 125:
            msgs.append(body[i])
            ops.append(f"simple_npc_msg({body[i]})")
            i += 6
        elif op == 128:
            msgs.append(body[i])
            ops.append("signpost")
            i += 6
        elif op == 28:
            flag = struct.unpack_from("<H", body, i + 1)[0]
            flags.append(flag)
            ops.append(f"goto_if_set(FLAG_{flag})")
            i += 5
        elif op in (17, 41, 40):
            ops.append(f"goto_if(op={op})")
            i += 4
        elif op == 22:
            ops.append("goto_if_eq")
            i += 4
        elif op in (36, 37):
            ops.append(f"compare(op={op})")
            i += 6
        elif op == 20:
            ops.append("compare_var")
            i += 2
        elif op == 1:
            ops.append("play_se")
            i += 2
        elif op == 2:
            ops.append("lockall")
            i += 2
        elif op == 3:
            ops.append("faceplayer")
            i += 2
        elif op == 4:
            ops.append("releaseall")
            i += 2
        elif op == 46:
            ops.append("wait_button_or_walk_away")
            i += 2
        elif op == 47:
            ops.append("closemsg")
            i += 2
        else:
            ops.append(f"op_{op}")
            i += 2
    return {"msgs": msgs, "flags": flags, "ops": ops}


def decode_msg_bank(bank: int) -> list[str]:
    try:
        import ndspy  # type: ignore
    except ImportError:
        return []

    if not ROM.is_file():
        return []

    rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))
    narc = ndspy.narc.NARC(rom.files[rom.filenames["a/0/2/7"]])
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bank.bin"
        out.write_bytes(narc.files[bank])
        subprocess.run(
            [str(ROOT / "tools/msgenc"), "-d", str(out)],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        txt = out.with_suffix(".txt")
        if txt.is_file():
            lines: list[str] = []
            for raw in txt.read_text(encoding="utf-8", errors="replace").splitlines():
                if raw.startswith("#"):
                    continue
                lines.append(raw.replace("\\r", " ").replace("\\n", " / "))
            return lines
    return []


def dump_member(label: str, path: Path) -> None:
    if not path.is_file():
        print(f"\n{label}: missing {path}")
        return

    data = path.read_bytes()
    _, count = slot_body(data, 0)
    print(f"\n{'=' * 70}")
    print(f"{label}: member 260 — {count} scripts, {len(data)} bytes")
    print(f"{'=' * 70}")
    for slot in range(count):
        body, _ = slot_body(data, slot)
        info = scan_script(body)
        print(f"\nSlot {slot} → scriptId {slot + 1}  ({len(body)} bytes)")
        print(f"  npc_msg indices: {info['msgs']}")
        if info["flags"]:
            print(f"  flag checks: {info['flags']}")
        op_line = " → ".join(info["ops"][:14])
        if len(info["ops"]) > 14:
            op_line += " → …"
        print(f"  flow: {op_line}")


def main() -> int:
    if not SCR_V.is_file():
        subprocess.check_call(
            [sys.executable, str(ROOT / "tools/extract_scr_seq_vanilla.py"), str(ROOT / "build/a012")]
        )

    dump_member("VANILLA (rom.nds)", SCR_V)
    dump_member("BUILT (if patched)", SCR_B)

    print(f"\n{'=' * 70}")
    print("Text bank 404")
    print(f"{'=' * 70}")
    vanilla_lines = decode_msg_bank(404)
    repo_lines = []
    repo_path = ROOT / "data/text/404.txt"
    if repo_path.is_file():
        for raw in repo_path.read_text(encoding="utf-8").splitlines():
            if not raw.startswith("#"):
                repo_lines.append(raw.replace("\\r", " ").replace("\\n", " / "))

    if vanilla_lines:
        print("Vanilla ROM lines:")
        for i, line in enumerate(vanilla_lines):
            print(f"  [{i}] {line[:100]}")
    if repo_lines:
        print("\nRepo data/text/404.txt (may include hack lines):")
        for i, line in enumerate(repo_lines):
            print(f"  [{i}] {line[:100]}")

    print(f"\n{'=' * 70}")
    print("zone_event 043 — what binds to scriptIds 1–5")
    print(f"{'=' * 70}")
    if ZONE.is_file():
        data = ZONE.read_bytes()
        pos = 4
        bg_n = struct.unpack_from("<I", data, 0)[0]
        print("\nBg events (signposts / hidden items):")
        for _ in range(bg_n):
            script, typ, x, z, y, dir_ = struct.unpack_from("<HHIIII", data, pos)
            note = ""
            if script in (1, 2, 3, 4, 5):
                note = f" ← scr_seq 260 slot {script - 1}"
            print(f"  scriptId {script:5d} type={typ} at ({x},{z}) dir={dir_}{note}")
            pos += 20

        pos = 4 + bg_n * 20
        obj_n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        print("\nObjects with scriptId 1–5 (would use map scr_seq if type=0):")
        found = False
        for _ in range(obj_n):
            f = struct.unpack_from("<14H", data, pos)
            if f[5] in (1, 2, 3, 4, 5):
                found = True
                print(
                    f"  obj {f[0]:2d} ({f[12]:4d},{f[13]:3d}) script={f[5]} "
                    f"type={f[3]} sprite={f[1]}"
                )
            pos += 32
        if not found:
            print("  (none — all NPCs use type=1 + scripts 3000+)")

    print(f"\n{'=' * 70}")
    print("In-game mapping cheat sheet")
    print(f"{'=' * 70}")
    print(
        """
scriptId 2 @ bg (634,171) → slot 1 → msgs 0+1 (Ice Path / Rt.44 signs)
scriptId 3 @ bg (552,178) → slot 2 → likely second sign handler (112B)
scriptId 8100 @ bg (613,171) type=2 → hidden item (not scr_seq 260)

slot 0 scriptId 1 (246B) → no dialogue; likely OnLoad / map init
slot 3 scriptId 4 (163B) → npc_msg 2 — check vanilla text [2] in-game
slot 4 scriptId 5 (128B) → npc_msg 5,6 + flag checks — vanilla NPC dialogue?

Bridge fisherman obj 1 uses script 3124 type=1 (common/trainer script bank),
NOT scr_seq 260. Same for all other walkable NPCs on member 043.
"""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
