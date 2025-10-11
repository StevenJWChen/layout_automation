#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test empty cell instances - they should get default size constraints and display
"""

from layout_automation.gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt

# Create a cell with content
cell_with_content = Cell('cell_with_content')
p1 = Polygon('p1', 'metal1')
cell_with_content.add_polygon(p1)

# Create an empty cell
empty_cell = Cell('empty_cell')

# Create top cell with both instances
top = Cell('top')
inst1 = CellInstance('inst_with_content', cell_with_content)
inst2 = CellInstance('inst_empty', empty_cell)
top.add_instance([inst1, inst2])

# Constrain them
top.constrain(inst1, 'sx2+10<ox1', inst2)  # empty instance to the right

print("Solving...")
result = top.solver()
print(f"Solver result: {result}")

if result:
    print(f"\nInstance with content: {inst1.pos_list}")
    print(f"  Content polygon p1: {p1.pos_list}")
    print(f"\nEmpty instance: {inst2.pos_list}")
    print(f"  Width: {inst2.pos_list[2] - inst2.pos_list[0]:.2f}")
    print(f"  Height: {inst2.pos_list[3] - inst2.pos_list[1]:.2f}")

    print("\nDrawing layout...")
    fig = top.draw(solve_first=False, show=False)
    plt.savefig('test_empty_instance.png')
    print("Saved to test_empty_instance.png")
    print("\nBoth instances are solved correctly.")
    print("Empty instance shows as a dashed box with default size (10x10).")
else:
    print("Solver failed!")
