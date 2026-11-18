#!/usr/bin/env python3
"""Host C checks for elemental stone thresholds, resolver item path, and menu labels."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]

def function(source, signature):
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]

def main():
    pokemon = (ROOT / "src/pokemon.c").read_text()
    menu = (ROOT / "src/party_menu.c").read_text()
    resolver = (ROOT / "src/individual/GetMonEvolutionInternal.c").read_text()
    item = resolver[resolver.index("        for (i", resolver.index("    case EVOCTX_ITEM_CHECK:")):]
    item = item[:item.index("#if defined(IMPLEMENT_LEVEL_CAP)")]
    fixture = (ROOT / "scripts/dev/verify_stone_level_evolution.c").read_text()
    species = (ROOT / "data/Species.c").read_text(encoding="utf-8")
    types = re.findall(r"\[(SPECIES_\w+)\] = \{.*?\.types = \{ (TYPE_\w+), (TYPE_\w+) \}", species, re.S)
    type_rows = "\n".join(f"    [{name}] = {{ {first}, {second} }}," for name, first, second in types)
    fixture = fixture.replace("/* PERSONAL_TYPES */", type_rows)
    fixture = fixture.replace("/* REQUIREMENT_WRAPPER */", function(pokemon, "u8 LONG_CALL GetStoneLevelEvolutionRequirement("))
    fixture = fixture.replace("/* ITEM_RESOLUTION */", item)
    level_cases = resolver[resolver.index("            case EVO_NONE:"):resolver.index("            case EVO_TRADE:")]
    level_cases += resolver[resolver.index("            case EVO_MAGNETIC_FIELD:"):resolver.index("            case EVO_LEVEL_DAY:")]
    level_cases += resolver[resolver.index("            case EVO_HAS_MOVE_TYPE:"):resolver.index("            case EVO_LEVEL_DARK_TYPE_MON_IN_PARTY:")]
    fixture = fixture.replace("/* EEVEE_LEVEL_CASES */", level_cases)
    fixture = fixture.replace("/* MENU_LABEL */", function(menu, "void LONG_CALL PartyMenu_PrintEvoStoneCompatString("))
    with tempfile.TemporaryDirectory(prefix="stone_evolution_") as tmp:
        source = Path(tmp) / "test.c"
        binary = Path(tmp) / "test"
        source.write_text(fixture)
        subprocess.run(["gcc", "-std=c11", "-w", "-I", str(ROOT), "-I", str(ROOT / "include"), str(source), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)

if __name__ == "__main__":
    main()
