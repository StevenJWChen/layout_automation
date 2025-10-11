#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed comparison between SkyWater original and our replica
"""

import gdstk
from layout_automation.units import um, nm, to_um

print("=" * 70)
print("DETAILED INVERTER COMPARISON")
print("=" * 70)

# Load SkyWater original
print("\n1. SkyWater Original (sky130_fd_sc_hd__inv_1)")
print("-" * 70)
gds_file = 'skywater-pdk-libs-sky130_fd_sc_hd/cells/inv/sky130_fd_sc_hd__inv_1.gds'
lib_orig = gdstk.read_gds(gds_file)
cell_orig = lib_orig.cells[0]

bbox_orig = cell_orig.bounding_box()
(x1_o, y1_o), (x2_o, y2_o) = bbox_orig
width_orig = x2_o - x1_o
height_orig = y2_o - y1_o

print(f"Bounding box: ({x1_o:.3f}, {y1_o:.3f}) to ({x2_o:.3f}, {y2_o:.3f})")
print(f"Size: {width_orig:.3f} x {height_orig:.3f} um")
print(f"Polygons: {len(cell_orig.polygons)}")

# Analyze layers in original
print("\nLayer breakdown:")
layers_orig = {}
for poly in cell_orig.polygons:
    layer_key = (poly.layer, poly.datatype)
    if layer_key not in layers_orig:
        layers_orig[layer_key] = []
    layers_orig[layer_key].append(poly)

layer_names = {
    (64, 16): 'pwell (datatype 16)',
    (64, 20): 'nwell (datatype 20)',
    (65, 20): 'diff (active)',
    (66, 20): 'poly',
    (66, 44): 'licon1 (contact)',
    (67, 16): 'li1 (datatype 16)',
    (67, 20): 'li1',
    (67, 44): 'mcon',
    (68, 16): 'met1 (datatype 16)',
    (93, 44): 'nsdm (N+ implant)',
    (94, 20): 'psdm (P+ implant)',
    (95, 20): 'lvtn',
    (122, 16): 'std_cell_via',
    (236, 0): 'boundary/prBoundary',
}

for (layer, dtype), polys in sorted(layers_orig.items()):
    name = layer_names.get((layer, dtype), f'layer {layer}/{dtype}')
    print(f"  {name:30s}: {len(polys):2d} polygons")

# Find active regions (diff)
print("\nActive regions (diff, layer 65/20):")
diff_polys = layers_orig.get((65, 20), [])
for i, poly in enumerate(diff_polys):
    bb = poly.bounding_box()
    if bb:
        (x1, y1), (x2, y2) = bb
        w = x2 - x1
        h = y2 - y1
        print(f"  Diff {i}: ({x1:.3f},{y1:.3f}) to ({x2:.3f},{y2:.3f}), size {w:.3f} x {h:.3f} um")

# Find poly gates
print("\nPoly gates (layer 66/20):")
poly_gates = layers_orig.get((66, 20), [])
for i, poly in enumerate(poly_gates):
    bb = poly.bounding_box()
    if bb:
        (x1, y1), (x2, y2) = bb
        w = x2 - x1
        h = y2 - y1
        print(f"  Poly {i}: ({x1:.3f},{y1:.3f}) to ({x2:.3f},{y2:.3f}), size {w:.3f} x {h:.3f} um")

# Find contacts
print("\nContacts (licon1, layer 66/44):")
contacts = layers_orig.get((66, 44), [])
for i, poly in enumerate(contacts[:5]):  # First 5
    bb = poly.bounding_box()
    if bb:
        (x1, y1), (x2, y2) = bb
        w = x2 - x1
        h = y2 - y1
        print(f"  Contact {i}: ({x1:.3f},{y1:.3f}) to ({x2:.3f},{y2:.3f}), size {w:.3f} x {h:.3f} um")

# Load our replica
print("\n" + "=" * 70)
print("2. Our Replica (sky130_inv_replica)")
print("-" * 70)
lib_replica = gdstk.read_gds('sky130_inv_replica.gds')

print(f"Number of cells: {len(lib_replica.cells)}")
for cell in lib_replica.cells:
    bbox = cell.bounding_box()
    if bbox:
        (x1, y1), (x2, y2) = bbox
        w = x2 - x1
        h = y2 - y1
        print(f"\nCell: {cell.name}")
        print(f"  Bounding box: ({x1:.3f}, {y1:.3f}) to ({x2:.3f}, {y2:.3f})")
        print(f"  Size: {w:.3f} x {h:.3f} um")
        print(f"  Polygons: {len(cell.polygons)}")
        print(f"  References: {len(cell.references)}")

# Analyze top-level cell
top_cell = [c for c in lib_replica.cells if 'replica' in c.name][0]
print(f"\nTop cell layer breakdown:")
layers_replica = {}
for poly in top_cell.polygons:
    layer_key = (poly.layer, poly.datatype)
    if layer_key not in layers_replica:
        layers_replica[layer_key] = []
    layers_replica[layer_key].append(poly)

for (layer, dtype), polys in sorted(layers_replica.items()):
    print(f"  Layer {layer}/{dtype}: {len(polys):2d} polygons")

# Compare key dimensions
print("\n" + "=" * 70)
print("3. DIMENSION COMPARISON")
print("-" * 70)

print(f"\nCell size:")
print(f"  Original:    {width_orig:.3f} x {height_orig:.3f} um")
print(f"  Our replica: {w:.3f} x {h:.3f} um (TOP CELL)")
print(f"  Ratio:       {w/width_orig:.1%} x {h/height_orig:.1%}")

# Key observations
print("\n" + "=" * 70)
print("4. KEY FINDINGS")
print("-" * 70)

print("\nPROBLEMS IDENTIFIED:")
print("  ✗ Our cell is ~6x too small in both dimensions!")
print("  ✗ This suggests the MOSFET generator is using wrong dimensions")
print("  ✗ Likely issue: Wrong design rule values or incorrect layout algorithm")

print("\nExpected transistor dimensions:")
print("  NMOS: W=0.65um, L=0.15um")
print("  PMOS: W=1.0um, L=0.15um")

print("\nFrom SkyWater diff analysis:")
if len(diff_polys) >= 2:
    bb1 = diff_polys[0].bounding_box()
    bb2 = diff_polys[1].bounding_box()
    if bb1 and bb2:
        h1 = bb1[1][1] - bb1[0][1]
        h2 = bb2[1][1] - bb2[0][1]
        print(f"  Diff 0 height: {h1:.3f} um (should be NMOS width ~0.65um)")
        print(f"  Diff 1 height: {h2:.3f} um (should be PMOS width ~1.0um)")

print("\nNEXT STEPS:")
print("  1. Check MOSFET.py - verify dimension calculations")
print("  2. Check Contact.py - verify contact sizes and enclosures")
print("  3. Compare actual generated dimensions vs expected")
print("  4. Fix the layout generation to match SkyWater dimensions")
