# Agents: build, git, and repo workflow

Instructions for **coding agents** working on **Pokémon Wandering Heart** (this hg-engine fork). Implementation recipes and ROM IDs live in [HACK-NOTES.md](HACK-NOTES.md). Design specs: [DESIGN.md](../DESIGN.md).

**New agent session?** Read this file before changing game files.

## Contents

| Topic | Section |
| ----- | ------- |
| Git rules | [Git (agents)](#git-agents) |
| Python script buckets | [Scripts layout](#scripts-layout) |
| Build handoff rule | [Agents: always build](#agents-always-build-user-does-not) |
| Docker / `make` | [Build and verification](#build-and-verification) → [How to build](#how-to-build-this-fork), [Build types](#build-types), [Full build scope](#what-a-full-build-covers-roughly) |
| Find dialogue | [Quick “find this dialogue” checklist](#quick-find-this-dialogue-checklist) |

## Git (agents)

**Read-only only.** Agents may run git commands that **inspect** state (`status`, `diff`, `log`, `show`, etc.). **Never commit, push, merge, rebase, reset, checkout, add, stash, or any other mutating git action** — the user handles all of that themselves. If they say they’re committing, they mean they will do it; don’t beat them to it.

## Scripts layout

Python helpers live under `scripts/` in three buckets. **Keep new scripts in the right bucket** so `scripts/local/` can stay gitignored.

| Folder | Track in git? | When to use |
|--------|---------------|-------------|
| `scripts/build/` | Yes | Wired into `Makefile`, `narcs.mk`, `overlays.mk`, or `data/codetables.mk` |
| `scripts/dev/` | Yes | Reusable inspect/verify helpers referenced from HACK-NOTES or wiki docs |
| `scripts/local/` | **No** | One-off recon, session experiments, throwaway debugging |

**Rules for agents:**

- New recon or “figure this out once” scripts → `scripts/local/` (prefix with `_` when possible).
- When a script becomes reusable, move it to `dev/` or `build/` and update Makefile/docs references.
- Do **not** add Makefile hooks for `local/` scripts.
- `scripts/fixed/` is unrelated metadata (monData numbering) — leave it alone.

See [`scripts/README.md`](../scripts/README.md) for the inventory.

## Agents: always build (user does not)

**The user does not build this project.** They are not set up to run Docker, `make`, or MSYS2/WSL for day-to-day work. **You must build for them** whenever you change anything that affects the ROM.

**Rule:** If you edited C/asm, armips scr_seq, `data/text/`, zone_event JSON, `include/config.h`, NARC patchers, or similar — **run a full build and produce `test.nds` before you finish.** Do not hand off source-only changes and expect the user to compile.

**Do not run `tools/armips` or other build tools natively on Windows** — they are meant to run inside the Docker/Linux build environment. Use Docker `make` below.

**User testing workflow:** load **`test.nds`** (repo root) in DeSmuME. That file *is* the deliverable. Use a **new save** after intro/flag/starting-city changes.

**Agent build command** (this machine, repo at `e:\Code\hg-engine`):

```bat
docker run --rm -v "e:/Code/hg-engine:/hg-engine" -w /hg-engine hg-engine make -j24
```

**One-time Docker image** (only if `hg-engine` image is missing or Dockerfile changed):

```bat
docker build -t hg-engine e:\Code\hg-engine
```

Interactive shell (optional): run `docker-makerom.cmd` from the repo root, then `make -j24` inside the container.

If the build fails, say so explicitly — do not imply the user can test your edits without a successful build.

See **[Build and verification](#build-and-verification)** below for build types, outputs, and troubleshooting.

## Build and verification

| File | Role |
|------|------|
| `rom.nds` | User-provided base ROM (input). **Never commit.** |
| `test.nds` | **Playable build output** — user loads this in DeSmuME. **Never commit.** Agents must regenerate it after ROM-affecting changes. |
| `build/` | Intermediate artifacts (NARCs, objects, extracted vanilla). Regenerated; do not commit. |

### How to build (this fork)

**Use Docker on this machine** — native MSYS2/UCRT64 linking has been unreliable with hg-engine’s dual linker scripts.

**Default (agents):** full ROM, non-interactive:

```bat
docker run --rm -v "e:/Code/hg-engine:/hg-engine" -w /hg-engine hg-engine make -j24
```

**One-time image:** `docker build -t hg-engine e:\Code\hg-engine`

**Interactive:** `./docker-makerom.cmd` from repo root, then `make -j24` inside the container.

Upstream native/WSL/MSYS2 setup (without Docker): [README (HG-Engine).md](../README%20(HG-Engine).md).

**Notes:**

- Do **not** commit `rom.nds` or `test.nds`.
- First Docker build on a dirty tree can be slow; text-only rebuilds are faster.
- If MSYS-built object files cause trouble, clear `tools/source/**/*.o` before Docker `make`.
- After text/scr_seq/zone_event edits, close the emulator and reload **`test.nds`** — don’t reuse a stale file from an old build.

### Build types

| Command | Use when | Output / notes |
|---------|----------|----------------|
| `make -j24` | Default — verify any change end-to-end | Full **`test.nds`**: C/asm (`src/`, `asm/`), `data/*.c`, armips, NARC rebuild, overlays |
| `make build/narc/scr_seq.narc build/narc/zone_event.narc NOSCAN=1` | Iterating on scr_seq / zone_event only | NARCs only; still repack `test.nds` before in-game test |
| `make scr_seq_clean && make -j24` | Suspect scr_seq corruption or duplicate NPCs after patch | Clears scr_seq build artifacts, then full rebuild |
| `make clean_code && make -j24` | C/asm changed but objects seem stale | Drops compiled code objects only |
| `make clean && make -j24` | Broken build state, tool rebuild, or “nothing makes sense” | Full clean (slow) |
| `make AUTO_TEST=Y -j24` | Battle-engine automated tests | Same **`test.nds`** name, compiled with `DEBUG_BATTLE_SCENARIOS`; see [data/battle_tests/README.md](../data/battle_tests/README.md) |
| `make restore_build` | Reset extracted `base/` from `rom.nds` then rebuild | Nuclear reset of extracted filesystem |

**`NOSCAN=1`** skips dependency scanning — use for targeted NARC targets to save time; not a substitute for a full verify before calling something done.

**Compile toggles** (`HEAL_AFTER_BATTLE`, trainer scaling, open-world grants, etc.) live in `include/config.h` and `armips/include/config.s` — documented in [CONFIG.md](../CONFIG.md) and [Index-2](../DESIGN.md#index-2-current-technical-baseline).

### What a full build covers (roughly)

1. **Tools** — armips, nitrogfx, msgenc, ndstool, patch scripts, …
2. **Generated data** — species/move/trainer text banks, learnsets, evo tables, …
3. **NARCs** — encounters, scr_seq, zone_event, sprites, msgdata overrides from `data/text/`, …
4. **Engine code** — `src/` + overlays linked into `base/`
5. **Pack** — `test.nds` from `rom.nds` + modified `base/root/`

Field-script recipes in [HACK-NOTES.md](HACK-NOTES.md) often add Python **verify_*.py** scripts — run those after the relevant `make` when listed.

## Quick “find this dialogue” checklist

1. `rg` / search in `data/text/` and `data/*.c` (trainer speech lives in `data/Trainers.c`).
2. If missing: scan decoded msgdata banks (Docker + `msgenc` + `ndspy`).
3. Dump full bank → `data/text/<N>.txt` → edit → `make` in Docker → reload `test.nds`.

See also [HACK-NOTES § How text editing works](HACK-NOTES.md#how-text-editing-works).
