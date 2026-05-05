"""Integration tests for ROM building.

Tests the complete ROM build pipeline:
- ROM generation
- Header validation
- Size checks
- Data section placement
"""
import pytest


@pytest.mark.integration
class TestROMBuild:
    """Tests for full ROM build process."""

    def test_rom_builds_successfully(self):
        """ROM can be built without errors."""
        from build_rom import build

        rom = build()
        assert rom is not None

    def test_rom_is_32kb(self, rom_data):
        """Built ROM is exactly 32KB (32768 bytes)."""
        assert len(rom_data) == 32768

    def test_rom_data_is_bytes(self, rom_data):
        """ROM data is bytes type."""
        assert isinstance(rom_data, (bytes, bytearray))

    def test_rom_all_bytes_valid(self, rom_data):
        """All ROM bytes are valid (0x00-0xFF)."""
        assert all(0 <= b <= 255 for b in rom_data)


@pytest.mark.integration
class TestROMHeader:
    """Tests for GBC ROM header validation."""

    def test_entry_point_valid(self, rom_data):
        """Entry point (0x0100) has NOP + JP."""
        assert rom_data[0x0100] == 0x00  # NOP
        assert rom_data[0x0101] == 0xC3  # JP opcode

    def test_header_starts_at_0x100(self, rom_data):
        """Header region starts at 0x0100."""
        # 0x0104-0x0133 is GBC header region
        header = rom_data[0x0104:0x0134]
        assert len(header) == 48

    def test_title_region_present(self, rom_data):
        """Title region (0x0134-0x013F) has content."""
        title = rom_data[0x0134:0x0140]
        assert any(b != 0x00 for b in title), "Title region is all zeros"

    def test_cart_type_valid(self, rom_data):
        """Cartridge type (0x0147) is valid."""
        cart_type = rom_data[0x0147]
        # GBC with RAM and battery
        assert cart_type in (0x03, 0x13)  # MBC1 variants

    def test_rom_size_field_valid(self, rom_data):
        """ROM size field (0x0148) is 0x00 (32KB)."""
        rom_size = rom_data[0x0148]
        assert rom_size == 0x00  # 32KB

    def test_ram_size_field_valid(self, rom_data):
        """RAM size field (0x0149) is valid."""
        ram_size = rom_data[0x0149]
        assert ram_size in (0x02, 0x03)  # 8KB or 32KB


@pytest.mark.integration
class TestROMSections:
    """Tests for ROM data section placement."""

    def test_isr_vectors_present(self, rom_data):
        """ISR vectors at 0x0040-0x0067 are set."""
        # VBlank ISR (0x0040) should be non-zero
        assert rom_data[0x0040] != 0x00 or rom_data[0x0041] != 0x00

    def test_tile_data_section_present(self, rom_data):
        """Tile data section (0x0800+) is populated."""
        # Tile data starts at 0x0800
        tile_section = rom_data[0x0800:0x1800]
        assert len(tile_section) == 4096
        assert any(b != 0x00 for b in tile_section), "Tile data is empty"

    def test_palette_data_present(self, rom_data):
        """Palette data (0x1800+) is populated."""
        # Palettes start around 0x1800
        palette_section = rom_data[0x1800:0x1880]
        assert len(palette_section) == 128
        assert any(b != 0x00 for b in palette_section), "Palette data is empty"

    def test_game_code_present(self, rom_data):
        """Game code section (0x0150+) has content."""
        code_section = rom_data[0x0150:0x0800]
        assert any(b != 0x00 for b in code_section), "Game code section is empty"


@pytest.mark.integration
class TestROMSize:
    """Tests for ROM size and overflow checks."""

    def test_rom_not_truncated(self, rom_data):
        """ROM is full 32KB, not truncated."""
        assert len(rom_data) == 32768

    def test_rom_end_not_all_zeros(self, rom_data):
        """ROM end section has content (not all zeros)."""
        last_kb = rom_data[-1024:]
        assert any(b != 0x00 for b in last_kb), "Last 1KB is all zeros"

    def test_rom_middle_not_all_zeros(self, rom_data):
        """ROM middle sections have content."""
        mid = rom_data[16000:16100]
        assert any(b != 0x00 for b in mid), "Middle section all zeros"
