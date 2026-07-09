# GDS-10 — Requirements Traceability Matrix level

> **Status: ✅ Authored (bootstrap as-built, 2026-07-06; ID-scheme table refreshed 2026-07-09 for
> the procgen-world increment — see "Scheme confirmation" below).** Owned by
> `03-architecture-design-synthesis`. Builds on [GDS-09](09-interface-specification.md); it is
> the last level of the global ladder. This is an as-built scaffold: it states the traceability
> *scheme* the project uses; the row-level matrix itself belongs to `docs/requirements/` (RQ-04).

## Purpose

How traceability is carried at the architecture level; defers row-level detail to
[`docs/requirements/04-requirements-traceability-matrix.md`](../requirements/04-requirements-traceability-matrix.md)
once authored.

## Content

### 1. Why this level doesn't contain a matrix yet

A traceability matrix's rows link a requirement to its origin (research/vision) on one side and
its implementation/verification evidence on the other. As of this pass, the origin side (GDS-00
through GDS-09, `docs/research/`) is fully authored, but the requirements baseline
(`docs/requirements/RQ-01`…`RQ-04`) and everything downstream of it (feature planning, feature
specs, implementation packages) are still `⛔` per `ROADMAP.md`. A matrix authored now would have
populated origin columns and empty destination columns — indistinguishable from a stub pretending
to be data. **This level therefore documents the scheme, not the rows**; `RQ-04` becomes the
authoritative row-level matrix once `04-requirements-engineering` runs, per this project's own
gate discipline (no level/stage fabricates content for a downstream stage that hasn't run).

### 2. The ID-namespace scheme (confirmed by direct read of `ROADMAP.md`)

Every document this project produces carries a stable ID prefix, unique within its theme, that a
traceability row can cite without ambiguity:

| Prefix | Theme | Example |
|---|---|---|
| `MSTR-xxx` | Program vision (commitments `C1`…`C10` live inside `MSTR-001`, not a separate prefix) | `MSTR-001`, its commitment `C10` |
| `R1xx`/`R2xx`/`R3xx` | Research encyclopedia (hardware/design/tooling tiers) | `R105`, `R203`, `R302`, `R111`/`R212`/`R213`/`R214` (2026-07-09) |
| `GDS-xx` | Global architecture ladder | `GDS-07` |
| `AR-ASSUME` | Strategic assumptions register (entries `A1`…`A10`) | `A2`, `A9`/`A10` (2026-07-09) |
| `ADR-xxxx` | Architecture Decision Records | `ADR-0001`…`ADR-0011` (`ADR-0009`/`ADR-0011` supersede `ADR-0001`, 2026-07-09) |
| `RQ-0x` | Requirements baseline | `RQ-01`…`RQ-04` (authored run #17, 2026-07-06) |
| `FP-0x` | Feature planning | `FP-01`…`FP-05` (authored run #19, 2026-07-07) |
| `FS-xxx` | Feature specifications | `FS-101` |
| `IM-00`/`IP-xxxx` | Implementation plans/packages | `IM-00` (Master Build Plan), `IP-9010`…`IP-9040`, `IP-1010` |
| `VR-xxxx` | Verification reports | `VR-9010`, `VR-1010`, `VR-9020`, `VR-9040` |
| `RV-xxx` | Reviews (content/integration/release) | *(⛔ not yet authored — awaits `10-integration-review`/`11-release-readiness`)* |
| `BL-xxxx` | Pipeline backlog (findings/decisions/deferrals) | `BL-0009`, `BL-0029`…`BL-0033` (2026-07-09) |

### Scheme confirmation (2026-07-09, procgen-world increment)

**No new prefix was needed for this increment's artifacts** — every one fits an existing family:
`MSTR-001`'s **C8/C9/C10** are ordinary lettered commitments inside the existing `MSTR-xxx`
document (not a new ID class); **`ADR-0009`/`ADR-0010`/`ADR-0011`** are ordinary sequential
`ADR-xxxx` entries (the *first* instance of one ADR superseding another, but the supersession
relationship is stated in prose per Workflow C's existing "supersede, never rewrite" rule, not a
new field); the **GDS-01/04/07/08/09 deltas** are ordinary edits to existing `GDS-xx` documents
(a "delta" is a documented *editing convention* this increment established — dated delta
sections within an existing level — not a new ID or a new level number). The scheme scales
without modification.

**Housekeeping finding, not fixed by this pass:** the table above was stale before this
increment touched it — it read "not yet authored" for `RQ`/`FP`/`FS`/`IP`/`VR` rows that were
in fact populated back at the bootstrap increment's stage 04–09 runs (2026-07-06/07), predating
this correction. Per this document's own §"Merge decision" below, `RQ-04` was supposed to
become the authoritative row-level matrix — with this level's §3/§4 becoming pointers to it —
once `RQ-04` was authored; that transition itself was never executed. This pass corrects only
the example column (a factual refresh, needed to honestly confirm the new increment's artifacts
fit); it does **not** execute the deeper §3/§4-becomes-a-pointer restructuring, which is
bootstrap-increment housekeeping outside this delta's scope — filed as a backlog finding for a
dedicated future pass instead of executed inline here.

This is already load-bearing practice, not a proposal: every GDS level authored so far cites its
grounding using exactly these prefixes (e.g. GDS-08 §4 cites `BL-0009`'s correction; GDS-09 cites
`R101`/`R302`/`R109`). The scheme this level states is a description of an existing convention.

### 3. How a traceability row will be built once `RQ-xxx` exists

Per the ID scheme above, a future `RQ-04` row is a tuple: **origin** (one or more of `MSTR-001`'s
commitments, a `GDS-0x` §, an `R-xxx` topic) → **requirement** (`RQ-01`/`RQ-02` FR/NFR ID) →
**feature** (`FS-xxx`) → **implementation** (`IP-xxxx`) → **verification** (`VR-xxxx`). The
origin-side columns for that future matrix are already fully populated by this ladder — GDS-05's
six FR groupings and GDS-06's five NFRs are the direct ancestors `RQ-01`/`RQ-02` will formalize
into numbered `FR-xxxx`/`NFR-xxxx` IDs when `04-requirements-engineering` runs. **Contract for that
future work: `RQ-01`/`RQ-02` must cite back to the specific GDS-05/GDS-06 grouping each numbered
requirement formalizes** — not restate the capability from scratch — so the matrix's origin
column is a real link, not a re-derivation.

### 4. Backlog IDs are already a de facto cross-cutting traceability lane

`BL-xxxx` entries already thread through every layer authored so far — e.g. `BL-0009` was raised
at the research tier (R101), corrected at GDS-07 (Data Model), and cited again at GDS-08
(Presentation Architecture). This is the one traceability lane already exercised end-to-end
across three document tiers in this project, and the future `RQ-04` matrix should treat resolved/
open `BL-xxxx` references the same way it treats `GDS-0x`/`R-xxx` origins — as citable anchors,
not prose asides.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's (`GDS-09`) gate was fully closed before this level was authored.

**Merge decision (2026-07-06):** The stated "merges from" source, `docs/requirements/`, does not
exist yet (`RQ-01`…`RQ-04` are all `⛔` in `ROADMAP.md`) — there is nothing to pull in. **Decision:
this level stays authoritative for the traceability *scheme* (the ID namespace, the row shape,
the backlog-as-cross-cutting-lane observation) until `RQ-04` is authored, at which point `RQ-04`
becomes authoritative for row-level data and this level's §3/§4 become the pointer** ("see RQ-04
for the populated matrix; this level documents the scheme it must follow"). No `Claude.md`/
`memory.md` section is superseded — neither document previously attempted a traceability scheme.
This closes the global ladder (`GDS-00`…`GDS-10`); stage 03 is now fully authored pending only the
deferred as-built ADR pass (`BL-0016`).

**Delta record (2026-07-09):** the ID-scheme table (§2) refreshed with current examples and a
"Scheme confirmation" subsection added, per the adopted increment plan's Phase 3 — confirming
this increment's artifacts (MSTR-001 C8–C10, ADR-0009–0011, GDS-01/04/07/08/09 deltas) need no
new ID prefix or scheme change. This closes stage 03's GDS-ladder-delta phase for the current
increment (all levels this increment touches — 01/04/07/08/09/10 — now carry a dated delta).
The deeper "§3/§4 should become a pointer to `RQ-04`" transition this document's original merge
decision anticipated is a separate, still-open housekeeping item — filed as a new backlog
finding, not executed by this delta.
