# IP-9030 — Root Documentation Refresh

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9030` — bug-remediation series; no FS. Source: **`BL-0007`** (High), under the **`BL-0008`**
umbrella.

## 2. Objective

Make the three root onboarding docs (`Claude.md`, `memory.md`, `README.md`) describe the game
that actually ships — **Bunny Quest**, 9 zones, 9-carrot victory — replacing their pre-rewrite
"Bunny Garden Adventure" content, which is actively misleading (wrong WRAM map, wrong tile
index map, wrong zone list, stale "v2.1"/"88/88" claims).

## 3. Requirements Covered

No numbered FR/NFR — this is documentation-defect remediation. Honors MSTR-001 §6's
doc-currency commitment and executes the merge decisions the GDS ladder already recorded
(GDS-01/02/03/04/07/08 each name the section of `Claude.md`/`memory.md` they supersede).

## 4. Architecture Components

The whole GDS ladder is the *source*; this package makes the root docs *pointers into it* per
the recorded merge decisions (GDS-07's is the most consequential: byte-level WRAM/SRAM/tile
tables).

## 5. Interfaces

None (documentation only; no production module, no ROM change).

## 6. Files to Create/Modify

- **Modify: `Claude.md`** — replace stale sections (system overview, architecture overview,
  data layout/WRAM/SRAM tables, Known Good Behavior list, "Remaining Known Issues", "v2.1"
  status line) with current facts + pointers to the owning GDS/RQ docs.
- **Modify: `memory.md`** — replace stale entity tables, tile-index/palette quick-reference,
  and the "Active Bug" section (BL-0001: verified not-reproducing; BL-0003: fixed by IP-9020).
- **Modify: `README.md`** — game name, zone/victory description, build/test quick-start
  (post-IP-9010 portable commands: `python3 build_rom.py` → `BunnyQuest.gbc`,
  `python3 test_rom.py` from the repo root).

## 7. Implementation Tasks

1. For each superseded section, follow the GDS ladder's recorded merge decision: keep a short
   accurate summary in the root doc, link the authoritative GDS/RQ document for detail. Do not
   duplicate byte tables back into root docs (GDS-07 owns them — the duplication is what went
   stale last time).
2. Update `Claude.md`'s known-issues section to the *current* truth: BL-0003 fixed (IP-9020),
   BL-0001 not-reproducing, test suite trustworthy again (IP-9010), remaining open items live
   in `docs/pipeline/backlog.md`.
3. Update `README.md`'s quick-start against the actually-working commands (verify by running
   them).
4. Sweep all three docs for the stale terms: "Bunny Garden Adventure" (as the game's name),
   "gifts", 3-zone references, `BunnyGarden.gbc` (except when naming the archived legacy
   artifact), "88/88".

## 8. Tests to Add

None (no testable production behavior). Verification is by checklist grep + link check.

## 9. Documentation Updates

The package *is* documentation. Additionally: `ROADMAP.md`'s RT-CLAUDE/RT-MEMORY/RT-README rows
get a "refreshed <date>" note; Master Build Plan status row.

## 10. Definition of Done

- No statement in any of the three docs contradicts the GDS ladder, the requirements baseline,
  or the shipped code.
- Every replaced section links its authoritative owner document.
- The stale-term sweep (§7.4) returns clean.
- `README.md`'s quick-start commands were actually executed and work.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header (unchanged by this package).
- [ ] G5: full `test_rom.py` suite passes (unchanged by this package).
- [ ] Grep of the three docs for `gifts|88/88|BunnyGarden` (excluding legacy-artifact
      references and historical notes explicitly marked as such) returns nothing.
- [ ] Rebuilt ROM byte-identical (docs-only change).
- [ ] Spot-check: `Claude.md`'s WRAM pointer resolves to GDS-07 and GDS-07's table matches
      `asm_game.py`'s constants.

## 12. Dependencies

- **IP-9010** (`VERIFIED`) — the refreshed docs must describe the trustworthy suite and cite
  real test output.
- **IP-9020** (`VERIFIED`) — the known-issues section must state the score-bar fix as shipped
  fact, not prediction.

## 13. Risks

- **Drift risk is the package's own subject**: the mitigation is structural (pointers to owning
  docs instead of duplicated tables), per the GDS merge decisions.
- ROM budget: none.

## 14. Rollback Considerations

Git revert of three doc files; no runtime impact. Reverting would re-introduce the misleading
content, so a revert should only accompany a revert of the facts it describes.
