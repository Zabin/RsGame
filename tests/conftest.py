"""Pytest configuration and fixtures for RsGame tests."""
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def rom_path():
    """Build and return path to ROM file (once per test session)."""
    rom_file = Path("BunnyGarden.gbc")
    return rom_file


@pytest.fixture
def rom_data(rom_path):
    """Load raw ROM bytes into memory."""
    if rom_path.exists():
        with open(rom_path, "rb") as f:
            return f.read()
    return b""
