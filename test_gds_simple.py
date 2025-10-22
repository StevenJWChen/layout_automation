#!/usr/bin/env python3
"""
Simplified GDS test with manual position setting
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Import/Export Test - Manual Positions")
print("="*70)

# ==============================================================================
# Test 1: Cell named 'top' with manual positions
# ==============================================================================
print("\n" + "="*70)
print("Test 1: Cell named 'top'")
print("="*70)

# Create a cell named 'top'
top = Cell('top')
child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'metal2')

# Add children using *args in constructor
top = Cell('top', child1, child2)

# Manually set positions (bypass solver)
top.pos_list = [0, 0, 100, 100]
child1.pos_list = [10, 10, 40, 30]
child2.pos_list = [50, 50, 80, 90]

print("\nOriginal layout:")
print(f"  top: {top.pos_list}")
print(f"  child1: {child1.pos_list}")
print(f"  child2: {child2.pos_list}")

# Export to GDS
gds_file = 'test_top.gds'
print(f"\nExporting to {gds_file}...")
top.export_gds(gds_file, use_tech_file=False)
print("  ✓ Export succeeded")

# Import back
print(f"\nImporting from {gds_file}...")
top_imported = Cell.from_gds(gds_file, use_tech_file=False)
print(f"  ✓ Import succeeded")
print(f"  Imported cell name: '{top_imported.name}'")
print(f"  Imported pos_list: {top_imported.pos_list}")
print(f"  Number of children: {len(top_imported.children)}")

for i, child in enumerate(top_imported.children):
    print(f"    child[{i}]: name='{child.name}', pos_list={child.pos_list}, layer={child.layer_name}")

# Compare positions
print("\nPosition comparison:")
if len(top_imported.children) >= 2:
    # Convert to sets of tuples for comparison
    imported_set = {tuple(c.pos_list) for c in top_imported.children}
    expected_set = {(10, 10, 40, 30), (50, 50, 80, 90)}

    if imported_set == expected_set:
        print("  ✓ Child positions match exactly!")
    else:
        print("  ✗ Position mismatch!")
        print(f"    Expected: {expected_set}")
        print(f"    Got:      {imported_set}")
        print(f"    Missing:  {expected_set - imported_set}")
        print(f"    Extra:    {imported_set - expected_set}")
else:
    print(f"  ✗ Expected 2 children, got {len(top_imported.children)}")

# ==============================================================================
# Test 2: Cell named 'my_layout' (non-'top' name for comparison)
# ==============================================================================
print("\n" + "="*70)
print("Test 2: Cell named 'my_layout' (control)")
print("="*70)

# Create same structure with different name
layout = Cell('my_layout')
rect1 = Cell('rect1', 'metal1')
rect2 = Cell('rect2', 'metal2')

layout = Cell('my_layout', rect1, rect2)

# Same positions
layout.pos_list = [0, 0, 100, 100]
rect1.pos_list = [10, 10, 40, 30]
rect2.pos_list = [50, 50, 80, 90]

print("\nOriginal layout:")
print(f"  my_layout: {layout.pos_list}")
print(f"  rect1: {rect1.pos_list}")
print(f"  rect2: {rect2.pos_list}")

# Export
gds_file2 = 'test_my_layout.gds'
layout.export_gds(gds_file2, use_tech_file=False)

# Import
imported2 = Cell.from_gds(gds_file2, use_tech_file=False)
print(f"\nImported cell name: '{imported2.name}'")
print(f"  Number of children: {len(imported2.children)}")

for i, child in enumerate(imported2.children):
    print(f"    child[{i}]: name='{child.name}', pos_list={child.pos_list}")

# ==============================================================================
# Test 3: Floating point rounding
# ==============================================================================
print("\n" + "="*70)
print("Test 3: Floating point position rounding")
print("="*70)

fract_layout = Cell('fract_layout')
fract_cell = Cell('fract_cell', 'metal1')
fract_layout = Cell('fract_layout', fract_cell)

# Set fractional positions
fract_layout.pos_list = [0.0, 0.0, 100.0, 100.0]
fract_cell.pos_list = [10.7, 20.3, 40.9, 35.6]

print("\nOriginal (with fractions):")
print(f"  fract_cell: {fract_cell.pos_list}")

# Export
gds_file3 = 'test_fractional.gds'
fract_layout.export_gds(gds_file3, use_tech_file=False)

# Import
imported3 = Cell.from_gds(gds_file3, use_tech_file=False)
imported_fract = imported3.children[0] if imported3.children else None

if imported_fract:
    print(f"\nAfter GDS round-trip:")
    print(f"  fract_cell: {imported_fract.pos_list}")
    print(f"\nRounding analysis:")
    print(f"  10.7 -> {imported_fract.pos_list[0]} (expected: 11)")
    print(f"  20.3 -> {imported_fract.pos_list[1]} (expected: 20)")
    print(f"  40.9 -> {imported_fract.pos_list[2]} (expected: 41)")
    print(f"  35.6 -> {imported_fract.pos_list[3]} (expected: 36)")

    # Check for errors
    expected = [11, 20, 41, 36]
    actual = imported_fract.pos_list
    errors = [actual[i] - expected[i] for i in range(4)]

    if any(e != 0 for e in errors):
        print(f"\n  ✗ Rounding errors detected: {errors}")
    else:
        print(f"\n  ✓ Rounding correct")

# ==============================================================================
# Test 4: Nested hierarchy
# ==============================================================================
print("\n" + "="*70)
print("Test 4: Nested hierarchy with 'top' name")
print("="*70)

# Create 3-level hierarchy with 'top' as root
top_level = Cell('top')
mid_level = Cell('middle')
leaf1 = Cell('leaf1', 'metal1')
leaf2 = Cell('leaf2', 'metal2')

# Build hierarchy
mid_level = Cell('middle', leaf1, leaf2)
top_level = Cell('top', mid_level)

# Set positions
top_level.pos_list = [0, 0, 200, 200]
mid_level.pos_list = [10, 10, 100, 100]
leaf1.pos_list = [20, 20, 40, 40]
leaf2.pos_list = [50, 50, 80, 80]

print("\nOriginal hierarchy:")
print(f"  top: {top_level.pos_list}")
print(f"  middle: {mid_level.pos_list}")
print(f"  leaf1: {leaf1.pos_list}")
print(f"  leaf2: {leaf2.pos_list}")

# Export
gds_file4 = 'test_hierarchy.gds'
top_level.export_gds(gds_file4, use_tech_file=False)

# Import
imported4 = Cell.from_gds(gds_file4, use_tech_file=False)
print(f"\nImported:")
print(f"  Root name: '{imported4.name}'")
print(f"  Root children: {len(imported4.children)}")

if imported4.children:
    mid_imported = imported4.children[0]
    print(f"  First child: '{mid_imported.name}'")
    print(f"  First child has {len(mid_imported.children)} children")

# ==============================================================================
# Cleanup
# ==============================================================================
print("\n" + "="*70)
print("Cleaning up...")
for f in [gds_file, gds_file2, gds_file3, gds_file4]:
    if os.path.exists(f):
        os.remove(f)
print("Done!")
print("="*70)
