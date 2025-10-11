#!/usr/bin/env python3
"""Read actual GDS polygon points"""

import gdstk

lib = gdstk.read_gds('sky130_inv_replica.gds')

print("="*70)
print("READING ACTUAL GDS POLYGON COORDINATES")
print("="*70)

for cell in lib.cells:
    if cell.name == "NMOS":
        print(f"\nCell: {cell.name}")
        print(f"Polygons: {len(cell.polygons)}")

        for i, poly in enumerate(cell.polygons[:5]):
            print(f"\nPolygon {i}: Layer {poly.layer}/{poly.datatype}")
            print(f"  Points: {poly.points}")
            if len(poly.points) == 4:
                pts = poly.points
                x_coords = [p[0] for p in pts]
                y_coords = [p[1] for p in pts]
                x1, x2 = min(x_coords), max(x_coords)
                y1, y2 = min(y_coords), max(y_coords)
                w = x2 - x1
                h = y2 - y1
                print(f"  BBox: ({x1:.6f}, {y1:.6f}) to ({x2:.6f}, {y2:.6f})")
                print(f"  Size: {w:.6f} x {h:.6f} um = {w*1000:.1f} x {h*1000:.1f} nm")
