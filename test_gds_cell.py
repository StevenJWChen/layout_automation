#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for GDS-style Cell class
"""

from gds_cell import Cell, Polygon, CellInstance

# Test 1: Single cell with polygons
print("Test 1: Single cell with polygons")
base_cell = Cell('base_cell')
poly1 = Polygon('poly1', 'metal1')
poly2 = Polygon('poly2', 'metal2')
base_cell.add_polygon([poly1, poly2])

# Add constraints between polygons
base_cell.constrain(poly1, 'sx2+3<ox1, sy2+5<oy1', poly2)

result = base_cell.solver()
print(f"Solver result: {result}")

if result:
    print(f"  poly1: {poly1.pos_list}")
    print(f"  poly2: {poly2.pos_list}")
    base_cell.draw(solve_first=False, show=False)
    print("Success!")

# Test 2: Cell with instances
print("\nTest 2: Cells with instances")

# Create fresh base cell for instances
base_cell2 = Cell('base_cell2')
p1 = Polygon('p1', 'metal1')
p2 = Polygon('p2', 'metal2')
base_cell2.add_polygon([p1, p2])
base_cell2.constrain(p1, 'sx2+3<ox1, sy2+5<oy1', p2)

top_cell = Cell('top_cell')

# Create two instances of base_cell2
inst1 = CellInstance('inst1', base_cell2)
inst2 = CellInstance('inst2', base_cell2)
top_cell.add_instance([inst1, inst2])

# Constrain instances relative to each other
top_cell.constrain(inst1, 'sx2+5<ox1', inst2)

print(f"Solving top_cell with instances...")
print(f"  top_cell has {len(top_cell.instances)} instances")
print(f"  base_cell2 has {len(base_cell2.polygons)} polygons")
print(f"  base_cell2 has {len(base_cell2.constraints)} constraints")
result2 = top_cell.solver()
print(f"Solver result: {result2}")

if result2:
    print(f"  inst1: {inst1.pos_list}")
    print(f"  inst2: {inst2.pos_list}")
    print("\nDrawing layout...")
    top_cell.draw(solve_first=False)
    print("Success!")
else:
    print("Failed")
