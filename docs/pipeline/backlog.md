# Pipeline Backlog

> **Findings & intake register for the documentation-driven-development pipeline.** Two writers:
> **`00-pipeline-manager`** (harvests every invoked skill's findings/recommendations/Outstanding
> Issues after each run, triages every open entry at the start of the next run, and flips
> statuses) and **`00-intake`** (appends `NEW` entries for user-submitted features, bugs, and
> observations). Stage skills never write here — their findings reach this file via the manager's
> harvest step. Rows are never deleted: resolved entries flip to `DONE`, rejected ones to
> `REJECTED` with the reason kept.

[↑ Docs index](../INDEX.md) · [Pipeline journal](pipeline-journal.md) ·
[Pipeline README](../../.claude/skills/README.md)

## Lifecycle

```
NEW ──triage──▶ SCHEDULED (rides a named step)  ──that step runs──▶ DONE
        ├─────▶ DEFERRED  (named revisit trigger) ──trigger fires──▶ NEW (re-triage)
        ├─────▶ NEEDS-USER (named decision)       ──user decides───▶ SCHEDULED / REJECTED
        └─────▶ REJECTED  (reason recorded)
IN PIPELINE = the entry's work is the current/next step's explicit target
```

Every open entry carries a live disposition — `SCHEDULED` names the step it rides with,
`DEFERRED` names its revisit trigger, `NEEDS-USER` names the exact decision required. A
Critical/High entry may not be `DEFERRED` without the user's explicit agreement.

## Entries

| ID | Filed | Type | Source | Summary | Sev/Pri | Entry stage | Disposition | Status |
|---|---|---|---|---|---|---|---|---|
| BL-0001 | 2026-07-06 | bug | scaffold init: `memory.md` §"Active Bug" | Map-screen hearts written to wrong BG map addresses — correct values are 0x98CC/0x990C/0x994C (rows 6/8/10, col 12); current code is off by one row each. Fix location and exact patch already recorded in `memory.md`. Covered by the G3 bootstrap carve-out. | Medium | 07 | SCHEDULED (run #1 triage): rides the bootstrap's first `07-implementation-planning` remediation pass, after the as-built baseline reaches stage 07 | SCHEDULED |
| BL-0002 | 2026-07-06 | finding | scaffold init: `Claude.md` §"Remaining Known Issues" | Bunny renders as two separate 8x8 OAM entries (head+body) and reads small; evaluate 8x16 OBJ mode or a larger composed sprite. Likely needs design synthesis (sprite strategy is GDS-08 territory) before a package — route 03→06→07 if pursued. | Low | 03 | SCHEDULED (run #1 triage): evaluated during `03-architecture-design-synthesis`'s GDS-08 (Presentation Architecture) authoring; if a sprite-strategy change is warranted it routes 06→07 afterward | SCHEDULED |
| BL-0003 | 2026-07-06 | bug | scaffold init: `Claude.md` §"Remaining Known Issues" | Score display writes VRAM while the LCD is on (works in practice on emulator, but should be VBlank-gated per the PPU access rules R102 will document). Covered by the G3 bootstrap carve-out. | Medium | 07 | SCHEDULED (run #1 triage): rides the bootstrap's first `07-implementation-planning` remediation pass (R102 grounds the fix once authored) | SCHEDULED |
| BL-0004 | 2026-07-06 | design-question | scaffold init: repo-root file survey | Duplicate/legacy build artifacts need reconciling: `BunnyGarden_build_rom.py` (monolithic, 45KB) and `BunnyGarden_logic.json` coexist with the modular canonical chain (`build_rom.py` + `gbc_lib/tiles/tilemaps/music/asm_game`). Decide which is canonical and what happens to the others (archive under `legacy/`, delete, or document). Needs a user decision at triage. | Medium | 03 | **User decided (run #1, 2026-07-06): modular chain is canonical; archive `BunnyGarden_build_rom.py` + `BunnyGarden_logic.json` to `legacy/` with a README note.** Decision recorded at GDS-03's authoring; the file move rides the first `07-implementation-planning` hygiene/remediation pass (IP-9xx0 series) | SCHEDULED |
| BL-0005 | 2026-07-06 | bug | scaffold init: `build_rom.py`/`test_rom.py` read-through | Hardcoded absolute paths break portable runs: `build_rom.py` defaults output to `/mnt/user-data/outputs/BunnyGarden.gbc`; `test_rom.py` hardcodes `ROM_PATH`, the PyBoy `.ram` path, `SHOT_DIR=/home/claude/bunnygarden/test_shots`, and the `test_results.txt` output path. Make them repo-relative with env/argv overrides. Highest-leverage first remediation — the G5 permanent gates depend on these scripts running anywhere. Covered by the G3 bootstrap carve-out. | Medium | 07 | SCHEDULED (run #1 triage): rides the bootstrap's first `07-implementation-planning` remediation pass, **sequenced first** — the G5 permanent gates depend on these scripts running anywhere | SCHEDULED |
