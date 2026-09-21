# Pokémon Wandering Heart

An open-world HeartGold/SoulSilver romhack built on [hg-engine](https://github.com/BluRosie/hg-engine).

## Documentation

| Document | What it covers |
| -------- | -------------- |
| **[DESIGN.md](DESIGN.md)** | Design index — vision, world, battles, wilds, story; what’s implemented vs planned |
| **[CHANGELOG.md](CHANGELOG.md)** | Player-facing changes vs vanilla HGSS |
| **[documentation/HACK-NOTES.md](documentation/HACK-NOTES.md)** | Implementation recipes, IDs, verified patches, msg banks |
| **`.cursor/rules/agents.mdc`** | **Coding agents:** Docker build, git rules, script layout (local Cursor config; not in git) |
| **[README (HG-Engine).md](README%20(HG-Engine).md)** | Upstream hg-engine setup (WSL, MSYS2, native `make`, Docker image build) |

### Design sub-documents

Linked from [DESIGN.md](DESIGN.md):

- [DESIGN-VISION.md](DESIGN-VISION.md) — core vision, starting city & starters
- [DESIGN-WORLD.md](DESIGN-WORLD.md) — travel, HMs, shops, ferries
- [DESIGN-WILDS.md](DESIGN-WILDS.md) — wild levels, fishing, ecology
- [DESIGN-BATTLES.md](DESIGN-BATTLES.md) — gyms, trainer scaling, EXP, healing
- [DESIGN-STORY.md](DESIGN-STORY.md) — story policy, vanilla cleanup
- [DESIGN-FUTURE.md](DESIGN-FUTURE.md) — deferred / parking-lot features

## Playtesting

The user loads **`test.nds`** (repo root) in DeSmuME. Agents regenerate it after ROM-affecting changes — see `.cursor/rules/agents.mdc`.

Place a clean **HeartGold** ROM named **`rom.nds`** in the repo root (never commit it).

## Credits

Upstream engine credits: [CREDITS.md](CREDITS.md) and [README (HG-Engine).md](README%20(HG-Engine).md).
