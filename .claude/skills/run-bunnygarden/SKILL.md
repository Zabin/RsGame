---
name: run-bunnygarden
description: Build, launch, drive, and screenshot Bunny Garden Adventure — the Game Boy Color ROM built by this repo's Python assembler pipeline — using PyBoy headless. Use when asked to build the ROM, run the game, smoke-test it, take screenshots, press buttons/drive gameplay, or run the ROM test suite. Utility skill outside the numbered pipeline; the pipeline's stage-08/09/10 skills call it for their G5 permanent gates and emulator evidence.
---

# Run Bunny Garden Adventure

Bunny Garden Adventure is a 32KB GBC ROM assembled entirely by Python: `build_rom.py` imports the
content modules (`tiles.py`, `tilemaps.py`, `music.py`, `asm_game.py`, via the `ROM` class in
`gbc_lib.py`) and writes `BunnyGarden.gbc`. Verification is **PyBoy** headless — memory
assertions + screenshots; no real hardware needed.

All paths are relative to the repo root. Python 3 with `pyboy` and `pillow` installed
(`pip install pyboy pillow`).

## Known path wart (read first)

`build_rom.py` defaults its output to `/mnt/user-data/outputs/BunnyGarden.gbc`, and `test_rom.py`
**hardcodes** `ROM_PATH = '/mnt/user-data/outputs/BunnyGarden.gbc'` plus a results path under
`/home/claude/bunnygarden/`. This is backlog item **BL-0005** (a remediation package should make
these paths repo-relative/overridable). Until that ships, make the directories exist:

```bash
mkdir -p /mnt/user-data/outputs /home/claude/bunnygarden
```

If those directories cannot be created in your environment, the remediation package for BL-0005
is the highest-leverage first implementation step — say so and route it rather than editing paths
ad hoc outside a package.

## Build

```bash
python3 build_rom.py /mnt/user-data/outputs/BunnyGarden.gbc
# expected: "Wrote 32768 bytes → /mnt/user-data/outputs/BunnyGarden.gbc"
```

`build_rom.py` takes the output path as `argv[1]` (defaults to the path above). A successful
build is exactly 32768 bytes. The checked-in `BunnyGarden.gbc` at the repo root is the shipped
v2.1 artifact — don't overwrite it except as a deliberate, committed release step.

## Test (the G5 permanent gate)

```bash
python3 test_rom.py
# expected: "RESULTS: 88/88 passed   0 failed" (count grows as packages add checks)
```

`test_rom.py` is a single self-running script (not pytest): suites T1 (header) · T2 (VRAM tiles)
· T3 (LCDC) · T4 (state machine) · T5 (tilemaps) · T6 (OAM/sprites) · T7 (joypad/movement) · T8
(collision/score) · T9 (zone transitions) · T10 (SRAM save/load). It writes `test_results.txt`.
It boots PyBoy repeatedly; ~1–3 minutes is normal. **Remove stale save files before fresh-boot
testing** — the game auto-loads a valid save and skips the title screen, which will confuse
state-machine assertions:

```bash
rm -f /mnt/user-data/outputs/BunnyGarden.gbc.ram /mnt/user-data/outputs/*.sav
```

## Drive the game / screenshot (agent path)

```python
from pyboy import PyBoy
pb = PyBoy('/mnt/user-data/outputs/BunnyGarden.gbc', window='null', sound_emulated=False)
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()            # boot to title

pb.button('start'); [pb.tick() for _ in range(30)]   # title -> intro
pb.button('a');     [pb.tick() for _ in range(30)]   # intro -> gameplay
pb.button('right', delay=60); [pb.tick() for _ in range(60)]  # hold right ~1s

pb.screen.image.save('shot.png')          # 160x144 PIL image
gs = pb.memory[0xC000]                    # GAMESTATE: 0=TITLE 1=INTRO 2=PLAYING 3=SAVE 4=MAP 5=VICTORY
x, y = pb.memory[0xC001], pb.memory[0xC002]
score, gifts = pb.memory[0xC006], pb.memory[0xC009]
pb.stop()
```

Write throwaway driver scripts in the scratchpad, not the repo. The WRAM map (C000–C2FF) in
`Claude.md` is the assertion surface — prefer memory assertions for logic, screenshots for
content review. `test_rom.py`'s own helpers (`fresh_boot`, `wipe_save`, button patterns) are the
reference idiom; mirror them.

## Gotchas

- **Save auto-load skips the title.** A valid SRAM save (magic `BUNY`) boots straight into
  gameplay. Wipe `.ram`/`.sav` files for fresh-boot tests; keep them to test persistence.
- **PyBoy uses `<rom>.ram`** as the battery-save file next to the ROM path.
- **Frame counts matter.** The game reads input on specific frames; use the ~30-frame settle
  loops after button presses as `test_rom.py` does.
- **Zone transitions:** walk off the right edge → next zone, left edge → previous. Player X is
  pixel 0–159; row 0 of the screen is the UI bar (player Y starts at 16).
- **The ROM is deterministic** given the same input script and a clean save state — identical
  runs should produce identical memory/screenshots; use that for regression evidence.
