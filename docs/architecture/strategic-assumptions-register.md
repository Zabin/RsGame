# Strategic Assumptions Register

- **Owned by:** `01-vision` skill · **Created:** 2026-07-06 (bootstrap baseline, v1.0) ·
  **Revised:** 2026-07-06 (A1/A6 corrected + A8 added, same day — see
  [MSTR-001 §8](../master/MSTR-001-program-vision.md#8-vision-amendment-log))
- The explicit assumptions [MSTR-001](../master/MSTR-001-program-vision.md) rests on. Each row
  carries a **trigger**: the observable condition under which the assumption stops holding. A
  fired trigger is not silently absorbed — the row returns to `00-pipeline-manager` for
  re-triage, and any resulting vision change runs through `01-vision` with its blast radius
  enumerated.

| ID | Assumption | Trigger ("revisit when…") | Downstream artifacts most exposed |
|---|---|---|---|
| A1 | **A single ROM bank suffices for now** — no MBC bank switching needed *yet* (~9.6KB headroom remains at v2.0: 23148/32768 bytes used). **Revised:** this is no longer expected to hold indefinitely — MSTR-001 C7's Zelda/Pokémon-scale world target makes outgrowing one bank an anticipated, planned-for future step, not a risk to avoid. | *(lowered bar)* A specific planned feature's byte cost cannot fit the remaining headroom; **or** GDS-01/03 conclude the C7 world-scale target requires more zones than one bank can hold — whichever comes first, expect this sooner than "never." | GDS-01/02/03/07, an ADR on MBC strategy (should be authored proactively, not reactively), every IP touching ROM layout |
| A2 | **PyBoy headless is the verification target**; real-hardware behavior is expected to match but is not a gate. | A credible real-hardware (or second-emulator) divergence report; or a release is planned for physical flash carts. | G5 gate definition, R301/R305/R306 research, `test_rom.py` harness, GDS-02 |
| A3 | **The modular Python assembler chain is the build strategy** — no RGBDS/external toolchain; `gbc_lib.py` grows as needed. (Reaffirmed by the BL-0004 decision, 2026-07-06.) | A needed capability (e.g. bank switching, complex linking) proves uneconomical to add to `gbc_lib.py`. | GDS-03/09, an ADR, `build_rom.py`, every stage-08 package |
| A4 | **This repository hosts exactly one game** (**Bunny Quest**, formerly documented under the stale name "Bunny Garden Adventure" — see MSTR-001 §8); the pipeline and docs tree serve it alone. Growing that one game's world (C7) is not "a second game." | A second, genuinely distinct ROM/game is proposed for this repo. | MSTR-001 §1, docs tree layout, ROADMAP |
| A5 | **Audience is casual/all-ages short-session play**; content stays family-friendly and non-violent; no fail states — expected to hold even as the world scales up per C7 (bigger ≠ harder/longer). *(Bootstrap-derived — the shipped game implies but nowhere states this; recorded here rather than blocking on a user interview.)* | The project owner directs a tonal, difficulty, or audience shift. | MSTR-001 §2/§3 C6, R201/R206 research, every content FS |
| A6 | **The shipped Bunny Quest behavior is the intended design** (9 zones, 9-carrot win condition, star/flower scoring). **Revised:** the original wording ("v2.1," BL-0001/BL-0003) described the *pre-rewrite* game and is retracted — those two backlog entries need re-verification against the current code before being treated as still-valid bug reports (see MSTR-001 §8). | Stage-04 baselining finds shipped behavior that contradicts an intended-design statement; or the owner marks specific current behavior as unintended. | GDS-01/05, `docs/requirements/`, the as-built FS set |
| A7 | **English-only text** on the existing Latin font tiles. | A localization request, or text content exceeding the font tile budget. | GDS-08, `tiles.py` font range, content FS specs |
| A8 *(new)* | **The working docs/tests will be brought back into sync with shipped code** before requirements-baselining (stage 04) relies on them. Right now this assumption is **known false** for `test_rom.py`, `Claude.md`, `memory.md`, `README.md` (all describe the pre-rewrite game) — recorded as a standing, already-fired trigger rather than a healthy assumption, so it isn't lost between now and the remediation pass. | *(already fired — see note)* Resolves when a documentation/test-refresh package lands, or when GDS-04/05 confirm they derived requirements from direct code inspection rather than these stale files. | `test_rom.py` (G5 gate), `Claude.md`, `memory.md`, `README.md`, `docs/pipeline/backlog.md` |

**Retired assumptions:** none yet. Retire by striking the row's status, never by deleting the row.
