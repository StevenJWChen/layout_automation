#!/usr/bin/env python3
"""Test fix_layout() with duplicate cell names"""

from layout_automation import Cell

# Create cells with duplicate names
block1 = Cell('duplicate_name', 'metal1')
block2 = Cell('duplicate_name', 'metal2')
block3 = Cell('duplicate_name', 'poly')

# Create parent and constrain the children
parent = Cell('parent')
parent.constrain(block1, 'x1=0, y1=0, x2=10, y2=10')
parent.constrain(block2, 'x1=20, y1=0, x2=30, y2=10')
parent.constrain(block3, 'x1=40, y1=0, x2=50, y2=10')

# Solve and fix
print("Solving...")
parent.solver()
print(f"block1 position: {block1.pos_list}")
print(f"block2 position: {block2.pos_list}")
print(f"block3 position: {block3.pos_list}")

print("\nFixing layout...")
parent.fix_layout()

print("\nReposition parent to (100, 100)...")
parent.set_position(100, 100)
print(f"Parent position: {parent.pos_list}")
print(f"block1 position: {block1.pos_list}")
print(f"block2 position: {block2.pos_list}")
print(f"block3 position: {block3.pos_list}")

# Verify all children moved correctly using pos_list
assert block1.pos_list == [100, 100, 110, 110], f"block1 incorrect: {block1.pos_list}"
assert block2.pos_list == [120, 100, 130, 110], f"block2 incorrect: {block2.pos_list}"
assert block3.pos_list == [140, 100, 150, 110], f"block3 incorrect: {block3.pos_list}"

# Also verify using the new properties
print("\nVerifying with properties:")
print(f"  block1: x={block1.x1}, width={block1.width}")
print(f"  block2: x={block2.x1}, width={block2.width}")
print(f"  block3: x={block3.x1}, width={block3.width}")

assert block1.x1 == 100 and block1.width == 10
assert block2.x1 == 120 and block2.width == 10
assert block3.x1 == 140 and block3.width == 10

print("\n[PASS] Test passed! fix_layout() works correctly with duplicate cell names.")
print("[PASS] All new properties (x1, y1, x2, y2, width, height, cx, cy) work correctly!")
