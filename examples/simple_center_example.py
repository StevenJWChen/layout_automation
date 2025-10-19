#!/usr/bin/env python3
"""
Simple example: Center two polygons with ±1 tolerance

This demonstrates the new automatic centering with tolerance feature.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

# Create parent and two polygons
parent = Cell('parent')
polygon1 = Cell('polygon1', 'metal1')
polygon2 = Cell('polygon2', 'metal2')

# Define sizes and position of first polygon
parent.constrain(polygon1, 'width=4, height=6')
parent.constrain(polygon2, 'width=2, height=3')

# Center polygon2 with polygon1 (prefers exact, allows ±1 tolerance)
parent.constrain(polygon2, 'center', polygon1)

# Solve and display results
if parent.solver():
    print("✓ Solver succeeded!")
    print(f"\nPolygon1: {polygon1.pos_list}")
    print(f"Polygon2: {polygon2.pos_list}")

    # Calculate centers
    p1_cx = (polygon1.pos_list[0] + polygon1.pos_list[2]) / 2
    p1_cy = (polygon1.pos_list[1] + polygon1.pos_list[3]) / 2
    p2_cx = (polygon2.pos_list[0] + polygon2.pos_list[2]) / 2
    p2_cy = (polygon2.pos_list[1] + polygon2.pos_list[3]) / 2

    print(f"\nPolygon1 center: ({p1_cx}, {p1_cy})")
    print(f"Polygon2 center: ({p2_cx}, {p2_cy})")

    x_dev = abs(p1_cx - p2_cx)
    y_dev = abs(p1_cy - p2_cy)

    print(f"\nDeviation: X={x_dev}, Y={y_dev}")

    if x_dev == 0 and y_dev == 0:
        print("✓ Exact centering achieved!")
    elif x_dev <= 1 and y_dev <= 1:
        print(f"✓ Centering within ±1 tolerance achieved!")
    else:
        print("✗ Outside tolerance range")

    # Draw the layout
    parent.draw()
else:
    print("✗ Solver failed")

print("\n" + "="*60)
print("How it works:")
print("  - parent.constrain(b, 'center', c)")
print("  - Tries exact centering first")
print("  - Falls back to ±1 tolerance if needed")
print("  - Uses OR-Tools soft constraints (no left/bottom bias)")
print("="*60)
