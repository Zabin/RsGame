# MSTR-001 — Program Vision: Bunny Garden Adventure

- **Document ID:** MSTR-001 · **Version:** 1.0 · **Status:** ✅ Authored (bootstrap baseline)
- **Date:** 2026-07-06 · **Owned by:** `01-vision` skill
- **Derived from:** the shipped `BunnyGarden.gbc` v2.1, `Claude.md` (developer guide),
  `memory.md` (runtime notes), `test_rom.py` (88 verified behaviors) — bootstrap mode, no user
  interview; genuine ambiguities are recorded as assumptions in the
  [strategic assumptions register](../architecture/strategic-assumptions-register.md).
- **Design-facing restatement:** [`docs/architecture/00-vision.md`](../architecture/00-vision.md)
  (GDS-00)

## §1 What this project is

**Bunny Garden Adventure** is a complete, polished **Game Boy Color game**: a top-down
collect-a-thon in which a bunny explores three connected outdoor zones (garden, forest, meadow),
collects stars and flowers for score, finds the hidden gift in each zone, and wins by collecting
all three gifts — with a title/intro flow, an in-game save menu, a map screen, a victory screen,
music, and a battery-backed save that persists across power-off and auto-loads on boot.

Equally load-bearing: the game is **built entirely by a modular Python assembler pipeline** —
no RGBDS or external toolchain. Python modules define the tiles, screens, music, and SM83 game
logic; `build_rom.py` assembles them into a valid 32KB ROM; a headless-emulator test suite proves
the result. The project is therefore two products in one: a finished, playable GBC game, and a
**reference demonstration that an agent-driven Python pipeline can produce and verify real
console software**. (Per the project owner's decision of 2026-07-06 — backlog BL-0004 — the
modular chain is the canonical build; the legacy monolith is to be archived under `legacy/`.)

## §2 Who it is for

1. **Players:** an all-ages, casual audience playing short handheld sessions — gentle pacing, no
   fail states, non-violent, family-friendly content throughout (assumption A5).
2. **Developers and coding agents:** the repository is a worked example of a fully-tested,
   documentation-driven GBC project — every behavior traceable from vision to a named emulator
   test.

## §3 Scope commitments (what must always be true)

| # | Commitment | Evidence at baseline |
|---|---|---|
| C1 | The ROM is a **32KB single bank** (rsize 0x00) with a **valid header** (checksum, GBC flag 0x80) | `test_rom.py` T1.1–T1.7 |
| C2 | Cart type is **MBC1+RAM+BATTERY (0x03)**; progress **persists across power-off** and a valid save **auto-loads on boot** | T1.5, T10.x; save magic `BUNY` |
| C3 | The build is the **modular Python assembler chain** (`build_rom.py` + content/logic modules) — reproducible from source with no external assembler | BL-0004 decision; `build_rom.py` output "Wrote 32768 bytes" |
| C4 | Every release is **emulator-verified**: the ROM builds and the full `test_rom.py` suite passes (88/88 at baseline; the count only grows) | rule G5, `test_results.txt` |
| C5 | The shipped **v2.1 behavior set** (`Claude.md` §Known Good Behavior) is the protected baseline — changes to it are deliberate, pipeline-traced decisions, never side effects | `Claude.md`, `test_rom.py` T4–T10 |
| C6 | Content stays **family-friendly** and playable by a casual audience | §2 |

## §4 Non-goals (at this vision's date)

Not commitments against forever — just explicitly *not* promised now: real-hardware certification
(emulator verification is the gate — assumption A2) · bank-switched ROM growth beyond 32KB (A1) ·
localization beyond English (A7) · a second game in this repository (A4) · multiplayer/link-cable
features.

## §5 Quality bar

"Done" for any change means: the ROM builds at exactly 32768 bytes with a valid header; the full
test suite is green; the behavior is traceable through the pipeline's artifacts (requirement →
feature spec → package → verification report); and the working quick-references (`Claude.md`,
`memory.md`) match the shipped bytes.

## §6 Authority & document precedence

1. This document (MSTR-001) is the top of the tree for *purpose-level* statements; the GDS ladder
   (`docs/architecture/`) is authoritative for design as each level's merge gate closes.
2. Until `docs/master/MSTR-006` is authored, the governance rules **G1–G5** in
   [`.claude/skills/README.md`](../../.claude/skills/README.md) are binding.
3. `Claude.md` and `memory.md` remain the live developer quick-references; each GDS level's merge
   gate records which statements it absorbs from them.
4. Conflicts between documents are findings for the owning skill — never resolved by silently
   editing the downstream copy.

## §7 Change control

A change to §1–§4 is the most expensive kind of change in the tree: it is made only by the
`01-vision` skill, dated, with rationale recorded here and the downstream blast radius enumerated
(artifact → owning skill). The assumptions register carries the tripwires; when a trigger fires,
the register entry returns to the pipeline manager for re-triage rather than being quietly
edited.
