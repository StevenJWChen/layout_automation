#!/usr/bin/env python3
"""
Detailed analysis of hierarchical GDS export to understand the bug
"""

from layout_automation.cell import Cell
import gdstk
import os

print("="*70)
print("Hierarchical GDS Export - Detailed Analysis")
print("="*70)

# Create simple 3-level hierarchy
top = Cell('top')
mid = Cell('mid')
leaf = Cell('leaf', 'metal1')

mid = Cell('mid', leaf)
top = Cell('top', mid)

# Set positions
top.pos_list = [0, 0, 1000, 1000]
mid.pos_list = [100, 100, 500, 500]  # Mid starts at (100, 100)
leaf.pos_list = [150, 150, 250, 250]  # Leaf starts at (150, 150)

print("\nOriginal hierarchy:")
print(f"  top: {top.pos_list}")
print(f"    mid: {mid.pos_list}")
print(f"      leaf: {leaf.pos_list}")

print("\nExpected relative positions:")
print(f"  leaf relative to mid: [{150-100}, {150-100}, {250-100}, {250-100}] = [50, 50, 150, 150]")
print(f"  If mid is at (100, 100), leaf should be at (100+50, 100+50) = (150, 150)")

# Export
gds_file = 'test_hierarchy_detail.gds'
top.export_gds(gds_file, use_tech_file=False)

# Analyze the GDS file
lib = gdstk.read_gds(gds_file)

print("\n" + "="*70)
print("GDS File Structure:")
print("="*70)

for cell in lib.cells:
    print(f"\nCell '{cell.name}':")

    if cell.polygons:
        print(f"  Polygons: {len(cell.polygons)}")
        for i, poly in enumerate(cell.polygons):
            bbox = poly.bounding_box()
            print(f"    Polygon {i}: bbox {bbox}")

    if cell.references:
        print(f"  References: {len(cell.references)}")
        for i, ref in enumerate(cell.references):
            print(f"    Ref {i}: to '{ref.cell.name}' at origin {ref.origin}")

print("\n" + "="*70)
print("Analysis:")
print("="*70)

# Find the mid cell
mid_cell = None
for cell in lib.cells:
    if cell.name == 'mid':
        mid_cell = cell
        break

if mid_cell and mid_cell.references:
    leaf_ref = mid_cell.references[0]
    print(f"\nIn the 'mid' cell, the 'leaf' reference is at: {leaf_ref.origin}")
    print(f"Expected: (50.0, 50.0)  [leaf position relative to mid]")
    print(f"Actual: {leaf_ref.origin}")

    if leaf_ref.origin[0] == 150.0:
        print(f"\n❌ BUG CONFIRMED!")
        print(f"   The leaf is placed at absolute position (150, 150)")
        print(f"   instead of relative position (50, 50)")
        print(f"\n   This causes double-counting when imported:")
        print(f"   - top references mid at (100, 100)")
        print(f"   - mid references leaf at (150, 150)  ← should be (50, 50)")
        print(f"   - Final position: 100 + 150 = 250  ← should be 100 + 50 = 150")
    elif leaf_ref.origin[0] == 50.0:
        print(f"\n✓ Correct: leaf is at relative position")

# Import and check
imported = Cell.from_gds(gds_file, use_tech_file=False)

print("\n" + "="*70)
print("Imported positions:")
print("="*70)

def print_tree(cell, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{cell.name}: {cell.pos_list}")
    for child in cell.children:
        print_tree(child, indent+1)

print_tree(imported)

print("\n" + "="*70)
print("Position shift:")
print("="*70)

def find_leaf(cell):
    if cell.name == 'leaf' or 'leaf' in cell.name:
        return cell
    for child in cell.children:
        result = find_leaf(child)
        if result:
            return result
    return None

imported_leaf = find_leaf(imported)
if imported_leaf:
    original_pos = [150, 150, 250, 250]
    imported_pos = imported_leaf.pos_list
    shift = [imported_pos[i] - original_pos[i] for i in range(4)]

    print(f"Original leaf position: {original_pos}")
    print(f"Imported leaf position: {imported_pos}")
    print(f"Shift: {shift}")

    if shift == [100, 100, 100, 100]:
        print(f"\n❌ Shift equals mid's x1,y1 position (100, 100)")
        print(f"   This confirms the bug: positions are not made relative to parent")

# Cleanup
os.remove(gds_file)
