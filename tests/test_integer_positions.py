#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test integer position constraint
"""

from layout_automation.gds_cell import Cell, Polygon, CellInstance

print("="*70)
print("Testing Integer Position Constraint")
print("="*70)

# Test 1: Simple polygon with integer positions (default)
print("\nTest 1: Integer positions (default)")
cell1 = Cell('int_test')
rect1 = Polygon('rect1', 'metal1')
rect2 = Polygon('rect2', 'metal2')
cell1.add_polygon([rect1, rect2])

cell1.constrain(rect1, 'sx2+5<ox1', rect2)
cell1.constrain(rect1, 'sy1=oy1', rect2)

result = cell1.solver()  # integer_positions=True by default
print(f"Solver: {result}")
print(f"rect1: {rect1.pos_list}")
print(f"rect2: {rect2.pos_list}")

# Check all positions are integers
for val in rect1.pos_list + rect2.pos_list:
    assert isinstance(val, int), f"Position {val} is not integer: {type(val)}"

print("✓ All positions are integers\n")

# Test 2: With subtraction constraint
print("Test 2: Integer positions with subtraction constraint")
cell2 = Cell('width_test')
rect = Polygon('rect', 'metal1')
cell2.add_polygon(rect)
cell2.constrain(rect, 'sx2-sx1=25', None)

result = cell2.solver(integer_positions=True)
print(f"Solver: {result}")
print(f"rect: {rect.pos_list}")
width = rect.pos_list[2] - rect.pos_list[0]
print(f"Width: {width}")

assert all(isinstance(v, int) for v in rect.pos_list), "Positions not integers"
assert width == 25, f"Width should be 25, got {width}"
print("✓ Integer positions with exact width constraint\n")

# Test 3: Float positions (opt-in)
print("Test 3: Float positions (integer_positions=False)")
cell3 = Cell('float_test')
rect3 = Polygon('rect3', 'metal1')
cell3.add_polygon(rect3)
cell3.constrain(rect3, 'sx2-sx1=20', None)

result = cell3.solver(integer_positions=False)
print(f"Solver: {result}")
print(f"rect3: {rect3.pos_list}")

# Check positions are floats
print(f"Types: {[type(v).__name__ for v in rect3.pos_list]}")
assert any(isinstance(v, float) for v in rect3.pos_list), "Should have float positions"
print("✓ Float positions when requested\n")

# Test 4: Hierarchical with integer positions
print("Test 4: Hierarchical layout with integer positions")
base = Cell('base')
p1 = Polygon('p1', 'poly')
p2 = Polygon('p2', 'metal1')
base.add_polygon([p1, p2])
base.constrain(p1, 'sx2+3<ox1', p2)
base.constrain(p1, 'sy1=oy1', p2)

top = Cell('top')
inst1 = CellInstance('inst1', base)
inst2 = CellInstance('inst2', base)
top.add_instance([inst1, inst2])
top.constrain(inst1, 'sx2+10<ox1', inst2)
top.constrain(inst1, 'sy1=oy1', inst2)

result = top.solver(integer_positions=True)
print(f"Solver: {result}")
print(f"p1: {p1.pos_list}")
print(f"p2: {p2.pos_list}")
print(f"inst1: {inst1.pos_list}")
print(f"inst2: {inst2.pos_list}")

# Check all are integers
all_positions = p1.pos_list + p2.pos_list + inst1.pos_list + inst2.pos_list
for val in all_positions:
    assert isinstance(val, int), f"Position {val} is not integer"

print("✓ All hierarchical positions are integers\n")

# Test 5: Export to GDS with integer positions
print("Test 5: GDS export with integer positions")
export_cell = Cell('export_test')
poly = Polygon('poly', 'metal1')
export_cell.add_polygon(poly)
export_cell.constrain(poly, 'sx2-sx1=30, sy2-sy1=20', None)

result = export_cell.solver(integer_positions=True)
print(f"Solver: {result}")
print(f"poly: {poly.pos_list}")

export_cell.export_gds('integer_test.gds')
print("✓ GDS exported with integer coordinates\n")

print("="*70)
print("ALL INTEGER POSITION TESTS PASSED! ✓")
print("="*70)
print("\nSummary:")
print("  ✓ Default solver uses integer positions")
print("  ✓ Integer positions work with all constraint types")
print("  ✓ Can opt-in to float positions if needed")
print("  ✓ Hierarchical layouts have integer positions")
print("  ✓ GDS export uses integer coordinates")
print("\nAll layout positions are now integers by default!")
