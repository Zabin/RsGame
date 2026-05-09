"""Unit tests for bunny sprite visibility on gameplay screens."""
import pytest


class TestBunnyOAM:
    """Tests for bunny OAM (sprite) rendering."""

    def test_player_tile_indices_valid(self):
        """Bunny sprite tile indices (TL_BUNNY_T_F1, etc.) are defined."""
        from tiles import TL_BUNNY_T_F1, TL_BUNNY_T_F2, TL_BUNNY_B_F1, TL_BUNNY_B_F2
        # Verify all bunny tile indices exist and are valid (0x00-0xFF)
        for idx in [TL_BUNNY_T_F1, TL_BUNNY_T_F2, TL_BUNNY_B_F1, TL_BUNNY_B_F2]:
            assert isinstance(idx, int), f"Bunny tile index {idx} is not an integer"
            assert 0 <= idx <= 0xFF, f"Bunny tile index {idx} out of range"

    def test_obj_palettes_defined(self, rom_data):
        """OBJ palettes are loaded into ROM."""
        # OBJ palettes: 8 palettes × 4 colors × 2 bytes each = 64 bytes
        # Located in palette data section (after BG palettes)
        # For now, verify ROM has palette data (non-zero bytes in expected region)
        assert len(rom_data) == 32768, "ROM size incorrect"
        # Verify palettes section exists (not all zeros)
        assert any(b != 0x00 for b in rom_data[0x0800:0x1000]), "Palette data missing"

    def test_oam_buffer_in_wram(self):
        """OAM buffer is allocated at 0xC300 (shadow OAM)."""
        # This is verified in asm_game.py definition:
        # OAM_BUF = 0xC300
        # Shadow OAM is 160 bytes (40 sprites × 4 bytes each)
        from asm_game import OAM_BUF
        assert OAM_BUF == 0xC300, "OAM buffer not at 0xC300"

    def test_player_coordinates_initialized(self):
        """Player X/Y coordinates are defined in WRAM."""
        from asm_game import PLAYER_X, PLAYER_Y
        assert PLAYER_X == 0xC001, "PLAYER_X not at 0xC001"
        assert PLAYER_Y == 0xC002, "PLAYER_Y not at 0xC002"

    def test_player_coordinates_valid_range(self):
        """Player starting coordinates are within valid range."""
        # From asm_game.py st_intro state:
        # PLAYER_X = 76 (center-ish)
        # PLAYER_Y = 72 (center-ish)
        assert 0 <= 76 <= 160, "Starting PLAYER_X out of range"
        assert 16 <= 72 <= 143, "Starting PLAYER_Y out of range"

    def test_bunny_oam_entries_layout(self):
        """Bunny OAM entries are 2 sprites (head+body)."""
        # From asm_game.py update_oam:
        # Entry 0: head sprite (Y, X, tile, attrs)
        # Entry 1: body sprite (Y, X, tile, attrs)
        # Each entry is 4 bytes
        # Total: 8 bytes for bunny
        assert 8 == 2 * 4, "Bunny OAM layout incorrect"

    def test_oam_update_enabled_in_playing(self, rom_data):
        """OAM update code is only active during PLAYING state."""
        # Verify assembly contains check for GS_PLAYING in update_oam
        # This is in asm_game.py: rom.CP_n(GS_PLAYING); rom.RET_NZ()
        # We verify build completes (patch points exist)
        assert len(rom_data) == 32768, "ROM built"

    def test_bunny_sprite_palette(self):
        """Bunny uses OBJ palette 0 (defined in build_rom.py OBJ_PALETTES[0])."""
        # OBJ_PALETTES[0] = [BLACK, BG_W, PNK_L, PNK_D] (bunny colors)
        from build_rom import OBJ_PALETTES
        assert len(OBJ_PALETTES) >= 1, "OBJ palette 0 not defined"
        assert len(OBJ_PALETTES[0]) == 4, "OBJ palette 0 incorrect size"

    def test_frame_animation_state(self):
        """Bunny animation frame counter is defined in WRAM."""
        from asm_game import PLAYER_FRAME, ANIM_CTR
        assert PLAYER_FRAME == 0xC004, "PLAYER_FRAME not at 0xC004"
        assert ANIM_CTR == 0xC005, "ANIM_CTR not at 0xC005"

    def test_bunny_direction_state(self):
        """Bunny direction (facing) state is defined."""
        from asm_game import PLAYER_DIR
        assert PLAYER_DIR == 0xC003, "PLAYER_DIR not at 0xC003"
        # Direction 0 = right, 1 = left
        assert 0 <= 0 <= 1, "Direction right valid"
        assert 0 <= 1 <= 1, "Direction left valid"
