# R306 — Toolchain Portability

- **Document ID:** R306 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R301 (PyBoy's own path-relative-to-ROM `.ram` behavior)
- **Referenced By:** R307 (BL-0005's remediation is the precedent structure-level toolchain change) — **this topic directly grounds BL-0005/BL-0008's path fix**
- **Produces:** grounds the remediation `build_rom.py`/`test_rom.py` need for portable execution
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R301

## Purpose

Concrete, code-cited guidance for fixing the hardcoded-path problem backlog `BL-0005` (widened by
`BL-0008`) already identifies — not general portability philosophy, but the exact lines to change
and what to change them to.

## Scope

The current hardcoded paths in `build_rom.py`/`test_rom.py`, why they break outside one specific
prior environment, and a concrete repo-relative replacement scheme.

## Concepts

Portable build/test tooling should resolve output locations **relative to the repository** (or
via explicit, overridable configuration) rather than hardcoding an absolute path that only existed
in one prior working environment. The standard low-risk pattern for a small Python script: default
to a path computed from `__file__`'s directory (or `pathlib.Path(__file__).resolve().parent`), and
allow override via a command-line argument or environment variable — exactly the `argv[1]`
override `build_rom.py` already partially implements for its output path, just pointed at the
wrong default.

## Operational Context — the exact defects (confirmed by direct code read, 2026-07-06)

`build_rom.py`'s `if __name__ == '__main__':` block: `out = sys.argv[1] if len(sys.argv) > 1 else
'/mnt/user-data/outputs/BunnyGarden.gbc'` — an absolute path specific to one prior session's
filesystem layout, **and** the stale pre-rewrite ROM filename (should be `BunnyQuest.gbc` per
`build_rom.py`'s own `set_header("BUNNYQUEST", ...)` call — R109).

`test_rom.py` hardcodes four separate absolute paths, none repo-relative:
- `ROM_PATH = '/mnt/user-data/outputs/BunnyGarden.gbc'` (line 21) — same stale-name problem, and
  the *only* path a test run actually reads the ROM from, so a portability fix here is the one
  that matters most.
- `RAM_PATH = '/mnt/user-data/outputs/BunnyGarden.gbc.ram'` (line 22, with a comment "PyBoy uses
  .gbc.ram" — correctly noting PyBoy's own convention of a `.ram` file next to the ROM path,
  R301) — must track `ROM_PATH` exactly (same directory, same base filename + `.ram`), not be
  independently hardcoded, or the two will silently diverge the next time either is edited.
- `SHOT_DIR = '/home/claude/bunnygarden/test_shots'` (line 23) — an entirely different absolute
  path root than `ROM_PATH`'s, for screenshot output.
- The results-file write at line 492: `open('/home/claude/bunnygarden/test_results.txt', 'w')` —
  a third hardcoded absolute location, not even using the `SHOT_DIR` constant it could share a
  root with.

None of these four paths currently agree on a root, and none are relative to the repository or
overridable — which is precisely why `run-bunnygarden`'s SKILL.md currently documents a
`mkdir -p /mnt/user-data/outputs /home/claude/bunnygarden` workaround rather than a real fix.

## Implementation Guidance — the concrete remediation shape

- **Compute a single repo-relative base directory** in both files, e.g.
  `BASE = pathlib.Path(__file__).resolve().parent` (both scripts live at the repo root today, so
  this is simply the repo root) — then derive every output path from it: `BASE / 'BunnyQuest.gbc'`
  for the ROM, `BASE / 'BunnyQuest.gbc.ram'` for the save file, `BASE / 'test_shots'` for
  screenshots, `BASE / 'test_results.txt'` for the results file. This also fixes the stale
  `BunnyGarden` filename in the same change (both `BL-0005` and part of `BL-0006`/`BL-0007`'s
  wider "stale name" theme trace back to this exact line).
- **Preserve the existing `argv[1]` override in `build_rom.py`** — just fix its *default*, don't
  remove the override capability.
- **Add an equivalent override to `test_rom.py`** (e.g. an environment variable or `argv[1]`) if
  a future CI environment needs a different output location — not required to fix `BL-0005` itself,
  but cheap to add in the same pass and consistent with `build_rom.py`'s existing convention.
- **`RAM_PATH` must be derived from `ROM_PATH`** (`ROM_PATH` with `.gbc` replaced by `.gbc.ram`, or
  simply `ROM_PATH + '.ram'` if the ROM path already ends `.gbc`) rather than hardcoded
  independently — this removes the single largest risk of the two silently diverging again.
- **This is a `07-implementation-planning` → `08-code-implementation` remediation package**
  (part of `BL-0008`'s umbrella) — small, mechanical, and unblocks every future stage-08/09 run's
  ability to actually execute the G5 permanent gates in this (or any other) environment.

## Feature Mapping

*(No `FS-xxx` authored yet — this topic's primary consumer is expected to be a `07-implementation-
planning` package for BL-0005/BL-0008, not a Feature Specification.)*

## Related Topics

R301 (PyBoy's own path-relative-to-ROM `.ram` file convention, which this topic's `RAM_PATH`
derivation must stay consistent with).
