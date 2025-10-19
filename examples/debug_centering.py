#!/usr/bin/env python3
"""
Debug centering issue
"""

from layout_automation.cell import Cell

# Simplest possible test
parent = Cell('parent')
child1 = Cell('child1', 'metal1')
child2 = Cell('child2', 'metal2')

# Set parent size
parent.constrain('width=100, height=100, x1=0, y1=0')

# Set child1 position and size
parent.constrain(child1, 'width=20, height=20, x1=10, y1=10')

# Set child2 size only
parent.constrain(child2, 'width=20, height=20')

print("Constraints added:")
print(f"  Parent constraints: {parent.constraints}")
print(f"  Centering constraints: {parent._centering_constraints}")

# Try WITHOUT centering first
print("\n" + "=" * 60)
print("Test 1: WITHOUT centering (should work)")
print("=" * 60)

if parent.solver():
    print(f"✓ Solver succeeded!")
    print(f"  Parent: {parent.pos_list}")
    print(f"  Child1: {child1.pos_list}")
    print(f"  Child2: {child2.pos_list}")
else:
    print("✗ Solver failed")

# Now try WITH centering
print("\n" + "=" * 60)
print("Test 2: WITH centering")
print("=" * 60)

parent2 = Cell('parent2')
child3 = Cell('child3', 'metal1')
child4 = Cell('child4', 'metal2')

parent2.constrain('width=100, height=100, x1=0, y1=0')
parent2.constrain(child3, 'width=20, height=20, x1=10, y1=10')
parent2.constrain(child4, 'width=20, height=20')

# Add centering constraint
parent2.constrain(child4, 'center', child3)

print(f"Constraints added:")
print(f"  Parent constraints: {parent2.constraints}")
print(f"  Centering constraints: {parent2._centering_constraints}")

if parent2.solver():
    print(f"✓ Solver succeeded!")
    print(f"  Parent: {parent2.pos_list}")
    print(f"  Child3: {child3.pos_list}")
    print(f"  Child4: {child4.pos_list}")

    # Calculate centers
    c3_cx = (child3.pos_list[0] + child3.pos_list[2]) / 2
    c3_cy = (child3.pos_list[1] + child3.pos_list[3]) / 2
    c4_cx = (child4.pos_list[0] + child4.pos_list[2]) / 2
    c4_cy = (child4.pos_list[1] + child4.pos_list[3]) / 2

    print(f"  Child3 center: ({c3_cx}, {c3_cy})")
    print(f"  Child4 center: ({c4_cx}, {c4_cy})")
    print(f"  Deviation: X={abs(c3_cx-c4_cx)}, Y={abs(c3_cy-c4_cy)}")
else:
    print("✗ Solver failed")
