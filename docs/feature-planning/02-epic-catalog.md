# FP-02 — Epic Catalog

> **Status: ✅ Authored (bootstrap as-built, 2026-07-07).** Owned by `05-feature-decomposition`.
> Groups [FP-03](03-feature-catalog.md)'s seven Features into four Epics. Every Feature belongs to
> exactly one Epic.

## EP-1000 — Core Gameplay Loop

- **ID:** EP-1000
- **Title:** Core Gameplay Loop
- **Purpose:** The moment-to-moment play experience — what state the game is in, how the player
  moves, and how they collect and win.
- **Features Included:** FEAT-1000 (Game State Machine & Menu Flow), FEAT-2000 (Player Movement &
  Zone Traversal), FEAT-3000 (Collectibles, Scoring & Victory).
- **Modules:** `asm_game.py` (all three Features are primarily this module), `tilemaps.py`
  (FEAT-2000's arrow signaling only).
- **Estimated Scope:** Already shipped in full — no new construction; this Epic's scope in future
  passes is limited to remediation (e.g. `BL-0006`'s test-suite rewrite touches this Epic's
  behavior, without changing it) or genuinely new mechanics if ever proposed.
- **Risks:** Automated Test-method verification for this entire Epic is currently compromised by
  `BL-0006` (Critical) — every Feature in it is verified today by direct source-code confirmation,
  not a passing automated suite.
- **Dependencies:** None on other Epics for its own existence; EP-2000 (World Content &
  Presentation) supplies the content this Epic operates on.

## EP-2000 — World Content & Presentation

- **ID:** EP-2000
- **Title:** World Content & Presentation
- **Purpose:** The game's explorable content and how it's visually presented to the player.
- **Features Included:** FEAT-4000 (Zone & Screen Composition), FEAT-6000 (Presentation & HUD).
- **Modules:** `tilemaps.py`, `tiles.py`, `asm_game.py` (HUD digit-writing only).
- **Estimated Scope:** Already shipped in full (9 zones, 14 screens). Future scope: any new zone/
  screen content (e.g. toward MSTR-001's C7 world-scale target) would extend this Epic.
- **Risks:** `NFR-1200` (score-bar write timing, not met — `BL-0003`/`BL-0008`) and the CGB
  palette/ROM-headroom watch items (`BL-0009`/`BL-0019`) both live in this Epic's Features.
- **Dependencies:** None — a foundational content Epic that EP-1000 operates on top of.

## EP-3000 — Persistence

- **ID:** EP-3000
- **Title:** Persistence
- **Purpose:** Saving and restoring player progress across power-off.
- **Features Included:** FEAT-5000 (Save/Load System, as-built), FEAT-5100 (Per-Zone ScoreItem
  Persistence, new — not yet implemented).
- **Modules:** `asm_game.py`.
- **Estimated Scope:** FEAT-5000 is fully shipped. **FEAT-5100 is the one piece of genuinely new,
  unscheduled-in-code work in this entire catalog** — a small-to-medium single-Feature addition
  extending an existing, well-understood mechanism (no new save format, no new hardware
  dependency).
- **Risks:** FEAT-5100's save-format-compatibility open question (does a pre-upgrade save default
  to "all collected" or "all uncollected" on first load?) must be resolved explicitly at
  `06-feature-specification` before implementation — see FP-03's Open Questions for FEAT-5100.
- **Dependencies:** EP-1000 (the SAVE state and the score/carrot data being persisted).

## EP-4000 — Engineering Quality & Verification

- **ID:** EP-4000
- **Title:** Engineering Quality & Verification
- **Purpose:** The cross-cutting, non-player-visible guarantees (ROM budget, module boundaries,
  build determinism, verification approach) every other Epic depends on holding true.
- **Features Included:** FEAT-7000 (Engine Quality & Build Infrastructure).
- **Modules:** All six modules, plus `test_rom.py` and the `run-bunnygarden` harness.
- **Estimated Scope:** Already shipped for 4 of 6 included NFRs; **2 known, tracked
  non-compliances** (`NFR-4000`'s future C7 supersession is not yet due; `NFR-7100`'s test-suite
  currency is due now, Critical, `BL-0006`/`BL-0008`).
- **Risks:** **Highest risk in the whole catalog** — `NFR-7100`'s non-compliance means every other
  Epic's automated verification claims are currently unsatisfiable, per RQ-03 finding #3.
- **Dependencies:** None — this Epic is the infrastructure floor; every other Epic implicitly
  depends on it.

## Epic summary table

| Epic | Title | Features | Primary Modules | Risk level |
|---|---|---|---|---|
| EP-1000 | Core Gameplay Loop | FEAT-1000, FEAT-2000, FEAT-3000 | `asm_game.py` | Low (per-Feature); verification-compromised project-wide |
| EP-2000 | World Content & Presentation | FEAT-4000, FEAT-6000 | `tilemaps.py`, `tiles.py` | Medium (NFR-1200 not met) |
| EP-3000 | Persistence | FEAT-5000, FEAT-5100 | `asm_game.py` | Medium (FEAT-5100 is new, unimplemented work) |
| EP-4000 | Engineering Quality & Verification | FEAT-7000 | all six + `test_rom.py` | **High** (NFR-7100 Critical non-compliance) |

Every Feature in [FP-03](03-feature-catalog.md) belongs to exactly one Epic above; no Feature
required splitting across Epics.
