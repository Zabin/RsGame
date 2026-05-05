"""
graphics_utils.py — Graphics rendering utilities for tile previews.

Provides helper functions for rendering tiles, palettes, and screens to images.
"""

import sys
from pathlib import Path
from typing import Callable, List, Tuple, Optional
import inspect


def rgb15_to_rgb8(rgb15: int) -> Tuple[int, int, int]:
    """Convert Game Boy RGB15 (5-bit per channel) to RGB8 (8-bit per channel).

    Args:
        rgb15: 16-bit value with format 0BBBBBGGGGGRRRRR (5 bits each)

    Returns:
        Tuple of (R, G, B) each in range 0-255
    """
    r = (rgb15 & 0x1F) << 3          # Bits 0-4 → 3-7
    g = ((rgb15 >> 5) & 0x1F) << 3   # Bits 5-9 → 3-7
    b = ((rgb15 >> 10) & 0x1F) << 3  # Bits 10-14 → 3-7
    return (r, g, b)


def apply_palette(pixels: List[List[int]], palette: List[int]) -> List[List[Tuple[int, int, int]]]:
    """Apply color palette to 8x8 pixel array.

    Args:
        pixels: 8x8 array of values 0-3 (palette indices)
        palette: List of 4 RGB15 color values

    Returns:
        8x8 array of (R, G, B) tuples
    """
    rgb_palette = [rgb15_to_rgb8(color) for color in palette]
    return [[rgb_palette[pixel] for pixel in row] for row in pixels]


def get_tile_pixels(tile_index: int) -> Optional[List[List[int]]]:
    """Get the pixel data for a tile by index.

    Args:
        tile_index: Tile index 0x00-0xFF

    Returns:
        8x8 list of pixel values (0-3), or None if not found
    """
    try:
        from tile_pixels import TILE_PIXELS
        return TILE_PIXELS.get(tile_index)
    except ImportError:
        pass

    return None


def get_tile_function(tile_index: int) -> Optional[Callable]:
    """Get the pixel data for a tile by index (returns function for compatibility).

    Args:
        tile_index: Tile index 0x00-0xFF

    Returns:
        Function that returns 8x8 pixel array, or None if not found
    """
    pixels = get_tile_pixels(tile_index)
    if pixels:
        # Return a callable that returns the pixels
        return lambda: pixels

    return None


def get_palette(pal_id: int, pal_type: str = "BG") -> Optional[List[int]]:
    """Get palette colors by ID and type.

    Args:
        pal_id: Palette ID (0-7)
        pal_type: "BG" or "OBJ"

    Returns:
        List of 4 RGB15 color values, or None if not found
    """
    try:
        import build_rom

        if pal_type == "BG" and hasattr(build_rom, 'BG_PALETTES'):
            if 0 <= pal_id < len(build_rom.BG_PALETTES):
                return build_rom.BG_PALETTES[pal_id]
        elif pal_type == "OBJ" and hasattr(build_rom, 'OBJ_PALETTES'):
            if 0 <= pal_id < len(build_rom.OBJ_PALETTES):
                return build_rom.OBJ_PALETTES[pal_id]

    except ImportError:
        pass

    return None


def get_all_tile_indices() -> Tuple[List[int], List[int], List[int]]:
    """Get lists of OBJ, BG, and font tile indices.

    Returns:
        Tuple of (obj_indices, bg_indices, font_indices)
    """
    obj_indices = list(range(0x00, 0x08))      # OBJ tiles: 0x00-0x07
    bg_indices = list(range(0x10, 0x2C))       # BG tiles: 0x10-0x2B
    font_indices = list(range(0x40, 0x62))     # Font tiles: 0x40-0x61

    return obj_indices, bg_indices, font_indices


def get_screen_names() -> List[str]:
    """Get list of all available screen names.

    Returns:
        List of screen names (e.g., ['garden', 'forest', 'meadow'])
    """
    try:
        from tilemaps import ALL_SCREENS
        return [name for name, _ in ALL_SCREENS]
    except ImportError:
        return []


def get_screen_function(screen_name: str) -> Optional[Callable]:
    """Get the screen function by name.

    Args:
        screen_name: Screen name (e.g., 'garden', 'forest')

    Returns:
        Function that returns (tiles, attrs) tuple, or None if not found
    """
    try:
        from tilemaps import ALL_SCREENS
        for name, func in ALL_SCREENS:
            if name == screen_name:
                return func
    except ImportError:
        pass

    return None


def safe_import_test_helpers() -> Tuple[bool, str]:
    """Check if PIL is available and return status.

    Returns:
        Tuple of (available: bool, message: str)
    """
    try:
        from PIL import Image
        return True, "PIL available"
    except ImportError:
        return False, "PIL not installed (run: pip install Pillow)"
