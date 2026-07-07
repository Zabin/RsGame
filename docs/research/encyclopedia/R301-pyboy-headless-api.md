# R301 — PyBoy Headless API

- **Document ID:** R301 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** none
- **Referenced By:** R305 (test design built on this API), the `run-bunnygarden` utility skill
- **Produces:** grounds `test_rom.py`'s PyBoy usage and the `run-bunnygarden` skill's driving
  patterns
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R305

## Purpose

The exact PyBoy API surface this project's test suite and driving skill already use, confirmed
against PyBoy's own documentation/source — so a future test or driver script uses the *current*,
correct calls rather than a plausible-looking guess.

## Scope

Constructor arguments, `tick()`, the three button-input methods, memory indexing, screen/image
access, emulation speed, and `.ram` save-file / `stop()` behavior.

## Concepts

- **Constructor:** `PyBoy(gamerom, window=..., sound_emulated=...)` — only `gamerom` is required;
  `window="null"` runs fully headless (no rendering backend), reported to run roughly 100× faster
  than real-time versus a rendered window.[^1] Older PyBoy versions accepted `window="headless"`/
  `"dummy"`; both are deprecated in favor of `"null"` since a `tick()` signature change made them
  redundant.[^2]
- **`tick(count=1, render=True)`:** advances at least one frame; passing a `count` frame-skips
  (rendering only the final frame of the batch), and `render=False` suppresses rendering entirely
  for a given call — the mechanism headless test loops use to run fast.[^3]
- **Button input, three methods:**[^4] `button(name)` — presses and auto-releases at the *next*
  `tick()` call (convenience, one-shot); `button_press(name)` — presses and holds until an
  explicit `button_release(name)` (or `send_input`) call; `button_release(name)` — releases a
  held button. Valid names: `"a"`, `"b"`, `"start"`, `"select"`, `"left"`, `"right"`, `"up"`,
  `"down"`.
- **Memory access:** direct indexing, `pyboy.memory[0xC345]` for both read and (implied by the
  indexing interface) write.[^1]
- **Screen access:** `pyboy.screen.image` returns a PIL `Image`; `.save(path)` writes a PNG.[^1]
- **Speed control:** `set_emulation_speed(0)` removes the frame-rate cap entirely (run as fast as
  the host can).[^1]
- **Battery-save persistence:** if the loaded cartridge has a battery (cart type `0x03`,
  MBC1+RAM+BATTERY per R106), PyBoy automatically manages a `.ram` file next to the ROM path,
  loading it on construction and writing it on `stop()`; `stop()` (default: saves) vs. `stop(False)`
  (discards) controls whether that write happens, and a custom file-like object can be passed via
  `stop(ram_file=...)` to redirect the save location.[^5]

### Sources
[^1]: [PyBoy README](https://github.com/Baekalfen/PyBoy/blob/master/README.md), accessed 2026-07-06.
[^2]: [Migrating from v1.x.x to v2.0.0 — PyBoy Wiki](https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0), accessed 2026-07-06.
[^3]: [PyBoy README](https://github.com/Baekalfen/PyBoy/blob/master/README.md), accessed 2026-07-06.
[^4]: [pyboy/pyboy.py — PyBoy source](https://github.com/Baekalfen/PyBoy/blob/master/pyboy/pyboy.py), accessed 2026-07-06 (button method behavior cross-confirmed via search of the source/docs; **not independently fetched line-by-line in this session — flagged as needing fetch-verification** if a future session has unrestricted access).
[^5]: [Can PyBoy load save files? — Answer Overflow](https://www.answeroverflow.com/m/1319684658329419818), accessed 2026-07-06 (community Q&A citing PyBoy's own `stop()`/`.ram` behavior; single-source for the `ram_file=` custom-location detail — flag as needing a second source before treating that specific detail as certain).

**PyBoy is not installed in this session's environment** (`import pyboy` fails —
`ModuleNotFoundError`) — no local experiment could be run to independently confirm any of the
above against the actually-installed version. `memory.md` records "PyBoy 2.7.0" as the version
used for this project's last verified test run; treat that as the target version for any future
environment that installs it, and re-verify this topic's claims against it once installed.

## Operational Context

`test_rom.py` already exercises most of this surface directly and correctly (per the code):
`PyBoy(ROM_PATH, window='null', sound_emulated=False)` then `pb.set_emulation_speed(0)` at
construction; `pb.tick()` in bare loops (`for _ in range(80): pb.tick()`) to advance fixed frame
counts; both `pb.button('start')` (one-shot, auto-release) for menu navigation and the explicit
`pb.button_press('right'); ...; pb.button_release('right')` pair for held-movement tests;
`pb.memory[addr]` read throughout every check; `pb.screen.image.save(f"{SHOT_DIR}/{name}.png")`
for screenshots; `pb.stop()` at the end of each test block. This is a textbook-correct usage of
the documented API — the *test assertions* built on top of these calls are what's wrong (per
`test_rom.py`'s pre-rewrite WRAM semantics, backlog `BL-0006`), not the PyBoy driving code itself.

## Implementation Guidance

- **Any new driver/test code should follow `test_rom.py`'s existing idioms exactly**: `window=
  'null'`, `set_emulation_speed(0)`, `button()` for simple menu taps, `button_press`/
  `button_release` for held movement, fixed-frame-count `tick()` loops sized generously (the
  existing code uses 40–80 frame settle windows after an input) rather than a single `tick()` and
  hoping the frame landed right.
- **Remove stale `.ram`/save files before a fresh-boot test** (already documented in
  `run-bunnygarden`'s SKILL.md) — since PyBoy auto-loads a `.ram` file if one exists next to the
  ROM path, a leftover save from a prior run will make the game boot straight into `PLAYING`
  instead of `TITLE`, exactly the class of test flakiness a fresh-boot check must avoid.
- **A rewritten `test_rom.py` (per BL-0006/BL-0008) should keep this exact API-usage pattern** —
  the defect is in *what* is asserted (stale WRAM addresses/values), not *how* PyBoy is driven; do
  not rewrite the driving code, only the assertions (see R305 for the assertion-design guidance).
- **PyBoy's actual installed version should be confirmed and recorded** the next time this
  environment (or the CI/dev environment that eventually runs these tests) has it installed —
  this topic's claims are grounded in PyBoy's public docs/source, not a local experiment, and
  should be spot-checked against `import pyboy; pyboy.__version__` once available.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R305 (the test-design guidance built directly on this API).
