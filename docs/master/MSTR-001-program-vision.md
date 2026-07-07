# MSTR-001 — Program Vision: Bunny Quest

- **Document ID:** MSTR-001 · **Version:** 2.0 · **Status:** ✅ Authored (corrected + expanded)
- **Date:** 2026-07-06 (v1.0 authored earlier same day; superseded same day — see §8) ·
  **Owned by:** `01-vision` skill
- **Derived from (v2.0):** direct inspection of the current shipped source
  (`tilemaps.py`, `asm_game.py`, `build_rom.py`, `music.py`, `tiles.py`) and a rebuilt ROM
  compared byte-for-byte against the checked-in `BunnyQuest.gbc` — **not** from `Claude.md`/
  `memory.md`, which v1.0 trusted and which are now known-stale (see §8). Plus the project
  owner's explicit scope-expansion instruction, 2026-07-06.
- **Design-facing restatement:** [`docs/architecture/00-vision.md`](../architecture/00-vision.md)
  (GDS-00)

## §1 What this project is

**Bunny Quest** (renamed from "Bunny Garden Adventure" — see §8) is a top-down exploration game
for **Game Boy Color**: a bunny explores a **3×3 grid of nine visually distinct zones** — Beach,
Forest, Mountain, Lake, Village, Cave, Desert, Plains, Castle — walking off any screen edge to
enter the neighboring zone in that direction. Stars and flowers scattered through each zone add
to a running score; each zone also hides one **carrot**, and collecting all nine carrots
(tracked in a 9-byte per-zone flag array) is the win condition. The game has a title/intro flow,
an in-game save menu, a 3×3 world-map screen showing which zones' carrots are collected, a
victory screen, an original melody, and a battery-backed save that persists across power-off and
auto-loads on boot.

Equally load-bearing: the game is **built entirely by a modular Python assembler pipeline** — no
RGBDS or external toolchain. Python modules define the tiles, screens, music, and SM83 game
logic; `build_rom.py` assembles them into a valid ROM; a headless-emulator test suite proves the
result. The project is therefore two products in one: a playable GBC game, and a **reference
demonstration that an agent-driven Python pipeline can produce and verify real console
software**. (Per the project owner's decision of 2026-07-06 — backlog BL-0004 — the modular
chain is the canonical build; legacy artifacts predating it are to be archived under `legacy/` —
see §8 for what "legacy" now includes.)

## §2 Who it is for

1. **Players:** an all-ages, casual audience playing short handheld sessions — gentle pacing, no
   fail states, non-violent, family-friendly content throughout (assumption A5).
2. **Developers and coding agents:** the repository is a worked example of a fully-tested,
   documentation-driven GBC project — every behavior traceable from vision to a named emulator
   test. *(This claim is currently only aspirational for the test layer — see §8's flagged gap.)*

## §3 Scope commitments (what must always be true)

| # | Commitment | Evidence at v2.0 |
|---|---|---|
| C1 | The ROM is **CGB-color, single-bank at present** (rsize 0x00), with a **valid header** (checksum, GBC flag 0x80). *Single-bank is the current shape, not a permanent ceiling* — see C7 and assumption A1. | rebuilt-and-diffed against `BunnyQuest.gbc`, header `set_header("BUNNYQUEST", cart=0x03, rsize=0x00, ramsize=0x02)` in `build_rom.py:163` |
| C2 | Cart type is **MBC1+RAM+BATTERY (0x03)**; progress **persists across power-off** and a valid save **auto-loads on boot** | `build_rom.py:163`; save-format bytes in `asm_game.py` (0xA004–0xA00E range) |
| C3 | The build is the **modular Python assembler chain** (`build_rom.py` + `gbc_lib`/`tiles`/`tilemaps`/`music`/`asm_game`) — reproducible from source with no external assembler | BL-0004 decision; a clean rebuild from source reproduces `BunnyQuest.gbc` byte-for-byte |
| C4 | Every release is **emulator-verified**: the ROM builds and a full, *currently-accurate* test suite passes | rule G5 — **not currently satisfiable as written; `test_rom.py` tests the pre-rewrite game (see §8)** |
| C5 | The **currently shipped Bunny Quest behavior** (9 zones, 9-carrot win condition, star/flower scoring, save/map/victory flows, auto-load) is the protected baseline going forward — changes to it are deliberate, pipeline-traced decisions, never side effects | direct code read of `tilemaps.py`/`asm_game.py`, 2026-07-06 |
| C6 | Content stays **family-friendly** and playable by a casual audience | §2 |
| **C7** *(new)* | **Long-term world-scale target: comparable to a Zelda- or Pokémon-class overworld** — substantially more than nine zones/biomes, explored at a larger scale, "pressing the limits beyond that" as far as the platform and this pipeline's tooling can be stretched. This is a direction, not a single fixed target size. | project owner's explicit instruction, 2026-07-06 |

## §4 Non-goals (at this vision's date)

Not commitments against forever — just explicitly *not* promised **yet**: real-hardware
certification (emulator verification is the gate — assumption A2) · localization beyond English
(A7) · a second, distinct game in this repository (A4 — Bunny Quest's own world growing much
larger is C7, not a second game) · multiplayer/link-cable features.

**Reversed by this revision:** "bank-switched ROM growth beyond one bank" is **no longer a
non-goal** — C7 explicitly anticipates it becoming necessary as the world grows past what a
single 32KB bank holds (currently ~9.6KB of headroom remains: 23148/32768 bytes used at v2.0).
MBC bank-switching strategy is now an expected future architecture question for
`03-architecture-design-synthesis`, not a boundary to protect.

## §5 Quality bar

"Done" for any change means: the ROM builds with a valid header; a full test suite that actually
matches the current shipped behavior is green; the behavior is traceable through the pipeline's
artifacts (requirement → feature spec → package → verification report); and the working
quick-references (`Claude.md`, `memory.md`) match the shipped bytes. **This bar is not currently
met for the test-suite and quick-reference clauses — see §8.**

## §6 Authority & document precedence

1. This document (MSTR-001) is the top of the tree for *purpose-level* statements; the GDS ladder
   (`docs/architecture/`) is authoritative for design as each level's merge gate closes.
2. Until `docs/master/MSTR-006` is authored, the governance rules **G1–G5** in
   [`.claude/skills/README.md`](../../.claude/skills/README.md) are binding.
3. `Claude.md` and `memory.md` are *intended* to remain the live developer quick-references, but
   are currently known to describe the pre-rewrite game (§8) — treat their current-state claims
   as unreliable until a remediation pass corrects them; their process notes (how the pipeline
   works, how to run things) are unaffected.
4. Conflicts between documents are findings for the owning skill — never resolved by silently
   editing the downstream copy. **`test_rom.py` currently conflicts with the shipped game** —
   flagged in §8, not silently patched here (out of this skill's write scope).

## §7 Change control

A change to §1–§4 is the most expensive kind of change in the tree: it is made only by the
`01-vision` skill, dated, with rationale recorded in §8's amendment log, and the downstream blast
radius enumerated (artifact → owning skill). The assumptions register carries the tripwires; when
a trigger fires, the register entry returns to the pipeline manager for re-triage rather than
being quietly edited.

## §8 Vision Amendment Log

| Date | Version | What changed | Why | Downstream blast radius |
|---|---|---|---|---|
| 2026-07-06 | 1.0 → 2.0 | **Corrected §1/§3/§4 wholesale**: the game is *Bunny Quest* (9 zones, 3×3 grid, 9-carrot win condition), not the 3-zone "Bunny Garden Adventure" v1.0 described. Added **C7** (Zelda/Pokémon-scale world target) and reversed the bank-switching non-goal. | v1.0 was authored (correctly, per its own bootstrap-mode rules) from `Claude.md`/`memory.md` — but those files describe the game **as it existed before commit `679b5cf` ("Rewrite as Bunny Quest")**, which had already landed on `main` before the pipeline scaffold's own PR merged. v1.0 never read the actual code. This revision does, and layers on the project owner's explicit forward-looking scale ambition given the same message. | See the full enumeration below — this is not a small fix. |

### Full downstream blast radius of this revision

Everything below was authored, or is otherwise exposed, on the basis of the now-superseded v1.0
description (3 zones, "gifts," "BunnyGarden" naming) or is independently found stale by the same
investigation:

| Artifact | Exposure | Owning skill | Recommended action |
|---|---|---|---|
| `docs/architecture/00-vision.md` (GDS-00) | Repeats "three-zone play," "v2.1," old naming | `01-vision` | **Fixed in this same run** — see below. |
| `docs/architecture/strategic-assumptions-register.md` | A1 (32KB) needs its framing updated for C7; A6 referenced the old bug set and "v2.1" | `01-vision` | **Fixed in this same run** — see below. |
| `docs/pipeline/backlog.md` — **BL-0001, BL-0002, BL-0003** | Filed against the *old* game's specific code (old map-heart BG addresses, old 2-sprite bunny, old score-write path) — the current `tilemaps.py`/`asm_game.py` implement the map screen and score bar completely differently now; these three entries need **re-verification against current code**, not automatic carry-forward. | `00-pipeline-manager` (triage) | Re-open at next triage; do not implement as literally filed. |
| `docs/pipeline/backlog.md` — **BL-0004** | Scoped to reconciling `BunnyGarden_build_rom.py`/`BunnyGarden_logic.json` against "the modular chain" — still correct, but the modular chain itself has moved on, and there is now **also** a stale `BunnyGarden.gbc` binary at the repo root (superseded by `BunnyQuest.gbc`, which matches current source) that needs the same archival treatment. | `00-pipeline-manager` (triage) | Widen BL-0004's scope to include `BunnyGarden.gbc`. |
| `docs/pipeline/backlog.md` — **BL-0005** | Still accurate as filed (hardcoded paths) — **and now compounded**: `test_rom.py`'s hardcoded `ROM_PATH` points at `BunnyGarden.gbc` (the *stale* ROM name), not `BunnyQuest.gbc`. Fixing the path portability without also fixing the filename would leave the suite testing the wrong binary. | `00-pipeline-manager` (triage) → `07-implementation-planning` | Amend BL-0005's scope to include the ROM filename, not just the path. |
| **`test_rom.py`** (new finding, not in the original five) | Asserts pre-rewrite WRAM semantics — `CUR_ZONE` bounded to 0–2, victory at a 3-bit `GIFTS` bitfield (`GS=5` when `GIFTS==7`) — against code that now uses `CUR_ZONE` 0–8 and a 9-byte `CARROT_FLAGS` array with victory at `CARROTS_COUNT==9`. **The G5 permanent gate cannot currently be satisfied**: the suite tests behavior the code no longer has. `test_results.txt`'s "88/88 passed" is a stale artifact, not evidence about the current tree. | `00-intake` → `07-implementation-planning` | **File as a new, high-severity backlog entry** — this blocks every future stage-08/09 run's G5 gate until remediated. Recommend prioritizing above BL-0001/0003/0005. |
| `Claude.md`, `memory.md`, `README.md` (repo-root working docs) | Describe the old game throughout (WRAM map, tile index map, zone names, "v2.1," known-good-behavior list) | not owned by any pipeline skill directly — the GDS ladder absorbs sections over time per each level's merge decision | **File as a new backlog entry** (doc-defect, high — these are the primary onboarding docs and are actively misleading right now). Likely fastest fix: a dedicated `07`/`08` documentation-refresh package once GDS-01/04/05 re-baseline against the real code. |
| `docs/pipeline/pipeline-journal.md` run #1's Position block | Recorded "Stage 01 ✅ complete" against the now-superseded v1.0 content | `00-pipeline-manager` | Journal this correction as its own run; do not silently overwrite run #1's history — append, as always. |

**Everything downstream of vision that hasn't been authored yet** (research tiers, the GDS-01…10
ladder, requirements, features, packages) is **unaffected in the sense that nothing needs
unwinding** — none of it existed yet. The correction lands before any of that work was done, which
is the cheapest possible time for a vision correction to land.
