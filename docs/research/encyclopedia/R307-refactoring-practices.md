# R307 — Refactoring Practices: Behavior-Preserving Code & Meaning-Preserving Docs

- **Document ID:** R307 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R302 (the codegen module boundaries a refactor must respect), R304 (why the
  header/size checks survive any true refactor), R305 (the characterization role `test_rom.py`
  already plays), R306 (precedent: the one prior structure-level toolchain change, BL-0005)
- **Referenced By:** the `08-refactoring` skill (its equivalence discipline is this topic's §5),
  `07-implementation-planning` (the `IP-8xx0` equivalence-contract field), `00-pipeline-manager`
  (its refactoring scheduling conditions cite this topic)
- **Produces:** the evidence standard every `IP-8xx0` refactoring package must meet
- **Feature Mapping:** *(none — this topic's consumers are pipeline skills and `IP-8xx0`
  packages, not Feature Specifications)*
- **Related Topics:** R302, R304, R305, R306

## Purpose

Ground the pipeline's refactoring stage (`08-refactoring`, `IP-8xx0` packages) in cited practice:
what makes a change a *refactoring* rather than a rewrite, what evidence proves behavior was
preserved in **this** toolchain specifically, and what the equivalent discipline is for the
documentation tree, whose "behavior" is its meaning, statuses, and link graph.

### Sources

- M. Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed., Addison-Wesley 2018,
  ISBN 978-0134757599; companion site refactoring.com — *needs fetch-verification* (site blocked
  by this environment's network policy, 2026-07-13; the definition cited is the book's own
  well-established one).
- M. Feathers, *Working Effectively with Legacy Code*, Prentice Hall 2004, ISBN 978-0131177055,
  ch. 13 (characterization tests) — *needs fetch-verification* (same policy block).

## Scope

Code refactoring across the repo-root modules (`asm_game.py` 2048 lines, `test_rom.py` 2284,
`tiles.py` 1030, `tilemaps.py` 463, `gbc_lib.py` 225, `worldgen.py` 227, `build_rom.py` 195,
`music.py` 57 — line counts from `wc -l`, 2026-07-13) and documentation refactoring across
`docs/` (indexes, ID-bearing artifacts, the cross-link graph). Out of scope: *when* to refactor
(the manager's scheduling conditions) and *authorization* (G3) — those are pipeline governance,
not research.

## Concepts

**Refactoring is defined by what does not change.** Fowler's definition: a change made to the
internal structure of software to make it easier to understand and cheaper to modify **without
changing its observable behavior** (Fowler 2018, ch. 1 — needs fetch-verification). The practical
consequence he draws is the "two hats" rule: adding behavior and restructuring are separate
activities never worn at once — which is exactly why an `IP-8xx0` that "also fixes" a bug has
destroyed its own proof: the diff can no longer be read as structure-only.

**Characterization tests pin current behavior, not intended behavior.** Feathers (2004, ch. 13 —
needs fetch-verification) defines a characterization test as one that documents what the system
*actually does now*, written specifically so legacy code can be restructured against a fixed
reference. This repo already owns a 246-check characterization suite: `test_rom.py` asserts
observed WRAM values, tilemap bytes, and screenshots of the shipped ROM (R305) — for refactoring
purposes its value is precisely that it was **not** written with the refactor in mind.

**The golden master / approval pattern: compare whole outputs, not properties.** Where a system
emits a complete artifact, the strongest characterization is to capture the artifact before the
change and diff it after — the "golden master" technique long used for legacy systems whose
outputs are deterministic (Feathers 2004; also the premise of approval-testing tools — needs
fetch-verification). This toolchain is the ideal case: the entire observable product is one
32768-byte file, so the golden master is the ROM itself and the diff is a hash comparison.

**Reproducible builds make the hash comparison valid.** A build is reproducible when the same
source always yields a **bit-for-bit identical** artifact (reproducible-builds.org, "Definition"
— needs fetch-verification, same policy block). Only a deterministic build lets "same hash" mean
"same behavior"; §4 proves this build qualifies by local experiment, which is why byte-identity
is the *default* equivalence contract rather than an aspiration.

**Docs-as-code: documentation earns the same discipline.** The docs-as-code approach (Write the
Docs community guide — needs fetch-verification) treats documentation like source: versioned,
reviewed, and mechanically checked (notably link integrity). Its refactoring analogue: the
"observable behavior" of a doc tree is its **meaning** (every claim, decision, and status token),
its **IDs** (`BL-`/`FR-`/`IP-`/`R-`… — this tree's foreign keys), and its **link graph**. A doc
refactor preserves all three; renames publish a migration map so stale references remain
resolvable, the doc-tree equivalent of a deprecation alias.

### Sources

- Fowler 2018 (above); Feathers 2004 (above) — both *needs fetch-verification*.
- reproducible-builds.org, "Definition" — *needs fetch-verification* (HTTP 403 via session proxy,
  2026-07-13).
- Write the Docs, "Docs as Code" guide (writethedocs.org/guide/docs-as-code/) — *needs
  fetch-verification* (same).
- Local experiment, this repo — §4 below (Tier-A, command + output recorded).

## Operational Context — this toolchain's equivalence oracle, proven locally

**The build is deterministic (local experiment, 2026-07-13, Python 3.11.15).** Two builds run
with different `PYTHONHASHSEED` values (the classic source of Python nondeterminism via hash
ordering) produced byte-identical output:

```
$ PYTHONHASHSEED=1  python3 build_rom.py a.gbc
$ PYTHONHASHSEED=99 python3 build_rom.py b.gbc
$ sha256sum a.gbc b.gbc
34d32ef4da4e1731556303e4f1d8780f07cffe376ba6c8b564f769e8881a66f4  a.gbc
34d32ef4da4e1731556303e4f1d8780f07cffe376ba6c8b564f769e8881a66f4  b.gbc
```

Both 32768 bytes; the build log's section layout (`Total used: 0x63C8 (25544 bytes of 32768)`)
was identical across runs. Determinism holds because the pipeline is a single-pass emitter over
insertion-ordered structures (R302): Python `dict`s preserve insertion order (guaranteed since
CPython 3.7), labels resolve by explicit patch-point dicts rather than hash iteration, and no
timestamps or absolute paths are embedded in the ROM (`build_rom.py:194` takes the output path
from `argv[1]`, defaulting to the repo-relative `BunnyQuest.gbc` since BL-0005's remediation —
direct code read).

**What the ROM hash cannot see.** Byte-identity covers everything the *player* can observe, but
a refactor of `test_rom.py` or `build_rom.py` changes files the hash never touches. There the
characterization is the suite's own output: same 246 checks (count via `grep -c "check("`,
2026-07-13, minus the `def check` line), same names, same pass/fail set, and `build_rom.py`'s
printed section layout unchanged. A refactor that renames or drops a check has weakened the
characterization and must say so in its package, or it fails review.

**When a refactor legitimately moves bytes.** Reordering emitted sections or renaming a label
that feeds an address table produces a different-but-equivalent ROM. That is the *enumerated
predicted deltas* case: determinism still guarantees the diff is stable and inspectable
(`cmp -l old.gbc new.gbc` lists exactly the changed offsets), so the package must predict each
delta region and justify it — anything unpredicted is a failed refactor, not a footnote.

**The doc tree's mechanical invariants.** 100+ files under `docs/` cross-reference by relative
link and by ID; INDEX files and `ROADMAP.md` duplicate status tokens that reconciliation (the
manager's Step 1) treats as ledgers. So a doc refactor has three checkable invariants: zero
dangling relative links tree-wide (inbound links break silently — the sweep must cover the whole
tree, not just edited files), an unchanged multiset of status tokens, and every ID either stable
or mapped old→new in a migration map.

### Sources

- Local experiment above (Tier-A; scratchpad, 2026-07-13).
- Direct code reads: `build_rom.py:77,135,194`; `test_rom.py:88` (`check()`); counts as noted.
- CPython documentation, "Dictionaries preserve insertion order" (language guarantee since 3.7)
  — *needs fetch-verification* (docs.python.org blocked by the same policy; the guarantee is
  also stated in the CPython 3.7 changelog).

## Implementation Guidance — do/don't for `IP-8xx0` work

- **DO capture the baseline before the first edit:** built-ROM SHA-256, full `test_rom.py`
  output (check count + names), `build_rom.py`'s printed section layout, and — for doc work —
  the link set and status-token inventory of the affected files. An uncaptured baseline makes
  the after-state uninterpretable.
- **DO default the equivalence contract to byte-identical ROM.** §4 proves the build supports
  it. Accept enumerated predicted deltas only when the package names each expected offset region
  and why it is behavior-neutral; verify with `cmp -l`.
- **DO refactor in steps that keep the tree buildable,** re-running the two G5 gates
  (`python3 build_rom.py <out>` → 32768 bytes; `python3 test_rom.py` → full suite) between
  steps where practical — Fowler's small-steps discipline exists to make the failing step
  obvious and cheap to revert.
- **DO sweep the whole `docs/` tree for inbound links** after any move/rename, and write the
  old→new migration map where the package says. Grep for the *old* name after the change: the
  correct result is zero hits outside the migration map itself.
- **DON'T mix behavior change in — not even a bug fix.** A bug found mid-refactor is filed
  (intake → backlog), never fixed inline; one behavior edit turns the whole diff from
  "provably equivalent" into "manually re-reviewable" (the two-hats rule).
- **DON'T weaken the characterization to make it pass.** Renaming, loosening, or deleting a
  `test_rom.py` check during a refactor inverts the tool's purpose; any check change must be
  named in the package as part of its contract.
- **DON'T trust the suite alone for `test_rom.py`'s own refactors** — the suite can't
  characterize itself. There the invariant is the check inventory (same 246 names, same
  assertions against the same unchanged ROM hash) plus a diff review showing structure-only
  hunks.
- **DON'T edit meaning while moving prose.** Doc refactors copy statuses and decisions
  character-for-character; permitted editorial normalizations (heading case, wrapping) must be
  listed in the package, or the diff review treats them as meaning drift.

### Sources

- §3/§4 sources; G5 commands per `run-bunnygarden` and `.claude/skills/README.md`.

## Feature Mapping

*(None. Consumers are the `08-refactoring` skill, `07-implementation-planning`'s `IP-8xx0`
equivalence contracts, and `00-pipeline-manager`'s scheduling conditions.)*

## Related Topics

R302 (module boundaries and patch-point conventions that make the build deterministic) · R304
(header/size checks — invariant under any true refactor) · R305 (the characterization suite's
design and its known gaps) · R306 (BL-0005's path remediation — the closest prior
structure-level change, and the precedent for stating exact lines and exact replacements).
