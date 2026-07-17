# Integration Review — Nine Biome-Family Identities + Procedural Music Generation Delta

## Scope

Eight packages, all `VERIFIED` on the Master Build Plan as of this review:

| Package | Arc | VR |
|---|---|---|
| `IP-1105` | (3) Nine biome-family identities | `VR-1105` |
| `IP-1033` | (3) | `VR-1033` |
| `IP-1022` | (3) | `VR-1022` |
| `IP-1106` | (3) | `VR-1106` |
| `IP-1110` | (4) Procedural music generation | `VR-1110` |
| `IP-1111` | (4) | `VR-1111` |
| `IP-9160` | remediation (`BL-0138`, zone-name restoration) | `VR-9160` |
| `IP-9150` | remediation (`BL-0134`, ROM hygiene) | `VR-9150` |

Reviewed against commit `01768f5` (tree head at review start). ROM rebuild confirmed
byte-identical to the checked-in `BunnyQuest.gbc` (sha256 match).

## Dimension 1 — Interface consistency

- **`ALL_SCREENS`**: unchanged 5 biome-family + 5 UI entries (`tilemaps.py:448`) — `IP-1022`'s own
  procedural-fill approach never added entries here, confirmed unchanged across the whole delta.
- **`ZONE_COLLECTS`**: 9 lists post-splice (`tilemaps.py:471`, `+= [...]` at `:556`) — `IP-1033`'s
  four staged lists and `IP-1022`'s splice agree exactly; `IP-1106`'s `inf_treasure_pos` re-derived
  against these nine type-2 entries independently in `VR-1106`, exact match.
- **Patch-point keys**: both `music_tbl` (`IP-1111`) and `zc_table` (`IP-1022`/pre-existing) are
  declared in `asm_game.py` and resolved in `build_rom.py` — confirmed both present and paired
  (`asm_game.py:1334`/`2133`, `build_rom.py:210`/`266`), same established pattern, no key collision.
- **Landmark-overlay list format** (`IP-1022`'s `ADR-0020` mechanism): `IP-9160` only appends
  entries to the four existing `*_LANDMARKS` lists, confirmed unchanged in shape.
- **Live cross-package seam, driven directly** (not merely inferred from separate VRs): entered
  Infinite Mode via the real MAIN MENU → MODE SELECT → INFINITE SEED ENTRY → PLAYING path, forced
  `INF_WINDOW`'s center cell to biome-id 5 (Village) after confirming `GAMESTATE == PLAYING` (a
  methodology correction was needed mid-review — an initial under-counted button sequence left
  the state machine in `INTRO`, producing a false blank-name read; corrected by verifying
  `GAMESTATE` explicitly before forcing, the same discipline `T26`'s own helpers already apply).
  Confirmed simultaneously, in one live session: (a) the Village family screen renders (tile-family
  audit), (b) the row-0 name region matches `village_screen()`'s own oracle exactly — `IP-1022`'s
  dispatch + `IP-9160`'s fix working together via the infinite-mode entry specifically, not just
  the finite path each package's own VR exercised — and (c) `MUSIC_PTR` (`0x2c8c`) sits inside
  `music_table[5]`'s own track (base `0x2c89`, read directly from the built ROM's own bytes, 3
  bytes advanced — one note played, consistent with `T28`'s documented live-cursor behavior) —
  `IP-1110`/`IP-1111`'s selection firing correctly from the same dispatch entry point. All three
  packages' effects are consistent and simultaneous at the one seam where they actually meet.

**Result: consistent, no defects found.**

## Dimension 2 — Invariant sweep

- **ROM size**: rebuilds to exactly 32768 bytes, valid header (sha256-identical to the checked-in
  binary).
- **VBlank/LCD-off gating**: `do_screen_redraw` disables LCDC at entry (`asm_game.py:1381`,
  `XOR_A; LDH_n_A(LCDC)`) and re-enables it at exit (`asm_game.py:1538`) — both `music_select`
  call sites (the default reset at `:1392` and the dispatch-entry override) execute entirely
  inside this bracket, confirmed by direct read: no VBlank-timing exposure (`NFR-1300`) introduced.
- **WRAM map**: this delta's one new field pair, `MUSIC_BASE_LO`/`MUSIC_BASE_HI` (`0xC6B3`/
  `0xC6B4`), sits immediately after `IP-1022`'s `FPS_TEMP` (`0xC6B2`) with no gap or overlap;
  both addresses appear in `GDS-07` (`docs/architecture/07-data-model.md:431`,`433`).
- **Tile-index budget**: `IP-9150`'s `TILE_DATA_TILES = 184` ceiling (2,944 bytes) comfortably
  covers the highest used index (181, `TL_TORCH`) with no interaction with this delta's other
  packages — none of them add new tiles.
- **One-job-per-file**: no module gained a second responsibility — `music_select` lives beside
  `music_tick` (existing music-playback code); `IP-9160`'s change is pure `tilemaps.py` data.
- **`NFR-1400`** (Infinite Mode region-materialization cycle budget, already `NOT MET` and
  accepted per `VR-1102`): `inf_mod9` (mod-9, up to 8 repeated-subtraction iterations) replaces
  `inf_mod5` (mod-5, up to 4) at the same single call site — a handful of extra cycles in the
  worst case, folded into an already-documented, already-accepted overage; does not change the
  accepted `NOT MET` status or require new escalation.

**Result: all invariants hold; no interaction found that breaks a permanent gate.**

## Dimension 3 — Behavioral coherence

- Full suite: **321/321** on the reviewed commit (`test_rom.py`), spanning every package's own
  suite (`T13`, `T22`/`T24`/`T26`–`T28`) run together in one tree — no cross-suite conflict.
- The live cross-package drive under Dimension 1 is this dimension's own strongest evidence: no
  player-visible workflow dead-ends at a seam (entering a newly-folded identity in Infinite Mode
  correctly renders its screen, its name, its treasure position, *and* its music together).
- No two packages implement overlapping behavior divergently — `IP-1022`'s dispatch cascade,
  `IP-1106`'s value-range widening, and `IP-1111`'s music selection each touch disjoint concerns
  at the same convergence point (`dsr_p_dispatch`, `A` = biome-id) without redefining each other's
  logic, confirmed by the diff-scope audits each package's own `VR-*` already performed
  independently.

**Result: coherent, no dead-ends or divergent implementations found.**

## Dimension 4 — Traceability coherence

- **RTM** (`docs/requirements/04-requirements-traceability-matrix.md`): `FR-4320`'s row correctly
  cites `IP-1033`/`IP-1022`/`IP-1106` as `VERIFIED`, but still shows **`IP-9160 (COMPLETE)`**
  rather than `VERIFIED` — a one-cell staleness left over from this session's own `VR-9160` pass
  (the correction was made to the packages `INDEX.md`/Master Build Plan rows but missed this RTM
  cell). `FR-7110`'s row correctly shows `IP-1111 (VERIFIED, VR-1111)`.
- **Master Build Plan** / **`packages/INDEX.md`**: all eight packages agree `VERIFIED` with
  matching VR links, cross-checked directly (script comparison, no mismatches beyond the RTM cell
  above).
- **`ROADMAP.md`**'s `IM-00`/`IP-xxxx` narrative rows are stale — last updated for the delta's
  interim state ("37 packages total, 31 VERIFIED, 3 COMPLETE, 3 BLOCKED", predating this session's
  four verification passes). This is the same standing, recurring class of drift the backlog
  already tracks under the doc-accuracy sweep family (`BL-0136` and its predecessors, e.g.
  `BL-0035`/`BL-0041`) — not a new defect, but this delta's own portion of it is now confirmed
  stale too.

**Result: one small RTM cell staleness (Low); the pre-existing `ROADMAP.md` staleness pattern is
reconfirmed, not newly introduced.**

## Dimension 5 — Documentation coherence

- **`memory.md`**'s "Collectible Positions" section (the file's own quick-reference for
  `ZONE_COLLECTS`) still states `ZONE_COLLECTS` "has 5 biome-family-representative lists" and
  describes `IP-1033`'s four lists as "staged not wired... unreferenced by any code path until
  `IP-1022` splices them in" — but `IP-1022` shipped and was `VERIFIED` this same delta;
  `ZONE_COLLECTS` has carried all nine lists in the real array since. This quick-ref was written
  when `IP-1033` really was staged-only and was never updated once `IP-1022` shipped — a genuine,
  reachable-by-a-future-agent staleness (the exact kind this file exists to prevent, now itself
  stale).
- **`Claude.md`**'s "Known Good Behavior" section correctly scopes itself to Baseline/Release
  1/Release 2 only — this delta is not yet part of a GO'd release, so its absence there is
  expected, not a defect (the standing G4 question governs when/whether that changes).
- No mention of the `music_select`/sub-theme-playback mechanism anywhere in `Claude.md`'s "How to
  Change Things" section (e.g. no "Edit music" update for the new per-biome selection) — a
  completeness gap, not an inconsistency (the existing "Edit music" section is still accurate for
  editing the theme's own note data, just silent on the new selection layer).

**Result: one Medium finding (`memory.md` stale quick-ref), one Low finding (`Claude.md` completeness gap).**

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| 1 | RTM `FR-4320` row, `IP-9160` | RTM cell still reads `IP-9160 (COMPLETE)`; should read `VERIFIED` per `VR-9160` — a one-cell correction missed during this session's own verification pass | Low | `04-requirements-engineering` (or a direct correction on the next touch to this row) |
| 2 | `memory.md` "Collectible Positions" | Quick-reference still describes `ZONE_COLLECTS` as 5 lists with `IP-1033`'s four lists "staged not wired," stale since `IP-1022` shipped and spliced them into the real 9-list array this same delta | Medium | Doc-accuracy sweep (the `BL-0136` family) — `memory.md` maintenance has no dedicated numbered skill; route via `00-intake`/manager triage |
| 3 | `ROADMAP.md` `IM-00`/`IP-xxxx` rows | Narrative rows stale at this delta's interim state (pre-dates all four of this session's verification passes) — reconfirms the standing, already-tracked doc-accuracy pattern (`BL-0136` and predecessors), not a new defect | Low | Doc-accuracy sweep (`BL-0136` family) |
| 4 | `Claude.md` "How to Change Things" § Edit music | No mention of the new per-biome sub-theme selection mechanism (`music_select`) — a completeness gap for a future agent editing music-selection behavior specifically | Low | Doc-accuracy sweep (`BL-0136` family) or a small dedicated doc touch |

No Critical or High findings. No integration defect found in shipped code — every cross-package
seam actually exercised (interface, invariant, behavioral) held.

## Test run

- `python3 build_rom.py` → 32768 bytes, valid header, sha256-identical to `BunnyQuest.gbc`.
- `python3 test_rom.py` → **321/321 passed, 0 failed**.

## Ledger updates

`ROADMAP.md`'s reviews row updated to record this review (see diff).
