#!/usr/bin/env python3
"""Compile and exercise the actual shared C stage selector (run in Docker/Linux)."""
import os
import argparse
import csv
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-generate", action="store_true", help="Check existing generated tables without rewriting them")
    args = parser.parse_args()
    learnsets = json.loads((ROOT / "data/learnsets/learnsets.json").read_text())
    with (ROOT / "data/synthetic_evolution_thresholds.tsv").open(encoding="utf-8") as source:
        edges = list(csv.DictReader(source, delimiter="\t"))
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("synthetic_generator", ROOT / "scripts/build/gen_synthetic_evo_edges.py")
    generator = module_from_spec(spec)
    spec.loader.exec_module(generator)
    moves = {"AncientPower": "ANCIENT_POWER", "Rollout": "ROLLOUT", "Double Hit": "DOUBLE_HIT",
             "Mimic": "MIMIC", "Psyshield Bash": "PSYSHIELD_BASH", "Rage Fist": "RAGE_FIST",
             "Twin Beam": "TWIN_BEAM", "Hyper Drill": "HYPER_DRILL"}
    for edge in edges:
        if edge["requirement"] in moves:
            species = generator.display_name_to_enum(edge["from"])
            move = "MOVE_" + moves[edge["requirement"]]
            levels = [entry["Level"] for entry in learnsets[species]["LevelMoves"] if entry["Move"] == move]
            assert levels == [int(edge["min_level"])], (species, move, levels, edge)
    print("PASS: move-known encounter thresholds match source learnsets.", flush=True)
    if not args.no_generate:
        subprocess.run(["python3", "scripts/build/gen_level_up_evo_tables.py"], cwd=ROOT, check=True)
        subprocess.run(["python3", "scripts/build/gen_synthetic_evo_edges.py"], cwd=ROOT, check=True)
    wild = (ROOT / "src/wild_level_caps.c").read_text()
    wild = wild[wild.index("// Encounter levels never"):wild.index("#ifdef DEBUG_WILD_LEVEL_CAP_LEVELS", wild.index("u8 RollWildLevel"))]
    trainers = (ROOT / "src/field/enemy_party.c").read_text()
    leader = trainers[trainers.index("static BOOL IsGymLeaderTrainerClass"):trainers.index("#if defined(TRAINER_SPECIES_STAGE_ADJUST)")]
    fixture = (ROOT / "scripts/dev/verify_encounter_stage.c").read_text()
    fixture = fixture.replace("/* ACTUAL_WILD_LEVEL_ROLL */", wild).replace("/* ACTUAL_TRAINER_CONTEXT */", leader)
    with tempfile.TemporaryDirectory(prefix="encounter_stage_") as tmp:
        source = Path(tmp) / "verify.c"
        binary = Path(tmp) / "verify"
        source.write_text(fixture)
        subprocess.run([os.environ.get("CC", "gcc"), "-std=c11", "-w", "-I", str(ROOT / "include"),
                        str(source), str(ROOT / "src/field/level_up_evo_tables.c"),
                        str(ROOT / "src/field/synthetic_evo_edges_data.c"), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    main()
