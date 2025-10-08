#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test absolute constraints (single object)
"""

from gds_cell import Cell, Polygon

# Test 1: Single polygon with absolute size constraint
print("Test 1: Absolute size constraint using x prefix")
cell1 = Cell('cell1')
p1 = Polygon('p1', 'metal1')
cell1.add_polygon(p1)

# Set size using absolute constraint (no second object)
cell1.constrain(p1, 'x2-x1=20, y2-y1=10')

result = cell1.solver()
print(f"Result: {result}")
if result:
    print(f"  p1: {p1.pos_list}")
    print(f"  width: {p1.pos_list[2]-p1.pos_list[0]:.2f}, height: {p1.pos_list[3]-p1.pos_list[1]:.2f}")
else:
    print("  FAILED")

print()

# Test 2: Two polygons with absolute sizes and relative position
print("Test 2: Two polygons - absolute sizes + relative position")
cell2 = Cell('cell2')
diff = Polygon('diff', 'diff')
poly = Polygon('poly', 'poly')
cell2.add_polygon([diff, poly])

# Set absolute sizes
cell2.constrain(diff, 'x2-x1=40, y2-y1=20')
cell2.constrain(poly, 'x2-x1=4, y2-y1=30')

# Position poly relative to diff
cell2.constrain(diff, 'sx1+18=ox1, sy1-5=oy1', poly)

result = cell2.solver()
print(f"Result: {result}")
if result:
    print(f"  diff: {diff.pos_list}")
    print(f"    width: {diff.pos_list[2]-diff.pos_list[0]:.2f}, height: {diff.pos_list[3]-diff.pos_list[1]:.2f}")
    print(f"  poly: {poly.pos_list}")
    print(f"    width: {poly.pos_list[2]-poly.pos_list[0]:.2f}, height: {poly.pos_list[3]-poly.pos_list[1]:.2f}")

    cell2.draw(solve_first=False, show=False)
    print("  Drawing succeeded")
else:
    print("  FAILED")
