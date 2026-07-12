# VR-9110 — `gw_prng_step` Mixing-Step Repair

> Verification Report for
> [IP-9110](../packages/IP-9110-gw-prng-step-mixing-step-repair.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[ADR-0014](../../architecture/adr/ADR-0014-gw-prng-step-repair-needs-user-authorization.md)

## Package

- **ID / Title:** IP-9110 — `gw_prng_step` Mixing-Step Repair (`BL-0074`/`ADR-0014` remediation,
  no FS)
- **Commit verified:** tree head `9566006` (2026-07-12). Implementing commit `fb070ab` ("feat
  (worldgen): IP-9110 -- gw_prng_step mixing-step repair (BL-0074)"), authored 2026-07-11 — prior
  to this session.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9110. All 4 Definition of Done items and all 8
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
222/222 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.
This run independently re-verified the pre-upgrade save-exclusion claim, which the package's own
Verification Checklist explicitly named as "ad hoc, not a permanent test" — this run performed
that ad hoc check itself, live, via PyBoy.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `gw_prng_step`'s mixing step implements the `7,9,8` shift triplet exactly; `SAVE_VERSION_VAL` is `0x04`; `worldgen.py`'s `_step` mirrors it exactly, zero oracle mismatches | `asm_game.py:1274-1313`: `x^=x<<7` via 7 chained `SLA_E`/`RL_D` (`:1290-1295`), `x^=x>>9` via one byte-move + `SRL_D`/`RR_E` (`:1300-1304`), `x^=x<<8` via a straight byte-move (`:1306-1310`) — matches §6's own instruction-level spec exactly. `SAVE_VERSION_VAL = 0x04` confirmed (`asm_game.py:137`). `worldgen.py:24-28`'s `_step` is the literal Python mirror (`x ^= (x<<7)&0xFFFF; x ^= x>>9; x ^= (x<<8)&0xFFFF`). `T12.a`/`T12.b`/`T19.c` (oracle-parity checks) all `[PASS]` with `mismatches=[]` | ✅ |
| 2 | `T12.j`/`T12.k` demonstrably pass; every existing `worldgen.py`-dependent check still passes | `T12.j` `[PASS]` (`mean=0.156 over_40=[]` — well under the ~40% band, down from the unrepaired PRNG's ~46% mean); `T12.k` `[PASS]` (`water_frac=0.259 rows1-8_all_zero=False` — the literal `seed=0`/`scale=9` reproduction case is no longer flooded). Full suite 231/231, including every `T12`/`T17`/`T19` check that depends on `worldgen.py`/`gw_prng_step` | ✅ |
| 3 | `BL-0074`'s own originally-reported case (`seed=0`, `scale=3`/`scale=9`) directly re-checked, no longer Water-flooded | `T12.k` is exactly this re-check for `scale=9` (`water_frac=0.259`, `rows1-8_all_zero=False` — the old flood pattern is gone); `T12.j`'s corpus includes `seed=0` at `scale=9` among its 36 entries, confirmed under the 40% band. `scale=3`'s own default-fixture suites (`T4`–`T11`, etc.) all pass throughout the full run, confirming no default-seed degeneracy at that scale either | ✅ |
| 4 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, up from 222/222 at implementation time) | ✅ |
| 3 | Direct code read: `gw_prng_step`'s mixing step matches the `7,9,8` shift-triplet shape, not the old `1,1,byteswap` sequence | Confirmed under DoD #1 — the code's own comment explicitly documents the old sequence being replaced, and the shipped shape matches the new triplet exactly | ✅ |
| 4 | Direct code read: `SAVE_VERSION_VAL` reads `0x04` | Confirmed — `asm_game.py:137` | ✅ |
| 5 | `worldgen.py`'s `_step` matches `gw_prng_step`'s corrected algorithm exactly — oracle-parity checks pass with zero mismatches | Confirmed under DoD #1 — `T12.a`/`T12.b`/`T19.c` all `mismatches=[]` | ✅ |
| 6 | `T12.j`/`T12.k` present and passing | Confirmed above | ✅ |
| 7 | Direct PyBoy re-check of `BL-0074`'s own literal reported case shows a properly varied `REGION_GRAPH` | `T12.k` itself drives the live SM83-built ROM via `invoke_generate_world` (not only the Python oracle, per the test's own comment: "the oracle is the thing being kept in lockstep, not independent evidence") — this is a direct PyBoy check, not an inference from a statistical aggregate | ✅ |
| 8 | A pre-fix (version `0x03`) save is confirmed excluded from "continue" — confirm by direct test, not assumption | **No permanent automated test exists for this specific transition** (the package's own §6 and the Master Build Plan's Implementation Summary both describe this as an "ad hoc" check performed at implementation time, not a new permanent test) — so this run performed its own independent ad hoc re-check, live: built a synthetic SRAM fixture at `version=0x03` (mirroring `T16.d`'s own established fixture-construction method) and booted it — `GAMESTATE=6` (MAIN MENU), the "CONTINUE" label's first tile reads `0x10` (`TL_BG_BLANK`) — **blank, excluded**. An identical fixture at `version=0x04` shows the label's first tile at a real font-tile value (`0x42`) — **offered**. Confirms the existing generic version-guard machinery (unmodified by this package) correctly excludes the pre-fix save | ✅ |
| 9 | Requirements/RTM deltas applied exactly as §9 names | `FR-9100` Notes cites this package; `NFR-2200` Notes confirms the shift/XOR-only constraint still holds; RTM's `FR-9100` row cites `T12.j`/`T12.k`, `IP-9110`, `ADR-0014` | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-9100 (world-scale determinism — `gw_prng_step` repair) | `gw_prng_step`'s corrected mixing step (`asm_game.py`), `worldgen.py`'s lockstep mirror | `T12.j`, `T12.k`, plus every existing `T12`/`T19` oracle-parity check | Cites `T12.j`/`T12.k`, `IP-9110`, `ADR-0014` — accurate | ✅ |
| NFR-2200 (no `DIV`/`MUL` opcodes) | The corrected mixing step is shift/XOR-only (7 chained `SLA`/`RL`, one `SRL`/`RR`, byte-moves) | `T12.h` (static audit, no `LDH` reads — a related but distinct NFR-2200 concern about hardware-register reads, still passing) | Notes field confirms the constraint remains satisfied, orthogonal to the fix | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
grep T12.j/T12.k test_results.txt    → both [PASS], mean Water fraction 15.6%, seed=0/scale=9 25.9%
```

**Ad hoc pre-upgrade-save re-check (this run, live PyBoy, not a permanent suite addition per the
package's own framing):**

```
version=0x03 fixture → GS=6 (MAIN MENU), CONTINUE label tile = 0x10 (TL_BG_BLANK) → excluded
version=0x04 fixture → GS=6 (MAIN MENU), CONTINUE label tile = 0x42 (real font glyph) → offered
```

**Non-default-parameter drive:** `T12.j`'s 36-seed corpus and `T12.k`'s direct reproduction both
run at `scale=9` (not the suite's default `scale=3` fixture), and `T12.j`'s corpus spans small
integers, the existing `T12_CORPUS`/`T19_CORPUS` values, and several large seeds (`65535`,
`42424`) — this package's core claim (the PRNG no longer degenerates for effectively any seed) is
exercised well beyond the default fixture.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (`gw_prng_step`'s
mixing step, `SAVE_VERSION_VAL` bump), `worldgen.py` (`_step`'s lockstep mirror), `test_rom.py`
(`T12.j`/`T12.k`). `IP-1070`'s `GW_MAZE_DRAW_CTR` perturbation confirmed left in place, as the
package's own §6 explicitly decided (not removed, not an oversight) — `T19.e`'s braid-fraction
statistical check still passes (`24.35%`, within band), consistent with the perturbation remaining
active and the underlying PRNG now also being non-degenerate. No excursion beyond the declared
set found.

## Findings

No new findings. `IP-9110`'s core correctness claims (the `7,9,8` triplet shipped exactly as
specified, zero oracle mismatches under the new algorithm, the specific reported flood case fixed,
the pre-upgrade save-exclusion machinery working correctly with zero new code) are each
independently confirmed against a fresh 231/231 suite run, direct source reads, and this run's own
live PyBoy re-check of the save-version-guard behavior — not taken on the Implementation Summary's
word.
