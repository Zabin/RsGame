# IP-9210 — Automatic Weapon-Tier Upgrade Trigger (`BL-0148`/`ADR-0022`)

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9210` — implements `FR-11510`'s 2026-07-20 revision (`BL-0148`/`ADR-0022`): the weapon-tier
funding trigger changes from a player-invoked, unreachable spend action (`IP-1129`, shipped fully
built and `VERIFIED`, but with no button ever bound to it) to an **automatic**, threshold-crossing
check run once per frame during `COMBAT_MODE` — no input event required. Direct user request:
"implement an automatic weapon upgrade."

## 2. Objective

While `COMBAT_MODE` is active and `WEAPON_TIER` is below its own maximum (3), each frame checks
`RUNNING_TREASURE_COUNT` against the current tier's own next threshold (10 for tier 1→2, 25 for
tier 2→3); when met or exceeded, `WEAPON_TIER` increases by exactly one and that threshold amount
is decremented from `RUNNING_TREASURE_COUNT` in the same frame. Once `WEAPON_TIER == 3`, the
check is a true no-op — no further treasure is ever decremented by this leaf.

## 3. Requirements Covered

- **`FR-11510`** (automatic treasure-funded weapon-tier upgrade economy, revised 2026-07-20) —
  this package is that revision's own implementation.

## 4. Architecture Components

`ADR-0022` (automatic weapon-tier funding trigger) — this package implements Decisions 1-4
verbatim (automatic per-frame trigger; threshold-crossing, not flat-rate; 10/25 threshold curve;
`WEAPON_TIER`'s own existing persistence/cap/setback-immunity unchanged). No new WRAM (thresholds
are compile-time constants, not persisted state) — confirmed against `GDS-07`: no data-model
delta.

## 5. Interfaces

- **`WEAPON_TIER`** (`0xC6D9`, existing, `IP-1122`) — read (to select the current tier's own
  threshold and to gate the at-cap no-op) and written (incremented by exactly 1 on a successful
  check). No address/width change.
- **`RUNNING_TREASURE_COUNT`** (existing, 16-bit, `IP-1103`) — read (compared against the current
  threshold) and written (decremented by the threshold amount on a successful check). Same shared
  count `FR-10400`'s top-score comparison and `FR-11500`'s heal-spend both already read/write —
  no second ledger.
- **`COMBAT_MODE`** (existing, `IP-1120`) — gates the check exactly as every other per-frame
  combat routine already does.
- **`st_playing`** (`asm_game.py:706`-717) — gains one new unconditional `CALL` alongside the
  existing combat chain (`inf_mob_move`/`inf_projectile_update`/`inf_mob_contact_check`/
  `inf_invincibility_tick`), mirroring that chain's own established "no-op unless `COMBAT_MODE`"
  convention.
- **`inf_tier_spend`** (`asm_game.py:4033`, `IP-1129`) — **rewritten in place** (not extended):
  its current body (a single unconditional `CALL('treasure_spend_gate_and_decrement')` — the
  shared 1-treasure-per-call helper `inf_heal_spend` also uses — followed by a capped increment)
  no longer fits the revised behavior, which needs a 16-bit compare-against-a-variable-threshold
  and a variable-amount decrement, not the shared helper's fixed "decrement by exactly 1" shape.
  `treasure_spend_gate_and_decrement` itself is **not modified** — `inf_heal_spend` (`FR-11500`,
  still a discrete, currently-unbound player action, out of scope for this package) continues to
  use it unchanged. `inf_tier_spend`'s own label/entry point is preserved (nothing else calls it
  today, confirmed by the supersession sweep below) so no rename is needed.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - **`inf_tier_spend`** (`:4033`-4038): replace the current body. New logic, in pseudocode:
    ```
    if COMBAT_MODE == 0: return                      # unchanged gate
    if WEAPON_TIER >= 3: return                       # true no-op at cap (NOT inf_heal_spend's
                                                       # "spend even at cap" shape -- no further
                                                       # threshold exists past tier 3)
    threshold = 10 if WEAPON_TIER == 1 else 25        # WEAPON_TIER is 1 or 2 here (3 excluded above)
    if RUNNING_TREASURE_COUNT (16-bit) < threshold: return   # not enough yet, re-checked next frame
    RUNNING_TREASURE_COUNT -= threshold               # 16-bit subtract, mirroring
                                                       # treasure_spend_gate_and_decrement's own
                                                       # check-before-decrement borrow technique
                                                       # (threshold fits in one byte, so this is a
                                                       # single-byte-immediate 16-bit subtraction,
                                                       # not the full shared helper)
    WEAPON_TIER += 1
    SCORE_DIRTY = 1                                   # HUD refresh, mirroring every other
                                                       # RUNNING_TREASURE_COUNT-mutating routine
    ```
    Confirm `WEAPON_TIER`'s current range (1-3) and `RUNNING_TREASURE_COUNT`'s exact address/width
    by direct re-read before editing (drift check).
  - **`st_playing`** (`:706`-717): add one `CALL('inf_tier_spend')` alongside the existing
    unconditional combat chain (`inf_mob_move`/`inf_projectile_update`/`inf_mob_contact_check`/
    `inf_invincibility_tick`) — placement within that chain does not matter functionally (none of
    those routines read/write `WEAPON_TIER` or `RUNNING_TREASURE_COUNT`, confirmed by direct
    re-read), but append it last in the chain for minimal diff noise.
- **No change** to `treasure_spend_gate_and_decrement`, `inf_heal_spend`, `gbc_lib.py`,
  `build_rom.py`, `worldgen.py`, `tiles.py`, `tilemaps.py`, `music.py`.
- **Modify: `test_rom.py`**: rewrite suite `T38` per §8 (the existing `T38.a`-`e` exercise the
  *old* manual-spend, 1-for-1 shape and must be replaced, not merely extended — the old
  `invoke_no_arg(pb, ITS_ADDR)` single-call pattern no longer matches the automatic-per-frame,
  threshold-crossing behavior being tested).

## 7. Implementation Tasks

Ordered: (1) confirm `inf_tier_spend`'s current body, `st_playing`'s exact combat-chain sequence,
and `WEAPON_TIER`/`RUNNING_TREASURE_COUNT`'s addresses by direct re-read (drift check — this
session's own `IP-8010`/`IP-8020`/`IP-8030` refactor packages touched nearby routines but not
`inf_tier_spend`/`st_playing` themselves, confirm still true); (2) **mandatory supersession
sweep**: grep the tree for every reference to `inf_tier_spend` and `ITS_ADDR` to confirm the only
existing call sites are `test_rom.py`'s own `T38` suite (no other production call site exists to
account for) — record the result explicitly, not silently; (3) rewrite `inf_tier_spend`'s body
per §6's pseudocode; (4) add the new `CALL('inf_tier_spend')` to `st_playing`; (5) rebuild, run
the full suite — expect `T38.a`-`e` to fail (they test the retired manual-spend shape) until
task (6); (6) rewrite `T38` per §8; (7) full suite run; (8) documentation updates (§9).

## 8. Tests to Add

Rewrite suite `T38` (`IP-1129`'s own suite, retired manual-spend shape replaced in place — same
suite number, new content, since it's still "Combat Sub-Mode: Weapon-Tier Funding Economy"):

- **`T38.a` — tier 1→2 threshold crossing:** force `WEAPON_TIER=1`, `RUNNING_TREASURE_COUNT=10`,
  `COMBAT_MODE=1`; tick one real frame (via the real `st_playing` per-frame path, not a direct
  `inf_tier_spend` invoke, to prove the automatic call site actually fires — mirrors this
  package's own "no input event" claim); confirm `WEAPON_TIER == 2` and `RUNNING_TREASURE_COUNT
  == 0`.
- **`T38.b` — below-threshold no-op:** force `WEAPON_TIER=1`, `RUNNING_TREASURE_COUNT=9`; tick one
  frame; confirm `WEAPON_TIER` and `RUNNING_TREASURE_COUNT` both unchanged (re-checked, not
  consumed).
- **`T38.c` — tier 2→3 threshold crossing, and confirms independence from tier 1's own
  threshold:** force `WEAPON_TIER=2`, `RUNNING_TREASURE_COUNT=25`; tick one frame; confirm
  `WEAPON_TIER == 3` and `RUNNING_TREASURE_COUNT == 0`. Spot-check `RUNNING_TREASURE_COUNT=24`
  (one below) does *not* fire.
- **`T38.d` — true no-op at cap (the deliberate divergence from `inf_heal_spend`'s own "spends
  even at cap" precedent):** force `WEAPON_TIER=3`, `RUNNING_TREASURE_COUNT=999`; tick several
  frames; confirm `RUNNING_TREASURE_COUNT` stays exactly `999` — no decrement at all, unlike
  `T31.d2`'s own heal-spend-at-max-health precedent.
- **`T38.e` — `COMBAT_MODE` off is a complete no-op:** force `WEAPON_TIER=1`,
  `RUNNING_TREASURE_COUNT=10`, `COMBAT_MODE=0`; tick a frame; confirm nothing changes.
- **`T38.f` — persistence:** a tier increase earned via the automatic trigger survives a
  mob-contact setback (mirrors the retired `T38.e`'s own in-session persistence check) and a
  save/load round trip (mirrors `IP-1124`'s own `T32.a` coverage — `WEAPON_TIER`'s own SRAM
  mirror is unaffected by this package, confirm it still round-trips).

## 9. Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-11510`'s own Status line flips from
  "re-implementation owed" to Implemented, citing this package and the new `T38` suite.
- `docs/requirements/04-requirements-traceability-matrix.md`: `FR-11510`'s row's own
  Implementation Package/Test columns updated from "superseded, re-implementation owed" to
  `IP-9210` / `T38.a`-`f`.
- `docs/features/FS-112-infinite-mode-combat-sub-mode.md`: Workflow D step 3a's own delta note
  gains an "implemented" line citing this package.
- `docs/pipeline/backlog.md`: `BL-0148` → updated to record the tier-spend half's own real
  implementation (not just the architecture decision); `BL-0147` cross-referenced as fully closed
  end-to-end.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- `inf_tier_spend` implements the automatic threshold-crossing check described in §6; `st_playing`
  calls it unconditionally every frame, mirroring the existing combat chain's own convention.
- `T38.a`-`f` all pass; no other suite regresses.
- ROM builds at exactly 32768 bytes; full suite passes.
- Diff scope: `asm_game.py` + `test_rom.py` only.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] `T38.a`/`c` confirm both tier thresholds (10, 25) fire correctly and independently.
- [ ] `T38.b` confirms a below-threshold balance does not fire.
- [ ] `T38.d` confirms the at-cap state is a true no-op (zero decrement), not `inf_heal_spend`'s
      own spend-even-at-cap shape.
- [ ] `T38.a` (or a dedicated check) confirms the trigger fires via the real `st_playing` per-frame
      path with no input event — not merely via a direct `inf_tier_spend` invoke.
- [ ] Direct diff: `treasure_spend_gate_and_decrement`/`inf_heal_spend` byte-for-byte unchanged.
- [ ] Direct diff: no `gbc_lib.py`/`build_rom.py`/`worldgen.py`/`tiles.py`/`tilemaps.py`/
      `music.py` change.
- [ ] Supersession sweep result (no other `inf_tier_spend` call site existed) recorded, not
      assumed.

## 12. Dependencies

- **`IP-1129`** (`VERIFIED`) — this package rewrites its own `inf_tier_spend` body in place;
  hard dependency, already satisfied.
- **`IP-1122`/`IP-1103`** (`VERIFIED`) — `WEAPON_TIER`/`RUNNING_TREASURE_COUNT` must already exist
  at their shipped addresses; satisfied.

## 13. Risks

Low. A localized rewrite of one already-`VERIFIED` routine's internal body plus one new
unconditional call site, both following this codebase's own established per-frame-gate
conventions exactly. The one named risk: the 10/25 threshold curve (`ADR-0022`) is a deliberately
conservative, non-research-derived design choice — if playtesting shows it feels too slow or too
fast, that is a future `03`/`04` revision, not a defect in this package's own correct
implementation of the values as specified.

## 14. Rollback Considerations

Revert `inf_tier_spend` to its prior `treasure_spend_gate_and_decrement`-based body; remove the
new `CALL('inf_tier_spend')` from `st_playing`; revert `T38` to its prior manual-spend-shape
content. No WRAM, save-format, or interface dependency to unwind — `WEAPON_TIER`'s own SRAM
mirror (`IP-1124`) is unaffected either way.
