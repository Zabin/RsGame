# RsGame — Bunny Quest

A complete Game Boy Color game (32KB ROM, MBC1+RAM+BATTERY save) — a bunny explores a
procedurally generated world, collecting stars/flowers for score and one carrot per region
toward victory — built entirely by a Python assembler pipeline and verified headlessly with
PyBoy (**404/404 ROM tests**, `test_rom.py`).

## The game

From the main menu, a new game picks one of two modes, each with its own seed and (for finite
mode) a player-chosen world scale:

- **Finite mode** — a deterministic, seed-generated world of `WORLD_SCALE`×`WORLD_SCALE` regions
  across nine biome families (Beach, Forest, Mountain, Lake, Village, Cave, Desert, Plains,
  Castle). Exactly `WORLD_SCALE` carrots are placed (dead-end-prioritized); collecting all of
  them wins the game. Stars/flowers add to a running score along the way.
- **Infinite mode** — the same generation engine streamed indefinitely in every direction, no
  win condition — a running treasure count and a persisted top-score table drive a high-score
  chase instead. Optionally, from a `COMBAT MODE CONFIRM` prompt, the player can opt into a
  **Combat Sub-Mode**: hostile mobs materialize per region and move toward the player, an
  8-directional ranged weapon (with hit resolution and mob defeat) can be fired, and player
  health has a non-lethal setback protected by combined invincibility frames, knockback, and a
  per-mob cooldown. Collected treasure can also fund a healing economy and a weapon-tier
  upgrade economy (both implemented; player-input binding for triggering a spend is still an
  open item, `BL-0148`).

Both modes share the title/intro flow, an in-game save menu (battery-backed, persists across
power-off), a map screen, a victory flow (finite mode), an original procedurally-generated
melody per biome family, and full save/load of mode-specific state (including combat state,
where active).

## Build, run, test

- **Play/build/test:** see [`.claude/skills/run-bunnygarden/SKILL.md`](.claude/skills/run-bunnygarden/SKILL.md)
  — from the repo root: `python3 build_rom.py BunnyQuest.gbc` then `python3 test_rom.py` (both
  repo-relative; no absolute paths needed).
- **Developer quick-reference:** [`Claude.md`](Claude.md) (architecture, ROM/WRAM/SRAM maps,
  how-to-change-things) and [`memory.md`](memory.md) (tile/palette/collectible tables, debug log).

The game is built entirely by a modular Python assembler pipeline — no RGBDS or external
toolchain. `tiles.py`/`tilemaps.py`/`music.py`/`asm_game.py`/`worldgen.py` define content, art,
music, generation, and SM83 game logic; `build_rom.py` assembles them into a valid ROM via the
`ROM` class in `gbc_lib.py`; `test_rom.py` proves the result headlessly via PyBoy.

## Documentation-driven development pipeline

This project is developed through a staged, documentation-driven pipeline (vision → research →
architecture → requirements → features → implementation packages → verification → integration
review → release readiness), with a persistent journal and backlog so the pipeline's own state
survives across sessions.

- **Pipeline skills:** [`.claude/skills/README.md`](.claude/skills/README.md) — drive it with the
  `00-pipeline-manager` skill; the bootstrap run-book is
  [`docs/pipeline/BOOTSTRAP.md`](docs/pipeline/BOOTSTRAP.md).
- **Where things stand:** [`docs/pipeline/pipeline-journal.md`](docs/pipeline/pipeline-journal.md)
  (position + run log) and [`docs/pipeline/backlog.md`](docs/pipeline/backlog.md) (every open
  finding/recommendation with its disposition).
- **Docs index:** [`docs/INDEX.md`](docs/INDEX.md) · **Status tracker:** [`ROADMAP.md`](ROADMAP.md).
