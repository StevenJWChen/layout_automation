#!/usr/bin/env python3
"""Debug what happens to polygon coordinates during solving"""

from layout_automation.gds_cell import Cell
from layout_automation.mosfet import MOSFET
from layout_automation.technology import create_sky130_tech
from layout_automation.units import um, nm

tech = create_sky130_tech()

# Create NMOS
nmos = MOSFET('NMOS', 'nfet', width=um(0.65), length=um(0.15), technology=tech)
nmos_cell = nmos.generate()

print("NM OS cell polygons BEFORE adding to parent:")
for i, poly in enumerate(nmos_cell.polygons[:3]):
    if poly.pos_list:
        print(f"  {i}. {poly.name:30s} {poly.pos_list}")

# Create parent cell and add instance
parent = Cell("parent")
from layout_automation.gds_cell import CellInstance
nmos_inst = CellInstance('NMOS_inst', nmos_cell)
parent.add_instance(nmos_inst)

# Position it
parent.constrain(nmos_inst, f'x1={nm(200)}, y1={nm(400)}')

print(f"\nInstance pos_list BEFORE solving: {nmos_inst.pos_list}")

# Solve
parent.solver()

print(f"\nInstance pos_list AFTER solving: {nmos_inst.pos_list}")

print("\nNMOS cell polygons AFTER solving:")
for i, poly in enumerate(nmos_cell.polygons[:3]):
    if poly.pos_list:
        print(f"  {i}. {poly.name:30s} {poly.pos_list}")
