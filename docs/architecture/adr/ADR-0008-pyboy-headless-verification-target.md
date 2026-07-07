# ADR-0008 — PyBoy headless emulator as the verification target, not real hardware

**Status:** Accepted (as-built, mined 2026-07-06)

## Context

`test_rom.py`'s harness drives the built ROM under PyBoy (a headless Python GBC emulator,
[R301](../../research/encyclopedia/R301-pyboy-headless-emulation-api.md)) and asserts on emulated
memory/PPU state. Real-hardware behavior is expected to match but is never itself gated on — no
flash-cart test rig, no second independent emulator cross-check exists in this project. This is
already recorded as strategic assumption **A2** in the
[assumptions register](../strategic-assumptions-register.md): *"PyBoy headless is the
verification target; real-hardware behavior is expected to match but is not a gate,"* with an
explicit trigger condition — *"a credible real-hardware (or second-emulator) divergence report; or
a release is planned for physical flash carts."*

## Decision

Keep PyBoy headless as the sole automated verification target for the G5 permanent gate ("ROM
must build to exactly 32768 bytes with valid header, full `test_rom.py` suite passes"). Do not add
real-hardware or second-emulator verification speculatively; only add it once A2's stated trigger
condition actually fires.

## Consequences

- Fast, CI-friendly, no physical hardware dependency — verification runs anywhere Python + PyBoy
  run, consistent with this project's toolchain-portability goals
  ([R306](../../research/encyclopedia/R306-toolchain-portability.md)).
- Carries real, accepted risk: a PyBoy emulation inaccuracy could pass a test that would fail on
  real hardware, and this project would not currently detect that divergence. This risk is
  explicitly accepted (not hidden) via A2's trigger-condition framing rather than left as an
  unstated gap.
- This ADR does not resolve — and should not be read as resolving — the separate, more urgent
  problem that `test_rom.py`'s T2–T10 suites currently test pre-rewrite (Bunny Garden Adventure)
  semantics against the shipped Bunny Quest code, breaking G5 today (`BL-0006`/`BL-0008`). That is
  a test-content staleness problem; this ADR is about the *choice of verification target*, which
  remains sound independent of that separate defect.
