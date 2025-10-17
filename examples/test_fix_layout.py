"""
Test fix_layout feature - repositionable cells with automatic internal updates

This test verifies that:
1. A cell can be "fixed" after solving
2. The fixed cell can be repositioned via constraints
3. When repositioned, all internal polygons automatically update their positions
4. The relative offsets between parent and children are preserved

This is different from freeze_layout:
- freeze: treats cell as black box, internal structure locked and hidden
- fix: allows repositioning while updating and exposing all internal elements
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

def test_fix_layout():
    """
    Test that fixed layouts can be repositioned and internal elements update correctly
    """
    print("="*70)
    print("Testing fix_layout Feature")
    print("="*70)

    # 1. Create a block with internal structure
    print("\n1. Creating block with 3 internal rectangles...")
    block = Cell('block')
    rect1 = Cell('rect1', 'metal1')
    rect2 = Cell('rect2', 'poly')
    rect3 = Cell('rect3', 'metal1')

    block.add_instance([rect1, rect2, rect3])

    # Define internal structure with relative constraints
    block.constrain(rect1, 'x2-x1=10, y2-y1=10')
    block.constrain(rect2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=5, sy2-sy1=10', rect1)
    block.constrain(rect3, 'sx1=ox1, sy1=oy2+2, sx2-sx1=17, sy2-sy1=5', rect1)
    block.constrain(rect1, 'sx1=x1, sy1=y1')  # Align to block origin

    # Solve to get initial positions
    if not block.solver():
        print("✗ Failed to solve block")
        return False

    print("   ✓ Block solved successfully")
    print(f"      block: {block.pos_list}")
    print(f"      rect1: {rect1.pos_list}")
    print(f"      rect2: {rect2.pos_list}")
    print(f"      rect3: {rect3.pos_list}")

    # 2. Fix the layout
    print("\n2. Fixing the layout...")
    block.fix_layout()
    print(f"   ✓ Block fixed (is_fixed={block.is_fixed()})")

    # Store original positions for comparison
    original_block = tuple(block.pos_list)
    original_rect1 = tuple(rect1.pos_list)
    original_rect2 = tuple(rect2.pos_list)
    original_rect3 = tuple(rect3.pos_list)

    # Calculate original offsets
    orig_rect1_offset = (
        rect1.pos_list[0] - block.pos_list[0],
        rect1.pos_list[1] - block.pos_list[1]
    )
    orig_rect2_offset = (
        rect2.pos_list[0] - block.pos_list[0],
        rect2.pos_list[1] - block.pos_list[1]
    )
    orig_rect3_offset = (
        rect3.pos_list[0] - block.pos_list[0],
        rect3.pos_list[1] - block.pos_list[1]
    )

    print(f"   Original offsets from block origin:")
    print(f"      rect1: offset=({orig_rect1_offset[0]}, {orig_rect1_offset[1]})")
    print(f"      rect2: offset=({orig_rect2_offset[0]}, {orig_rect2_offset[1]})")
    print(f"      rect3: offset=({orig_rect3_offset[0]}, {orig_rect3_offset[1]})")

    # 3. Place the fixed block in a parent cell at a NEW position
    print("\n3. Placing fixed block in parent at position (100, 50)...")
    parent = Cell('parent')
    parent.add_instance(block)
    parent.constrain(block, 'x1=100, y1=50')

    # Solve parent - this should reposition the block
    if not parent.solver():
        print("✗ Failed to solve parent")
        return False

    print("   ✓ Parent solved successfully")
    print(f"      block: {block.pos_list}")
    print(f"      rect1: {rect1.pos_list}")
    print(f"      rect2: {rect2.pos_list}")
    print(f"      rect3: {rect3.pos_list}")

    # 4. Verify that the block moved to the new position
    new_block = tuple(block.pos_list)
    new_rect1 = tuple(rect1.pos_list)
    new_rect2 = tuple(rect2.pos_list)
    new_rect3 = tuple(rect3.pos_list)

    print("\n4. Verifying positions after repositioning...")

    # Check block moved to correct position
    if block.pos_list[0] != 100 or block.pos_list[1] != 50:
        print(f"✗ Block did not move to (100, 50), got ({block.pos_list[0]}, {block.pos_list[1]})")
        return False
    print(f"   ✓ Block repositioned to (100, 50)")

    # Check internal rectangles updated
    new_rect1_offset = (
        rect1.pos_list[0] - block.pos_list[0],
        rect1.pos_list[1] - block.pos_list[1]
    )
    new_rect2_offset = (
        rect2.pos_list[0] - block.pos_list[0],
        rect2.pos_list[1] - block.pos_list[1]
    )
    new_rect3_offset = (
        rect3.pos_list[0] - block.pos_list[0],
        rect3.pos_list[1] - block.pos_list[1]
    )

    print(f"   New offsets from block origin:")
    print(f"      rect1: offset=({new_rect1_offset[0]}, {new_rect1_offset[1]})")
    print(f"      rect2: offset=({new_rect2_offset[0]}, {new_rect2_offset[1]})")
    print(f"      rect3: offset=({new_rect3_offset[0]}, {new_rect3_offset[1]})")

    # 5. Verify offsets are preserved
    print("\n5. Checking that relative offsets are preserved...")

    offsets_match = True

    if new_rect1_offset != orig_rect1_offset:
        print(f"   ✗ rect1 offset changed!")
        offsets_match = False
    else:
        print(f"   ✓ rect1 offset preserved")

    if new_rect2_offset != orig_rect2_offset:
        print(f"   ✗ rect2 offset changed!")
        offsets_match = False
    else:
        print(f"   ✓ rect2 offset preserved")

    if new_rect3_offset != orig_rect3_offset:
        print(f"   ✗ rect3 offset changed!")
        offsets_match = False
    else:
        print(f"   ✓ rect3 offset preserved")

    # 6. Try repositioning again to a different location
    print("\n6. Repositioning block to (200, 150)...")
    parent2 = Cell('parent2')
    parent2.add_instance(block)
    parent2.constrain(block, 'x1=200, y1=150')

    if not parent2.solver():
        print("✗ Failed to solve parent2")
        return False

    print("   ✓ Parent2 solved successfully")
    print(f"      block: {block.pos_list}")
    print(f"      rect1: {rect1.pos_list}")
    print(f"      rect2: {rect2.pos_list}")
    print(f"      rect3: {rect3.pos_list}")

    # Verify positions again
    final_rect1_offset = (
        rect1.pos_list[0] - block.pos_list[0],
        rect1.pos_list[1] - block.pos_list[1]
    )
    final_rect2_offset = (
        rect2.pos_list[0] - block.pos_list[0],
        rect2.pos_list[1] - block.pos_list[1]
    )
    final_rect3_offset = (
        rect3.pos_list[0] - block.pos_list[0],
        rect3.pos_list[1] - block.pos_list[1]
    )

    if (final_rect1_offset == orig_rect1_offset and
        final_rect2_offset == orig_rect2_offset and
        final_rect3_offset == orig_rect3_offset):
        print("   ✓ Offsets still preserved after second repositioning")
    else:
        print("   ✗ Offsets changed after second repositioning")
        offsets_match = False

    # Final result
    if offsets_match:
        print("\n" + "="*70)
        print("✓ TEST PASSED!")
        print("  fix_layout works correctly:")
        print("  - Block can be repositioned multiple times")
        print("  - Internal polygons automatically update")
        print("  - Relative offsets are perfectly preserved")
        print("="*70)
        return True
    else:
        print("\n" + "="*70)
        print("✗ TEST FAILED!")
        print("  Relative offsets were not preserved correctly")
        print("="*70)
        return False


if __name__ == '__main__':
    if test_fix_layout():
        sys.exit(0)
    else:
        sys.exit(1)
