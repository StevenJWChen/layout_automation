#!/usr/bin/env python3
"""
Test to reproduce cell name collision bug in GDS export
If the same cell name appears in different parts of hierarchy, it gets overwritten
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Cell Name Collision Test")
print("="*70)

# Create hierarchy with duplicate cell names
top = Cell('top')
block1 = Cell('block1')
block2 = Cell('block2')

# Both blocks contain a cell named 'rect' - but different sizes!
rect_in_block1 = Cell('rect', 'metal1')  # Same name
rect_in_block2 = Cell('rect', 'metal2')  # Same name, different layer/size

block1.add_instance(rect_in_block1)
block2.add_instance(rect_in_block2)
top.add_instance([block1, block2])

# Set positions - make the rects DIFFERENT sizes to see the bug
top.pos_list = [0, 0, 1000, 1000]
block1.pos_list = [100, 100, 400, 400]
block2.pos_list = [600, 600, 900, 900]

# rect in block1: 100x100
rect_in_block1.pos_list = [150, 150, 250, 250]

# rect in block2: 200x200 (DIFFERENT SIZE)
rect_in_block2.pos_list = [650, 650, 850, 850]

print("\nOriginal positions:")
print(f"  top: {top.pos_list}")
print(f"    block1: {block1.pos_list}")
print(f"      rect (in block1): {rect_in_block1.pos_list} [100x100, metal1]")
print(f"    block2: {block2.pos_list}")
print(f"      rect (in block2): {rect_in_block2.pos_list} [200x200, metal2]")

print("\nNote: Both cells are named 'rect' but have DIFFERENT sizes!")

# Export to GDS
gds_file = 'test_name_collision.gds'
top.export_gds(gds_file, use_tech_file=False)
print(f"\nExported to {gds_file}")

# Analyze GDS file
import gdstk
lib = gdstk.read_gds(gds_file)

print("\n" + "="*70)
print("GDS File Analysis - Checking for overwrites:")
print("="*70)

# Count how many 'rect' cells exist in GDS
rect_cells = [cell for cell in lib.cells if cell.name == 'rect']
print(f"\nNumber of 'rect' cells in GDS file: {len(rect_cells)}")

if len(rect_cells) == 1:
    print("  ✗ BUG DETECTED! Only ONE 'rect' cell - second one was overwritten!")
    rect_cell = rect_cells[0]
    if rect_cell.polygons:
        bbox = rect_cell.polygons[0].bounding_box()
        width = bbox[1][0] - bbox[0][0]
        height = bbox[1][1] - bbox[0][1]
        print(f"  The 'rect' cell has size: {width}x{height}")
        print(f"  Expected: TWO different cells or unique naming")
elif len(rect_cells) == 2:
    print("  ✓ Correct: Two separate 'rect' cells preserved")
else:
    print(f"  ? Unexpected: {len(rect_cells)} 'rect' cells found")

# Check what block1 and block2 reference
print("\nChecking what blocks reference:")
for cell in lib.cells:
    if cell.name == 'block1':
        print(f"\n  block1 references:")
        for ref in cell.references:
            print(f"    - '{ref.cell.name}' at {ref.origin}")
            if ref.cell.polygons:
                bbox = ref.cell.polygons[0].bounding_box()
                layer = ref.cell.polygons[0].layer
                print(f"      Polygon: {bbox}, layer={layer}")

    elif cell.name == 'block2':
        print(f"\n  block2 references:")
        for ref in cell.references:
            print(f"    - '{ref.cell.name}' at {ref.origin}")
            if ref.cell.polygons:
                bbox = ref.cell.polygons[0].bounding_box()
                layer = ref.cell.polygons[0].layer
                print(f"      Polygon: {bbox}, layer={layer}")

# Import and check
print("\n" + "="*70)
print("Import test:")
print("="*70)

imported = Cell.from_gds(gds_file, use_tech_file=False)

def print_tree(cell, indent=0):
    layer_info = f", layer={cell.layer_name}" if cell.is_leaf else ""
    print(f"{'  '*indent}{cell.name}: {cell.pos_list}{layer_info}")
    for child in cell.children:
        print_tree(child, indent+1)

print_tree(imported)

# Check if both rects have correct sizes
print("\n" + "="*70)
print("Size verification:")
print("="*70)

def find_all_cells(cell, name_part, found_list):
    if name_part in cell.name:
        found_list.append(cell)
    for child in cell.children:
        find_all_cells(child, name_part, found_list)

all_rects = []
find_all_cells(imported, 'rect', all_rects)

print(f"\nFound {len(all_rects)} cells with 'rect' in name:")
for i, rect in enumerate(all_rects):
    if rect.pos_list and all(v is not None for v in rect.pos_list):
        width = rect.pos_list[2] - rect.pos_list[0]
        height = rect.pos_list[3] - rect.pos_list[1]
        print(f"  rect {i}: {rect.pos_list}, size={width}x{height}, layer={rect.layer_name}")

# Check if sizes match original
expected_sizes = {100, 200}  # We expect 100x100 and 200x200
actual_sizes = set()
for rect in all_rects:
    if rect.pos_list and all(v is not None for v in rect.pos_list):
        width = rect.pos_list[2] - rect.pos_list[0]
        actual_sizes.add(width)

print(f"\nExpected sizes: {expected_sizes}")
print(f"Actual sizes:   {actual_sizes}")

if actual_sizes == expected_sizes:
    print("✓ Both sizes preserved correctly")
else:
    print("✗ BUG: Sizes don't match - cell was overwritten!")

os.remove(gds_file)

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("If GDS file has only ONE 'rect' cell instead of keeping both,")
print("then the bug is confirmed: using cell names as dictionary keys")
print("causes overwrites when the same name appears in different places.")
print("="*70)
