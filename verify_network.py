#!/usr/bin/env python3
"""Verify complete 3×3 zone road network."""

from road_generator import RoadGenerator, ZONE_NAMES

gen = RoadGenerator()
gen.generate()

print("\n🗺️  3×3 ZONE GRID LAYOUT\n")
print("     [0,2]         [1,2]        [2,2]")
print("     ↓↑            ↓↑            ↓↑")
print("  [SNOW_PEAK] ← → [CRYSTAL] ← → [SUNSET]")
print("     ↓↑            ↓↑            ↓↑")
print("  [GARDEN]   ← → [FOREST]  ← → [MEADOW]")
print("     ↓↑            ↓↑            ↓↑")
print("  [DESERT]   ← → [CAVE]    ← → [SWAMP]")
print("     [0,0]        [1,0]        [2,0]\n")

print("\n✅ CONNECTIVITY VERIFICATION:\n")

# Verify all zones have correct neighbors
expected_neighbors = {
    (0, 0): {"down", "right"},      # Snow Peak
    (0, 1): {"down", "left", "right"},  # Crystal Lake
    (0, 2): {"down", "left"},       # Sunset Sky
    (1, 0): {"up", "down", "right"},    # Garden
    (1, 1): {"up", "down", "left", "right"},  # Forest (center)
    (1, 2): {"up", "down", "left"},     # Meadow
    (2, 0): {"up", "right"},        # Desert
    (2, 1): {"up", "left", "right"},    # Cave
    (2, 2): {"up", "left"},         # Swamp
}

all_valid = True
for zone_pos, expected in expected_neighbors.items():
    actual = set(gen.connections[zone_pos].keys())
    zone_name = ZONE_NAMES[zone_pos]
    
    if actual == expected:
        print(f"✓ {zone_name:12} has {len(actual)} correct connections")
    else:
        print(f"✗ {zone_name:12} MISMATCH")
        print(f"  Expected: {expected}")
        print(f"  Got: {actual}")
        all_valid = False

if all_valid:
    print("\n✅ All zones have correct connectivity!")
else:
    print("\n❌ Some zones have incorrect connectivity!")

