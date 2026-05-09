# RsGame Developer Workflow

Complete guide to the automated testing, building, and preview generation pipeline.

---

## Overview

The RsGame project uses **automated pre-commit hooks** and **Makefile targets** to ensure every change is tested and the ROM stays in sync with source code.

```
Your Code Change
    ↓
git commit
    ↓
Pre-Commit Hook Triggers:
    ├─ pytest (tests must pass)
    ├─ python build_rom.py (rebuild ROM)
    ├─ python tile_preview.py --all (refresh tile graphics)
    ├─ python screen_preview.py --all (refresh screen layouts)
    ├─ python music_preview.py (refresh music visualization)
    └─ git add (stage updated files)
    ↓
Commit Succeeds with Fresh ROM + Previews
    ↓
git push
    ↓
GitHub Actions CI:
    ├─ Lint (code quality)
    ├─ Test (unit + integration)
    └─ Build validation
    ↓
Tests Pass → Green Status
```

---

## Makefile Commands

All common tasks are available via `make`:

```bash
make help              # Show all available commands

make build             # Build ROM to ./BunnyGarden.gbc
make test              # Run all tests (unit + integration)
make test-unit         # Unit tests only (fast, ~0.2s)
make test-integration  # Integration tests (slow, requires PyBoy)

make previews          # Regenerate tiles/screens/music PNGs
make lint              # Code quality checks (Black, Pylint, Flake8)
make clean             # Delete generated files

make all               # Full pipeline: build + test + previews
make install-hooks    # Set up the pre-commit hook (one-time)
```

---

## Typical Developer Workflow

### 1. Edit Source Code
```bash
# Make changes to any of:
#   - tiles.py (tile pixel art)
#   - tilemaps.py (screen layouts)
#   - asm_game.py (game logic)
#   - music.py (melody)
vim tilemaps.py   # e.g., edit forest_screen()
```

### 2. Commit Changes
```bash
git add tilemaps.py
git commit -m "Update forest screen to add more trees"

# Pre-commit hook automatically runs:
# ✓ Tests (must pass or commit aborts)
# ✓ ROM rebuild → BunnyGarden.gbc
# ✓ Preview generation → previews/*.png
# ✓ File staging → git add BunnyGarden.gbc previews/
```

### 3. Push to Remote
```bash
git push origin claude/review-rsgame-main-QPu7z

# GitHub Actions CI validates on next push:
# ✓ Lint checks
# ✓ Tests pass
# ✓ ROM builds & validates
# → Commit shown as green on GitHub
```

### 4. Download Artifact (Optional)
If you want the latest built ROM from CI:
1. Go to https://github.com/Zabin/RsGame/actions
2. Click latest workflow run
3. Download "BunnyGarden.gbc" artifact

---

## Pre-Commit Hook Details

The hook (`.git/hooks/pre-commit`) runs automatically before every commit.

### What It Does
1. **Tests:** Runs `pytest tests/ test_rom.py --tb=short`
   - If tests fail: **Commit aborts**, you must fix errors
   - If tests pass: Continue to step 2

2. **Rebuild ROM:** Runs `python build_rom.py`
   - Compiles to `./BunnyGarden.gbc`
   - If build fails: **Commit aborts**, you must fix errors

3. **Refresh Previews:**
   - `python tile_preview.py --all` (tile grid PNG)
   - `python screen_preview.py --all` (screen layouts PNG)
   - `python music_preview.py` (piano roll PNG)
   - If any fail: Warning printed, but commit continues (non-critical)

4. **Stage Files:**
   - Automatically `git add BunnyGarden.gbc previews/`
   - These files are now included in your commit

### Emergency Bypass
If you need to commit without running the hook (use sparingly):
```bash
git commit --no-verify   # Bypass pre-commit hook
```

---

## Integration Testing in CI/CD

GitHub Actions runs on every push:

### `.github/workflows/test.yml`
- **Python 3.10, 3.11, 3.12**
- Unit tests: `pytest tests/unit`
- Integration tests: `pytest tests/integration`
- Coverage reporting to Codecov

### `.github/workflows/build.yml`
- Builds ROM: `python build_rom.py`
- Validates:
  - ROM size (32KB)
  - Entry point (NOP + JP)
  - Cart type (0x03 or 0x13)
  - ROM sections (code, tiles, palettes present)
- Uploads ROM as artifact (30-day retention)

### `.github/workflows/lint.yml`
- Code quality checks
- Black, Pylint, Flake8
- Pre-commit hooks

---

## Preview Tools

### Tile Preview
Visualizes all tile graphics as a grid.

```bash
python tile_preview.py --all
# Output: previews/tiles_*.png (8 files covering all tiles)
```

### Screen Preview
Visualizes complete screen layouts (32×18 tilemap + attributes).

```bash
python screen_preview.py --all
# Output: previews/screens/*.png (14 screens)
```

### Music Preview
Generates piano roll visualization of the melody.

```bash
python music_preview.py
# Output: previews/music_preview.png (note timeline)
```

---

## Troubleshooting

### "Tests failed. Aborting commit."
Fix the failing test, then retry:
```bash
pytest tests/unit -v --tb=short   # See what failed
vim your_file.py                  # Fix the issue
git add .
git commit -m "Fix test failure"  # Retry commit
```

### "ROM build failed. Aborting commit."
Debug the build:
```bash
python build_rom.py               # See build error
vim build_rom.py                  # Fix issue (likely import or syntax)
git add .
git commit -m "Fix ROM build"     # Retry commit
```

### "PreviewGeneration failed (non-critical)"
This is a warning, not an error. Commit proceeds. But to fix:
```bash
python tile_preview.py --all      # See what failed
# Usually means Pillow/PIL not installed
pip install Pillow
```

### "I accidentally broke tests but committed with --no-verify"
No problem! The GitHub Actions CI will catch it:
1. Push your broken commit
2. CI tests fail (red ❌ on GitHub)
3. Fix the code locally
4. Commit + push again
5. CI passes (green ✅ on GitHub)

---

## Best Practices

1. **Use `make all` to validate locally before committing:**
   ```bash
   make all    # Build + test + previews
   git status  # See what would be committed
   git commit -m "message"
   ```

2. **Keep ROM in sync:** Never manually edit `BunnyGarden.gbc`. It's generated by `build_rom.py` and should always match the source code.

3. **Review previews:** After running `make previews`, check the PNG files in `previews/` to see the visual impact of your changes.

4. **Test frequently:** Use `make test-unit` (fast, ~0.2s) during development, then `make test` before committing.

5. **Commit related changes together:** Don't mix unrelated changes in one commit.

---

## How to Add New Features

### Example: Add a new tile
1. Edit `tile_pixels.py` to define the pixel art (8×8 array)
2. Edit `tiles.py` to add a tile index constant and call `enc()`
3. Edit `tilemaps.py` to use the new tile in a screen
4. Run `make previews` to see the change
5. Verify in `previews/screens/screen_name.png`
6. Commit: `git commit -m "Add new tile: TL_MY_TILE"`
   - Hook rebuilds ROM + previews + auto-stages files

### Example: Modify game logic
1. Edit `asm_game.py` to change game behavior
2. Edit a test in `tests/unit/test_*.py` or `test_rom.py`
3. Run `make test-unit` (should fail first per TDD)
4. Verify the test now passes
5. Commit: `git commit -m "Fix: X behavior"`
   - Hook rebuilds ROM + previews

---

## GitHub Status

The ROM file in GitHub (`BunnyGarden.gbc`) is automatically kept in sync:

- **Every commit:** Pre-commit hook rebuilds the ROM from source
- **Committed to git:** File is tracked alongside source code
- **GitHub CI:** Validates ROM on every push
- **Always current:** GitHub ROM always matches latest code

No manual file synchronization needed—the workflow handles it automatically.

---

## Questions?

See `DEVELOPMENT.md` for detailed architecture notes or `GRAPHICS_PREVIEW.md` for graphics tools reference.
