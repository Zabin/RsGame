# IP-1070 — Maze-Shaped Region Adjacency

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-1070` — implements
[**FS-107**](../../features/FS-107-maze-shaped-region-adjacency.md) (`FEAT-9100`, Epic `EP-5000`,
Release 2 post-ship addendum). Resolves FS-107 Open Questions 1–3 — see the
[Technical Work Breakdown](../01-technical-work-breakdown.md)'s "Maze-shaped region adjacency
(FS-107, planned 2026-07-11)" section for the full reasoning; this package states only the
resulting concrete design.

## 2. Objective

Extend `generate_world` (`asm_game.py`) and its `worldgen.py` oracle mirror with a second,
independent generation pass: after biome assignment completes unchanged, carve a spanning tree
over the `WORLD_SCALE`×`WORLD_SCALE` region grid via randomized DFS/recursive backtracker, then
run a braid pass reopening a fixed fraction of the pruned edges — replacing today's full-lattice
`REGION_GRAPH` adjacency with a generated maze, per `ADR-0012`.

## 3. Requirements Covered

FR-9140, FR-9150 (FS-107's full Included-Requirements set).

## 4. Architecture Components

`ADR-0012` (algorithm choice, pass ordering, data-format non-change) · `ADR-0009` point 1 (refined,
not reversed) · GDS-04 delta (`Region`'s "generated adjacency edges" becoming selective) · GDS-07
§6 (WRAM layout — this package proposes the new transient-scratch addresses) · GDS-09 (`worldgen.py`
contract, extended in place) · `R112` (algorithm/WRAM-cost grounding) · `R111` (existing PRNG).

## 5. Interfaces

- **`worldgen.py`'s existing confirmed contract** (`generate(seed: int, scale: int) -> list[dict]`)
  — extended in place: each region `dict`'s `'neighbors'` field reflects the maze's subgraph, same
  shape.
- **No new `patches` dict key** — entirely WRAM working-set data, mirroring `IP-1020`'s own OQ3
  resolution (no ROM-resident table needed).
- **`dsr_p`/`draw_region_arrows`/`check_zone_transition`** — confirmed by direct re-read of
  `asm_game.py` (lines 594–836, 885+) to consume `REGION_GRAPH`'s neighbor bytes generically (any
  0–80 value or `0xFF`); **zero changes**, per `ADR-0012` point 2.

## 6. Files to Create/Modify

- **Modify: `asm_game.py`**:
  - WRAM constants block (after `GW_SCALE_SQ = 0xC27C`, before `MM_SAVE_VALID`): add new
    **maze-generation transient scratch**, placed starting at `0xC3A0` — the first byte after
    `OAM_BUF`'s own confirmed 160-byte extent (`0xC300`–`0xC39F`), the next unclaimed WRAM
    following the live `asm_game.py` WRAM-constants block read start-to-finish for this package
    (nothing is allocated past `OAM_BUF` today). This resolves FS-107 Open Question 2. Proposed,
    not yet built — confirmed once the routine's exact code size/scratch footprint is known, per
    `IP-1020`'s own established confidence precedent for new WRAM entities:
    - `GW_MAZE_STATE = 0xC3A0` — up to 81 bytes, one per region: **bit 7 = visited**, **bits
      1:0 = parent-direction** (`0`=up, `1`=down, `2`=left, `3`=right — matching `REGION_GRAPH`'s
      own byte-order convention exactly), meaningful only when bit 7 is set. Combines FS-107 OQ1's
      "visited flag" and the backtracking parent-pointer into a single byte per region (81 bytes
      total) rather than two separate arrays — resolves OQ1 in favor of the simplest correct
      encoding (not the further bit-packed-to-11-bytes option R112 also named): headroom is ample
      (3168 bytes/3.09 KiB free, `NFR-4200`) and a single-byte-per-region layout needs no
      additional shift/mask overhead beyond the 2-bit direction extraction already required to
      use the value at all.
    - `GW_CUR_REGION = 0xC3F1` — 1 byte, the current-region pointer during tree construction.
    - `GW_MAZE_DIR = 0xC3F2` — 1 byte, scratch holding the mod-4 direction draw and the loop index
      while trying up to 4 directions in rotation.
    - `GW_BRAID_IDX = 0xC3F3` — 1 byte, the braid pass's own region-loop counter (comparable in
      role to `GW_REGION_IDX`'s existing transient-scratch pattern).
  - **`generate_world`, inserted between the existing biome-assignment loop (`gw_loop`, ends at
    the existing `rom.RET()` after `gw_no_row_wrap`/`gw_loop`'s termination check) and that
    `RET()`** — the existing loop is **entirely unchanged** (per `ADR-0012` point 1): it still
    writes both the biome-id byte and the full-lattice up/down/left/right candidate bytes into
    `REGION_GRAPH` exactly as today. This package's new code runs immediately after, before the
    routine returns:
    1. **Zero `GW_MAZE_STATE`** for all `scale²` regions (a region count already known from
       `GW_SCALE_SQ`, computed by the existing loop).
    2. **Mark region 0 visited** (`GW_MAZE_STATE[0]` bit 7 = 1; parent-direction bits left at 0,
       disambiguated from a real "up" parent by region 0's own index — see task 4 below, resolving
       FS-107 Open Question 3). Set `GW_CUR_REGION = 0`.
    3. **Spanning-tree carve loop** (iterative — no `CALL`-based recursion, per `ADR-0012` point 3):
       at `GW_CUR_REGION = R`, draw one PRNG byte (`gw_prng_step`, already exists) and mask it
       `AND 3` for a starting direction `D0` (`GW_MAZE_DIR`). Try directions `D0`, `(D0+1) mod 4`,
       `(D0+2) mod 4`, `(D0+3) mod 4` in turn: for each tried direction `Di`, read `REGION_GRAPH[R]`'s
       existing candidate byte at slot `Di` (still the full-lattice value the unchanged loop wrote —
       this package reads it as the "does a grid-adjacent region exist here" test, resolving the
       cost R112 flagged for a fresh `(row,col,scale)` re-derivation: reusing the already-written
       byte is strictly cheaper and exactly as correct). If the candidate is `0xFF`: try the next
       direction. Else let `V` = the candidate region index; if `GW_MAZE_STATE[V]` bit 7 is already
       set (visited): try the next direction. Else: **carve** — set `GW_MAZE_STATE[V]` bit 7 = 1,
       parent-direction bits = `opposite(Di)` (`up`↔`down`, `left`↔`right`); set `GW_CUR_REGION = V`;
       restart the direction draw at the new current region (go to the top of this step). If all 4
       directions are exhausted with no carve: **backtrack** — if `R` is region 0 (the root) and no
       candidate was found, the tree is complete, proceed to task 4; otherwise, set
       `GW_CUR_REGION` to `R`'s own parent (`REGION_GRAPH[R]`'s candidate byte at the slot named by
       `GW_MAZE_STATE[R]`'s own parent-direction bits — "re-reading the just-carved edge's own
       reverse direction," `ADR-0012` point 3's cited technique) and retry the direction draw
       there.
    4. **Prune pass** (a single `O(scale²×4)` sweep, but only the two "canonical" directions per
       region — `down` and `right` — are evaluated, so each undirected edge is visited exactly
       once, never twice from opposite ends): for every region `R`, for `Di` in `{down, right}`:
       let `V` = `REGION_GRAPH[R]`'s existing candidate at slot `Di`. If `V == 0xFF`: leave
       unchanged (true grid boundary, already correct). Else, determine whether `(R,Di)` is a
       **tree edge**: true iff `GW_MAZE_STATE[V]` bit 7 is set and its parent-direction equals
       `opposite(Di)` (i.e. `V`'s recorded parent is `R`, reached via this exact edge) — this
       single check correctly identifies every tree edge, since every non-root region's parent-
       direction was set at carve time in task 3. If it **is** a tree edge: leave both
       `REGION_GRAPH[R]`'s `Di` slot and `REGION_GRAPH[V]`'s `opposite(Di)` slot unchanged (both
       already hold the correct, live values from the unchanged biome-loop write). If it is **not**
       a tree edge (a pruned candidate): draw one PRNG byte (`gw_prng_step`) and compare against
       the braid-fraction threshold (`FR-9150`, a fixed ROM constant, task 6 below); if the drawn
       byte is at or below the threshold, **reopen** — leave both slots unchanged (braided back
       in); otherwise **prune** — write `0xFF` into both `REGION_GRAPH[R]`'s `Di` slot and
       `REGION_GRAPH[V]`'s `opposite(Di)` slot. **Both slots of an undirected edge always receive
       the same keep/prune decision** — this is what keeps `REGION_GRAPH` symmetric (if `V` is
       reachable from `R`, `R` is reachable from `V`), matching today's shipped full-lattice
       model's own always-symmetric property; evaluating only `down`/`right` per region (never
       `up`/`left`) is what guarantees each edge is decided exactly once, not twice with a risk of
       disagreeing outcomes.
  - **New label `gw_braid_threshold`** (a ROM constant, not a WRAM address): the braid-fraction
    byte value `FR-9150` establishes, resolving that FR's own fixed-default Notes field —
    concretely, a single-byte constant emitted inline (no new WRAM/SRAM cost) chosen so that
    roughly one quarter of pruned edges reopen (`threshold ≈ 63` out of the PRNG byte's full
    0–255 range, `256×0.25 − 1`).
- **New in: `worldgen.py`** — a `_carve_maze(regions, scale, x)` step, added after `generate()`'s
  existing biome-assignment loop and before it builds/returns the `regions` list (or, more simply
  given the Python structure already separates biome computation from the `regions` list build at
  line 80: run maze carving as a mutation over the already-built `neighbors` lists, using the
  identical algorithm task 3/4 above describes, in the identical step order — same starting
  direction draw, same canonical `down`/`right` prune-pass order — so the oracle and the SM83
  routine stay in lockstep (`ADR-0012` point 7). A Python `visited: set[int]` and
  `parent_dir: dict[int,int]` stand in for `GW_MAZE_STATE`'s bit-packed WRAM encoding — same
  logical state, natural Python representation, not required to bit-pack identically to the SM83
  side (the oracle only needs to produce the identical *output* graph, not identical internal
  representation).
- **No change to `test_rom.py`'s T12 suite** — confirmed by direct read (`test_rom.py:799–819`):
  `T12.c` (reachability) and `T12.d` (grammar-validity) both already iterate only over each
  region's **existing** (non-`None`) neighbor entries, never asserting a candidate exists — both
  checks remain correct, unchanged, against this package's sparser output. A genuine "found
  nothing needing change" result from this package's own supersession-adjacent check.
- **Modify: `test_rom.py`** — add new suite **T19** (see §8).

## 7. Implementation Tasks

**Verb inventory:** this capability is pure **generate** — `render`/`navigate`/`persist`/`review`
all get an explicit deferral-not-applicable note, not silence: `render` (`dsr_p`/
`draw_region_arrows`) and `navigate` (`check_zone_transition`) both already consume `REGION_GRAPH`
generically and need zero code changes (`ADR-0012` point 2, confirmed by direct re-read, §5);
`persist` does not apply — `REGION_GRAPH` is never persisted to SRAM, regenerating from
`(SEED, WORLD_SCALE)` on every load including this package's own maze pass (`ADR-0012` point 6);
`review` (`09-content-review`) does not apply — this package adds no new tile art, screen, or
rendered content of its own (the FEAT-2100/FS-108 blocked-edge *indicator* is a separate Feature,
package, and eventual content-review target).

**Supersession sweep:** this package does not retire an existing model the way `IP-9050` did
(full-lattice adjacency was never itself asserted as an invariant anywhere outside
`generate_world`'s own writing of it) — but a sweep was still run, per this skill's own mandatory
rule, to confirm nothing else assumes full connectivity: `dsr_p`/`draw_region_arrows`/
`check_zone_transition` (`asm_game.py`) — generic `REGION_GRAPH`-neighbor-byte consumers, no
full-lattice assumption (§5); `tilemaps.py` — screen selection keys off biome-id only, never
adjacency; `test_rom.py`'s `T12` suite — confirmed clean, iterates existing edges only (§6). **No
other call site found; sweep confirmed clean.**

Ordered: (1) new WRAM constants (`GW_MAZE_STATE`/`GW_CUR_REGION`/`GW_MAZE_DIR`/`GW_BRAID_IDX`,
§6); (2) the spanning-tree carve loop, appended to `generate_world` after the existing
biome-assignment loop; (3) the canonical-edge prune pass, including the `gw_braid_threshold`
constant; (4) `worldgen.py`'s `_carve_maze`, written against tasks 2–3's exact step order and
cross-checked line-by-line before task 6 — the oracle-vs-SM83 lockstep is this package's single
most load-bearing correctness property (FS-107 §14), exactly as `IP-1020`'s own §7 already
established for biome assignment; (5) rebuild ROM; (6) author T19; (7) full suite run; (8)
documentation/traceability updates (§9).

## 8. Tests to Add

New `test_rom.py` suite **`T19: Maze-Shaped Region Adjacency`**, implementing FS-107's
Verification Plan against a corpus extending T12's own (`R305`'s adequate-not-unbounded
convention): at minimum `scale ∈ {2, 3, 9}`, seeds including `0`, plus at least one run at each
braid-fraction extreme (0 — a pure spanning tree — and the maximum, full-lattice-equivalent) in
addition to the fixed default threshold.

- T19.a — **subgraph-of-full-lattice**: for every corpus entry, every edge in the generated
  `REGION_GRAPH` also appears in the full grid-adjacency set computed independently from
  `(row, col, scale)` arithmetic (FS-107 AC-1) — a new check, the prior full-lattice model made
  this trivially true and untested.
- T19.b — **reachability**: direct extension of `T12.c`'s existing graph-traversal check, re-run
  against the maze-sparsified graph (FS-107 AC-2) — the check itself is unchanged (§6).
- T19.c — **determinism**: direct extension of `T12.a`/`T12.b`'s existing two-boot and
  oracle-vs-SM83 comparison pattern, extended to include the maze pass's own output (FS-107 AC-3).
- T19.d — **grammar-validity non-regression**: direct extension of `T12.d`, confirming it still
  holds for whichever edges the maze pass keeps (FS-107 AC-4) — the check itself is unchanged
  (§6).
- T19.e — **braid-fraction statistical check**: for a large `(seed, scale)` sample at the fixed
  default threshold, count reopened (non-tree) edges and assert the observed fraction falls within
  a defined statistical tolerance band (FS-107 AC-5, `FR-9150`'s own probabilistic Acceptance
  Criteria — not exact-equality).
- T19.f — **determinism static audit** (Inspection): direct code read confirming the new pass
  reads no `DIV`/uninitialized WRAM (FS-107 AC-6, extends `T12.h`'s pattern).
- T19.g — **headroom audit** (Inspection): direct WRAM-layout audit at `scale=9` confirming
  `GW_MAZE_STATE`–`GW_BRAID_IDX`'s extent (`0xC3A0`–`0xC3F3`, 84 bytes worst case) stays inside
  bank-0 without `SVBK` banking (FS-107 AC-7, extends `T12.i`'s pattern).

## 9. Documentation Updates

- `docs/architecture/07-data-model.md` (GDS-07 §6): add the confirmed `GW_MAZE_STATE`/
  `GW_CUR_REGION`/`GW_MAZE_DIR`/`GW_BRAID_IDX` WRAM entries at `0xC3A0`–`0xC3F3`, transient
  scratch, not part of the persisted data model — same framing as the existing `GW_TOP_ROW`
  family.
- `docs/requirements/01-functional-requirements.md`: FR-9140/FR-9150 Notes → implemented, status
  updated.
- `docs/requirements/02-non-functional-requirements.md`: NFR-4200 Notes extended with this
  package's actual measured WRAM addition (84 bytes) once built.
- `docs/requirements/04-requirements-traceability-matrix.md`: FR-9140/FR-9150 rows → `IP-1070`/T19.
- `docs/features/FS-107-…md` metadata: implemented-by pointer; Open Questions 1–3 marked resolved,
  citing this package's §6 design.
- Master Build Plan status row; `packages/INDEX.md`.

## 10. Definition of Done

- All seven FS-107 Acceptance Criteria demonstrably pass via T19.
- ROM builds at 32768 bytes; full suite passes headless.
- `worldgen.py`'s `_carve_maze` and the SM83 routine's new pass produce byte-identical
  `REGION_GRAPH` output for the full T19 corpus (T19.c) — the lockstep property proven, not
  assumed.
- `T12`'s existing suite (unchanged) continues to pass unmodified against the new sparser graph —
  confirms the "no change needed" supersession-sweep finding (§7) empirically, not just by
  inspection.
- No new `patches` dict key; `dsr_p`/`draw_region_arrows`/`check_zone_transition` files show zero
  diff.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes (T1–T19).
- [ ] T19.a–g each present and passing (map 1:1 to FS-107 AC-1…7).
- [ ] Direct code read: the new pass reads no `DIV`/uninitialized WRAM.
- [ ] Direct code read: `GW_MAZE_STATE`'s prune-pass logic evaluates each undirected edge exactly
      once (`down`/`right` only) — no region's `up`/`left` slot is independently decided.
- [ ] `worldgen.py`'s `_carve_maze` step order (starting-direction draw, rotation order, canonical
      prune-pass direction pair) matches `generate_world`'s new pass, confirmed by direct
      side-by-side read, not only by T19.c's output match.
- [ ] `asm_game.py`'s `dsr_p`/`draw_region_arrows`/`check_zone_transition` show zero diff from this
      package (confirms §5/§7's "zero changes" claim empirically).
- [ ] BL-0019/NFR-4200 rider: WRAM headroom re-affirmed — this package's actual new-WRAM byte
      count against the confirmed ~3.09 KiB bank-0 headroom.
- [ ] GDS-07/RQ-01/RQ-02/RQ-04/FS-107/Master-Build-Plan deltas applied exactly as §9 names.

## 12. Dependencies

- **IP-1020** (`VERIFIED`) — this package's entire new pass runs inside `generate_world`,
  immediately after `IP-1020`'s own biome-assignment loop, and reads `REGION_GRAPH`'s already-
  written candidate bytes as its own input.
- **IP-1030, IP-1040, IP-1050** (all `VERIFIED`) — no functional dependency (this package touches
  neither rendering nor the SEED/SCALE ENTRY UI nor save/load), but all four are required
  `VERIFIED` transitively via `IP-1020`'s own already-confirmed dependency chain, per this
  project's standing convention of listing the full verified foundation a new package builds on.
- **IP-9050, IP-9070** (`COMPLETE`, not yet `VERIFIED`) — not a functional dependency (this
  package doesn't touch `check_zone_transition`/`SCOREITEM_FLAGS`), named here only because both
  sit in the same file (`asm_game.py`) this package also edits; no shared line range, no merge
  risk.

## 13. Risks

- **Genuinely new algorithm family for this codebase** (Low-Medium, carried from FEAT-9100's own
  catalog assessment) — mitigated by `R112`/`ADR-0012` already resolving the hardware-fit question
  decisively; this package's own remaining design latitude (§6's task 3/4 algorithm) was chosen for
  minimal WRAM/write cost (reusing the biome-loop's already-written candidate bytes rather than
  re-deriving grid adjacency, deciding each undirected edge exactly once) rather than invented from
  scratch.
- **Oracle/SM83 lockstep drift** (carried from FS-107 §18) — mitigated identically to `IP-1020`'s
  own §13: both implementations authored together, cross-checked line-by-line, T19.c's explicit
  byte-for-byte parity check (not merely internal self-consistency of either side alone).
- **The starting region's own no-parent termination condition** (§6 task 3's final `else` branch) —
  a genuine new edge case this codebase's existing `generate_world` loop never had (it has no
  backtracking of its own). Mitigated by T19.b's reachability check, which would fail loudly if the
  termination condition were wrong (either an infinite loop, caught by a test timeout, or a
  prematurely truncated tree, caught by an unreachable region).
- ROM budget: a new code-only pass (spanning-tree carve + prune sweep), no precomputed map data —
  expected to be a modest ROM addition (comparable in scale to `IP-9050`'s `check_zone_transition`
  rewrite, not a new subsystem); exact delta is an implementation-time measurement. WRAM growth: up
  to 84 bytes worst case at `scale=9` (§11), trivial against the confirmed ~3.09 KiB headroom.

## 14. Rollback Considerations

Revert `asm_game.py`/`worldgen.py`/`test_rom.py` and rebuild. No save-format change in this
package (`REGION_GRAPH` is never persisted, unaffected by this package's own determinism
guarantee, `ADR-0012` point 6) — no save-compatibility concern from a rollback of this package
alone. `FEAT-2100`/`FS-108`'s own package (`IP-1080`) depends on this package reaching at least
`COMPLETE`; a rollback here would need to re-block `IP-1080` in turn.
