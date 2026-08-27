#!/usr/bin/env python3
"""Verify Mom patches made it into scr_seq.narc and/or test.nds."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
if not PYTHON.is_file():
    PYTHON = Path(sys.executable)
sys.path.insert(0, str(ROOT / "tools"))

from patch_scr_seq_t20_mom import extract_scripts  # noqa: E402

GIVE_ITEM = bytes.fromhex("f107")
EARLY_SETVAR = bytes.fromhex("290006410100")
COMPARE_SCENE = bytes.fromhex("110006410000")
VANILLA_ONFRAME_LOOP = bytes.fromhex("064100000100")


def member_path(out_dir: Path, index: int) -> Path:
    for name in (f"2_{index:03d}", f"2_{index}", f"scr_seq.narc_{index}"):
        path = out_dir / name
        if path.is_file():
            return path
    matches = sorted(out_dir.glob(f"*_{index}"))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError(f"missing scr_seq member {index} in {out_dir}")


def extract_narc_member(narc: Path, out_dir: Path) -> tuple[bytes, bytes]:
    subprocess.check_call(
        [str(PYTHON), str(ROOT / "tools/narcpy.py"), "extract", str(narc), "-o", str(out_dir), "-nf"],
        cwd=ROOT,
    )
    return member_path(out_dir, 618).read_bytes(), member_path(out_dir, 845).read_bytes()


def vanilla_hdr() -> bytes:
    path = ROOT / "build/a012_vanilla/2_618"
    if not path.is_file():
        raise FileNotFoundError("missing build/a012_vanilla/2_618")
    return path.read_bytes()


def check_pair(h618: bytes, h845: bytes, label: str) -> list[str]:
    errors: list[str] = []
    ref = vanilla_hdr()
    if h618 != ref:
        errors.append(f"{label}: header 618 not vanilla ({h618.hex()})")
    elif VANILLA_ONFRAME_LOOP not in h618:
        errors.append(f"{label}: header 618 missing OnFrame var==0 row")
    else:
        print(f"{label}: init header 618 ok (vanilla OnFrame)")

    body = extract_scripts(h845)[0]
    if COMPARE_SCENE not in body[:20]:
        errors.append(f"{label}: script 0 missing scene compare")
    if EARLY_SETVAR not in body[:32]:
        errors.append(f"{label}: script 0 missing early setvar (OnFrame loop guard)")
    if body.count(GIVE_ITEM) < 3:
        errors.append(f"{label}: script 0 missing item grants")
    if body[-8:] != b"\x00" * 8:
        errors.append(f"{label}: script 0 tail not zero-padded")
    if not errors:
        print(f"{label}: script 845 ok ({len(body)} bytes, early setvar + grants)")
    return errors


def check_path(path: Path) -> list[str]:
    if path.suffix == ".narc":
        with tempfile.TemporaryDirectory(prefix="mom_narc_") as tmp:
            h618, h845 = extract_narc_member(path, Path(tmp))
            return check_pair(h618, h845, str(path))
    if path.suffix == ".nds":
        with tempfile.TemporaryDirectory(prefix="mom_rom_") as tmp:
            fs = Path(tmp) / "root"
            fs.mkdir()
            subprocess.check_call(
                [str(ROOT / "tools/ndstool"), "-x", str(path), "-d", str(fs)],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            narc = fs / "a/0/1/2"
            if not narc.is_file():
                return [f"{path}: no embedded a/0/1/2 filesystem"]
            with tempfile.TemporaryDirectory(prefix="mom_fs_") as tmp2:
                h618, h845 = extract_narc_member(narc, Path(tmp2))
                return check_pair(h618, h845, str(path))
    return [f"unsupported path {path}"]


def main() -> int:
    try:
        vanilla_hdr()
    except FileNotFoundError as exc:
        print(exc)
        return 1

    candidates = [
        ROOT / "build/a012",
        ROOT / "build/narc/scr_seq.narc",
        ROOT / "test.nds",
    ]
    errors: list[str] = []
    checked = False
    for path in candidates:
        if path.is_dir():
            h618 = path / "2_618"
            h845 = path / "2_845"
            if h618.is_file() and h845.is_file():
                errors.extend(check_pair(h618.read_bytes(), h845.read_bytes(), str(path)))
                checked = True
        elif path.is_file():
            errors.extend(check_path(path))
            checked = True
        else:
            print(f"skip missing {path.relative_to(ROOT)}")

    if not checked:
        print("nothing to verify")
        return 1

    if errors:
        print("\nFAILED:")
        for err in errors:
            print(f" - {err}")
        print("\nQuick rebuild:\n  make scr_seq_clean && make -j24")
        return 1

    print("\nPatches are present in all checked artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
