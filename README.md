# Pokémon Wandering Heart

An open-world HeartGold/SoulSilver romhack built on [hg-engine](https://github.com/BluRosie/hg-engine).

## Documentation

| Document | What it covers |
| -------- | -------------- |
| **[DESIGN.md](DESIGN.md)** | Design index — vision, world, battles, wilds, story; what’s implemented vs planned |
| **[CHANGELOG.md](CHANGELOG.md)** | Player-facing changes vs vanilla HGSS |
| **[TODO.md](TODO.md)** | Release blockers (bugs, cleanup, Gym gates) — not Future scope |
| **[documentation/HACK-NOTES.md](documentation/HACK-NOTES.md)** | Implementation recipes, IDs, verified patches, msg banks |
| **`.cursor/rules/agents.mdc`** | **Coding agents:** Docker build, git rules, script layout |
| **[README (HG-Engine).md](README%20(HG-Engine).md)** | Upstream hg-engine setup (WSL, MSYS2, native `make`, Docker image build) |

### Design sub-documents

Linked from [DESIGN.md](DESIGN.md):

- [DESIGN-WORLD.md](DESIGN-WORLD.md) — open-world principles, travel, HMs, shops, ferries
- [DESIGN-WILDS.md](DESIGN-WILDS.md) — wild levels, fishing, ecology
- [DESIGN-BATTLES.md](DESIGN-BATTLES.md) — fair trainer fights, badge caps, Gyms, EXP
- [DESIGN-STORY.md](DESIGN-STORY.md) — intro (Story-1/2), script policy (Story-3); release work in [TODO.md](TODO.md)
- [DESIGN-FUTURE.md](DESIGN-FUTURE.md) — deferred / parking-lot features

## Playtesting

The user loads **`test.nds`** (repo root) in DeSmuME. Agents regenerate it after ROM-affecting changes — see `.cursor/rules/agents.mdc`.

Place a clean **HeartGold** ROM named **`rom.nds`** in the repo root (never commit it).

## Credits

Upstream engine credits: [CREDITS.md](CREDITS.md) and [README (HG-Engine).md](README%20(HG-Engine).md).
