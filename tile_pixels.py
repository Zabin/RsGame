"""
tile_pixels.py — Raw pixel data for all tiles (8x8 arrays, values 0-3).

Generated from tiles.py tile functions. Used by preview tools.
"""

# Define all tile pixel arrays for easy access by preview tools

# OBJ Sprites - Enhanced Bunny with Better Animation
BUNNY_TOP_F1 = [
    [0,3,2,0,3,2,0,0],  # tall alert ears
    [0,3,2,2,3,2,0,0],
    [0,3,1,2,3,1,0,0],
    [0,0,3,3,3,3,0,0],  # head
    [0,3,1,1,1,1,3,0],  # face - neutral
    [0,3,2,1,1,2,3,0],  # eyes - bright
    [0,3,1,2,2,1,1,3],  # nose - emphasized
    [0,0,3,1,1,1,3,0],  # chin
]

BUNNY_BOT_F1 = [
    [0,3,1,1,1,1,1,3],  # body - straight stance
    [3,1,2,2,2,2,1,3],  # belly - bright detail
    [3,1,1,1,1,1,1,3],
    [3,1,1,1,1,1,1,3],
    [3,1,1,1,1,1,1,3],  # legs - grounded
    [0,3,1,1,1,1,3,0],
    [0,0,3,2,2,3,0,0],  # feet
    [0,0,1,3,3,1,0,0],
]

BUNNY_TOP_F2 = [
    [0,3,0,0,3,0,0,0],  # ears raised (jumping)
    [0,3,2,0,3,0,0,0],
    [0,3,2,0,3,0,0,0],
    [0,0,3,3,3,3,0,0],  # head
    [0,3,1,1,1,1,3,0],  # face - happy
    [0,3,2,1,1,2,3,0],  # eyes - wide awake
    [0,3,1,1,2,1,1,3],  # nose - mid-expression
    [0,0,3,1,1,1,3,0],  # chin
]

BUNNY_BOT_F2 = [
    [0,3,1,1,1,1,1,3],  # body - hopping pose
    [3,1,2,2,2,2,1,3],  # belly - bright
    [3,1,1,1,1,1,1,3],
    [3,1,1,1,1,1,1,3],
    [3,1,0,1,1,0,1,3],  # legs - jumping
    [0,3,1,0,0,1,3,0],  # feet elevated
    [0,0,3,1,1,3,0,0],
    [0,0,2,3,3,2,0,0],
]

GIFT_OBJ = [
    [0,3,3,3,3,3,0,0],  # enhanced gift box
    [3,2,2,2,2,2,3,0],  # wrapped present
    [3,2,1,1,2,2,3,0],  # bright ribbon detail
    [3,2,1,1,2,2,3,0],  #
    [3,2,2,2,2,2,3,0],  #
    [0,3,2,2,2,2,3,0],  #
    [0,0,3,3,3,3,0,0],  #
    [0,0,0,1,1,0,0,0],  # bow highlight
]

STAR_OBJ = [
    [0,0,0,3,0,0,0,0],  # bright star
    [0,0,3,3,3,0,0,0],
    [0,3,3,2,3,3,0,0],  # golden core
    [3,3,3,1,3,3,3,0],  # bright highlight
    [0,3,3,2,3,3,0,0],  # glow effect
    [0,0,3,3,3,0,0,0],
    [0,0,0,3,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

FLOWER_OBJ = [
    [0,0,0,3,0,0,0,0],  # enhanced flower
    [0,0,3,2,3,0,0,0],
    [0,3,2,1,2,3,0,0],  # vibrant petals
    [3,2,1,1,1,2,3,0],
    [0,3,2,3,2,3,0,0],
    [0,0,0,3,0,0,0,0],
    [0,0,0,3,0,0,0,0],
    [0,0,0,2,0,0,0,0],
]

# BG Tiles
GRASS_PLAIN = [
    [0,1,2,1,0,1,2,1],  # lush grass blend
    [2,1,1,1,2,1,1,1],
    [0,1,2,1,0,1,2,1],
    [1,1,0,1,1,1,0,1],  # texture variation
    [0,1,2,1,0,1,2,1],
    [2,1,1,1,2,1,1,1],
    [0,1,2,1,0,1,2,1],
    [1,1,0,1,1,1,0,1],
]

GRASS_TUFT = [
    [0,0,2,1,1,2,0,0],  # wildflower tuft
    [0,2,1,1,1,1,2,0],
    [2,1,3,3,3,1,1,2],  # bright petals
    [0,1,3,1,3,1,1,0],  # flower detail
    [0,2,1,3,3,1,2,0],
    [0,0,2,1,1,2,0,0],
    [2,1,0,1,2,1,0,1],
    [0,1,2,1,0,1,2,1],
]

GRASS_CLOVER = [
    [0,3,2,0,0,2,3,0],  # vibrant clover field
    [3,1,1,3,3,1,1,3],
    [2,1,3,1,1,3,1,2],  # varied flowers
    [0,3,1,3,3,1,3,0],
    [0,2,3,1,1,3,2,0],
    [2,1,0,1,2,1,0,1],
    [0,1,2,1,0,1,2,1],
    [2,1,0,1,2,1,0,1],
]

PATH_TILE = [
    [3,3,3,3,3,3,3,3],  # dirt path with detail
    [3,3,2,3,3,2,3,3],  # pebble pattern
    [3,2,3,3,3,3,2,3],  # worn texture
    [3,3,3,3,3,3,3,3],
    [3,3,2,3,3,2,3,3],
    [3,2,3,3,3,3,2,3],  # footprint effect
    [3,3,3,3,3,3,3,3],
    [3,2,3,3,3,3,2,3],
]

PATH_TOP_EDGE = [
    [1,1,1,1,1,1,1,1],  # grass border top
    [1,0,0,0,0,0,0,1],  # transition zone
    [3,3,3,3,3,3,3,3],  # path begins
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
]

PATH_BOT_EDGE = [
    [3,3,3,3,3,3,3,3],  # path ends
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [1,0,0,0,0,0,0,1],  # transition zone
    [1,1,1,1,1,1,1,1],  # grass border bottom
    [2,2,2,2,2,2,2,2],  # shadow line
]

ROCK_BIG = [
    [0,0,2,2,2,2,0,0],  # rugged boulder
    [0,2,2,1,1,2,2,0],
    [2,2,1,1,1,1,2,2],  # cracks & shadow detail
    [2,2,1,3,3,1,2,2],  # light reflection
    [2,2,1,1,1,1,2,2],
    [2,2,1,1,3,1,2,2],  # surface texture
    [0,2,2,1,1,2,2,0],
    [0,0,2,2,2,2,0,0],
]

ROCK_SMALL = [
    [0,0,0,0,0,0,0,0],  # small pebble
    [0,0,2,2,2,0,0,0],
    [0,2,2,1,2,2,0,0],  # varied shading
    [0,2,1,1,1,2,0,0],
    [0,2,2,1,2,2,0,0],
    [0,0,2,2,2,0,0,0],
    [1,0,0,0,0,0,0,1],
    [0,1,1,1,1,1,1,0],
]

TREE_TOP = [
    [0,0,2,2,2,0,0,0],  # dense green foliage
    [0,2,2,1,2,2,0,0],
    [2,2,1,1,1,2,2,0],
    [2,2,1,3,1,2,2,0],  # light gaps in canopy
    [2,2,1,1,1,2,2,0],
    [0,2,2,1,2,2,0,0],
    [0,0,2,2,2,0,0,0],
    [0,0,0,0,0,0,0,0],
]

TREE_BOT = [
    [0,0,0,3,0,0,0,0],  # detailed tree trunk
    [0,0,3,3,3,0,0,0],  # trunk widens
    [0,0,3,2,3,0,0,0],  # bark texture
    [0,3,3,2,3,3,0,0],  # roots begin
    [0,3,2,2,2,3,0,0],  # root detail
    [3,3,1,1,1,3,3,0],  # base/roots
    [3,3,1,2,1,3,3,0],  # ground connection
    [3,3,1,1,1,3,3,0],
]

MUSHROOM = [
    [0,0,2,2,2,0,0,0],  # red toadstool cap
    [0,2,2,2,2,2,0,0],
    [2,2,1,1,1,2,2,0],  # white spots
    [2,2,1,1,1,2,2,0],
    [0,2,2,1,2,2,0,0],
    [0,0,0,3,0,0,0,0],  # stem
    [0,0,3,3,3,0,0,0],  # wide stem base
    [0,0,3,1,3,0,0,0],  # ground texture
]

BG_FLOWER = [
    [0,0,0,3,0,0,0,0],  # wildflower accent
    [0,0,3,3,3,0,0,0],
    [0,3,3,2,3,3,0,0],  # vibrant center
    [3,3,2,1,2,3,3,0],  # detailed core
    [0,3,3,3,3,3,0,0],
    [0,0,3,3,3,0,0,0],
    [0,0,0,3,0,0,0,0],
    [0,0,0,2,0,0,0,0],
]

UI_BLANK = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

HEART_FULL = [
    [0,0,3,3,0,3,3,0],  # bright vibrant heart
    [0,3,3,3,3,3,3,0],
    [3,3,3,3,3,3,3,3],  # solid filled
    [3,3,3,2,2,3,3,3],  # highlight reflection
    [3,3,3,3,3,3,3,3],
    [0,3,3,3,3,3,3,0],
    [0,0,3,3,3,3,0,0],
    [0,0,0,3,3,0,0,0],
]

HEART_EMPTY = [
    [0,0,2,2,0,2,2,0],  # outlined heart
    [0,2,0,0,0,0,2,0],
    [2,0,0,0,0,0,0,2],  # hollow with shadow
    [2,0,0,1,1,0,0,2],  # depth indicator
    [2,0,0,0,0,0,0,2],
    [0,2,0,0,0,0,2,0],
    [0,0,2,1,1,2,0,0],
    [0,0,0,2,2,0,0,0],
]

GIFT_ICON_BG = [
    [0,3,3,3,3,3,0,0],  # bright gift icon
    [3,2,2,2,2,3,3,0],
    [3,2,1,1,2,3,3,0],  # detailed ribbon
    [3,2,1,1,2,3,3,0],
    [3,2,2,2,2,3,3,0],
    [0,3,3,3,3,3,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

STAR_ICON_BG = [
    [0,0,0,3,0,0,0,0],  # bright star icon
    [0,0,3,2,3,0,0,0],
    [0,3,2,2,2,3,0,0],  # full detail
    [3,2,2,1,2,2,3,0],  # highlight
    [0,3,2,2,2,3,0,0],
    [0,0,3,2,3,0,0,0],
    [0,0,0,3,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

BORDER_H = [
    [3,3,3,3,3,3,3,3],  # darker border
    [3,2,2,2,2,2,2,3],  # gradient effect
    [3,2,1,1,1,1,2,3],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

ARROW_RIGHT = [
    [0,0,0,0,0,0,0,0],  # bold arrow
    [0,0,3,0,0,0,0,0],
    [0,0,3,3,0,0,0,0],
    [0,0,3,3,3,0,0,0],  # bright indicator
    [0,0,3,3,0,0,0,0],
    [0,0,3,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

# Digits
def digit_pixels(n: int):
    """Return 8x8 pixel array for digit 0-9"""
    digits = {
        0: [[0,1,1,1,1,1,0,0],
            [1,0,0,0,0,0,1,0],
            [1,0,0,0,0,0,1,0],
            [1,0,0,0,0,0,1,0],
            [1,0,0,0,0,0,1,0],
            [1,0,0,0,0,0,1,0],
            [0,1,1,1,1,1,0,0],
            [0,0,0,0,0,0,0,0]],
        1: [[0,0,0,1,0,0,0,0],
            [0,0,1,1,0,0,0,0],
            [0,1,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0,0],
            [0,1,1,1,1,0,0,0],
            [0,0,0,0,0,0,0,0]],
    }
    return digits.get(n, [[0]*8 for _ in range(8)])

# Mapping for easy lookup by tile index
TILE_PIXELS = {}

def _build_tile_map():
    """Build mapping of tile indices to pixel data"""
    import tiles as tiles_module
    global TILE_PIXELS

    # OBJ tiles
    TILE_PIXELS[getattr(tiles_module, 'TL_BUNNY_T_F1', 0x00)] = BUNNY_TOP_F1
    TILE_PIXELS[getattr(tiles_module, 'TL_BUNNY_B_F1', 0x01)] = BUNNY_BOT_F1
    TILE_PIXELS[getattr(tiles_module, 'TL_BUNNY_T_F2', 0x02)] = BUNNY_TOP_F2
    TILE_PIXELS[getattr(tiles_module, 'TL_BUNNY_B_F2', 0x03)] = BUNNY_BOT_F2
    TILE_PIXELS[getattr(tiles_module, 'TL_GIFT', 0x04)] = GIFT_OBJ
    TILE_PIXELS[getattr(tiles_module, 'TL_STAR', 0x05)] = STAR_OBJ
    TILE_PIXELS[getattr(tiles_module, 'TL_FLOWER_OBJ', 0x06)] = FLOWER_OBJ
    TILE_PIXELS[getattr(tiles_module, 'TL_CURSOR', 0x07)] = STAR_OBJ

    # BG tiles
    TILE_PIXELS[getattr(tiles_module, 'TL_GRASS_PLAIN', 0x10)] = GRASS_PLAIN
    TILE_PIXELS[getattr(tiles_module, 'TL_GRASS_TUFT', 0x11)] = GRASS_TUFT
    TILE_PIXELS[getattr(tiles_module, 'TL_GRASS_CLOVER', 0x12)] = GRASS_CLOVER
    TILE_PIXELS[getattr(tiles_module, 'TL_PATH', 0x13)] = PATH_TILE
    TILE_PIXELS[getattr(tiles_module, 'TL_PATH_TOP', 0x14)] = PATH_TOP_EDGE
    TILE_PIXELS[getattr(tiles_module, 'TL_PATH_BOT', 0x15)] = PATH_BOT_EDGE
    TILE_PIXELS[getattr(tiles_module, 'TL_ROCK', 0x16)] = ROCK_BIG
    TILE_PIXELS[getattr(tiles_module, 'TL_ROCK_SMALL', 0x17)] = ROCK_SMALL
    TILE_PIXELS[getattr(tiles_module, 'TL_TREE_TOP', 0x18)] = TREE_TOP
    TILE_PIXELS[getattr(tiles_module, 'TL_TREE_BOT', 0x19)] = TREE_BOT
    TILE_PIXELS[getattr(tiles_module, 'TL_MUSHROOM', 0x1A)] = MUSHROOM
    TILE_PIXELS[getattr(tiles_module, 'TL_BG_FLOWER', 0x1B)] = BG_FLOWER
    TILE_PIXELS[getattr(tiles_module, 'TL_BG_BLANK', 0x1C)] = UI_BLANK
    TILE_PIXELS[getattr(tiles_module, 'TL_HEART_FULL', 0x1D)] = HEART_FULL
    TILE_PIXELS[getattr(tiles_module, 'TL_HEART_EMPTY', 0x1E)] = HEART_EMPTY
    TILE_PIXELS[getattr(tiles_module, 'TL_GIFT_ICON', 0x1F)] = GIFT_ICON_BG
    TILE_PIXELS[getattr(tiles_module, 'TL_STAR_ICON_BG', 0x20)] = STAR_ICON_BG
    TILE_PIXELS[getattr(tiles_module, 'TL_BORDER_H', 0x21)] = BORDER_H
    TILE_PIXELS[getattr(tiles_module, 'TL_ARROW', 0x22)] = ARROW_RIGHT

    # Digits
    digit_start = getattr(tiles_module, 'TL_DIGIT_0', 0x23)
    for n in range(10):
        TILE_PIXELS[digit_start + n] = digit_pixels(n)

_build_tile_map()
