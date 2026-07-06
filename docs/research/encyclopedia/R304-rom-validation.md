# R304 — ROM Validation (Build-Time Tooling Perspective)

- **Document ID:** R304 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R109 (the hardware-required header/checksum facts this topic's tests verify)
- **Referenced By:** R305 (these checks are T1's suite within the larger test-design picture)
- **Produces:** grounds `test_rom.py`'s T1 suite and what a rewritten suite must keep verifying
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R109, R305

## Purpose

Distinct from R109 (which grounds *why* the hardware requires certain header bytes), this topic
grounds *how this project's own tooling verifies a build produced a valid ROM* — the specific,
reusable checks that must survive any future `test_rom.py` rewrite (BL-0006/BL-0008), since they
are the one part of the suite that is **not** affected by the game's zone-count/win-condition
rewrite.

## Scope

The concrete, code-verifiable facts a build-validation check can assert without any game-logic
knowledge: file size, entry point shape, header field values, checksum validity.

## Concepts

A ROM's validity as a *bootable cartridge image* is fully determined by facts local to the header
region (R109) plus the file's raw size matching the declared ROM-size code — none of this depends
on what the game's WRAM layout or win condition actually is. This makes header/size validation the
most **stable** class of test in the whole suite: it is true for "Bunny Garden Adventure" and
"Bunny Quest" alike, and will remain true for whatever the game becomes next under MSTR-001 C7's
growth.

### Sources
*(No external citation needed beyond R109's, which this topic explicitly builds on — see R109's
Sources for the Pan Docs/RGBDS citations grounding the underlying header facts.)*

## Operational Context

`test_rom.py`'s **T1 suite** (per `Claude.md`/`memory.md` and confirmed by the check names in
`test_results.txt`) already implements exactly this class of check, and — unlike the T4/T7/T8/T9
suites — **is not among the stale, pre-rewrite-semantics checks BL-0006 identifies**: T1.1 (ROM
size = 32768), T1.2 (entry point = `NOP; JP`), T1.3 (`JP` target ≥ `0x0150`), T1.4 (GBC flag =
`0x80`), T1.5 (cart type = `0x03`), T1.6 (RAM size = `0x02`), T1.7 (header checksum valid). Every
one of these facts is grounded in R109 and is **unaffected by the Bunny Quest rewrite** — the
header format didn't change, only the game logic did. This is a directly useful, good-news finding
for whoever executes BL-0006/BL-0008's remediation: **T1 does not need to be rewritten**, only the
T4/T7/T8/T9-family suites that assert game-state semantics (R305 covers those).

`gbc_lib.py`'s `resolve()`/`set_header()` (R109, R302) are the code these checks validate; a
passing T1 suite is direct evidence the build pipeline's header-writing path is intact.

## Implementation Guidance

- **Preserve T1's checks verbatim in any `test_rom.py` rewrite** — they test facts that don't
  depend on game semantics and would need to be re-derived from scratch (at real risk of missing
  a check) if discarded along with the genuinely-stale suites.
- **A future ROM-size or cart-type change** (e.g. moving to a banked MBC per R106/C7) must update
  T1.1/T1.5/T1.6's expected values in lockstep with the `build_rom.py` `set_header()` call that
  changes — these are exactly the kind of test that silently goes stale itself if a header change
  ships without a matching test update (the same class of drift BL-0006 found at the *game-logic*
  level, now flagged proactively at the *header* level before it can recur there too).
- **Add a same-class check whenever a new header-adjacent invariant is introduced** (e.g. a future
  RAM-banking flag, a new global-checksum expectation) — following the existing T1.x numbering
  convention rather than inventing a new suite for a single fact.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R109 (the hardware facts these checks verify) · R305 (where this topic's checks fit into the
overall test-suite design, alongside the game-logic assertion classes that do need rewriting).
