#!/usr/bin/env python3
# Debug actual dimensions being generated

from layout_automation.mosfet import MOSFET
from layout_automation.technology import create_sky130_tech
from layout_automation.units import um, nm, to_um

tech = create_sky130_tech()

print("Creating NMOS (W=0.65um, L=0.15um)")
nmos = MOSFET('NMOS_debug', 'nfet', width=um(0.65), length=um(0.15), technology=tech)
nmos_cell = nmos.generate()

print(f"\nNMOS internal values:")
print(f"  width (total): {nmos.width} nm = {to_um(nmos.width):.3f} um")
print(f"  length: {nmos.length} nm = {to_um(nmos.length):.3f} um")
print(f"  finger_width: {nmos.finger_width} nm = {to_um(nmos.finger_width):.3f} um")

print(f"\nNMOS polygons:")
for poly in nmos_cell.polygons[:5]:
    if poly.pos_list and all(v is not None for v in poly.pos_list):
        x1, y1, x2, y2 = poly.pos_list
        w = x2 - x1
        h = y2 - y1
        print(f"  {poly.name:20s}: ({x1:4d},{y1:4d}) to ({x2:4d},{y2:4d}), size {w:3d} x {h:3d} nm = {to_um(w):.3f} x {to_um(h):.3f} um, layer={poly.layer}")

# Check PMOS
print(f"\n{'='*70}")
print("Creating PMOS (W=1.0um, L=0.15um)")
pmos = MOSFET('PMOS_debug', 'pfet', width=um(1.0), length=um(0.15), technology=tech)
pmos_cell = pmos.generate()

print(f"\nPMOS internal values:")
print(f"  width (total): {pmos.width} nm = {to_um(pmos.width):.3f} um")
print(f"  length: {pmos.length} nm = {to_um(pmos.length):.3f} um")
print(f"  finger_width: {pmos.finger_width} nm = {to_um(pmos.finger_width):.3f} um")

print(f"\nPMOS polygons:")
for poly in pmos_cell.polygons[:5]:
    if poly.pos_list and all(v is not None for v in poly.pos_list):
        x1, y1, x2, y2 = poly.pos_list
        w = x2 - x1
        h = y2 - y1
        print(f"  {poly.name:20s}: ({x1:4d},{y1:4d}) to ({x2:4d},{y2:4d}), size {w:3d} x {h:3d} nm = {to_um(w):.3f} x {to_um(h):.3f} um, layer={poly.layer}")

# Check cell bounding boxes
bbox_nmos = nmos_cell.polygons[0].pos_list if nmos_cell.polygons else None
bbox_pmos = pmos_cell.polygons[0].pos_list if pmos_cell.polygons else None

print(f"\n{'='*70}")
print("Expected vs Actual:")
print(f"\nNMOS:")
print(f"  Expected: W=0.65um (650nm), L=0.15um (150nm)")
print(f"  Generated diff height should be: 650nm")
print(f"  Generated poly width should be: 150nm")

print(f"\nPMOS:")
print(f"  Expected: W=1.0um (1000nm), L=0.15um (150nm)")
print(f"  Generated diff height should be: 1000nm")
print(f"  Generated poly width should be: 150nm")

# Also check what SkyWater has
print(f"\n{'='*70}")
print("SkyWater Original Analysis:")
print(f"  Diff 0 (PMOS): 0.670 x 1.000 um")
print(f"  Diff 1 (NMOS): 0.670 x 0.650 um")
print(f"  Poly: 0.430 x 2.510 um")
print(f"\nNotice:")
print(f"  - Diff WIDTH is always 0.670um (not the transistor W!)")
print(f"  - Diff HEIGHT varies: 1.000um for PMOS, 0.650um for NMOS")
print(f"  - Poly WIDTH is 0.430um (much wider than L=0.15um due to DRC rules)")
