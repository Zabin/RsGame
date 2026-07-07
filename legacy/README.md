# Legacy artifacts

These three files predate the **Bunny Quest** rewrite (commit `679b5cf`) and are no longer part
of the canonical build chain (`build_rom.py` → `gbc_lib.py`/`tiles.py`/`tilemaps.py`/`music.py`/
`asm_game.py` → `BunnyQuest.gbc`):

- `BunnyGarden_build_rom.py` — the monolithic, pre-modularization build script.
- `BunnyGarden_logic.json` — pre-rewrite game-logic data, superseded by the modular content
  modules.
- `BunnyGarden.gbc` — the pre-rewrite shipped ROM ("Bunny Garden Adventure"), superseded by
  `BunnyQuest.gbc` at the repo root.

Archived 2026-07-07 per [`BL-0004`](../docs/pipeline/backlog.md) (user decision: the modular
chain is canonical) as executed by
[`IP-9040`](../docs/implementation/packages/IP-9040-legacy-artifact-archival.md). Kept for
history; referenced by no current code.
