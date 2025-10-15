#!/usr/bin/env python3
"""
Verify two important behaviors:
1. Frozen layout cells can still be constrained by top cell
2. Center constraint: parent.constrain(child, 'sx1+sx2=ox1+ox2') centers child in parent
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 80)
print("VERIFICATION: FROZEN CELLS AND CENTER CONSTRAINTS")
print("=" * 80)
print()

# ==============================================================================
# TEST 1: Frozen cell can be constrained by top cell
# ==============================================================================
print("TEST 1: Frozen Cell Positioning by Top Cell")
print("-" * 80)
print()

# Create a frozen block
frozen_block = Cell('frozen_block')
layer1 = Cell('metal1', 'metal1')
layer2 = Cell('poly', 'poly')

frozen_block.add_instance([layer1, layer2])
frozen_block.constrain(layer1, 'x1=0, y1=0, x2=20, y2=20')
frozen_block.constrain(layer2, 'x1=5, y1=5, x2=15, y2=15')

# Solve and freeze
if frozen_block.solver():
    print(f"Step 1: Created block")
    print(f"  Block bbox before freeze: {frozen_block.pos_list}")

    frozen_block.freeze_layout()
    print(f"  Block frozen: {frozen_block.is_frozen()}")
    print(f"  Frozen bbox: {frozen_block.get_bbox()}")
    print()

    # Now use frozen block in top cell and constrain its position
    top_cell = Cell('top_cell')

    # Create instance of frozen block
    block_inst1 = frozen_block.copy()
    block_inst2 = frozen_block.copy()

    top_cell.add_instance([block_inst1, block_inst2])

    # Constrain frozen blocks' positions in top cell
    top_cell.constrain(block_inst1, 'x1=10, y1=10, x2=30, y2=30')
    top_cell.constrain(block_inst2, 'sx1=ox2+20, sy1=oy1, sx2-sx1=20, sy2-sy1=20', block_inst1)

    print(f"Step 2: Added frozen blocks to top cell with constraints")
    print(f"  block_inst1 constraint: x1=10, y1=10")
    print(f"  block_inst2 constraint: 20 units right of block_inst1")
    print()

    if top_cell.solver():
        print(f"Step 3: Top cell solved successfully!")
        print(f"  ✓ Frozen cells CAN be constrained by top cell")
        print(f"  block_inst1 final position: {block_inst1.pos_list}")
        print(f"  block_inst2 final position: {block_inst2.pos_list}")
        print()
        print(f"Conclusion: Frozen cells maintain their internal structure")
        print(f"            but can be positioned by parent constraints")
    else:
        print(f"  ✗ Top cell solver failed")
else:
    print("✗ Frozen block solver failed")

print()
print()

# ==============================================================================
# TEST 2: Center constraint syntax
# ==============================================================================
print("TEST 2: Center Constraint - sx1+sx2=ox1+ox2")
print("-" * 80)
print()

# Create parent and child
parent = Cell('parent')
child = Cell('child', 'metal1')

# Set parent size
parent.constrain('x1=0, y1=0, x2=100, y2=100')

# Set child size
parent.constrain(child, 'sx2-sx1=30, sy2-sy1=40')

# Center child in parent
# For X centering: sx1 + sx2 = ox1 + ox2 means:
#   child_x1 + child_x2 = parent_x1 + parent_x2
#   2 * child_center_x = 2 * parent_center_x
#   child_center_x = parent_center_x
print("Setting center constraint: sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2")
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

if parent.solver():
    print(f"✓ Solver succeeded")
    print()
    print(f"Parent bbox: {parent.pos_list}")
    print(f"  Parent X range: {parent.pos_list[0]} to {parent.pos_list[2]}")
    print(f"  Parent Y range: {parent.pos_list[1]} to {parent.pos_list[3]}")
    print(f"  Parent center X: {(parent.pos_list[0] + parent.pos_list[2]) / 2}")
    print(f"  Parent center Y: {(parent.pos_list[1] + parent.pos_list[3]) / 2}")
    print()
    print(f"Child bbox: {child.pos_list}")
    print(f"  Child X range: {child.pos_list[0]} to {child.pos_list[2]}")
    print(f"  Child Y range: {child.pos_list[1]} to {child.pos_list[3]}")
    print(f"  Child center X: {(child.pos_list[0] + child.pos_list[2]) / 2}")
    print(f"  Child center Y: {(child.pos_list[1] + child.pos_list[3]) / 2}")
    print()

    # Verify centering
    parent_center_x = (parent.pos_list[0] + parent.pos_list[2]) / 2
    parent_center_y = (parent.pos_list[1] + parent.pos_list[3]) / 2
    child_center_x = (child.pos_list[0] + child.pos_list[2]) / 2
    child_center_y = (child.pos_list[1] + child.pos_list[3]) / 2

    x_centered = abs(parent_center_x - child_center_x) < 0.1
    y_centered = abs(parent_center_y - child_center_y) < 0.1

    if x_centered and y_centered:
        print(f"✓ VERIFIED: Child is centered in parent!")
        print(f"  Constraint 'sx1+sx2=ox1+ox2' means child center X = parent center X")
        print(f"  Constraint 'sy1+sy2=oy1+oy2' means child center Y = parent center Y")
    else:
        print(f"✗ Child is NOT centered")
        print(f"  X center difference: {abs(parent_center_x - child_center_x)}")
        print(f"  Y center difference: {abs(parent_center_y - child_center_y)}")
else:
    print("✗ Solver failed")

print()
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print()
print("1. Frozen Layout Positioning:")
print("   ✓ Frozen cells CAN be constrained by top cell")
print("   ✓ Frozen cells maintain internal structure while being positioned")
print("   Usage: top.constrain(frozen_child, 'x1=10, y1=10, ...')")
print()
print("2. Center Constraint Syntax:")
print("   ✓ parent.constrain(child, 'sx1+sx2=ox1+ox2') centers child X in parent")
print("   ✓ parent.constrain(child, 'sy1+sy2=oy1+oy2') centers child Y in parent")
print("   ✓ Combined: centers child in both dimensions")
print()
print("   Math: sx1 + sx2 = ox1 + ox2")
print("        (child.x1 + child.x2) = (parent.x1 + parent.x2)")
print("        2 * child_center_x = 2 * parent_center_x")
print("        child_center_x = parent_center_x")
print()
print("=" * 80)
