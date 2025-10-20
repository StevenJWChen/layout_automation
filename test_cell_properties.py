#!/usr/bin/env python3
"""Test all position properties of Cell class"""

from layout_automation import Cell

print("="*70)
print("Testing Cell Position Properties")
print("="*70)

# Test 1: All properties return None before solving
print("\nTest 1: All properties return None before solving")
cell = Cell('test', 'metal1')
assert cell.width is None
assert cell.height is None
assert cell.x1 is None
assert cell.y1 is None
assert cell.x2 is None
assert cell.y2 is None
assert cell.cx is None
assert cell.cy is None
print("  [PASS] All properties return None before solving")

# Test 2: Properties work correctly after solving
print("\nTest 2: Properties work correctly after solving")
parent = Cell('parent')
rect = Cell('rect', 'metal1')
parent.constrain(rect, 'x1=10, y1=20, x2=110, y2=70')
parent.solver()

print(f"  rect position: {rect.pos_list}")
print(f"  rect.x1 = {rect.x1}")
print(f"  rect.y1 = {rect.y1}")
print(f"  rect.x2 = {rect.x2}")
print(f"  rect.y2 = {rect.y2}")
print(f"  rect.width = {rect.width}")
print(f"  rect.height = {rect.height}")
print(f"  rect.cx = {rect.cx}")
print(f"  rect.cy = {rect.cy}")

assert rect.x1 == 10
assert rect.y1 == 20
assert rect.x2 == 110
assert rect.y2 == 70
assert rect.width == 100
assert rect.height == 50
assert rect.cx == 60.0  # (10 + 110) / 2
assert rect.cy == 45.0  # (20 + 70) / 2
print("  [PASS] All coordinate properties correct")

# Test 3: Properties update after repositioning
print("\nTest 3: Properties update after repositioning with fix_layout")
block = Cell('block')
inner = Cell('inner', 'poly')
block.constrain(inner, 'x1=0, y1=0, x2=50, y2=30')
block.solver()

print(f"  Before fix: center=({block.cx}, {block.cy}), size={block.width}x{block.height}")

block.fix_layout()
block.set_position(100, 200)

print(f"  After reposition: center=({block.cx}, {block.cy}), size={block.width}x{block.height}")
assert block.x1 == 100
assert block.y1 == 200
assert block.x2 == 150
assert block.y2 == 230
assert block.cx == 125.0
assert block.cy == 215.0
assert block.width == 50
assert block.height == 30
print("  [PASS] Properties updated correctly after repositioning")

# Test 4: Using properties in code (practical example)
print("\nTest 4: Practical usage - align cells using properties")
parent2 = Cell('parent2')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent2.constrain(box1, 'x1=0, y1=0, x2=40, y2=30')
parent2.constrain(box2, 'sx1=ox2+10, sy1=oy1, sx2-sx1=60, sy2-sy1=30', box1)
parent2.solver()

print(f"  box1: pos={box1.pos_list}, center=({box1.cx}, {box1.cy})")
print(f"  box2: pos={box2.pos_list}, center=({box2.cx}, {box2.cy})")

# Verify spacing between boxes
spacing = box2.x1 - box1.x2
print(f"  Spacing between boxes: {spacing}")
assert spacing == 10
print("  [PASS] Properties useful for verification")

# Test 5: Check parent container properties
print("\nTest 5: Parent container properties")
print(f"  parent2: bounds=[{parent2.x1}, {parent2.y1}, {parent2.x2}, {parent2.y2}]")
print(f"  parent2: size={parent2.width}x{parent2.height}, center=({parent2.cx}, {parent2.cy})")

assert parent2.x1 == 0
assert parent2.y1 == 0
assert parent2.x2 == 110  # box2's right edge
assert parent2.y2 == 30
assert parent2.width == 110
assert parent2.height == 30
print("  [PASS] Parent container properties correct")

print("\n" + "="*70)
print("All cell property tests passed!")
print("="*70)
print("\nAvailable properties:")
print("  - cell.x1, cell.y1, cell.x2, cell.y2  : Corner coordinates")
print("  - cell.width, cell.height             : Dimensions")
print("  - cell.cx, cell.cy                    : Center coordinates")
print("  - All return None if cell not yet positioned")
