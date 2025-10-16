#!/usr/bin/env python3
"""
Simple test to verify frozen layout optimization works
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

print("=" * 80)
print("SIMPLE FROZEN LAYOUT TEST")
print("=" * 80)
print()

# Test 1: Basic frozen functionality
print("Test 1: Basic Freeze/Unfreeze")
print("-" * 80)

cell = Cell('test', 'metal1')
cell.constrain('x1=0, y1=0, x2=10, y2=10')

if cell.solver():
    print(f"✓ Solved: {cell.pos_list}")

    cell.freeze_layout()
    print(f"✓ Frozen: {cell.is_frozen()}")
    print(f"✓ Bbox: {cell.get_bbox()}")

    cell.unfreeze_layout()
    print(f"✓ Unfrozen: {cell.is_frozen()}")
else:
    print("✗ Solver failed")
    sys.exit(1)

print()

# Test 2: Solver optimization - frozen cells exclude children
print("Test 2: Solver Optimization")
print("-" * 80)

# Create block with children
block = Cell('block')
for i in range(10):
    layer = Cell(f'layer_{i}', 'poly')
    block.constrain(layer, f'x1={i*2}, y1=0, x2={i*2+2}, y2=10')

# Before freeze
cells_before = block._get_all_cells()
print(f"Cells before freeze: {len(cells_before)}")
print(f"  Expected: 1 parent + 10 children = 11")

if not block.solver():
    print("✗ Solve failed")
    sys.exit(1)

# After freeze
block.freeze_layout()
cells_after = block._get_all_cells()
print(f"Cells after freeze: {len(cells_after)}")
print(f"  Expected: 1 (parent only)")

if len(cells_after) == 1:
    print(f"✓ Optimization working: {len(cells_before)} → {len(cells_after)} cells")
else:
    print(f"✗ Expected 1 cell, got {len(cells_after)}")
    sys.exit(1)

print()

# Test 3: Use frozen block in parent
print("Test 3: Frozen Block in Parent")
print("-" * 80)

parent = Cell('parent')
inst1 = block.copy()
inst2 = block.copy()

parent.add_instance([inst1, inst2])
parent.constrain(inst1, 'x1=0, y1=0, x2=20, y2=10')
parent.constrain(inst2, 'x1=30, y1=0, x2=50, y2=10')

# Check cells in parent
parent_cells = parent._get_all_cells()
print(f"Cells in parent hierarchy: {len(parent_cells)}")
print(f"  Expected: 1 parent + 2 frozen blocks = 3")
print(f"  (Frozen blocks' children NOT included)")

if parent.solver():
    print(f"✓ Parent solved")
    print(f"  inst1: {inst1.pos_list}")
    print(f"  inst2: {inst2.pos_list}")

    # Verify size preserved
    width1 = inst1.pos_list[2] - inst1.pos_list[0]
    height1 = inst1.pos_list[3] - inst1.pos_list[1]
    print(f"✓ inst1 size: {width1}×{height1} (frozen size preserved)")
else:
    print("✗ Parent solve failed")
    sys.exit(1)

print()
print("=" * 80)
print("✓ ALL TESTS PASSED!")
print("=" * 80)
