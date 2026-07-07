# IP-9020 — Score-Bar VRAM Write Timing Fix

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9020` — bug-remediation series; no FS. Source: **`BL-0003`** (Medium), under the
**`BL-0008`** umbrella. Rider: **`BL-0019`** (ROM-headroom re-affirmation).

## 2. Objective

Eliminate the unguarded mid-frame VRAM writes in the HUD update path so the score/carrot digits
are always written during the VBlank window, closing `NFR-1200`'s recorded NOT MET status.

## 3. Requirements Covered

- **`NFR-1200`** (VBlank-gated VRAM writes for the status bar — currently NOT MET).
- **`FR-6200`-family HUD behavior** unchanged (digits still update after score/carrot changes);
  no functional requirement's behavior is altered, only its timing discipline.

## 4. Architecture Components

GDS-08 §HUD (static row-0 HUD, `SCORE_DIRTY` protocol) · GDS-06 N2 (the non-compliance this
fixes) · R102 (PPU mode timing: VRAM inaccessible during mode 3) · R110 (VBlank ISR /
`VBLANK_FLAG` handshake).

## 5. Interfaces

No GDS-09 cross-module contract is touched; `build_game_asm`'s `patches` dict keys are
unchanged. Internal-to-`asm_game.py` control-flow change only.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`** — verified current state: `update_status_disp` at line 505 (writes
  `0x9802`, `0x9808`–`0x980A`; already self-guards on `GAMESTATE==GS_PLAYING` at its entry,
  line 506, and on `SCORE_DIRTY` at line 507); its sole caller is `st_playing` at line 203,
  which runs after input/collision/transition/complete checks — i.e. at an unbounded distance
  from the VBlank wake-up at lines 152–155.

## 7. Implementation Tasks

1. Move the `CALL('update_status_disp')` from `st_playing` (line 203) to the main loop's
   frame top: immediately after `VBLANK_FLAG` is cleared (line 155) and **before**
   `NEED_REDRAW`/`do_screen_redraw` dispatch — the earliest post-wake point, guaranteeing the
   ≤4 BG-map writes land within the first few hundred cycles of the ~1.1 ms VBlank period
   (R102). The routine's existing internal `GAMESTATE`/`SCORE_DIRTY` guards make the
   unconditional call-site safe in every state.
2. Remove the old call from `st_playing`.
3. Note the accepted one-frame latency: `SCORE_DIRTY` set during frame N is now drawn at the
   top of frame N+1 (previously same-frame but timing-unsafe). No spec/requirement states
   same-frame HUD latency.

## 8. Tests to Add

In `test_rom.py` (post-IP-9010 form): extend the T8 collision/score suite with a check that
after a collection event, the digit tiles at `0x9802`/`0x9808`–`0x980A` reflect the new
`SCORE`/`CARROTS_COUNT` values within 2 frames (memory-assertion on the BG map via PyBoy,
R305 pattern). This is the observable regression guard for the relocated call.

## 9. Documentation Updates

- `docs/requirements/02-non-functional-requirements.md`: flip `NFR-1200` to Met (dated
  changelog line citing this package).
- `docs/architecture/06-non-functional-requirements.md` (GDS-06 N2): add a dated note that the
  non-compliance is remediated (pointer-level edit, content owned by the NFR flip).
- `docs/requirements/04-requirements-traceability-matrix.md`: NFR-1200 row's
  implementation/verification columns.
- Master Build Plan status row.

## 10. Definition of Done

- No code path writes `0x9800`-region bytes while the LCD is on outside the VBlank window:
  the only remaining VRAM writers are `do_screen_redraw` (LCD off, verified at line 540) and
  the relocated `update_status_disp` (frame-top, VBlank).
- HUD digits still update correctly on collection (T8 checks pass).
- ROM still 32768 bytes; byte-count delta ≈ 0 (a `CALL` moves; net size change ±3 bytes).

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes (including the new T8 digit-timing check).
- [ ] Direct code read confirms `st_playing` no longer calls `update_status_disp` and the
      frame-top call sits between the `VBLANK_FLAG` clear and the `NEED_REDRAW` check.
- [ ] BL-0019 rider: NFR-4000 headroom re-affirmed — report used/32768 bytes after build
      (expected ≈23148, delta ≈ 0).

## 12. Dependencies

- **IP-9010** (`VERIFIED`) — the G5 suite gate is meaningless before the rewrite lands, and
  this package's regression test (§8) lands in the rewritten suite.

## 13. Risks

- **Low.** The relocation relies on `update_status_disp`'s existing internal guards
  (verified present, lines 506–507). Worst case is a visible one-frame HUD latency —
  cosmetically imperceptible at 60 fps.
- ROM budget: ±3 bytes (BL-0019 rider item in §11 confirms).

## 14. Rollback Considerations

Single-call-site revert in `asm_game.py` restores prior behavior (and the prior NFR-1200
non-compliance). Save format, WRAM map, and all cross-module interfaces untouched.
