# VR-9100 — Collectible Pickup Hitbox Fix

> Verification Report for
> [IP-9100](../packages/IP-9100-collectible-pickup-hitbox-fix.md), produced by
> `09-package-verification`. Read-only audit — no code, package, spec, or requirement was edited
> by this run.

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) ·
[Package](../packages/IP-9100-collectible-pickup-hitbox-fix.md)

## Package

- **ID / Title:** IP-9100 — Collectible Pickup Hitbox Fix (`BL-0053` remediation, no FS)
- **Commit verified:** tree head `5b3f072` (2026-07-12). Implementing commit `623c33a` ("fix
  (collision): IP-9100 -- correct collectible pickup hitbox"), authored 2026-07-11 — prior to
  this session.
- **Date:** 2026-07-12
- **Independence:** clean — not implemented in this session.

## Result

**VERIFIED** — 0 failed checks attributable to IP-9100. All 3 Definition of Done items and all 5
Verification Checklist items confirmed with direct evidence; full suite 231/231 pass (up from
217/217 at the package's own claimed implementation time) against a byte-identical rebuilt ROM.

## Definition of Done audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | `check_collisions` collects iff `0<=item_x-PLAYER_X<=7` AND `0<=item_y-PLAYER_Y<=15` — not the symmetric formula originally proposed | `asm_game.py:597-604`: X-axis is a single unsigned subtract (`LD_A_E(); SUB H` where `H=PLAYER_X`) then `CP_n(8); JR_NC('cc_skip')` — an unsigned-wraparound range test, not a symmetric abs-value comparison. Y-axis is the identical shape with `CP_n(16)`, `H=PLAYER_Y`. Confirmed by direct read this is the asymmetric point-in-box test the package's own correction note (§6) describes, not the originally-planned symmetric `|diff|<8`/`|diff|<16` formula | ✅ |
| 2 | `T8.x`/`T8.y`/`T8.z` demonstrably pass; every existing `T8` check still passes unchanged | `T8.x`/`T8.y`/`T8.z1`/`T8.z2` all `[PASS]` (`test_results.txt:91-94`) — `item_y=75` correctly rejected, `item_y=94` correctly collected, `dx=7`/`dy=15` collect while `dx=8`/`dy=16` don't. Full `T8` suite (all sub-checks) passes within the 231/231 total, including the corrected `T11.a1` fixture (region 0's index-0 star now approached at exact coordinates, not the old `(dx,dy)=(8,8)` near-miss the buggy tolerance permitted) | ✅ |
| 3 | ROM builds at 32768 bytes; full suite passes | Rebuild wrote 32768 bytes; `sha256sum` matches the checked-in ROM exactly (`6d67a17d…e18bd`). `python3 test_rom.py` → **231/231 passed, 0 failed** | ✅ |

## Verification Checklist audit

| # | Item | Evidence | Verdict |
|---|---|---|---|
| 1 | G5: ROM builds at exactly 32768 bytes with valid header | Confirmed above | ✅ |
| 2 | G5: full `test_rom.py` suite passes | **231/231 pass, 0 failed** this run (current suite size, up from 217/217 at implementation time) | ✅ |
| 3 | Direct code read: X-axis reads `CP_n(8)` after `item_x - PLAYER_X`; Y-axis reads `CP_n(16)` after `item_y - PLAYER_Y` | Confirmed under DoD #1 | ✅ |
| 4 | Direct PyBoy verification (not just static read): both of `BL-0053`'s reproduction points and all four exact boundary values confirmed correct | `T8.x`/`T8.y` are the direct runtime re-verification of the two reproduction points (`item_y=75` not collected, `item_y=94` collected); `T8.z1`/`T8.z2` are the direct runtime re-verification of all four boundary values (`dx∈{7,8}`, `dy∈{15,16}`) — this run re-ran the full suite fresh (not merely re-reading a prior pass), all four confirmed `[PASS]` | ✅ |
| 5 | `T8.x`/`T8.y`/`T8.z` present and passing, each using a synthetic item placed via WRAM at the exact boundary coordinates named in §8 | Confirmed — check names/values (`item_y=75`/`item_y=94`, `dx7=True dx8=False`, `dy15=True dy16=False`) match §8's own named coordinates exactly | ✅ |
| 6 | `FR-3100` Notes/RTM deltas applied exactly as §9 names; `FR-3100`'s own baselined text left unmodified | `FR-3100`'s Notes field (`01-functional-requirements.md:540+`) carries the 2026-07-11 delta note citing `IP-9100`/`BL-0053` and the corrected model, without rewriting the Description/Acceptance-Criteria text itself (confirmed still reads "within the proximity threshold... 10px," the pre-fix baselined text, exactly as the package's own §3/§9 promise); RTM's `FR-3100` row cites `T8.4, T8.x/T8.y/T8.z1/T8.z2` | ✅ |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Verdict |
|---|---|---|---|---|
| FR-3100 (collection-proximity detection — corrected model, text intentionally left stale per this package's own scope) | `check_collisions`'s asymmetric point-in-box test (`asm_game.py`) | `T8.4` (base), `T8.x/T8.y/T8.z1/T8.z2` (corrected model) | Cites `IP-9100` and the corrected test list — accurate, and the RTM/Notes honestly flag the FR-text divergence rather than silently absorbing it | ✅ |

## Test run

```
python3 build_rom.py BunnyQuest.gbc  → "Wrote 32768 bytes -> BunnyQuest.gbc"
sha256sum BunnyQuest.gbc <checked-in> → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd — identical
python3 test_rom.py                  → RESULTS: 231/231 passed   0 failed
```

No tunable/generated parameter is named in this package's DoD (a fixed sprite-geometry hitbox,
independent of `seed`/`scale`) — the non-default-parameter drive rule does not apply. The four
`T8.z1`/`T8.z2` boundary checks already exercise the exact off-by-one edges the fix's own
correctness claim rests on, which is the relevant rigor bar here.

## Scope audit

Every changed symbol traces to exactly the §6-declared files: `asm_game.py` (`check_collisions`'s
X/Y overlap test rewrite), `test_rom.py` (new `T8.x`/`T8.y`/`T8.z1`/`T8.z2`, `T11.a1`'s fixture
corrected in scope per §8's own named supersession fix). No excursion beyond the declared set
found. The package's own mid-implementation correction (symmetric formula abandoned in favor of
the asymmetric point-in-box test, after direct PyBoy verification proved the original plan wrong)
is fully documented in the package's own §6/§7 and confirmed to match what's actually shipped.

## Findings

No new findings. `IP-9100`'s core correctness claims (asymmetric point-in-box test, exact boundary
behavior at all four edges, `FR-3100`'s text-vs-implementation divergence honestly flagged rather
than silently resolved) are each independently confirmed against a fresh 231/231 suite run and
direct source reads — not taken on the Implementation Summary's word.
