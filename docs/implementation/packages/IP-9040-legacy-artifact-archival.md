# IP-9040 — Legacy Artifact Archival

> Owned by `07-implementation-planning` (definition) / `08-code-implementation` (execution).
> Status and authorization live in the [Master Build Plan](../00-master-build-plan.md).

## 1. Package ID

`IP-9040` — bug-remediation series; no FS. Source: **`BL-0004`** (Medium, `design-question`
resolved by user decision, run #1; scope widened run #2), under the **`BL-0008`** umbrella.

## 2. Objective

Move the three pre-rewrite artifacts out of the repo root into `legacy/`, so the root contains
exactly one build chain (the modular canonical one) and one shipped ROM (`BunnyQuest.gbc`).

## 3. Requirements Covered

No numbered FR/NFR — repository hygiene executing a recorded user decision ("modular chain is
canonical; archive the monolith", run #1; widened to the stale ROM binary, run #2).

## 4. Architecture Components

GDS-02/GDS-03 (the six-module canonical build chain the archival leaves as the sole chain).

## 5. Interfaces

None. The archived files are referenced by no current code: verified — `BunnyGarden_build_rom.py`
and `BunnyGarden_logic.json` are imported/read by nothing in the modular chain, and the stale
`BunnyGarden.gbc` is referenced only by pre-IP-9010 `test_rom.py` (whose rewrite retargets
`BunnyQuest.gbc`).

## 6. Files to Create/Modify

- **Create: `legacy/`** directory with a short `legacy/README.md` (one paragraph: what these
  files are, why archived, date, pointer to `BL-0004`).
- **Move (git mv):** `BunnyGarden_build_rom.py`, `BunnyGarden_logic.json`, `BunnyGarden.gbc`
  → `legacy/` (all three verified present at the repo root today).
- **Keep at root:** `BunnyQuest.gbc` (current shipped artifact, byte-identical to a fresh
  build — verified run #2).

## 7. Implementation Tasks

1. `git mv` the three files into `legacy/`; author `legacy/README.md`.
2. Grep the tree for references to the moved filenames; the only expected hits are historical
   (docs describing the archival itself, pipeline records). Update none that are historical;
   fix any live reference found (none expected per §5).

## 8. Tests to Add

None. The permanent gates (§11) prove the canonical chain is unaffected.

## 9. Documentation Updates

- `README.md` (or `legacy/README.md` alone if the root README's rewrite is pending IP-9030):
  one line noting where the legacy artifacts live.
- Master Build Plan status row.

## 10. Definition of Done

- Repo root contains no `BunnyGarden_*` files and no stale ROM; `legacy/` contains all three
  plus its README.
- `python3 build_rom.py` and `python3 test_rom.py` still work from the repo root.

## 11. Verification Checklist

- [ ] G5: ROM builds at exactly 32768 bytes with valid header.
- [ ] G5: full `test_rom.py` suite passes.
- [ ] Rebuilt ROM byte-identical to `BunnyQuest.gbc` (this package must not change the game).
- [ ] `ls` of repo root shows no `BunnyGarden*` entries; `ls legacy/` shows exactly the three
      artifacts + README.
- [ ] Grep confirms no live (non-historical) reference to the moved paths remains.

## 12. Dependencies

- **IP-9010** (`VERIFIED`) — solely because the G5 suite gate is unsatisfiable before it; the
  file moves themselves conflict with nothing.

## 13. Risks

- **Minimal.** Git history preserves the files; the move is content-free.
- ROM budget: none.

## 14. Rollback Considerations

`git mv` back. No code, save, or doc content depends on the files' location except the
archival note itself.
