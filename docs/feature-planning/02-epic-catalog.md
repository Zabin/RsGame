# FP-02 — Epic Catalog

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07); delta 2026-07-10 (procgen-world
> increment).** Owned by `05-feature-decomposition`. Groups [FP-03](03-feature-catalog.md)'s
> thirteen Features into five Epics. Every Feature belongs to exactly one Epic. **New Epic
> EP-5000** holds the procgen-world increment's world-generation-and-narrative Features;
> **FEAT-1100** joins EP-1000 (state-machine extension); **FEAT-5300** joins EP-3000
> (save-system extension).

## EP-1000 — Core Gameplay Loop

- **ID:** EP-1000
- **Title:** Core Gameplay Loop
- **Purpose:** The moment-to-moment play experience — what state the game is in, how the player
  moves, and how they collect and win.
- **Features Included:** FEAT-1000 (Game State Machine & Menu Flow), FEAT-2000 (Player Movement &
  Zone Traversal), FEAT-3000 (Collectibles, Scoring & Victory), FEAT-1100 (Main Menu & New-Game
  Flow, new — not yet implemented).
- **Modules:** `asm_game.py` (all Features are primarily this module), `tilemaps.py`
  (FEAT-2000's arrow signaling; FEAT-1100's new main-menu/seed-scale-entry screens).
- **Estimated Scope:** Three of four Features already shipped in full. **FEAT-1100 is new work**
  — extends the state machine with three new states, gated on EP-5000's world-generation routine
  (FEAT-9000) existing to call into.
- **Risks:** `BL-0006`'s prior test-suite-currency risk is **resolved** (IP-9010 VERIFIED,
  2026-07-07) — no longer a live risk for this Epic. FEAT-1100 carries its own new-work risk:
  retiring FR-1120's auto-load bypass is a deliberate protected-baseline change needing careful
  negative testing (see FP-03's FEAT-1100 entry).
- **Dependencies:** EP-2000 (World Content & Presentation) supplies the content this Epic operates
  on; EP-5000 (World Generation & Visual Narrative) — FEAT-1100 triggers FEAT-9000's generation
  routine.

## EP-2000 — World Content & Presentation

- **ID:** EP-2000
- **Title:** World Content & Presentation
- **Purpose:** The game's explorable content and how it's visually presented to the player.
- **Features Included:** FEAT-4000 (Zone & Screen Composition), FEAT-6000 (Presentation & HUD).
- **Modules:** `tilemaps.py`, `tiles.py`, `asm_game.py` (HUD digit-writing only).
- **Estimated Scope:** Already shipped in full (9 zones, 14 screens). The procgen-world
  increment's generated-region rendering extends this Epic's *pattern* without modifying these
  Features directly — see EP-5000 (FEAT-4100).
- **Risks:** `NFR-1200` (score-bar write timing) is **resolved** (IP-9020 VERIFIED, 2026-07-07) —
  no longer a live risk. The CGB palette/ROM-headroom watch items (`BL-0009`/`BL-0019`) remain a
  standing convention for future ROM/palette-growing packages, not a current defect.
- **Dependencies:** None — a foundational content Epic that EP-1000 operates on top of.

## EP-3000 — Persistence

- **ID:** EP-3000
- **Title:** Persistence
- **Purpose:** Saving and restoring player progress across power-off.
- **Features Included:** FEAT-5000 (Save/Load System, as-built), FEAT-5100 (Per-Zone ScoreItem
  Persistence, shipped, VERIFIED 2026-07-07), FEAT-5300 (Generated-World Save Persistence, new —
  not yet implemented).
- **Modules:** `asm_game.py`.
- **Estimated Scope:** FEAT-5000 and FEAT-5100 are both fully shipped and independently verified.
  **FEAT-5300 is this Epic's new work** — a second, structurally-identical instance of FEAT-5100's
  version-byte pattern, extended to seed/scale/per-region flags.
- **Risks:** FEAT-5100's save-format-compatibility question was resolved before implementation
  (pre-upgrade saves default to "all uncollected," proven by `T11.d`) — no longer open. FEAT-5300
  carries an analogous risk of its own: a wrong version-guard bump could misread pre-upgrade save
  bytes as seed/scale/region data; mitigated by following `IP-1010`'s synthetic-fixture pattern.
- **Dependencies:** EP-1000 (the SAVE state and the score/carrot data being persisted); EP-5000
  (World Generation & Visual Narrative) — FEAT-5300 persists FEAT-9000's generation output.

## EP-4000 — Engineering Quality & Verification

- **ID:** EP-4000
- **Title:** Engineering Quality & Verification
- **Purpose:** The cross-cutting, non-player-visible guarantees (ROM budget, module boundaries,
  build determinism, verification approach) every other Epic depends on holding true.
- **Features Included:** FEAT-7000 (Engine Quality & Build Infrastructure).
- **Modules:** All six modules, plus `test_rom.py` and the `run-bunnygarden` harness.
- **Estimated Scope:** Already shipped for 4 of 6 included NFRs; the two prior tracked
  non-compliances have both since resolved (`NFR-1200`/`BL-0003` fixed by `IP-9020`, VERIFIED;
  `NFR-7100`/`BL-0006` fixed by `IP-9010`, VERIFIED) — `NFR-4000`'s future C7 supersession remains
  the only still-open, not-yet-due item.
- **Risks:** **No longer the highest risk in the catalog** — `NFR-7100`'s non-compliance was the
  Critical item; it is now Met (`IP-9010`/`VR-9010`, 2026-07-07), confirmed again by
  `10-integration-review`'s bootstrap-tranche pass (2026-07-10). Only `NFR-4000`'s future-trigger
  watch item remains, not due.
- **Dependencies:** None — this Epic is the infrastructure floor; every other Epic implicitly
  depends on it.

## EP-5000 — World Generation & Visual Narrative

- **ID:** EP-5000
- **Title:** World Generation & Visual Narrative
- **Purpose:** Generate a deterministic, grammar-valid, fully-reachable world from (seed, scale)
  and tell the game's story through it visually — one biome per screen, flowing logically into
  the next, with no text-dialogue requirement.
- **Features Included:** FEAT-9000 (Procedural World Generation & Item-Agnostic Collection),
  FEAT-4100 (Generated-Region Screen Composition), FEAT-6100 (Aesthetic & Biome-Transition
  Compliance). All three new — not yet implemented.
- **Modules:** New `worldgen.py` (FEAT-9000); `tilemaps.py`, `tiles.py` (FEAT-4100, generalizing
  the existing per-zone rendering pattern); no code module for FEAT-6100 (a review-process
  capability).
- **Estimated Scope:** This Epic is the aesthetics/visual-story-narrative/procgen-world-map
  increment's entire new-construction scope — the largest body of genuinely new work in this
  catalog. Its own requirements baseline (RQ-01…04 delta, 2026-07-09) and architecture (3 ADRs,
  six GDS deltas) are both already authored and closed; nothing here is built yet.
- **Risks:** FEAT-9000 is High complexity/Medium-High risk — a wholly new generation algorithm
  with no shipped precedent, depending on a new verification technique (the reference-generator-
  oracle pattern, R305) working correctly. FEAT-4100/FEAT-6100 carry comparatively low risk,
  reusing existing rendering/review mechanisms.
- **Dependencies:** EP-1000 (FEAT-1100 triggers FEAT-9000's routine); EP-2000 (FEAT-4100/FEAT-6100
  extend EP-2000's existing rendering/presentation patterns); EP-3000 (FEAT-5300 persists this
  Epic's output).

## Epic summary table

| Epic | Title | Features | Primary Modules | Risk level |
|---|---|---|---|---|
| EP-1000 | Core Gameplay Loop | FEAT-1000, FEAT-2000, FEAT-3000, FEAT-1100 | `asm_game.py`, `tilemaps.py` | Low (shipped Features); Medium (FEAT-1100, new) |
| EP-2000 | World Content & Presentation | FEAT-4000, FEAT-6000 | `tilemaps.py`, `tiles.py` | Low (both prior non-compliances resolved) |
| EP-3000 | Persistence | FEAT-5000, FEAT-5100, FEAT-5300 | `asm_game.py` | Low (shipped Features); Medium (FEAT-5300, new) |
| EP-4000 | Engineering Quality & Verification | FEAT-7000 | all six + `test_rom.py` | Low (both tracked non-compliances resolved) |
| EP-5000 | World Generation & Visual Narrative | FEAT-9000, FEAT-4100, FEAT-6100 | new `worldgen.py`, `tilemaps.py`, `tiles.py` | **Medium-High** (FEAT-9000: new algorithm, no shipped precedent) |

Every Feature in [FP-03](03-feature-catalog.md) belongs to exactly one Epic above; no Feature
required splitting across Epics.
