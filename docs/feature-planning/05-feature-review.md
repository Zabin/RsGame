# FP-05 — Feature Review

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07); re-run 2026-07-10 (procgen-world
> increment delta + `BL-0036` correction; finding #5 resolved, `BL-0037`); re-run 2026-07-11
> (`ADR-0012` maze-adjacency remediation delta — see finding #7); re-run 2026-07-13
> (edge-indicator legend screen delta, `FEAT-1200` — see finding #8); re-run 2026-07-14 (Infinite
> Mode delta, `FEAT-10000`/`EP-6000` — see finding #9; also closes `BL-0102`'s tally gap); re-run
> 2026-07-14 (cont'd) (`FEAT-10000`'s missing `FEAT-4100` dependency corrected — see finding #10,
> closes `BL-0111`); re-run 2026-07-16 (Procedural Music Generation delta, `FEAT-7100`/`EP-7000`
> — see finding #11); re-run 2026-07-17 (Infinite Mode combat sub-mode delta, `FEAT-11000` joins
> `EP-6000` — see finding #12); re-run 2026-07-19 (`FEAT-11000`'s Included Requirements grows by
> two, `FR-11210`/`FR-11410` — see finding #13, no structural catalog change).** Owned by
> `05-feature-decomposition`. Reviews
> [FP-02](02-epic-catalog.md)–[FP-04](04-feature-dependency-graph.md) for oversized/undersized
> Features, duplicates, missing Features, mis-assigned requirements, and architectural
> inconsistencies. **Recommend only — this document applies no fixes to the other four
> documents** (the correction to FEAT-5100/Release 1's status, `BL-0036`, was applied directly to
> those two documents by this same pass per the user's explicit instruction, not by this review).

## Requirement-assignment check (every FR/NFR owned by exactly one Feature)

**Bootstrap baseline** (unchanged from the 2026-07-07 tally) against
[RQ-01](../requirements/01-functional-requirements.md)/
[RQ-02](../requirements/02-non-functional-requirements.md)'s 25 `FR-xxxx` + 11 `NFR-xxxx` = 36
requirement IDs:

- FEAT-1000: FR-1100, FR-1110, FR-1120, FR-1130, FR-1140, FR-1150, FR-1160, NFR-2100 (8)
- FEAT-2000: FR-2100, FR-2200, FR-2300, FR-2310, FR-2320 (5)
- FEAT-3000: FR-3100, FR-3200, FR-3210, FR-3300 (4)
- FEAT-4000: FR-4100, FR-4200, NFR-4100 (3)
- FEAT-5000: FR-5100, FR-5200, FR-5210, NFR-5100, NFR-5200 (5)
- FEAT-5100: FR-5220 (1)
- FEAT-6000: FR-6100, FR-6200, FR-6300, NFR-1200 (4)
- FEAT-7000: NFR-1100, NFR-3100, NFR-4000, NFR-6100, NFR-7100, NFR-8100 (6)

**Procgen-world increment delta** (2026-07-09 RQ-01…04 delta) — 11 new `FR-xxxx` + 6 new
`NFR-xxxx` = 17 requirement IDs:

- FEAT-9000: FR-9100, FR-9110, FR-9120, FR-9130, FR-4310, FR-3220, NFR-2200, NFR-4200 (8)
- FEAT-4100: FR-4300, NFR-1300 (2)
- FEAT-1100: FR-1170, FR-1180, FR-1190 (3)
- FEAT-5300: FR-9200, NFR-5300 (2)
- FEAT-6100: NFR-6500, NFR-6510 (2)

**Total: 36 + 17 = 53.** Every requirement ID appears exactly once across all thirteen lists
(checked by direct cross-reference, no ID repeated, no ID from either the bootstrap baseline or
the 2026-07-09 delta omitted). **Clean — no unassigned or double-assigned requirements.**

**`ADR-0012` maze-adjacency delta** (2026-07-11 RQ-01 delta) — 3 new `FR-xxxx` = 3 requirement IDs:

- FEAT-9100: FR-9140, FR-9150 (2)
- FEAT-2100: FR-2330 (1)

**Total: 53 + 3 = 56.** Both new Features' requirements checked against every existing list above
— no overlap, no ID reused. **Clean — no unassigned or double-assigned requirements.** (`CR-05`
is explicitly not in this tally — it is a Candidate, not baselined, per RQ-01/RQ-03's own
disposition; this stage correctly does not force it into a Feature row.)

**Edge-indicator legend screen delta** (2026-07-13 RQ-01 delta) — 2 new `FR-xxxx` = 2 requirement
IDs:

- FEAT-1200: FR-1200, FR-1210 (2)

**Total: 56 + 2 = 58.** Checked against every existing list above — no overlap, no ID reused.
**Clean — no unassigned or double-assigned requirements.**

**Win-condition redesign fold-in** (`BL-0102`, closed by this delta) — `FR-9160`/`FR-9161`
(baselined 2026-07-12 for `ADR-0015`) were never added to this running tally, a bookkeeping gap
noted but not fixed by the prior review pass. Added now:

- FEAT-9000: FR-9160, FR-9161 (2) — supersede FR-9130/FR-3300 in place, already the correct owner

**Total: 58 + 2 = 60.** Checked against every existing list above — no overlap, no ID reused
(both IDs were already unambiguously `FEAT-9000`'s own). `BL-0102` closed.

**Infinite Mode delta** (2026-07-14 RQ-01/RQ-02 delta, `ADS-001`/`ADR-0016`/`ADR-0017`) — 7 new
`FR-xxxx` + 4 new `NFR-xxxx` = 11 new requirement IDs:

- FEAT-10000: FR-10100, FR-10200, FR-10210, FR-10300, FR-10400, FR-10500, FR-10600, NFR-1400,
  NFR-2300, NFR-4300, NFR-5400 (11)

**Total: 60 + 11 = 71.** Checked against every existing list above — no overlap, no ID reused.
**Clean — no unassigned or double-assigned requirements.** (`CR-05` remains outside this tally,
un-baselined per `ADR-0018`'s own routing to a future `04` pass — the same discipline this tally
already applied to `CR-05` before that ADR existed. `CR-07` is no longer a Candidate — already
counted above as `FR-10600`.)

**Procedural Music Generation delta** (2026-07-16 RQ-01/RQ-02 delta, `ADR-0019`/`BL-0127`) — 2 new
`FR-xxxx` + 1 new `NFR-xxxx` = 3 new requirement IDs:

- FEAT-7100: FR-7100, FR-7110, NFR-4400 (3)

**Total: 71 + 3 = 74.** Checked against every existing list above — no overlap, no ID reused.
**Clean — no unassigned or double-assigned requirements.** This is this project's first use of
the `FR-7xxx` audio range — confirmed unused before this delta both here and independently by
`03-requirements-review.md` finding #22.

**Infinite Mode combat sub-mode delta** (2026-07-17 RQ-01/RQ-02 delta, `ADS-002`/`MSTR-001`
C11/`BL-0133`) — 6 new `FR-xxxx` + 2 new `NFR-xxxx` = 8 new requirement IDs:

- FEAT-11000: FR-11100, FR-11200, FR-11300, FR-11400, FR-11500, FR-11600, NFR-1500, NFR-4500 (8)

**Total: 74 + 8 = 82.** Checked against every existing list above — no overlap, no ID reused.
**Clean — no unassigned or double-assigned requirements.** This is this project's first use of
the `FR-11xxx` range, confirmed unused before this delta both here and independently by
`03-requirements-review.md` finding #23.

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Missing requirement (surfaced here, not fixed here) | (no FR exists) — GDS-08 §2, ADR-0005, ADR-0007, `test_rom.py` T6 | **No numbered functional requirement covers player/collectible sprite (OAM) rendering as an observable behavior**, even though it is shipped, architecturally documented (8×16 OBJ pairs, shadow-OAM DMA), and exercised by `test_rom.py`'s T6 suite. Unchanged since the 2026-07-07 review — still open. | Low–Medium (informational; the behavior is shipped and working, only its formal requirement is missing) | Still routed to `04-requirements-engineering` (`BL-0020`, `SCHEDULED`) for a future delta. Not blocking any current Feature. |
| 2 | Architectural straddle (reviewed and accepted, not a defect) | FEAT-2000 | FEAT-2000 touches both `asm_game.py` and `tilemaps.py` (arrow-tile rendering, FR-2320). | Informational | No action — unchanged from the 2026-07-07 review; confirmed correct on re-review. |
| 3 | **Resolved since the last review** | FEAT-5100 | FEAT-5100's two prior Open Questions (SRAM byte layout; save-compatibility default) are both answered — `FS-101` resolved them, `IP-1010` implemented them, `VR-1010` independently confirmed both (`T11.d`'s synthetic pre-upgrade fixture proves the save-compatibility answer specifically). | — (closed) | No further action. This finding is retained here, marked resolved, rather than deleted — the Feature Catalog's own Open Questions field for FEAT-5100 was updated to "None remaining" in the same pass that corrected `BL-0036`. |
| 4 | **Resolved since the last review** | FEAT-5100 vs. FEAT-7000's `NFR-7100` remediation | Both scheduling options this finding named are now moot — both work items completed the same day (2026-07-07): `IP-1010` (FEAT-5100) and `IP-9010` (`NFR-7100` remediation) both shipped and were independently verified. | — (closed) | No further action. |
| 5 | Stale Risk field — **RESOLVED 2026-07-10** | FEAT-6000, FEAT-7000 (Feature Catalog entries) | **Both Features' own Risk fields in [FP-03](03-feature-catalog.md) still described non-compliances as current** — FEAT-6000's Risk said `NFR-1200` is "confirmed not met"; FEAT-7000's said `NFR-7100` is "confirmed not met at Critical severity." Both are now Met, VERIFIED 2026-07-07 (`IP-9020`/`VR-9020`, `IP-9010`/`VR-9010`) and reconfirmed by `10-integration-review` (2026-07-10). **Resolved:** both Risk fields corrected to Low, citing the VERIFIED status; FEAT-7000's Open Questions field also corrected (its former sequencing question is moot — both items it named landed the same day). | Low (cosmetic at filing) → resolved | No further action — `BL-0037` closed. |
| 6 | Oversized-Feature judgment call (reviewed and accepted, not a defect) | FEAT-9000 | FEAT-9000 (8 requirements: FR-9100/9110/9120/9130/4310/3220, NFR-2200/4200) is the largest Feature in the catalog, tied with FEAT-1000. It deliberately merges two threads — the generation algorithm itself and the item-agnostic collection generalization — because `FR-9130` ("one KeyItem per region") and `FR-3220` ("item-agnostic collection") name each other as dependencies at the requirement level (see [FP-04](04-feature-dependency-graph.md)'s circular-dependency check). Splitting them into two Features would either force an artificial FEAT-level cycle or an arbitrary one-directional cut through a genuinely mutual coupling. | Informational | No action — reviewed and confirmed the right call: cohesion (avoiding a cycle) was correctly prioritized over uniform Feature size. If `06-feature-specification` finds the two threads separable once implementation detail is known, splitting at that stage remains available; not pre-judged here. |
| 7 | Missing dependency artifact — **RESOLVED 2026-07-11** | FEAT-2100, GDS-08 | **`FEAT-2100` (maze-aware transition-edge signaling) cannot be fully specified past its logic half** — its own blocked-edge indicator's tile art/palette assignment has no `GDS-08` (presentation architecture) delta authored yet, and this stage correctly does not originate one (out of `05-feature-decomposition`'s own scope, per its SHALL-NOT-redesign-architecture rule — the same rule `04-requirements-engineering` invoked for `CR-05`/`BL-0066` one stage upstream). `FEAT-2100`'s own catalog entry already names this as an Open Question, not silently assumed resolved. **Resolved:** `GDS-08` §10 landed 2026-07-11 (`BL-0068`), `FEAT-2100`'s rendering half fully specified and its content half shipped/`VERIFIED` (`IP-1081`); only the render branch (`IP-1082`) remains unimplemented, a `07`/`08` question, not a `05`-stage gap anymore. | Low-Medium (a real, named blocker on full specification — not a defect in what's cataloged, since the logic half is fully specifiable independent of the art question) | Routed to `03-architecture-design-synthesis` for a `GDS-08` delta (blocked-edge indicator tile art). `06-feature-specification` can still specify `FEAT-2100`'s logic half (the grid-arithmetic re-derivation `FR-2330` describes) independently, per that Feature's own Suggested Verification Strategy, without waiting on the art decision — not a hard block on all downstream work, only on the rendering half's full spec. |
| 8 | 05-delta review (`FEAT-1200` added) | FEAT-1200, FEAT-1000, FEAT-1100, FEAT-2100 | Reviewed the new Feature against the catalog's own consistency rules. **Cohesion/coupling:** `FEAT-1200` cleanly separates from `FEAT-1000` (extends its state set, doesn't modify its existing states' behavior) and from `FEAT-2100` (displays its tiles, doesn't redefine their meaning or render-time classification) — no straddle, no artificial split needed. **Dependency correctness:** cross-checked against [FP-04](04-feature-dependency-graph.md) — `FEAT-1200`'s three dependencies (`FEAT-1000`, `FEAT-1100`, `FEAT-2100`) are correctly a *content* dependency on `FEAT-2100` (its already-shipped tiles), not a *build-order* dependency on `FEAT-2100`'s own still-in-flight render branch — confirmed by direct re-read of `IP-1081`'s `VERIFIED` status (tiles shipped) versus `IP-1082`'s `COMPLETE`-pending-verification status (render branch, unrelated to what `FEAT-1200` needs). **Requirement assignment:** `FR-1200`/`FR-1210` assigned to `FEAT-1200` only, confirmed not double-assigned anywhere else in the catalog. **Bucket placement:** joins Release 2 as a second, independent addendum (this stage's own established "no Release 3" convention, per the `ADR-0012` addendum's own precedent) — reviewed and confirmed not a forced fit, since `FEAT-1200` genuinely has no dependency on the `ADR-0012` remediation thread it shares a bucket with. | — (clean check, no new defect; one new Feature added, correctly scoped and placed) | None — this finding records that the delta was reviewed and found internally consistent, per this stage's own Step-5 discipline (a zero-finding pass is a signal to re-check, not proof of quality — this re-check found the addition clean). |
| 9 | 05-delta review (`FEAT-10000`/`EP-6000` added; `BL-0102` tally gap closed) | FEAT-10000, EP-6000, EP-5000, FEAT-9000, FEAT-1100, FEAT-3000, FEAT-5000 | Reviewed the new Feature/Epic against the catalog's own consistency rules. **Epic-boundary judgment call, reviewed and accepted:** `FEAT-10000` was kept in a new `EP-6000` rather than folded into `EP-5000` (the existing world-generation Epic) — confirmed the right call, not a forced split: `ADR-0016` point 7 explicitly frames Infinite Mode as "a second, independent generation architecture," unlike `FEAT-9100`'s 2026-07-11 addition to `EP-5000`, which directly extended `FEAT-9000`'s own generation routine. Splitting on "does this extend an existing routine or start a new one" is a real, defensible line, not an arbitrary one. **Dependency correctness:** cross-checked against [FP-04](04-feature-dependency-graph.md) — `FEAT-10000`'s five dependencies (`FEAT-1000`, `FEAT-1100`, `FEAT-3000`, `FEAT-5000`, `FEAT-9000`) are all already shipped/`VERIFIED`; the `FEAT-9000` dependency confirmed as code-reuse only (`gw_prng_step`), not a build-order dependency on anything `FEAT-9000`-specific — matches `FEAT-10000`'s own catalog entry text exactly, not merely asserted. **Unsplit-Feature judgment call, reviewed and accepted:** `FEAT-10000` bundles mode entry, generation, treasure placement, win condition, save/load, and session shape into one Feature (11 requirements, the largest in the catalog, surpassing `FEAT-9000`'s own 8) — mirrors finding #6's own precedent (`FEAT-9000` itself started unsplit) rather than forcing a premature split before implementation reveals a real seam; explicitly not pre-judged, per `FEAT-10000`'s own Scope field. **Requirement assignment:** all 11 new IDs assigned to `FEAT-10000` only, confirmed not double-assigned. **Bucket placement:** `Future`, not a numbered Release — confirmed correct: `FEAT-10000` has zero graph-blocking dependencies (unlike a genuine technical blocker), so its Future placement is a release-commitment choice, not a technical one, and is stated as such rather than conflated. **`BL-0102`'s tally gap also closed in this same pass** (a natural fold-in, not a separate delta) — `FR-9160`/`FR-9161` added to the running tally, `FEAT-9000`'s own 8-requirement count in finding #6 above is now stale by 2 (10, not 8) as a direct consequence; noted here rather than silently left inconsistent. | — (clean check, no new defect; one new Feature/Epic added, correctly scoped and placed; one pre-existing bookkeeping gap closed) | None — this finding records that the delta was reviewed and found internally consistent, per this stage's own Step-5 discipline. |
| 10 | Missing dependency edge — **RESOLVED same-day (2026-07-14)** | FEAT-10000, FEAT-4100 | **`FEAT-10000`'s own Dependencies field omitted `FEAT-4100`** — rendering a materialized Infinite Mode region requires `FEAT-4100`'s existing biome-family screen-composition dispatch (the same dispatch the finite mode's `REGION_GRAPH`-sourced biome-id already selects through, per `FS-103`), but finding #9's own review (above) missed it too, cross-checking only the five dependencies the catalog entry stated rather than independently re-deriving the full set from `FEAT-10000`'s own Description. Correctly caught downstream instead, by `06-feature-specification`'s own `FS-110` Open Question 1 (filed `BL-0111`) — this stage's SHALL-NOT-modify-the-catalog-entry rule meant `06` could only flag it, not fix it, so the correction rode a dedicated same-day `05-feature-decomposition` re-touch rather than sitting unresolved. **Resolved:** `FEAT-10000`'s Dependencies field, `FEAT-4100`'s Dependent Features field, and the corresponding [FP-04](04-feature-dependency-graph.md) edge/summary-row/critical-path note all updated in the same pass. Re-verified: `FEAT-4100` is already shipped/`VERIFIED`, so this is a documentation correction only — no build-order risk, no requirement-tally change (both Features' Included Requirements are unchanged). | Low-Medium (a real, correctly-surfaced gap — not a defect in what was implemented, since nothing depending on this edge has shipped yet) | No further action — `BL-0111` closed. Worth noting for future dependency reviews: cross-check a new Feature's Dependencies field against its own Description/Purpose text, not only against the requirements it lists, since a code-reuse or rendering-path dependency can be real without appearing in the Included Requirements list. |
| 11 | 05-delta review (`FEAT-7100`/`EP-7000` added) | FEAT-7100, EP-7000, FEAT-9000, FEAT-10000, FEAT-1000, FEAT-4100 | Reviewed the new Feature/Epic against the catalog's own consistency rules. **Epic-boundary judgment call, reviewed and accepted:** `FEAT-7100` was placed in a new `EP-7000` rather than folded into any existing Epic — confirmed the right call: `EP-2000` (World Content & Presentation) was the closest candidate by surface analogy (both are "presentation"), but its own Features (`FEAT-4000`/`FEAT-6000`) are visual, module-adjacent to `tilemaps.py`/`tiles.py`, while `FEAT-7100` is audio, module-adjacent to `music.py` — no real cohesion gain from forcing the merge, and `EP-2000`'s own Purpose text doesn't mention audio at all. **Dependency correctness:** cross-checked against [FP-04](04-feature-dependency-graph.md) — `FEAT-7100`'s three dependencies (`FEAT-9000`, `FEAT-10000`, `FEAT-1000`) are correctly named: `FEAT-9000` and `FEAT-10000` are genuine build-order dependencies (both supply the biome-family identity `FEAT-7100`'s own playback selection reads), unlike `FEAT-10000`'s own earlier code-reuse-only relationship to `FEAT-9000` — confirmed this is a materially different dependency *kind*, not miscategorized. **Requirement assignment:** `FR-7100`/`FR-7110`/`NFR-4400` assigned to `FEAT-7100` only, confirmed not double-assigned anywhere else in the catalog (this project's first use of the `FR-7xxx` range, independently confirmed by `03-requirements-review.md` finding #22). **Bucket placement:** `Future`, not a numbered Release — confirmed correct per the same reasoning `FEAT-10000` established: zero graph-blocking dependencies on the build-time half, but no release commitment made. **Real cross-arc sequencing risk surfaced, not smoothed over:** unlike every prior new-Feature delta in this catalog, `FEAT-7100`'s own full verification (all nine biome-family identities) depends on *two separate, both-still-open* upstream threads — `FR-4320`'s four implementation packages (gated on G3, `BL-0128`) and `FEAT-10000`'s own release scheduling (currently `Future`, no commitment) — named explicitly in [FP-04](04-feature-dependency-graph.md)'s critical-path and parallel-opportunities sections rather than left implicit. | — (clean check, no new defect; one new Feature/Epic added, correctly scoped and placed; one genuine cross-arc sequencing dependency correctly surfaced rather than hidden) | None — this finding records that the delta was reviewed and found internally consistent, per this stage's own Step-5 discipline. `06-feature-specification` is the natural next step; its own spec pass should state the two-source sequencing dependency in `FS-xxx`'s own Open Questions rather than silently assume `FR-4320`/`FEAT-10000` will both be ready by the time this Feature is implemented. |
| 12 | 05-delta review (`FEAT-11000` added, joins `EP-6000`) | FEAT-11000, EP-6000, FEAT-10000, FEAT-3000, FEAT-6000 | Reviewed the new Feature against the catalog's own consistency rules. **Epic-boundary judgment call, reviewed and accepted:** `FEAT-11000` joins the existing `EP-6000` rather than opening a new Epic (unlike `FEAT-7100`'s own `EP-7000` precedent) — confirmed the right call: `FEAT-11000` is strictly a gated sub-mode *of* Infinite Mode (`COMBAT_MODE` valid only alongside `GAME_MODE=1`), not an independent capability with no existing pattern to extend, the same "does this extend an existing thing or start something new" line finding #9 already drew for `FEAT-10000`/`EP-5000`, applied in the opposite direction here. **Dependency correctness:** cross-checked against [FP-04](04-feature-dependency-graph.md) — `FEAT-11000`'s three dependencies (`FEAT-10000`, `FEAT-3000`, `FEAT-6000`) are all already shipped/`VERIFIED`; `FEAT-6000` is a genuinely new direct edge `FEAT-10000` itself never needed (the health HUD's own heart-tile reuse), correctly named rather than folded silently into the `FEAT-10000` edge. **Unsplit-Feature judgment call, reviewed and accepted:** `FEAT-11000` bundles gating, mob materialization/defeat, weapon fire/hit resolution, player health/setback, the healing economy, and save persistence into one Feature (8 requirements) — mirrors finding #9's own precedent (`FEAT-10000` itself started unsplit at 11 requirements) rather than forcing a premature split before implementation reveals a real seam. **Requirement assignment:** all 8 new IDs (`FR-11100`–`FR-11600`, `NFR-1500`, `NFR-4500`) assigned to `FEAT-11000` only, confirmed not double-assigned anywhere else in the catalog (this project's first use of the `FR-11xxx` range, independently confirmed by `03-requirements-review.md` finding #23). **Bucket placement:** `Future`, not a numbered Release — confirmed correct per the same reasoning `FEAT-10000`/`FEAT-7100` established: zero graph-blocking dependencies, but no release commitment made, and the pipeline journal (run #228) recorded a deliberate checkpoint here given the scope of the eventual production code. | — (clean check, no new defect; one new Feature added, correctly scoped and placed) | None — this finding records that the delta was reviewed and found internally consistent, per this stage's own Step-5 discipline. `06-feature-specification` is the natural next step for `FEAT-11000` once the user confirms continuing into the combat increment (per the pipeline journal's own checkpoint note). |
| 13 | 05-delta review (`FEAT-11000`'s Included Requirements grows by two — `FR-11210`/`FR-11410`) | FEAT-11000, FR-11210, FR-11410, EP-6000, BL-0156, BL-0158 | Reviewed the incremental catalog update against the catalog's own consistency rules, per the "maintain incrementally" discipline (not a full regeneration). **No new Feature/Epic opened, confirmed correct:** both new leaves are user-filed extensions of behavior `FEAT-11000` already owns (mob presence/movement, player-health/setback) with no new module boundary or dependency introduced — `FR-11210` depends only on `FR-11200` (already `FEAT-11000`'s own), `FR-11410` only on `FR-11400` (likewise) — so folding both into the existing Feature, per this document's own Step-1 cohesion rule, is the correct call, not a shortcut around opening a new `FEAT-xxxx`. **Requirement assignment:** `FR-11210`/`FR-11410` confirmed assigned to `FEAT-11000` only, not double-assigned anywhere else in the catalog — cross-checked against `03-requirements-review.md` finding #24, which independently confirmed both IDs were previously unused. **Dependency/Epic/release-bucket structure unchanged, confirmed rather than assumed:** neither leaf introduces a dependency `FEAT-11000` doesn't already carry, so `EP-6000` membership, the three existing Dependencies (`FEAT-10000`/`FEAT-3000`/`FEAT-6000`), and the `Future` release bucket all remain correct without edits to FP-01/FP-02/FP-04 — verified by direct re-read of all three, not assumed unaffected. **Sizing check:** `FEAT-11000` grows from 8 to 10 Included Requirements, still well within the range `FEAT-10000` (11) already established as an acceptable unsplit size at this stage — not yet an oversized-Feature concern. | — (clean check, no new defect; two requirement IDs added to an existing Feature's own Included Requirements list, correctly scoped, no structural change elsewhere in the catalog) | None — this finding records that the incremental delta was reviewed and found internally consistent. `06-feature-specification` still owns `FEAT-11000` as a whole (unchanged next step) — when it next touches `FS-112`, it should fold `FR-11210`/`FR-11410` into that spec's own field set rather than treat them as a separate document, per this Feature's own single-`FS-xxx` framing. |
| 14 | 05-delta review (`FEAT-11000`'s Included Requirements grows by two more — `FR-11310`/`FR-11510`) | FEAT-11000, FR-11310, FR-11510, EP-6000, BL-0147, BL-0155, BL-0157 | Reviewed the incremental catalog update against the catalog's own consistency rules, per the "maintain incrementally" discipline — the same pattern finding #13 already established, applied to a second, later delta. **No new Feature/Epic opened, confirmed correct:** both new leaves extend behavior `FEAT-11000` already owns (weapon fire, the treasure economy) with no new module boundary or dependency introduced — `FR-11310` depends only on `FR-11300` (already `FEAT-11000`'s own) plus `ADR-0021` (a design decision, not a new Feature dependency); `FR-11510` depends only on `FR-11300`/`FR-10300`/`FR-10400`/`FR-11500`/`FR-11600`, all already `FEAT-11000`'s or `FEAT-10000`'s own — so folding both into the existing Feature is the correct call. **Requirement assignment:** `FR-11310`/`FR-11510` confirmed assigned to `FEAT-11000` only, not double-assigned anywhere else in the catalog — cross-checked against `03-requirements-review.md` finding #25, which independently confirmed both IDs were previously unused. **Dependency/Epic/release-bucket structure unchanged, confirmed rather than assumed:** neither leaf introduces a dependency `FEAT-11000` doesn't already carry (`FR-11510`'s own currency-sharing with `FR-11500` is an *intra*-Feature relationship, not a new external edge), so `EP-6000` membership, the three existing Dependencies (`FEAT-10000`/`FEAT-3000`/`FEAT-6000`), and the `Future` release bucket all remain correct without edits to FP-01/FP-02/FP-04 — verified by direct re-read of all three. **Sizing check:** `FEAT-11000` grows from 10 to 12 Included Requirements, now the largest Feature in the catalog (surpassing `FEAT-10000`'s own 11) — named explicitly rather than left unremarked, though still not treated as an automatic split trigger: `FEAT-11000`'s own Scope field already states a split awaits a real implementation-revealed seam, and nothing about these two leaves (both extending already-included capabilities, not introducing a new one) changes that judgment. | — (clean check, no new defect; two requirement IDs added to an existing Feature's own Included Requirements list, correctly scoped, no structural change elsewhere in the catalog; sizing milestone noted, not treated as a split trigger without cause) | None — this finding records that the incremental delta was reviewed and found internally consistent. `06-feature-specification` still owns `FEAT-11000` as a whole (unchanged next step) — when it next touches `FS-112`, it should fold `FR-11310`/`FR-11510` into that spec's own field set, mirroring `FR-11210`/`FR-11410`'s own precedent. |


## Oversized / undersized Feature check

**Bootstrap baseline:** unchanged — no Feature approaches a size where splitting or merging would
improve cohesion. **Procgen-world delta:** FEAT-9000 (8 requirements) is addressed by finding #6
above (reviewed and accepted). The other four new Features (FEAT-4100: 2, FEAT-1100: 3,
FEAT-5300: 2, FEAT-6100: 2) are all appropriately small, single-capability Features, consistent
with FEAT-5100's own precedent (1 requirement) for a new, narrowly-scoped addition.
**`ADR-0012` delta (2026-07-11):** FEAT-9100 (2 requirements) and FEAT-2100 (1 requirement) are
both appropriately small — FEAT-9100's 2-requirement size mirrors FEAT-4100/FEAT-5300/FEAT-6100's
own established precedent for a focused, single-capability extension; FEAT-2100's 1-requirement
size mirrors FEAT-5100's own precedent exactly. **Procedural Music Generation delta (2026-07-16):**
FEAT-7100 (3 requirements) is appropriately small, mirroring FEAT-9100's own 2-3-requirement,
single-capability-extension precedent. **Infinite Mode combat sub-mode delta (2026-07-17):**
FEAT-11000 (8 requirements) is addressed by finding #12 above (reviewed and accepted, mirroring
FEAT-10000's own unsplit-at-11 precedent) — not oversized enough to force a split before
implementation reveals a real seam.

## Duplicate Feature check

None found, including after this delta. Each of the five new Features' Purpose is distinct from
every other Feature (new and bootstrap); no overlap in player-visible or system-level capability.
**`ADR-0012` delta:** FEAT-9100/FEAT-2100 checked against all fifteen other Features — neither
overlaps `FEAT-9000` (generation vs. adjacency-shaping) nor `FEAT-2000` (base traversal/signaling
vs. maze-aware signaling extension); both are genuinely new capability, not restatements.
**Procedural Music Generation delta:** FEAT-7100 checked against all seventeen other Features —
no overlap; it is the only Feature in the catalog whose Purpose concerns audio at all.
**Infinite Mode combat sub-mode delta:** FEAT-11000 checked against all eighteen other Features —
no overlap; it is the only Feature in the catalog whose Purpose concerns combat/damage/health at
all, and its own Scope field explicitly excludes `FEAT-10000`'s base capability rather than
restating it.

## Architectural consistency check

Every Feature's Affected Modules list — including the five new Features' — is consistent with
[GDS-03](../architecture/03-architecture.md)'s module decomposition and
[GDS-09](../architecture/09-interface-specification.md)'s interface contracts, including that
delta's new `worldgen.py` module contract (FEAT-9000) and the generalization of
`ALL_SCREENS`/per-zone screen functions to per-biome-family functions (FEAT-4100). No Feature
implies a module boundary violation. **`ADR-0012` delta:** FEAT-9100's Affected Modules
(`worldgen.py`, `asm_game.py`) match `ADR-0012` point 1 exactly (a second pass within the same two
modules `FEAT-9000` already touches, not a new module); FEAT-2100's (`asm_game.py`, `tiles.py`/
`tilemaps.py`) match `FEAT-2000`'s own precedent for the identical straddle (finding #2 above) —
consistent, not a new pattern. **Procedural Music Generation delta:** FEAT-7100's Affected Modules
(`music.py`, `build_rom.py`, prospective `asm_game.py`) match `ADR-0019`'s own explicit decision
exactly — no new sibling module (the `worldgen.py` pattern this ADR deliberately did not copy),
generation logic living inside the existing `music.py` module per GDS-03's one-job-per-file rule.
**Infinite Mode combat sub-mode delta:** FEAT-11000's Affected Modules (`asm_game.py` only) match
`ADS-002`'s own System Architecture section exactly — no new sibling module, new mob/projectile/
health routines living inside the existing module per GDS-03's one-job-per-file rule, the same
pattern `ADR-0019` established for `FEAT-7100`.

## Circular dependency check

Re-confirmed clean per [FP-04](04-feature-dependency-graph.md)'s own check, including the five
new Features — no cycle exists. **`ADR-0012` delta:** re-confirmed clean again with
`FEAT-9100`/`FEAT-2100` added — both sit at the end of existing chains (`FEAT-9000` → `FEAT-9100`
→ `FEAT-2100`, with `FEAT-2100` also depending on the already-terminal `FEAT-2000`), introducing
no new back-edge. The one near-miss at the requirement level (`FR-9130`/`FR-3220`,
finding #6 above) was resolved by Feature-level grouping, not left as an unresolved graph cycle.
**Infinite Mode delta:** re-confirmed clean with `FEAT-10000` added — all five of its own edges
point *into* it from already-terminal-or-mid-chain Features (`FEAT-1000`, `FEAT-1100`, `FEAT-3000`,
`FEAT-5000`, `FEAT-9000`), and `FEAT-10000` itself has zero dependents, so it can only ever be a
sink, never introduce a cycle by construction. **`BL-0111` correction (same day):** re-confirmed
clean with the added `FEAT-4100 → FEAT-10000` edge — `FEAT-4100` is itself a sink with only one
prior dependent (`FEAT-6100`, also a sink), so the new edge extends an existing terminal branch
into `FEAT-10000` (already confirmed a sink above) without creating any new path back toward the
graph's root; still a strict DAG. **Procedural Music Generation delta:** re-confirmed clean with
`FEAT-7100` added — all three of its own edges (`FEAT-1000`, `FEAT-9000`, `FEAT-10000`) point
*into* it, and `FEAT-7100` itself has zero dependents, so it can only ever be a sink, never
introduce a cycle by construction. **Infinite Mode combat sub-mode delta:** re-confirmed clean
with `FEAT-11000` added — all three of its own edges (`FEAT-10000`, `FEAT-3000`, `FEAT-6000`)
point *into* it, and `FEAT-11000` itself has zero dependents, so it can only ever be a sink,
never introduce a cycle by construction. `FEAT-10000` gains a second dependent (`FEAT-11000`,
alongside `FEAT-7100`) but both its outgoing edges still point strictly forward to sink Features,
so the graph remains a strict DAG.

## Summary

The Feature Catalog remains complete and internally consistent after this delta: all 53
requirement IDs (36 bootstrap + 17 new) are owned exactly once, no Feature is mis-sized or
duplicated (FEAT-9000's size is a reviewed, accepted cohesion trade-off, not a defect), and no
circular dependency exists at the Feature level. **Two findings closed since the last review**
(FEAT-5100's Open Questions and the FEAT-5100/FEAT-7000 sequencing choice — both resolved by
2026-07-07's implementation work). **One new Low finding** (#5: FEAT-6000/FEAT-7000's own Risk
fields are stale, cosmetic only) is routed to a future light `05-feature-decomposition` touch.
**One prior finding remains open** (#1, the missing sprite-rendering FR, `BL-0020`). No finding
in this review requires revising FP-01–FP-04 before advancing to `06-feature-specification`.

**2026-07-11 `ADR-0012` delta review:** the Feature Catalog remains complete and internally
consistent after adding `FEAT-9100`/`FEAT-2100` — all 56 requirement IDs (53 prior + 3 new) are
owned exactly once, neither new Feature is mis-sized or duplicated, and no circular dependency
exists. **One new Low-Medium finding** (#7: `FEAT-2100`'s tile art needs a `GDS-08` delta not yet
authored) is a real, correctly-surfaced blocker on that Feature's *rendering* half only — its
logic half and `FEAT-9100` entirely are unblocked. `CR-05`/`BL-0066` correctly received no Feature
row (no baselined FR exists for it yet) — this stage did not invent one to fill the gap. No
finding in this delta requires revising FP-01–FP-04 before advancing to `06-feature-specification`
on `FEAT-9100`/`FEAT-2100`'s unblocked portions.

**2026-07-14 Infinite Mode delta review:** see finding #9 — the Feature Catalog remains complete
and internally consistent after adding `FEAT-10000`/`EP-6000` — all 71 requirement IDs (60 prior,
including the `BL-0102` tally fold-in this same pass closed, + 11 new) are owned exactly once, the
new Feature is not mis-sized in a way that requires splitting (11 requirements, reviewed and
accepted per finding #9, mirroring `FEAT-9000`'s own precedent), and no circular dependency
exists. **No new Critical/High/Medium finding** — the Epic-boundary and unsplit-Feature choices
were both judgment calls, reviewed and accepted, not defects. `CR-05`/`BL-0066` again correctly
received no Feature row (still un-baselined, per `ADR-0018`'s own routing to a future `04` pass) —
this stage continues not inventing one to fill that gap. No finding in this delta requires
revising FP-01–FP-04 before advancing to `06-feature-specification` on `FEAT-10000`.

**2026-07-16 Procedural Music Generation delta review:** see finding #11 — the Feature Catalog
remains complete and internally consistent after adding `FEAT-7100`/`EP-7000` — all 74 requirement
IDs (71 prior + 3 new) are owned exactly once, the new Feature is appropriately sized (3
requirements), and no circular dependency exists. **No new Critical/High/Medium finding** — the
Epic-boundary choice was a judgment call, reviewed and accepted, not a defect. **One genuine
cross-arc sequencing dependency correctly surfaced, not a defect but worth carrying forward:**
`FEAT-7100`'s own full verification depends on both `FR-4320`'s implementation packages (gated on
G3) and `FEAT-10000`'s own release scheduling (currently `Future`) — named explicitly in
[FP-04](04-feature-dependency-graph.md) rather than left implicit. No finding in this delta
requires revising FP-01–FP-04 before advancing to `06-feature-specification` on `FEAT-7100`.

**2026-07-17 Infinite Mode combat sub-mode delta review:** see finding #12 — the Feature Catalog
remains complete and internally consistent after adding `FEAT-11000` (joining `EP-6000`) — all 82
requirement IDs (74 prior + 8 new) are owned exactly once, the new Feature is appropriately sized
(8 requirements, reviewed and accepted per finding #12, mirroring `FEAT-10000`'s own 11-requirement
unsplit precedent), and no circular dependency exists. **No new Critical/High/Medium finding** —
the Epic-boundary choice (joining `EP-6000` rather than opening a new Epic, the opposite call
from `FEAT-7100`'s own precedent) was a judgment call, reviewed and accepted, not a defect.
`FEAT-11000` is immediately specifiable — unlike `FEAT-7100`, none of its three dependencies
carry an open sequencing blocker. No finding in this delta requires revising FP-01–FP-04 before
advancing to `06-feature-specification` on `FEAT-11000` — subject to the pipeline journal's own
recorded checkpoint (run #228): the user has not yet confirmed continuing past this stage into
the combat increment's remaining, substantially larger production-code work.
