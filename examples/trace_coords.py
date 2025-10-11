#!/usr/bin/env python3
"""Trace actual polygon coordinates being generated"""

from layout_automation.mosfet import MOSFET
from layout_automation.technology import create_sky130_tech
from layout_automation.units import um, nm, to_um

tech = create_sky130_tech()

print("Creating NMOS (W=0.65um, L=0.15um)")
nmos = MOSFET('NMOS_trace', 'nfet', width=um(0.65), length=um(0.15), technology=tech)
nmos_cell = nmos.generate()

print(f"\nAll NMOS polygons (raw coordinates):")
for i, poly in enumerate(nmos_cell.polygons):
    if poly.pos_list and all(v is not None for v in poly.pos_list):
        x1, y1, x2, y2 = poly.pos_list
        w = x2 - x1
        h = y2 - y1
        print(f"{i:2d}. {poly.name:30s} layer={poly.layer:10s} pos=({x1:4d},{y1:4d},{x2:4d},{y2:4d}) size=({w:3d}x{h:3d}) nm")

print(f"\nExpected diff:")
print(f"  Should be: 0 to 670 in X, 130 to 780 in Y")
print(f"  Size: 670 x 650 nm")

print(f"\nExpected poly:")
print(f"  Should be: 170 to 600 in X, 0 to 910 in Y")
print(f"  Size: 430 x 910 nm")
