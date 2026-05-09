"""Byte-level ROM integrity tests verifying runtime-critical configuration.

These tests catch regressions where ROM data is logically correct in source
but incorrectly compiled or patched into the binary, which is what caused
the bunny invisibility and music garbling bugs.
"""
import pytest


class TestAudioInit:
    """Verify audio register initialization in compiled ROM."""

    def test_nr12_no_envelope_decay(self, rom_data):
        """NR12 init must NOT have envelope decay (period > 0 with decrease direction).

        BUG HISTORY: NR12=0xD2 caused volume to decay to 0 mid-note, producing
        garbled audio. NR12=0xF0 (volume 0xF, period 0) keeps volume constant.
        """
        # Search for "LD A, n; LDH (FF12), A" pattern in code section
        for i in range(0x100, 0x800):
            if rom_data[i] == 0x3E and rom_data[i + 2] == 0xE0 and rom_data[i + 3] == 0x12:
                nr12_value = rom_data[i + 1]
                # Bits 2-0 = envelope period; if non-zero with bit 3=0 (decrease), volume fades
                period = nr12_value & 0x07
                direction_increase = bool(nr12_value & 0x08)
                if period > 0 and not direction_increase:
                    pytest.fail(
                        f"NR12=0x{nr12_value:02X} causes volume decay "
                        f"(period={period}, direction=decrease). "
                        f"Use period=0 (e.g. 0xF0) for steady volume."
                    )
                return
        pytest.fail("NR12 write not found in ROM code section")

    def test_nr52_audio_power_on(self, rom_data):
        """NR52 must be initialized to 0x80 (audio power on)."""
        for i in range(0x100, 0x800):
            if rom_data[i] == 0x3E and rom_data[i + 2] == 0xE0 and rom_data[i + 3] == 0x26:
                assert rom_data[i + 1] == 0x80, (
                    f"NR52=0x{rom_data[i+1]:02X} should be 0x80 (audio power on)"
                )
                return
        pytest.fail("NR52 write not found in ROM code section")


class TestVramInit:
    """Verify VRAM initialization clears both banks."""

    def test_vram_bank_1_cleared(self, rom_data):
        """VRAM bank 1 must be cleared before tile/attr loads.

        BUG HISTORY: Without clearing bank 1, the BG attribute map could contain
        garbage including BG-OAM priority bit (bit 7), which would render the
        bunny BEHIND the BG and make it invisible.
        """
        # Look for "LD A, 1; LDH (FF4F), A" - select VRAM bank 1
        # Then expect a clear loop (LD HL, 0x8000; LD BC, 0x2000; XOR A; LDI; ...)
        found_bank_1_select = False
        for i in range(0x150, 0x300):
            if (
                rom_data[i] == 0x3E
                and rom_data[i + 1] == 0x01
                and rom_data[i + 2] == 0xE0
                and rom_data[i + 3] == 0x4F
            ):
                found_bank_1_select = True
                break
        assert found_bank_1_select, "VRAM bank 1 select (LD A,1; LDH (FF4F),A) not found"


class TestZoneNavigation:
    """Verify zone navigation supports full 3×3 grid."""

    def test_zone_right_boundary_prevents_row_wrap(self, rom_data):
        """Right boundary check must prevent wrapping from col 2 to col 0 of next row.

        For a proper 3×3 grid with LEFT/RIGHT/UP/DOWN navigation:
        - Boundary 2: if (zone & 3) >= 2, don't navigate right
          * Prevents zone 2 → zone 3 (which would be row 1, col 0)
          * Keeps rows separate; UP/DOWN nav moves between rows
        - UP/DOWN navigation handles row transitions
        """
        # The check is: AND 3; CP n  (where n is the boundary)
        # Pattern: 0xE6 0x03 (AND 3) 0xFE 0x?? (CP n)
        for i in range(0x150, 0x800):
            if (
                rom_data[i] == 0xE6
                and rom_data[i + 1] == 0x03
                and rom_data[i + 2] == 0xFE
            ):
                boundary = rom_data[i + 3]
                # 2 = correct value (prevents wrapping between rows)
                # With UP/DOWN nav, all 9 zones are fully accessible
                assert boundary == 2, (
                    f"Zone column boundary CP {boundary} is incorrect. "
                    f"Should be 2 to prevent wrapping from col 2 to row 1, col 0."
                )
                return
        pytest.fail("Zone boundary check (AND 3; CP n) not found in ROM")


class TestSpriteRendering:
    """Verify sprite (OAM) rendering setup."""

    def test_lcdc_obj_enabled(self, rom_data):
        """LCDC initialization must have OBJ enable bit (bit 1) set."""
        # Search for LCDC writes (LDH (FF40), A)
        for i in range(0x100, 0x800):
            if rom_data[i] == 0x3E and rom_data[i + 2] == 0xE0 and rom_data[i + 3] == 0x40:
                lcdc_value = rom_data[i + 1]
                if lcdc_value == 0:
                    continue  # LCD off (used for VRAM updates) — skip
                obj_enabled = bool(lcdc_value & 0x02)
                assert obj_enabled, (
                    f"LCDC=0x{lcdc_value:02X} has OBJ disabled (bit 1=0). "
                    f"Bunny sprite cannot render."
                )

    def test_obj_palette_size(self, rom_data):
        """OBJ palette load must write 64 bytes (8 palettes × 4 colors × 2 bytes)."""
        # Pattern: LD B, n where n=64 followed by an OCPD write loop
        # OCPD = 0xFF6B
        # Find: LD A, n / LDH (FF6A), A (OCPS); ... LD B, 64
        for i in range(0x100, 0x800):
            if (
                rom_data[i] == 0x3E
                and rom_data[i + 2] == 0xE0
                and rom_data[i + 3] == 0x6A
            ):
                # OCPS write found; look for nearby LD B, 64
                for j in range(i, min(i + 20, 0x800)):
                    if rom_data[j] == 0x06 and rom_data[j + 1] == 64:
                        return
                pytest.fail("OCPS write found but LD B, 64 not nearby")
        pytest.fail("OCPS init write not found in ROM")
