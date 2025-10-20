#!/usr/bin/env python3
"""
Example demonstrating the convenience of Cell position properties

This shows how properties make code more readable and intuitive
compared to accessing pos_list directly.
"""

from layout_automation import Cell

# Create a simple layout
print("Creating a layout with two boxes...")
parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')

parent.constrain(box1, 'x1=10, y1=20, x2=60, y2=70')
parent.constrain(box2, 'sx1=ox2+5, sy1=oy1, sx2-sx1=40, sy2-sy1=50', box1)
if not parent.solver():
    print("ERROR: Solver failed!")
    exit(1)

print("\n" + "="*70)
print("Readable access with properties:")
print("="*70)

# BEFORE: Using pos_list (less readable)
print("\nOLD WAY - Using pos_list:")
print(f"  box1 left edge: {box1.pos_list[0]}")
print(f"  box1 width: {box1.pos_list[2] - box1.pos_list[0]}")
print(f"  box1 center: ({(box1.pos_list[0] + box1.pos_list[2])/2}, {(box1.pos_list[1] + box1.pos_list[3])/2})")

# AFTER: Using properties (more readable)
print("\nNEW WAY - Using properties:")
print(f"  box1 left edge: {box1.x1}")
print(f"  box1 width: {box1.width}")
print(f"  box1 center: ({box1.cx}, {box1.cy})")

print("\n" + "="*70)
print("Practical examples:")
print("="*70)

# Example 1: Calculate spacing between cells
print("\n1. Calculate spacing between cells:")
spacing = box2.x1 - box1.x2
print(f"   Spacing between box1 and box2: {spacing} units")

# Example 2: Check if cells are aligned
print("\n2. Check vertical alignment:")
if box1.y1 == box2.y1:
    print(f"   box1 and box2 are bottom-aligned at y={box1.y1}")
else:
    print(f"   box1 bottom: y={box1.y1}, box2 bottom: y={box2.y1}")

# Example 3: Print cell dimensions
print("\n3. Print all cell dimensions:")
for cell in [box1, box2, parent]:
    print(f"   {cell.name}: {cell.width}x{cell.height} at ({cell.x1}, {cell.y1})")

# Example 4: Calculate area
print("\n4. Calculate cell areas:")
box1_area = box1.width * box1.height
box2_area = box2.width * box2.height
print(f"   box1 area: {box1_area}")
print(f"   box2 area: {box2_area}")
print(f"   Total area: {box1_area + box2_area}")

# Example 5: Find the rightmost cell
print("\n5. Find rightmost cell:")
rightmost = box1 if box1.x2 > box2.x2 else box2
print(f"   Rightmost cell: {rightmost.name} (right edge at x={rightmost.x2})")

# Example 6: Center point calculation
print("\n6. Layout center point:")
print(f"   Parent center: ({parent.cx}, {parent.cy})")
print(f"   Parent spans from ({parent.x1}, {parent.y1}) to ({parent.x2}, {parent.y2})")

print("\n" + "="*70)
print("Properties make code more intuitive and easier to read!")
print("="*70)
