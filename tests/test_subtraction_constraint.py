#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test subtraction constraints like 'sx2-sx1=20'
"""

from layout_automation.gds_cell import Cell, Polygon

print("="*70)
print("Testing Subtraction Constraints")
print("="*70)

# Test 1: Simple width constraint
print("\nTest 1: Width constraint sx2-sx1=20")
cell1 = Cell('width_test')
rect = Polygon('rect', 'metal1')
cell1.add_polygon(rect)
cell1.constrain(rect, 'sx2-sx1=20', None)

result = cell1.solver()
print(f"Solver: {result}")
print(f"Rectangle position: {rect.pos_list}")
width = rect.pos_list[2] - rect.pos_list[0]
height = rect.pos_list[3] - rect.pos_list[1]
print(f"Width: {width:.3f} (expected: 20.000)")
print(f"Height: {height:.3f} (expected: >=10.000 from default)")

assert abs(width - 20.0) < 0.01, f"Width should be 20, got {width}"
print("✓ PASS - Width constraint works!\n")

# Test 2: Both width and height constraints
print("Test 2: Width and height constraints")
cell2 = Cell('both_test')
rect2 = Polygon('rect2', 'metal1')
cell2.add_polygon(rect2)
cell2.constrain(rect2, 'sx2-sx1=15', None)
cell2.constrain(rect2, 'sy2-sy1=25', None)

result = cell2.solver()
print(f"Solver: {result}")
print(f"Rectangle position: {rect2.pos_list}")
width2 = rect2.pos_list[2] - rect2.pos_list[0]
height2 = rect2.pos_list[3] - rect2.pos_list[1]
print(f"Width: {width2:.3f} (expected: 15.000)")
print(f"Height: {height2:.3f} (expected: 25.000)")

assert abs(width2 - 15.0) < 0.01, f"Width should be 15, got {width2}"
assert abs(height2 - 25.0) < 0.01, f"Height should be 25, got {height2}"
print("✓ PASS - Both constraints work!\n")

# Test 3: Relative size constraint between two objects
print("Test 3: Relative size - ox2-ox1=sx2-sx1 (same width)")
cell3 = Cell('relative_test')
rect_a = Polygon('rect_a', 'metal1')
rect_b = Polygon('rect_b', 'metal2')
cell3.add_polygon([rect_a, rect_b])

# Make them same width
cell3.constrain(rect_a, 'ox2-ox1=sx2-sx1', rect_b)
# Make rect_a specific width
cell3.constrain(rect_a, 'sx2-sx1=18', None)
# Position them
cell3.constrain(rect_a, 'sx2+5<ox1', rect_b)
cell3.constrain(rect_a, 'sy1=oy1', rect_b)

result = cell3.solver()
print(f"Solver: {result}")
print(f"rect_a position: {rect_a.pos_list}")
print(f"rect_b position: {rect_b.pos_list}")
width_a = rect_a.pos_list[2] - rect_a.pos_list[0]
width_b = rect_b.pos_list[2] - rect_b.pos_list[0]
print(f"rect_a width: {width_a:.3f} (expected: 18.000)")
print(f"rect_b width: {width_b:.3f} (expected: 18.000)")

assert abs(width_a - 18.0) < 0.01, f"rect_a width should be 18, got {width_a}"
assert abs(width_b - 18.0) < 0.01, f"rect_b width should be 18, got {width_b}"
print("✓ PASS - Relative size constraint works!\n")

# Test 4: Complex expression with subtraction
print("Test 4: Complex expression - sx2-sx1+10=ox2-ox1")
cell4 = Cell('complex_test')
rect_c = Polygon('rect_c', 'poly')
rect_d = Polygon('rect_d', 'poly')
cell4.add_polygon([rect_c, rect_d])

# rect_d should be 10 units wider than rect_c
cell4.constrain(rect_c, 'sx2-sx1+10=ox2-ox1', rect_d)
cell4.constrain(rect_c, 'sx2-sx1=12', None)
cell4.constrain(rect_c, 'sx2+3<ox1', rect_d)
cell4.constrain(rect_c, 'sy1=oy1', rect_d)

result = cell4.solver()
print(f"Solver: {result}")
print(f"rect_c position: {rect_c.pos_list}")
print(f"rect_d position: {rect_d.pos_list}")
width_c = rect_c.pos_list[2] - rect_c.pos_list[0]
width_d = rect_d.pos_list[2] - rect_d.pos_list[0]
print(f"rect_c width: {width_c:.3f} (expected: 12.000)")
print(f"rect_d width: {width_d:.3f} (expected: 22.000)")
print(f"Difference: {width_d - width_c:.3f} (expected: 10.000)")

assert abs(width_c - 12.0) < 0.01, f"rect_c width should be 12, got {width_c}"
assert abs(width_d - 22.0) < 0.01, f"rect_d width should be 22, got {width_d}"
print("✓ PASS - Complex expression works!\n")

# Test 5: Multiple subtractions in one constraint
print("Test 5: Multiple variables - sx2-sx1=oy2-oy1 (width = other's height)")
cell5 = Cell('cross_test')
rect_e = Polygon('rect_e', 'metal1')
rect_f = Polygon('rect_f', 'metal1')
cell5.add_polygon([rect_e, rect_f])

# rect_e's width should equal rect_f's height
cell5.constrain(rect_e, 'sx2-sx1=oy2-oy1', rect_f)
cell5.constrain(rect_f, 'sy2-sy1=30', None)  # rect_f height = 30
cell5.constrain(rect_e, 'sx2+5<ox1', rect_f)
cell5.constrain(rect_e, 'sy1=oy1', rect_f)

result = cell5.solver()
print(f"Solver: {result}")
print(f"rect_e position: {rect_e.pos_list}")
print(f"rect_f position: {rect_f.pos_list}")
width_e = rect_e.pos_list[2] - rect_e.pos_list[0]
height_f = rect_f.pos_list[3] - rect_f.pos_list[1]
print(f"rect_e width: {width_e:.3f} (expected: 30.000)")
print(f"rect_f height: {height_f:.3f} (expected: 30.000)")

assert abs(width_e - 30.0) < 0.01, f"rect_e width should be 30, got {width_e}"
assert abs(height_f - 30.0) < 0.01, f"rect_f height should be 30, got {height_f}"
print("✓ PASS - Cross-dimension constraint works!\n")

print("="*70)
print("ALL SUBTRACTION CONSTRAINT TESTS PASSED! ✓")
print("="*70)
print("\nSubtraction constraints are working correctly:")
print("  - Simple: sx2-sx1=20")
print("  - Multiple: sx2-sx1=15, sy2-sy1=25")
print("  - Relative: ox2-ox1=sx2-sx1")
print("  - Complex: sx2-sx1+10=ox2-ox1")
print("  - Cross-dim: sx2-sx1=oy2-oy1")
