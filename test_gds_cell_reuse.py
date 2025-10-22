#!/usr/bin/env python3
"""
Test proper GDS cell reuse vs cell name collision
Shows the difference between:
1. Same cell reused in multiple places (SHOULD share GDS cell)
2. Different cells with same name (MUST have unique GDS names)
"""

from layout_automation.cell import Cell
import os

print("="*70)
print("GDS Cell Reuse Test")
print("="*70)

# ==============================================================================
# Test 1: Proper cell reuse (same cell, multiple instances)
# ==============================================================================
print("\n" + "="*70)
print("Test 1: Proper cell reuse - same cell instance in multiple places")
print("="*70)

top1 = Cell('top1')
block1a = Cell('block1a')
block1b = Cell('block1b')

# Create ONE rect cell and use it in BOTH blocks
shared_rect = Cell('rect', 'metal1')
shared_rect.pos_list = [0, 0, 100, 100]  # 100x100

block1a.add_instance(shared_rect)
block1b.add_instance(shared_rect)  # Same instance!

top1.add_instance([block1a, block1b])
top1.pos_list = [0, 0, 1000, 1000]
block1a.pos_list = [100, 100, 300, 300]
block1b.pos_list = [600, 600, 800, 800]

print("\nStructure:")
print(f"  block1a contains: shared_rect (id={id(shared_rect)})")
print(f"  block1b contains: shared_rect (id={id(shared_rect)}) - SAME object")
print(f"  This is PROPER REUSE - should only create ONE GDS 'rect' cell")

gds_file1 = 'test_reuse_proper.gds'
top1.export_gds(gds_file1, use_tech_file=False)

import gdstk
lib1 = gdstk.read_gds(gds_file1)

rect_cells = [c for c in lib1.cells if 'rect' in c.name.lower()]
print(f"\nGDS result: {len(rect_cells)} 'rect' cell(s) in GDS file")
for cell in rect_cells:
    print(f"  - '{cell.name}'")

if len(rect_cells) == 1:
    print("  ✓ CORRECT: Only one GDS cell (proper reuse)")
else:
    print(f"  ✗ WRONG: Should be 1, got {len(rect_cells)}")

os.remove(gds_file1)

# ==============================================================================
# Test 2: Name collision (different cells, same name)
# ==============================================================================
print("\n" + "="*70)
print("Test 2: Name collision - different cells with same name")
print("="*70)

top2 = Cell('top2')
block2a = Cell('block2a')
block2b = Cell('block2b')

# Create TWO different rect cells with same name
rect_a = Cell('rect', 'metal1')  # Different object
rect_a.pos_list = [0, 0, 100, 100]  # 100x100

rect_b = Cell('rect', 'metal1')  # Different object, same name!
rect_b.pos_list = [0, 0, 200, 200]  # 200x200 - DIFFERENT SIZE

block2a.add_instance(rect_a)
block2b.add_instance(rect_b)

top2.add_instance([block2a, block2b])
top2.pos_list = [0, 0, 1000, 1000]
block2a.pos_list = [100, 100, 300, 300]
block2b.pos_list = [600, 600, 900, 900]

print("\nStructure:")
print(f"  block2a contains: rect_a (id={id(rect_a)}, size=100x100)")
print(f"  block2b contains: rect_b (id={id(rect_b)}, size=200x200)")
print(f"  DIFFERENT objects, same name, DIFFERENT content")
print(f"  Must create unique GDS names to preserve both")

gds_file2 = 'test_reuse_collision.gds'
top2.export_gds(gds_file2, use_tech_file=False)

lib2 = gdstk.read_gds(gds_file2)

rect_cells2 = [c for c in lib2.cells if 'rect' in c.name.lower()]
print(f"\nGDS result: {len(rect_cells2)} 'rect' cell(s) in GDS file")
for cell in rect_cells2:
    if cell.polygons:
        bbox = cell.polygons[0].bounding_box()
        size = (bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1])
        print(f"  - '{cell.name}': size={size}")

if len(rect_cells2) == 2:
    print("  ✓ CORRECT: Two GDS cells (different content, unique names needed)")

    # Check sizes are different
    sizes = set()
    for cell in rect_cells2:
        if cell.polygons:
            bbox = cell.polygons[0].bounding_box()
            w = bbox[1][0] - bbox[0][0]
            sizes.add(w)

    if len(sizes) == 2:
        print(f"  ✓ Both sizes preserved: {sizes}")
    else:
        print(f"  ✗ Size mismatch: {sizes}")
else:
    print(f"  ✗ WRONG: Should be 2, got {len(rect_cells2)}")

os.remove(gds_file2)

# ==============================================================================
# Test 3: Mixed case - reuse AND collision
# ==============================================================================
print("\n" + "="*70)
print("Test 3: Mixed - both reuse and collision")
print("="*70)

top3 = Cell('top3')
b1 = Cell('b1')
b2 = Cell('b2')
b3 = Cell('b3')

# Cell A - used in b1 and b2 (reuse)
cell_a = Cell('shared', 'metal1')
cell_a.pos_list = [0, 0, 50, 50]

# Cell B - used only in b3, different content but same name
cell_b = Cell('shared', 'metal2')  # DIFFERENT layer
cell_b.pos_list = [0, 0, 50, 50]  # Same size but different layer

b1.add_instance(cell_a)
b2.add_instance(cell_a)  # Reuse cell_a
b3.add_instance(cell_b)  # Different cell, same name

top3.add_instance([b1, b2, b3])
top3.pos_list = [0, 0, 1000, 1000]
b1.pos_list = [100, 100, 200, 200]
b2.pos_list = [300, 300, 400, 400]
b3.pos_list = [600, 600, 700, 700]

print("\nStructure:")
print(f"  b1 contains: cell_a (id={id(cell_a)}, layer=metal1)")
print(f"  b2 contains: cell_a (id={id(cell_a)}, layer=metal1) - REUSE")
print(f"  b3 contains: cell_b (id={id(cell_b)}, layer=metal2) - COLLISION")
print(f"  Expected: 2 GDS 'shared' cells (one for metal1, one for metal2)")

gds_file3 = 'test_reuse_mixed.gds'
top3.export_gds(gds_file3, use_tech_file=False)

lib3 = gdstk.read_gds(gds_file3)

shared_cells = [c for c in lib3.cells if 'shared' in c.name.lower()]
print(f"\nGDS result: {len(shared_cells)} 'shared' cell(s)")
for cell in shared_cells:
    if cell.polygons:
        layer = cell.polygons[0].layer
        print(f"  - '{cell.name}': layer={layer}")

if len(shared_cells) == 2:
    layers = {cell.polygons[0].layer for cell in shared_cells if cell.polygons}
    if len(layers) == 2:
        print(f"  ✓ CORRECT: Two cells with different layers: {layers}")
    else:
        print(f"  ✗ Layer issue: {layers}")
else:
    print(f"  ✗ WRONG: Expected 2, got {len(shared_cells)}")

os.remove(gds_file3)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("Current implementation:")
print("  ✓ Uses object ID to avoid overwrites")
print("  ✓ Creates unique names when needed (rect_1, rect_2)")
print("  ✓ Preserves all different cell contents")
print("\nIdeal implementation would also:")
print("  - Detect when cells have identical content")
print("  - Reuse GDS cell definition for identical content")
print("  - Only create unique names when content differs")
print("="*70)
