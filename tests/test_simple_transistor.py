#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug simple transistor layout
"""

from layout_automation.gds_cell import Cell, Polygon

# Test 1: Single polygon with size constraint
print("Test 1: Single polygon with size constraint")
cell1 = Cell('cell1')
p1 = Polygon('p1', 'metal1')
cell1.add_polygon(p1)

# Set size
cell1.constrain(p1, 'sx2-sx1=20, sy2-sy1=10', p1)

result = cell1.solver()
print(f"Result: {result}")
if result:
    print(f"  p1: {p1.pos_list}")
    print(f"  width: {p1.pos_list[2]-p1.pos_list[0]:.2f}, height: {p1.pos_list[3]-p1.pos_list[1]:.2f}")
else:
    print("  FAILED")

print()

# Test 2: Two polygons with size and position constraints
print("Test 2: Two polygons with size and position")
cell2 = Cell('cell2')
diff = Polygon('diff', 'diff')
poly = Polygon('poly', 'poly')
cell2.add_polygon([diff, poly])

# Set sizes
cell2.constrain(diff, 'sx2-sx1=40, sy2-sy1=20', diff)
cell2.constrain(poly, 'sx2-sx1=4, sy2-sy1=30', poly)

# Position poly relative to diff
cell2.constrain(diff, 'sx1+18=ox1', poly)  # poly.x1 = diff.x1 + 18
cell2.constrain(diff, 'sy1-5=oy1', poly)   # poly.y1 = diff.y1 - 5

result = cell2.solver()
print(f"Result: {result}")
if result:
    print(f"  diff: {diff.pos_list}")
    print(f"    width: {diff.pos_list[2]-diff.pos_list[0]:.2f}, height: {diff.pos_list[3]-diff.pos_list[1]:.2f}")
    print(f"  poly: {poly.pos_list}")
    print(f"    width: {poly.pos_list[2]-poly.pos_list[0]:.2f}, height: {poly.pos_list[3]-poly.pos_list[1]:.2f}")
    print(f"  poly.x1 - diff.x1 = {poly.pos_list[0] - diff.pos_list[0]:.2f} (should be 18)")
    print(f"  poly.y1 - diff.y1 = {poly.pos_list[1] - diff.pos_list[1]:.2f} (should be -5)")

    cell2.draw(solve_first=False, show=False)
    print("  Drawing succeeded")
else:
    print("  FAILED")
