# RsGame — Bunny Garden Adventure

A complete Game Boy Color game (32KB ROM, battery save) built entirely by a Python assembler
pipeline and verified headlessly with PyBoy (88/88 ROM tests).

- **Play/build/test:** see [`.claude/skills/run-bunnygarden/SKILL.md`](.claude/skills/run-bunnygarden/SKILL.md)
  — `python3 build_rom.py <out.gbc>` then `python3 test_rom.py`.
- **Developer quick-reference:** [`Claude.md`](Claude.md) (architecture, ROM/WRAM/SRAM maps,
  how-to-change-things) and [`memory.md`](memory.md) (tile/palette/collectible tables, debug log).
- **Development pipeline:** [`.claude/skills/README.md`](.claude/skills/README.md) — a staged
  documentation-driven-development pipeline (vision → research → architecture → requirements →
  features → packages → verification → release). Drive it with the `00-pipeline-manager` skill;
  the bootstrap run-book is [`docs/pipeline/BOOTSTRAP.md`](docs/pipeline/BOOTSTRAP.md).
- **Docs:** [`docs/INDEX.md`](docs/INDEX.md) · **Status tracker:** [`ROADMAP.md`](ROADMAP.md).
