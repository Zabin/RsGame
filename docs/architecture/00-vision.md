# GDS-00 — Vision

> **Status: ✅ Authored (corrected 2026-07-06, same-day revision of the 2026-07-06 bootstrap
> draft — see [MSTR-001 §8](../master/MSTR-001-program-vision.md#8-vision-amendment-log)).**
> Owned by the `01-vision` skill, together with
> [MSTR-001](../master/MSTR-001-program-vision.md) and the
> [strategic assumptions register](strategic-assumptions-register.md). This level is the
> design-facing restatement of the program vision; GDS-01 onward build on it and are owned by
> `03-architecture-design-synthesis`.

## Purpose

The design-facing restatement of the program vision (MSTR-001) that the rest of the GDS ladder
builds on.

## The vision, restated for designers

**Purpose and audience live in [MSTR-001](../master/MSTR-001-program-vision.md) §1–§2 and are not
duplicated here.** What every downstream design level must hold as given:

1. **Platform envelope, current shape (MSTR-001 C1/C2):** CGB color, MBC1+RAM+BATTERY with a
   battery save that auto-loads, **single-bank today but not a permanent ceiling** (C7 — see
   point 6 below). Design inside the current 32KB box until a specific feature's byte cost
   genuinely can't fit (assumption A1); don't pre-emptively architect for bank switching before
   that's the real constraint, but don't design as if a single bank is the final word either.
2. **Build-as-design-medium (C3):** tiles, screens, music, and logic are Python source assembled
   by the modular chain. Design levels therefore express content as data the pipeline emits —
   never as hand-patched bytes or external-tool artifacts.
3. **Verification-first, in principle (C4):** a behavior should exist only once a named emulator
   check proves it. **This is currently not true in practice** — `test_rom.py` tests the
   pre-rewrite game, not the shipped Bunny Quest code (MSTR-001 §8). Treat "a `test_rom.py` check
   passes" as *not yet meaningful evidence* until that gap is remediated; GDS-04/05 must derive
   requirements from the real shipped behavior (direct code read), not from the current test
   file's assertions.
4. **The shipped game is the protected baseline (C5):** **Bunny Quest** — a 3×3 grid of nine
   zones (Beach, Forest, Mountain, Lake, Village, Cave, Desert, Plains, Castle), star/flower
   scoring, a 9-carrot win condition, save/map/victory flows, auto-load — is the floor design
   levels build from. Design work extends or deliberately (and traceably) amends it; it never
   erodes it as a side effect.
5. **Session shape (A5):** short, gentle, fail-state-free handheld sessions for an all-ages
   player. Pacing, difficulty, and content decisions at GDS-01/GDS-08 inherit this register
   assumption until its trigger fires. **This assumption is expected to hold even as C7's world
   scale grows** — a bigger world is not the same design lever as a harder or longer one.
6. **Long-term scale direction (C7, new):** downstream design should treat "how many zones/biomes,
   at what scale" as an open, growing question — not "nine is the design," but "nine is where we
   are on the way to a Zelda/Pokémon-class overworld." GDS-01 (Concept of Play) and GDS-03
   (Architecture) are where this first becomes concrete: a zone-count/world-topology model that
   scales past a fixed 3×3 grid, and — eventually — a bank-switching strategy once the single-bank
   budget is actually exhausted (currently ~9.6KB of headroom remains).

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's gate was fully closed before this level was authored. *(GDS-00 is the
      first level — not applicable.)*

**Merge decision (2026-07-06, revised same day):** MSTR-001 **carries** all purpose/audience/
commitment statements; GDS-00 **points** to them and adds only the design-facing consequences
above — the two documents never restate the same sentence. `Claude.md`'s intro paragraph remains
the intended working quick-reference summary, but is **currently known-stale** (describes the
pre-rewrite game) — not superseded by this level, but not to be trusted for current-state facts
until a documentation-refresh package corrects it (see MSTR-001 §8's blast-radius table).
