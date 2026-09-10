#!/usr/bin/env python3
"""Full inventory of scr_seq member 260 for Route 44 mapping."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "build/a012"
SCR_VANILLA = ROOT / "build/a012_vanilla"
ZONE = ROOT / "build/a032"
HDR = ROOT / "base/root/a/0/4/1"
TEXT_404 = ROOT / "data/text/404.txt"

# HGSS scr command names (partial) for readable dumps
OP_NAMES: dict[int, str] = {
    0: "end",
    17: "goto",
    20: "compare",
    22: "goto_if_eq",
    28: "goto_if_set",
    36: "goto_if_ge",
    37: "goto_if_le",
    40: "goto_if_ne",
    41: "goto_if",
    45: "npc_msg",
    125: "simple_npc_msg",
    128: "signpost",
}


def find_scrdef_end(data: bytes) -> tuple[int, int]:
    pos = 0
    count = 0
    while pos + 2 <= len(data) and pos < 512:
        if struct.unpack_from("<H", data, pos)[0] == 0xFD13:
            return pos, count
        count += 1
        pos += 4
    raise ValueError("scrdef_end not found")


def script_offset(data: bytes, index: int) -> int:
    word_pos = index * 4
    rel = struct.unpack_from("<i", data, word_pos)[0]
    return word_pos + 4 + rel


def slot_body(data: bytes, slot: int, count: int) -> bytes:
    start = script_offset(data, slot)
    if slot + 1 < count:
        end = script_offset(data, slot + 1)
    else:
        end = len(data)
    return data[start:end]


def scan_ops(body: bytes) -> list[tuple[int, str, object]]:
    out: list[tuple[int, str, object]] = []
    i = 0
    while i + 1 < len(body):
        op = struct.unpack_from("<H", body, i)[0]
        i += 2
        if op == 0:
            out.append((op, "end", None))
            break
        name = OP_NAMES.get(op, f"op_{op}")
        extra: object = None
        if op == 45 and i < len(body):
            extra = body[i]
            i += 1
        elif op in (17, 41, 40):
            extra = struct.unpack_from("<i", body, i)[0]
            i += 4
        elif op == 22:
            extra = struct.unpack_from("<H", body, i)[0]
            i += 4
        elif op == 28:
            extra = (body[i], struct.unpack_from("<H", body, i + 1)[0])
            i += 5
        elif op in (36, 37):
            extra = struct.unpack_from("<Hi", body, i)[0:2]
            i += 6
        elif op in (125, 128):
            extra = body[i]
            i += 6
        elif op == 20:
            extra = struct.unpack_from("<H", body, i)[0]
            i += 2
        else:
            i += 2
        out.append((op, name, extra))
    return out


def text_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("#"):
            continue
        lines.append(raw.replace("\\r", " ").replace("\\n", " / "))
    return lines


def parse_map_header(index: int) -> dict[str, int]:
    raw = HDR.read_bytes()
    off = index * 24
    b = raw[off : off + 24]
    wild, area = b[0], b[1]
    matrix, scripts, scripthdr, msg, daym, nightm, events = struct.unpack_from("<7H", b, 4)
    return {
        "wild": wild,
        "area": area,
        "matrix": matrix,
        "scripts": scripts,
        "script_header": scripthdr,
        "msg": msg,
        "events": events,
    }


def parse_zone_bgs(member: str) -> list[dict[str, int]]:
    data = (ZONE / f"2_{member}").read_bytes()
    bg_count = struct.unpack_from("<I", data, 0)[0]
    pos = 4
    out: list[dict[str, int]] = []
    for _ in range(bg_count):
        script, typ, x, z, y, dir_ = struct.unpack_from("<HHIIII", data, pos)
        out.append({"script": script, "type": typ, "x": x, "z": z, "y": y, "dir": dir_})
        pos += 20
    return out


def ensure_extract() -> None:
    if not (SCR_VANILLA / "2_260").is_file():
        subprocess.check_call(
            [sys.executable, str(ROOT / "tools/extract_scr_seq_vanilla.py"), str(SCR)]
        )
    if not (ZONE / "2_043").is_file():
        subprocess.check_call(
            [sys.executable, str(ROOT / "tools/extract_zone_event_vanilla.py"), str(ZONE)]
        )


def main() -> int:
    ensure_extract()

    vanilla_path = SCR_VANILLA / "2_260"
    built_path = SCR / "2_260"
    for label, path in (("vanilla", vanilla_path), ("built", built_path)):
        if not path.is_file():
            print(f"{label}: missing {path}")
            continue
        data = path.read_bytes()
        _, count = find_scrdef_end(data)
        print(f"\n{'=' * 60}")
        print(f"scr_seq member 260 ({label}): {count} scripts, {len(data)} bytes")
        print(f"{'=' * 60}")
        for slot in range(count):
            body = slot_body(data, slot, count)
            ops = scan_ops(body)
            msg_idxs = [x for op, name, x in ops if name in ("npc_msg", "simple_npc_msg", "signpost")]
            print(f"\n--- slot {slot} → scriptId {slot + 1} ({len(body)} bytes) ---")
            print(f"  msg indices: {msg_idxs}")
            preview = []
            for op, name, extra in ops[:12]:
                if extra is not None:
                    preview.append(f"{name}({extra})")
                else:
                    preview.append(name)
            if len(ops) > 12:
                preview.append("...")
            print(f"  flow: {' → '.join(preview)}")

    print("\n" + "=" * 60)
    print("Text bank 404 (msg index → line)")
    print("=" * 60)
    lines = text_lines(TEXT_404)
    for i, line in enumerate(lines):
        print(f"  [{i}] {line[:90]}{'…' if len(line) > 90 else ''}")

    print("\n" + "=" * 60)
    print("Map headers 44–48 (scriptsBank / eventsBank / msgBank)")
    print("=" * 60)
    for idx in range(44, 49):
        h = parse_map_header(idx)
        print(
            f"  MAP index {idx}: scripts={h['scripts']:3d} events={h['events']:3d} "
            f"msg={h['msg']:3d} matrix={h['matrix']:3d}"
        )

    print("\n" + "=" * 60)
    print("zone_event 043 bg events (signposts → scriptId)")
    print("=" * 60)
    for bg in parse_zone_bgs("043"):
        print(
            f"  scriptId={bg['script']:2d} type={bg['type']} at ({bg['x']},{bg['z']}) "
            f"y={bg['y']} dir={bg['dir']}"
        )

    print("\n" + "=" * 60)
    print("zone_event 043 objects using low scriptIds (type=0, script < 2000)")
    print("=" * 60)
    data = (ZONE / "2_043").read_bytes()
    pos = 4 + struct.unpack_from("<I", data, 0)[0] * 20
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    for _ in range(n):
        f = struct.unpack_from("<14H", data, pos)
        if f[3] == 0 and f[5] < 2000 and f[5] != 65535:
            print(
                f"  obj {f[0]:2d} ({f[12]:4d},{f[13]:3d}) script={f[5]:5d} "
                f"sprite={f[1]:4d}"
            )
        pos += 32

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
