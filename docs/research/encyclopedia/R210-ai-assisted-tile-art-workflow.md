# R210 — AI/Agent-Assisted Tile-Art Generation & Iteration Workflow

- **Document ID:** R210 · **Version:** 1.0 · **Status:** ✅
- **Dependencies:** R209 (the craft technique this workflow must produce), R303 (2bpp encoding),
  R104 (palette budget), R301 (the screenshot tooling this workflow's review step uses)
- **Referenced By:** none yet
- **Produces:** grounds how `08-content-authoring` (or any future agent session) should actually
  produce new `tiles.py` art
- **Feature Mapping:** *(none yet)*
- **Related Topics:** R209, R303, R104, R301, R105

## Purpose

**Filed per backlog `BL-0013`** (project owner's direct request). This topic is the
workflow/process half of that request: a concrete, structured, repeatable loop for an AI agent
(Claude, in a coding-agent role, not a separate image-generation product) to design, encode,
render, review, and revise tile art *for this specific pipeline* — not generic "AI art" advice.

## Scope

Why this project's actual toolchain shapes the workflow (no image-import path exists today), the
concrete design→encode→render→review→revise loop, and budget/constraint checks that must run
before any new tile is committed.

## Concepts — the general AI-assisted pixel-art landscape, and why it doesn't transfer directly

Generic AI-assisted pixel-art workflows (image-generation models, LoRAs tuned for "pixel art"
styles) typically follow: generate several raster candidate images from a text prompt
constrained toward the target era/resolution, pick the best, then hand-refine in a pixel editor
to enforce an exact palette and pixel grid — because raw model output is rarely pixel-perfect or
palette-exact even when prompted for it.[^1] Generated art is conventionally produced small and
then scaled with **nearest-neighbor** (never bilinear/smooth) resampling to avoid destroying the
hard pixel edges.[^1]

**This project's toolchain has no raster-image-import path at all.** `tiles.py` (confirmed by
direct code read) defines every tile as a literal Python `pix` array of small integers (0–3, one
per pixel) passed to `enc()` — there is no code anywhere in the pipeline that reads a PNG, sprite
sheet, or any external image format and converts it into this array form. This means the generic
"generate a PNG with an AI tool, import it" workflow **is not currently executable in this
project** — it would require a new, unbuilt conversion step (a script quantizing an input image
to a 4-color palette and emitting the resulting `pix` array), which does not exist today and is
its own scoped tooling gap (flag as a Candidate research/implementation item if ever pursued, not
assumed available).

## Operational Context — the workflow that *is* available today

An AI coding agent (this project's own operating mode) can already author `pix` arrays directly
as structured, reviewable text — which is a genuinely good fit for an LLM-driven workflow, since
the "image" *is* a small, explicit, machine-readable grid rather than an opaque raster the agent
would have to infer pixel values from. The available loop, grounded in this project's real tools:

1. **Design the shape as an explicit 8×8 (or 8×16-paired, R105) grid of small integers**
   (0 = transparent/background, 1–3 = the tile's other palette slots), following R209's
   silhouette-first, budgeted-color-per-part discipline — write this grid out in the chat/response
   as a literal, human-readable table before touching `tiles.py`, so a human (or the agent itself,
   re-reading it) can review the *shape* independent of the code.
2. **Check budget constraints before committing:** a free tile-index slot in the 256-tile space
   (`TL_*` constants, R303) and, if the tile needs a new/different palette, that an 8-BG/8-OBJ
   palette slot is actually available (R104/`BL-0009` — likely **not** available without reusing
   an existing zone's palette, at the current 9-zone count). A design that fails either check
   needs a decision (reuse an index/palette, or defer) *before* writing code, not after.
3. **Encode via the existing `enc()` helper** — never hand-pack bytes (R209/R303) — and register
   the new tile in `build_tile_data()` at the checked-available index.
4. **Render and review visually, not just by reading the code.** Build the ROM and drive it via
   `run-bunnygarden`'s PyBoy screenshot capability (R301) to see the tile as it actually renders
   in-context (correct palette applied, correct scale, next to its neighboring tiles) — a `pix`
   array that looks right as a table of digits can still look wrong once colored and placed; this
   step is not optional.
5. **Iterate from the screenshot, not from a second guess.** If the rendered tile doesn't read
   well, revise the specific pixel-grid cells that are the actual problem (informed by what the
   screenshot shows — a silhouette issue, a color-budget issue, a contrast issue against its
   neighbors) and re-render; treat this as a tight, cheap loop (steps 3–4 are fast) rather than
   trying to perfect the grid mentally before ever rendering it once.
6. **Only then treat the tile as content-review-ready** for `09-content-review`'s own visual
   judgment pass (which checks against design intent/spec, not just "does it render").

## Implementation Guidance

- **Always externalize the pixel grid as reviewable text before writing `tiles.py` code** — this
  is the concrete practice that makes this workflow "structured and iterable" rather than
  one-shot: a design that's wrong is cheap to fix at the grid-review stage, expensive to
  rediscover after it's already encoded, built, and screenshotted.
- **Never skip the render-and-look step.** An LLM reasoning about a `pix` array's color indices
  can verify the *shape* correctly but cannot reliably verify how the encoded, palette-applied
  result actually looks without rendering it — this is exactly why R301's screenshot capability
  is load-bearing for this workflow, not a nice-to-have.
- **Treat the "no image-import path" gap as a real, current limitation, not a workaround to
  invent ad hoc.** If a future task specifically wants to start from an external reference image
  (a scanned sketch, an AI-generated raster mockup), that is new tooling scope (a quantize-to-
  palette-and-grid converter) — route it through `00-intake` as a tooling feature request rather
  than hand-transcribing an image pixel-by-pixel as a one-off.
- **Budget-check before designing in detail, not after.** Confirming a free tile index and an
  available (or deliberately reused) palette slot takes seconds against the current `tiles.py`/
  `build_rom.py` state and prevents discovering a conflict after a design is already finished.
- **This workflow is stage-08 (`08-content-authoring`) execution scope**, not stage-02 research —
  this topic grounds *how* that skill should work; it doesn't perform the work itself.

## Feature Mapping

*(No `FS-xxx` authored yet.)*

## Related Topics

R209 (the craft technique this workflow's output must satisfy) · R303 (the encoding format the
final `pix` array feeds into) · R104 (the palette-budget check step) · R301 (the screenshot
tooling the render-and-review step depends on) · R105 (8×16 OBJ tile-pairing, relevant when the
subject is a sprite rather than a single BG tile).
