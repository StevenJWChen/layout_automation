"""
Comparison test: fix_layout vs freeze_layout

This demonstrates the key differences:

freeze_layout:
- Treats cell as a black box (internal structure hidden)
- Fixed size: x2-x1 and y2-y1 are constant
- Internal polygons are NOT accessible after freezing
- Used for optimization: reduces solver complexity
- Example: Standard cell library blocks

fix_layout:
- Internal structure remains visible and accessible
- Can be repositioned, all internals update automatically
- Preserves relative offsets between parent and children
- Used for reusable layout blocks that need to be repositioned
- Example: Arraying blocks at different positions
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell

def create_test_block(name):
    """Create a test block with 3 rectangles"""
    block = Cell(name)
    rect1 = Cell(f'{name}_rect1', 'metal1')
    rect2 = Cell(f'{name}_rect2', 'poly')
    rect3 = Cell(f'{name}_rect3', 'metal1')

    block.add_instance([rect1, rect2, rect3])

    # Define internal structure
    block.constrain(rect1, 'x2-x1=10, y2-y1=10')
    block.constrain(rect2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=5, sy2-sy1=10', rect1)
    block.constrain(rect3, 'sx1=ox1, sy1=oy2+2, sx2-sx1=17, sy2-sy1=5', rect1)
    block.constrain(rect1, 'sx1=x1, sy1=y1')

    block.solver()
    return block


def test_freeze_layout():
    """Test freeze_layout behavior"""
    print("="*70)
    print("Testing freeze_layout")
    print("="*70)

    block = create_test_block('frozen_block')
    print(f"\n1. Original block position: {block.pos_list}")
    print(f"   Internal rectangles:")
    for child in block.children:
        print(f"      {child.name}: {child.pos_list}")

    # Freeze the block
    print(f"\n2. Freezing block...")
    block.freeze_layout()
    bbox = block.get_bbox()
    print(f"   ✓ Frozen with bbox: {bbox}")
    print(f"   is_frozen: {block.is_frozen()}")

    # Try to place in parent
    print(f"\n3. Placing frozen block at (100, 50)...")
    parent = Cell('parent_frozen')
    parent.add_instance(block)

    # For frozen blocks, must specify full bbox
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    parent.constrain(block, f'x1=100, y1=50, x2={100+width}, y2={50+height}')

    parent.solver()

    print(f"   ✓ Block position: {block.pos_list}")
    print(f"   Internal rectangles (still at original positions):")
    for child in block.children:
        print(f"      {child.name}: {child.pos_list}")

    print("\n   Key observation:")
    print("   - Block bbox moved to (100, 50)")
    print("   - BUT internal rectangles did NOT update")
    print("   - They remain at original (0, 0) origin positions")
    print("   - This is because frozen cells are treated as black boxes")


def test_fix_layout():
    """Test fix_layout behavior"""
    print("\n" + "="*70)
    print("Testing fix_layout")
    print("="*70)

    block = create_test_block('fixed_block')
    print(f"\n1. Original block position: {block.pos_list}")
    print(f"   Internal rectangles:")
    for child in block.children:
        print(f"      {child.name}: {child.pos_list}")

    # Fix the layout
    print(f"\n2. Fixing block...")
    block.fix_layout()
    print(f"   ✓ Fixed")
    print(f"   is_fixed: {block.is_fixed()}")

    # Place in parent
    print(f"\n3. Placing fixed block at (100, 50)...")
    parent = Cell('parent_fixed')
    parent.add_instance(block)
    parent.constrain(block, 'x1=100, y1=50')

    parent.solver()

    print(f"   ✓ Block position: {block.pos_list}")
    print(f"   Internal rectangles (updated automatically!):")
    for child in block.children:
        print(f"      {child.name}: {child.pos_list}")

    print("\n   Key observation:")
    print("   - Block moved to (100, 50)")
    print("   - AND internal rectangles automatically updated!")
    print("   - rect1 is now at (100, 50) - moved with block")
    print("   - rect2 is at (112, 50) - maintained 12-unit offset")
    print("   - rect3 is at (100, 62) - maintained 12-unit y-offset")


def test_comparison():
    """Compare freeze vs fix side-by-side"""
    print("\n" + "="*70)
    print("COMPARISON: freeze_layout vs fix_layout")
    print("="*70)

    # Create two identical blocks
    frozen_block = create_test_block('frozen')
    fixed_block = create_test_block('fixed')

    print("\n1. Both blocks start at origin with same internal structure")
    print(f"   frozen_block: {frozen_block.pos_list}")
    print(f"   fixed_block:  {fixed_block.pos_list}")

    # Apply freeze to one, fix to the other
    frozen_block.freeze_layout()
    fixed_block.fix_layout()

    print("\n2. Apply freeze to first block, fix to second block")

    # Place both at position (100, 50)
    print("\n3. Place both blocks at (100, 50)...")

    # Frozen block
    parent_frozen = Cell('parent_frozen')
    parent_frozen.add_instance(frozen_block)
    bbox = frozen_block.get_bbox()
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    parent_frozen.constrain(frozen_block, f'x1=100, y1=50, x2={100+width}, y2={50+height}')
    parent_frozen.solver()

    # Fixed block
    parent_fixed = Cell('parent_fixed')
    parent_fixed.add_instance(fixed_block)
    parent_fixed.constrain(fixed_block, 'x1=100, y1=50')
    parent_fixed.solver()

    print("\n4. Results:")
    print("\n   FROZEN BLOCK:")
    print(f"      Block bbox: {frozen_block.pos_list}")
    print(f"      Internal rectangles (not updated):")
    for child in frozen_block.children:
        print(f"         {child.name}: {child.pos_list}")

    print("\n   FIXED BLOCK:")
    print(f"      Block bbox: {fixed_block.pos_list}")
    print(f"      Internal rectangles (automatically updated!):")
    for child in fixed_block.children:
        print(f"         {child.name}: {child.pos_list}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nfreeze_layout:")
    print("  ✓ Optimizes solver (treats as black box)")
    print("  ✓ Fixed size (width/height constant)")
    print("  ✗ Internal structure hidden/inaccessible")
    print("  ✗ Internal polygons don't update when repositioned")
    print("  → Use for: Standard cell libraries, optimization")

    print("\nfix_layout:")
    print("  ✓ Internal structure visible and accessible")
    print("  ✓ Automatic position updates for all internals")
    print("  ✓ Preserves relative offsets perfectly")
    print("  ✓ Easy to reposition (just constrain x1, y1)")
    print("  → Use for: Reusable blocks, arrays, repositionable layouts")
    print("="*70)


if __name__ == '__main__':
    test_freeze_layout()
    test_fix_layout()
    test_comparison()
