"""
Test fix_layout cells with constraint-based positioning

This test verifies that fixed layout cells can be positioned correctly
using constraints in a parent cell, not just manual set_position().
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell


def test_constraint_positioning():
    """Test that fixed cells can be positioned via constraints"""
    print("="*70)
    print("TEST: Fixed cells with constraint-based positioning")
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
    print(f"   child: {child.pos_list}")

    # Copy and fix
    print("\n2. Copying and fixing...")
    c = child.copy('c')
    c.fix_layout()
    print(f"   c (fixed): {c.pos_list}")

    # Test 1: Relative positioning constraint
    print("\n3. Test 1: Relative positioning (sx2+5=ox1)")
    top1 = Cell('top1')
    top1.add_instance([child.copy('child1'), c.copy('c1')])
    top1.constrain(top1.child_dict['child1'], 'sx2+5=ox1', top1.child_dict['c1'])
    top1.solver()

    child1 = top1.child_dict['child1']
    c1 = top1.child_dict['c1']
    expected = child1.pos_list[2] + 5
    actual = c1.pos_list[0]
    print(f"   child1.x2 + 5 = {expected}")
    print(f"   c1.x1 = {actual}")
    assert abs(expected - actual) < 1e-6, f"Constraint not satisfied: {expected} != {actual}"
    print("   ✓ PASS")

    # Test 2: Absolute positioning constraint
    print("\n4. Test 2: Absolute positioning (x1=100, y1=50)")
    top2 = Cell('top2')
    c2 = c.copy('c2')
    top2.add_instance(c2)
    top2.constrain(c2, 'x1=100, y1=50')
    top2.solver()

    assert c2.pos_list[0] == 100 and c2.pos_list[1] == 50, \
        f"Absolute position wrong: {c2.pos_list}"
    # Check that children moved
    r1_c2 = [ch for ch in c2.children if 'r1' in ch.name][0]
    assert r1_c2.pos_list[0] == 100 and r1_c2.pos_list[1] == 50, \
        f"Child not updated: {r1_c2.pos_list}"
    print(f"   c2: {c2.pos_list}")
    print(f"   c2.r1: {r1_c2.pos_list}")
    print("   ✓ PASS")

    # Test 3: Multiple fixed cells with constraints
    print("\n5. Test 3: Multiple fixed cells in a row")
    top3 = Cell('top3')
    c3a = c.copy('c3a')
    c3b = c.copy('c3b')
    c3c = c.copy('c3c')
    top3.add_instance([c3a, c3b, c3c])
    top3.constrain(c3a, 'x1=0, y1=0')
    top3.constrain(c3b, 'sx1=ox2+10', c3a)  # 10 units after c3a
    top3.constrain(c3c, 'sx1=ox2+10', c3b)  # 10 units after c3b
    top3.solver()

    print(f"   c3a: {c3a.pos_list}")
    print(f"   c3b: {c3b.pos_list}")
    print(f"   c3c: {c3c.pos_list}")

    # Verify spacing
    spacing_ab = c3b.pos_list[0] - c3a.pos_list[2]
    spacing_bc = c3c.pos_list[0] - c3b.pos_list[2]
    assert abs(spacing_ab - 10) < 1e-6, f"Spacing AB wrong: {spacing_ab}"
    assert abs(spacing_bc - 10) < 1e-6, f"Spacing BC wrong: {spacing_bc}"
    print("   ✓ PASS")

    # Test 4: Fixed cells in hierarchy
    print("\n6. Test 4: Fixed cell as child of non-fixed parent")
    parent = Cell('parent')
    c4 = c.copy('c4')
    other = Cell('other', 'metal1')
    parent.add_instance([c4, other])
    parent.constrain(c4, 'x1=10, y1=10')
    parent.constrain(other, 'x2-x1=5, y2-y1=5')
    parent.constrain(other, 'sx1=ox2+5, sy1=oy1', c4)
    parent.solver()

    print(f"   parent: {parent.pos_list}")
    print(f"   c4: {c4.pos_list}")
    print(f"   other: {other.pos_list}")

    # Verify c4 at (10,10)
    assert c4.pos_list[0] == 10 and c4.pos_list[1] == 10, \
        f"c4 position wrong: {c4.pos_list}"
    # Verify other is 5 units right of c4
    assert abs(other.pos_list[0] - c4.pos_list[2] - 5) < 1e-6, \
        f"other position wrong: {other.pos_list}"
    print("   ✓ PASS")

    print("\n" + "="*70)
    print("✓ ALL CONSTRAINT POSITIONING TESTS PASSED!")
    print("="*70)

    return True


if __name__ == '__main__':
    success = test_constraint_positioning()
    sys.exit(0 if success else 1)
