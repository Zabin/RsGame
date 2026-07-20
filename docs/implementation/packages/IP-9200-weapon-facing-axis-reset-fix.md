# IP-9200 — Weapon-Facing Axis Reset Fix (`BL-0184`)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9200` — remediation package for [`BL-0184`](../../pipeline/backlog.md): weapon fire only
shoots diagonally in real play, a High-severity bug in the shipped `VERIFIED` `FR-11310`/
`IP-1128` (movement-based multi-directional weapon fire) feature. User-reported, confirmed by
live PyBoy reproduction with real button input.

## 2. Objective

`handle_play_input`'s facing computation correctly derives `PLAYER_FACING_X`/`PLAYER_FACING_Y`
from the player's *currently held* movement input each frame — clearing an axis to 0 when that
axis's own direction is not held — instead of only ever setting an axis on press with no
clearing branch, which lets a stale nonzero value (including the boot-time default
`PLAYER_FACING_X=1`) silently ride along into a different axis's own movement, producing a
diagonal fire where the player's real, current movement is purely cardinal.

## 3. Requirements Covered

- **`FR-11310`** (movement-based multi-directional weapon fire) — this package fixes a
  correctness defect in the shipped implementation; it does not change the requirement itself
  (the requirement's own "moving direction, else last-faced" rule, per `R220`, is exactly what
  this fix restores — the shipped code deviated from it, the requirement did not).

## 4. Architecture Components

None new. No `ADS-002`/`GDS-07` delta — `PLAYER_FACING_X`/`PLAYER_FACING_Y` already exist at
their shipped addresses (`0xC6DF`/`0xC6E0`); this package changes only how they are computed
inside `handle_play_input`, not their meaning, address, or any consumer's own read of them
(`hpi_no_fire`'s copy into `PROJ_STEP_X`/`Y` at fire time is unchanged).

## 5. Interfaces

- **`PLAYER_FACING_X`/`PLAYER_FACING_Y`** (`0xC6DF`/`0xC6E0`, existing, `IP-1128`) — write-side
  logic corrected here; no address/width/meaning change. Read-side (the fire block's copy into
  `PROJ_STEP_X`/`PROJ_STEP_Y`, `asm_game.py:1145`-1146) is unchanged.
- **`handle_play_input`** (`asm_game.py:1114`-1198) — the routine being fixed. `JOY_CUR`
  (`0xC00C`), already read into `B` at the top of the movement block (`:1149`), is the only new
  input this fix needs — no new register/WRAM dependency.
- **`PLAYER_DIR`** (existing, animation-facing direction — a *different* concept from
  `PLAYER_FACING_X`/`Y`, per `IP-1128`'s own original design decision) — untouched; this package
  does not touch `PLAYER_DIR`'s own writes (`:1158`, `:1167`) or its consumer (the OAM X-flip
  render).
- **`TMP1`** (existing, "did the player move this frame" flag used for the animation-frame
  toggle at `:1191`-1198) — untouched; this package's own facing computation is a separate block
  from the movement/clamp/animation logic and must not perturb `TMP1`'s own value.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**, `handle_play_input` (`:1149`-1198 today; exact line numbers may
  shift slightly by the time this package is picked up — confirm by direct re-read before
  editing, per this project's own standing drift-check convention):
  - **Remove** the four individual `PLAYER_FACING_X`/`PLAYER_FACING_Y` writes currently embedded
    inside the RIGHT/LEFT/UP/DOWN movement-clamp blocks (today at `:1159`, `:1168`, `:1177`,
    `:1187`) — leave every other instruction in those blocks (the movement-clamp arithmetic,
    `PLAYER_DIR` writes, `TMP1` sets) exactly as they are.
  - **Add**, immediately after `JOY_CUR` is loaded into `B` and before the RIGHT/LEFT/UP/DOWN
    movement-clamp block begins (today right after `:1150`'s `XOR_A(); LD_nn_A(TMP1)`): a new
    facing-computation block, in pseudocode —
      ```
      A = B AND (bit_RIGHT | bit_LEFT | bit_UP | bit_DOWN)
      if A == 0:
          # no direction held at all this frame -- preserve the last-faced
          # value untouched (FR-11310's own "moving direction, else
          # last-faced" rule; matches T37.e's own already-shipped,
          # already-passing precedent -- do not regress it)
          skip to the movement-clamp block, unchanged
      else:
          PLAYER_FACING_X = 0
          if B has bit_RIGHT set: PLAYER_FACING_X = 1
          if B has bit_LEFT set:  PLAYER_FACING_X = -1   # (0xFF, two's complement)
          PLAYER_FACING_Y = 0
          if B has bit_UP set:   PLAYER_FACING_Y = -1    # (0xFF)
          if B has bit_DOWN set: PLAYER_FACING_Y = 1
      ```
      (If both `RIGHT`+`LEFT`, or both `UP`+`DOWN`, are simultaneously held — an edge case with
      no defined real-hardware meaning — last-checked-wins is acceptable; this matches the
      existing movement-clamp block's own unspecified precedent for the same simultaneous-press
      case and is not part of this bug's own scope to resolve.)
- **No change** to `gbc_lib.py`, `build_rom.py`, `worldgen.py`, `tiles.py`, `tilemaps.py`,
  `music.py`.
- **Modify: `test_rom.py`**: extend `T37`'s own fixture per §8 below.

## 7. Implementation Tasks

Ordered: (1) confirm `handle_play_input`'s current exact structure by direct re-read (drift
check — this project's session already ran two refactor packages, `IP-8010`/`IP-8020`, elsewhere
in `asm_game.py`, though neither named `handle_play_input` in their own Files to Modify;
confirm it is unaffected); (2) remove the four embedded facing writes from the RIGHT/LEFT/UP/
DOWN blocks; (3) insert the new facing-computation block per §6's pseudocode; (4) rebuild,
confirm the existing `T37.a`/`b`/`c`/`e`/`f` checks (which exercise single-press, diagonal-press,
stationary, and fresh-boot-default cases respectively) still pass unmodified — they should,
since none of them exercises an axis-switch; (5) add the new regression checks (§8) that do
exercise an axis switch, confirm they fail against the pre-fix code (encode the bug as a failing
check first, per this project's own test-first convention) and pass against the fix; (6) full
suite run; (7) documentation updates (§9).

## 8. Tests to Add

Extends suite `T37` (`IP-1128`'s own weapon-directionality suite):

- **New helper, `fire_after_real_movement(pb, presses)`**: drives `handle_play_input` via
  successive `invoke_no_arg(pb, HPI_ADDR)` calls (this suite's own established real-routine-
  invocation technique, `T30`'s own precedent), setting `pb.memory[JOY_CUR_ADDR]` to each
  successive direction bitmask in `presses` before each invocation — this exercises the routine's
  own real per-frame facing computation across a sequence of held directions, unlike
  `fire_with_facing`'s direct force-injection (which cannot express this class of bug at all).
  After the sequence, force `JOY_NEW`'s own A-bit and invoke once more to fire.
- **`T37.j` — axis-switch regression (the exact reported bug): move RIGHT only for several
  frames, then release RIGHT and hold UP only for several frames (never touching LEFT/RIGHT
  again), then fire.** Expected: `(step_x, step_y) == (0, -1)` — pure up, not `(1, -1)`. This is
  the precise failure `BL-0184` reported and reproduced live.
- **`T37.k` — the symmetric case: move UP only, then switch to RIGHT only, then fire.** Expected:
  `(1, 0)` — pure right, not `(1, -1)`.
- **`T37.l` — non-regression: a fresh, never-moved session still fires rightward by default**
  (mirrors `T37.f`'s own existing check, re-run through the new code path to confirm the "no
  direction held → preserve last value" branch still yields the boot default correctly).
- **`T37.m` — non-regression: releasing all directions after moving preserves the last-held
  facing** (mirrors `T37.e`'s own existing check via the new real-movement-driven helper, to
  directly confirm the new code's "nothing held → don't touch it" branch, not just the
  pre-existing `fire_with_facing`-based `T37.e`).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-11310`'s Notes gains a line recording
  this remediation (the requirement itself is unchanged — its own "moving direction, else
  last-faced" rule is what the fix restores).
- `docs/pipeline/backlog.md`: `BL-0184` → resolution note (manager flips status on harvest).
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- `handle_play_input`'s facing computation clears an unheld axis to 0 whenever any direction is
  held, and preserves the last-faced value when nothing is held.
- `T37.j`/`T37.k` (the axis-switch regressions) pass; `T37.a`/`b`/`c`/`e`/`f` (pre-existing) and
  the new `T37.l`/`m` non-regression checks all pass.
- ROM builds at exactly 32768 bytes; full suite passes.
- Diff scope: `asm_game.py` (the fix) + `test_rom.py` (the new/extended tests) only.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] `T37.j`: moving RIGHT then switching to UP-only and firing yields `(0, -1)`, not `(1, -1)`.
- [ ] `T37.k`: the symmetric UP-then-RIGHT case yields `(1, 0)`, not `(1, -1)`.
- [ ] `T37.a`/`b`/`c`/`e`/`f` (pre-existing) still pass unmodified.
- [ ] Direct diff: `PLAYER_DIR`'s own two write sites and `TMP1`'s own animation-flag logic
      confirmed byte-for-byte unchanged (facing computation is a separate, additive block, not a
      rewrite of the movement/animation logic around it).
- [ ] Direct diff: no `gbc_lib.py`/`build_rom.py`/`worldgen.py`/`tiles.py`/`tilemaps.py`/
      `music.py` change.

## 12. Dependencies

- **`IP-1128`** (weapon directionality, `VERIFIED`) — this package fixes a defect in its own
  shipped code; hard dependency, already satisfied.

## 13. Risks

Low. The fix is a narrow, localized correction to one routine's own facing computation, with a
test-first regression pair (`T37.j`/`T37.k`) directly encoding the reported bug before the fix
lands. The one named risk: the simultaneous-opposite-press edge case (`RIGHT`+`LEFT` or
`UP`+`DOWN` both held) has no defined real-hardware meaning and is deliberately left as
last-checked-wins, matching the existing movement-clamp block's own unspecified precedent — not
a regression this package introduces, and not resolved here.

## 14. Rollback Considerations

Revert `handle_play_input` to the pre-fix per-direction facing writes; remove `T37.j`/`k`/`l`/`m`
and the `fire_after_real_movement` helper from `test_rom.py`. No WRAM address, save-format, or
interface change to unwind — the fix is purely computational.
