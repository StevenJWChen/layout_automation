#!/usr/bin/env python3
"""Debug AND3 positioning"""

import gdstk

lib = gdstk.read_gds('sky130_and3_replica.gds')

print("="*70)
print("AND3 Instance Positions (converted to microns)")
print("="*70)

top_cell = [c for c in lib.cells if 'replica' in c.name][0]

print(f"\nTop cell: {top_cell.name}")
print(f"\nInstance positions:")
print(f"{'Cell Name':<25} {'Origin (um)':<25} {'Comment'}")
print("-"*70)

for ref in top_cell.references:
    ox, oy = ref.origin
    cell_type = ""
    if 'NMOS_NAND' in ref.cell.name:
        cell_type = "NAND3 NMOS (series)"
    elif 'PMOS_NAND' in ref.cell.name:
        cell_type = "NAND3 PMOS (parallel)"
    elif 'NMOS_INV' in ref.cell.name:
        cell_type = "Inverter NMOS"
    elif 'PMOS_INV' in ref.cell.name:
        cell_type = "Inverter PMOS"

    print(f"{ref.cell.name:<25} ({ox:6.3f}, {oy:6.3f})     {cell_type}")

# Check bounding box
bbox = top_cell.bounding_box()
if bbox:
    (x1, y1), (x2, y2) = bbox
    w = x2 - x1
    h = y2 - y1
    print(f"\nTotal bounding box:")
    print(f"  ({x1:.3f}, {y1:.3f}) to ({x2:.3f}, {y2:.3f})")
    print(f"  Size: {w:.3f} x {h:.3f} um")

print("\n" + "="*70)
print("Analysis")
print("="*70)

# Group by type
nand_nmos_y = []
nand_pmos_y = []
inv_y = []

for ref in top_cell.references:
    _, oy = ref.origin
    if 'NMOS_NAND' in ref.cell.name:
        nand_nmos_y.append(oy)
    elif 'PMOS_NAND' in ref.cell.name:
        nand_pmos_y.append(oy)
    elif 'INV' in ref.cell.name:
        inv_y.append(oy)

print(f"\nNAND3 NMOS Y positions: {sorted(nand_nmos_y)}")
print(f"  These should be stacked vertically (different Y)")
if len(set(nand_nmos_y)) < len(nand_nmos_y):
    print(f"  ⚠️  WARNING: Some Y positions are the same!")

print(f"\nNAND3 PMOS Y positions: {sorted(nand_pmos_y)}")
print(f"  These should be at same Y (parallel)")
if len(set(nand_pmos_y)) > 1:
    print(f"  ⚠️  WARNING: Y positions differ!")

print(f"\nInverter Y positions: {sorted(inv_y)}")

# Check if the layout makes sense
print("\n" + "="*70)
print("Layout Sanity Check")
print("="*70)

issues = []

# All positions should be in nanometers originally but shown in microns in GDS
# Typical positions should be 0.2-3 um range
all_origins = [(ref.cell.name, ref.origin) for ref in top_cell.references]
for name, (ox, oy) in all_origins:
    if ox < 0 or oy < 0:
        issues.append(f"  ✗ {name} has negative position: ({ox:.3f}, {oy:.3f})")
    if ox > 10 or oy > 10:
        issues.append(f"  ⚠️  {name} has large position: ({ox:.3f}, {oy:.3f}) - might be wrong")

if issues:
    print("\nIssues found:")
    for issue in issues:
        print(issue)
else:
    print("\n✓ All positions look reasonable")

# The strange output might be due to the small Y values (0.035, 0.065)
# This suggests the constraints aren't working as expected
print("\n" + "="*70)
print("ISSUE IDENTIFIED")
print("="*70)
print("""
The Y positions for NMOS_NAND_B (0.035) and NMOS_NAND_C (0.065) are
suspiciously small - these are 35nm and 65nm, which is smaller than
a single transistor!

This indicates the constraint solver may not be positioning them
correctly. They should be stacked with spacing of ~500nm between them.

Expected Y positions should be more like:
  NMOS_NAND_A: ~400nm (0.4um) ✓
  NMOS_NAND_B: ~1200nm (1.2um) - but getting 0.035um!
  NMOS_NAND_C: ~2000nm (2.0um) - but getting 0.065um!

The constraint 'oy1>sy2+spacing' may not be working correctly.
""")
