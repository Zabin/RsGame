"""
worldgen.py — build-side Python reference-generator oracle (IP-1020).

Mirrors `generate_world` (asm_game.py) step-for-step: same PRNG state update,
same row-major visitation order, same neighbor-constraint/clamp logic. Consumed
only by test_rom.py (T12's oracle-parity check) — never imported by
build_rom.py/asm_game.py (GDS-09 delta, explicit — this is a test-only mirror,
not shared code).

Biome axis (9 families, linear grammar per the TWBS's resolved FS-102 OQ1,
widened from the original 5 per FR-4320/CR-08, IP-1022):
  0=Water 1=Sand 2=Grass 3=Stone 4=Brick 5=Village 6=Cave 7=Desert 8=Plains
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


def generate(seed: int, scale: int, _with_treasure: bool = False):
    """
    Deterministically generate a scale x scale region grid from (seed, scale).

    Returns a list of `scale*scale` dicts, row-major order (index = row*scale+col):
        {'biome_id': int (0-8), 'neighbors': [up, down, left, right]}
    where each neighbor is a region index (int) or None (grid boundary, 0xFF on
    the SM83 side).

    If `_with_treasure` is set, returns `(regions, treasure)` instead, where
    `treasure` is a `scale*scale`-length list mirroring KEYITEM_FLAGS's
    generation-time output (IP-1021/FR-9160): 0 = present, 2 = absent. Kept as
    an opt-in third argument (not a separate duplicated pipeline) so existing
    two-arg call sites are untouched.
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
            lo, hi = 0, 8
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
            if b > 8:
                b = 8
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

    treasure = _carve_maze(regions, scale, x)
    if _with_treasure:
        return regions, treasure
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

    Between the spanning-tree carve and the braid pass, also computes the
    IP-1021/FR-9160 KeyItem-placement pass (dead-end-priority with a random-
    fill fallback -- mirrors asm_game.py's `ki_passA_region`/`ki_passB_region`
    exactly): a region is a leaf iff no neighbor's `parent_dir` points back to
    it (reusing the same tree-edge test the braid pass below performs, just
    over all 4 directions instead of the canonical down/right pair, and run
    against the pre-braid neighbor lists since braiding can turn a leaf into
    a non-leaf by reopening a pruned edge). No PRNG draws are consumed by
    this pass -- returns the resulting `treasure` list (0=present, 2=absent),
    length `scale*scale`, in addition to mutating `regions` as before.
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

    # IP-1021: pre-braid leaf classification + placement (Pass A: leaves,
    # capped at `scale`; Pass B: fallback-fill from the first non-leaf
    # regions in index order if the leaf count fell short). Must run here --
    # after the spanning tree completes, before the braid pass below mutates
    # `regions`' neighbor lists.
    is_leaf = [True] * n
    for r in range(n):
        for d in range(4):
            v = regions[r]['neighbors'][d]
            if v is not None and parent_dir[v] == _OPPOSITE[d]:
                is_leaf[r] = False
                break

    treasure = [2] * n
    placed = 0
    for r in range(n):
        if is_leaf[r] and placed < scale:
            treasure[r] = 0
            placed += 1
    if placed < scale:
        for r in range(n):
            if not is_leaf[r]:
                if placed >= scale:
                    break
                treasure[r] = 0
                placed += 1

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

    return treasure


# ── Infinite Mode: per-region materialization (IP-1101) ──────────────────
# Independent of generate()/_carve_maze() above -- a second, additive
# generation routine (ADR-0016), not an extension of the finite mode's own
# whole-graph pass. Mirrors inf_materialize_region (asm_game.py) step-for-
# step.


def _region_seed0(seed, row, col):
    """Reseeds to hash(seed, row, col): SEED normalized 0->1, XORed with row
    then stepped once, XORed with col then stepped once (ADR-0016 point 3).
    Row/col are masked to 16 bits -- two's complement wraps naturally for
    negative values, matching the SM83 side's own 16-bit register
    arithmetic."""
    x = seed & 0xFFFF
    if x == 0:
        x = 1
    x ^= (row & 0xFFFF)
    x = _step(x)
    x ^= (col & 0xFFFF)
    x = _step(x)
    return x


def materialize_region(seed, row, col):
    """
    Deterministically materializes one region's biome-id, 4-direction
    connectivity, and treasure-presence as a pure function of
    (seed, row, col) -- no dependency on generation order or any other
    region's own history (NFR-2300).

    Returns (region_byte, treasure_present):
      region_byte -- bits 0-3 biome-id (0-4), bits 4-7 connectivity nibble
        (bit4=north/up, bit5=south/down, bit6=west/left, bit7=east/right,
        1=open); the TWBS's own per-region encoding decision, repacked
        IP-1105 (biome 0-2->0-3, connectivity 3-6->4-7) to free a fourth
        biome-id bit for FR-4320's widened domain -- value range itself
        stays %5, unchanged by this repack.
      treasure_present -- bool, hash(seed,row,col) mod 16 == 0 (K=16,
        ADR-0017/TWBS's own resolution of FS-110 Open Question 2).

    Binary Tree maze (ADR-0016 point 5, zero-memory): this region's own
    carve-bias decides whether it opens north or west; south/east openness
    is read from the south/east neighbor's own carve-bias (the neighbor on
    that side is the one that "decides" the shared edge). No grid-boundary
    special case is ever needed -- Infinite Mode's world is unbounded, every
    direction always has a real, materializable neighbor -- unlike the
    finite mode's own bounded carve pass (`_carve_maze` above, IP-1070).

    Own-region draws are sequential from one reseed (biome, own carve-bias,
    treasure-presence), not three independent reseeds -- a second reseed of
    the identical (seed,row,col) would reproduce the exact same first-drawn
    byte, correlating treasure with biome/connectivity instead of keeping it
    independent (a real defect an earlier draft of this routine, and the
    planning package's own text, both had -- caught and fixed during
    implementation, not shipped).
    """
    x0 = _region_seed0(seed, row, col)
    x1 = _step(x0)
    biome = (x1 & 0xFF) % 5
    x2 = _step(x1)
    own_bias = x2 & 1          # 0 = carve north (open north), 1 = carve west
    x3 = _step(x2)
    treasure_present = ((x3 & 0xFF) & 0x0F) == 0

    s0 = _region_seed0(seed, row + 1, col)
    s1 = _step(s0)             # discarded (that region's own biome draw)
    s2 = _step(s1)
    south_bias = s2 & 1
    open_south = (south_bias == 0)

    e0 = _region_seed0(seed, row, col + 1)
    e1 = _step(e0)             # discarded
    e2 = _step(e1)
    east_bias = e2 & 1
    open_east = (east_bias == 1)

    open_north = (own_bias == 0)
    open_west = (own_bias == 1)

    conn = ((0x10 if open_north else 0) | (0x20 if open_south else 0) |
            (0x40 if open_west else 0) | (0x80 if open_east else 0))
    region_byte = (biome & 0x0F) | conn
    return region_byte, treasure_present

    return treasure
