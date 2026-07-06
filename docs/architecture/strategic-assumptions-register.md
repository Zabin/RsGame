# Strategic Assumptions Register

- **Owned by:** `01-vision` skill · **Created:** 2026-07-06 (bootstrap baseline, v1.0)
- The explicit assumptions [MSTR-001](../master/MSTR-001-program-vision.md) rests on. Each row
  carries a **trigger**: the observable condition under which the assumption stops holding. A
  fired trigger is not silently absorbed — the row returns to `00-pipeline-manager` for
  re-triage, and any resulting vision change runs through `01-vision` with its blast radius
  enumerated.

| ID | Assumption | Trigger ("revisit when…") | Downstream artifacts most exposed |
|---|---|---|---|
| A1 | **32KB single-bank ROM suffices** for all planned content — no MBC bank switching needed. | A planned feature's byte cost cannot fit the GDS-07 section budget even after content trimming. | GDS-02/03/07, an ADR on MBC strategy, every IP touching ROM layout |
| A2 | **PyBoy headless is the verification target**; real-hardware behavior is expected to match but is not a gate. | A credible real-hardware (or second-emulator) divergence report; or a release is planned for physical flash carts. | G5 gate definition, R301/R305/R306 research, `test_rom.py` harness, GDS-02 |
| A3 | **The modular Python assembler chain is the build strategy** — no RGBDS/external toolchain; `gbc_lib.py` grows as needed. (Reaffirmed by the BL-0004 decision, 2026-07-06.) | A needed capability (e.g. bank switching, complex linking) proves uneconomical to add to `gbc_lib.py`. | GDS-03/09, an ADR, `build_rom.py`, every stage-08 package |
| A4 | **This repository hosts exactly one game**; the pipeline and docs tree serve it alone. | A second ROM/game is proposed for this repo. | MSTR-001 §1, docs tree layout, ROADMAP |
| A5 | **Audience is casual/all-ages short-session play**; content stays family-friendly and non-violent; no fail states. *(Bootstrap-derived — the shipped game implies but nowhere states this; recorded here rather than blocking on a user interview.)* | The project owner directs a tonal, difficulty, or audience shift. | MSTR-001 §2/§3 C6, R201/R206 research, every content FS |
| A6 | **The shipped v2.1 behavior set is the intended design** — its two recorded defects (BL-0001 map-hearts addresses, BL-0003 un-gated VRAM score writes) are bugs, not behavior to preserve. | Stage-04 baselining finds shipped behavior that contradicts an intended-design statement; or the owner marks other v2.1 behavior as unintended. | GDS-01/05, `docs/requirements/`, the as-built FS set |
| A7 | **English-only text** on the existing Latin font tiles (0x40–0x61). | A localization request, or text content exceeding the font tile budget. | GDS-08, `tiles.py` font range, content FS specs |

**Retired assumptions:** none yet. Retire by striking the row's status, never by deleting the row.
