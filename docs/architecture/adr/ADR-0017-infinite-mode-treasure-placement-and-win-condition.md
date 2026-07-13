# ADR-0017 — Infinite Mode treasure placement (decoupled from maze structure) and score-chasing win condition

**Status:** Accepted (2026-07-13)

## Context

[R114](../../research/encyclopedia/R114-streaming-world-generation-feasibility.md) found the only
proven zero-memory streaming-compatible maze algorithm (Binary Tree,
[ADR-0016](ADR-0016-streaming-infinite-mode-generation-architecture.md)) has "no dead-ends (and
never will be any dead-ends) facing either north or west" — a direct conflict with
[BL-0094](../../pipeline/backlog.md)'s carried-forward design ("populate a treasure only at dead
ends"), itself inherited unmodified from `IP-1021`'s just-shipped finite-mode dead-end-priority win
condition (`ADR-0015`).

[R216](../../research/encyclopedia/R216-infinite-mode-win-condition-design.md) resolves this by
proposing to decouple treasure placement from maze structure entirely, reusing the same
`hash(SEED, row, col)` positional-determinism technique `R114` already established for biome
assignment. R216 also confirms `BL-0094`'s own score-chasing design (running count + top-3
persisted, no name-entry UI) is the historically correct genre answer for non-terminating play
(the arcade high-score convention), not an improvised fallback, and needs no amendment.

**User authorization:** as `ADR-0016`.

## Decision

**1. A region holds treasure iff `hash(SEED, row, col) mod K == 0`, for a tuned density constant
`K` — independent of that region's maze connectivity or dead-end status.**

- This is a genuine departure from `BL-0094`'s literal "at dead ends" wording, adopted deliberately
  and named explicitly here rather than silently substituted, per R216's own flag: "dead-end
  hunting" and "tuned-density exploration reward" are different player experiences. The tradeoff:
  this decision rewards exploration generally rather than maze-solving specifically, in exchange
  for removing all dependency on which maze algorithm `ADR-0016` picks (Binary Tree's bias becomes
  irrelevant to treasure placement specifically, though it may still bear on maze *feel* generally
  — ADS-001 Open Question 2, not this ADR's concern).
- **`K`'s exact value is an implementation-time tuning question, not fixed here.** R216 recommends
  anchoring near R215's measured `scale=9` finite-world dead-end density (~6.4%) as a starting
  point, given density should sit in a comparable low-single-digit-percent range at large extent
  to avoid feeling either too sparse (against R206's short-loop pacing preference) or too dense
  (undermining the scarce-tier property R201 established for the finite game's own collectible
  tiers). `07-implementation-planning`/`08-code-implementation` settle the actual constant.
- Computable the instant a region is materialized (same `hash(SEED, row, col)` reseed `ADR-0016`
  already performs for biome/connectivity) — no dependency on maze-carve completion, no
  whole-grid/whole-maze pass.

**2. Win condition: adopt `BL-0094`'s score-chasing design as specified, unamended** — a running
count of treasures collected during the current run, compared against a persisted top-3 high-score
table on run end; **no character-name-entry UI** (the classic arcade convention's original purpose
— proving whose initials are on top to other players at a shared cabinet — does not transfer to a
single-player handheld cartridge with one save slot).

**3. "Infinite" means unbounded exploration extent with bounded persisted memory, not literally
unbounded save data** — the running count and top-3 table are small, fixed-size fields; nothing
about this win condition requires tracking collection state for every region ever generated (unlike
a hypothetical "collect everything" condition would), consistent with `ADR-0016`'s
visited-region-ledger save model.

**4. Run/session shape is explicitly NOT decided by this ADR.** Whether an Infinite Mode
playthrough is indefinitely resumable (matching the finite game's save/continue convention) or is
its own bounded "run" needing a new end-condition mechanic (death/retreat/checkpoint, which this
game does not currently have) is genuine new mechanic-design scope, routed to a future
`04-requirements-engineering` pass (ADS-001 Open Question 1) — this ADR's win-condition state
(running count, top-3 table) is compatible with either answer and does not need to anticipate
which is chosen.

## Consequences

- **Resolves the design half of `BL-0082`** together with `ADR-0016`.
- **`BL-0094` is ready to advance to `04-requirements-engineering`** once triaged — its own design
  is adopted with one named amendment (decoupled treasure placement) rather than shipped literally.
- **No `GDS-04`/`GDS-07` delta yet** — the same deferral `ADR-0016` records, for the same reason
  (new epic, not yet formalized into the ladder).
- **Does not decide `K`, run/session shape, or Binary Tree's aesthetic acceptability** — all three
  are named, unresolved Open Questions routed to specific downstream owners (ADS-001).
- **Does not itself implement anything** — the hash-density check, the score-tracking WRAM/SRAM
  fields, and the run-end comparison logic ship through the normal `04`→`08` pipeline, gated by G3.

## Related

- Synthesized in [ADS-001](../ADS-001-streaming-infinite-world-generation.md) alongside
  [ADR-0016](ADR-0016-streaming-infinite-mode-generation-architecture.md) (the generation
  architecture this decision's hash-density technique reuses).
- Grounded by [R216](../../research/encyclopedia/R216-infinite-mode-win-condition-design.md)
  (win-condition design, decoupling proposal) and
  [R215](../../research/encyclopedia/R215-procgen-win-condition-design.md) (dead-end density data
  reused as the density-tuning anchor).
- Builds on, without amending, [ADR-0015](ADR-0015-dead-end-anchored-treasure-and-win-condition.md)
  (the finite-mode treasure/win-condition decision this ADR's Infinite Mode counterpart deliberately
  diverges from — dead-end-anchored placement remains correct and unchanged for the finite mode).
- Resolves [BL-0094](../../pipeline/backlog.md)'s own open amendment question.
