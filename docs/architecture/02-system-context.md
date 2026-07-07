# GDS-02 — System Context

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-01](01-concept-of-play.md); the next level,
> [GDS-03 Architecture](03-architecture.md), builds on this one.

## Purpose

The ROM artifact, the Python build pipeline, the PyBoy verification harness, real-hardware
aspirations, and the external constraints (32KB cart, CGB feature set).

## Content

### 1. The artifact

The system produces exactly one artifact: `BunnyQuest.gbc`, a 32768-byte Game Boy Color ROM,
header-declared MBC1+RAM+BATTERY (cart type `0x03`), single-bank (`rsize=0x00`, no bank
switching), 8KB cartridge SRAM (`ramsize=0x02`) —
[R106](../research/encyclopedia/R106-mbc1-sram-battery-saves.md),
[R109](../research/encyclopedia/R109-cartridge-header-checksums.md). At this system's current
state, 23148 of 32768 bytes are used (~9.6KB headroom) — the concrete number
[MSTR-001](../master/MSTR-001-program-vision.md) C7's world-scale ambition and
[GDS-01](01-concept-of-play.md) §5's Open Question will eventually press against.

### 2. The build pipeline

The ROM is produced entirely by a **from-scratch Python assembler** — no RGBDS, no external
toolchain (MSTR-001 C3). Six modules, each with exactly one job:
`gbc_lib.py` (SM83 opcode emitters + label/fixup resolution + header/checksum writing,
[R101](../research/encyclopedia/R101-sm83-instruction-set.md)/
[R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md)) ·
`tiles.py` (2bpp tile pixel data,
[R303](../research/encyclopedia/R303-2bpp-tile-encoding.md)) ·
`tilemaps.py` (screen composition + collectible tables,
[R203](../research/encyclopedia/R203-screen-composition-tile-grid.md)) ·
`music.py` (channel-1 melody data,
[R108](../research/encyclopedia/R108-apu-channels-registers.md)/
[R207](../research/encyclopedia/R207-gb-chiptune-composition.md)) ·
`asm_game.py` (game logic, ISRs, WRAM/IO constants) · `build_rom.py` (the master build: invokes
`build_game_asm(rom)`, lays out every data section, resolves the patch-point dict, calls
`rom.resolve()`, writes the header, saves the file — the fixed ordering
[R302](../research/encyclopedia/R302-python-assembler-codegen-patterns.md) documents as
load-bearing). `docs/architecture/03-architecture.md` (GDS-03, next) owns the module-decomposition
detail; this level's concern is only that this pipeline is the system's sole path from source to
artifact, and it is fully reproducible (a clean rebuild from source is byte-identical to the
checked-in ROM — confirmed directly during the vision correction, MSTR-001 §8).

### 3. The verification harness

**Intended state:** `test_rom.py` builds the ROM and drives it headlessly via PyBoy
([R301](../research/encyclopedia/R301-pyboy-headless-api.md)), asserting both boot-time header
validity (suite T1) and in-game behavioral correctness (suites T2–T10) — the G5 permanent gate
this whole pipeline's stage-08/09 skills depend on.

**Actual current state:** T1 (header validation) is genuinely reliable —
[R304](../research/encyclopedia/R304-rom-validation.md) confirms its checks (ROM size, entry
point, GBC flag, cart type, RAM size, header checksum) test facts that don't depend on game logic
and are unaffected by the Bunny Quest rewrite. **The remaining suites are not currently
trustworthy**: `test_rom.py` asserts pre-rewrite WRAM semantics (a 3-bit `GIFTS` bitfield model,
zones bounded 0–2) against code that has moved to a 9-byte `CARROT_FLAGS` array and zones 0–8 —
[`BL-0006`](../pipeline/backlog.md), Critical, confirmed by direct comparison of the test
assertions against `asm_game.py`. **`test_results.txt`'s "88/88 passed" is not evidence about the
current tree** — it predates the rewrite. [R305](../research/encyclopedia/R305-emulator-based-test-design.md)
already specifies the exact rewrite target (current addresses, current victory condition, current
zone-boundary shape); the fix itself is `07`/`08` scope (`BL-0008`'s umbrella), not something this
level resolves.

PyBoy is not installed in the environment this documentation was authored in — its API surface is
grounded in PyBoy's own public documentation/source plus this project's working `test_rom.py`
code (R301), not a local experiment; `memory.md` records PyBoy 2.7.0 as the last confirmed
working version.

### 4. Real-hardware aspirations

Per assumption **A2**: PyBoy headless is the verification *gate* — a change is "done" once it
builds and the (eventually-correct) test suite passes on PyBoy. Real-hardware behavior is
*expected* to match (nothing in the design deliberately relies on emulator-specific leniency) but
is explicitly **not** part of the gate — no flash-cart testing, no second-emulator cross-check is
currently part of this system's verification loop. This is a deliberate, stated scope boundary,
not an oversight: it keeps the verification loop fast and fully automatable, at the cost of not
catching emulator-vs-hardware divergence (R106's confirmed-correct SRAM enable/disable bracketing
is the kind of fact that would matter more on real hardware than it typically does on a lenient
emulator).

### 5. External constraints

- **Platform:** CGB hardware target (GBC flag `0x80`, "supports CGB, also runs on DMG" —
  [R109](../research/encyclopedia/R109-cartridge-header-checksums.md)); single 32KB bank today
  (§1); MBC1+RAM+BATTERY save persistence (R106).
- **Toolchain portability is currently broken outside one prior environment.** `build_rom.py`
  defaults its output path, and `test_rom.py` hardcodes four separate absolute paths (the ROM
  path — under the stale `BunnyGarden.gbc` name — its `.ram` sibling, a screenshot directory, and
  the results-file path), none of them repo-relative
  ([R306](../research/encyclopedia/R306-toolchain-portability.md),
  [`BL-0005`](../pipeline/backlog.md)). This is a real external constraint on this system today:
  the build/test tooling does not run correctly in an arbitrary environment without a manual
  `mkdir -p` workaround (documented as a stopgap in the `run-bunnygarden` utility skill) — a
  proper fix is scoped and ready for `07`/`08` (part of `BL-0008`'s umbrella), same status as the
  test-suite rewrite it's bundled with.
- **No CI is configured for this repository** — the G5 gates (build + test suite) run only when a
  stage-08/09 skill (or a human) invokes them directly; nothing currently runs them automatically
  on push.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-01`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** `Claude.md`'s general system-overview prose and `test_rom.py`'s
header comments are the sources this level was scaffolded to merge from — both are treated here
the same way `GDS-01` treated `Claude.md`: **not trusted for current-state facts** (both predate
or mischaracterize the Bunny Quest rewrite; `test_rom.py`'s own docstring still calls the suite
"BunnyGarden.gbc" tests). **Decision: this level supersedes `Claude.md`'s system/build/verification
overview and `test_rom.py`'s header-comment framing** for System-Context-level facts; both remain
flagged stale pending the `BL-0007`/`BL-0008` documentation-refresh pass, at which point
`Claude.md`'s corresponding section should become a pointer here rather than be independently
rewritten to say the same thing twice.
