#!/usr/bin/env python3
"""
Simple GDS hierarchical test - minimal case
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("Simple GDS Hierarchical Test")
print("="*70)

# Create simple 2-level hierarchy
parent = Cell('parent')
child = Cell('child', 'metal1')

# Give child a fixed size first (like frozen cells in show_layout.py)
child.pos_list = [0, 0, 60, 60]  # 60x60 cell

parent.add_instance(child)

# Set constraints
parent.constrain('x1=0, y1=0, x2=100, y2=100')
# Now just position it with x1, y1 (like show_layout.py does)
parent.constrain(child, 'x1=20, y1=20')

print("\nConstraints set:")
print(f"  parent: x1=0, y1=0, x2=100, y2=100")
print(f"  child: x1=20, y1=20, x2=80, y2=80 (relative to parent)")

print("\nSolving...")
result = parent.solver()
print(f"Solver result: {result}")

if result:
    print("\nOriginal positions (after solving):")
    print(f"  parent: {parent.pos_list}")
    print(f"  child: {child.pos_list}")

    # Expected: child at (20, 20, 80, 80) in global coordinates
    expected = [20, 20, 80, 80]
    if child.pos_list == expected:
        print(f"  ✓ Child position correct: {expected}")
    else:
        print(f"  ✗ Child position wrong!")
        print(f"    Expected: {expected}")
        print(f"    Got:      {child.pos_list}")

    # Export to GDS
    gds_file = 'test_simple_hier.gds'
    parent.export_gds(gds_file, use_tech_file=False)
    print(f"\nExported to {gds_file}")

    # Check what's in the GDS file
    import gdstk
    lib = gdstk.read_gds(gds_file)

    print("\nGDS file structure:")
    for cell in lib.cells:
        print(f"\nCell '{cell.name}':")
        if cell.polygons:
            for poly in cell.polygons:
                bbox = poly.bounding_box()
                print(f"  Polygon: {bbox}")
        if cell.references:
            for ref in cell.references:
                print(f"  References '{ref.cell.name}' at origin: {ref.origin}")

    # Import back
    imported = Cell.from_gds(gds_file, use_tech_file=False)

    print("\nImported positions:")
    print(f"  {imported.name}: {imported.pos_list}")
    for c in imported.children:
        print(f"    {c.name}: {c.pos_list}")

    # Check shift
    if imported.children:
        imp_child = imported.children[0]
        shift = [imp_child.pos_list[i] - child.pos_list[i] for i in range(4)]
        print(f"\nShift analysis:")
        print(f"  Original child: {child.pos_list}")
        print(f"  Imported child: {imp_child.pos_list}")
        print(f"  Shift: {shift}")

        if any(abs(s) > 1 for s in shift):
            print(f"  ✗ POSITION SHIFT DETECTED!")
        else:
            print(f"  ✓ No shift - positions preserved")

    os.remove(gds_file)
else:
    print("✗ Solver failed - cannot continue test")

print("\n" + "="*70)
