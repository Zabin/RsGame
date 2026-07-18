# Bunny Quest — Developer Guide

## Development pipeline (read this first for any non-trivial change)

This project is driven by a documentation-driven-development skill pipeline — see
[`.claude/skills/README.md`](.claude/skills/README.md) (stages, iteration loops, hard rules
G1–G5), [`ROADMAP.md`](ROADMAP.md) (per-document status), and
[`docs/pipeline/BOOTSTRAP.md`](docs/pipeline/BOOTSTRAP.md) (the run-book). The default entry
point is the `00-pipeline-manager` skill ("run the pipeline skill"); new features and bug reports
enter via `00-intake`, never by side-channel edits. Position and obligations persist in
[`docs/pipeline/pipeline-journal.md`](docs/pipeline/pipeline-journal.md) and
[`docs/pipeline/backlog.md`](docs/pipeline/backlog.md). This file remains the working
quick-reference; the GDS ladder under `docs/architecture/` absorbs its sections level by level
(each level's merge gate records the decision).

## Architecture Overview

Each file has ONE job. Edit only what you need.

```
gbc_lib.py     — ROM class (assembler opcodes) + color math + header writing
tiles.py       — All tile pixel data (8x8 arrays) + build_tile_data()
tilemaps.py    — Screen generators + collectible spawn tables + ZONE_COLLECTS
music.py       — Music note data (Twinkle Twinkle, C4 octave)
asm_game.py    — Game logic: ISRs, main loop, all subroutines, WRAM/IO constants
build_rom.py   — Master: imports all modules, lays out ROM sections, patches pointers
```

### Data layout, WRAM map, SRAM save format

**Superseded here — authoritative source is
[`docs/architecture/07-data-model.md`](docs/architecture/07-data-model.md) (GDS-07).** GDS-07
states exact byte addresses (ROM section layout, the `0xC000`–`0xC3A0` WRAM map, the `0xA000`+
SRAM save format including the magic `BUNY` header and the `SAVE_VERSION_VAL` guard) confirmed
directly against `build_rom.py`/`asm_game.py`. Duplicating those tables back into this file is
exactly what went stale last time (see `docs/pipeline/backlog.md` BL-0007/BL-0008) — don't; edit
GDS-07 when the layout changes, and this file's pointer stays correct with zero maintenance.

Quick orientation only (see GDS-07 for the real tables): the game is **Bunny Quest** — 9 zones
(Beach, Forest, Mountain, Lake, Village, Cave, Desert, Plains, Castle) in a 3×3 grid, one carrot
per zone, victory at `CARROTS_COUNT == 9`. `CUR_ZONE` is `0–8`; `CARROT_FLAGS` and
`SCOREITEM_FLAGS` are each 9-byte per-zone arrays.

---

## How to Change Things

### Add a new tile
1. Edit `tiles.py`: add a new pixel array function and a new `TL_*` constant (use unused 0x00-0xFF slot)
2. Add a `put(TL_NEW, new_fn())` call in `build_tile_data()`
3. Reference `TL_NEW` from `tilemaps.py` or `asm_game.py`

### Edit a screen layout
1. Edit the function in `tilemaps.py` (e.g. `beach_screen()`, `forest_screen()` — one function
   per zone, plus `title_screen()`/`intro_screen()`/`save_screen()`/`map_screen()`/
   `victory_screen()` for the non-zone screens)
2. No changes needed elsewhere — it auto-rebuilds
3. Collectible positions are in `ZONE_COLLECTS` at bottom of `tilemaps.py`

### Edit music
1. Edit `music.py` — change `SONG` list of (freq, duration) tuples
2. QN=18 frames per quarter note, HN=36 half note
3. Frequencies: use `freq(hz)` helper. `freq(261.63)` = C4

### Change game logic
1. Edit `asm_game.py` — functions return label dictionaries for patch points
2. Each subroutine is a labeled block. The `build_game_asm(rom)` function emits all code.
3. Patch points are returned as a dict so `build_rom.py` can write data addresses.

### Add a new game state
1. Add `GS_NEW = 6` constant in `asm_game.py`
2. Add dispatch entry in main loop: `rom.CP_n(GS_NEW); rom.JP_Z('st_new')`
3. Add handler label + RET somewhere before data section
4. Add redraw handler in `do_screen_redraw`
5. Add screen generator in `tilemaps.py` + emit it in `build_rom.py`

---

## Known Good Behavior (Baseline + Release 1 — assessed GO 2026-07-10; Release 2 — assessed GO 2026-07-12; Release 2 addendum — assessed GO 2026-07-17)

> Release readiness: **GO** ([release-assessment-bootstrap-tranche.md](docs/reviews/release-assessment-bootstrap-tranche.md));
> **Release 2 (procedural world + visual narrative, bundled with all post-ship remediation):
> GO, user-confirmed 2026-07-12**
> ([release-assessment-release-2-bundled.md](docs/reviews/release-assessment-release-2-bundled.md))
> — one named exception carried forward: `FEAT-2100`'s maze-aware edge-signaling shipped its
> classification logic only, the visual rendering half is not yet built (`BL-0075`).
> **Release 2 addendum (Infinite Mode + nine biome-family identities + procedural music):
> GO, user-confirmed 2026-07-17**
> ([release-assessment-infinite-mode-and-nine-biome-family-delta.md](docs/reviews/release-assessment-infinite-mode-and-nine-biome-family-delta.md))
> — twelve packages shipped: Infinite Mode (`FEAT-10000`, a new game mode alongside the original
> finite mode — seed/scale still fixed at new-game creation, but the world streams indefinitely
> instead of stopping at a bounded grid); the finite-mode biome-family taxonomy widened from 5 to
> 9 identities (folding the original Village/Cave/Desert/Plains zone art back in); procedural
> per-biome music sub-themes. Everything below (the bulleted list) still describes only the
> pre-Release-2 fixed-9-zone model, per the pre-existing staleness note below (`BL-0091`) — not
> re-authored by this GO, which is a trackers/status flip only.
>
> **Staleness flagged, not fixed here:** the bulleted behavior list immediately below still
> describes the pre-Release-2 fixed-9-zone/9-carrot/3×3-map model. Release 2 replaced world
> layout with a seed/scale-driven procedurally generated world (`FEAT-9000`/FS-102), the win
> condition and map screen were **not** updated to match (see `BL-0050`, `BL-0081`), and this
> section's own prose was never re-authored against that shipped reality. A full refresh is
> filed as `BL-0091` (new, this run) rather than attempted inline here — this baseline flip's
> own scope is trackers/status only, not a content rewrite.

Confirmed by the current `test_rom.py` suite (125/125 checks pass;
[`docs/architecture/01-concept-of-play.md`](docs/architecture/01-concept-of-play.md) (GDS-01) is
the authoritative narrative description of the state machine below):

- Title → START → Intro → A → gameplay in the boot zone
- D-pad moves the bunny (held), 8×16-OBJ walk animation works
- Collectibles detected by proximity; stars/flowers add to `SCORE` (0–99, no completion
  requirement); one carrot per zone sets a `CARROT_FLAGS` bit and increments `CARROTS_COUNT`
- All 9 carrots collected → VICTORY screen
- START in game → SAVE menu → A saves to SRAM, B cancels
- SELECT in game → MAP screen (3×3 grid, shows which zones' carrots are collected) → B exits
- SRAM save persists across sessions (battery save, MBC1+RAM+BATTERY cart type `0x03`); a valid
  save auto-loads on boot, skipping the title screen
- Zone transition: walking off any screen edge with a valid 3×3-grid neighbor (signaled by a
  directional arrow) enters that zone
- A collected star/flower (`ScoreItem`) stays inactive across a save/reload of the same session,
  and does not re-award `SCORE` on zone re-entry ([FR-5220](docs/requirements/01-functional-requirements.md), `BL-0023` fix, `IP-1010`)

## Known Issues

None currently reproducing against the shipped code. Two items from this file's earlier,
pre-rewrite content were re-verified and closed:

- **Map screen hearts / wrong BG addresses (`BL-0001`):** does not reproduce —
  `update_map_hearts` matches `map_screen()`'s heart placement exactly; a permanent regression
  check rides the test suite.
- **Score display writing during LCD-on (`BL-0003`):** fixed by `IP-9020` (2026-07-07) — the
  write is now VBlank-gated at frame top; verified independently
  ([VR-9020](docs/implementation/verification/VR-9020-score-bar-vblank-fix.md)).

The bunny's two-separate-OAM-entry rendering issue from the pre-rewrite game is also resolved —
the shipped sprite uses 8×16 OBJ mode, a single OAM pair per frame (commit `9a587ac`,
[ADR-0007](docs/architecture/adr/ADR-0007-8x16-obj-sprite-mode.md)).

Any currently open item lives in [`docs/pipeline/backlog.md`](docs/pipeline/backlog.md), not
here — this file is a snapshot at last refresh, not a live tracker.
