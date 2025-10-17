"""
Advanced tests for fix_layout feature

Tests:
1. fix_layout with copy() - Multiple copies of fixed cell
2. fix_layout with hierarchical cells - Nested structures
3. fix_layout with deep hierarchy - Multiple levels
4. Edge cases and combinations
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell


def test_fix_with_copy():
    """
    Test that copy() works correctly with fixed layouts.
    Each copy should be independently repositionable.
    """
    print("="*70)
    print("TEST 1: fix_layout with copy()")
    print("="*70)

    # Create and solve a block
    print("\n1. Creating a block with internal structure...")
    block = Cell('block')
    rect1 = Cell('rect1', 'metal1')
    rect2 = Cell('rect2', 'poly')

    block.add_instance([rect1, rect2])
    block.constrain(rect1, 'x2-x1=10, y2-y1=10')
    block.constrain(rect2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=5, sy2-sy1=10', rect1)
    block.constrain(rect1, 'sx1=x1, sy1=y1')

    block.solver()
    print(f"   ✓ Block solved: {block.pos_list}")
    print(f"      rect1: {rect1.pos_list}")
    print(f"      rect2: {rect2.pos_list}")

    # Fix the layout
    print("\n2. Fixing the layout...")
    block.fix_layout()
    print(f"   ✓ Block fixed (is_fixed={block.is_fixed()})")

    # Create three copies
    print("\n3. Creating three copies of the fixed block...")
    copy1 = block.copy('block_copy1')
    copy2 = block.copy('block_copy2')
    copy3 = block.copy('block_copy3')
    print(f"   ✓ Created copy1, copy2, copy3")
    print(f"   copy1.is_fixed() = {copy1.is_fixed()}")
    print(f"   copy2.is_fixed() = {copy2.is_fixed()}")
    print(f"   copy3.is_fixed() = {copy3.is_fixed()}")

    # Place all copies at different positions
    print("\n4. Placing copies at different positions...")
    parent = Cell('parent')
    parent.add_instance([copy1, copy2, copy3])

    parent.constrain(copy1, 'x1=0, y1=0')
    parent.constrain(copy2, 'x1=50, y1=0')
    parent.constrain(copy3, 'x1=0, y1=50')

    parent.solver()

    print(f"   ✓ Parent solved")
    print(f"\n   Copy positions:")
    print(f"      copy1: {copy1.pos_list}")
    print(f"      copy2: {copy2.pos_list}")
    print(f"      copy3: {copy3.pos_list}")

    # Check internal rectangles of each copy
    print(f"\n   Internal rectangles:")
    for copy in [copy1, copy2, copy3]:
        print(f"      {copy.name}:")
        for child in copy.children:
            print(f"         {child.name}: {child.pos_list}")

    # Verify each copy's internals updated correctly
    print("\n5. Verifying internal positions...")
    success = True

    # Check copy1 at (0, 0)
    copy1_rect1 = copy1.children[0]
    if copy1_rect1.pos_list[0] != 0 or copy1_rect1.pos_list[1] != 0:
        print(f"   ✗ copy1 rect1 not at origin")
        success = False
    else:
        print(f"   ✓ copy1 internals at (0, 0)")

    # Check copy2 at (50, 0)
    copy2_rect1 = copy2.children[0]
    if copy2_rect1.pos_list[0] != 50 or copy2_rect1.pos_list[1] != 0:
        print(f"   ✗ copy2 rect1 not at (50, 0)")
        success = False
    else:
        print(f"   ✓ copy2 internals at (50, 0)")

    # Check copy3 at (0, 50)
    copy3_rect1 = copy3.children[0]
    if copy3_rect1.pos_list[0] != 0 or copy3_rect1.pos_list[1] != 50:
        print(f"   ✗ copy3 rect1 not at (0, 50)")
        success = False
    else:
        print(f"   ✓ copy3 internals at (0, 50)")

    if success:
        print("\n" + "="*70)
        print("✓ TEST 1 PASSED: fix_layout works with copy()")
        print("  Each copy is independently repositionable!")
        print("="*70)
        return True
    else:
        print("\n" + "="*70)
        print("✗ TEST 1 FAILED")
        print("="*70)
        return False


def test_fix_with_hierarchy():
    """
    Test fix_layout with hierarchical cells.
    A parent cell contains child cells, and we fix the parent.
    """
    print("\n" + "="*70)
    print("TEST 2: fix_layout with hierarchical cells")
    print("="*70)

    # Create a child cell
    print("\n1. Creating child cell with 2 rectangles...")
    child_cell = Cell('child_cell')
    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'poly')

    child_cell.add_instance([r1, r2])
    child_cell.constrain(r1, 'x2-x1=8, y2-y1=8')
    child_cell.constrain(r2, 'sx1=ox2+1, sy1=oy1, sx2-sx1=3, sy2-sy1=8', r1)
    child_cell.constrain(r1, 'sx1=x1, sy1=y1')

    child_cell.solver()
    print(f"   ✓ Child cell solved: {child_cell.pos_list}")

    # Create a parent cell with two instances of child_cell
    print("\n2. Creating parent cell with 2 child instances...")
    parent_cell = Cell('parent_cell')
    child_a = child_cell.copy('child_a')
    child_b = child_cell.copy('child_b')

    parent_cell.add_instance([child_a, child_b])
    parent_cell.constrain(child_a, 'x1=0, y1=0')
    parent_cell.constrain(child_b, 'sx1=ox2+5, sy1=oy1', child_a)

    parent_cell.solver()
    print(f"   ✓ Parent cell solved: {parent_cell.pos_list}")
    print(f"      child_a: {child_a.pos_list}")
    print(f"      child_b: {child_b.pos_list}")

    # Fix the parent cell
    print("\n3. Fixing the parent cell...")
    parent_cell.fix_layout()
    print(f"   ✓ Parent cell fixed (is_fixed={parent_cell.is_fixed()})")

    # Get original positions for comparison
    orig_parent = tuple(parent_cell.pos_list)
    orig_child_a = tuple(child_a.pos_list)
    orig_child_b = tuple(child_b.pos_list)
    orig_r1_a = tuple(child_a.children[0].pos_list)
    orig_r2_a = tuple(child_a.children[1].pos_list)

    print(f"\n   Original positions:")
    print(f"      parent_cell: {orig_parent}")
    print(f"      child_a: {orig_child_a}")
    print(f"      child_b: {orig_child_b}")
    print(f"      child_a.r1: {orig_r1_a}")
    print(f"      child_a.r2: {orig_r2_a}")

    # Reposition the parent cell
    print("\n4. Repositioning parent to (100, 100)...")
    top = Cell('top')
    top.add_instance(parent_cell)
    top.constrain(parent_cell, 'x1=100, y1=100')

    top.solver()

    print(f"   ✓ Top solved")
    print(f"\n   New positions:")
    print(f"      parent_cell: {parent_cell.pos_list}")
    print(f"      child_a: {child_a.pos_list}")
    print(f"      child_b: {child_b.pos_list}")
    print(f"      child_a.r1: {child_a.children[0].pos_list}")
    print(f"      child_a.r2: {child_a.children[1].pos_list}")

    # Verify positions updated correctly
    print("\n5. Verifying hierarchical updates...")

    # Parent should be at (100, 100)
    if parent_cell.pos_list[0] != 100 or parent_cell.pos_list[1] != 100:
        print(f"   ✗ Parent not at (100, 100)")
        return False
    print(f"   ✓ Parent at (100, 100)")

    # Child_a should have moved by (100, 100)
    expected_child_a = (orig_child_a[0] + 100, orig_child_a[1] + 100)
    if child_a.pos_list[0] != expected_child_a[0] or child_a.pos_list[1] != expected_child_a[1]:
        print(f"   ✗ child_a not at expected position")
        print(f"      Expected: ({expected_child_a[0]}, {expected_child_a[1]})")
        print(f"      Got: ({child_a.pos_list[0]}, {child_a.pos_list[1]})")
        return False
    print(f"   ✓ child_a moved correctly to ({child_a.pos_list[0]}, {child_a.pos_list[1]})")

    # Child_b should have moved by (100, 100)
    expected_child_b = (orig_child_b[0] + 100, orig_child_b[1] + 100)
    if child_b.pos_list[0] != expected_child_b[0] or child_b.pos_list[1] != expected_child_b[1]:
        print(f"   ✗ child_b not at expected position")
        return False
    print(f"   ✓ child_b moved correctly to ({child_b.pos_list[0]}, {child_b.pos_list[1]})")

    # Grandchildren (r1, r2) should also have moved
    expected_r1_a = (orig_r1_a[0] + 100, orig_r1_a[1] + 100)
    r1_a = child_a.children[0]
    if r1_a.pos_list[0] != expected_r1_a[0] or r1_a.pos_list[1] != expected_r1_a[1]:
        print(f"   ✗ r1 in child_a not at expected position")
        print(f"      Expected: ({expected_r1_a[0]}, {expected_r1_a[1]})")
        print(f"      Got: ({r1_a.pos_list[0]}, {r1_a.pos_list[1]})")
        return False
    print(f"   ✓ Grandchild r1 moved correctly to ({r1_a.pos_list[0]}, {r1_a.pos_list[1]})")

    print("\n" + "="*70)
    print("✓ TEST 2 PASSED: fix_layout works with hierarchical cells")
    print("  All levels of hierarchy update correctly!")
    print("="*70)
    return True


def test_deep_hierarchy():
    """
    Test fix_layout with multiple levels of hierarchy.
    Level 3 -> Level 2 -> Level 1 -> Leaf cells
    """
    print("\n" + "="*70)
    print("TEST 3: fix_layout with deep hierarchy")
    print("="*70)

    # Level 1: Basic cell with 2 rectangles
    print("\n1. Creating Level 1 (leaf level)...")
    level1 = Cell('level1')
    leaf1 = Cell('leaf1', 'metal1')
    leaf2 = Cell('leaf2', 'poly')

    level1.add_instance([leaf1, leaf2])
    level1.constrain(leaf1, 'x2-x1=5, y2-y1=5')
    level1.constrain(leaf2, 'sx1=ox2+1, sy1=oy1, sx2-sx1=3, sy2-sy1=5', leaf1)
    level1.constrain(leaf1, 'sx1=x1, sy1=y1')

    level1.solver()
    print(f"   ✓ Level1 solved: {level1.pos_list}")

    # Level 2: Contains two level1 instances
    print("\n2. Creating Level 2...")
    level2 = Cell('level2')
    l1_a = level1.copy('l1_a')
    l1_b = level1.copy('l1_b')

    level2.add_instance([l1_a, l1_b])
    level2.constrain(l1_a, 'x1=0, y1=0')
    level2.constrain(l1_b, 'sx1=ox2+3, sy1=oy1', l1_a)

    level2.solver()
    print(f"   ✓ Level2 solved: {level2.pos_list}")

    # Level 3: Contains two level2 instances
    print("\n3. Creating Level 3...")
    level3 = Cell('level3')
    l2_a = level2.copy('l2_a')
    l2_b = level2.copy('l2_b')

    level3.add_instance([l2_a, l2_b])
    level3.constrain(l2_a, 'x1=0, y1=0')
    level3.constrain(l2_b, 'sx1=ox2+5, sy1=oy1', l2_a)

    level3.solver()
    print(f"   ✓ Level3 solved: {level3.pos_list}")

    # Fix level3
    print("\n4. Fixing Level 3...")
    level3.fix_layout()
    print(f"   ✓ Level3 fixed")

    # Store original leaf position
    orig_leaf1 = tuple(l2_a.children[0].children[0].pos_list)
    print(f"   Original deepest leaf position: {orig_leaf1}")

    # Reposition level3
    print("\n5. Repositioning Level 3 to (200, 200)...")
    top = Cell('top')
    top.add_instance(level3)
    top.constrain(level3, 'x1=200, y1=200')

    top.solver()

    print(f"   ✓ Top solved")
    print(f"      level3: {level3.pos_list}")

    # Check the deepest leaf cell
    new_leaf1 = tuple(l2_a.children[0].children[0].pos_list)
    print(f"   New deepest leaf position: {new_leaf1}")

    # Verify the deepest leaf moved by (200, 200)
    expected_leaf = (orig_leaf1[0] + 200, orig_leaf1[1] + 200)

    print("\n6. Verifying deep hierarchy update...")
    if new_leaf1[0] == expected_leaf[0] and new_leaf1[1] == expected_leaf[1]:
        print(f"   ✓ Deepest leaf moved correctly!")
        print(f"      Expected: {expected_leaf}")
        print(f"      Got: {new_leaf1}")
        print("\n" + "="*70)
        print("✓ TEST 3 PASSED: fix_layout works with deep hierarchy")
        print("  Even deeply nested cells update correctly!")
        print("="*70)
        return True
    else:
        print(f"   ✗ Deepest leaf position incorrect")
        print(f"      Expected: {expected_leaf}")
        print(f"      Got: {new_leaf1}")
        print("\n" + "="*70)
        print("✗ TEST 3 FAILED")
        print("="*70)
        return False


def run_all_tests():
    """Run all advanced tests"""
    print("\n" + "="*70)
    print("ADVANCED TESTS FOR fix_layout")
    print("="*70)

    results = []

    # Test 1: copy()
    results.append(("fix_layout with copy()", test_fix_with_copy()))

    # Test 2: hierarchy
    results.append(("fix_layout with hierarchy", test_fix_with_hierarchy()))

    # Test 3: deep hierarchy
    results.append(("fix_layout with deep hierarchy", test_deep_hierarchy()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        return False


if __name__ == '__main__':
    if run_all_tests():
        sys.exit(0)
    else:
        sys.exit(1)
