# Integration Review — Infinite Mode Tranche (IP-1100–IP-1104)

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

The full Infinite Mode tranche (`FS-110`/`FEAT-10000`/`EP-6000`) — all five packages, the
tranche's own complete implementation set, each independently verified across four separate
verification passes (three delegated to background subagents for genuine session independence,
one performed directly by a fresh session).

| Package | Title | VR |
|---|---|---|
| IP-1100 | Mode selection & new-game entry | [VR-1100](../implementation/verification/VR-1100-infinite-mode-mode-selection.md) |
| IP-1101 | Per-region materialization | [VR-1101](../implementation/verification/VR-1101-infinite-mode-region-materialization.md) |
| IP-1102 | Streaming window, navigation & render integration | [VR-1102](../implementation/verification/VR-1102-infinite-mode-streaming-window-and-render.md) |
| IP-1103 | Treasure placement & win-condition state | [VR-1103](../implementation/verification/VR-1103-infinite-mode-treasure-and-win-condition.md) |
| IP-1104 | Visited-region-ledger save persistence | [VR-1104](../implementation/verification/VR-1104-infinite-mode-ledger-save-persistence.md) |

**Commit reviewed:** `0be6db6` (tree head at review time — carries all five packages' own
implementation/amendment/verification commits plus pipeline journal/backlog updates). All five
packages confirmed `VERIFIED` on the Master Build Plan before this review began (31 of 31
implementation packages in the tree, all `VERIFIED` — this tranche's own closure is what reached
that count).

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x74C8 (29896 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
python3 test_rom.py                   → RESULTS: 309/309 passed   0 failed
```

(309, matching `IP-1104`'s own last-recorded suite size — no regressions since `VR-1104`. Rebuild
independently re-confirmed byte-identical via `sha256sum` against the committed ROM.)

## Dimension 1 — Interface consistency

**Clean.** Confirmed by direct code read and a live cross-package drive (see below), not just
re-trusting each package's own prior claim:

- **`GAME_MODE` claimed once, reused consistently.** `IP-1102` claims `GAME_MODE = 0xC3F6`
  (an implementation-order deviation from the original plan, which assigned it to `IP-1100` —
  both packages' own planning text already agreed on the address, confirmed no conflict). Every
  consumer (`dsr_p`/`dsr_p_inf`, `check_zone_transition`/`czt_infinite`, `setup_zone_collects`/
  `szc_infinite`, `check_collisions`/`cc_inf_hit`, `save_to_sram`/`try_load_save`'s Infinite
  Mode blocks) reads the identical WRAM byte, never redefines it.
- **The biome-id bitmask is applied identically everywhere it's extracted.** `dsr_p_inf`
  (`asm_game.py:1386`, `IP-1102`) and `szc_infinite` (`:1936`, `IP-1103`) both compute
  `INF_WINDOW+4` `AND 0x07` — the same mask, not two divergent re-implementations. The
  connectivity nibble (bits 3-6) is read consistently via `BIT_b_A(3/4/5/6)` across
  `czt_infinite` (`IP-1102`) and `draw_region_arrows_inf` (`IP-1102`) — no third encoding
  anywhere in the set.
- **`inf_ensure_window` is the single choke point for `INF_TREASURE_HERE`, and stays that way
  across two packages amending it.** `IP-1103` first added the center-cell cache write; `IP-1104`
  (via its own `BL-0119` amendment) added the ledger cross-reference immediately after it, in the
  same `if _idx == 4:` block. Confirmed by direct read: no second write site was introduced
  anywhere else, so the fix `IP-1104` shipped applies uniformly to every call site (`IP-1100`'s
  new-game entry, `IP-1102`'s `czt_infinite` navigation, `IP-1104`'s post-load restore) — this
  is the seam a per-package verification pass structurally cannot see (each VR audited its own
  package's edit to this shared routine in isolation; only reviewing the routine's cumulative
  state across all three edits confirms the composition is still correct).
- **`inf_ledger_mark_collected`: a clean forward-declared seam, resolved.** `IP-1103` names the
  call (`check_collisions`' `cc_inf_hit` branch) and ships a `RET` stub; `IP-1104` implements the
  real logic. Confirmed the call site's own register/flag expectations (none — a bare `CALL`,
  no return value consumed) match what `IP-1104`'s real implementation actually provides.
- **The two new screens' patch-point keys resolve correctly.** `ms_t`/`ms_a`/`ise_t`/`ise_a`
  (declared in `asm_game.py`'s `_dsr_screen`/`_dsr_family` calls, `IP-1100`) are each assigned
  exactly once by `build_rom.py` (confirmed via the printed section layout — `mode_select`/
  `infinite_seed_entry` both present, no `KeyError`/silent-overlap failure at build time) and
  resolved from `tilemaps.py`'s `ALL_SCREENS` registration (`IP-1100`), matching the established
  `mm_t`/`sse_t` pattern exactly.
- **Live cross-package drive (this review's own exercise, not any single package's own test):**
  drove the full assembled flow — `MAIN MENU → MODE SELECT (IP-1100) → INFINITE SEED ENTRY
  (IP-1100) → materialization via inf_ensure_window (IP-1102, calling IP-1101's routine) →
  treasure collection (IP-1101 presence half + IP-1103 collection half) → navigate two regions
  east (IP-1102) → save (IP-1104) → fresh-instance load (IP-1104) → navigate back, confirming
  collected-state persisted via the ledger cross-reference (IP-1102/1103/1104 seam) → indefinite
  resumability sweep (IP-1104/FR-10600)` — all six stages passed end to end at a fresh seed, not
  reusing any suite's own fixture.

## Dimension 2 — Invariant sweep

**Clean.**

- **ROM budget:** 32768 bytes exactly (29896 used, ~2.9 KiB headroom remaining — up from
  22984 bytes at the pre-tranche baseline; the ~6.9 KiB growth is this tranche's own five
  packages, confirmed disjoint from any other in-flight work).
- **WRAM/SRAM address map completeness:** every named constant in the tranche's own address
  ranges (`0xC3F6`–`0xC69A` WRAM, `0xA0C1`–`0xA34F` SRAM — 25 constants total, enumerated by
  direct extraction from `asm_game.py`) is documented in `GDS-07` §7d–§7h. No orphaned address:
  every byte the code actually uses traces to a named row in the data model.
- **No collision:** the WRAM range `0xC3F6`–`0xC69A` is contiguous and exclusively this
  tranche's own (confirmed against the full project-wide WRAM constant list — the next-lowest
  claimed address below it is `GW_KI_PLACED` at `0xC3F5`, `IP-1021`'s own, untouched; nothing
  above `0xC69A` is claimed by any other package). The SRAM range `0xA0C1`–`0xA34F` sits
  immediately after `SRAM_SCOREITEM`'s own end (`0xA0C0`), confirmed by direct address
  arithmetic, no gap or overlap.
- **VBlank-gating:** the two new screens' redraws (`dsr_ms`/`dsr_ise`, `IP-1100`) and the
  infinite-mode render path (`dsr_p_inf`/`draw_region_arrows_inf`, `IP-1102`) all run inside
  `do_screen_redraw`'s existing LCD-off bracket, the identical discipline every other screen in
  the tree already uses — no new unguarded VRAM write introduced anywhere in this tranche.
- **One-job-per-file:** no module boundary crossed. All five packages' own code lives in
  `asm_game.py`/`test_rom.py`; `IP-1100` alone touches `tilemaps.py` (two new screen-generator
  functions, explicitly named in its own §6 as the narrow content-adjacent exception) and
  `build_rom.py` (patch-key resolution) — confirmed against each package's own VR scope audit,
  re-confirmed here against the current tree head.
- **`SAVE_VERSION_VAL` sequence:** `0x04` → `0x05`, `IP-1104`'s own bump, correctly extending
  `IP-9110`'s prior bump — confirmed strictly monotonic, no reused value, consistent across
  `save_to_sram`/`try_load_save`/`check_save_valid`, all three reading the identical constant.

## Dimension 3 — Behavioral coherence

**Clean, with one confirmed-safe cross-package interaction worth recording explicitly.**

- No two packages implement the same behavior divergently (see Dimension 1's biome-mask/
  connectivity-bit consistency checks).
- No player-visible workflow spanning packages dead-ends at a seam: mode selection leads to seed
  entry leads to materialization leads to a renderable, navigable, collectible, saveable,
  resumable world — confirmed by this review's own six-stage live drive above, not merely by each
  package's own isolated test suite.
- **`check_complete` (pre-tranche, `IP-1021`/`FS-102`) is never gated on `GAME_MODE`, and this is
  confirmed safe by construction, not merely by empirical luck.** `check_complete` runs
  unconditionally every `PLAYING` frame, comparing `CARROTS_COUNT == WORLD_SCALE` and
  transitioning to the finite victory state on a match. No package in this tranche added a
  `GAME_MODE` guard to it. This is safe because: (1) `CARROTS_COUNT` is reset to 0 by the shared
  `st_intro` state (which both finite and Infinite Mode new-game flows pass through identically)
  and is never incremented by any Infinite Mode code path (`check_collisions`' `cc_inf_hit`
  branch increments `RUNNING_TREASURE_COUNT` instead, confirmed disjoint — `T26.a7`); (2)
  `WORLD_SCALE` is unconditionally reset to `3` by `mm_newgame` on every "new game" entry
  (`SSE_SCALE`'s own default), and `INFINITE SEED ENTRY`'s digit-cursor is bounded to cursor
  values 0–4 (never reaching the scale-slot cursor value 5), so no Infinite Mode input path can
  ever change it away from 3 — `WORLD_SCALE` is therefore never `0` for an Infinite Mode game,
  making the `0 == WORLD_SCALE` comparison structurally always-false. Independently re-confirmed
  live in this review's own drive (Dimension 1): `GAMESTATE` stayed `PLAYING` across 120
  consecutive frames of active Infinite Mode play with a treasure already collected. This is
  exactly the class of interaction a single package's own verification cannot see (no `IP-110x`
  package's own DoD mentions `check_complete` at all) — worth stating explicitly so a future
  change to either `mm_newgame`'s own `SSE_SCALE` default or `INFINITE SEED ENTRY`'s cursor bound
  doesn't silently reopen the spurious-victory hazard `IP-1100` §6 originally named and this
  tranche closed.
- The `IP-1100` §6-named hazard itself (Infinite Mode spuriously running finite-mode
  spawn/collection logic against stale `CUR_ZONE`/`REGION_GRAPH` data) is confirmed closed —
  `check_collisions`/`setup_zone_collects` both gate on `GAME_MODE` before reaching their
  finite-mode bodies, confirmed by direct code read and by this review's own live drive (no
  finite counter touched across the full six-stage session).

## Dimension 4 — Traceability coherence

**One Medium finding — real, contained staleness in two forward-reference/status artifacts,
while every implementation-facing ledger is accurate.**

- **Accurate and current:** Master Build Plan (all five rows `VERIFIED`, narrative prose matches
  each VR's own record), `docs/implementation/packages/INDEX.md` (same), `docs/implementation/
  verification/INDEX.md` (all four VR rows present and accurate), `ROADMAP.md`'s `IM-00`/
  `IP-xxxx` rows (dense but accurate dated deltas, confirmed by direct read all the way through
  to the `IP-1104` verification entry), `FS-110`'s own header metadata (confirmed correctly
  updated to `VERIFIED`/`COMPLETE` status for all five packages, including the incidental
  `IP-1100` staleness fix `IP-1104`'s own implementation made — `BL-0122`), `GDS-07` §7d–§7h,
  RTM rows for `FR-10100`/`10200`/`10210`/`10300`/`10400`/`10500`/`10600`/`NFR-1400`/`2300`/
  `4300`/`5400` (all confirmed accurate, correctly noting `FR-10400`'s own partial-implementation
  status rather than rounding up).
- **Stale:** `docs/features/INDEX.md`'s own `FS-110` row still reads "planned + authorized
  2026-07-14 (`IP-1100`–`IP-1104`, `Future` release bucket); **`IP-1101` `COMPLETE` 2026-07-14**
  (per-region materialization, `T22`, 253/253) — `IP-1100`/`1102`/`1103`/`1104` `NOT STARTED`" —
  last updated near the very start of the tranche, before any of the four verification passes or
  the other four implementation passes landed. `docs/feature-planning/03-feature-catalog.md`'s
  own `FEAT-10000` entry still carries the section header "(new — not yet implemented)" and a
  forward-reference note that only records `BL-0111`'s own resolution (2026-07-14) — neither has
  been touched since. Both are genuinely misleading to anyone consulting feature-planning
  artifacts rather than implementation artifacts: a reader of either would believe four of five
  packages haven't been started at all, when in fact all five are `VERIFIED`. This is squarely a
  metadata/forward-reference staleness question (the kind `05-feature-decomposition`'s own
  "forward reference: metadata only" convention already covers, per `03-feature-catalog.md`'s own
  existing precedent of recording `BL-0111`'s resolution in exactly this style) — not a
  substantive content rewrite, and not blocking (the release bucket itself, `Future`, remains
  correctly unchanged, since `11-release-readiness` hasn't run and shouldn't be implied by this
  fix).

## Dimension 5 — Documentation coherence

**Clean.** `Claude.md`/`memory.md` checked directly against their own explicitly-stated scope
(`Claude.md`'s own text: "this file remains the working quick-reference... duplicating \[GDS-07's\]
tables back into this file is exactly what went stale last time... don't," and its "Known Good
Behavior" section is explicitly scoped to what has passed an `11-release-readiness` GO call).
Infinite Mode has not been through a release decision — it correctly remains absent from both
documents' "Known Good Behavior"/"shipped" framing, exactly matching every prior tranche's own
precedent for pre-release work (`BL-0082`'s own adoption decision, `ADS-001`, etc. — all absent
from `Claude.md` for the identical reason). No claim in either document contradicts anything this
tranche shipped. `GDS-07` §7d–§7h (already confirmed under Dimension 2) and `GDS-01` §4d (`IP-1100`'s
own "Confirmed as shipped" note) are both current and accurate.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | `docs/features/INDEX.md`'s `FS-110` row and `docs/feature-planning/03-feature-catalog.md`'s `FEAT-10000` header/forward-reference note both understate the tranche's actual status — both still describe 4 of 5 packages as `NOT STARTED`/unimplemented, last touched near the tranche's own start. All five packages are `VERIFIED`. Metadata-only fix (mirrors `03-feature-catalog.md`'s own existing precedent for recording implementation-status forward-references, e.g. its `BL-0111` note) — does not require reopening either artifact's substantive content, and does not imply a release-bucket change (`Future` remains correct pending an `11-release-readiness` decision). | Medium (genuinely misleading to a reader relying on feature-planning artifacts instead of implementation artifacts; no functional/correctness impact, no release-readiness impact) | `05-feature-decomposition` (a metadata-only forward-reference refresh to both files, the identical class of touch-up that skill already performed for `BL-0111`) |

No Critical/High findings. Two informational notes recorded above, not filed as separate backlog
items (both already fully addressed within this report): the `check_complete`/`GAME_MODE`
interaction (Dimension 3, confirmed safe by construction, not a defect) and the incidental
`BL-0122` fix already landed (Dimension 4, already `DONE`). The tranche's five VRs' own
previously-filed findings (`BL-0115`/`117`/`120`/`121`/`122`/`124`/`125`, all Low
documentation-accuracy items, six still open) are unaffected by this review — already correctly
routed to a future `IP-110x` text-accuracy sweep, not re-litigated here.

## Next step

**No Critical/High findings — clear to advance to `11-release-readiness` for whatever release
bucket the user chooses to fold Infinite Mode into**, once (a) the Medium finding above is
addressed (a fast, metadata-only `05-feature-decomposition` touch-up — does not require another
integration-review cycle, per this skill's own gating rule which reserves the
07→08→09→re-review loop for Critical/High findings only) and (b) the user makes an explicit
release-bucket decision, since `FEAT-10000` currently sits in the `Future` bucket with "no
release commitment made" by its own catalog entry's design. Separately available, none blocking
this tranche: `09-content-review` on `IP-1081`/`IP-1082`'s shipped tile art (`BL-0097`, a
different, still-open tranche); `BL-0112` (the `FR-10400` run-end trigger) remains the Infinite
Mode tranche's own sole standing *implementation* gap — a deliberate, already-adjudicated scope
boundary (`IP-1103`'s own explicit routing), not a defect this review found, and not a blocker to
release-readiness consideration (a shipped win-condition *state* with no automatic trigger is an
honest, named partial-implementation, not a broken one).
