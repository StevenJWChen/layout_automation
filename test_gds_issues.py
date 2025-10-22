#!/usr/bin/env python3
"""
Test script to reproduce and diagnose GDS import/export issues:
1. Cell name 'top' causing issues
2. Polygon position shift after import
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("Testing GDS Import/Export Issues")
print("="*70)

# ==============================================================================
# Test 1: Cell named 'top'
# ==============================================================================
print("\n" + "="*70)
print("Test 1: Cell named 'top'")
print("="*70)

# Create a cell named 'top'
top = Cell('top')

# Add a child
child = Cell('child1', 'metal1')
top.add_instance(child)

# Set direct constraints (avoid solver issues)
top.constrain('x1=0, y1=0, x2=100, y2=100')
child.constrain('x1=10, y1=10, x2=40, y2=30')

# Solve and check positions
print("\nOriginal layout:")
top.solver()
print(f"  top.pos_list = {top.pos_list}")
print(f"  child1.pos_list = {child.pos_list}")

# Export to GDS
gds_file = 'test_top_cell.gds'
print(f"\nExporting to {gds_file}...")
try:
    top.export_gds(gds_file, use_tech_file=False)
    print("  ✓ Export succeeded")
except Exception as e:
    print(f"  ✗ Export failed: {e}")

# Import back
print(f"\nImporting from {gds_file}...")
try:
    top_imported = Cell.from_gds(gds_file, use_tech_file=False)
    print(f"  ✓ Import succeeded")
    print(f"  Imported cell name: {top_imported.name}")
    print(f"  Imported cell pos_list: {top_imported.pos_list}")
    if top_imported.children:
        print(f"  Child count: {len(top_imported.children)}")
        for i, child in enumerate(top_imported.children):
            print(f"    child[{i}]: {child.name}, pos_list={child.pos_list}")
except Exception as e:
    print(f"  ✗ Import failed: {e}")

# ==============================================================================
# Test 2: Polygon position shift
# ==============================================================================
print("\n" + "="*70)
print("Test 2: Polygon position shift")
print("="*70)

# Create layout with precise floating point positions
parent = Cell('parent')

# Create children with fractional positions (common in real GDS)
rect1 = Cell('rect1', 'metal2')
rect2 = Cell('rect2', 'metal3')
rect3 = Cell('rect3', 'via1')

parent.add_instance(rect1)
parent.add_instance(rect2)
parent.add_instance(rect3)

# Use direct constraints with exact integer positions
parent.constrain('x1=0, y1=0, x2=200, y2=150')
rect1.constrain('x1=10, y1=20, x2=40, y2=35')
rect2.constrain('x1=50, y1=60, x2=75, y2=78')
rect3.constrain('x1=100, y1=100, x2=112, y2=112')

parent.solver()

print("\nOriginal positions (integer):")
print(f"  rect1: {rect1.pos_list}")
print(f"  rect2: {rect2.pos_list}")
print(f"  rect3: {rect3.pos_list}")

# Export
gds_file2 = 'test_positions.gds'
parent.export_gds(gds_file2, use_tech_file=False)

# Import
imported = Cell.from_gds(gds_file2, use_tech_file=False)

print("\nPositions after GDS round-trip:")
for child in imported.children:
    print(f"  {child.name}: {child.pos_list}")

# Check for shifts
print("\nChecking for position shifts:")
original_positions = {
    'rect1': [10, 20, 40, 35],
    'rect2': [50, 60, 75, 78],
    'rect3': [100, 100, 112, 112]
}

shift_detected = False
for child in imported.children:
    # Extract the base name (without suffixes added during import)
    base_name = None
    for orig_name in original_positions.keys():
        if orig_name in child.name:
            base_name = orig_name
            break

    if base_name and child.pos_list:
        orig = original_positions[base_name]
        imported_pos = child.pos_list

        # Check if positions match
        if orig != imported_pos:
            print(f"  ✗ SHIFT DETECTED in {base_name}:")
            print(f"    Original:  {orig}")
            print(f"    Imported:  {imported_pos}")
            print(f"    Delta:     {[imported_pos[i] - orig[i] for i in range(4)]}")
            shift_detected = True
        else:
            print(f"  ✓ {base_name}: No shift")

if not shift_detected:
    print("  ✓ No position shifts detected")

# ==============================================================================
# Test 3: Floating point positions (potential rounding issue)
# ==============================================================================
print("\n" + "="*70)
print("Test 3: Floating point positions (rounding test)")
print("="*70)

parent3 = Cell('parent3')

# Manually set fractional positions to simulate GDS with sub-unit precision
fract = Cell('fractional', 'metal1')
parent3.add_instance(fract)

parent3.constrain('x1=0, y1=0, x2=200, y2=150')
fract.constrain('x1=10, y1=20, x2=40, y2=35')
parent3.solver()

# Manually modify positions to have fractional values
print("\nManually setting fractional positions:")
print(f"  Original: {fract.pos_list}")
fract.pos_list = [10.7, 20.3, 40.9, 35.6]  # Fractional coordinates
print(f"  Modified: {fract.pos_list}")

# Export
gds_file3 = 'test_fractional.gds'
parent3.export_gds(gds_file3, use_tech_file=False)

# Import
imported3 = Cell.from_gds(gds_file3, use_tech_file=False)

print("\nPositions after import with rounding:")
for child in imported3.children:
    print(f"  {child.name}: {child.pos_list}")

# Expected after rounding: [11, 20, 41, 36]
expected_rounded = [11, 20, 41, 36]
actual = imported3.children[0].pos_list if imported3.children else None

if actual:
    print(f"\n  Expected (rounded): {expected_rounded}")
    print(f"  Actual:             {actual}")
    if actual == expected_rounded:
        print("  ✓ Rounding works as expected")
    else:
        print(f"  ✗ Unexpected result! Delta: {[actual[i] - expected_rounded[i] for i in range(4)]}")

# ==============================================================================
# Cleanup
# ==============================================================================
print("\n" + "="*70)
print("Cleaning up test files...")
for f in [gds_file, gds_file2, gds_file3]:
    if os.path.exists(f):
        os.remove(f)
        print(f"  Removed {f}")

print("\n" + "="*70)
print("Test complete!")
print("="*70)
