#!/usr/bin/env python3
"""
Deep investigation of GDS position shift issue
Testing with real cell positions to find the actual shift
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Position Shift - Deep Investigation")
print("="*70)

# ==============================================================================
# Test 1: Simple absolute positions - no hierarchy
# ==============================================================================
print("\n" + "="*70)
print("Test 1: Simple leaf cells with absolute positions")
print("="*70)

# Create simple leaf cells at specific positions
parent = Cell('chip')
rect1 = Cell('rect1', 'metal1')
rect2 = Cell('rect2', 'metal2')
rect3 = Cell('rect3', 'metal3')

parent = Cell('chip', rect1, rect2, rect3)

# Set absolute positions (integers)
parent.pos_list = [0, 0, 1000, 1000]
rect1.pos_list = [100, 200, 300, 400]
rect2.pos_list = [500, 600, 700, 800]
rect3.pos_list = [50, 50, 150, 150]

print("\nOriginal positions:")
print(f"  rect1: {rect1.pos_list}")
print(f"  rect2: {rect2.pos_list}")
print(f"  rect3: {rect3.pos_list}")

# Export
gds_file = 'test_shift1.gds'
parent.export_gds(gds_file, use_tech_file=False)
print(f"\nExported to {gds_file}")

# Import
imported = Cell.from_gds(gds_file, use_tech_file=False)

print("\nImported positions:")
for child in imported.children:
    print(f"  {child.name}: {child.pos_list}")

# Check for shifts
print("\nShift analysis:")
original = {
    'rect1': [100, 200, 300, 400],
    'rect2': [500, 600, 700, 800],
    'rect3': [50, 50, 150, 150]
}

for child in imported.children:
    for orig_name, orig_pos in original.items():
        if orig_name in child.name:
            shift = [child.pos_list[i] - orig_pos[i] for i in range(4)]
            if any(s != 0 for s in shift):
                print(f"  ✗ {orig_name}: SHIFT {shift}")
            else:
                print(f"  ✓ {orig_name}: No shift")
            break

# ==============================================================================
# Test 2: Check what's actually in the GDS file
# ==============================================================================
print("\n" + "="*70)
print("Test 2: Examining GDS file structure")
print("="*70)

import gdstk

lib = gdstk.read_gds(gds_file)

print(f"\nGDS Library: {lib.name}")
print(f"Number of cells: {len(lib.cells)}")

for cell in lib.cells:
    print(f"\nCell: '{cell.name}'")
    print(f"  Polygons: {len(cell.polygons)}")

    for i, poly in enumerate(cell.polygons):
        bbox = poly.bounding_box()
        print(f"    Polygon {i}: layer={poly.layer}, bbox={bbox}")
        print(f"      Points: {poly.points}")

    print(f"  References: {len(cell.references)}")
    for i, ref in enumerate(cell.references):
        print(f"    Ref {i}: to '{ref.cell.name}', origin={ref.origin}")

# ==============================================================================
# Test 3: Export/Import with hierarchy
# ==============================================================================
print("\n" + "="*70)
print("Test 3: Hierarchical cells")
print("="*70)

# Create hierarchical structure
top = Cell('top_cell')
mid1 = Cell('mid_level1')
mid2 = Cell('mid_level2')
leaf1 = Cell('leaf1', 'metal1')
leaf2 = Cell('leaf2', 'metal2')
leaf3 = Cell('leaf3', 'metal3')

# Build hierarchy
mid1 = Cell('mid_level1', leaf1, leaf2)
mid2 = Cell('mid_level2', leaf3)
top = Cell('top_cell', mid1, mid2)

# Set positions
top.pos_list = [0, 0, 2000, 2000]
mid1.pos_list = [100, 100, 500, 500]
mid2.pos_list = [600, 600, 900, 900]
leaf1.pos_list = [150, 150, 250, 250]
leaf2.pos_list = [300, 300, 450, 450]
leaf3.pos_list = [650, 650, 850, 850]

print("\nOriginal hierarchy:")
print(f"  top_cell: {top.pos_list}")
print(f"    mid_level1: {mid1.pos_list}")
print(f"      leaf1: {leaf1.pos_list}")
print(f"      leaf2: {leaf2.pos_list}")
print(f"    mid_level2: {mid2.pos_list}")
print(f"      leaf3: {leaf3.pos_list}")

# Export
gds_file2 = 'test_shift_hierarchy.gds'
top.export_gds(gds_file2, use_tech_file=False)

# Import
imported2 = Cell.from_gds(gds_file2, use_tech_file=False)

print("\nImported hierarchy:")
print(f"  {imported2.name}: {imported2.pos_list}")

def print_hierarchy(cell, indent=2):
    for child in cell.children:
        print(f"{' '*indent}{child.name}: {child.pos_list}")
        print_hierarchy(child, indent+2)

print_hierarchy(imported2)

# Check for position shifts in leaf cells
print("\nLeaf position analysis:")
original_leaves = {
    'leaf1': [150, 150, 250, 250],
    'leaf2': [300, 300, 450, 450],
    'leaf3': [650, 650, 850, 850]
}

def check_leaves(cell, original_dict):
    for child in cell.children:
        if child.is_leaf:
            for orig_name, orig_pos in original_dict.items():
                if orig_name in child.name:
                    shift = [child.pos_list[i] - orig_pos[i] for i in range(4)]
                    if any(s != 0 for s in shift):
                        print(f"  ✗ {orig_name}: {child.pos_list} (shift: {shift})")
                    else:
                        print(f"  ✓ {orig_name}: {child.pos_list} (no shift)")
                    break
        else:
            check_leaves(child, original_dict)

check_leaves(imported2, original_leaves)

# ==============================================================================
# Test 4: What happens with non-leaf cells containing polygons?
# ==============================================================================
print("\n" + "="*70)
print("Test 4: Direct polygon positions in GDS")
print("="*70)

# Read the first GDS file and check actual polygon coordinates
lib1 = gdstk.read_gds(gds_file)

print("\nAnalyzing polygon coordinates in GDS:")
for cell in lib1.cells:
    if cell.polygons:
        print(f"\nCell '{cell.name}' contains polygons:")
        for poly in cell.polygons:
            bbox = poly.bounding_box()
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]
            print(f"  Polygon bbox in GDS: ({x1}, {y1}) to ({x2}, {y2})")
            print(f"  Polygon points: {poly.points}")

# ==============================================================================
# Test 5: Check if parent bounding box affects child positions
# ==============================================================================
print("\n" + "="*70)
print("Test 5: Parent bounding box effect")
print("="*70)

# Create case where parent bbox doesn't start at (0,0)
offset_parent = Cell('offset_parent')
child_a = Cell('child_a', 'metal1')
child_b = Cell('child_b', 'metal2')

offset_parent = Cell('offset_parent', child_a, child_b)

# Parent starts at (1000, 1000), not (0, 0)
offset_parent.pos_list = [1000, 1000, 2000, 2000]
child_a.pos_list = [1100, 1100, 1300, 1300]
child_b.pos_list = [1500, 1500, 1800, 1800]

print("\nOriginal (parent bbox NOT at origin):")
print(f"  offset_parent: {offset_parent.pos_list}")
print(f"  child_a: {child_a.pos_list}")
print(f"  child_b: {child_b.pos_list}")

gds_file3 = 'test_offset_parent.gds'
offset_parent.export_gds(gds_file3, use_tech_file=False)

imported3 = Cell.from_gds(gds_file3, use_tech_file=False)

print("\nImported:")
print(f"  {imported3.name}: {imported3.pos_list}")
for child in imported3.children:
    print(f"  {child.name}: {child.pos_list}")

print("\nShift analysis:")
if imported3.children:
    for child in imported3.children:
        if 'child_a' in child.name:
            orig = [1100, 1100, 1300, 1300]
            shift = [child.pos_list[i] - orig[i] for i in range(4)]
            print(f"  child_a shift: {shift}")
        elif 'child_b' in child.name:
            orig = [1500, 1500, 1800, 1800]
            shift = [child.pos_list[i] - orig[i] for i in range(4)]
            print(f"  child_b shift: {shift}")

# ==============================================================================
# Cleanup
# ==============================================================================
print("\n" + "="*70)
print("Cleaning up...")
for f in [gds_file, gds_file2, gds_file3]:
    if os.path.exists(f):
        os.remove(f)
print("Done!")
print("="*70)
