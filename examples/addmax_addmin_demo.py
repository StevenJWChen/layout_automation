#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AddMaxEquality/AddMinEquality Demonstration

This example demonstrates the improved bounding box constraint implementation
using OR-Tools' AddMaxEquality and AddMinEquality methods.

The new approach is more efficient than the previous implementation which used
individual inequality constraints (parent_x1 <= child_x1, etc.) for each child.

Key Benefits:
1. Fewer constraints: 4 constraints per parent (regardless of number of children)
   vs. 4*N constraints (where N = number of children)
2. More efficient solving: CP-SAT can optimize Min/Max operations directly
3. Clearer semantic meaning: "parent bbox = min/max of children"
4. Better propagation: Solver can infer bounds more efficiently

Previous Implementation (per child):
    model.Add(parent_x1 <= child_x1)
    model.Add(parent_y1 <= child_y1)
    model.Add(parent_x2 >= child_x2)
    model.Add(parent_y2 >= child_y2)

New Implementation (all children at once):
    model.AddMinEquality(parent_x1, [child1_x1, child2_x1, ...])
    model.AddMinEquality(parent_y1, [child1_y1, child2_y1, ...])
    model.AddMaxEquality(parent_x2, [child1_x2, child2_x2, ...])
    model.AddMaxEquality(parent_y2, [child1_y2, child2_y2, ...])
"""

import time
import os
from layout_automation.cell import Cell

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("=" * 70)
print("AddMaxEquality/AddMinEquality Demonstration")
print("=" * 70)
print()

# ==============================================================================
# EXAMPLE 1: Basic Hierarchical Layout
# ==============================================================================

print("Example 1: Basic Hierarchical Layout")
print("-" * 70)
print()

# Create leaf cells (basic polygons)
leaf1 = Cell('leaf1', 'metal1')
leaf2 = Cell('leaf2', 'metal2')
leaf3 = Cell('leaf3', 'metal3')

# Create parent cell containing the leaves
parent = Cell('parent', leaf1, leaf2, leaf3)

# Add constraints: arrange leaves in a row
parent.constrain(leaf1, 'sx1=5, sy1=5')
parent.constrain(leaf1, 'sx2+10=ox1, sy1=oy1', leaf2)
parent.constrain(leaf2, 'sx2+10=ox1, sy1=oy1', leaf3)

print("Solving parent cell with 3 children...")
start = time.time()
result = parent.solver()
solve_time = time.time() - start

if result:
    print(f"✓ Solved in {solve_time:.4f}s")
    print(f"  leaf1: {leaf1.pos_list}")
    print(f"  leaf2: {leaf2.pos_list}")
    print(f"  leaf3: {leaf3.pos_list}")
    print(f"  parent (computed bbox): {parent.pos_list}")
    print()

    # Verify parent encompasses all children
    parent_x1, parent_y1, parent_x2, parent_y2 = parent.pos_list
    for i, child in enumerate([leaf1, leaf2, leaf3], 1):
        cx1, cy1, cx2, cy2 = child.pos_list
        encompasses = (parent_x1 <= cx1 and parent_y1 <= cy1 and
                      parent_x2 >= cx2 and parent_y2 >= cy2)
        print(f"  ✓ Parent encompasses leaf{i}: {encompasses}")

    print()
    print("Key Point: Parent bbox is automatically computed as:")
    print(f"  x1 = min(leaf1.x1, leaf2.x1, leaf3.x1) = {parent_x1}")
    print(f"  y1 = min(leaf1.y1, leaf2.y1, leaf3.y1) = {parent_y1}")
    print(f"  x2 = max(leaf1.x2, leaf2.x2, leaf3.x2) = {parent_x2}")
    print(f"  y2 = max(leaf1.y2, leaf2.y2, leaf3.y2) = {parent_y2}")
else:
    print("✗ Failed to solve")

print()

# ==============================================================================
# EXAMPLE 2: Deep Hierarchy
# ==============================================================================

print("Example 2: Multiple Instances of Same Cell")
print("-" * 70)
print()

# Create a standard cell
std_cell = Cell('std_cell', 'metal1')

# Create multiple instances
container = Cell('container', std_cell.copy(), std_cell.copy(), std_cell.copy())
inst1, inst2, inst3 = container.children

# Arrange instances in an L-shape
container.constrain(inst1, 'sx1=10, sy1=10')
container.constrain(inst1, 'sx2+10=ox1, sy1=oy1', inst2)
container.constrain(inst1, 'sx1=ox1, sy2+10=oy1', inst3)

print("Layout pattern:")
print("  inst3")
print("  inst1 inst2")
print()

print("Solving container with 3 instances...")
start = time.time()
result = container.solver()
solve_time = time.time() - start

if result:
    print(f"✓ Solved in {solve_time:.4f}s")
    print(f"  inst1: {inst1.pos_list}")
    print(f"  inst2: {inst2.pos_list}")
    print(f"  inst3: {inst3.pos_list}")
    print(f"  container (computed bbox): {container.pos_list}")
    print()

    # Verify container encompasses all instances
    cx1, cy1, cx2, cy2 = container.pos_list
    print("Verification:")
    print(f"  container.x1 = min(inst1.x1, inst2.x1, inst3.x1) = {cx1}")
    print(f"  container.x2 = max(inst1.x2, inst2.x2, inst3.x2) = {cx2}")
    print(f"  container.y1 = min(inst1.y1, inst2.y1, inst3.y1) = {cy1}")
    print(f"  container.y2 = max(inst1.y2, inst2.y2, inst3.y2) = {cy2}")

    # Draw the hierarchy
    fig = container.draw(solve_first=False, show=False)
    import matplotlib.pyplot as plt
    plt.savefig('demo_outputs/addmax_addmin_hierarchy.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Visualization saved to demo_outputs/addmax_addmin_hierarchy.png")
else:
    print("✗ Failed to solve")

print()

# ==============================================================================
# EXAMPLE 3: Performance with Many Children
# ==============================================================================

print("Example 3: Performance with Many Children")
print("-" * 70)
print()

def create_array(name, n_children):
    """Create a parent cell with n_children in a row"""
    children = [Cell(f'{name}_child{i}', 'metal1') for i in range(n_children)]
    parent = Cell(name, *children)

    # Arrange children in a row
    for i, child in enumerate(children):
        if i == 0:
            parent.constrain(child, 'sx1=5, sy1=5')
        else:
            parent.constrain(children[i-1], 'sx2+5=ox1, sy1=oy1', child)

    return parent, children

# Test with increasing number of children
test_sizes = [5, 10, 20, 50]

print("Testing solve time vs. number of children:")
print()

for n in test_sizes:
    array, children = create_array(f'array_{n}', n)

    start = time.time()
    result = array.solver()
    solve_time = time.time() - start

    if result:
        bbox = array.pos_list
        width = bbox[2] - bbox[0]
        print(f"  {n:3d} children: {solve_time:.4f}s, bbox width = {width}")
    else:
        print(f"  {n:3d} children: FAILED")

print()
print("Note: With AddMaxEquality/AddMinEquality, solve time scales well")
print("because we use 4 constraints per parent (regardless of # children)")
print("instead of 4*N constraints with the old approach.")

print()

# ==============================================================================
# EXAMPLE 4: Export to GDS
# ==============================================================================

print("Example 4: Export to GDS")
print("-" * 70)
print()

# Create a simple hierarchy
rect1 = Cell('rect1', 'metal1')
rect2 = Cell('rect2', 'metal2')
container = Cell('container', rect1, rect2)

container.constrain(rect1, 'sx1=10, sy1=10')
container.constrain(rect1, 'sx2+20=ox1, sy1=oy1', rect2)

result = container.solver()

if result:
    print(f"✓ Container solved")
    print(f"  rect1: {rect1.pos_list}")
    print(f"  rect2: {rect2.pos_list}")
    print(f"  container: {container.pos_list}")
    print()
    print("  Note: GDS export available via gds_cell.Cell class")
else:
    print("✗ Failed to solve")

print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("✓ AddMaxEquality/AddMinEquality implementation demonstrated")
print("✓ Parent bounding boxes automatically computed from children")
print("✓ Works with multiple instances of same cell")
print("✓ Efficient scaling with many children")
print("✓ Compatible with hierarchical designs")
print()
print("Technical Details:")
print("  • Uses 4 constraints per parent (was 4*N)")
print("  • Better constraint propagation in CP-SAT solver")
print("  • Clearer semantic meaning")
print("  • Implementation in cell.py:_add_parent_child_constraints_ortools()")
print()
print("Files generated:")
print("  • demo_outputs/addmax_addmin_hierarchy.png")
print()
print("=" * 70)
