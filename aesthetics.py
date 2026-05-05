"""
aesthetics.py — Tile registry and palette system for Bunny Garden Adventure.

Enables dynamic tile allocation, palette management, and asset-driven content
without requiring code changes for new tiles or colors.
"""


class TileSlot:
    """A registered tile with metadata (name, pixel function, palette, usage)."""

    def __init__(self, index, name, pixel_fn, obj=False, palette=0, description=""):
        """
        Args:
            index: Tile index (0x00-0xFF)
            name: Human-readable tile name
            pixel_fn: Function returning 8x8 pixel array (0-3 values)
            obj: True if OBJ (sprite) tile, False if BG tile
            palette: Palette ID (0-7)
            description: What this tile is for
        """
        self.index = index
        self.name = name
        self.pixel_fn = pixel_fn
        self.obj = obj
        self.palette = palette
        self.description = description

    def encode(self):
        """Generate 16-byte 2bpp encoding of tile pixel data."""
        from tiles import enc
        return enc(self.pixel_fn())

    def __repr__(self):
        tile_type = "OBJ" if self.obj else "BG"
        return f"TileSlot(0x{self.index:02X} {self.name} {tile_type} pal{self.palette})"


class Palette:
    """A named color palette with 4 colors (Game Boy 2bpp)."""

    def __init__(self, palette_id, name, colors, pal_type="BG"):
        """
        Args:
            palette_id: Palette index (0-7)
            name: Human-readable name
            colors: List of 4 RGB15 color values (e.g., from rgb15(r,g,b))
            pal_type: "BG" or "OBJ"
        """
        self.palette_id = palette_id
        self.name = name
        self.colors = colors
        self.pal_type = pal_type
        assert len(colors) == 4, "Palette must have exactly 4 colors"
        assert all(0 <= c <= 0x7FFF for c in colors), "Colors must be RGB15 (0-0x7FFF)"

    def to_bytes(self):
        """Convert to 8-byte format for ROM (2 bytes per color)."""
        data = []
        for color in self.colors:
            data.append(color & 0xFF)
            data.append((color >> 8) & 0xFF)
        return bytes(data)

    def __repr__(self):
        return f"Palette(id={self.palette_id} {self.name} {self.pal_type})"


class TileRegistry:
    """Central registry for all game tiles and palettes."""

    def __init__(self):
        self.tiles = {}  # index -> TileSlot
        self.palettes = {}  # (type, id) -> Palette
        self.next_bg_slot = 0x10  # BG tiles start at 0x10
        self.next_obj_slot = 0x08  # OBJ tiles start after bunny (0x00-0x07)

    def register_tile(self, tile_slot):
        """Register a tile slot."""
        if tile_slot.index in self.tiles:
            raise ValueError(f"Tile index 0x{tile_slot.index:02X} already registered")
        self.tiles[tile_slot.index] = tile_slot
        return tile_slot

    def register_palette(self, palette):
        """Register a palette."""
        key = (palette.pal_type, palette.palette_id)
        if key in self.palettes:
            raise ValueError(f"Palette {palette.name} already registered at ID {palette.palette_id}")
        self.palettes[key] = palette
        return palette

    def allocate_bg_tile(self, name, pixel_fn, palette=0, description=""):
        """Allocate next available BG tile slot."""
        while self.next_bg_slot in self.tiles:
            self.next_bg_slot += 1
        if self.next_bg_slot >= 0x40:
            raise Exception("BG tile slots exhausted (0x40+)")
        slot = TileSlot(self.next_bg_slot, name, pixel_fn, obj=False, palette=palette, description=description)
        self.register_tile(slot)
        self.next_bg_slot += 1
        return slot

    def allocate_obj_tile(self, name, pixel_fn, palette=0, description=""):
        """Allocate next available OBJ tile slot."""
        while self.next_obj_slot in self.tiles:
            self.next_obj_slot += 1
        if self.next_obj_slot >= 0x40:
            raise Exception("OBJ tile slots exhausted (0x40+)")
        slot = TileSlot(self.next_obj_slot, name, pixel_fn, obj=True, palette=palette, description=description)
        self.register_tile(slot)
        self.next_obj_slot += 1
        return slot

    def get_tile(self, index):
        """Retrieve a registered tile by index."""
        return self.tiles.get(index)

    def get_palette(self, pal_type, palette_id):
        """Retrieve a registered palette."""
        return self.palettes.get((pal_type, palette_id))

    def build_tile_data(self):
        """Generate complete 4096-byte tile data for ROM."""
        data = bytearray()
        for i in range(256):
            if i in self.tiles:
                data.extend(self.tiles[i].encode())
            else:
                data.extend([0] * 16)  # Empty tile
        return data

    def list_tiles(self, tile_type=None):
        """List all registered tiles, optionally filtered by type."""
        for slot in sorted(self.tiles.values(), key=lambda s: s.index):
            if tile_type is None or (slot.obj == (tile_type == "OBJ")):
                print(f"  {slot}")

    def __repr__(self):
        return f"TileRegistry({len(self.tiles)} tiles, {len(self.palettes)} palettes)"


# Global registry instance
registry = TileRegistry()


def load_assets_from_json(json_path):
    """Load tile and palette definitions from JSON asset file."""
    import json
    from pathlib import Path

    json_file = Path(json_path)
    if not json_file.exists():
        raise FileNotFoundError(f"Asset file not found: {json_path}")

    with open(json_file) as f:
        assets = json.load(f)

    # Load palettes first
    if "palettes" in assets:
        from gbc_lib import rgb15
        for pal_name, pal_def in assets["palettes"].items():
            palette_id = pal_def.get("id", 0)
            pal_type = pal_def.get("type", "BG")
            colors_hex = pal_def.get("colors", [])
            # Convert hex color strings to RGB15
            colors = []
            for hex_color in colors_hex:
                # Parse #RRGGBB format
                hex_color = hex_color.lstrip("#")
                r = int(hex_color[0:2], 16) >> 3  # 0-255 → 0-31
                g = int(hex_color[2:4], 16) >> 3
                b = int(hex_color[4:6], 16) >> 3
                colors.append(rgb15(r, g, b))
            palette = Palette(palette_id, pal_name, colors, pal_type)
            registry.register_palette(palette)

    # Load tiles
    if "tiles" in assets:
        for tile_name, tile_def in assets["tiles"].items():
            # For now, skip actual pixel loading (would require dynamic function generation)
            # This is a skeleton for future tile asset loading
            pass

    return registry
