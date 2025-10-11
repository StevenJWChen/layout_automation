#!/usr/bin/env python3
"""Test GDS export directly"""

from layout_automation.mosfet import MOSFET
from layout_automation.technology import create_sky130_tech
from layout_automation.units import um, nm

tech = create_sky130_tech()

# Create simple NMOS
nmos = MOSFET('NMOS_test', 'nfet', width=um(0.65), length=um(0.15), technology=tech)
nmos_cell = nmos.generate()

print("Before export - first 3 polygons:")
for i, poly in enumerate(nmos_cell.polygons[:3]):
    if poly.pos_list:
        x1, y1, x2, y2 = poly.pos_list
        print(f"{i}. {poly.name:30s} ({x1:4d},{y1:4d},{x2:4d},{y2:4d}) layer={poly.layer}")

# Export with technology
nmos_cell.export_gds("test_nmos.gds", technology=tech)

# Read back
import gdstk
lib = gdstk.read_gds("test_nmos.gds")
cell = lib.cells[0]

print(f"\nAfter export - first 3 polygons:")
for i, poly in enumerate(cell.polygons[:3]):
    pts = poly.points
    print(f"{i}. Layer {poly.layer}/{poly.datatype}: points={pts[0]}")
