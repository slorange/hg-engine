"""Generate the base species in families with a friendship evolution."""

import re
import sys
from collections import defaultdict
from pathlib import Path

from gen_level_up_evo_tables import BLOCK_RE, EVOLUTIONS_C, ROOT

FRIENDSHIP_METHODS = {
    "EVO_FRIENDSHIP", "EVO_FRIENDSHIP_DAY", "EVO_FRIENDSHIP_NIGHT", "EVO_HAS_MOVE_TYPE",
}
EDGE_RE = re.compile(
    r"\{\s*(EVO_\w+)\s*,\s*[^,]+,\s*(?:MON_WITH_FORM\(\s*)?(SPECIES_\w+)"
)


def main(output: Path):
    forms = dict(re.findall(
        r"\[(SPECIES_\w+) - SPECIES_\w+\]\s*=\s*(SPECIES_\w+)",
        (ROOT / "data/FormToSpeciesMapping.c").read_text(encoding="utf-8"),
    ))
    text = EVOLUTIONS_C.read_text(encoding="utf-8")
    blocks = list(BLOCK_RE.finditer(text))
    neighbors = defaultdict(set)
    pending = set()
    for i, block in enumerate(blocks):
        source = forms.get(block[1], block[1])
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        for method, target in EDGE_RE.findall(text[block.end():end]):
            if method == "EVO_NONE" or target == "SPECIES_NONE":
                continue
            target = forms.get(target, target)
            neighbors[source].add(target)
            neighbors[target].add(source)
            if method in FRIENDSHIP_METHODS:
                pending.add(source)

    family = set()
    while pending:
        species = pending.pop()
        family.add(species)
        pending.update(neighbors[species] - family)

    generated = "// Generated from the player evolution table.\n"
    generated += "".join(f"    {species},\n" for species in sorted(family))
    output.write_text(generated, encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
