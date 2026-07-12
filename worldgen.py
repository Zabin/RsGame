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
    """One xorshift-style PRNG step. Shift+XOR only, no multiply/divide (NFR-2200).

    Period-sound 7,9,8 shift triplet (BL-0074/ADR-0014/IP-9110) -- mirrors
    gw_prng_step's corrected mixing step exactly. The previously-shipped
    x^=x<<1;x^=x>>1;x^=byteswap(x) sequence forced hi==lo on every call (R113);
    fixed here.
    """
    x &= 0xFFFF
    x ^= (x << 7) & 0xFFFF
    x ^= (x >> 9)
    x ^= (x << 8) & 0xFFFF
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

    _carve_maze(regions, scale, x)
    return regions


_GW_BRAID_THRESHOLD = 63  # ~63/255 -> reopen ~25% of pruned edges (FR-9150 default)
_OPPOSITE = (1, 0, 3, 2)  # index by direction 0=up,1=down,2=left,3=right


def _carve_maze(regions, scale, x):
    """
    Mirrors generate_world's maze-generation pass (IP-1070, ADR-0012/ADR-0013)
    step-for-step: a randomized DFS/recursive-backtracker spanning tree
    (reusing the already-built full-lattice `neighbors` lists above as the
    "does a grid-adjacent region exist here" test, exactly as the SM83 side
    reuses REGION_GRAPH's own already-written candidate bytes), then a
    canonical-edge (down=1/right=3 only, so each undirected edge is decided
    exactly once) braid/prune pass. Every PRNG draw is perturbed with the
    same loop-local, never-persisted counter (step 97, XORed in) the SM83
    side uses, per ADR-0013 -- this is the load-bearing lockstep property
    (FS-107 §14): a mismatched counter sequence would desync which edges get
    reopened even if both sides independently draw "correct" PRNG bytes.
    Mutates `regions`' neighbor lists in place (writes None where the SM83
    side would write 0xFF). Discards the advanced PRNG state -- this is the
    generator's own last step, nothing downstream consumes it further.
    """
    n = scale * scale
    visited = [False] * n
    parent_dir = [0] * n  # meaningful for every index by the time carving completes
    draw_ctr = 0

    def perturb(raw_low_byte):
        nonlocal draw_ctr
        p = (raw_low_byte ^ draw_ctr) & 0xFF
        draw_ctr = (draw_ctr + 97) & 0xFF
        return p

    # maze_init
    visited[0] = True
    cur = 0

    # spanning-tree carve (iterative -- mirrors maze_carve_top/maze_try_loop/
    # maze_backtrack exactly: one PRNG draw per entry to "current region",
    # whether reached by a fresh carve or by backtracking)
    while True:
        x = _step(x)
        start_dir = perturb(x & 0xFF) & 3
        carved = False
        for k in range(4):
            d = (start_dir + k) & 3
            cand = regions[cur]['neighbors'][d]
            if cand is None or visited[cand]:
                continue
            visited[cand] = True
            parent_dir[cand] = _OPPOSITE[d]
            cur = cand
            carved = True
            break
        if carved:
            continue
        if cur == 0:
            break  # root exhausted with nothing left to carve -- tree complete
        cur = regions[cur]['neighbors'][parent_dir[cur]]  # backtrack

    # canonical-edge braid/prune pass (down=1, right=3 only -- each undirected
    # edge decided exactly once; every region is visited by this point, so no
    # visited[] guard is needed on either side of the tree-edge test, mirroring
    # the SM83 side's own unconditional Check 1/Check 2)
    for r in range(n):
        for d in (1, 3):
            v = regions[r]['neighbors'][d]
            if v is None:
                continue
            is_tree_edge = (parent_dir[v] == _OPPOSITE[d]) or (parent_dir[r] == d)
            if is_tree_edge:
                continue
            x = _step(x)
            perturbed = perturb(x & 0xFF)
            if perturbed <= _GW_BRAID_THRESHOLD:
                continue  # reopen -- leave both slots as-is
            regions[r]['neighbors'][d] = None
            regions[v]['neighbors'][_OPPOSITE[d]] = None

    return x
