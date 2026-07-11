# RQ-03 — Requirements Review

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; delta 2026-07-09 reviewing the
> procgen-world increment's new FR/NFR content — see findings #7–10; delta 2026-07-10 reviewing
> the 04-delta batch — see finding #11; delta 2026-07-11 reviewing the NFR-6500/6510 Met flip —
> see finding #12; delta 2026-07-11 reviewing `ADR-0012`'s maze-adjacency FR/NFR delta — see
> finding #13).** Owned by
> `04-requirements-engineering`. Reviews the final
> [RQ-01](01-functional-requirements.md)/[RQ-02](02-non-functional-requirements.md)
> baseline for duplicates, conflicts, ambiguities, gaps, impossible requirements, architecture
> violations, and missing verification/traceability. **Report only — this document applies no
> fixes**; every finding below routes to an owner as a separate follow-up.

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Ambiguity / unresolved design question — **RESOLVED 2026-07-07** | FR-5210, FR-5220, NFR-5200, BL-0018 | The save/restore requirements were internally consistent but left genuinely open whether the declared save scope was intended. **Resolved by explicit user decision (2026-07-07):** facing direction/animation frame persistence rejected ("not important"); per-zone ScoreItem persistence approved ("should save and persist"), promoted to FR-5220. BL-0018 flipped to `DONE`. | Medium (at filing) → closed | No further action — CR-01 was split and dispositioned in RQ-01's 2026-07-07 changelog; FR-5210 reworded; NFR-5200 updated to the widened field set. Retained here as the historical record that this finding was raised, tracked, and resolved rather than silently dropped. |
| 2 | Missing enforcement / gap | FR-3210, BL-0017, CR-02 | FR-3210 describes carrot-collection behavior *assuming* exactly one Carrot exists per zone, but no requirement in this baseline mandates that invariant be *enforced* — it is an unchecked authoring convention (`ZONE_COLLECTS`). This is a real, if low-severity, gap: a future content package could violate the invariant with nothing in this baseline (or any test) catching it. | Low | CR-02 (Candidate Requirements, RQ-01) correctly declines to baseline this as a numbered NFR today, per BL-0017's own SCHEDULED disposition (a Verification Checklist item on any future `ZONE_COLLECTS`-touching package, not a standalone requirement). No baseline change needed; keep BL-0017 open until such a package exists. |
| 3 | Missing verification (systemic, cross-cutting) — **RESOLVED 2026-07-07** | NFR-7100, and every FR-1xxx/2xxx/3xxx/5xxx/6xxx whose Verification Method names "Test" | NFR-7100 documents (honestly) that `test_rom.py`'s T2–T10 suites test pre-rewrite semantics and cannot currently verify anything (BL-0006, Critical). This means **every FR above whose Verification Method is "Test" is not, in fact, currently verifiable by the existing suite** — the method is correct in principle but unsatisfiable in practice until BL-0006/BL-0008 lands. This is the single largest latent risk in the baseline: a future stage-08/09 run could believe "Test" next to an FR ID means a passing check exists today, when none does. **Resolved:** `IP-9010` rewrote the suite against current semantics (109/109 pass at its own commit, 125/125 today), independently verified `VR-9010` (2026-07-07). `NFR-7100` is `MET`; every "Test"-method FR now has genuine, current coverage. | High (at filing) → resolved | Read every "Verification Method: Test" cell in RQ-01 as *the intended method once BL-0006/BL-0008 is remediated*, not as current coverage. Recommend `07-implementation-planning` treat the `test_rom.py` rewrite as a high-priority package independent of feature work — it blocks honest verification for the entire FR baseline, not just the NFR it's filed against. Owner: `07-implementation-planning`/`08-code-implementation`, per BL-0006/BL-0008. No further action — retained as the historical record this was the baseline's single largest risk and was tracked through to resolution, not silently dropped. |
| 4 | Forward-looking conflict risk (not a current conflict) | NFR-4000, MSTR-001 C7, ADR-0001 | NFR-4000 ("Met," single 32768-byte bank) and vision commitment C7 (Zelda/Pokémon-scale world, anticipating future bank-switching) are not in conflict *today* — NFR-4000 explicitly names its own future-supersession trigger. But nothing in this baseline currently *watches* the 9.6KB headroom as it's consumed; a future content package could push usage close to the ceiling without any requirement flagging that NFR-4000's "Met" status is approaching its limit. | Low | Recommend any future package that materially increases ROM usage include a checklist item confirming remaining headroom against the 32768-byte ceiling, and that this NFR's status be re-affirmed (not silently left "Met") once headroom drops below some threshold (e.g. 2KB) — a concrete number to set is itself future `03-architecture-design-synthesis`/`05-feature-decomposition` work, not decided here. |
| 5 | Weak/derived traceability (self-flagged, reviewed here for discipline) | NFR-2100 | NFR-2100 (deterministic state-machine behavior) has no single direct GDS-06 statement as its source — it is derived from the FR baseline's own testability demands, and RQ-02 already flags this honestly in its own Notes field. | Low | No baseline change needed — the derivation is sound (a non-deterministic state machine would make FR-1xxx's Acceptance Criteria untestable) and the document already discloses it rather than presenting it as a direct citation. Recorded here only to confirm the Review actually checked it, not to raise a new concern. |
| 6 | Missing requirement — **SUPERSEDED 2026-07-09** | Usability category (RQ-02) | No NFR states a player-facing usability standard. **Superseded:** the procgen-world increment's delta populated this category (NFR-6500/6510, C8/C9's aesthetic/biome-transition standards) — the category is no longer empty. | Low (at filing) → superseded | No action — see findings #7–10 below for the review of the content that now fills this category. Retained as the historical record that the category's emptiness was checked and correctly attributed to "nothing to derive yet," not an oversight, at the time it was filed. |
| 7 | Coexisting current/target requirements, same baseline (new pattern, not a defect) | FR-1120/FR-1170, FR-1160/FR-1170, FR-3210/FR-3220 | The procgen-world delta introduces a new pattern this baseline hasn't used before: a **target-state FR co-existing with the current-state FR it will eventually supersede**, distinguished only by prose ("target — not yet implemented" in the Title/Status area) and a cross-reference Note on each side, not a formal lifecycle field. E.g. FR-1120 (auto-load, shipped) and FR-1170 (main menu, target) both describe boot behavior for the *same* game, mutually exclusive once FR-1170 ships. | Low (methodology note, not a current defect — both descriptions are individually accurate for their respective timeframes) | This is a deliberate, working choice (mirrors MSTR-001 v3.0's own C7-before-C8/9/10 forward-commitment pattern and GDS-01's §2a-alongside-§2 delta convention) — not a defect, but **flag for `05-feature-decomposition`**: when FR-1170/1180/1190/3220/4300/4310/9100–9200 are actually scheduled for implementation, the corresponding FR-1120/1160/3210 should be formally superseded (a dated RQ-01 changelog entry per this document's existing precedent, per BL-0018's own worked example), not left silently coexisting once the target ships for real. |
| 8 | Missing verification (expected, not a new instance of finding #3) | Every new FR-1170–9200/NFR-1300–6510 | Every new requirement's Verification Method names Test, but none has any `test_rom.py` coverage — nothing is implemented yet. | Informational (not a defect — explicitly, honestly marked "not yet implemented"/"NOT YET IMPLEMENTED" throughout, the same honesty discipline finding #3 already established for the bootstrap baseline) | No action needed now — this is the expected state for a target-only requirement set, exactly parallel to finding #3's own resolution path (a requirement's Verification Method states the *intended* method, not current coverage). Will convert to real Test coverage as `07`/`08` packages implement each requirement. |
| 9 | Requirement–ADR consistency check (new ADRs) | ADR-0009, ADR-0010, ADR-0011, and every new FR/NFR citing them | Every new FR/NFR's "Related ADRs" field was cross-checked against ADR-0009/0010/0011's actual Decision/Consequences text (e.g. FR-9110's "immutable per save" matches ADR-0010's decision verbatim; FR-4310's "enforced by construction" matches ADR-0009's decision; NFR-4200's headroom figures match GDS-07 delta's §6/§7, which in turn matches R111's analysis). No requirement asserts anything its cited ADR doesn't actually decide. | — (clean check, no finding) | None — recorded to confirm the cross-check was performed, per this document's own established pattern (see finding #5's precedent for "clean check, still recorded"). |
| 10 | Scope-boundary check: D1's non-goal | FR-9100 (Notes), MSTR-001 §4 | Confirmed no FR/NFR in the delta requires a text/dialogue system, consistent with `MSTR-001` D1/§4's explicit non-goal (not ruled out, not required). FR-9100's Notes field states this explicitly rather than leaving it implicit. | — (clean check, no finding) | None — a future request to add dialogue would reverse a recorded non-goal and re-open at `01-vision` (per MSTR-001 §4's own framing), not enter here as a requirements-stage addition. |
| 11 | 04-delta batch review (`BL-0020`/`BL-0022`/`BL-0026`/`BL-0028`) | FR-6400, FR-3200, NFR-6100, NFR-1200, NFR-5200, NFR-7100 | Reviewed all four corrections together: **FR-6400** (new) cites only shipped, already-passing evidence (T6.1–T6.10) — no new behavior, no new test, clean. **FR-3200**'s corrected postcondition matches `setup_zone_collects`'s actual shipped behavior exactly (direct code re-read during this review); does not contradict `FR-5220`/`IP-1010`, which build persistence *on top of* the respawn behavior rather than assuming it away. **NFR-6100/NFR-1200/NFR-7100/NFR-5200**'s corrected Test cells/status lines all cite real, existing Verification Reports (`VR-9010`/`VR-9020`/`VR-1010`) — no forward reference invented. **Finding #7's own pattern** (target FRs coexisting with current ones) is now further along than when filed: `05-feature-decomposition`/`06-feature-specification`/`07-implementation-planning` have all since run for the procgen-world increment's five target Features — the RTM's Feature Spec/Implementation Package columns for FR-1170–9200/NFR-1300–6510 were filled in this same pass (citing `FS-102`…`FS-106`/`IP-1020`/`IP-1030`/`IP-1031`/`IP-1040`/`IP-1050`) to keep the matrix current, per finding #7's own recommendation that this coexistence be tracked deliberately, not left to drift. | — (clean check, no new defect; four corrections applied, all confirmed accurate) | None — this finding records that the batch was reviewed together and found internally consistent, per this stage's own Step-3 discipline (review, don't silently trust the edits made in Steps 1–2 of the same pass). |
| 12 | 04-delta review (`BL-0045`) | NFR-6500, NFR-6510 | Reviewed the Met-status flip against its source: `content-review-IP-1031.md` genuinely exercises both NFRs' own Acceptance Criteria (NFR-6500: craft/clean-screen checklist against `IP-1031`'s 5 rendered screens; NFR-6510: palette-stepping judgment against the 4 grammar-legal pairs a real generated world exposed) — not a status flip made without evidence. NFR-6510's Low/informational note (Stone↔Brick pairing) is carried into the requirement's own Status field verbatim rather than smoothed over, consistent with this NFR's "Should" priority (a note, not a failure). Cross-checked against finding #7/#8's own pattern: this is the first of the procgen-world delta's target NFRs to reach real, evidenced Test/Inspection coverage — the remaining NFR-1300/2200/4200/5300 and FR-1170–9200 are implemented/verified (per `IP-1020`/`1030`/`1040`/`1050`/`1031`) but their own RQ-02/RQ-01 status lines were already updated in earlier passes (run #55–58's `07`/`09` touches), not newly discovered stale here. | — (clean check, no new defect) | None — recorded to confirm this delta's evidence was checked against the actual review document, not merely trusted from its own summary. |
| 13 | Architecture conflict, correctly not resolved unilaterally | FR-9140, FR-9150, FR-2330, CR-05, ADR-0012, BL-0065, BL-0066 | Reviewed `ADR-0012`'s maze-adjacency FR/NFR delta as a set. **FR-9140/FR-9150/FR-2330** are internally consistent with `ADR-0012` and with each other (cross-checked: FR-9140's Postconditions cite FR-9120/FR-4310 correctly as unaffected; FR-9150's mechanism matches ADR-0012 point 4 verbatim; FR-2330's 3-state signal matches ADR-0012 point 2's "both cases are `0xFF` at the data level" fact exactly, correctly deriving that the render-time distinction needs independent grid arithmetic, not a new `REGION_GRAPH` field). **One genuine architecture conflict found, correctly routed rather than patched:** `BL-0066` (biome-blob clustering)'s own first-suggested approach — seeding blob centers from the maze's dead-ends — requires maze-generation to run *before* biome assignment, directly contradicting `ADR-0012` point 1's fixed pass order (biome first, maze second, independent). This is not a wording ambiguity fixable by rephrasing an FR; it is a real conflict between what `BL-0066` asks for and what `ADR-0012` already decided. **Correctly handled per this skill's own SHALL-NOT-redesign-architecture rule:** no FR was written that silently picks a compatible variant on the user's behalf; the conflict was written up as **CR-05** (Candidate Requirements, RQ-01) and left un-baselined, with both real options named (revisit `ADR-0012`'s ordering, or use the compatible flood-fill alternative instead) for `03-architecture-design-synthesis`/the user to decide. **`BL-0065`'s UI-exposure sub-question** (should the braid-fraction value become a new SEED/SCALE ENTRY field) was similarly not decided unilaterally — `FR-9150` baselines only the mechanism-plus-fixed-default half, deliberately not gating on the UI question, and this Review flags the sub-question as needing user input before any `06-feature-specification`/`07-implementation-planning` work on a UI change specifically (not before `FR-9140`/`FR-9150`'s own core implementation, which the fixed default already unblocks). | Medium (a real architecture conflict, correctly caught rather than silently resolved — not a defect in the baseline itself) | `CR-05` stays un-baselined until `03-architecture-design-synthesis` (or the user directly) picks between "revisit `ADR-0012`'s pass ordering" and "use flood-fill instead of dead-end-seeding." `BL-0065`'s UI-exposure question routes to the user whenever a future stage reaches the SEED/SCALE ENTRY UI specifically — not blocking now. Extends **finding #7's coexistence pattern** a third time: `FR-2320`/`FR-2330` join `FR-1120`/`FR-1170` and `FR-3210`/`FR-3220` as current-vs-target pairs this baseline deliberately carries side by side. |

## Duplicates / contradictions checked and found clean

- FR-1160 (VICTORY state transition) and FR-3300 (the CarrotCount==9 condition that triggers it)
  are complementary, not duplicate — FR-1160 correctly declares a dependency on FR-3300 rather
  than restating its condition.
- No FR/NFR contradicts another FR/NFR or a binding ADR (ADR-0001 through ADR-0008 cross-checked
  against every FR/NFR that names one in its Related ADRs field).
- No requirement crosses into implementation detail (WRAM addresses, opcodes) — GDS-07's
  byte-level facts are cited only where GDS-05/GDS-06 already cited them, never re-derived here.
- **2026-07-09 delta:** ADR-0009 through ADR-0011 cross-checked against every new FR/NFR that
  names one (finding #9) — clean. FR-9130 (generalized one-KeyItem-per-region) and the existing
  FR-3210/BL-0017 finding #2 are complementary, not duplicate: FR-9130 explicitly notes its
  guarantee is *stronger* (generator-enforced) than the shipped baseline's convention-only rule,
  not a restatement. FR-4300/4310's "one biome per screen"/"grammar-valid adjacency" do not
  conflict with FR-6100 (zone screen composition) — FR-6100 remains accurate for the current
  hand-authored screens; FR-4300/4310 describe the generated-world target, cross-referenced not
  duplicated (see finding #7 for the coexistence pattern this introduces).
- **2026-07-11 delta (`ADR-0012`):** `ADR-0012` cross-checked against every new/touched FR/NFR
  that names it (finding #13) — clean except the one routed conflict (`CR-05`, not a baseline
  defect). `FR-9140` and `FR-9120`/`FR-4310` (both lightly Notes-touched, not reworded) do not
  conflict — confirmed the touches only clarified the *mechanism* behind an already-accurate
  postcondition, never changed a Description/Postcondition/Acceptance-Criteria field. `FR-2330`
  and `FR-2320` are complementary current/target pairs (finding #7's pattern), not duplicates.

## Candidate Requirements disposition

**CR-01 (full save-field persistence) is now RESOLVED and SPLIT (2026-07-07)** — see finding #1
above: its facing/frame half is rejected, its per-zone ScoreItem half is approved and promoted to
FR-5220. CR-02 (carrot-invariant enforcement) in RQ-01, and CR-03 (bank-switching-ready
extensibility) and CR-04 (real-hardware/second-emulator verification) in RQ-02, remain correctly
excluded from the numbered baseline — none has a source document that states it as a present
requirement. **CR-05 (biome-blob clustering seeded from maze dead-ends, RQ-01, filed 2026-07-11)**
joins them — see finding #13: a genuine `ADR-0012` conflict, not a wording gap, correctly routed
rather than resolved here. All five remain open, each with a named owner for its next step (see
the table above and each Candidate's own Disposition field).

## Summary

The FR/NFR baseline is internally consistent and traceable — every leaf cites a real GDS-05/GDS-06
grounding, no contradictions or duplicates were found, and every honestly-tracked gap from the
architecture ladder (BL-0003/BL-0006/BL-0009/BL-0017; BL-0018 now resolved) carries through into
this baseline rather than being silently resolved. Findings #1 and #3 are both now resolved
(2026-07-07); everything else is either already correctly scoped as a Candidate/open question, or
a low-severity forward-looking watch item.

**2026-07-09 delta review:** the ten new FRs and six new NFRs grounding the adopted increment's
C8/C9/C10 streams are internally consistent, fully traceable to the now-complete architecture
baseline (three ADRs, six GDS deltas), and correctly, honestly marked as unimplemented throughout
— no requirement claims compliance it hasn't earned. The one genuinely new methodology question
this delta raises is **finding #7** (target requirements coexisting with the shipped requirements
they will eventually supersede) — not a defect today, but a pattern `05-feature-decomposition`
and later stages should resolve deliberately (formal supersession at implementation time) rather
than let drift indefinitely. Per the adopted plan §2 Phase 4's own definition of done: every new
FR/NFR traces to a GDS-ladder section and an R-topic (confirmed throughout RQ-01/RQ-02's Source
Documents fields), and §0's ten owner decisions (D1–D10) each have a visible requirement-level
descendant (D1→FR-9100's Notes; D2→FR-3220/FR-4300; D3→FR-9100; D4→NFR-1300/6500; D5→ this
baseline names no FR for the archived 3×3 world, correctly, since archival is an implementation
action not an observable requirement; D6→FR-1180/9110's scale range; D7→FR-9110; D8→FR-1190;
D9→FR-1170; D10→FR-1190). **This closes the adopted increment plan's Phase 4 and its stated
terminal deliverable.**

**2026-07-10 04-delta batch review:** see finding #11 — `BL-0020`/`BL-0022`/`BL-0026`/`BL-0028`'s
four corrections (new `FR-6400`, corrected `FR-3200` postcondition, filled `NFR-6100` RTM cell,
refreshed `NFR-1200`/`NFR-5200`/`NFR-7100` stale-verification clauses) reviewed together and
found clean — no new defect, all four confirmed accurate against the shipped tree and existing
Verification Reports. The RTM's Feature Spec/Implementation Package columns for the procgen-world
increment's 17 target rows were also filled in this same pass (now that `06`/`07` have run for
that increment), addressing finding #7's own recommendation that the target/current coexistence
pattern be tracked deliberately as downstream stages advance, not left stale.

**2026-07-11 `ADR-0012` delta review:** see finding #13 — `FR-9140`/`FR-9150`/`FR-2330` (three
new FRs) plus light Notes-only touches to `FR-9100`/`FR-9120`/`FR-4310` and one NFR-4200 touch
are internally consistent with `ADR-0012` and with each other. The delta's own honesty highlight:
rather than silently baselining a compatible-but-unrequested clustering strategy for `BL-0066`,
the genuine `ADR-0012` pass-ordering conflict its owner-preferred approach (dead-end seeding)
creates was surfaced as **CR-05**, not patched around — exactly the discipline this stage's own
SHALL-NOT-redesign-architecture rule requires. `FR-2320`/`FR-2330` extend finding #7's
coexistence pattern a third time (after `FR-1120`/`FR-1170` and `FR-3210`/`FR-3220`).
