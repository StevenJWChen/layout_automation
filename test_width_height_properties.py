#!/usr/bin/env python3
"""Test width and height properties of Cell class"""

from layout_automation import Cell

# Test 1: Properties should return None before solving
print("Test 1: Width and height before solving")
cell = Cell('test', 'metal1')
print(f"  width: {cell.width}")
print(f"  height: {cell.height}")
assert cell.width is None, "Width should be None before solving"
assert cell.height is None, "Height should be None before solving"
print("  [PASS]\n")

# Test 2: Properties should return correct values after solving
print("Test 2: Width and height after solving")
parent = Cell('parent')
rect1 = Cell('rect1', 'metal1')
rect2 = Cell('rect2', 'poly')

parent.constrain(rect1, 'x1=0, y1=0, x2=100, y2=50')
parent.constrain(rect2, 'x1=110, y1=0, x2=200, y2=75')

parent.solver()

print(f"  rect1 position: {rect1.pos_list}")
print(f"  rect1 width: {rect1.width}")
print(f"  rect1 height: {rect1.height}")
assert rect1.width == 100, f"rect1 width should be 100, got {rect1.width}"
assert rect1.height == 50, f"rect1 height should be 50, got {rect1.height}"

print(f"\n  rect2 position: {rect2.pos_list}")
print(f"  rect2 width: {rect2.width}")
print(f"  rect2 height: {rect2.height}")
assert rect2.width == 90, f"rect2 width should be 90, got {rect2.width}"
assert rect2.height == 75, f"rect2 height should be 75, got {rect2.height}"

print(f"\n  parent position: {parent.pos_list}")
print(f"  parent width: {parent.width}")
print(f"  parent height: {parent.height}")
assert parent.width == 200, f"parent width should be 200, got {parent.width}"
assert parent.height == 75, f"parent height should be 75, got {parent.height}"
print("  [PASS]\n")

# Test 3: Properties work with fixed layouts
print("Test 3: Width and height with fixed layouts")
block = Cell('block')
inner = Cell('inner', 'metal1')
block.constrain(inner, 'x1=10, y1=20, x2=50, y2=80')
block.solver()

print(f"  block position before fix: {block.pos_list}")
print(f"  block width: {block.width}, height: {block.height}")
assert block.width == 40, f"block width should be 40, got {block.width}"
assert block.height == 60, f"block height should be 60, got {block.height}"

block.fix_layout()
block.set_position(100, 100)

print(f"  block position after reposition: {block.pos_list}")
print(f"  block width: {block.width}, height: {block.height}")
assert block.width == 40, f"block width should still be 40, got {block.width}"
assert block.height == 60, f"block height should still be 60, got {block.height}"
print("  [PASS]\n")

# Test 4: Properties work with constraint keywords
print("Test 4: Using width/height in constraint strings")
container = Cell('container')
box = Cell('box', 'poly')

# Use width and height keywords in constraints
container.constrain(box, 'x1=0, y1=0, width=150, height=100')
container.solver()

print(f"  box position: {box.pos_list}")
print(f"  box width: {box.width}")
print(f"  box height: {box.height}")
assert box.width == 150, f"box width should be 150, got {box.width}"
assert box.height == 100, f"box height should be 100, got {box.height}"
print("  [PASS]\n")

print("="*60)
print("All width and height property tests passed!")
print("="*60)
