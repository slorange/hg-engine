#!/usr/bin/env python3
"""Build tools/ecologygen (if needed) and run a test ecology assignment."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN_COMPAT = ROOT / "scripts/build/gen_ecology_compatibility.py"
ECOLOGYGEN_DIR = ROOT / "tools/source/ecologygen"
ECOLOGYGEN = ROOT / "tools/ecologygen"
DEFAULT_OUT = ROOT / "build/ecology/ecology_assignment.tsv"
DOCKER_IMAGE = "hg-engine"


def _use_docker() -> bool:
    from shutil import which

    if which("make") is None or which("gcc") is None:
        return which("docker") is not None
    return False


def _docker_run(workdir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    mount = f"{ROOT.as_posix()}:/hg-engine"
    inner = " ".join(args)
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            mount,
            "-w",
            f"/hg-engine/{workdir.relative_to(ROOT).as_posix()}",
            DOCKER_IMAGE,
            "bash",
            "-lc",
            inner,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def build_ecologygen() -> None:
    if _use_docker():
        proc = _docker_run(ECOLOGYGEN_DIR, "make")
    else:
        proc = subprocess.run(
            ["make"],
            cwd=ECOLOGYGEN_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run standalone ecology world generation (C core).")
    parser.add_argument("--seed", type=str, default="0xC0FFEE", help="World seed (hex or decimal)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output TSV path")
    parser.add_argument("--summary", action="store_true", help="Per-family placement summary instead of full slots")
    parser.add_argument("--skip-compat", action="store_true", help="Do not regenerate compat tables first")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of tools/ecologygen")
    args = parser.parse_args()
    if not args.out.is_absolute():
        args.out = ROOT / args.out

    if not args.skip_compat:
        proc = subprocess.run([sys.executable, str(GEN_COMPAT)], cwd=ROOT)
        if proc.returncode != 0:
            return proc.returncode

    if args.rebuild or not ECOLOGYGEN.is_file():
        build_ecologygen()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(ECOLOGYGEN), "--seed", args.seed, "--out", str(args.out)]
    if args.summary:
        cmd.append("--summary")

    if _use_docker():
        rel_out = args.out.relative_to(ROOT).as_posix()
        inner = f"./tools/ecologygen --seed {args.seed} --out {rel_out}"
        if args.summary:
            inner += " --summary"
        proc = _docker_run(ROOT, inner)
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
    else:
        proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode == 0:
        print(f"Wrote {args.out}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
