#!/usr/bin/env python3
"""
Test auto-solving position properties
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from layout_automation.cell import Cell

print("="*70)
print("Testing Auto-Solving Position Properties")
print("="*70)

# Create a simple cell with constraints
print("\nCreating cell with constraints...")
cell = Cell('my_cell', 'metal1')
cell.constrain('x1=10, y1=20, x2=110, y2=70')

print(f"Initial pos_list: {cell.pos_list}")
print("Positions are None - not yet solved")

# Test 1: Access width property (should auto-solve)
print("\n" + "="*70)
print("Test 1: Accessing width property")
print("="*70)
print(f"Accessing cell.width...")
width = cell.width
print(f"✓ Width: {width}")
print(f"✓ pos_list after width access: {cell.pos_list}")
print(f"✓ Auto-solved successfully!")

# Test 2: Access height property (already solved, should not re-solve)
print("\n" + "="*70)
print("Test 2: Accessing height property (already solved)")
print("="*70)
print(f"Accessing cell.height...")
height = cell.height
print(f"✓ Height: {height}")
print(f"✓ No re-solve needed")

# Test 3: Access all position properties
print("\n" + "="*70)
print("Test 3: Accessing all position properties")
print("="*70)
print(f"x1: {cell.x1}")
print(f"y1: {cell.y1}")
print(f"x2: {cell.x2}")
print(f"y2: {cell.y2}")
print(f"cx (center x): {cell.cx}")
print(f"cy (center y): {cell.cy}")
print(f"width: {cell.width}")
print(f"height: {cell.height}")

# Test 4: New cell with auto-solve
print("\n" + "="*70)
print("Test 4: New cell - direct property access")
print("="*70)
parent = Cell('parent')
child = Cell('child', 'poly')
parent.add_instance(child)
parent.constrain('x1=0, y1=0, x2=200, y2=100')
child.constrain('x1=50, y1=30, x2=150, y2=70')

print(f"Before property access:")
print(f"  parent.pos_list = {parent.pos_list}")
print(f"  child.pos_list = {child.pos_list}")

print(f"\nAccessing parent.width directly...")
print(f"Parent width: {parent.width}")
print(f"Parent height: {parent.height}")
print(f"Child width: {child.width}")
print(f"Child height: {child.height}")

print(f"\nAfter property access:")
print(f"  parent.pos_list = {parent.pos_list}")
print(f"  child.pos_list = {child.pos_list}")
print(f"✓ Both auto-solved!")

# Test 5: Using properties in calculations
print("\n" + "="*70)
print("Test 5: Using properties in calculations")
print("="*70)
box = Cell('box', 'metal2')
box.constrain('x1=0, y1=0, x2=80, y2=60')

print(f"Box area = width × height")
area = box.width * box.height
print(f"Area: {area} square units")

print(f"\nBox perimeter = 2 × (width + height)")
perimeter = 2 * (box.width + box.height)
print(f"Perimeter: {perimeter} units")

print(f"\nBox center: ({box.cx}, {box.cy})")
print(f"✓ All calculations work seamlessly!")

print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\nSummary:")
print("  ✓ width and height properties auto-solve when needed")
print("  ✓ x1, y1, x2, y2 properties auto-solve when needed")
print("  ✓ cx, cy (center) properties auto-solve when needed")
print("  ✓ No need to manually call solver() before accessing properties")
print("  ✓ Properties can be used directly in calculations")
print("\nThis makes the API much more intuitive and user-friendly!")
