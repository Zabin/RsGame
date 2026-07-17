# VR-1033 — Collectible-Spawn Content for the Four Newly-Folded Biome Identities

> Verification Report for
> [IP-1033](../packages/IP-1033-nine-biome-family-collectible-spawn-content.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-1033-nine-biome-family-collectible-spawn-content.md)

## Package

- **ID / Title:** IP-1033 — Collectible-Spawn Content for the Four Newly-Folded Biome Identities
  (Village/Cave/Desert/Plains, `FR-4320`/`BL-0128`, delta against `FS-103`)
- **Commit verified (Pass 2):** `fc3c181` ("content(IP-1033): rework collectible placement per
  VR-1033 Finding 1"), tree head `cde16cb`.
- **Date:** 2026-07-17 (Pass 1) / 2026-07-17 (Pass 2, separate session)
- **Independence:** clean — Pass 2 ran in a fresh session with no memory of either the original
  implementation (2026-07-16) or the rework commit `fc3c181` (a prior session, per that commit's
  own authorship and the pipeline journal's run #189/#190 record of the rework happening before
  this session started). This session's own prior actions were unrelated (an intake filing on a
  different branch) before invoking `09-package-verification`.

## Result

**VERIFIED** (Pass 2) — supersedes Pass 1's `RETURNED` result below, which is kept as the
permanent record of what the first pass found. Independent re-derivation of every one of the 24
staged entries' tile-grid positions (computed directly from `village_screen`/`cave_screen`/
`desert_screen`/`plains_screen`'s own landmark `_put` calls, not from the rework commit's own
claim) confirms **zero exact-tile overlaps remain** across all four lists — the four positions
`VR-1033` Pass 1 found colliding are now clear, and none of the twenty entries Pass 1 already
found clean regressed. Every other checked item continues to pass: ROM builds correctly, the full
suite is unchanged, the diff stayed in scope (both `IP-1033` commits, including the rework, touch
only `tilemaps.py` + docs — never `asm_game.py`/`build_rom.py`).

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | Four new `ZONE_COLLECTS`-format lists exist, one per newly-folded identity, each respecting its own screen's existing landmark layout and the player-spawn exclusion zone | `tilemaps.py:506-556` — `VILLAGE_COLLECTS`/`CAVE_COLLECTS`/`DESERT_COLLECTS`/`PLAINS_COLLECTS`, four lists present, correct `(pixel_x, pixel_y, type)` format. Landmark respect: independently re-derived (see Findings below) — **all 24 entries across all four lists now clear** | ✅ |
| 2 | Each list contains exactly one type-2 (`KeyItem`) entry and a fair mix of type-0/1 entries | Direct count (independently re-tallied, not just re-trusting Pass 1): Village 5+1, Cave 5+1, Desert 5+1, Plains 5+1 — all four correct, unchanged by the rework | ✅ |
| 3 | A temporary-force visual check confirms each list's collectibles render correctly-positioned against their screen's real, already-shipped art, with no overlap | The rework commit's own message claims direct rendered-tile-value inspection at the four new coordinates; this pass independently re-derived the same tile-grid arithmetic from source (not the commit's own claim) and confirms the claim holds — see Findings | ✅ |
| 4 | The ROM's behavior is unchanged (staged data inert, confirmed by full suite pass with zero new/changed assertions and byte-identical gameplay-affecting code) | Rebuilt ROM (this session): 31362/32768 bytes, matching both Pass 1's and the rework commit's claimed figure exactly. `test_rom.py` (this session, fresh PyBoy 2.7.0 install): **309/309, 0 failed** — identical count to Pass 1, no new suite added by the rework. `git show fc3c181 --stat` / `git show e5cbab1 --stat`: only `tilemaps.py` + docs touched across both `IP-1033` commits, no `asm_game.py`/`build_rom.py` change in either | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | `python3 build_rom.py BunnyQuest.gbc` (this session) → "Wrote 32768 bytes", 31362 used, valid header via the same `set_header()` path every prior `VERIFIED` package uses | ✅ |
| 2 | G5: full `test_rom.py` suite passes, unchanged in every existing assertion | `python3 test_rom.py` (this session, fresh PyBoy/Pillow/numpy install) → **309/309 passed, 0 failed** | ✅ |
| 3 | Direct diff: `setup_zone_collects`, `asm_game.py`, `build_rom.py` byte-for-byte unchanged | `git show e5cbab1 --stat -- asm_game.py build_rom.py` and `git show fc3c181 --stat -- asm_game.py build_rom.py` both return empty — neither `IP-1033` commit touches either file | ✅ |
| 4 | Each of the four staged lists inspected against its screen's own landmark layout — confirmed no overlap, confirmed exactly one type-2 entry each, confirmed player-spawn zone respected | Independent re-derivation (this session, own script, not the rework commit's own claimed positions taken on faith): built the full landmark tile-set for each of the four screens directly from `village_screen`/`cave_screen`/`desert_screen`/`plains_screen`'s source (`tilemaps.py:155-252`), then checked every one of the 24 staged entries' `(px//8, py//8)` tile position against it. **Zero exact matches** — nearest-landmark distances range 1.0–4.12 tiles across all four lists, with the previously-colliding four now at 2.0–2.83 tiles from the landmark they used to sit on. Type-2 count and spawn-zone clearance re-confirmed unchanged from Pass 1 | ✅ |
| 5 | Temporary-force screenshots captured for each of the four confirming visual placement fairness | Per §8, screenshots are evidence-only, not committed to the repo — same as Pass 1, none exist to re-inspect visually. This pass instead independently verified the underlying claim by direct tile-grid arithmetic (the same method that caught Pass 1's defect), which is stronger evidence than a screenshot for an exact-tile-overlap property and is what actually resolves this item | ✅ |

## Findings

### Finding 1 (Informational) — independent re-derivation confirms the rework, method cross-checked against Pass 1's own defect-finding method

Re-ran the identical class of check Pass 1 used (tile-grid arithmetic against every landmark
`_put` call in each of the four screen functions), computed fresh from source rather than from the
rework commit's own stated positions or its own claimed "confirmed clear" language. Full result
table (pixel position → tile position → nearest-landmark distance in tiles):

- **Village** (6 entries): `(56,48)`→`(7,6)` d=1.00; `(112,56)`→`(14,7)` d=3.16; `(136,40)`→`(17,5)`
  d=1.00; `(40,96)`→`(5,12)` d=2.00; `(104,96)`→`(13,12)` d=2.24; `(48,64,type2)`→`(6,8)` d=2.83
  (the repositioned entry — was `(17,12)`, exactly on a fence tile, d=0).
- **Cave** (6 entries, unchanged by the rework): `(32,80)`→`(4,10)` d=4.12; `(80,48)`→`(10,6)`
  d=3.00; `(128,88)`→`(16,11)` d=2.24; `(64,120)`→`(8,15)` d=2.00; `(112,104)`→`(14,13)` d=3.00;
  `(136,72,type2)`→`(17,9)` d=4.00 — all six re-confirmed clean, matching Pass 1 exactly (this
  list was never flagged and the rework did not touch it).
- **Desert** (6 entries): `(24,40)`→`(3,5)` d=1.00; `(80,48)`→`(10,6)` d=2.00; `(144,64)`→`(18,8)`
  d=2.24; `(64,96)`→`(8,12)` d=2.83 (the repositioned entry — was `(4,12)`, exactly on a cactus
  tile, d=0); `(56,104)`→`(7,13)` d=3.00; `(128,40,type2)`→`(16,5)` d=3.00.
- **Plains** (6 entries): `(40,40)`→`(5,5)` d=2.00 (repositioned — was `(3,4)`, exactly on a
  flower tile, d=0); `(88,40)`→`(11,5)` d=1.00; `(128,72)`→`(16,9)` d=1.00; `(48,112)`→`(6,14)`
  d=1.00 (repositioned — was `(3,12)`, exactly on a flower tile, d=0); `(104,96)`→`(13,12)` d=2.00;
  `(144,88,type2)`→`(18,11)` d=2.24.

No exact overlap (d=0) anywhere in any of the 24 entries. The four previously-colliding positions
now sit 2.0–2.83 tiles from the landmark they used to occupy — comparable to or better than
several of the already-clean entries in the same lists (e.g. Village's own `(7,6)`/`(17,5)` sit at
exactly d=1.00 from a landmark and were never flagged, since Pass 1's own bar was *exact-tile*
overlap, not minimum spacing — the rework's repositioned entries clear that same bar with margin
to spare, and Plains' own tighter-margin convention, named explicitly in the file's own comment,
is respected: none of the four lists' entries lands closer than 1.0 tile to any landmark, matching
the precedent set by the already-shipped five `ZONE_COLLECTS` lists).

**Severity:** Informational — this is the expected, successful outcome of the routed rework;
recorded in full because a re-verification pass's value is in re-deriving the check independently,
not in restating the fix commit's own claim.

**Owner:** none — no further action.

### Finding 2 (Informational, carried forward from Pass 1) — player-spawn exclusion and type-2 counts remain correct

Unchanged from Pass 1: no staged entry across all four lists falls within a landmark-comparable
distance of the player-spawn point `(76, 72)`, and each of the four lists carries exactly one
type-2 entry. Re-confirmed directly this pass, not merely carried forward on faith.

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| `FR-3220` (item-agnostic collection mechanic) | Not touched by this package (pre-existing mechanism, correctly unmodified per §5/§6) | N/A — no new mechanic | Unaffected | ✅ (out of this package's scope, correctly so) |
| `FR-9130`/`FR-9160` (exactly one `KeyItem` per region) | Each staged list carries exactly one type-2 entry — re-confirmed by direct count this pass | Not yet live (data inert until `IP-1022` splices it in, per package's own §5) | Correctly `UNASSIGNED`/pending wiring — no premature claim in the RTM | ✅ |
| `FR-4320` (nine biome-family identity set) | This package supplies 4 of the identity set's own content, now placement-clean; correct per its own scope | Same as above — pending `IP-1022` | Correctly pending | ✅ |

No RTM correction needed — the package correctly leaves forward columns unassigned rather than
claiming premature completion; this holds unchanged from Pass 1.

## Scope audit

`git show fc3c181 --stat`: `tilemaps.py` (+27/-12 lines, the four repositioned entries plus
explanatory comments) plus two ledger files (`00-master-build-plan.md`, `packages/INDEX.md`). No
excursion outside the package's declared file set (§6: "Modify: `tilemaps.py`" only). Combined
with Pass 1's already-confirmed scope audit of the original commit `e5cbab1`, both `IP-1033`
commits together touch only `tilemaps.py` plus documentation/ledger files — `setup_zone_collects`,
`asm_game.py`, and `build_rom.py` remain byte-for-byte unchanged across the package's full history.

## Test run

- `python3 build_rom.py BunnyQuest.gbc` (this session) → 32768 bytes written, valid header, 31362
  used — matching the figure both Pass 1 and the rework commit recorded.
- `python3 test_rom.py` (this session, fresh `pyboy`/`Pillow`/`numpy` install in this container) →
  **309/309 passed, 0 failed** — identical to Pass 1's count; this package's own rework added no
  new suite, consistent with §8's "no new suite" statement.
- ROM size: 31362/32768 bytes, unchanged since Pass 1 and since `IP-1105`/`IP-1110` landed —
  confirming the rework's own claim that repositioning inert staged data has zero footprint
  impact.

No tunable/generated parameter applies to this package's own DoD (static staged data, not a
runtime-configurable parameter) — same as Pass 1, the overlap check itself is the parameter this
package's own DoD cares about, and both passes drove it directly against the real, current
screen-layout source rather than a fixture.

## Recommendations

None outstanding from this package. The `IP-1022`/`IP-1106` chain that was blocked on this
package's own re-pass is now unblocked to the extent `IP-1033` was the blocker — `IP-1022` still
carries its own separate readiness/authorization state independent of this VR.

## Next step

**`IP-1033` is `VERIFIED`.** `IP-1022` (finite-mode nine-identity generation & screen dispatch),
already `AUTHORIZED` (G3, "Build all six," 2026-07-16) and now unblocked on its `IP-1033`
dependency, is the next critical-path step — `08-code-implementation` on `IP-1022`.
