---
name: run-bunnygarden
description: Build, launch, drive, and screenshot Bunny Quest — the Game Boy Color ROM built by this repo's Python assembler pipeline — using PyBoy headless. Use when asked to build the ROM, run the game, smoke-test it, take screenshots, press buttons/drive gameplay, or run the ROM test suite. Utility skill outside the numbered pipeline; the pipeline's stage-08/09/10 skills call it for their G5 permanent gates and emulator evidence.
---

# Run Bunny Quest

Bunny Quest is a 32KB GBC ROM assembled entirely by Python: `build_rom.py` imports the
content modules (`tiles.py`, `tilemaps.py`, `music.py`, `asm_game.py`, via the `ROM` class in
`gbc_lib.py`) and writes `BunnyQuest.gbc`. Verification is **PyBoy** headless — memory
assertions + screenshots; no real hardware needed.

All paths are repo-relative (no absolute/hardcoded paths anywhere in the pipeline, since
`IP-9010`, 2026-07-07). Python 3 with `pyboy` installed (`pip install pyboy numpy`); `pillow` is
optional (screenshots degrade to diagnostics-only without it — no check depends on it).

## Build

```bash
python3 build_rom.py BunnyQuest.gbc
# expected: "Wrote 32768 bytes → BunnyQuest.gbc"
```

`build_rom.py` takes the output path as `argv[1]` (defaults to `BunnyQuest.gbc` if omitted). A
successful build is exactly 32768 bytes. The checked-in `BunnyQuest.gbc` at the repo root is the
shipped artifact — don't overwrite it except as a deliberate, committed release step.

## Test (the G5 permanent gate)

```bash
python3 test_rom.py
# expected: "RESULTS: N/N passed   0 failed" (N grows as packages add checks — 125 as of the
# bootstrap tranche + IP-1010; new suites T12+ will land as the procgen-world increment ships)
```

`test_rom.py` is a single self-running script (not pytest), run from the repo root — it derives
`ROM_PATH`/`RAM_PATH` from its own location (`BASE = Path(__file__).resolve().parent`), no
absolute paths or manual directory setup needed. Suites T1 (header) · T2 (VRAM tiles) · T3
(LCDC) · T4 (state machine) · T5 (tilemaps) · T6 (OAM/sprites) · T7 (joypad/movement) · T8
(collision/score/carrots) · T9 (zone transitions) · T10 (SRAM save/load) · T11 (per-zone
ScoreItem persistence). It writes `test_results.txt`. It boots PyBoy repeatedly; ~1–3 minutes is
normal. **The suite handles its own `.ram`/`.sav` cleanup** — no manual `rm` needed before a
fresh run.

## Drive the game / screenshot (agent path)

```python
from pyboy import PyBoy
pb = PyBoy('BunnyQuest.gbc', window='null', sound_emulated=False)   # repo-relative
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()            # boot to title (or straight to PLAYING if a valid save auto-loads)

pb.button('start'); [pb.tick() for _ in range(30)]   # title -> intro
pb.button('a');     [pb.tick() for _ in range(30)]   # intro -> gameplay
pb.button('right', delay=60); [pb.tick() for _ in range(60)]  # hold right ~1s

pb.screen.image.save('shot.png')          # 160x144 PIL image (needs Pillow; use pb.screen.ndarray otherwise)
gs = pb.memory[0xC000]                    # GAMESTATE: 0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY
x, y = pb.memory[0xC001], pb.memory[0xC002]
score, carrots = pb.memory[0xC006], pb.memory[0xC009]  # SCORE, CARROTS_COUNT
pb.stop()
```

Write throwaway driver scripts in the scratchpad, not the repo. `docs/architecture/07-data-model.md`
(GDS-07) is the authoritative WRAM/SRAM map and assertion surface — prefer memory assertions for
logic, screenshots for content review. `test_rom.py`'s own helpers (`fresh_boot`, `wipe_save`,
button patterns) are the reference idiom; mirror them.

## Gotchas

- **Save auto-load skips the title.** A valid SRAM save (magic `BUNY`, matching version byte)
  boots straight into gameplay today — this is FR-1120's current shipped behavior. **Note:** the
  procgen-world increment's `FEAT-1100` (main menu & new-game flow, planned but not yet
  implemented as of 2026-07-10) will retire this auto-load bypass in favor of a menu-driven
  "continue" choice — update this gotcha once that package ships. Wipe `.ram`/`.sav` files for
  fresh-boot tests (or let `test_rom.py`'s own cleanup handle it); keep them to test persistence.
- **PyBoy uses `<rom>.ram`** as the battery-save file next to the ROM path.
- **Frame counts matter.** The game reads input on specific frames; use the ~30-frame settle
  loops after button presses as `test_rom.py` does.
- **Zone transitions:** the shipped 3×3 grid is fully connected — walk off any screen edge with a
  valid neighbor (signaled by a directional arrow) to transition. Player X is pixel 0–159; row 0
  of the screen is the UI bar (player Y starts at 16). **Note:** the procgen-world increment will
  generalize this to a generated `scale×scale` region grid once `IP-1020`/`IP-1030`/`IP-1031`
  ship (not yet implemented as of 2026-07-10).
- **Screenshots need Pillow.** If absent, `pb.screen.image` isn't available — use
  `pb.screen.ndarray` instead (as `test_rom.py`'s T6.7 does); no test currently depends on
  Pillow being installed.
- **The ROM is deterministic** given the same input script and a clean save state — identical
  runs should produce identical memory/screenshots; use that for regression evidence.
