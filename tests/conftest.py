"""Pytest fixtures for Bunny Garden Adventure tests."""
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def rom_path():
    """Build and return path to ROM file (once per test session).

    Returns:
        Path: Path to built BunnyGarden.gbc file
    """
    rom_file = Path("BunnyGarden.gbc")

    # Build ROM if not present
    if not rom_file.exists():
        from build_rom import build

        build(str(rom_file))

    assert rom_file.exists(), "ROM build failed"
    assert rom_file.stat().st_size == 32768, f"ROM size invalid: {rom_file.stat().st_size}"

    return rom_file


@pytest.fixture
def rom_data(rom_path):
    """Load raw ROM bytes into memory.

    Args:
        rom_path: Fixture providing ROM file path

    Returns:
        bytes: Raw ROM data (32KB)
    """
    with open(rom_path, "rb") as f:
        return f.read()


@pytest.fixture
def pyboy_emulator(rom_path):
    """Fresh PyBoy emulator instance (one per test).

    Cleans up any existing save files and returns emulator
    with max emulation speed (0 = infinite).

    Args:
        rom_path: Fixture providing ROM file path

    Yields:
        PyBoy: Emulator instance ready for testing

    Cleanup:
        Automatically stops emulator after test
    """
    try:
        from pyboy import PyBoy
    except ImportError:
        pytest.skip("PyBoy not installed; install with: pip install pyboy")

    # Remove any existing save files (fresh game)
    for ext in [".sav", ".ram"]:
        save_file = Path(str(rom_path) + ext)
        if save_file.exists():
            save_file.unlink()

    # Create emulator
    pb = PyBoy(str(rom_path), window="null", sound_emulated=False)
    pb.set_emulation_speed(0)  # Unlimited speed for testing

    yield pb

    # Cleanup
    pb.stop()


@pytest.fixture
def temp_rom(tmp_path):
    """Temporary directory for test ROM builds.

    Args:
        tmp_path: pytest built-in temp directory

    Returns:
        Path: Temporary directory for ROM output
    """
    return tmp_path


@pytest.fixture
def tile_data():
    """Pre-built tile data for comparison.

    Returns:
        bytearray: Complete tile data (4096 bytes)
    """
    from tiles import build_tile_data

    return build_tile_data()


@pytest.fixture
def rom_object():
    """Fresh ROM assembler object for testing.

    Returns:
        ROM: Empty 32KB ROM object
    """
    from gbc_lib import ROM

    return ROM(32768)
