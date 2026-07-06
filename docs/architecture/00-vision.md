# GDS-00 — Vision

> **Status: ✅ Authored (bootstrap baseline, 2026-07-06).** Owned by the `01-vision` skill,
> together with [MSTR-001](../master/MSTR-001-program-vision.md) and the
> [strategic assumptions register](strategic-assumptions-register.md). This level is the
> design-facing restatement of the program vision; GDS-01 onward build on it and are owned by
> `03-architecture-design-synthesis`.

## Purpose

The design-facing restatement of the program vision (MSTR-001) that the rest of the GDS ladder
builds on.

## The vision, restated for designers

**Purpose and audience live in [MSTR-001](../master/MSTR-001-program-vision.md) §1–§2 and are not
duplicated here.** What every downstream design level must hold as given:

1. **Platform envelope (MSTR-001 C1/C2):** one 32KB ROM bank, CGB color, MBC1+RAM+BATTERY with a
   battery save that auto-loads. Design inside this box; a design that needs more triggers
   assumption A1/A3 — it doesn't quietly get more.
2. **Build-as-design-medium (C3):** tiles, screens, music, and logic are Python source assembled
   by the modular chain. Design levels therefore express content as data the pipeline emits —
   never as hand-patched bytes or external-tool artifacts.
3. **Verification-first (C4):** a behavior exists when a named emulator check proves it. Every
   design level's statements must be phrased so stage 04 can derive testable requirements and
   `test_rom.py` can verify them headlessly.
4. **The shipped game is the protected baseline (C5):** v2.1's known-good behavior — title →
   intro → three-zone play, collect/score/gift mechanics, save/map/victory flows, auto-load — is
   the floor. Design work extends or deliberately (and traceably) amends it; it never erodes it
   as a side effect.
5. **Session shape (A5):** short, gentle, fail-state-free handheld sessions for an all-ages
   player. Pacing, difficulty, and content decisions at GDS-01/GDS-08 inherit this register
   assumption until its trigger fires.

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's gate was fully closed before this level was authored. *(GDS-00 is the
      first level — not applicable.)*

**Merge decision (2026-07-06):** MSTR-001 **carries** all purpose/audience/commitment statements;
GDS-00 **points** to them and adds only the design-facing consequences above — the two documents
never restate the same sentence. `Claude.md`'s intro paragraph remains the working
quick-reference summary; it is not superseded by this level (later ladder levels record their own
merge decisions against `Claude.md`'s technical sections).
