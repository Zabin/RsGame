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

## Release-2 tranche (procgen-world increment, planned 2026-07-10)

**Scope:** all five Release-2 Features from the aesthetics/visual-story-narrative/procgen-
world-map increment, specified as [FS-102](../features/FS-102-procedural-world-generation.md)
(`FEAT-9000`), [FS-103](../features/FS-103-generated-region-screen-composition.md) (`FEAT-4100`),
[FS-104](../features/FS-104-main-menu-new-game-flow.md) (`FEAT-1100`),
[FS-105](../features/FS-105-generated-world-save-persistence.md) (`FEAT-5300`), and
[FS-106](../features/FS-106-aesthetic-biome-transition-compliance.md) (`FEAT-6100`). This is
genuinely new work — **no G3 bootstrap carve-out applies to any package in this tranche.**

### Deferred design decisions resolved in this pass

Three FS-102/FS-103 Open Questions (`BL-0038`) and both FS-104 Open Questions (`BL-0039`) were
explicitly deferred to this stage by their own text. Resolved here, following the FS-101/IP-1010
precedent of confident direct resolution rather than escalation:

**FS-102 OQ1/OQ3 + FS-103 OQ1/OQ2 (biome-family set, grammar table, tile/palette sizing, ROM
pointer):** **Reuse the five existing shipped terrain families exactly** — Water, Sand/Dirt,
Grass, Stone, Brick/Red (GDS-07 §5/GDS-08 §4's own palette table) — as the biome-family
vocabulary, per GDS-08 §8's own recommendation ("reuse the existing terrain-family palette
groups"). This has two large consequences that shrink this tranche's scope significantly:

1. **Zero new tile art or palette work is required.** Each family already has a fully-authored
   shipped screen-generator function reusable as that family's canonical representative:
   `lake_screen()` → Water, `beach_screen()` → Sand/Dirt, `forest_screen()` → Grass,
   `mountain_screen()` → Stone, `castle_screen()` → Brick/Red. (Extra per-family variety —
   e.g. `desert_screen()` as a second Sand/Dirt option, `plains_screen()`/`village_screen()`/
   `cave_screen()` as additional Grass/Stone variants — is a **future, optional**
   `08-content-authoring` addition; this tranche's Definition of Done needs only one function per
   family, since GDS-09's delta requires "one `fn()` per biome family," not per variant.)
2. **The grammar table is a linear axis, not a lookup table — no ROM pointer needed (resolves
   FS-102 OQ3).** Order the five families along one axis, index 0–4: **Water(0) – Sand(1) –
   Grass(2) – Stone(3) – Brick(4)** (directly matching R212's water→beach→…→mountains example,
   generalizing "sky" out since no such family is shipped, and placing Brick/Red — Castle, a
   structure/civilization biome — at the far end from Water, adjacent only to Stone). **Adjacency
   is legal iff the two families' axis indices differ by at most 1** — a single `SUB`+`CP` check
   Z80 can perform inline (`|idx_a - idx_b| ≤ 1`), needing no ROM-resident table at all. This
   resolves FS-102 OQ3 directly: **no new `patches` dict entry is needed for the grammar itself.**

**FS-102 OQ2 (generation algorithm):** **Flood-fill biome assignment over the fixed
`scale × scale` grid**, not a graph built from scratch:

1. Regions occupy a `scale × scale` grid exactly like the shipped 3×3 model generalizes
   (`row = index // scale, col = index % scale`) — **every** grid-adjacent pair is a valid
   transition (matching the shipped fully-connected-3×3 topology), so **reachability (FR-9120)
   is trivially satisfied by construction**, exactly as GDS-04's delta already notes the fixed
   grid never needed a reachability guard — this design keeps that property true at any scale.
2. Seed the xorshift16 PRNG (R111) from `SEED` (0 normalized to 1).
3. Assign region 0 (the start region, grid position `(0,0)`) axis-index **2 (Grass)** — matching
   the shipped world's default felt terrain and giving every generated world a consistent,
   familiar starting biome.
4. Visit every other region in row-major order; each region's axis-index = an already-visited
   grid-adjacent neighbor's axis-index, plus a PRNG-drawn delta in `{-1, 0, +1}`, **clamped to
   `[0, 4]`**. Because every grid-adjacent pair is generated from a delta of at most 1, **every
   grid-adjacent pair is grammar-legal by construction (FR-4310) — no candidate edge is ever
   rejected, no backtracking, no contradiction risk** (the exact WFC failure mode ADR-0009/R213
   name as the reason to avoid per-tile constraint solving).
5. Place exactly one `KeyItem` per region (FR-9130) — trivial, matching the shipped
   one-Carrot-per-zone convention, now generator-guaranteed rather than convention-only.

This algorithm is deliberately the simplest one satisfying all four generator-guaranteed
invariants (determinism, reachability, grammar-validity, one-KeyItem-per-region) — a design
choice this pass makes explicitly, not a default arrived at by omission.

**FS-104 OQ1 (SEED/SCALE ENTRY cancel path):** **B cancels back to MAIN MENU**, matching the
existing SAVE state's own A(confirm)/B(cancel) convention exactly — no new input convention
introduced.

**FS-104 OQ2 (menu input mapping):** D-pad up/down moves the highlighted option between
"continue"/"new game" (when both are present); A confirms the highlighted option — the same
cursor-based interaction shape ADR-0010 already specifies for the digit-cursor picker itself, not
a new convention.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| World generation routine (flood-fill biome assignment, PRNG, `REGION_GRAPH` layout) + item-agnostic `KeyItem` collection generalization + `worldgen.py` reference-generator oracle | [IP-1020](packages/IP-1020-procedural-world-generation.md) | `08-code-implementation` |
| `ALL_SCREENS` generalization to per-biome-family iteration + `build_rom.py`-side region-screen layout | [IP-1030](packages/IP-1030-generated-region-screen-composition-code.md) | `08-code-implementation` |
| Biome-family screen-generator registration (reusing the five existing shipped functions as canonical family representatives — zero new tile/palette authoring) | [IP-1031](packages/IP-1031-generated-region-screen-composition-content.md) | `08-content-authoring` |
| MAIN MENU + SEED/SCALE ENTRY states, SAVE's exit-to-main-menu option | [IP-1040](packages/IP-1040-main-menu-new-game-flow.md) | `08-code-implementation` |
| Save-format extension: `SEED`/`WORLD_SCALE`/`KeyItemFlags` persistence, version-guard bump | [IP-1050](packages/IP-1050-generated-world-save-persistence.md) | `08-code-implementation` |
| `FEAT-6100` (Aesthetic & Biome-Transition Compliance) | *(no package — see below)* | — |

**Split rationale:**

- **`FS-102` stays one package (IP-1020)**, mirroring FEAT-9000's own catalog-level cohesion
  decision (FP-05 finding #6) — the generation routine and the collection-mechanic
  generalization are tightly coupled (the same reasoning that merged `FR-9130`/`FR-3220` into one
  Feature to avoid an artificial cross-package cycle applies identically at the package level).
  The `worldgen.py` oracle rides the same package since it must be authored in lockstep with the
  SM83 routine from the start (GDS-09's delta), not bolted on afterward.
- **`FS-103` splits into code (IP-1030) and content (IP-1031)** — the exact code/content peer
  seam this skill's own workflow calls out. IP-1030 is pure `build_rom.py`/`asm_game.py`
  generalization (how the build assembles a variable-length, `WorldScale`-driven screen set
  instead of a fixed 9); IP-1031 is the biome-family-to-screen-generator registration (which
  existing function represents which family) — a content-authoring decision with **zero new
  pixel art**, per the biome-family reuse decision above. Keeping these separate lets
  `08-code-implementation` and `08-content-authoring` each own a clean Definition of Done instead
  of one package straddling both peers' scope.
- **`FS-104` stays one package (IP-1040)** — MAIN MENU, SEED/SCALE ENTRY, and SAVE's new exit
  option are one coherent state-machine extension; splitting them would leave an intermediate
  package unable to reach a testable end state (e.g. MAIN MENU alone, with no SEED/SCALE ENTRY to
  transition into on "new game," cannot be verified end-to-end).
- **`FS-105` stays one package (IP-1050)** — mirrors `IP-1010`'s own no-split precedent exactly
  (save-write and load-restore are one atomic contract; shipping either half alone leaves the
  save format partially migrated).
- **`FS-106` needs no Implementation Package.** Per its own spec (§8/§10), FEAT-6100 has **no
  runtime behavior and no module of its own** — its "implementation" already exists (GDS-08 delta
  §7/§8's checklist, `09-content-review`'s existing process). This tranche's `IP-1031` (the first
  content package this checklist applies to) is where FEAT-6100 is first *exercised*, via a
  future `09-content-review` pass — not authored as a package here. Naming this explicitly (rather
  than silently omitting FEAT-6100) keeps the Feature ↔ Package mapping complete and honest.

### Sequencing summary

**IP-1020 is this tranche's universal unblocker** — every other package either consumes its
generation output (IP-1030/IP-1031's screen rendering, IP-1050's save persistence) or triggers it
(IP-1040's new-game flow). Critical path (per FP-04, procgen-world increment): **IP-1020 →
IP-1030 → IP-1031** (3 packages — the same 3-node length FP-04's Feature-level critical path
predicted). IP-1040 and IP-1050 each depend only on IP-1020, parallel-eligible with each other
and with IP-1030/IP-1031.

### Backlog riders honored in this pass

- **`BL-0038`** (FS-102/FS-103's five shared Open Questions): resolved above — biome-family reuse,
  linear grammar axis, flood-fill algorithm, no ROM pointer needed.
- **`BL-0039`** (FS-104's two Open Questions): resolved above — B-cancels convention, cursor-based
  menu input mapping.
- **`BL-0019`** (ROM-headroom watch): IP-1020 (WRAM growth) and IP-1050 (SRAM growth) both carry
  NFR-4000/NFR-4200 headroom re-affirmation checklist items.

## Post-ship remediation tranche (playtesting bugs `BL-0047`/`BL-0048`, planned 2026-07-11)

Two bugs from the project owner's own playtesting of the shipped procgen-world tranche, both
already carrying reproduced root causes and recommended remediation shapes at intake (`00-intake`,
this session). Per this skill's own Step 1 discipline, both cuts additionally required the
mandatory **verb inventory** and **supersession sweep** checks before being called complete.

### Verb inventory — the procgen-world capability, re-audited

The Release-2 tranche (above) covered *generate* (`IP-1020`), *render* (`IP-1030`/`IP-1031`),
*trigger/menu* (`IP-1040`), and *persist* (`IP-1050`) — but never *navigate*. Re-auditing this now
against `BL-0047`'s own finding: `check_zone_transition` is the sole navigation call site, and it
was never touched by any Release-2 package. No deferral was ever recorded for it — it was simply
missed. This tranche closes that gap.

### Supersession sweep — run against `BL-0047`'s own framing ("`check_zone_transition` was never
generalized past the fixed-3×3 model")

A sweep for the retired model's literal signature (`CUR_ZONE` compared against small integer
literals tied to a 3×3 shape; fixed 9-entry tables indexed by `CUR_ZONE`) across
`asm_game.py`/`tilemaps.py`/`build_rom.py` found **two more instances, not just the one
`BL-0047` itself named**:

- **`SCOREITEM_FLAGS`** (`asm_game.py:44`) — still a fixed 9-byte array indexed by `CUR_ZONE`,
  unlike its sibling `KEYITEM_FLAGS` (already widened to 81 bytes by `IP-1020`). Filed as
  **`BL-0058`** (Critical) — fixing `BL-0047` alone, without this, converts a dormant bug into
  live WRAM corruption of `REGION_GRAPH` itself, since `CUR_ZONE` values above 8 become reachable
  the moment navigation is fixed.
- **`ZONE_COLLECTS`/`zc_table`** (`tilemaps.py:407`) — still the original 9 hand-authored,
  zone-named spawn-position lists (the module's own docstring says so verbatim), read via a
  9-entry ROM table indexed by `CUR_ZONE`. Filed as **`BL-0059`** (Critical) — the same
  dormant-until-navigation-is-fixed pattern, reading past the ROM table's own bounds.

Both are **causally coupled to `BL-0047`'s own fix, not independent findings** — `BL-0047`'s
remediation is what makes `CUR_ZONE > 8` reachable at all; `BL-0058`/`BL-0059` are what make that
reachability safe. Sweep result recorded here per this skill's own mandatory-recording rule:
**not clean — two additional Critical defects found and packaged alongside the reported bug,
not silently absorbed into it and not deferred.**

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| Widen `SCOREITEM_FLAGS`/`SRAM_SCOREITEM` to the full generated-region range (81 bytes); relocate both to avoid WRAM/SRAM collisions; regeneralize `ZONE_COLLECTS`/`zc_table` to 5 biome-family-representative lists keyed by biome-id (`BL-0058`/`BL-0059`) | [IP-9070](packages/IP-9070-cur-zone-indexed-structures-generalization.md) | `08-code-implementation` |
| Regeneralize `check_zone_transition` to read `REGION_GRAPH`'s neighbor bytes instead of hardcoded `CUR_ZONE` arithmetic (`BL-0047`) | [IP-9050](packages/IP-9050-generated-world-navigation-fix.md) | `08-code-implementation` |
| Fix `check_save_valid`'s `MM_CURSOR`-reset side effect clobbering the player's own MAIN MENU toggle (`BL-0048`) | [IP-9060](packages/IP-9060-main-menu-cursor-fix.md) | `08-code-implementation` |

**Split rationale:**

- **`IP-9070` split out from `IP-9050`, but sequenced as a hard prerequisite, not an independent
  parallel package.** Both are instances of "make a `CUR_ZONE`-indexed structure honor the
  generated world's real size," but they touch entirely different concerns (WRAM/SRAM layout +
  save-format version vs. navigation control flow) and have independently testable Definitions of
  Done. They are **not** parallel-eligible the way `IP-1040`/`IP-1050` were, though: `IP-9050`
  activating `CUR_ZONE > 8` before `IP-9070` widens the structures that index it would ship the
  exact corruption this sweep exists to prevent. `IP-9050`'s own Dependencies field names `IP-9070`
  explicitly for this reason — this is a correctness-ordering dependency, not a convenience one.
- **`SCOREITEM_FLAGS` and `ZONE_COLLECTS` fused into one package (`IP-9070`)**, not split further,
  because they are the same class of defect (a `CUR_ZONE`-indexed structure sized/shaped for the
  old 9-zone model) found by the same sweep, and a single Definition of Done — "every
  `CUR_ZONE`-indexed WRAM/ROM structure is safe across the full `scale²` region range" — covers
  both without the awkwardness of an intermediate half-fixed state.
- **`IP-9060` split out from `IP-9050`/`IP-9070`** because it is a wholly unrelated defect (MAIN
  MENU cursor logic) in the same file (`asm_game.py`) purely by coincidence of module boundaries —
  no shared root cause, no dependency in either direction, genuinely parallel-eligible with the
  other two.

### Sequencing summary

**`IP-9070` is this tranche's prerequisite** — `IP-9050` depends on it (correctness, not merely
convenience: see split rationale above). `IP-9060` is independent of both and parallel-eligible.
Critical path: **`IP-9070` → `IP-9050`** (2 packages). No package in this tranche is `08-content-
authoring` scope (WRAM/SRAM layout and control-flow only, no tile/palette/screen changes).

### Backlog riders honored in this pass

- **`BL-0047`** (Critical, navigation ignores `REGION_GRAPH`): packaged as `IP-9050`.
- **`BL-0048`** (High, MAIN MENU cursor unreachable): packaged as `IP-9060`.
- **`BL-0058`**/**`BL-0059`** (Critical, discovered by this pass's own mandatory supersession
  sweep): packaged as `IP-9070`, sequenced as `IP-9050`'s hard prerequisite.
- **`BL-0019`** (ROM/SRAM-headroom watch): `IP-9070` grows SRAM usage (9→81 bytes, ×1, net +72
  bytes) — carries an `NFR-4200` headroom re-affirmation checklist item.

## Maze-shaped region adjacency (`FS-107`/`FS-108`, planned 2026-07-11)

Two tranches's worth of specified work, planned together since the second (`FS-108`) is a direct
functional dependent of the first (`FS-107`): `FS-107` (`FEAT-9100`, `ADR-0012`'s maze-generation
decision) and `FS-108`'s logic half (`FEAT-2100`, blocked-edge classification — rendering half not
planned this pass, see below).

### Verb inventory

`FS-107` (`FEAT-9100`) is pure **generate** — `render`/`navigate`/`persist`/`review` all get an
explicit deferral-not-applicable note (`IP-1070` §7): `dsr_p`/`draw_region_arrows`/
`check_zone_transition` already consume `REGION_GRAPH` generically and need zero changes
(`ADR-0012` point 2, confirmed by direct re-read); `REGION_GRAPH` is never persisted; no new
content is authored. `FS-108`'s logic half (`FEAT-2100`) is pure **render** — `generate` is
`FS-107`'s own scope (a hard dependency, not this tranche's to redo); `navigate`/`persist` don't
apply; `review` doesn't apply to the logic-only package (no new visible tile drawn yet), though it
will apply to the eventual rendering-half package once `BL-0068` resolves.

### Supersession sweep

Neither package retires an existing model — `FS-107` is new generation logic layered onto an
unchanged biome-assignment pass (`ADR-0012` point 1: "entirely unchanged"); `FS-108`'s logic half
extends `draw_region_arrows`'s existing 2-state branch into a 3-state one without removing the
open-edge case. Both packages' own mandatory sweeps (run per this skill's own rule regardless) are
recorded in full in `IP-1070`§7/`IP-1080`§7 — summary: `dsr_p`/`draw_region_arrows`/
`check_zone_transition`/`tilemaps.py` all confirmed to have no full-lattice-connectivity
assumption baked in; `test_rom.py`'s existing `T12` suite (`T12.c`/`T12.d`) confirmed, by direct
read (`test_rom.py:799–819`), to already iterate only *existing* neighbor entries — **needs no
change** for either package, a genuine "found nothing" result, not silence.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| Spanning-tree carve (randomized DFS/recursive backtracker) + canonical-edge braid/prune pass, `generate_world`'s new second pass; `worldgen.py` oracle mirror (`FR-9140`/`FR-9150`) | [IP-1070](packages/IP-1070-maze-shaped-region-adjacency.md) | `08-code-implementation` |
| Render-time open/blocked/absent edge classification inside `draw_region_arrows`, logic half only (`FR-2330`, partial) | [IP-1080](packages/IP-1080-maze-aware-edge-classification.md) | `08-code-implementation` |

**Split rationale:**

- **One package for `FS-107`, not split further.** The spanning-tree carve and the braid/prune
  pass are two steps of one algorithm operating on the same data in the same routine, with one
  coherent Definition of Done ("`REGION_GRAPH` holds a maze, not a full lattice, with reachability
  preserved") — splitting them would create an intermediate, untestable half-state (a tree with no
  braid pass is not what `FR-9140` specifies).
- **`IP-1080` split out from `IP-1070`**, sequenced as a hard dependent, not fused into one
  package, because they implement two different Features (`FEAT-9100` vs. `FEAT-2100`) owned by
  two different Epics (`EP-5000` vs. `EP-1000`) with independently statable Definitions of Done —
  mirroring `IP-9070`→`IP-9050`'s own precedent of splitting causally-coupled work along Feature
  boundaries rather than fusing it for convenience.
- **`FS-108`'s rendering half is deliberately not packaged this pass.** `BL-0068` (the `GDS-08`
  tile-art delta) has not resolved — packaging a rendering interface ahead of that decision would
  mean guessing at tile/palette allocation this stage has no authority to invent (this skill's own
  SHALL-NOT-modify-specs-around-a-gap rule). `IP-1080` covers only the closeable logic half;
  FS-108's own Acceptance Criterion 4 (the visual claim) stays explicitly open in `IP-1080`'s own
  Definition of Done (§10) rather than silently implied covered.

### Sequencing summary

**`IP-1070` is this tranche's own prerequisite** — `IP-1080` depends on it reaching `VERIFIED`
(not merely `COMPLETE`, per this skill's own `READY` convention), since there is no maze-blocked
case to classify before a maze exists. Critical path: **`IP-1070` → `IP-1080`** (2 packages, the
tranche's full extent — no parallel-eligible package this pass). Both are `08-code-implementation`
scope (no tile/palette/screen changes in either — `IP-1080`'s own classification branch is a
no-op render-wise until the rendering half ships).

### Backlog riders honored in this pass

- **`BL-0064`** (maze-shaped region adjacency): packaged as `IP-1070`.
- **`BL-0065`** (braid-fraction parameter): folded into `IP-1070` (same generation pass, per
  `FS-107`'s own scope — not a separate package).
- **`BL-0067`** (3-state edge indicator): logic half packaged as `IP-1080`; rendering half remains
  riding `BL-0068`, not packaged this pass.
- **`BL-0068`** (the `GDS-08` tile-art delta `FEAT-2100`'s rendering half needs): **not resolved
  by this pass** — still rides a future `03-architecture-design-synthesis` invocation, named
  explicitly rather than silently absorbed into `IP-1080`.
- **`BL-0019`** (ROM/WRAM-headroom watch): `IP-1070` adds up to 84 bytes of new transient WRAM
  scratch at `scale=9` — carries an `NFR-4200` headroom re-affirmation checklist item.

## Movement/pickup/UI bug-remediation tranche (`BL-0049`/`BL-0051`/`BL-0052`/`BL-0053`, planned 2026-07-11)

Four standing, unpackaged backlog entries, each already carrying a reproduced root cause and a
recommended remediation shape from prior triage (three filed via `00-intake` this session, one —
`BL-0053` — likewise). None depends on the maze-shaped-adjacency thread or the five packages
awaiting fresh-session verification; all four are independently plannable and, once authorized,
independently implementable.

### Verb inventory

Not applicable — none of these four touches a multi-verb capability (generate/render/navigate/
persist/review). Each is a narrow, single-function correctness fix: `handle_play_input`'s own
movement-clamp arithmetic (`BL-0051`/`BL-0052`), `check_collisions`' own pickup-overlap arithmetic
(`BL-0053`), and `save_screen`'s own static tilemap content (`BL-0049`). No verb-inventory gap risk
of the `BL-0054` kind exists at this granularity.

### Supersession sweep

None of these four bugs retires or supersedes an existing model — each corrects a magic-constant/
threshold defect within an already-generalized routine (`handle_play_input`/`check_collisions`
already operate identically across every generated world; `save_screen` is static content, not
dispatched by any generalized model). Per this skill's own mandatory discipline (including the
`BL-0071`-established extension to check `test_rom.py` itself, not just production call sites), a
sweep was still run:

- **`BL-0051`/`BL-0052` (movement clamps):** `grep` for `CP_n(17)`/`CP_n(160)` and their sibling
  magic bounds (`CP_n(156)`, `CP_n(128)`, `CP_n(129)`, `CP_n(0xFF)`) across `asm_game.py` found no
  other call site referencing these two specific clamp constants — `handle_play_input`'s own four
  directional blocks (`asm_game.py:512-545`) are the only place `PLAYER_X`/`PLAYER_Y` are
  clamped by direct movement (as opposed to `check_zone_transition`'s separate, correct,
  already-`REGION_GRAPH`-driven edge-detection constants at `156`/`0`/`18`/`128`, which this
  tranche does not touch). **Found in `test_rom.py`, not production code:** `T7.8` (`test_rom.py:
  477-482`) directly asserts the *current buggy* UP floor (`17`) as if it were correct behavior
  ("movement floor is Y=17 (zone 0 = top row, no up-transition)") — this test will fail once
  `BL-0051` ships unless updated in the same package. `T7.10`'s own comment ("X capped at 159")
  is similarly stale once `BL-0052` ships (real cap becomes `152`), though the check's own
  assertion (`x<=159`) happens not to break numerically since it forces `X=159` directly rather
  than deriving it via the clamp — flagged for a comment correction, not a behavior-changing fix.
- **`BL-0053` (pickup hitbox):** `grep` for `CP_n(10)` across `asm_game.py` found exactly the two
  instances `check_collisions`' own X/Y overlap test uses (`asm_game.py:573`/`578`) — no other
  routine reuses this threshold. In `test_rom.py`, every existing `T8` pickup check places the
  player at the item's own exact `(x, y)` coordinates (`dx=dy=0`) — well inside any reasonable
  bounding-box definition — so **no existing test assumes the old symmetric window's specific
  asymmetry; the sweep found nothing to fix, only new boundary-exactness checks to add.**
- **`BL-0049` (SAVE screen text):** `grep` for `save_screen`/`GS_SAVE`/`st_save` across
  `asm_game.py`/`tilemaps.py`/`test_rom.py` found no existing test exercises the SAVE screen's own
  tilemap content at all (only `T14.d0`'s state-transition check reaches `GS_SAVE`, asserting
  nothing about what's drawn there) — nothing to break, a pure content addition.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| Correct `handle_play_input`'s UP/RIGHT movement-clamp magic bounds to match the already-correct DOWN/LEFT pattern (`BL-0051`/`BL-0052`); update `T7.8`'s own stale-floor assertion and `T7.10`'s stale comment | [IP-9090](packages/IP-9090-movement-clamp-boundary-fix.md) | `08-code-implementation` |
| Correct `check_collisions`' pickup-overlap test from a symmetric ±9/±9 window to a true axis-aligned bounding-box overlap test against the sprite's real 8×16 extent (`BL-0053`) | [IP-9100](packages/IP-9100-collectible-pickup-hitbox-fix.md) | `08-code-implementation` |
| Add on-screen text for the SAVE screen's third (SELECT) option, currently silent (`BL-0049`) | [IP-9080](packages/IP-9080-save-screen-third-option-labeling.md) | `08-content-authoring` |

**Split rationale:**

- **`BL-0051`/`BL-0052` fused into one package (`IP-9090`)** — same function
  (`handle_play_input`), same class of defect (a magic clamp bound inconsistent with its own
  already-correct sibling direction), one coherent Definition of Done ("every directional clamp
  matches its own established-correct sibling pattern"), following `IP-9070`'s own precedent for
  fusing same-class-same-sweep defects rather than splitting further.
- **`BL-0053` split out from `IP-9090`** despite sharing `asm_game.py` as a file, because it is a
  different function (`check_collisions`, not `handle_play_input`), a different root-cause class
  (an overlap-test formula, not a magic boundary constant), and independently testable/rollback-
  able — no shared root cause with the movement clamps beyond incidental file co-location.
- **`IP-9080` split out from both `08-code-implementation` packages** because it is
  `08-content-authoring` scope (a `tilemaps.py` data-only change — `st_save`'s own input-handling
  logic, `asm_game.py:319-339`, already correctly implements the SELECT option's save-and-exit
  behavior; only the missing on-screen text needs adding), a different stage-08 peer entirely, and
  genuinely parallel-eligible with the other two.

**UI-input-mapping question resolved directly (per this entry's own disposition note, citing
`FS-104` OQ2's established precedent):** keep the existing `A`/`B`/`SELECT` one-button-per-option
scheme unchanged — do **not** redesign it into a cursor-based UP/DOWN-select/A-confirm scheme
matching MAIN MENU's own convention. Rationale: the existing scheme already works correctly and
is a single-screen, three-fixed-option menu (not a growing/reorderable list, unlike MAIN MENU);
redesigning the input model to fix a missing *label* would be solving a problem the user never
reported (the report is specifically "no on-screen text," not "the controls are confusing") and
would touch `st_save`'s already-correct, already-tested control flow for no behavioral gain — out
of proportion to the actual defect. `IP-9080`'s own scope is therefore text-only, no
`asm_game.py` change.

### Sequencing summary

All three packages are mutually independent (three different root causes, three different
Definitions of Done, two different files with no shared symbol) — fully parallel-eligible, no
critical path within this tranche. None depends on the maze-shaped-adjacency thread, the five
packages awaiting fresh-session verification, or each other.

### Backlog riders honored in this pass

- **`BL-0051`**/**`BL-0052`** (movement-clamp magic-bound defects): packaged as `IP-9090`.
- **`BL-0053`** (pickup-hitbox asymmetric window): packaged as `IP-9100`.
- **`BL-0049`** (SAVE screen's silent third option): packaged as `IP-9080`; the entry's own
  UI-input-mapping open question resolved directly above, not escalated.
- **`BL-0071`** (supersession-sweep-must-include-`test_rom.py` discipline, filed after `IP-1070`):
  honored directly in this pass's own sweep above (`T7.8`/`T7.10` checked and one real conflict
  found and routed into `IP-9090`'s own scope).

## `gw_prng_step` mixing-step repair (`BL-0074`/`ADR-0014`, planned 2026-07-11)

One package: the core PRNG fix `ADR-0014` decided and the user explicitly authorized (2026-07-11,
"Yes, ship the fix"). No FS — this is a repair to an already-shipped, `VERIFIED` (`IP-1020`)
routine's own internal algorithm, not a new capability; the observable contract (`gw_prng_step`'s
own `TMP1:TMP2` in/out interface, called once per biome-assignment region and repeatedly within
`IP-1070`'s maze pass) is unchanged.

### Verb inventory

Not applicable — a single-routine algorithmic repair, not a multi-verb capability.

### Supersession sweep

Run directly (per `BL-0071`'s own extension of this discipline to `test_rom.py`, not just
production call sites): every `test_rom.py` check that depends on `worldgen.py`'s `generate()`
compares its output against the **live SM83 output for the same `(seed, scale)` pair**
(`T12.a/b`, `T19.c`, `T5.9`, `T11.a`'s own region-0 star position, `T17`'s DFS-tour checks) — none
hardcodes a literal expected biome-id/neighbor byte sequence independent of the oracle. Since this
package updates `worldgen.py`'s own `_step` function in the same lockstep discipline
`ADR-0012`/`ADR-0013` already established, every one of these checks continues to pass
automatically once both sides change together — **no test needs its own hardcoded values
updated**, only the shared oracle algorithm. `T12.f` (seed=0 normalization) hooks *before* any
`gw_prng_step` call and asserts a property of `ADR-0010`'s own normalization step, not of the
mixing algorithm — unaffected either way. **Sweep result: clean, nothing to update beyond the
oracle mirror itself (already this package's own §6 task).**

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| Repair `gw_prng_step`'s mixing step to the period-sound `7,9,8` shift triplet; bump `SAVE_VERSION_VAL`; update `worldgen.py`'s oracle mirror in lockstep; re-measure `ADR-0013`'s own maze-pass perturbation's continued necessity; add a non-degeneracy statistical check (`BL-0074`) | [IP-9110](packages/IP-9110-gw-prng-step-mixing-step-repair.md) | `08-code-implementation` |

**No split** — one routine, one coherent Definition of Done ("the shipped PRNG no longer
degenerates for any seed in a representative corpus"), a single `asm_game.py`/`worldgen.py`/
`test_rom.py` change set with no independently-shippable sub-piece.

### Sequencing summary

No dependency on any other in-flight package this session. Independent of the (exhausted)
movement/pickup/UI tranche and the (blocked/unauthorized) maze-shaped-adjacency tranche's
`IP-1080`. Touches `gw_prng_step`, which `IP-1070`'s own maze pass calls — but `IP-1070` is
`COMPLETE`, not yet `VERIFIED`, so this package's own change to the routine `IP-1070` depends on
is a real (if narrow) risk surface, named explicitly in Risks below rather than silently assumed
safe.

### Backlog riders honored in this pass

- **`BL-0074`** (default-seed/effectively-all-seeds biome-flooding, root-caused and architecturally
  decided this session): packaged as `IP-9110`.
- **`BL-0071`**/**`BL-0073`** (supersession-sweep-must-include-`test_rom.py`; planning-formula
  verification-against-reproduction-data): both honored directly in this pass (see Supersession
  sweep above; the `7,9,8` triplet's own non-degeneracy was verified against a 2000-seed corpus
  before this package was written, not merely asserted from `ADR-0014`'s own citation).

## RIGHT zone-transition regression (`BL-0076`, planned 2026-07-12)

One package: a single boundary-constant fix in `check_zone_transition`, a direct regression from
this session's own `IP-9090`. No FS — this repairs an already-shipped, already-`COMPLETE`
routine's internal threshold, not a new capability; `check_zone_transition`'s own interface and
every other direction's behavior are unchanged.

### Verb inventory

Not applicable — a single-constant boundary fix, not a multi-verb capability.

### Supersession sweep

Run directly, extended per this bug's own root-cause class (a magic-number boundary constant that
drifted out of sync with a sibling constant elsewhere in the same file — exactly the class of gap
`IP-9090`'s own supersession sweep should have, but did not, catch): grepped `asm_game.py` for
every `CP_n(156)`, `CP_n(152)`, `CP_n(153)`, `CP_n(159)`, `CP_n(160)` occurrence. **Exactly two
hits, both already accounted for**: `handle_play_input`'s own RIGHT clamp (`asm_game.py:518`,
`CP_n(153)`, correctly fixed by `IP-9090`) and `check_zone_transition`'s own RIGHT-edge trigger
(`asm_game.py:662`, `CP_n(156)`, this package's own target). No third call site carries the same
latent inconsistency (`draw_region_arrows`' `ARROW_ADDR_R` is a fixed VRAM tilemap offset,
unrelated to `PLAYER_X`; `update_oam`'s own OAM-X write is a flat `+8` sprite-offset add, not a
boundary comparison). Extended to `test_rom.py` per `BL-0071`'s own established discipline:
`T7.10`/`T17.c1`/`T11.a2` all use a memory-forced `PLAYER_X` value (`159`, `159`, `156`
respectively) at or above the *new* threshold (`152`) as well as the old one — none needs updating,
each remains correct under the new comparison for the reason it was written (a true grid-boundary
region with no right neighbor, or a value comfortably above either threshold). **Sweep result:
clean — exactly one other file location shares the old constant, and it's this package's own
target, not an overlooked duplicate.**

**Broader test-coverage gap found, named but not fixed by this package** (a `BL-0071`/`BL-0073`-
class process finding, not this package's own scope-creep): no existing `test_rom.py` check
confirms a zone transition actually *fires* via genuine, real button-press-driven walking, in any
of the four directions — every existing "did the zone change" check (`T11.a2`, `T17.a`, `T19.*`)
uses memory-forced `PLAYER_X`/`PLAYER_Y` teleportation to isolate the transition logic from the
movement clamp, which is legitimate for *their* own purpose (testing `check_zone_transition` in
isolation) but is exactly the reason this regression shipped undetected — no test exercises the
*combination* of the real movement clamp and the transition threshold together. This package adds
that missing case for RIGHT (`BL-0076`'s own direction); UP/DOWN/LEFT remain covered only
indirectly (their clamp/threshold pairs are separately confirmed consistent, see the package's own
§4) — a full real-button-press positive-transition sweep across all four directions is recommended
as a future, low-urgency `07` pass, not required here.

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| Fix `check_zone_transition`'s RIGHT-edge threshold (`CP_n(156)`→`CP_n(152)`) to match `IP-9090`'s corrected movement clamp; add a real-button-press regression test (`BL-0076`) | [IP-9120](packages/IP-9120-right-zone-transition-threshold-fix.md) | `08-code-implementation` |

**No split** — one comparison operand, one coherent Definition of Done ("a real, sustained
rightward button-press walk crosses into an open right-neighbor zone"), a single `asm_game.py`/
`test_rom.py` change set with no independently-shippable sub-piece.

### Sequencing summary

No dependency on any other in-flight package this session — `check_zone_transition`'s only
functional dependency is `IP-1010`'s own bootstrap (`VERIFIED`) and the already-`COMPLETE`
`IP-9050`/`IP-9090` (both touch the same function/its caller; this package's own diff is additive
to `IP-9090`'s, not a conflict). Independent of `IP-9110` (touches `gw_prng_step`, a disjoint
routine) and the blocked/unauthorized `IP-1080`.

### Backlog riders honored in this pass

- **`BL-0076`** (Critical, RIGHT zone-transition regression — root-caused and reproduced this
  session): packaged as `IP-9120`.
- **`BL-0071`** (supersession sweep must include `test_rom.py`): honored directly above.

## Spurious zone-transition regression (`BL-0078`, planned 2026-07-12)

One package: `check_zone_transition`'s own trigger model gains an intent gate. No FS — this
repairs an already-shipped, already-`COMPLETE` routine's decision logic, not a new capability;
its interface and every direction's *legitimate* transition behavior are unchanged.

### Verb inventory

Not applicable — a single-routine gating fix, not a multi-verb capability.

### Supersession sweep

Run directly, per this bug's own root-cause class (a routine whose trigger condition changed
scope — position-only → position-and-intent — needs every caller of that routine, test or
production, re-examined for an assumption the old, looser condition let slide). Confirmed by
direct code read: `check_zone_transition`'s four branches (`asm_game.py:660-701`) are symmetric —
none tests player input today, so the defect the user reported for RIGHT applies identically, by
construction, to LEFT/UP/DOWN. The fix therefore gates all four uniformly, not just RIGHT.

Swept `test_rom.py` for every `pb.memory[PLAYER_X] = …`/`pb.memory[PLAYER_Y] = …` write followed
by ticking (a potential transition trigger) with **no accompanying `button_press`/`button_release`
for the matching direction**:

- **`T11.a2`** (`test_rom.py:784-798`): forces `PLAYER_X`/`PLAYER_Y` directly to a boundary value
  and ticks, with no button held at all. **Needs updating.**
- **`_t17_do_move`** (`test_rom.py:1601-1615`): the shared helper behind `T17.a`, `T17.b2`, and
  `T17.b5` — teleports the player to a boundary and ticks, no button held. **Needs updating** (one
  fix here covers all three call sites/every check that depends on it).
- **`T17.c1`/`T17.c2`** (`test_rom.py:1675-1684`): force a boundary position with no open
  neighbor (region 24, a true grid boundary), asserting *no* transition occurs. Correct under
  either the old or the new gate (blocked by the missing neighbor either way) — **no update
  needed**, confirmed by direct trace, not assumed.
- Every other `PLAYER_X`/`PLAYER_Y` write in the file (item-pickup positions, save/load
  round-trip checks, state-reset positions between test blocks — `test_rom.py:404, 456, 496, 507,
  520, 527, 552, 593–625, 699, 729–730, 813, 1219–1239, 1307, 1368–1370, 1428, 1638, 1722–1727`)
  either already accompanies a real button hold (`T7.9`–`T7.11`) or targets an interior,
  non-boundary position with no transition in play — confirmed clean by direct read of each.
  **Correction to this bug's own intake framing**: the intake report speculated "several `T16`
  `CUR_ZONE`-forcing patterns" might be affected — direct sweep found `T16` uses
  `force_region_redraw` (sets `CUR_ZONE`/`NEED_REDRAW` directly, never `PLAYER_X`/`PLAYER_Y`) for
  an unrelated purpose (isolating collection behavior in a specific region), not transition
  testing — `T16` is unaffected, not merely assumed clean.

**Why `JOY_CUR`, not `JOY_NEW`**: `handle_play_input` itself gates continuous movement on
`JOY_CUR` (held state), not `JOY_NEW` (edge-triggered, newly-pressed-this-frame) — a player
walking into a boundary over several held-frames should transition on whichever frame position and
input coincide, not only the literal first frame the direction was pressed (which may have
happened many frames and pixels earlier). `check_zone_transition` runs every frame regardless of
`NEED_REDRAW`, so this holds regardless of frame timing. Consistency with the movement routine it
directly follows in `st_playing`'s own per-frame sequence is the deciding factor.

**Test methodology fix, not a `JOY_CUR` memory poke**: `JOY_CUR` (`asm_game.py:32`) is written
every frame by `read_joypad` (`asm_game.py:477`) from PyBoy's own real (virtual) hardware button
state — a raw `pb.memory[JOY_CUR] = …` poke would be overwritten by the very next tick's joypad
read, before `check_zone_transition` ever sees it, whenever more than one tick separates the poke
from the check. The correct test-side fix is a real `pb.button_press(<dir>)` held across the
teleport-and-settle window (exactly `T7.9`–`T7.11`'s own already-working pattern) — the teleport
still gives instant positioning (no need to simulate pixel-by-pixel walking), the held button
satisfies the new gate honestly.

### Work unit and package cut

| Work unit | Package | Owner |
|---|---|---|
| Gate `check_zone_transition`'s four branches on the corresponding `JOY_CUR` direction bit; update `T11.a2`/`_t17_do_move` to hold the matching button; add a direct `BL-0078` regression test (`BL-0078`) | [IP-9130](packages/IP-9130-zone-transition-intent-gate.md) | `08-code-implementation` |

**No split** — one routine, one coherent Definition of Done ("a zone transition fires only when
the player is actually pressing the corresponding direction, in addition to being positioned at
the edge"), a single `asm_game.py`/`test_rom.py` change set with no independently-shippable
sub-piece; the test-suite ripple is two call sites, not a separable body of work.

### Sequencing summary

No dependency on any other in-flight package this session — `check_zone_transition`'s only
functional dependency is `IP-1010`'s own bootstrap (`VERIFIED`) and the already-`COMPLETE`
`IP-9050`/`IP-9120` (both touch the same routine; this package's own diff is additive/corrective,
not a conflict). Independent of `IP-9110` (`gw_prng_step`, disjoint) and the blocked/unauthorized
`IP-1080`.

### Backlog riders honored in this pass

- **`BL-0078`** (High, spurious zone-transition regression — root-caused and reproduced at
  intake): packaged as `IP-9130`.
- **`BL-0071`** (supersession sweep must include `test_rom.py`): honored directly above.

## Maze-blocked edge indicator — rendering half (`FS-108`/`FEAT-2100`/`BL-0075`, planned 2026-07-12)

`FS-108`'s own last Open Question closed 2026-07-12 (`06-feature-specification`): the rendering
half's workflow and Acceptance Criteria (Workflow C, AC-4/AC-5) are now fully specified. This
tranche packages that spec — `IP-1080`'s own classification logic (`VERIFIED`) is untouched;
this pass wires the visible result.

### Verb inventory

Pure **render** — `generate` is `FS-107`'s own closed scope; the classification decision this
rendering consumes is `IP-1080`'s own closed scope (`navigate` doesn't apply); `persist` doesn't
apply (no new WRAM/SRAM entity, `FS-108` §10); `review` **does** apply this time (unlike
`IP-1080`'s own logic-only pass) — new visible tile art ships, so a `09-content-review` pass is
owed after implementation, mirroring `IP-1031`'s own precedent as `FEAT-6100`'s exercise.

### Supersession sweep

Not applicable in the retirement sense — this pass adds a third rendered state, it retires
nothing. Confirmed by direct code read: `draw_region_arrows`'s existing open-edge branch
(`asm_game.py:1002-1013`) and `_arrow_write` helper are unchanged targets, not superseded;
`TL_ARROW_U/D/L/R`'s own tile-index block (`tiles.py:36-39`) is untouched, the new tiles land at
the confirmed-free `0x1A`-`0x1D` slots immediately after it. Swept `test_rom.py`'s existing `T20`
suite (`T20.a`/`b`/`c`) for any assumption that would break once a `blocked` edge starts drawing a
non-blank tile: `T20.b`/`T20.c` both currently assert `not arrow_present` (`ARROW_POS[direction]
== ARROW_TILE[direction]`, the *open*-tile constant) for blocked/absent — that assertion remains
correct unchanged (a blocked tile is not the open tile), but needs a **new**, additive assertion
for the blocked case specifically (the tile now *is* the new blocked-tile constant, not blank) —
recorded as this package's own `Tests to Add`, not a rewrite of the existing check.

### Work units and package cut

| Work unit | Package | Owner |
|---|---|---|
| 4 new tile bitmaps (`TL_BLOCKED_U`/`D`/`L`/`R`, `0x1A`-`0x1D`, a short broken/dashed bar per `GDS-08` §10's silhouette concept) registered via `build_tile_data()`'s existing `put()` convention | [IP-1081](packages/IP-1081-maze-blocked-edge-indicator-content.md) | `08-content-authoring` |
| `draw_region_arrows`'s blocked-case render branch: for each direction already classified `blocked` by `IP-1080`'s own arithmetic (`DRA_ROW`/`DRA_COL` vs. `WORLD_SCALE`), write the direction's new tile at the existing `ARROW_ADDR_*` position (palette 2, reusing `_arrow_write`'s own write shape) instead of the current no-op | [IP-1082](packages/IP-1082-maze-blocked-edge-indicator-render.md) | `08-code-implementation` |

**Split rationale:**

- **Two packages, mirroring `IP-1030`/`IP-1031`'s own code/content peer-split precedent** for the
  same FS (`FS-103`) — different stage-08 peers own different files (`tiles.py` vs. `asm_game.py`),
  and the tile art half genuinely needs its own `09-content-review` pass this time (unlike
  `IP-1080`, which shipped no visible art at all).
- **Content package first, reversing `IP-1030`→`IP-1031`'s own ordering** — there, the code half
  established the interface the content half plugged into; here, the *code* half's new render
  branch needs the *content* half's new tile-index constants (`TL_BLOCKED_U`/`D`/`L`/`R`) to exist
  before it can reference them, so the dependency runs content→code this time. Named explicitly so
  the reversal isn't mistaken for an inconsistency.
- **Not fused into one package** despite the small combined size — the code branch's own
  Definition of Done ("draws the correct tile for a `blocked` classification") is independently
  statable and testable from the content package's own DoD ("4 new tiles exist, registered, cost
  0 new palette entries") once the tile constants exist as a dependency, mirroring the same
  Feature-boundary-respecting logic `IP-1070`/`IP-1080`'s own split rationale used (here it's a
  code/content boundary, not a Feature boundary, but the same "don't fuse for convenience"
  principle applies).

### Sequencing summary

**Critical path: `IP-1081` → `IP-1082`** (2 packages). `IP-1082` depends on `IP-1081` reaching
`VERIFIED` (this skill's own `READY` convention — `COMPLETE` is not sufficient) for the tile
constants to exist; both also depend on `IP-1080` (`VERIFIED`, already shipped) for the
classification arithmetic/WRAM bytes they read. No parallel-eligible package this pass — the
dependency is a hard sequencing constraint, not a convenience ordering.

### Backlog riders honored in this pass

- **`BL-0075`** (High, maze dead-end indistinguishable from a true world edge): packaged as
  `IP-1081`→`IP-1082`, the pair that closes it — not `DONE` until `IP-1082` ships and is
  `VERIFIED`.
- **`BL-0068`** (the `GDS-08` tile-art delta this rendering half needed): already resolved
  (2026-07-11); this pass is the implementation package `BL-0068`'s own resolution note named as
  still owed.
