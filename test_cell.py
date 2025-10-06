#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Cell class using example from my_spec.py
"""

from cell import Cell

# Simpler test - just copy and position
inst1 = Cell('inst1', 'metal1')
inst2 = Cell('inst2', 'metal2')
inst3 = Cell('inst3', 'metal3')
cell_inst1 = Cell('cell_inst1', inst1, inst2, inst3)
cell_inst1.constrain(inst1, 'sx1<ox2+3, sy2+5<oy1', inst2)
cell_inst1.constrain(inst1, 'sx1=ox1-1', inst3)
# Make copies
t_inst1 = cell_inst1.copy()
t_inst2 = cell_inst1.copy()

print(f"t_inst1 children: {len(t_inst1.children)}")
print(f"t_inst1.children[0].name: {t_inst1.children[0].name if t_inst1.children else 'none'}")

tt_inst = Cell('tt_inst', t_inst1, t_inst2)
tt_inst.constrain(t_inst1, 'sx2+5<ox1', t_inst2)  # t_inst1 left of t_inst2

# Solve and draw
print("Solving constraints for tt_inst hierarchy...")
result = tt_inst.solver()
print(f"Solver result: {result}")

if result:
    print("\nCell positions:")
    print(f"t_inst1: {t_inst1.pos_list}")
    print(f"t_inst2: {t_inst2.pos_list}")
    print(f"tt_inst (container): {tt_inst.pos_list}")

    print("\nDrawing layout...")
    tt_inst.draw(solve_first=False)
    print("Layout visualization created successfully!")
else:
    print("Failed to find solution")
