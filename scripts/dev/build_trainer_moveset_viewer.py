"""Refresh embedded ROM tables and selector in trainer_moveset_viewer.html.

Requires a built hg-engine checkout and clang/wasm-ld. A running Docker
container with those tools can be selected with --docker-container.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
VIEWER = ROOT / "scripts/dev/trainer_moveset_viewer.html"

BRIDGE = r"""
#include "types.h"
#undef THUMB_FUNC
#define THUMB_FUNC

#include "battle.h"
#include "pokemon.h"

#define EXPORT(name) __attribute__((export_name(name)))

static struct PartyPokemon party[6];
static struct {
    u16 species, moves[4], heldItem;
    u8 level, type1, type2, ev[6], baseIV[6], iv[6];
} previewMon[6];
static u32 rng, selectionSeed;

static void SetGeneratedTrainerEVs(struct PartyPokemon *mon, u8 badges, BOOL gymLeader);
static void UpgradeGeneratedTrainerIVs(struct PartyPokemon **members, int count, u8 badges, BOOL gymLeader);
void SetGeneratedTrainerHeldItem(struct PartyPokemon *mon, u8 badges);

extern void HostReadMove(int move, void *dest);
extern void HostReadLearnset(int species, void *dest, int count);
extern int HostCompatible(int species, int index);
extern int HostMachineMove(int index);
extern void HostSetMove(int mon, int slot, int move);
extern void HostInventory(u8 *copies, int count);
extern void HostCandidate(int mon, int move, int score, int type, int tm, u32 groupMask, int utilityAttackScore);
extern void HostStat(int mon, int stat, int ev, int baseIV, int iv);
extern void HostHeldItem(int mon, int item);

u16 gf_rand(void)
{
    rng = rng * 0x41C64E6Du + 0x6073u;
    return rng >> 16;
}

u32 GetMonData(struct PartyPokemon *mon, int field, void *unused)
{
    int i = mon - party;
    if (field >= MON_DATA_MOVE1 && field <= MON_DATA_MOVE4) {
        return previewMon[i].moves[field - MON_DATA_MOVE1];
    }
    if (field >= MON_DATA_HP_IV && field <= MON_DATA_SPDEF_IV) {
        return previewMon[i].iv[field - MON_DATA_HP_IV];
    }
    switch (field) {
    case MON_DATA_SPECIES: return previewMon[i].species;
    case MON_DATA_LEVEL: return previewMon[i].level;
    case MON_DATA_TYPE_1: return previewMon[i].type1;
    case MON_DATA_TYPE_2: return previewMon[i].type2;
    default: return 0; // preview inputs use base form
    }
}

void SetMonData(struct PartyPokemon *mon, int field, void *value)
{
    int i = mon - party;
    if (field >= MON_DATA_HP_EV && field <= MON_DATA_SPDEF_EV) {
        previewMon[i].ev[field - MON_DATA_HP_EV] = *(const u8 *)value;
    } else if (field >= MON_DATA_HP_IV && field <= MON_DATA_SPDEF_IV) {
        previewMon[i].iv[field - MON_DATA_HP_IV] = *(const u8 *)value;
    } else if (field == MON_DATA_HELD_ITEM) {
        previewMon[i].heldItem = *(const u16 *)value;
    }
}

void ReadWholeNarcMemberByIdPair(void *dest, int archive, int move)
{
    HostReadMove(move, dest);
}

void LoadLevelUpLearnset_HandleAlternateForm(int species, int form, u32 *learnset)
{
    HostReadLearnset(species, learnset, MAX_LEVELUP_MOVES);
}

BOOL GetTMHMCompatBySpeciesAndForm(u16 species, u16 form, u8 index)
{
    return HostCompatible(species, index);
}

u16 ItemToMachineMove(u16 itemId)
{
    return HostMachineMove(itemId - ITEM_TM001);
}

void SetPartyPokemonMoveAtPos(struct PartyPokemon *mon, u16 move, u8 slot)
{
    previewMon[mon - party].moves[slot] = move;
    HostSetMove(mon - party, slot, move);
}

void ClearMonMoves(struct PartyPokemon *mon)
{
    for (u8 slot = 0; slot < 4; slot++) {
        SetPartyPokemonMoveAtPos(mon, 0, slot);
    }
}

EXPORT("setMon") void SetPreviewMon(int i, int species, int level, int type1, int type2)
{
    previewMon[i].species = species;
    previewMon[i].level = level;
    previewMon[i].type1 = type1;
    previewMon[i].type2 = type2;
}

EXPORT("run") void RunPreview(int badges, int count, u32 inventorySeed, u32 moveSeed, int gymLeader)
{
    struct PartyPokemon *members[6];
    int order[6];
    // Separate initial IV rolls keep existing move and inventory seeds replayable.
    rng = moveSeed ^ 0xA511E9B3u;
    for (int i = 0; i < count; i++) {
        members[i] = &party[i];
        order[i] = i;
        for (int stat = 0; stat < 6; stat += 3) {
            u16 roll = gf_rand();
            for (int j = 0; j < 3; j++) {
                u8 iv = (roll >> (j * 5)) & 31;
                previewMon[i].baseIV[stat + j] = iv;
                previewMon[i].iv[stat + j] = iv;
            }
        }
        SetGeneratedTrainerEVs(members[i], badges, gymLeader);
    }
    rng = inventorySeed;
    selectionSeed = moveSeed;
    BuildGeneratedTrainerMovesets(members, order, count, badges);
    UpgradeGeneratedTrainerIVs(members, count, badges, gymLeader);
    for (int i = 0; i < count; i++) {
        SetGeneratedTrainerHeldItem(members[i], badges);
        HostHeldItem(i, previewMon[i].heldItem);
        for (int stat = 0; stat < 6; stat++) {
            HostStat(i, stat, previewMon[i].ev[stat], previewMon[i].baseIV[stat], previewMon[i].iv[stat]);
        }
    }
}
"""


def instrumented_source() -> str:
    source = (ROOT / "src/field/trainer_moves.c").read_text(encoding="utf-8")
    # Insert observation hooks in the browser build only. The original
    # selection loops and tables are compiled verbatim into WebAssembly.
    anchors = {
        "    ClearMonMoves(mon);": """
    for (int i = 0; i < count; i++) {
        const struct TrainerMoveCandidate *candidate = &pool[i];
        HostCandidate(mon - party, candidate->move, candidate->score, candidate->type,
            candidate->tm, candidate->groupMask, candidate->utilityAttackScore);
    }
    ClearMonMoves(mon);""",
        "    for (int i = count - 1; i >= 0; i--) {": """
    HostInventory(tmCopies, TRAINER_TM_COUNT);
    rng = selectionSeed;
    for (int i = count - 1; i >= 0; i--) {""",
    }
    for anchor, replacement in anchors.items():
        if source.count(anchor) != 1:
            raise ValueError(f"Trainer selector trace point changed: {anchor}")
        source = source.replace(anchor, replacement)
    enemy_party = (ROOT / "src/field/enemy_party.c").read_text(encoding="utf-8")
    stat_rules = []
    for function in ("SetGeneratedTrainerEVs", "UpgradeGeneratedTrainerIVs"):
        match = re.search(rf"^static void {function}\(.*?^\}}", enemy_party, re.M | re.S)
        if not match:
            raise ValueError(f"Missing generated trainer stat rule: {function}")
        stat_rules.append(match[0])
    items = (ROOT / "src/field/trainer_items.c").read_text(encoding="utf-8")
    return (
        '#include "constants/item.h"\n#include "constants/generated/learnsets.h"\n'
        "struct PartyPokemon;\n"
        "void BuildGeneratedTrainerMovesets(struct PartyPokemon **party, const int *order, int count, unsigned char badges);\n"
        + BRIDGE + source + "\n" + "\n".join(stat_rules) + "\n" + items
    )


def compile_selector(clang: str, container: str | None) -> bytes:
    flags = [
        "--target=wasm32", "-Oz", "-ffreestanding", "-fno-builtin",
        "-Wno-unknown-attributes", "-Wno-ignored-attributes", "-nostdlib",
        "-Wl,--no-entry", "-Wl,--allow-undefined",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)
        source = directory / "selector.c"
        source.write_text(instrumented_source(), encoding="utf-8")
        if container is None:
            output = directory / "selector.wasm"
            subprocess.run([clang, *flags, "-I", str(ROOT / "include"), str(source), "-o", str(output)], check=True)
            return output.read_bytes()
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as package:
            package.add(ROOT / "include", "include")
            package.add(source, "selector.c")
        command = (
            'set -eu; work=$(mktemp -d); trap \'rm -rf "$work"\' EXIT; '
            'tar -xzf - -C "$work"; cd "$work"; '
            'clang "$@" -I include selector.c -o selector.wasm; cat selector.wasm'
        )
        return subprocess.run(
            ["docker", "exec", "-i", container, "sh", "-c", command, "sh", *flags],
            input=archive.getvalue(), stdout=subprocess.PIPE, check=True,
        ).stdout


def constants(path: str, prefix: str) -> dict[str, int]:
    text = (ROOT / path).read_text(encoding="utf-8")
    return {key: int(value) for key, value in re.findall(rf"^#define\s+({prefix}\w+)\s+(\d+)\b", text, re.M)}


def pack(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def catalog() -> dict:
    species_ids = constants("include/constants/species.h", "SPECIES_")
    move_ids = constants("include/constants/moves.h", "MOVE_")
    counts = constants("include/constants/generated/learnsets.h", "")
    species_text = (ROOT / "data/Species.c").read_text(encoding="utf-8")
    species_names = dict(re.findall(
        r'^    \[(SPECIES_\w+)\] = \{\s*\.textData = \{\s*\.name = "([^"]+)"', species_text, re.M
    ))
    moves_text = (ROOT / "data/Moves.c").read_text(encoding="utf-8")
    move_names = dict(re.findall(
        r'^    \[(MOVE_\w+)\] = \{\s*\.names = \{[^}]*\.fullName = "([^"]+)"', moves_text, re.M
    ))
    scope = {key: number for key, number in species_ids.items() if 1 <= number <= 493}
    scope.update({
        "SPECIES_" + key: species_ids["SPECIES_" + key]
        for key in "SYLVEON KLEAVOR WYRDEER URSALUNA ANNIHILAPE FARIGIRAF DUDUNSPARCE LARVESTA VOLCARONA".split()
    })
    assert len(scope) == 502
    species = []
    for key, number in sorted(scope.items(), key=lambda pair: pair[1]):
        personal = (ROOT / f"build/a002/mondata_{number:04d}").read_bytes()
        excluded = number in (151, 201, 235, 251) or any(
            first <= number <= last for first, last in ((144,146),(150,151),(243,245),(249,251),(377,386),(480,493))
        )
        species.append([number, species_names.get(key, key[8:].title()), personal[6], personal[7], not excluded])
    machine_table = (ROOT / "src/item.c").read_text(encoding="utf-8").split("sMachineMoves[] = {", 1)[1].split("};", 1)[0]
    machine = [move_ids[key] for key in re.findall(r"^\s*(MOVE_\w+),", machine_table, re.M)][:100]
    assert len(machine) == 100
    selector = (ROOT / "src/field/trainer_moves.c").read_text(encoding="utf-8")
    hm_gates = [int(badge) for badge in re.search(r"hmBadges\[TRAINER_HM_COUNT\] = \{([^}]+)\}", selector)[1].split(",")]
    assert len(hm_gates) == 8
    move_files = sorted((ROOT / "build/a011").glob("1_*"))
    move_data = bytearray(16 * (max(int(p.name[2:]) for p in move_files) + 1))
    for path in move_files:
        index = int(path.name[2:])
        data = path.read_bytes()
        assert len(data) == 16, path
        move_data[index * 16:(index + 1) * 16] = data
    item_ids = constants("include/constants/item.h", "ITEM_")
    item_selector = (ROOT / "src/field/trainer_items.c").read_text(encoding="utf-8")
    item_keys = sorted(set(re.findall(r"\bITEM_\w+", item_selector)))
    item_names = {"ITEM_KINGS_ROCK": "King’s Rock", "ITEM_NEVER_MELT_ICE": "Never-Melt Ice"}
    return {
        "species": species,
        "moveNames": {number: move_names.get(key, key[5:].replace("_", " ").title()) for key, number in move_ids.items()},
        "itemNames": {item_ids[key]: item_names.get(key, key[5:].replace("_", " ").title()) for key in item_keys},
        "machines": machine,
        "hmBadges": hm_gates,
        "learnsetStride": counts["MAX_LEVELUP_MOVES"] * 4,
        "compatStride": ((counts["NUM_MACHINE_MOVES"] + 31) // 32) * 4,
        "learnsets": pack((ROOT / "build/a033/LevelupLearnsets.bin").read_bytes()),
        "compat": pack((ROOT / "build/MachineMoveLearnsets.bin").read_bytes()),
        "moveData": pack(move_data),
    }


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--clang", default="clang")
    args.add_argument("--docker-container", help="Use clang and wasm-ld in an already running container.")
    options = args.parse_args()
    data = json.dumps(catalog(), ensure_ascii=True, separators=(",", ":")).replace("<", r"\u003c")
    wasm = pack(compile_selector(options.clang, options.docker_container))
    html = VIEWER.read_text(encoding="utf-8")
    for element, payload in (("rom-data", data), ("selector-wasm", wasm)):
        pattern = rf'(<script id="{element}" type="application/octet-stream">).*?(</script>)'
        html, count = re.subn(pattern, lambda m: m[1] + payload + m[2], html, flags=re.S)
        if count != 1:
            raise ValueError(f"Missing or duplicate payload element: {element}")
    VIEWER.write_text(html, encoding="utf-8")
    print(f"Updated {VIEWER}")


if __name__ == "__main__":
    main()
