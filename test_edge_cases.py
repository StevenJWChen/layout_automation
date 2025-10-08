#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test edge cases for gds_cell
"""

from gds_cell import Cell, Polygon, CellInstance

# Test 1: Cell instance with no polygons (empty cell)
print("Test 1: Cell instance with empty cell")
empty_cell = Cell('empty_cell')
top = Cell('top')
inst_empty = CellInstance('inst_empty', empty_cell)
top.add_instance(inst_empty)

result = top.solver()
print(f"Solver result: {result}")
if result:
    print(f"  inst_empty: {inst_empty.pos_list}")
else:
    print("  Failed to solve")

# Test 2: Constraint with subtraction like 'sx2-sx1=10'
print("\nTest 2: Constraint with width specification sx2-sx1=10")
cell = Cell('cell')
p1 = Polygon('p1', 'metal1')
p2 = Polygon('p2', 'metal2')
cell.add_polygon([p1, p2])

# Try to set width difference: p2 width = p1 width + 10
try:
    cell.constrain(p1, 'sx2+3<ox1', p2)  # p1 left of p2
    cell.constrain(p1, 'ox2-ox1=sx2-sx1+10', p2)  # p2 width = p1 width + 10
    result = cell.solver()
    print(f"Solver result: {result}")
    if result:
        print(f"  p1: {p1.pos_list}")
        print(f"  p1 width: {p1.pos_list[2] - p1.pos_list[0]:.2f}")
        print(f"  p2: {p2.pos_list}")
        print(f"  p2 width: {p2.pos_list[2] - p2.pos_list[0]:.2f}")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: Simple subtraction constraint between two different objects
print("\nTest 3: Width equality constraint sx2-sx1=ox2-ox1")
cell2 = Cell('cell2')
poly1 = Polygon('poly1', 'metal1')
poly2 = Polygon('poly2', 'metal2')
cell2.add_polygon([poly1, poly2])

try:
    # Make poly1 and poly2 have same width
    cell2.constrain(poly1, 'sx2-sx1=ox2-ox1', poly2)
    # Position poly2 to the right of poly1
    cell2.constrain(poly1, 'sx2+5<ox1', poly2)

    result = cell2.solver()
    print(f"Solver result: {result}")
    if result:
        print(f"  poly1: {poly1.pos_list}")
        print(f"    width: {poly1.pos_list[2] - poly1.pos_list[0]:.2f}, height: {poly1.pos_list[3] - poly1.pos_list[1]:.2f}")
        print(f"  poly2: {poly2.pos_list}")
        print(f"    width: {poly2.pos_list[2] - poly2.pos_list[0]:.2f}, height: {poly2.pos_list[3] - poly2.pos_list[1]:.2f}")

        # Verify widths are equal
        w1 = poly1.pos_list[2] - poly1.pos_list[0]
        w2 = poly2.pos_list[2] - poly2.pos_list[0]
        print(f"  Width difference: {abs(w1 - w2):.6f} (should be ~0)")
except Exception as e:
    print(f"  Error: {e}")
