# RQ-03 — Requirements Review

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06).** Owned by `04-requirements-engineering`.
> Reviews the final [RQ-01](01-functional-requirements.md)/[RQ-02](02-non-functional-requirements.md)
> baseline for duplicates, conflicts, ambiguities, gaps, impossible requirements, architecture
> violations, and missing verification/traceability. **Report only — this document applies no
> fixes**; every finding below routes to an owner as a separate follow-up.

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Ambiguity / unresolved design question | FR-5210, NFR-5200, BL-0018 | The save/restore requirements are internally consistent (NFR-5200 is honestly scoped to "whatever fields are declared persisted," FR-5210 documents the current declared scope), but **whether the current declared scope is the *intended* one is genuinely open** — the baseline cannot silently assume either "this is a bug to fix" or "this is intentional design." | Medium | Requires an explicit design/user decision before any future package (06/07/08) treats CR-01 (full-field persistence) as in-scope or out-of-scope. Do not let a future stage infer an answer from FR-5210's Priority field ("Must, as-built") — that field describes current behavior, not intended scope. Owner: the user, or `03-architecture-design-synthesis` if reopened as an architecture question. |
| 2 | Missing enforcement / gap | FR-3210, BL-0017, CR-02 | FR-3210 describes carrot-collection behavior *assuming* exactly one Carrot exists per zone, but no requirement in this baseline mandates that invariant be *enforced* — it is an unchecked authoring convention (`ZONE_COLLECTS`). This is a real, if low-severity, gap: a future content package could violate the invariant with nothing in this baseline (or any test) catching it. | Low | CR-02 (Candidate Requirements, RQ-01) correctly declines to baseline this as a numbered NFR today, per BL-0017's own SCHEDULED disposition (a Verification Checklist item on any future `ZONE_COLLECTS`-touching package, not a standalone requirement). No baseline change needed; keep BL-0017 open until such a package exists. |
| 3 | Missing verification (systemic, cross-cutting) | NFR-7100, and every FR-1xxx/2xxx/3xxx/5xxx/6xxx whose Verification Method names "Test" | NFR-7100 documents (honestly) that `test_rom.py`'s T2–T10 suites test pre-rewrite semantics and cannot currently verify anything (BL-0006, Critical). This means **every FR above whose Verification Method is "Test" is not, in fact, currently verifiable by the existing suite** — the method is correct in principle but unsatisfiable in practice until BL-0006/BL-0008 lands. This is the single largest latent risk in the baseline: a future stage-08/09 run could believe "Test" next to an FR ID means a passing check exists today, when none does. | High | Read every "Verification Method: Test" cell in RQ-01 as *the intended method once BL-0006/BL-0008 is remediated*, not as current coverage. Recommend `07-implementation-planning` treat the `test_rom.py` rewrite as a high-priority package independent of feature work — it blocks honest verification for the entire FR baseline, not just the NFR it's filed against. Owner: `07-implementation-planning`/`08-code-implementation`, per BL-0006/BL-0008. |
| 4 | Forward-looking conflict risk (not a current conflict) | NFR-4000, MSTR-001 C7, ADR-0001 | NFR-4000 ("Met," single 32768-byte bank) and vision commitment C7 (Zelda/Pokémon-scale world, anticipating future bank-switching) are not in conflict *today* — NFR-4000 explicitly names its own future-supersession trigger. But nothing in this baseline currently *watches* the 9.6KB headroom as it's consumed; a future content package could push usage close to the ceiling without any requirement flagging that NFR-4000's "Met" status is approaching its limit. | Low | Recommend any future package that materially increases ROM usage include a checklist item confirming remaining headroom against the 32768-byte ceiling, and that this NFR's status be re-affirmed (not silently left "Met") once headroom drops below some threshold (e.g. 2KB) — a concrete number to set is itself future `03-architecture-design-synthesis`/`05-feature-decomposition` work, not decided here. |
| 5 | Weak/derived traceability (self-flagged, reviewed here for discipline) | NFR-2100 | NFR-2100 (deterministic state-machine behavior) has no single direct GDS-06 statement as its source — it is derived from the FR baseline's own testability demands, and RQ-02 already flags this honestly in its own Notes field. | Low | No baseline change needed — the derivation is sound (a non-deterministic state machine would make FR-1xxx's Acceptance Criteria untestable) and the document already discloses it rather than presenting it as a direct citation. Recorded here only to confirm the Review actually checked it, not to raise a new concern. |
| 6 | Missing requirement (correctly absent, not an oversight) | Usability category (RQ-02) | No NFR states a player-facing usability standard (control remapping, colorblind-safe palette guarantees, difficulty accessibility, etc.). | Low (informational) | Correctly left as "(none derivable from inputs)" per the writing rule against inventing requirements — not a defect in this baseline. Flagged only as an open scope question for a future `01-vision`/`02-research-game-design` pass if usability becomes an explicit program goal; no action required now. |

## Duplicates / contradictions checked and found clean

- FR-1160 (VICTORY state transition) and FR-3300 (the CarrotCount==9 condition that triggers it)
  are complementary, not duplicate — FR-1160 correctly declares a dependency on FR-3300 rather
  than restating its condition.
- No FR/NFR contradicts another FR/NFR or a binding ADR (ADR-0001 through ADR-0008 cross-checked
  against every FR/NFR that names one in its Related ADRs field).
- No requirement crosses into implementation detail (WRAM addresses, opcodes) — GDS-07's
  byte-level facts are cited only where GDS-05/GDS-06 already cited them, never re-derived here.

## Candidate Requirements disposition

Both CR-01 (full save-field persistence) and CR-02 (carrot-invariant enforcement) in RQ-01, and
CR-03 (bank-switching-ready extensibility) and CR-04 (real-hardware/second-emulator verification)
in RQ-02, are correctly excluded from the numbered baseline — none has a source document that
states it as a present requirement. All four remain open, each with a named owner for its next
step (see the table above and each Candidate's own Disposition field).

## Summary

The FR/NFR baseline is internally consistent and traceable — every leaf cites a real GDS-05/GDS-06
grounding, no contradictions or duplicates were found, and every honestly-tracked gap from the
architecture ladder (BL-0003/BL-0006/BL-0009/BL-0017/BL-0018) carries through into this baseline
rather than being silently resolved. **The one finding requiring action before downstream stages
proceed on Test-verified work is #3** (the systemic Test-method gap) — everything else is either
already correctly scoped as a Candidate/open question, or a low-severity forward-looking watch
item.
