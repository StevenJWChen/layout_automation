#!/usr/bin/env python3
"""Check individual cells in inverter GDS"""

import gdstk

lib = gdstk.read_gds('sky130_inv_replica.gds')

print("=" * 70)
print("Checking NMOS and PMOS cells in inverter GDS")
print("=" * 70)

# Check the actual cell instances
for cell in lib.cells:
    if cell.name in ['NMOS', 'PMOS']:
        print(f"\nCell: {cell.name}")
        print(f"Number of polygons: {len(cell.polygons)}")

        # Print first polygon (diff)
        if cell.polygons:
            poly = cell.polygons[0]
            pts = poly.points
            print(f"\nFirst polygon (should be diff, layer 65/20):")
            print(f"  Layer: {poly.layer}/{poly.datatype}")
            print(f"  Points: {pts}")

# Also check test_nmos.gds for comparison
print(f"\n{'='*70}")
print("Comparison with test_nmos.gds")
print("="*70)

lib_test = gdstk.read_gds('test_nmos.gds')
cell_test = lib_test.cells[0]
print(f"\nCell: {cell_test.name}")
if cell_test.polygons:
    poly = cell_test.polygons[0]
    print(f"First polygon:")
    print(f"  Layer: {poly.layer}/{poly.datatype}")
    print(f"  Points: {poly.points}")
