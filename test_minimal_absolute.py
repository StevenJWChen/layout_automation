#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal test of absolute constraint
"""

from gds_cell import Cell, Polygon

# Simplest possible test
cell = Cell('test')
p1 = Polygon('p1', 'metal1')
cell.add_polygon(p1)

# Just set width to 20 (no height constraint)
cell.constrain(p1, 'x2-x1=20')

print("Attempting to solve...")
print(f"Polygon: {p1.name}")
print(f"Constraint: x2-x1=20")

result = cell.solver(fix_polygon_size=False)  # Disable default size constraints
print(f"Result: {result}")

if result:
    w = p1.pos_list[2] - p1.pos_list[0]
    h = p1.pos_list[3] - p1.pos_list[1]
    print(f"  p1: {p1.pos_list}")
    print(f"  width: {w:.2f} (should be 20)")
    print(f"  height: {h:.2f}")
else:
    print("  FAILED")
    print("\nTrying with default size constraints...")
    result2 = cell.solver(fix_polygon_size=True)
    print(f"Result: {result2}")
    if result2:
        w = p1.pos_list[2] - p1.pos_list[0]
        h = p1.pos_list[3] - p1.pos_list[1]
        print(f"  p1: {p1.pos_list}")
        print(f"  width: {w:.2f}")
        print(f"  height: {h:.2f}")
