#!/usr/bin/env python3
"""Debug SkyWater extraction"""

from tools.skywater_extractor import SkyWaterExtractor
from layout_automation.technology import Technology
from layout_automation.gds_cell import Cell as GDSCell

# Load cell
cell = GDSCell("test")
cell.import_gds("sky130_inv_replica.gds", "sky130_fd_sc_hd__inv_1_replica")

# Extract
tech = Technology('sky130')
extractor = SkyWaterExtractor(cell, tech)

# Flatten
extractor._flatten_layout()

print("\n" + "="*70)
print("DEBUG: Checking for transistor extraction")
print("="*70)

# Check shapes
diff_shapes = extractor.shapes.get('diff', [])
poly_shapes = extractor.shapes.get('poly', [])
nwell_shapes = extractor.shapes.get('nwell', [])
contact_shapes = extractor.shapes.get('licon1', [])

print(f"\nShapes available:")
print(f"  diff: {len(diff_shapes)}")
print(f"  poly: {len(poly_shapes)}")
print(f"  nwell: {len(nwell_shapes)}")
print(f"  licon1 (contacts): {len(contact_shapes)}")

print(f"\nDiff shapes:")
for i, d in enumerate(diff_shapes):
    print(f"  {i}: {d.name} at ({d.x1:.0f}, {d.y1:.0f}) to ({d.x2:.0f}, {d.y2:.0f})")
    print(f"      Size: {d.width():.0f} × {d.height():.0f}")

print(f"\nPoly shapes:")
for i, p in enumerate(poly_shapes):
    print(f"  {i}: {p.name} at ({p.x1:.0f}, {p.y1:.0f}) to ({p.x2:.0f}, {p.y2:.0f})")
    print(f"      Size: {p.width():.0f} × {p.height():.0f}")

print(f"\nChecking diff-poly overlaps:")
overlap_count = 0
for diff in diff_shapes:
    for poly in poly_shapes:
        if diff.overlaps(poly):
            overlap_count += 1
            print(f"  Overlap {overlap_count}: {diff.name} × {poly.name}")

print(f"\nTotal overlaps: {overlap_count}")
print(f"Expected transistors: 2")

if overlap_count == 0:
    print("\n⚠️  No diff-poly overlaps found!")
    print("This means either:")
    print("  1. Shapes are not being extracted correctly")
    print("  2. Coordinates are wrong")
    print("  3. Layer mapping is incorrect")
