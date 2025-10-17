"""
Test fix_layout with correct understanding:

1. Solve original cell
2. fix_layout() creates a fixed layout cell
3. Copy the fixed cell → copies are also fixed
4. Place fixed cells by:
   a) Setting position manually: cell.set_position(x1, y1)
   b) Using constraints in parent cell
5. When position changes, all internal polygons update automatically

Fixed cells should NOT need solver - they just update positions!
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell


def test_basic_fix_and_manual_placement():
    """Test fixing and manually placing a cell"""
    print("="*70)
    print("TEST 1: Basic fix_layout with manual placement")
    print("="*70)

    # Create and solve a cell
    print("\n1. Creating and solving a cell...")
    cell = Cell('cell')
    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'poly')

    cell.add_instance([r1, r2])
    cell.constrain(r1, 'x2-x1=10, y2-y1=10')
    cell.constrain(r2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=5, sy2-sy1=10', r1)
    cell.constrain(r1, 'sx1=x1, sy1=y1')

    cell.solver()
    print(f"   ✓ Solved: cell={cell.pos_list}, r1={r1.pos_list}, r2={r2.pos_list}")

    # Fix the layout
    print("\n2. Fixing the layout...")
    cell.fix_layout()
    print(f"   ✓ Fixed (is_fixed={cell.is_fixed()})")

    # Manually set position
    print("\n3. Manually setting position to (100, 50)...")
    cell.set_position(100, 50)
    print(f"   ✓ Position set")
    print(f"      cell: {cell.pos_list}")
    print(f"      r1: {r1.pos_list}")
    print(f"      r2: {r2.pos_list}")

    # Verify positions
    if cell.pos_list[0] == 100 and cell.pos_list[1] == 50:
        if r1.pos_list[0] == 100 and r1.pos_list[1] == 50:
            if r2.pos_list[0] == 112 and r2.pos_list[1] == 50:
                print("\n✓ TEST 1 PASSED: Manual placement works!")
                return True

    print("\n✗ TEST 1 FAILED")
    return False


def test_copy_fixed_cell():
    """Test copying a fixed cell"""
    print("\n" + "="*70)
    print("TEST 2: Copying fixed cells")
    print("="*70)

    # Create, solve, and fix
    print("\n1. Creating, solving, and fixing a cell...")
    cell = Cell('cell')
    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'poly')

    cell.add_instance([r1, r2])
    cell.constrain(r1, 'x2-x1=10, y2-y1=10')
    cell.constrain(r2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=5, sy2-sy1=10', r1)
    cell.constrain(r1, 'sx1=x1, sy1=y1')

    cell.solver()
    cell.fix_layout()
    print(f"   ✓ Fixed")

    # Copy the fixed cell
    print("\n2. Creating copies...")
    copy1 = cell.copy('copy1')
    copy2 = cell.copy('copy2')
    copy3 = cell.copy('copy3')
    print(f"   ✓ Created 3 copies")
    print(f"   copy1.is_fixed() = {copy1.is_fixed()}")

    # Place copies at different positions
    print("\n3. Placing copies at different positions...")
    copy1.set_position(0, 0)
    copy2.set_position(50, 0)
    copy3.set_position(0, 50)

    print(f"   copy1: {copy1.pos_list}")
    print(f"   copy2: {copy2.pos_list}")
    print(f"   copy3: {copy3.pos_list}")

    # Check internals
    print(f"\n4. Checking internal positions...")
    print(f"   copy1.r1: {copy1.children[0].pos_list}")
    print(f"   copy2.r1: {copy2.children[0].pos_list}")
    print(f"   copy3.r1: {copy3.children[0].pos_list}")

    # Verify
    c1_r1 = copy1.children[0]
    c2_r1 = copy2.children[0]
    c3_r1 = copy3.children[0]

    if (c1_r1.pos_list[0] == 0 and c1_r1.pos_list[1] == 0 and
        c2_r1.pos_list[0] == 50 and c2_r1.pos_list[1] == 0 and
        c3_r1.pos_list[0] == 0 and c3_r1.pos_list[1] == 50):
        print("\n✓ TEST 2 PASSED: Copies work correctly!")
        return True

    print("\n✗ TEST 2 FAILED")
    return False


def test_hierarchical_fixed_cells():
    """Test fixed cells containing other cells"""
    print("\n" + "="*70)
    print("TEST 3: Hierarchical fixed cells")
    print("="*70)

    # Create child cell
    print("\n1. Creating child cell...")
    child = Cell('child')
    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'poly')

    child.add_instance([r1, r2])
    child.constrain(r1, 'x2-x1=8, y2-y1=8')
    child.constrain(r2, 'sx1=ox2+1, sy1=oy1, sx2-sx1=3, sy2-sy1=8', r1)
    child.constrain(r1, 'sx1=x1, sy1=y1')

    child.solver()
    print(f"   ✓ Child solved: {child.pos_list}")

    # Create parent with two child instances
    print("\n2. Creating parent cell with 2 child instances...")
    parent = Cell('parent')
    child_a = child.copy('child_a')
    child_b = child.copy('child_b')

    parent.add_instance([child_a, child_b])
    parent.constrain(child_a, 'x1=0, y1=0')
    parent.constrain(child_b, 'sx1=ox2+5, sy1=oy1', child_a)

    parent.solver()
    print(f"   ✓ Parent solved: {parent.pos_list}")
    print(f"      child_a: {child_a.pos_list}")
    print(f"      child_b: {child_b.pos_list}")

    # Fix the parent
    print("\n3. Fixing the parent...")
    parent.fix_layout()
    print(f"   ✓ Parent fixed")

    # Manually place parent
    print("\n4. Manually placing parent at (200, 100)...")
    parent.set_position(200, 100)

    print(f"   parent: {parent.pos_list}")
    print(f"   child_a: {child_a.pos_list}")
    print(f"   child_b: {child_b.pos_list}")
    print(f"   child_a.r1: {child_a.children[0].pos_list}")

    # Verify parent moved
    if parent.pos_list[0] == 200 and parent.pos_list[1] == 100:
        # Verify children moved
        if child_a.pos_list[0] == 200 and child_a.pos_list[1] == 100:
            # Verify grandchildren moved
            if child_a.children[0].pos_list[0] == 200 and child_a.children[0].pos_list[1] == 100:
                print("\n✓ TEST 3 PASSED: Hierarchical fixed cells work!")
                return True

    print("\n✗ TEST 3 FAILED")
    return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("CORRECT UNDERSTANDING OF fix_layout")
    print("="*70)

    results = []
    results.append(("Manual placement", test_basic_fix_and_manual_placement()))
    results.append(("Copy fixed cells", test_copy_fixed_cell()))
    results.append(("Hierarchical fixed cells", test_hierarchical_fixed_cells()))

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
