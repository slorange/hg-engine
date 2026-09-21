# Local scripts (not tracked)

Throwaway recon, one-off debugging, and session experiments live here. **Do not commit** contents of this folder.

When a script becomes reusable (referenced from `documentation/HACK-NOTES.md` / `.cursor/rules/agents.mdc` or wired into `Makefile` / `narcs.mk`), move it to `scripts/dev/` or `scripts/build/`.

Olivine recon leftovers (gitignored): `dump_msg_bank.py`, `_probe_map_header_fields.py` (wrong header layout — use pret `map_headers.h`).

Kanto ferry session leftovers: `dump_vanilla_slot_counts.py`, `find_flag_in_scr_seq.py`.

See `.cursor/rules/agents.mdc` § **Scripts layout**.
