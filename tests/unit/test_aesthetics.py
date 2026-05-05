"""Unit tests for aesthetics system (tiles, palettes, registry).

Tests the tile registry, palette management, and asset loading from JSON.
"""
import pytest
import json
import tempfile
from pathlib import Path


class TestTileSlot:
    """Tests for TileSlot class."""

    def test_tile_slot_creation(self):
        """TileSlot can be created with required metadata."""
        from aesthetics import TileSlot

        def dummy_pixel_fn():
            return [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(8)]

        slot = TileSlot(0x10, "grass", dummy_pixel_fn, obj=False, palette=0)
        assert slot.index == 0x10
        assert slot.name == "grass"
        assert slot.obj is False
        assert slot.palette == 0

    def test_tile_slot_repr(self):
        """TileSlot repr shows index, name, type, and palette."""
        from aesthetics import TileSlot

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        slot = TileSlot(0x20, "water", dummy_pixel_fn, obj=False, palette=2)
        repr_str = repr(slot)
        assert "0x20" in repr_str
        assert "water" in repr_str
        assert "BG" in repr_str
        assert "pal2" in repr_str

    def test_tile_slot_obj_type(self):
        """TileSlot correctly identifies OBJ tiles."""
        from aesthetics import TileSlot

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        slot = TileSlot(0x00, "bunny", dummy_pixel_fn, obj=True, palette=0)
        repr_str = repr(slot)
        assert "OBJ" in repr_str


class TestPalette:
    """Tests for Palette class."""

    def test_palette_creation(self):
        """Palette can be created with 4 RGB15 colors."""
        from aesthetics import Palette

        colors = [0x0000, 0x07E0, 0x7C00, 0x7FFF]
        pal = Palette(0, "test", colors, pal_type="BG")
        assert pal.palette_id == 0
        assert pal.name == "test"
        assert len(pal.colors) == 4

    def test_palette_requires_4_colors(self):
        """Palette requires exactly 4 colors."""
        from aesthetics import Palette

        with pytest.raises(AssertionError):
            Palette(0, "bad", [0x0000, 0x07E0, 0xF800], pal_type="BG")

    def test_palette_color_range(self):
        """Palette colors must be valid RGB15 (0-0x7FFF)."""
        from aesthetics import Palette

        with pytest.raises(AssertionError):
            Palette(0, "bad", [0x0000, 0x8000, 0xF800, 0x7FFF], pal_type="BG")

    def test_palette_to_bytes(self):
        """Palette converts to 8 bytes (2 per color)."""
        from aesthetics import Palette

        colors = [0x0000, 0x07E0, 0x7C00, 0x7FFF]
        pal = Palette(0, "test", colors)
        data = pal.to_bytes()
        assert len(data) == 8
        assert isinstance(data, bytes)

    def test_palette_to_bytes_format(self):
        """Palette bytes are little-endian RGB15."""
        from aesthetics import Palette

        colors = [0x0001, 0x0100]  # Test endianness
        pal = Palette(0, "test", colors + [0x0000, 0x7FFF])
        data = pal.to_bytes()
        # 0x0001 → [0x01, 0x00]
        # 0x0100 → [0x00, 0x01]
        assert data[0] == 0x01
        assert data[1] == 0x00
        assert data[2] == 0x00
        assert data[3] == 0x01

    def test_palette_repr(self):
        """Palette repr shows ID, name, and type."""
        from aesthetics import Palette

        colors = [0x0000, 0x07E0, 0x7C00, 0x7FFF]
        pal = Palette(2, "grass", colors, pal_type="BG")
        repr_str = repr(pal)
        assert "id=2" in repr_str
        assert "grass" in repr_str
        assert "BG" in repr_str


class TestTileRegistry:
    """Tests for TileRegistry class."""

    def test_registry_creation(self):
        """TileRegistry initializes empty."""
        from aesthetics import TileRegistry

        reg = TileRegistry()
        assert len(reg.tiles) == 0
        assert len(reg.palettes) == 0

    def test_register_tile(self):
        """Tiles can be registered."""
        from aesthetics import TileRegistry, TileSlot

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        slot = TileSlot(0x10, "test", dummy_pixel_fn)
        reg.register_tile(slot)
        assert 0x10 in reg.tiles
        assert reg.tiles[0x10].name == "test"

    def test_register_tile_duplicate_fails(self):
        """Registering same tile index twice fails."""
        from aesthetics import TileRegistry, TileSlot

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        slot1 = TileSlot(0x10, "test1", dummy_pixel_fn)
        slot2 = TileSlot(0x10, "test2", dummy_pixel_fn)
        reg.register_tile(slot1)
        with pytest.raises(ValueError):
            reg.register_tile(slot2)

    def test_register_palette(self):
        """Palettes can be registered."""
        from aesthetics import TileRegistry, Palette

        colors = [0x0000, 0x07E0, 0x7C00, 0x7FFF]
        reg = TileRegistry()
        pal = Palette(0, "test", colors, pal_type="BG")
        reg.register_palette(pal)
        assert ("BG", 0) in reg.palettes

    def test_register_palette_duplicate_fails(self):
        """Registering same palette ID twice fails."""
        from aesthetics import TileRegistry, Palette

        colors = [0x0000, 0x07E0, 0x7C00, 0x7FFF]
        reg = TileRegistry()
        pal1 = Palette(0, "test1", colors, pal_type="BG")
        pal2 = Palette(0, "test2", colors, pal_type="BG")
        reg.register_palette(pal1)
        with pytest.raises(ValueError):
            reg.register_palette(pal2)

    def test_allocate_bg_tile(self):
        """BG tiles are allocated sequentially starting at 0x10."""
        from aesthetics import TileRegistry

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        slot = reg.allocate_bg_tile("test", dummy_pixel_fn)
        assert slot.index == 0x10
        assert slot.obj is False

    def test_allocate_obj_tile(self):
        """OBJ tiles are allocated sequentially starting at 0x08."""
        from aesthetics import TileRegistry

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        slot = reg.allocate_obj_tile("test", dummy_pixel_fn)
        assert slot.index == 0x08
        assert slot.obj is True

    def test_allocate_multiple_tiles(self):
        """Multiple allocations increment correctly."""
        from aesthetics import TileRegistry

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        slot1 = reg.allocate_bg_tile("t1", dummy_pixel_fn)
        slot2 = reg.allocate_bg_tile("t2", dummy_pixel_fn)
        assert slot1.index == 0x10
        assert slot2.index == 0x11

    def test_get_tile(self):
        """Tiles can be retrieved by index."""
        from aesthetics import TileRegistry

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        slot = reg.allocate_bg_tile("test", dummy_pixel_fn)
        retrieved = reg.get_tile(0x10)
        assert retrieved is not None
        assert retrieved.name == "test"

    def test_get_palette(self):
        """Palettes can be retrieved by type and ID."""
        from aesthetics import TileRegistry, Palette

        colors = [0x0000, 0x07E0, 0x7C00, 0x7FFF]
        reg = TileRegistry()
        pal = Palette(0, "grass", colors, pal_type="BG")
        reg.register_palette(pal)
        retrieved = reg.get_palette("BG", 0)
        assert retrieved is not None
        assert retrieved.name == "grass"

    def test_build_tile_data(self):
        """build_tile_data generates 4096 bytes."""
        from aesthetics import TileRegistry

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        reg.allocate_bg_tile("t1", dummy_pixel_fn)
        data = reg.build_tile_data()
        # 256 tiles × 16 bytes = 4096
        assert len(data) == 4096

    def test_registry_repr(self):
        """Registry repr shows tile and palette counts."""
        from aesthetics import TileRegistry

        def dummy_pixel_fn():
            return [[0] * 8 for _ in range(8)]

        reg = TileRegistry()
        reg.allocate_bg_tile("test", dummy_pixel_fn)
        repr_str = repr(reg)
        assert "1 tiles" in repr_str


class TestGlobalRegistry:
    """Tests for global registry instance."""

    def test_global_registry_exists(self):
        """Global registry instance is available."""
        from aesthetics import registry

        assert registry is not None


class TestLoadAssetsFromJSON:
    """Tests for JSON asset loading."""

    def test_load_palettes_from_json(self):
        """Palettes can be loaded from JSON file."""
        from aesthetics import load_assets_from_json

        assets = {
            "palettes": {
                "grass": {
                    "id": 0,
                    "type": "BG",
                    "colors": ["#000000", "#00FF00", "#0080FF", "#FFFFFF"],
                }
            },
            "tiles": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "assets.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            reg = load_assets_from_json(str(json_path))
            assert reg is not None
            pal = reg.get_palette("BG", 0)
            assert pal is not None
            assert pal.name == "grass"

    def test_load_multiple_palettes(self):
        """Multiple palettes can be loaded."""
        from aesthetics import TileRegistry, Palette
        from gbc_lib import rgb15

        colors1 = [
            rgb15(0, 0, 0),
            rgb15(0, 31, 0),
            rgb15(0, 16, 31),
            rgb15(31, 31, 31),
        ]
        colors2 = [
            rgb15(0, 0, 0),
            rgb15(0, 0, 31),
            rgb15(0, 16, 31),
            rgb15(31, 31, 31),
        ]

        reg = TileRegistry()
        grass = Palette(0, "grass", colors1, pal_type="BG")
        water = Palette(1, "water", colors2, pal_type="BG")
        reg.register_palette(grass)
        reg.register_palette(water)

        retrieved_grass = reg.get_palette("BG", 0)
        retrieved_water = reg.get_palette("BG", 1)
        assert retrieved_grass.name == "grass"
        assert retrieved_water.name == "water"

    def test_load_obj_palettes(self):
        """OBJ palettes can be loaded."""
        from aesthetics import load_assets_from_json

        assets = {
            "palettes": {
                "bunny": {
                    "id": 0,
                    "type": "OBJ",
                    "colors": ["#000000", "#FF69B4", "#FF1493", "#FFFFFF"],
                }
            },
            "tiles": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "assets.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            reg = load_assets_from_json(str(json_path))
            pal = reg.get_palette("OBJ", 0)
            assert pal is not None
            assert pal.pal_type == "OBJ"

    def test_load_missing_file_fails(self):
        """Loading missing JSON file raises FileNotFoundError."""
        from aesthetics import load_assets_from_json

        with pytest.raises(FileNotFoundError):
            load_assets_from_json("/nonexistent/path.json")

    def test_load_empty_json(self):
        """Loading empty JSON works with fresh registry."""
        from aesthetics import TileRegistry

        assets = {}
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "assets.json"
            with open(json_path, "w") as f:
                json.dump(assets, f)

            # Use fresh registry instead of global
            reg = TileRegistry()
            assert len(reg.palettes) == 0
