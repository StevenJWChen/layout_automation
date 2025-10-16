#!/usr/bin/env python3
"""
Simple timing test to show solver performance difference
"""

import time
from layout_automation.cell import Cell

print("=" * 80)
print("FROZEN LAYOUT TIMING TEST")
print("=" * 80)
print()

# Configuration
NUM_BLOCKS = 10
LAYERS_PER_BLOCK = 20

print(f"Configuration:")
print(f"  - {NUM_BLOCKS} block instances")
print(f"  - {LAYERS_PER_BLOCK} layers per block")
print(f"  - Total cells: {NUM_BLOCKS * LAYERS_PER_BLOCK} layers + {NUM_BLOCKS} blocks + 1 parent")
print()

# ==============================================================================
# Test 1: WITH FROZEN CELLS
# ==============================================================================
print("=" * 80)
print("TEST 1: WITH FROZEN CELLS")
print("=" * 80)
print()

# Step 1: Create and solve template
print("Step 1: Create template block...")
template = Cell('frozen_template')
for i in range(LAYERS_PER_BLOCK):
    layer = Cell(f'layer_{i}', 'metal1')
    template.constrain(layer, f'x1={i*3}, y1=0, x2={i*3+2}, y2=10')

print(f"  Created template with {len(template.children)} layers")

# Solve template
print("Step 2: Solve template...")
start = time.time()
template_result = template.solver()
template_time = time.time() - start

if not template_result:
    print("  ✗ Template solve FAILED")
    exit(1)

print(f"  ✓ Template solved in {template_time:.4f}s")
print(f"  Template bbox: {template.pos_list}")

# Freeze template
template.freeze_layout()
print(f"  ✓ Template frozen")
print()

# Step 2: Create parent with frozen instances
print("Step 3: Create parent with frozen instances...")
parent_frozen = Cell('parent_frozen')

for i in range(NUM_BLOCKS):
    inst = template.copy()
    inst.name = f'block_{i}'
    parent_frozen.add_instance(inst)

    # Get frozen size
    bbox = template.get_bbox()
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    # Position this instance
    parent_frozen.constrain(inst, f'x1={i*70}, y1=0, x2={i*70+width}, y2={height}')

print(f"  Created parent with {len(parent_frozen.children)} frozen blocks")

# Check cells in solver
cells_frozen = parent_frozen._get_all_cells()
print(f"  Cells in solver: {len(cells_frozen)}")
print(f"    = 1 parent + {NUM_BLOCKS} frozen blocks")
print()

# Solve parent
print("Step 4: Solve parent...")
start = time.time()
parent_frozen_result = parent_frozen.solver()
parent_frozen_time = time.time() - start

if not parent_frozen_result:
    print("  ✗ Parent solve FAILED")
    exit(1)

print(f"  ✓ Parent solved in {parent_frozen_time:.4f}s")
print()

# Total time
frozen_total = template_time + parent_frozen_time
print(f"FROZEN TOTAL TIME: {frozen_total:.4f}s")
print(f"  Template solve: {template_time:.4f}s")
print(f"  Parent solve:   {parent_frozen_time:.4f}s")
print()

# ==============================================================================
# Test 2: WITHOUT FROZEN CELLS
# ==============================================================================
print("=" * 80)
print("TEST 2: WITHOUT FROZEN CELLS")
print("=" * 80)
print()

# Create parent with all blocks (not frozen)
print("Step 1: Create parent with non-frozen blocks...")
parent_unfrozen = Cell('parent_unfrozen')

for i in range(NUM_BLOCKS):
    block = Cell(f'block_{i}')

    # Add layers to this block
    for j in range(LAYERS_PER_BLOCK):
        layer = Cell(f'block_{i}_layer_{j}', 'metal1')
        block.add_instance(layer)
        block.constrain(layer, f'x1={i*70+j*3}, y1=0, x2={i*70+j*3+2}, y2=10')

    parent_unfrozen.add_instance(block)

print(f"  Created parent with {len(parent_unfrozen.children)} blocks")

# Check cells in solver
cells_unfrozen = parent_unfrozen._get_all_cells()
print(f"  Cells in solver: {len(cells_unfrozen)}")
print(f"    = 1 parent + {NUM_BLOCKS} blocks + {NUM_BLOCKS * LAYERS_PER_BLOCK} layers")
print()

# Solve everything at once
print("Step 2: Solve entire hierarchy...")
start = time.time()
unfrozen_result = parent_unfrozen.solver()
unfrozen_time = time.time() - start

if not unfrozen_result:
    print("  ✗ Solve FAILED")
    exit(1)

print(f"  ✓ Solved in {unfrozen_time:.4f}s")
print()

print(f"NON-FROZEN TOTAL TIME: {unfrozen_time:.4f}s")
print()

# ==============================================================================
# COMPARISON
# ==============================================================================
print("=" * 80)
print("TIMING COMPARISON")
print("=" * 80)
print()

print("Solver Complexity:")
print(f"  Frozen:     {len(cells_frozen):3d} cells")
print(f"  Non-frozen: {len(cells_unfrozen):3d} cells")
print(f"  Reduction:  {len(cells_unfrozen) - len(cells_frozen):3d} cells ({100.0 * (len(cells_unfrozen) - len(cells_frozen)) / len(cells_unfrozen):.1f}%)")
print()

print("Solve Time:")
print(f"  Frozen approach:     {frozen_total:.4f}s")
print(f"    - Template solve:  {template_time:.4f}s")
print(f"    - Parent solve:    {parent_frozen_time:.4f}s")
print(f"  Non-frozen approach: {unfrozen_time:.4f}s")
print()

if frozen_total < unfrozen_time:
    speedup = unfrozen_time / frozen_total
    saved = unfrozen_time - frozen_total
    print(f"✓ FROZEN IS FASTER")
    print(f"  Speedup:    {speedup:.2f}x")
    print(f"  Time saved: {saved:.4f}s ({100.0 * saved / unfrozen_time:.1f}%)")
else:
    slowdown = frozen_total / unfrozen_time
    overhead = frozen_total - unfrozen_time
    print(f"  Frozen is slower: {slowdown:.2f}x")
    print(f"  Overhead: {overhead:.4f}s")
    print(f"  (Frozen benefits increase with larger designs)")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
print("The frozen layout optimization:")
print(f"  1. Reduces solver cells from {len(cells_unfrozen)} to {len(cells_frozen)} ({100.0 * len(cells_frozen) / len(cells_unfrozen):.1f}% of original)")
print(f"  2. Template solved once: {template_time:.4f}s")
print(f"  3. Parent solved with frozen blocks: {parent_frozen_time:.4f}s")
print()
print("Benefits scale with:")
print("  - More block instances")
print("  - More complex blocks (more layers)")
print("  - Deeper hierarchy nesting")
print()
print("=" * 80)
