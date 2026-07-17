# GDS-00 — Vision

> **Status: ✅ Authored (revised 2026-07-17, v4.0 — see
> [MSTR-001 §8/§8a](../master/MSTR-001-program-vision.md#8-vision-amendment-log); previously
> revised 2026-07-09, v3.0; corrected 2026-07-06, same-day revision of the 2026-07-06 bootstrap
> draft).**
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

1. **Platform envelope, current shape (MSTR-001 C1/C2):** CGB color, MBC1+RAM+BATTERY,
   **single-bank today but not a permanent ceiling** (C7 — see point 6 below). Design inside the
   current 32KB box until a specific feature's byte cost genuinely can't fit (assumption A1);
   don't pre-emptively architect for bank switching before that's the real constraint, but don't
   design as if a single bank is the final word either. **C2 was amended at v3.0**: a battery
   save still persists across power-off, but *loading* it is no longer automatic — the target
   flow is boot → main menu (continue / new game), with new-game creation the sole place a
   world's seed and scale (point 6) are entered. This is a stated target, not yet built; the
   currently shipped auto-load-on-boot remains accurate until the corresponding package ships.
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
   erodes it as a side effect. **v3.0 names two deliberate amendments in flight** (not yet
   built): the fixed 3×3 layout is being superseded by C10's procedurally generated world
   (archived under `legacy/` when the corresponding package lands, per the `IP-9040` precedent —
   not deleted), and auto-load is being superseded by C2's player-initiated load. Until those
   packages ship, the *currently shipped* 3×3/auto-load behavior remains the protected floor —
   design levels should build the *new* architecture toward the amendment, not assume it's
   already live.
5. **Session shape (A5):** short, gentle, fail-state-free handheld sessions for an all-ages
   player. Pacing, difficulty, and content decisions at GDS-01/GDS-08 inherit this register
   assumption until its trigger fires. **This assumption is expected to hold even as C7's world
   scale grows** — a bigger world is not the same design lever as a harder or longer one. A
   generated world's scale parameter (point 6) must not be read as license to lengthen a
   *session* — scale changes world size, not the fail-state-free, interruptible pacing this
   assumption protects. **v4.0 carve-out (C11, 2026-07-17):** A5's trigger fired — the project
   owner directed a bounded exception, not a reversal: an opt-in combat sub-mode on Infinite
   Mode's map, intended for a parent/adult player, gated behind its own explicit entry point, may
   be tonally grimmer (real adversarial mechanics, damage, a fail state). Every mode a child
   reaches through the game's own default flow (finite mode; Infinite Mode's base collect-loop)
   keeps A5's fail-state-free, non-violent guarantee exactly as before — GDS-01/GDS-08 design
   work on C11's own gated mode is the only place this assumption's exception applies, and that
   design work must keep the gate genuinely separate from the default flow, not blur it.
6. **Long-term scale direction (C7), now concrete (C8/C9/C10, v3.0):** C7's "how many
   zones/biomes, at what scale" question has its first concrete answer: the world is
   **deterministically procedurally generated** from a **seed** and a **world-scale** parameter,
   both entered once at new-game creation (C10) — not a hand-authored zone count to keep
   growing. Downstream design must additionally treat as given: **a logical biome-adjacency
   grammar** governs which regions may border which (C9 — one biome per screen; a coherent flow
   such as water → beach → grassland → hills → mountains → sky, never a disjointed pairing), the
   collect-goal is **item-agnostic** and themed per region rather than fixed to "carrot," and
   **presentation itself is a checked quality gate** (C8 — smooth, every screen clean), not an
   informal craft preference. GDS-01 (Concept of Play) and GDS-03 (Architecture) are where these
   become concrete: a generator architecture (algorithm choice explicitly delegated to research,
   not fixed here), a seed & scale model, and — as this level already anticipated — a
   bank-switching strategy, now an expected near-term dependency of the generator itself and
   C9's expanded biome tile sets, not merely a someday-eventuality (currently ~9.1KB of headroom
   remains).

## Merge gate

- [x] Stub body replaced with real content addressing the stated Purpose.
- [x] Every "merges from" source consulted; the merge decision recorded in prose here.
- [x] No production code or byte-level detail beyond what this level calls for.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md` flipped together.
- [x] Previous level's gate was fully closed before this level was authored. *(GDS-00 is the
      first level — not applicable.)*

**Merge decision (2026-07-06, revised same day; reaffirmed 2026-07-09 at v3.0):** MSTR-001
**carries** all purpose/audience/commitment statements; GDS-00 **points** to them and adds only
the design-facing consequences above — the two documents never restate the same sentence.
`Claude.md`'s intro paragraph remains the intended working quick-reference summary and, as of
`IP-9030` (2026-07-09), is current again — describing the shipped pre-v3.0 game accurately (see
MSTR-001 §8's v3.0 blast-radius table: v3.0's new commitments are forward-looking targets, not
yet built, so `Claude.md` is not yet stale with respect to them).
