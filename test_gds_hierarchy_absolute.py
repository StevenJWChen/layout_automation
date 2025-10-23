#!/usr/bin/env python3
"""
Test GDS hierarchical export/import with absolute position assignment
This bypasses the constraint solver to isolate the GDS shift issue
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Hierarchical Test - Direct Position Assignment")
print("="*70)

# Create 3-level hierarchy
top = Cell('top')
mid1 = Cell('mid1')
mid2 = Cell('mid2')
leaf1 = Cell('leaf1', 'metal1')
leaf2 = Cell('leaf2', 'metal2')
leaf3 = Cell('leaf3', 'metal3')

# Build hierarchy
mid1.add_instance([leaf1, leaf2])
mid2.add_instance(leaf3)
top.add_instance([mid1, mid2])

# Set positions directly (no solver needed)
top.pos_list = [0, 0, 1000, 1000]
mid1.pos_list = [100, 100, 400, 400]
mid2.pos_list = [600, 600, 900, 900]
leaf1.pos_list = [150, 150, 250, 250]
leaf2.pos_list = [300, 300, 350, 350]
leaf3.pos_list = [700, 700, 850, 850]

print("\nOriginal positions (manually set):")
print(f"  top: {top.pos_list}")
print(f"    mid1: {mid1.pos_list}")
print(f"      leaf1: {leaf1.pos_list}")
print(f"      leaf2: {leaf2.pos_list}")
print(f"    mid2: {mid2.pos_list}")
print(f"      leaf3: {leaf3.pos_list}")

# Export to GDS
gds_file = 'test_hier_absolute.gds'
top.export_gds(gds_file, use_tech_file=False)
print(f"\nExported to {gds_file}")

# Analyze GDS file structure
import gdstk
lib = gdstk.read_gds(gds_file)

print("\n" + "="*70)
print("GDS File Analysis:")
print("="*70)

for cell in lib.cells:
    print(f"\nCell '{cell.name}':")

    if cell.polygons:
        for i, poly in enumerate(cell.polygons):
            bbox = poly.bounding_box()
            print(f"  Polygon {i}: {bbox}")

    if cell.references:
        for i, ref in enumerate(cell.references):
            print(f"  Reference {i}: to '{ref.cell.name}' at origin {ref.origin}")

            # This is the key check: are references using relative positions?
            if ref.cell.name == 'mid1':
                expected = (100.0, 100.0)
                actual = ref.origin
                print(f"    Expected origin: {expected}")
                print(f"    Actual origin:   {actual}")
                if actual == expected:
                    print(f"    ✓ Correct (relative to top)")
                else:
                    print(f"    ✗ Wrong positioning!")

            elif ref.cell.name == 'leaf1':
                # leaf1 is at (150, 150) globally
                # mid1 is at (100, 100) globally
                # So leaf1 should be at (50, 50) relative to mid1
                expected = (50.0, 50.0)
                actual = ref.origin
                print(f"    Expected origin: {expected} (relative to mid1)")
                print(f"    Actual origin:   {actual}")
                if actual == expected:
                    print(f"    ✓ Correct (relative positioning)")
                else:
                    print(f"    ✗ Wrong! Using absolute instead of relative!")

# Import back
imported = Cell.from_gds(gds_file, use_tech_file=False)

print("\n" + "="*70)
print("Imported Positions:")
print("="*70)

def print_tree(cell, indent=0):
    print(f"{'  '*indent}{cell.name}: {cell.pos_list}")
    for child in cell.children:
        print_tree(child, indent+1)

print_tree(imported)

# Check for shifts
print("\n" + "="*70)
print("Position Shift Analysis:")
print("="*70)

def find_cell(cell, name_part):
    if name_part in cell.name:
        return cell
    for child in cell.children:
        result = find_cell(child, name_part)
        if result:
            return result
    return None

errors = []
checks = [
    ('leaf1', leaf1, find_cell(imported, 'leaf1')),
    ('leaf2', leaf2, find_cell(imported, 'leaf2')),
    ('leaf3', leaf3, find_cell(imported, 'leaf3')),
]

for name, orig, imp in checks:
    if imp:
        shift = [imp.pos_list[i] - orig.pos_list[i] for i in range(4)]
        print(f"\n{name}:")
        print(f"  Original: {orig.pos_list}")
        print(f"  Imported: {imp.pos_list}")
        print(f"  Shift:    {shift}")

        if any(abs(s) > 1 for s in shift):
            print(f"  ✗ POSITION SHIFT DETECTED!")
            errors.append(name)
        else:
            print(f"  ✓ Preserved")

os.remove(gds_file)

print("\n" + "="*70)
print("RESULT:")
print("="*70)

if errors:
    print(f"✗ FAILED - Position shifts detected in: {', '.join(errors)}")
    print("\nThis confirms the GDS hierarchical position shift bug!")
else:
    print("✓ PASSED - All positions preserved correctly")
    print("\nThe GDS fix is working!")

print("="*70)
