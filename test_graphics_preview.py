#!/usr/bin/env python3
"""
test_graphics_preview.py — Verify graphics preview generation works correctly.

Tests that screen_preview.py and tile_preview.py generate valid PNG output
with correct dimensions.
"""

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)

from tilemaps import ALL_SCREENS


def test_screen_preview_garden():
    """Verify garden screen preview generates valid PNG."""
    output_dir = Path("previews/screens")
    output_file = output_dir / "garden.png"

    # Generate preview
    result = subprocess.run(
        [sys.executable, "screen_preview.py", "--screen", "garden"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Preview generation failed: {result.stderr}"
    assert output_file.exists(), f"Preview file not created: {output_file}"

    # Verify PNG is valid and has correct dimensions
    img = Image.open(output_file)
    assert img.format == "PNG", f"Expected PNG, got {img.format}"
    # 160x144 base * 2x upscale = 320x288
    assert img.size == (320, 288), f"Expected (320, 288), got {img.size}"
    assert img.mode == "RGB", f"Expected RGB, got {img.mode}"


def test_all_screens_preview():
    """Verify all screens can be previewed without error."""
    screen_names = [name for name, _ in ALL_SCREENS]

    for screen_name in screen_names:
        output_dir = Path("previews/screens")
        output_file = output_dir / f"{screen_name}.png"

        # Generate preview
        result = subprocess.run(
            [sys.executable, "screen_preview.py", "--screen", screen_name],
            capture_output=True,
            text=True,
        )
        assert (
            result.returncode == 0
        ), f"Preview generation failed for {screen_name}: {result.stderr}"
        assert output_file.exists(), f"Preview file not created: {output_file}"

        # Verify PNG is valid
        try:
            img = Image.open(output_file)
            assert img.format == "PNG"
            assert img.size == (320, 288), f"{screen_name}: expected (320, 288), got {img.size}"
            assert img.mode == "RGB"
        except Exception as e:
            raise AssertionError(f"Invalid PNG for {screen_name}: {e}")


def test_screen_preview_with_grid():
    """Verify grid overlay option works."""
    output_dir = Path("previews/screens")
    output_file = output_dir / "garden.png"

    result = subprocess.run(
        [sys.executable, "screen_preview.py", "--screen", "garden", "--grid"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Preview with grid failed: {result.stderr}"
    assert output_file.exists()

    img = Image.open(output_file)
    # With grid, image should still be valid
    assert img.format == "PNG"
    assert img.size == (320, 288)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
