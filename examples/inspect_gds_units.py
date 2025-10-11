#!/usr/bin/env python3
"""Inspect GDS units and actual polygon coordinates"""

import gdstk

# Read our replica
print("="*70)
print("INSPECTING GDS UNITS AND COORDINATES")
print("="*70)

lib = gdstk.read_gds('sky130_inv_replica.gds')
print(f"\nLibrary: {lib.name}")
print(f"Unit: {lib.unit} meters (user unit in meters)")
print(f"Precision: {lib.precision} meters")
print(f"DBU per user unit: {lib.unit / lib.precision}")

print(f"\nCells: {len(lib.cells)}")

# Check each cell
for cell in lib.cells:
    print(f"\n{'='*70}")
    print(f"Cell: {cell.name}")
    print(f"Polygons: {len(cell.polygons)}")
    print(f"References: {len(cell.references)}")

    if cell.polygons:
        print(f"\nFirst 3 polygons (in user units = microns):")
        for i, poly in enumerate(cell.polygons[:3]):
            bb = poly.bounding_box()
            if bb:
                (x1, y1), (x2, y2) = bb
                w = x2 - x1
                h = y2 - y1
                print(f"  Polygon {i}: Layer {poly.layer}/{poly.datatype}")
                print(f"    BBox: ({x1:.6f}, {y1:.6f}) to ({x2:.6f}, {y2:.6f})")
                print(f"    Size: {w:.6f} x {h:.6f} (in user units)")
                # Convert to nm
                print(f"    Size: {w*1000:.1f} x {h*1000:.1f} nm")

    if cell.references:
        print(f"\nReferences:")
        for ref in cell.references:
            print(f"  -> {ref.cell.name} at origin {ref.origin}")

# Read SkyWater original for comparison
print(f"\n{'='*70}")
print("SKYWATER ORIGINAL FOR COMPARISON")
print("="*70)

lib_orig = gdstk.read_gds('skywater-pdk-libs-sky130_fd_sc_hd/cells/inv/sky130_fd_sc_hd__inv_1.gds')
print(f"\nLibrary: {lib_orig.name}")
print(f"Unit: {lib_orig.unit} meters")
print(f"Precision: {lib_orig.precision} meters")
print(f"DBU per user unit: {lib_orig.unit / lib_orig.precision}")

cell_orig = lib_orig.cells[0]
print(f"\nCell: {cell_orig.name}")
if cell_orig.polygons:
    print(f"\nFirst 3 polygons (diff and poly):")
    # Find diff and poly
    for poly in cell_orig.polygons[:10]:
        if poly.layer == 65 or poly.layer == 66:
            bb = poly.bounding_box()
            if bb:
                (x1, y1), (x2, y2) = bb
                w = x2 - x1
                h = y2 - y1
                layer_name = {65: 'diff', 66: 'poly'}.get(poly.layer, str(poly.layer))
                print(f"  Layer {layer_name} ({poly.layer}/{poly.datatype}): {w:.3f} x {h:.3f} um")
