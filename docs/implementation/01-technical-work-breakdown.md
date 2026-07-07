# Technical Work Breakdown

> **Status: ✅ Authored (first planning pass, 2026-07-07).** Owned by
> `07-implementation-planning`. Records how approved work is cut into Implementation Packages —
> the rationale for every split/no-split decision is the artifact. Package status lives in the
> [Master Build Plan](00-master-build-plan.md), not here.

[↑ Docs index](../INDEX.md) · [Master Build Plan](00-master-build-plan.md) ·
[Packages](packages/INDEX.md)

## Scope of this pass

Two tranches, planned together in the pipeline's first stage-07 run:

1. **Remediation tranche** — the `BL-0008` umbrella ("docs/tests describe the wrong game"),
   covering `BL-0001`, `BL-0003`, `BL-0004`, `BL-0005`, `BL-0006`, `BL-0007`.
2. **Feature tranche** — [`FS-101` Per-Zone ScoreItem Persistence](../features/FS-101-per-zone-scoreitem-persistence.md)
   (`FEAT-5100`, `FR-5220`), with `BL-0023` (ScoreItem respawn/score-farming bug) riding as its
   designed side-effect fix.

## Re-verification results (planning-stage evidence, direct code reads 2026-07-07)

`BL-0008`'s scope required re-verifying `BL-0001`/`BL-0003`'s pre-rewrite claims against the
current tree before packaging. Results:

- **`BL-0001` (map hearts at wrong BG addresses) — does NOT reproduce; no package.** The
  current `update_map_hearts` (`asm_game.py:644`) writes 9 hearts at
  `0x9800 + row*32 + col` for rows 6/9/12 × cols 6/11/16 — exactly where `map_screen()`
  (`tilemaps.py:327`) places its heart tiles (`cx+3 = 6/11/16`, `cy+1 = 6/9/12`, from
  `cell_x0=3, cell_y0=5, cw=5, ch=3`). The routine runs only via `do_screen_redraw`'s `dsr_m`
  path (`asm_game.py:570`), i.e. with the LCD off, so the writes are also timing-safe. The bug
  as filed described the pre-rewrite 3-heart mechanism; the rewrite replaced and fixed it.
  The rewritten test suite (IP-9010) adds a heart-placement check so this stays verified.
- **`BL-0003` (score display writes VRAM while LCD on) — DOES reproduce; packaged as IP-9020.**
  `update_status_disp` (`asm_game.py:505`) writes BG-map bytes at `0x9802` and
  `0x9808`–`0x980A` with no STAT/VBlank guard. It is called from `st_playing`
  (`asm_game.py:203`) *after* `handle_play_input`/`check_collisions`/`check_zone_transition`/
  `check_complete`, so the writes can land outside the VBlank window (mode 3 → write dropped).
  This is exactly `NFR-1200`'s recorded NOT MET status.

## Work units and package cut

### Remediation tranche (`BL-0008`)

| Work unit | Package | Owner |
|---|---|---|
| Rewrite `test_rom.py` assertions for Bunny Quest semantics (`BL-0006`) + repo-relative paths and correct ROM filename (`BL-0005`) | [IP-9010](packages/IP-9010-test-suite-rewrite.md) | `08-code-implementation` |
| Fix `update_status_disp`'s unguarded VRAM writes (`BL-0003`) | [IP-9020](packages/IP-9020-score-bar-vblank-fix.md) | `08-code-implementation` |
| Refresh `Claude.md`/`memory.md`/`README.md` (`BL-0007`) | [IP-9030](packages/IP-9030-root-doc-refresh.md) | `08-code-implementation` |
| Archive legacy artifacts to `legacy/` (`BL-0004`) | [IP-9040](packages/IP-9040-legacy-artifact-archival.md) | `08-code-implementation` |
| Re-verify `BL-0001` | *(no package — does not reproduce; see above)* | — |

**Split rationale:**

- **`BL-0005` + `BL-0006` fused into one package (IP-9010).** Both live entirely inside
  `test_rom.py`; the path/filename fix alone is worthless (the suite still asserts the wrong
  game), and the assertion rewrite can't even run without the path fix. Two packages editing the
  same file serially would add coordination cost and zero parallelism. R305 explicitly recommends
  a suite-level rewrite over a line-by-line patch, which makes the fused package one coherent
  Definition of Done: *a trustworthy suite against the shipped game*.
- **`BL-0003` split out (IP-9020)** because it changes **game code** (ROM bytes change) while
  IP-9010 is test-harness-only (ROM unchanged). Keeping ROM-affecting and ROM-neutral changes in
  separate packages keeps each package's verification story clean (IP-9010 must produce a
  byte-identical ROM; IP-9020 must not).
- **`BL-0007` split out (IP-9030)** because it is documentation-only and should land *after*
  IP-9010/IP-9020 so the refreshed docs describe the post-remediation state (trustworthy suite,
  fixed score-bar timing) instead of needing a second refresh a week later.
- **`BL-0004` split out (IP-9040)** because it is pure file hygiene (git moves, no content
  edits) with an already-recorded user decision; folding it into any other package would blur
  that package's Definition of Done.

### Feature tranche (`FS-101`)

| Work unit | Package | Owner |
|---|---|---|
| Implement per-zone ScoreItem persistence end-to-end (WRAM array, collection hook, zone-entry suppression, save/load + version guard, resets, T11 tests) | [IP-1010](packages/IP-1010-per-zone-scoreitem-persistence.md) | `08-code-implementation` |

**No-split rationale:** FS-101's five behaviors (collect-hook, zone-entry check, save, load,
reset paths) are one atomic contract — shipping any subset leaves the save format or the
in-session behavior half-migrated (e.g. persisting bits that zone entry then ignores). All
changes land in one module (`asm_game.py`) plus the new T11 suite. One package, one stage-08
run, one Definition of Done.

**Deferred detail resolved here (FS-101 Open Question 3):** `SCOREITEM_FLAGS` is assigned
**`0xC060`–`0xC068`** (9 bytes). Rationale: GDS-07's WRAM map shows `C051`–`C2FF` unallocated
(the 2-byte gap at `C01E`–`C01F` FS-101 noticed is insufficient for 9 bytes); `0xC060` is
8-aligned, leaves `C051`–`C05F` spare next to `COLL_COUNT` for future collectible-state growth,
and sits inside the boot-time `C000`–`C2FF` clear (`asm_game.py:86-88`), which delivers FS-101's
"implicitly all-zero at first boot" for free. The SRAM layout is exactly as FS-101 specifies:
save-format version guard at `0xA012` (value `0x01`), `SCOREITEM_FLAGS` mirror at
`0xA013`–`0xA01B`.

## Sequencing summary

**IP-9010 is the universal unblocker**: the G5 permanent gate ("full `test_rom.py` suite
passes") is unsatisfiable for *every* package until the suite itself is rewritten, so every
other package depends on IP-9010 reaching `VERIFIED`. After that: IP-9020, IP-9040, and IP-1010
are parallel; IP-9030 waits for IP-9020 (it documents the fixed behavior). Critical path (per
FP-04, Release 1 = `FEAT-5100`): **IP-9010 → IP-1010**.

## Backlog riders honored in this pass

- **`BL-0017`** (one-carrot-per-zone invariant): no package touches `ZONE_COLLECTS`, but
  IP-9010's rewritten suite adds a data-level check asserting exactly one type-2 entry per
  zone list — turning the invariant from convention into a tested property.
- **`BL-0019`** (ROM-headroom watch): IP-9020 and IP-1010 (the two ROM-growing packages) each
  carry an NFR-4000 headroom re-affirmation checklist item.
- **`BL-0023`** (ScoreItem respawn/score farming): fixed by IP-1010 as FS-101's designed side
  effect; IP-1010's T11 tests cover the same-session respawn case explicitly.
