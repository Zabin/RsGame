# R107 — Joypad Register & Dual-Read Settling

- **Document ID:** R107 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** none
- **Referenced By:** none yet
- **Produces:** grounds `asm_game.py`'s joypad-read routine (`P1`, `JOY_CUR`/`JOY_PREV`/`JOY_NEW`)
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R110 (joypad interrupt, currently unused by this project)

## Purpose

Exact P1/JOYP register semantics and the standard multi-read settling idiom — directly relevant
because this project already shipped, and fixed, a bug in exactly this area (`Claude.md`'s "Bugs
Fixed vs v1": "Joypad dual-read with settle delay (was wrong button bits before)").

## Scope

The P1 register's active-low bit matrix, the select-then-read protocol, and the settling-read
idiom this project's current code implements.

## Concepts

**P1/JOYP (`0xFF00`)** multiplexes eight buttons onto four read bits via a 2×4 matrix, selected by
writing to bits 5/4:[^1]

| Bit | R/W | Meaning |
|---|---|---|
| 5 | W | Select Button keys (0 = select this group) |
| 4 | W | Select Direction keys (0 = select this group) |
| 3 | R | Down / Start (0 = pressed) |
| 2 | R | Up / Select |
| 1 | R | Left / B |
| 0 | R | Right / A |

**Buttons read active-low**: a pressed button reads as bit **0**, released as bit **1** — the
opposite of the intuitive "1 = pressed" mental model, and a natural place for an off-by-inversion
bug (exactly the class of bug this project's own v1 history records).[^1] If neither group is
selected (both bits 5/4 written as 1, i.e. writing `$30`), the low nibble reads all 1s (no buttons
report as pressed) regardless of physical state.[^1]

**Settling idiom:** because the matrix is analog-multiplexed hardware, most programs read the
port **several times in a row** after selecting a group and discard all but the last read — the
early reads exist purely as a delay to let the electrical signal settle, not to gather distinct
data.[^1] This is standard practice across essentially all GBC homebrew, not a project-specific
technique.

### Sources
[^1]: [Joypad Input — Pan Docs](https://gbdev.io/pandocs/Joypad_Input.html), accessed 2026-07-06.

## Operational Context

`asm_game.py`'s joypad routine implements exactly the documented idiom, twice over (once per
button group): select direction keys (`LD A,$10; LDH (P1),A`), then read `P1` **four times**,
discarding the first three (`LDH A,(P1)` ×4) before the group is switched to buttons (`LD A,$20;
...`) and read four more times, then the port is reset to `$30` (both groups deselected) and the
final combined reading is captured into `JOY_CUR`.[^1] This matches Pan Docs' documented idiom
directly.

The project's own bug history is the load-bearing example here: `Claude.md` records that in v1,
the joypad read was wrong ("wrong button bits before") until the dual-read-with-settle-delay
pattern was added — i.e., an earlier version likely read the port once per group (or without
enough settling reads) and got transient/incorrect bit values. The current four-read pattern
(more conservative than a bare minimum "read twice") is the fix, and should not be "optimized"
back down to fewer reads without understanding why the extra margin was added.

`asm_game.py` derives `JOY_NEW` (newly-pressed-this-frame) as `JOY_CUR AND (NOT JOY_PREV)` — a
standard edge-detection idiom built on top of the raw active-low `JOY_CUR` reading (the code
inverts `JOY_PREV` via `CPL` before ANDing, correctly converting the active-low "held" comparison
into an active-high "newly pressed" result).

## Implementation Guidance

- **Never reduce the joypad read to fewer than the current four settle-reads per group** without
  a specific, tested reason — this project already regressed here once (the v1 bug); treat the
  existing read count as a proven-safe margin, not an arbitrary number to trim for "efficiency."
- **Remember buttons are active-low** — any new button-handling logic (e.g. a future menu needing
  a specific button combo) should be written against `JOY_CUR`/`JOY_NEW`'s already-normalized
  (and already-tested) representation, not by re-deriving raw `P1` semantics inline.
- **This project does not use the joypad interrupt** (IE bit 4, R110) — input is polled every
  frame from the main loop, not interrupt-driven. A future low-power or menu-only-input feature
  wanting interrupt-driven input would be the first user of that IE bit and needs its own IF/IE
  wiring, not an extension of the current polling code.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R110 (the joypad interrupt source this project doesn't currently use).
