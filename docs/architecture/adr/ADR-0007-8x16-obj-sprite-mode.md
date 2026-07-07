# ADR-0007 — 8×16 OBJ sprite mode (corrects this project's own earlier "8×8" framing)

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

The player sprite uses 8×16 OBJ mode (`LCDC` bit 2 set, `LCDC=0x97`), each animation frame an
adjacent even/odd tile-index pair — confirmed by direct read
([R103](../../research/encyclopedia/R103-lcdc-stat-registers.md),
[R105](../../research/encyclopedia/R105-oam-sprites-dma.md),
[GDS-08](../08-presentation-architecture.md) §2). This mode was adopted via commit `9a587ac`
specifically to fix an earlier invisible-sprite bug — a real, already-made architectural decision
under time pressure, not an incidental default. Notably, this project's own GDS-08 scaffold stub
(authored before this ladder's bootstrap pass reached it) stated "8×8 OBJ pairs," and the
`docs/architecture/adr/INDEX.md` suggestion list inherited that same stale wording — both were
corrected during GDS-08's authoring pass to match the shipped `LCDC=0x97` fact. This ADR records
the correct, verified mode as the decision of record.

## Decision

Keep 8×16 OBJ mode for the player sprite (and, by extension, collectible sprites sharing the same
OAM budget). Any future sprite work must target 8×16 mode's tile-pair convention, not 8×8.

## Consequences

- 8×16 mode halves the number of distinct sprite *slots* needed per visual frame (one OAM entry
  covers a 8×16 region instead of two 8×8 entries), which is why it resolved the invisible-sprite
  bug commit `9a587ac` fixed — the bug was almost certainly an OAM-entry/tile-index mismatch under
  the previous (8×8, or incorrectly configured) setup.
- Every future sprite (a new collectible, an enemy, an NPC) must be authored as an adjacent
  even/odd tile-index pair to match this mode, not as an independent single 8×8 tile — a real
  constraint on future content-authoring work ([GDS-08](../08-presentation-architecture.md) §6's
  process note).
- This ADR is also a standing reminder that **this project's own docs have been wrong about this
  fact before** — a concrete instance of the doc-staleness risk this whole pipeline exists to
  guard against (parallel to the vision-layer correction recorded at
  [MSTR-001](../../master/MSTR-001-program-vision.md) §8).
