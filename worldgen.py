"""
worldgen.py — build-side Python reference-generator oracle (IP-1020).

Mirrors `generate_world` (asm_game.py) step-for-step: same PRNG state update,
same row-major visitation order, same neighbor-constraint/clamp logic. Consumed
only by test_rom.py (T12's oracle-parity check) — never imported by
build_rom.py/asm_game.py (GDS-09 delta, explicit — this is a test-only mirror,
not shared code).

Biome axis (5 families, linear grammar per the TWBS's resolved FS-102 OQ1):
  0=Water 1=Sand 2=Grass 3=Stone 4=Brick
Adjacency is grammar-legal iff axis indices differ by at most 1.
"""


def _step(x):
    """One xorshift-style PRNG step. Shift+XOR only, no multiply/divide (NFR-2200)."""
    x &= 0xFFFF
    x ^= (x << 1) & 0xFFFF
    x ^= (x >> 1)
    x ^= ((x << 8) | (x >> 8)) & 0xFFFF
    return x & 0xFFFF


def _draw_delta(x):
    """Steps the PRNG once; returns (new_state, delta) with delta in {-1, 0, +1}."""
    x = _step(x)
    m = (x & 0xFF) % 3
    delta = m - 1
    return x, delta


def generate(seed: int, scale: int):
    """
    Deterministically generate a scale x scale region grid from (seed, scale).

    Returns a list of `scale*scale` dicts, row-major order (index = row*scale+col):
        {'biome_id': int (0-4), 'neighbors': [up, down, left, right]}
    where each neighbor is a region index (int) or None (grid boundary, 0xFF on
    the SM83 side).
    """
    assert 2 <= scale <= 9
    x = seed & 0xFFFF
    if x == 0:
        x = 1

    n = scale * scale
    biome = [0] * n
    biome[0] = 2  # region (0,0) is always Grass — matches the shipped world's default

    for row in range(scale):
        for col in range(scale):
            i = row * scale + col
            if i == 0:
                continue
            lo, hi = 0, 4
            top = biome[(row - 1) * scale + col] if row > 0 else None
            left = biome[row * scale + (col - 1)] if col > 0 else None
            if top is not None:
                lo = max(lo, top - 1)
                hi = min(hi, top + 1)
            if left is not None:
                lo = max(lo, left - 1)
                hi = min(hi, left + 1)
            assert lo <= hi, "constraint intersection must never be empty by construction"

            x, delta = _draw_delta(x)
            anchor = left if left is not None else top
            b = anchor + delta
            if b < 0:
                b = 0
            if b > 4:
                b = 4
            if b < lo:
                b = lo
            if b > hi:
                b = hi
            biome[i] = b

    regions = []
    for row in range(scale):
        for col in range(scale):
            i = row * scale + col
            up = i - scale if row > 0 else None
            down = i + scale if row < scale - 1 else None
            left_n = i - 1 if col > 0 else None
            right_n = i + 1 if col < scale - 1 else None
            regions.append({
                'biome_id': biome[i],
                'neighbors': [up, down, left_n, right_n],
            })
    return regions
