#!/usr/bin/env python3
"""
Proper GDS hierarchical test based on my_demo.py pattern
Tests for position shift with hierarchical layouts using constrain methods
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Hierarchical Test - Proper Pattern from my_demo.py")
print("="*70)

# ==============================================================================
# Test 1: Simple 2-level hierarchy
# ==============================================================================
print("\n" + "="*70)
print("Test 1: Simple 2-level hierarchy")
print("="*70)

# Create parent and child
parent = Cell('parent')
child_cell = Cell('child')
leaf1 = Cell('leaf1', 'metal1')
leaf2 = Cell('leaf2', 'metal2')

# Build hierarchy: parent -> child_cell -> leaf1, leaf2
child_cell.add_instance([leaf1, leaf2])
parent.add_instance(child_cell)

# Set constraints (using absolute coordinates in each parent's coordinate system)
parent.constrain('x1=0, y1=0, x2=500, y2=500')

# Position child_cell in parent's coordinates
parent.constrain(child_cell, 'x1=100, y1=100, x2=400, y2=400')

# Position leaves in child_cell's coordinates
child_cell.constrain(leaf1, 'x1=150, y1=150, x2=230, y2=230')
child_cell.constrain(leaf2, 'x1=270, y1=270, x2=350, y2=350')

print("\nSolving...")
if not parent.solver():
    print("✗ Solver failed!")
    exit(1)

print("\nOriginal positions (after solving):")
print(f"  parent: {parent.pos_list}")
print(f"    child_cell: {child_cell.pos_list}")
print(f"      leaf1: {leaf1.pos_list}")
print(f"      leaf2: {leaf2.pos_list}")

# Export to GDS
gds_file = 'test_hier_proper.gds'
parent.export_gds(gds_file, use_tech_file=False)
print(f"\nExported to {gds_file}")

# Check what's in GDS file
import gdstk
lib = gdstk.read_gds(gds_file)

print("\nGDS file structure:")
for cell in lib.cells:
    print(f"\n  Cell '{cell.name}':")
    if cell.polygons:
        for poly in cell.polygons:
            bbox = poly.bounding_box()
            print(f"    Polygon: {bbox}")
    if cell.references:
        for ref in cell.references:
            print(f"    References '{ref.cell.name}' at origin: {ref.origin}")

# Import back
imported = Cell.from_gds(gds_file, use_tech_file=False)

print("\n" + "="*70)
print("Imported positions:")
print("="*70)

def print_tree(cell, indent=0):
    print(f"{'  '*indent}{cell.name}: {cell.pos_list}")
    for child in cell.children:
        print_tree(child, indent+1)

print_tree(imported)

# Check for position shifts
print("\n" + "="*70)
print("Position shift analysis:")
print("="*70)

def find_cell(cell, target_name):
    if target_name in cell.name:
        return cell
    for child in cell.children:
        result = find_cell(child, target_name)
        if result:
            return result
    return None

imp_child = find_cell(imported, 'child')
imp_leaf1 = find_cell(imported, 'leaf1')
imp_leaf2 = find_cell(imported, 'leaf2')

errors = []

if imp_child:
    shift = [imp_child.pos_list[i] - child_cell.pos_list[i] for i in range(4)]
    print(f"\nchild_cell:")
    print(f"  Original: {child_cell.pos_list}")
    print(f"  Imported: {imp_child.pos_list}")
    print(f"  Shift:    {shift}")
    if any(abs(s) > 1 for s in shift):
        print(f"  ✗ POSITION SHIFT DETECTED!")
        errors.append("child_cell shifted")
    else:
        print(f"  ✓ No shift")

if imp_leaf1:
    shift = [imp_leaf1.pos_list[i] - leaf1.pos_list[i] for i in range(4)]
    print(f"\nleaf1:")
    print(f"  Original: {leaf1.pos_list}")
    print(f"  Imported: {imp_leaf1.pos_list}")
    print(f"  Shift:    {shift}")
    if any(abs(s) > 1 for s in shift):
        print(f"  ✗ POSITION SHIFT DETECTED!")
        errors.append("leaf1 shifted")
    else:
        print(f"  ✓ No shift")

if imp_leaf2:
    shift = [imp_leaf2.pos_list[i] - leaf2.pos_list[i] for i in range(4)]
    print(f"\nleaf2:")
    print(f"  Original: {leaf2.pos_list}")
    print(f"  Imported: {imp_leaf2.pos_list}")
    print(f"  Shift:    {shift}")
    if any(abs(s) > 1 for s in shift):
        print(f"  ✗ POSITION SHIFT DETECTED!")
        errors.append("leaf2 shifted")
    else:
        print(f"  ✓ No shift")

os.remove(gds_file)

# ==============================================================================
# Test 2: 3-level hierarchy
# ==============================================================================
print("\n" + "="*70)
print("Test 2: 3-level hierarchy")
print("="*70)

top = Cell('top')
mid1 = Cell('mid1')
mid2 = Cell('mid2')
bottom1 = Cell('bottom1', 'metal1')
bottom2 = Cell('bottom2', 'metal2')
bottom3 = Cell('bottom3', 'metal3')

# Build hierarchy
mid1.add_instance([bottom1, bottom2])
mid2.add_instance(bottom3)
top.add_instance([mid1, mid2])

# Set constraints
top.constrain('x1=0, y1=0, x2=1000, y2=1000')
top.constrain(mid1, 'x1=100, y1=100, x2=400, y2=400')
top.constrain(mid2, 'x1=600, y1=600, x2=900, y2=900')

mid1.constrain(bottom1, 'x1=150, y1=150, x2=250, y2=250')
mid1.constrain(bottom2, 'x1=300, y1=300, x2=350, y2=350')

mid2.constrain(bottom3, 'x1=700, y1=700, x2=850, y2=850')

print("\nSolving...")
if not top.solver():
    print("✗ Solver failed!")
    exit(1)

print("\nOriginal positions:")
print(f"  top: {top.pos_list}")
print(f"    mid1: {mid1.pos_list}")
print(f"      bottom1: {bottom1.pos_list}")
print(f"      bottom2: {bottom2.pos_list}")
print(f"    mid2: {mid2.pos_list}")
print(f"      bottom3: {bottom3.pos_list}")

# Export and import
gds_file2 = 'test_hier_3level.gds'
top.export_gds(gds_file2, use_tech_file=False)

imported2 = Cell.from_gds(gds_file2, use_tech_file=False)

print("\nImported positions:")
print_tree(imported2)

print("\nPosition shift analysis:")

imp_bottom1 = find_cell(imported2, 'bottom1')
imp_bottom2 = find_cell(imported2, 'bottom2')
imp_bottom3 = find_cell(imported2, 'bottom3')

leaves = [
    ('bottom1', bottom1, imp_bottom1),
    ('bottom2', bottom2, imp_bottom2),
    ('bottom3', bottom3, imp_bottom3)
]

for name, orig, imp in leaves:
    if imp:
        shift = [imp.pos_list[i] - orig.pos_list[i] for i in range(4)]
        print(f"\n{name}:")
        print(f"  Original: {orig.pos_list}")
        print(f"  Imported: {imp.pos_list}")
        print(f"  Shift:    {shift}")
        if any(abs(s) > 1 for s in shift):
            print(f"  ✗ POSITION SHIFT DETECTED!")
            errors.append(f"{name} shifted")
        else:
            print(f"  ✓ No shift")

os.remove(gds_file2)

# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if errors:
    print("✗ ERRORS DETECTED:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✓ ALL TESTS PASSED - No position shifts detected!")

print("\nTests completed:")
print("  ✓ 2-level hierarchy with constrain methods")
print("  ✓ 3-level hierarchy with multiple branches")
print("  ✓ GDS export/import round-trip verification")
print("="*70)
