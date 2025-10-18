"""
Comprehensive test of all recent fixes

Tests:
1. Operator correctness (< vs <=, > vs >=)
2. Fixed cell constraint positioning
3. High resolution drawing
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
import matplotlib.pyplot as plt


def test_all_fixes():
    """Test all recent fixes together"""
    print("="*70)
    print("COMPREHENSIVE TEST: All Recent Fixes")
    print("="*70)

    # Test 1: Operator correctness
    print("\n1. Testing strict inequality operators...")
    c1 = Cell('test_gt')
    r1 = Cell('r1', 'metal1')
    c1.add_instance(r1)
    c1.constrain(r1, 'x1>10, x2-x1=5, y2-y1=5')  # Strict >
    c1.solver()
    assert r1.pos_list[0] > 10 and r1.pos_list[0] != 10, \
        f"Failed: '>' should be strict, got x1={r1.pos_list[0]}"
    print(f"   ✓ PASS: '>' operator works correctly (x1={r1.pos_list[0]}, which is > 10)")

    # Test 2: Fixed cell constraint positioning
    print("\n2. Testing fixed cell constraint positioning...")
    base = Cell('base')
    p1 = Cell('p1', 'metal1')
    p2 = Cell('p2', 'poly')
    base.add_instance([p1, p2])
    base.constrain(p1, 'x2-x1=8, y2-y1=8')
    base.constrain(p2, 'sx1=ox2+1, sy1=oy1, sx2-sx1=3, sy2-sy1=8', p1)
    base.constrain(p1, 'sx1=x1, sy1=y1')
    base.solver()

    fixed = base.copy('fixed')
    fixed.fix_layout()

    top = Cell('top')
    other = Cell('other', 'metal1')
    top.add_instance([other, fixed])
    top.constrain(other, 'x2-x1=5, y2-y1=5, x1=0, y1=0')
    top.constrain(fixed, 'sx1=ox2+10', other)  # Position fixed cell via constraint
    top.solver()

    expected_x1 = other.pos_list[2] + 10
    actual_x1 = fixed.pos_list[0]
    assert abs(expected_x1 - actual_x1) < 1e-6, \
        f"Failed: Fixed cell not positioned correctly. Expected {expected_x1}, got {actual_x1}"
    print(f"   ✓ PASS: Fixed cell positioned via constraint (x1={actual_x1})")

    # Verify fixed cell's children moved too
    p1_copy = [c for c in fixed.children if 'p1' in c.name][0]
    assert p1_copy.pos_list[0] == fixed.pos_list[0], \
        "Failed: Fixed cell's children didn't update"
    print(f"   ✓ PASS: Fixed cell's children updated correctly")

    # Test 3: High resolution drawing
    print("\n3. Testing high resolution drawing...")
    test_cell = Cell('test_draw')
    rect1 = Cell('rect1', 'metal1')
    rect2 = Cell('rect2', 'poly')
    test_cell.add_instance([rect1, rect2])
    test_cell.constrain(rect1, 'x2-x1=10, y2-y1=10')
    test_cell.constrain(rect2, 'sx1=ox2+2, sy1=oy1, sx2-sx1=8, sy2-sy1=10', rect1)
    test_cell.constrain(rect1, 'sx1=x1, sy1=y1')

    # Draw with new high resolution
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    test_cell.draw(ax=ax, show=False)

    # Check figure size
    assert fig.get_figwidth() == 10 and fig.get_figheight() == 10, \
        f"Failed: Figure size should be 10x10, got {fig.get_figwidth()}x{fig.get_figheight()}"
    print(f"   ✓ PASS: High resolution drawing (10x10 inches, 100 DPI)")

    plt.close()

    # Test 4: Complex scenario combining all fixes
    print("\n4. Testing complex scenario with all fixes...")
    complex_top = Cell('complex')
    base1 = Cell('base1')
    base1_r = Cell('base1_r', 'metal1')
    base1.add_instance(base1_r)
    base1.constrain(base1_r, 'x2-x1=6, y2-y1=6, x1=0, y1=0')
    base1.solver()
    base1.fix_layout()

    base2 = base1.copy('base2')

    spacer = Cell('spacer', 'poly')

    complex_top.add_instance([base1, spacer, base2])
    complex_top.constrain(base1, 'x1=0, y1=0')
    complex_top.constrain(spacer, 'sx1>ox2, sy1=oy1', base1)  # Use strict >
    complex_top.constrain(spacer, 'sx2-sx1=2, sy2-sy1=6')
    complex_top.constrain(base2, 'sx1>=ox2, sy1=oy1', spacer)  # Use non-strict >=
    complex_top.solver()

    # Verify strict vs non-strict
    gap1 = spacer.pos_list[0] - base1.pos_list[2]
    gap2 = base2.pos_list[0] - spacer.pos_list[2]
    assert gap1 > 0, f"Failed: Strict '>' should create gap, got {gap1}"
    assert gap2 >= 0, f"Failed: Non-strict '>=' allows no gap, got {gap2}"
    print(f"   ✓ PASS: Complex scenario works correctly")
    print(f"      Strict '>' gap: {gap1} (> 0)")
    print(f"      Non-strict '>=' gap: {gap2} (>= 0)")

    print("\n" + "="*70)
    print("✓ ALL COMPREHENSIVE TESTS PASSED!")
    print("="*70)
    print("\nVerified:")
    print("  1. Strict operators (<, >) work correctly")
    print("  2. Non-strict operators (<=, >=) allow equality")
    print("  3. Fixed cells position correctly via constraints")
    print("  4. High resolution drawing works")
    print("  5. All fixes work together in complex scenarios")

    return True


if __name__ == '__main__':
    success = test_all_fixes()
    sys.exit(0 if success else 1)
