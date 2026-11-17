#!/usr/bin/env python3
"""Host C checks for elemental stone thresholds, resolver item path, and menu labels."""
from pathlib import Path
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
    fixture = fixture.replace("/* REQUIREMENT_WRAPPER */", function(pokemon, "u8 LONG_CALL GetStoneLevelEvolutionRequirement("))
    fixture = fixture.replace("/* ITEM_RESOLUTION */", item)
    fixture = fixture.replace("/* MENU_LABEL */", function(menu, "void LONG_CALL PartyMenu_PrintEvoStoneCompatString("))
    with tempfile.TemporaryDirectory(prefix="stone_evolution_") as tmp:
        source = Path(tmp) / "test.c"
        binary = Path(tmp) / "test"
        source.write_text(fixture)
        subprocess.run(["gcc", "-std=c11", "-w", "-I", str(ROOT), "-I", str(ROOT / "include"), str(source), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)

if __name__ == "__main__":
    main()
