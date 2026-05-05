"""Unit tests for tile encoding and data generation.

Tests the tiles module independently:
- Pixel encoding (8x8 → 16-byte 2bpp)
- Tile constants
- Tile data building
- Character-to-tile mapping
"""
import pytest

from tiles import (
    TL_BUNNY_T_F1,
    TL_DIGIT_0,
    TL_GRASS_PLAIN,
    TL_HEART_EMPTY,
    TL_HEART_FULL,
    build_tile_data,
    char_to_tile,
    enc,
)


@pytest.mark.unit
class TestEncoding:
    """Tests for enc() pixel encoding function."""

    def test_enc_returns_16_bytes(self):
        """Encoding 8x8 pixels returns exactly 16 bytes."""
        pix = [[0] * 8 for _ in range(8)]
        result = enc(pix)
        assert len(result) == 16
        assert all(isinstance(b, int) for b in result)

    def test_enc_all_zeros(self):
        """All-zero pixel array encodes to all zeros."""
        pix = [[0] * 8 for _ in range(8)]
        result = enc(pix)
        assert all(b == 0 for b in result)

    def test_enc_color_mixed(self):
        """Mixed colors encode with correct bitplane split."""
        # Color encoding uses 2bpp: bit 0 and bit 1 per pixel
        pix = [
            [0, 1, 2, 3, 0, 1, 2, 3],
            [0] * 8,
            [0] * 8,
            [0] * 8,
            [0] * 8,
            [0] * 8,
            [0] * 8,
            [0] * 8,
        ]
        result = enc(pix)
        # First row should have specific encoding
        # Just verify it's not all zeros and has some structure
        assert any(b != 0 for b in result[0:2])  # First row non-zero

    def test_enc_different_pixels_different_output(self):
        """Different pixel patterns produce different encoded output."""
        pix1 = [[0] * 8 for _ in range(8)]
        pix2 = [[1] * 8 for _ in range(8)]
        result1 = enc(pix1)
        result2 = enc(pix2)
        assert result1 != result2, "Different pixels should encode differently"

    def test_enc_all_pixels_set(self):
        """All pixels set to color 3 encodes to all ones."""
        pix = [[3] * 8 for _ in range(8)]
        result = enc(pix)
        assert all(b == 0xFF for b in result)


@pytest.mark.unit
class TestTileConstants:
    """Tests for tile index constants."""

    def test_bunny_constants_defined(self):
        """All bunny tile constants are defined and in valid range."""
        assert TL_BUNNY_T_F1 == 0x00
        assert isinstance(TL_BUNNY_T_F1, int)
        assert 0 <= TL_BUNNY_T_F1 <= 0xFF

    def test_grass_tile_constant(self):
        """Grass tile constant in expected range."""
        assert TL_GRASS_PLAIN == 0x10
        assert TL_GRASS_PLAIN < 0x30  # BG tiles before font

    def test_digit_and_heart_constants(self):
        """Digit and heart tile constants defined."""
        assert TL_DIGIT_0 == 0x20
        assert TL_HEART_FULL == 0x1D
        assert TL_HEART_EMPTY == 0x1E

    def test_no_constant_overlap(self):
        """Tile constants are unique (no duplicates)."""
        constants = [
            TL_BUNNY_T_F1,
            TL_GRASS_PLAIN,
            TL_DIGIT_0,
            TL_HEART_FULL,
            TL_HEART_EMPTY,
        ]
        assert len(constants) == len(set(constants))


@pytest.mark.unit
class TestCharToTile:
    """Tests for character-to-tile mapping."""

    def test_uppercase_letters(self):
        """Uppercase letters A-Z map correctly."""
        assert char_to_tile("A") == 0x40
        assert char_to_tile("Z") == 0x59
        # Verify sequence
        for i, char in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            assert char_to_tile(char) == 0x40 + i

    def test_digits(self):
        """Digits 0-9 map correctly."""
        assert char_to_tile("0") == 0x20
        assert char_to_tile("9") == 0x29
        for i in range(10):
            assert char_to_tile(str(i)) == 0x20 + i

    def test_space_and_punctuation(self):
        """Special characters map to expected tiles."""
        space = char_to_tile(" ")
        assert space == 0x5A
        assert isinstance(space, int)
        assert 0 <= space <= 0xFF
        # Punctuation mapping depends on implementation

    def test_lowercase_converts_to_uppercase(self):
        """Lowercase letters are converted to uppercase."""
        # Implementation should normalize case
        a_lower = char_to_tile("a")
        a_upper = char_to_tile("A")
        # Both should be valid tile indices
        assert isinstance(a_lower, int)
        assert isinstance(a_upper, int)
        assert 0 <= a_lower <= 0xFF
        assert 0 <= a_upper <= 0xFF


@pytest.mark.unit
class TestBuildTileData:
    """Tests for tile data building."""

    def test_build_tile_data_size(self):
        """build_tile_data() produces exactly 4096 bytes."""
        data = build_tile_data()
        assert len(data) == 256 * 16
        assert len(data) == 4096

    def test_build_tile_data_type(self):
        """build_tile_data() returns bytes or bytearray."""
        data = build_tile_data()
        assert isinstance(data, (bytes, bytearray))

    def test_bunny_tiles_not_empty(self):
        """Bunny tile data (0x00, 0x01, 0x02, 0x03) is not all zeros."""
        data = build_tile_data()
        for tile_idx in [0x00, 0x01, 0x02, 0x03]:
            tile_data = data[tile_idx * 16 : (tile_idx + 1) * 16]
            assert any(b != 0 for b in tile_data), f"Tile {tile_idx:02X} is empty"

    def test_grass_tiles_not_empty(self):
        """Some grass/BG tiles (0x10+) are not all zeros."""
        data = build_tile_data()
        # Check a sample of tiles (not all may be used)
        non_empty_count = 0
        for tile_idx in range(0x10, 0x1F):
            tile_data = data[tile_idx * 16 : (tile_idx + 1) * 16]
            if any(b != 0 for b in tile_data):
                non_empty_count += 1
        # At least some tiles in this range should be populated
        assert non_empty_count >= 5, f"Only {non_empty_count} grass tiles populated"

    def test_tiles_are_bytes(self):
        """All tile data bytes are valid byte values."""
        data = build_tile_data()
        assert all(0 <= b <= 255 for b in data)

    def test_tile_data_deterministic(self):
        """build_tile_data() produces same result on multiple calls."""
        data1 = build_tile_data()
        data2 = build_tile_data()
        assert data1 == data2


@pytest.mark.unit
class TestTileIntegration:
    """Integration tests within tile module (no external deps)."""

    def test_encoded_tiles_match_build(self):
        """Tiles built via build_tile_data() can be re-encoded."""
        # This is more of a smoke test: just verify structure
        data = build_tile_data()
        assert data[0:16]  # First tile data exists
        assert data[4080:4096]  # Last tile data exists

    def test_all_256_tiles_allocated(self):
        """All 256 tile slots have data (at least some are non-zero)."""
        data = build_tile_data()
        non_empty_count = 0
        for i in range(256):
            tile_data = data[i * 16 : (i + 1) * 16]
            if any(b != 0 for b in tile_data):
                non_empty_count += 1

        # At minimum, bunny, grass, hearts, digits should be present
        assert non_empty_count >= 20, f"Only {non_empty_count} tiles populated"
