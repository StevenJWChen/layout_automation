#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test GDS import/export functionality
"""

from gds_cell import Cell, Polygon, CellInstance

# Create a layout
print("Creating layout...")
base_cell = Cell('base_cell')
poly1 = Polygon('poly1', 'metal1')
poly2 = Polygon('poly2', 'metal2')
base_cell.add_polygon([poly1, poly2])
base_cell.constrain(poly1, 'sx2+3<ox1, sy2+5<oy1', poly2)

top_cell = Cell('top_cell')
inst1 = CellInstance('inst1', base_cell)
inst2 = CellInstance('inst2', base_cell)
top_cell.add_instance([inst1, inst2])
top_cell.constrain(inst1, 'sx2+5<ox1', inst2)

# Solve
print("Solving constraints...")
result = top_cell.solver()
print(f"Solver result: {result}")

if result:
    print(f"  inst1: {inst1.pos_list}")
    print(f"  inst2: {inst2.pos_list}")
    print(f"  poly1: {poly1.pos_list}")
    print(f"  poly2: {poly2.pos_list}")

    # Export to GDS
    print("\nExporting to GDS...")
    top_cell.export_gds("test_layout.gds")

    # Import from GDS
    print("\nImporting from GDS...")
    imported_cell = Cell('imported')
    imported_cell.import_gds("test_layout.gds")

    print(f"\nImported cell: {imported_cell}")
    print(f"  Polygons: {len(imported_cell.polygons)}")
    print(f"  Instances: {len(imported_cell.instances)}")

    # Draw imported layout
    print("\nDrawing imported layout...")
    imported_cell.draw(solve_first=False)
    print("Success!")
else:
    print("Solver failed")
