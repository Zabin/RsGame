# Integration Review — IP-9110/9120/9130/9140 (Standalone Remediation Set)

> Produced by `10-integration-review`. Read-only with respect to code, packages, specs, and
> requirements — findings are reported and routed, never fixed in this pass.

[↑ Reviews index](INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md)

## Scope

An explicitly-named package set (not a formal tranche) chosen for a real interaction surface
between four otherwise-standalone remediation packages, all `VERIFIED` on the Master Build Plan:

| Package | Title | VR |
|---|---|---|
| IP-9110 | `gw_prng_step` mixing-step repair (BL-0074) | [VR-9110](../implementation/verification/VR-9110-gw-prng-step-mixing-step-repair.md) |
| IP-9120 | RIGHT zone-transition threshold fix (BL-0076) | [VR-9120](../implementation/verification/VR-9120-right-zone-transition-threshold-fix.md) |
| IP-9130 | Zone-transition intent gate (BL-0078) | [VR-9130](../implementation/verification/VR-9130-zone-transition-intent-gate.md) |
| IP-9140 | Right-arrow off-screen position fix (BL-0084) | [VR-9140](../implementation/verification/VR-9140-right-arrow-offscreen-position-fix.md) |

**Why reviewed as a set:** `IP-9120` and `IP-9130` both directly edit `check_zone_transition`'s
own RIGHT branch (a threshold constant and a new precondition, landed in that order); `IP-9110`
changes the raw PRNG stream every world-generation draw ultimately derives from, including the
maze pass this set's own navigation fixes operate against; `IP-9140` fixes the visual signal
(the right arrow) a player uses to interpret the exact navigation behavior `IP-9120`/`IP-9130`
correct. Each package's own individual VR confirmed it in isolation; this review confirms all
four operating together.

**Commit reviewed:** `2a8395a` (tree head at review time). All four packages confirmed `VERIFIED`
on the Master Build Plan before this review began.

## Full gates (reviewed commit)

```
python3 build_rom.py BunnyQuest.gbc   → "Total used: 0x57C8 (22472 bytes of 32768)"
                                          "Wrote 32768 bytes → BunnyQuest.gbc"
sha256sum BunnyQuest.gbc              → 6d67a17d552c1342e945f321562b6bc3ccfa1e966d9ff0fb3b0f326e79de18bd
                                          (identical to the checked-in ROM)
python3 test_rom.py                   → RESULTS: 231/231 passed   0 failed
```

## Dimension 1 — Interface consistency

**Clean.** Confirmed `check_zone_transition`'s RIGHT branch (`asm_game.py:675-693`) carries both
`IP-9120`'s corrected threshold (`CP_n(152)`) **and** `IP-9130`'s `JOY_CUR` gate
(`BIT_b_A(J_RIGHT)`, tested first) in the same, layered, mutually-consistent shape — confirmed by
direct read, both changes coexist exactly as each package's own commented rationale describes
(the gate precedes the position test; the position test uses the corrected operand). No
regression of one package's fix by the other's.

## Dimension 2 — Invariant sweep

**Clean.**

- **ROM budget:** exactly 32768 bytes, byte-identical rebuild.
- **WRAM:** none of the four packages introduces a new WRAM address — `IP-9110` only bumps
  `SAVE_VERSION_VAL` (`0x03`→`0x04`, confirmed the sole change of that kind); `IP-9120`/`IP-9130`
  are pure control-flow edits within `check_zone_transition`; `IP-9140` is a single constant-value
  change (`ARROW_ADDR_R`). No collision surface to check beyond what each package's own VR already
  confirmed.
- **`gw_prng_step` stream, the tranche's real cross-cutting invariant:** confirmed live that a
  world generated entirely under `IP-9110`'s repaired PRNG (`seed=1`/`scale=9`) is non-degenerate
  (Water fraction 25.9%, well under the ~40% regression band `T12.j` checks) — the exact world
  used to exercise `IP-9120`/`9130`/`9140` together below, so their own live evidence is itself
  additional confirmation `IP-9110`'s repair didn't destabilize anything the other three depend on.

## Dimension 3 — Behavioral coherence

**Clean.** Drove all four packages together in one continuous live session, at a non-default
scale (`seed=1`, `scale=9` — not the suite's own default `scale=3`, and not a value any single
package's own VR combined with real navigation this way):

```
New game (world generated under IP-9110's repaired PRNG) -> CUR_ZONE=0
Real, sustained RIGHT-held input -> stays at CUR_ZONE=0, PLAYER_X settles at exactly 152
  (IP-9090's clamp + IP-9120's matching threshold; region 0's grid-right neighbor exists but is
  maze-pruned, confirmed in the maze-adjacency tranche's own review)
Real, sustained DOWN-held input -> CUR_ZONE settles at 9, correctly -- NOT a spurious RIGHT
  re-trigger despite PLAYER_X still sitting at the RIGHT clamp ceiling (IP-9130's own fix,
  the exact BL-0078 reproduction sequence, exercised here at scale=9 rather than T7.12's own
  default scale=3)
Extended settle window -> CUR_ZONE stays 9, no follow-on spurious transition
Forced redraw at region 9 (whose own right neighbor, region 10, is open) -> the right arrow
  tile renders at ARROW_ADDR_R (0x16, non-blank) -- IP-9140's own fix, confirmed at a freshly
  real-navigated, non-default-scale region, not only the static/isolated case T13.d checks
```

Every package's own corrected behavior held simultaneously, live, at a scale none of the four
individual VRs combined with genuine multi-step navigation this way.

## Dimension 4 — Traceability coherence

**Clean.** RTM's `FR-2300` row cites `IP-9050, IP-9120, IP-9130` together with `T7.11`
(`IP-9120`) and `T7.12` (`IP-9130`) — accurate, reflecting both packages' own real sequencing.
`FR-9100`'s Notes cite `IP-9110`. `FR-2320`'s row cites `IP-1030` (base) and `IP-9140` (fix).
Master Build Plan, verification `INDEX.md`, and `ROADMAP.md` all agree all four are `VERIFIED`.

## Dimension 5 — Documentation coherence

**Clean.** No `Claude.md`/`memory.md`/GDS-07/GDS-08 staleness found attributable to any of these
four packages specifically (the one pre-existing GDS-07 staleness this session's reviews found —
`BL-0089`, `SEED`/`KEYITEM_FLAGS`'s stale narrative clauses — belongs to `IP-1040`/`IP-9050`, not
this set). `SAVE_VERSION_VAL`'s own documented value (GDS-07 §3, line 89) still reads `0x03`,
one version behind the shipped `0x04` — **a genuine finding**, distinct from `BL-0089`.

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| 1 | `docs/architecture/07-data-model.md` (GDS-07 §3, line 89) | The SRAM save-format table's `A012` row states `SAVE_VERSION_VAL = 0x03` (as of `IP-9070`) and does not mention `IP-9110`'s later `0x03`→`0x04` bump. The shipped value is `0x04`, confirmed in `VR-9110`. §7a (line 227) also states the bump as "`0x02`→`0x03` (third bump)" without a fourth-bump follow-up note. Distinct from `BL-0089` (which covers `SEED`/`KEYITEM_FLAGS`, not the version guard). | Low | `03-architecture-design-synthesis` (a GDS-07 delta adding `IP-9110`'s own version-bump row, mirroring `IP-9070`'s §7a precedent) |

No Critical/High findings.

## Next step

This package set is clear to advance to `11-release-readiness` alongside Release 2 whenever the
user is ready to make that release decision (not this review's own call). **This closes
`10-integration-review`'s own sweep — every `VERIFIED` package in the tree now belongs to a
reviewed tranche or set.**
