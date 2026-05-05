# Contributing to Bunny Garden Adventure

Thanks for helping improve Bunny Garden Adventure! This guide covers how to contribute code, report issues, and follow project conventions.

## Code of Conduct

- Be respectful and constructive
- Assume good intent
- Help others learn and grow

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- Text editor or IDE

### Local Setup

```bash
# Clone the repository
git clone https://github.com/your-fork/RsGame.git
cd RsGame

# Create a feature branch (see Branch Naming below)
git checkout -b feature/my-awesome-feature

# Install dependencies for development
pip install pyboy pytest black pylint isort pre-commit

# Install pre-commit hooks (auto-format on commit)
pre-commit install

# Verify setup
python3 build_rom.py     # Should create BunnyGarden.gbc
python3 test_rom.py      # Should run successfully
```

---

## Commit Conventions

Use **conventional commit** format to make history clear and enable automated tooling:

```
[SCOPE] Short description (< 70 chars)

Detailed explanation of changes, if needed.
- Bullet point explaining key change
- Another detail

Fixes: (optional, reference to issue)
```

### Scope Options
- `[BUILD]` — ROM generation, build process (build_rom.py, gbc_lib.py)
- `[GAME]` — Game logic, state machine (asm_game.py)
- `[TILES]` — Tile graphics, pixel art (tiles.py)
- `[LAYOUT]` — Screen layouts, zones (tilemaps.py)
- `[MUSIC]` — Audio, music data (music.py)
- `[TEST]` — Test infrastructure (test_rom.py, CI/CD)
- `[DOCS]` — Documentation (README, guides, comments)
- `[FIX]` — Bug fixes (any module)

### Examples

**Good commit:**
```
[TILES] Add stone path tile variant

Added TL_PATH_STONE tile (0x18) with gray palette (pal 4) for forest paths.
Enables better visual variety and transitions between biomes.

- Pixel art: 8×8 gray stone texture
- Palette: reuses existing palette 4
- Registration: added to build_tile_data()

Fixes: issue #12 (forest path visual repetition)
```

**OK commit:**
```
[LAYOUT] Update forest screen collectible positions

Moved star collectibles closer to player spawn to improve difficulty curve.
```

**Avoid:**
```
Fixed stuff  # ← vague, no scope

update  # ← no context

[BUILD] random refactor  # ← unclear intent
```

### Commit Hygiene
- **One commit per feature** (or very small logical grouping)
- **Atomic commits** — Each commit should be independently buildable/testable
- **Descriptive messages** — Future maintainers (including you!) will thank you
- **No merge commits** — Rebase before pushing to keep history linear

---

## Branch Naming

Use descriptive branch names:
```
feature/add-npc-dialog          # New feature
fix/map-hearts-address          # Bug fix
docs/add-music-guide            # Documentation
refactor/simplify-tile-encoding # Refactoring
test/add-collectible-tests      # Tests
perf/optimize-rom-build         # Performance
chore/update-dependencies       # Maintenance
```

**NOT:**
```
my-work               # Unclear
fix-everything        # Too broad
test123               # Meaningless
```

---

## Code Style

The project uses automated code formatting and linting. **Pre-commit hooks enforce this automatically.**

### Formatting (Black)
- 100 character line limit
- 4-space indentation
- Enforced automatically via pre-commit

```python
# Good
def update_player(rom, x, y):
    rom.LD_A_n(x)
    rom.LD_HL_nn(PLAYER_X)
    rom.LD_HL_A()
    return rom

# Still good (Black will reformat, but same result)
def update_player(rom,x,y):
  rom.LD_A_n(x);rom.LD_HL_nn(PLAYER_X);rom.LD_HL_A()
```

### Linting (Pylint)
- Target score: **8.0+**
- Catch undefined variables, unused imports, etc.
- Run manually: `pylint src/`

### Imports (isort)
- Automatic grouping and ordering
- Alphabetical within groups
- Enforced via pre-commit

```python
# Correct order
import sys
from pathlib import Path

from gbc_lib import ROM
from tiles import build_tile_data

import pytest  # This will be auto-sorted
```

### Comments & Documentation
- **No docstrings** (unless complex algorithm)
- **Short comments only** (if WHY isn't obvious from code)
- **Module docstring** (file purpose, 1-2 lines)

```python
# Bad
def enc(pix):
    """Encodes pixels to 2bpp format."""  # Obvious from name
    # This loop iterates through rows
    for row in pix:  # For each row...
        ...

# Good
def enc(pix):
    """8x8 pixel array (0-3) to 16-byte 2bpp Game Boy format."""
    # Split per-pixel color bits across two bitplanes (GBC hardware requirement)
    out = []
    for row in pix:
        p0 = p1 = 0
        for b, c in enumerate(row):
            if c & 1: p0 |= 0x80 >> b
            if c & 2: p1 |= 0x80 >> b
        out += [p0, p1]
    return out
```

---

## Pull Request Process

### Before Opening a PR
1. **Create a feature branch:** `git checkout -b feature/description`
2. **Make changes** and commit with conventional commits
3. **Run tests locally:**
   ```bash
   python3 build_rom.py           # Verify ROM builds
   python3 test_rom.py            # Run emulation tests
   black . && isort . && pylint   # Check style (pre-commit will do this)
   ```
4. **Push to your fork:** `git push origin feature/description`

### Opening the PR
1. Go to GitHub and create a PR against `main`
2. Use this template:

```markdown
## Description
Brief summary of changes.

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring

## How to Test
Steps to verify the change works:
1. Build ROM: `python3 build_rom.py`
2. Play in emulator
3. Check [specific behavior]

## Checklist
- [ ] Code follows style guidelines (black, pylint)
- [ ] All tests pass locally
- [ ] ROM builds successfully
- [ ] Commits use conventional format
- [ ] Documentation updated (if needed)
```

### PR Requirements
✅ **Must pass before merge:**
- Build validation (ROM builds, size OK)
- Test pass (emulation tests)
- Linting passes (black, pylint)
- Pre-commit hooks clean

✅ **Should include:**
- Clear description of what changed
- Why the change was needed
- Test plan (manual testing instructions)

✅ **Nice to have:**
- Link to related issue
- Screenshots of visual changes
- Performance impact (if relevant)

### Review Process
1. Maintainer reviews code and tests locally
2. May request changes ("Code review feedback")
3. Author addresses feedback with new commits (don't amend/rebase)
4. Maintainer approves when satisfied
5. Merge when all checks pass

---

## Reporting Issues

### Bug Report Template
```markdown
## Bug Description
What is the unexpected behavior?

## Steps to Reproduce
1. Build ROM: `python3 build_rom.py`
2. Open in emulator [PyBoy/BGB/etc.]
3. Navigate to [location]
4. Perform action [X]

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- Emulator: PyBoy 2.7.0 (or real hardware)
- Python: 3.10+
- OS: Linux/Mac/Windows

## Screenshots
[If visual issue, attach screenshot]
```

### Feature Request Template
```markdown
## Feature Description
What would you like to add?

## Use Case
Why is this useful?

## Proposed Implementation
How might this work? (optional)

## Related Issues
[Any linked issues]
```

---

## Development Workflow

### Typical Task: Add a New Tile

1. **Create branch:**
   ```bash
   git checkout -b feature/add-stone-path-tile
   ```

2. **Make changes:**
   - Edit `tiles.py`: add `def stone_path()` and `TL_STONE_PATH = 0x18`
   - Register in `build_tile_data()`
   - Edit `tilemaps.py` to use the new tile

3. **Test locally:**
   ```bash
   python3 build_rom.py
   python3 test_rom.py
   ```

4. **Commit:**
   ```bash
   git add tiles.py tilemaps.py
   git commit -m "[TILES] Add stone path tile for forest paths

   - New tile TL_STONE_PATH (0x18) with gray texture
   - Palette 4 (gray variants)
   - Used in forest_screen() for path variation
   
   Improves visual consistency in forest zone."
   ```

5. **Push and PR:**
   ```bash
   git push origin feature/add-stone-path-tile
   # Open PR on GitHub
   ```

---

## Performance & ROM Size

**ROM Budget: 32KB total**

Current usage:
- Game code: ~6.5 KB
- Tile data: 4 KB
- Palettes: 128 bytes
- Music: ~1 KB
- Screens: ~8 KB
- Collectibles: ~0.5 KB

**Remaining: ~12 KB** for future features

### Before Large Changes
- Estimate ROM impact (new tiles, code, music)
- Profile ROM build: `python3 analyze_rom.py` (Phase 2+)
- Ask maintainers if concerned about size

---

## Tips for Success

### Do's ✅
- Small, focused PRs (easier to review)
- Clear commit messages (easier to understand)
- Test locally before pushing (faster feedback)
- Ask questions if stuck (we're here to help)
- Link related issues (keeps context)

### Don'ts ❌
- Large PRs changing many files at once
- Vague commit messages ("update" or "fix bugs")
- Pushing without testing
- Force-pushing to main (never do this)
- Merging without passing checks

---

## Getting Help

- **Questions about code?** Check DEVELOPMENT.md or memory.md
- **Stuck on a task?** Open an issue with details
- **Design decision?** Discuss in PR before implementing
- **Need a maintainer?** Tag with @mention in issue/PR

---

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes (for substantial contributions)

---

## License

By contributing, you agree your work will be licensed under the same license as the project.

---

Thank you for contributing! Your help makes Bunny Garden Adventure better. 🐰🌻
