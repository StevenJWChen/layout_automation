#!/usr/bin/env python3
"""
Minimal test to understand the issue
"""

from layout_automation.cell import Cell

# Absolute minimal test
parent = Cell('parent')
child1 = Cell('child1', 'metal1')

# Add child to parent
parent.add_instance(child1)

# Set constraints
parent.constrain('width=100, height=100, x1=0, y1=0')
parent.constrain(child1, 'width=20, height=20, x1=10, y1=10')  # Constraint on child, added to parent

print("Parent constraints:", parent.constraints)
print("Child1 constraints:", child1.constraints)

if parent.solver():
    print(f"✓ Solver succeeded!")
    print(f"  Parent: {parent.pos_list}")
    print(f"  Child1: {child1.pos_list}")
else:
    print("✗ Solver failed")
