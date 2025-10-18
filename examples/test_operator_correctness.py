"""
Test that all constraint operators work correctly

This verifies that <, <=, >, >=, and = are correctly applied by the solver.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell


def test_operators():
    """Test all constraint operators"""
    print("="*70)
    print("TEST: Constraint Operator Correctness")
    print("="*70)

    # Test 1: >= operator
    print("\n1. Test '>=' operator (x1 >= 10)")
    c1 = Cell('test_gte')
    r1 = Cell('r1', 'metal1')
    c1.add_instance(r1)
    c1.constrain(r1, 'x1>=10, x2-x1=5, y2-y1=5')
    c1.solver()
    print(f"   Result: x1 = {r1.pos_list[0]}")
    assert r1.pos_list[0] >= 10, f"Failed: {r1.pos_list[0]} is not >= 10"
    print("   ✓ PASS: x1 >= 10")

    # Test 2: > operator (strict inequality)
    print("\n2. Test '>' operator (x1 > 10)")
    c2 = Cell('test_gt')
    r2 = Cell('r2', 'metal1')
    c2.add_instance(r2)
    c2.constrain(r2, 'x1>10, x2-x1=5, y2-y1=5')
    c2.solver()
    print(f"   Result: x1 = {r2.pos_list[0]}")
    assert r2.pos_list[0] > 10, f"Failed: {r2.pos_list[0]} is not > 10"
    assert r2.pos_list[0] != 10, f"Failed: x1 should be strictly greater than 10"
    print("   ✓ PASS: x1 > 10 (strictly)")

    # Test 3: <= operator
    print("\n3. Test '<=' operator (x1 <= 10)")
    c3 = Cell('test_lte')
    r3 = Cell('r3', 'metal1')
    c3.add_instance(r3)
    c3.constrain(r3, 'x1<=10, x1>=0, x2-x1=5, y2-y1=5')
    c3.solver()
    print(f"   Result: x1 = {r3.pos_list[0]}")
    assert r3.pos_list[0] <= 10, f"Failed: {r3.pos_list[0]} is not <= 10"
    print("   ✓ PASS: x1 <= 10")

    # Test 4: < operator (strict inequality)
    print("\n4. Test '<' operator (x1 < 10)")
    c4 = Cell('test_lt')
    r4 = Cell('r4', 'metal1')
    c4.add_instance(r4)
    c4.constrain(r4, 'x1<10, x1>=0, x2-x1=5, y2-y1=5')
    c4.solver()
    print(f"   Result: x1 = {r4.pos_list[0]}")
    assert r4.pos_list[0] < 10, f"Failed: {r4.pos_list[0]} is not < 10"
    assert r4.pos_list[0] != 10, f"Failed: x1 should be strictly less than 10"
    print("   ✓ PASS: x1 < 10 (strictly)")

    # Test 5: = operator
    print("\n5. Test '=' operator (x1 = 25)")
    c5 = Cell('test_eq')
    r5 = Cell('r5', 'metal1')
    c5.add_instance(r5)
    c5.constrain(r5, 'x1=25, x2-x1=5, y2-y1=5')
    c5.solver()
    print(f"   Result: x1 = {r5.pos_list[0]}")
    assert r5.pos_list[0] == 25, f"Failed: {r5.pos_list[0]} is not == 25"
    print("   ✓ PASS: x1 = 25")

    # Test 6: Complex constraints with different operators
    print("\n6. Test mixed operators (5 < x1 <= 15)")
    c6 = Cell('test_mixed')
    r6 = Cell('r6', 'metal1')
    c6.add_instance(r6)
    c6.constrain(r6, 'x1>5, x1<=15, x2-x1=5, y2-y1=5')
    c6.solver()
    print(f"   Result: x1 = {r6.pos_list[0]}")
    assert r6.pos_list[0] > 5 and r6.pos_list[0] <= 15, \
        f"Failed: {r6.pos_list[0]} is not in range (5, 15]"
    print(f"   ✓ PASS: 5 < x1 <= 15")

    # Test 7: Verify strict vs non-strict at boundary
    print("\n7. Test boundary difference (>= vs >)")
    c7a = Cell('test_boundary_gte')
    r7a = Cell('r7a', 'metal1')
    c7a.add_instance(r7a)
    c7a.constrain(r7a, 'x1>=20, x1<=20, x2-x1=5, y2-y1=5')  # Forces x1=20
    c7a.solver()
    print(f"   With '>=': x1 = {r7a.pos_list[0]} (should be 20)")
    assert r7a.pos_list[0] == 20, "Failed: >= should allow equality"

    c7b = Cell('test_boundary_gt')
    r7b = Cell('r7b', 'metal1')
    c7b.add_instance(r7b)
    c7b.constrain(r7b, 'x1>19, x1<=20, x2-x1=5, y2-y1=5')  # x1 in (19, 20]
    c7b.solver()
    print(f"   With '>':  x1 = {r7b.pos_list[0]} (should be 20)")
    assert r7b.pos_list[0] > 19 and r7b.pos_list[0] <= 20, "Failed: > should be strict"
    print("   ✓ PASS: Boundary conditions correct")

    print("\n" + "="*70)
    print("✓ ALL OPERATOR TESTS PASSED!")
    print("="*70)
    print("\nSummary:")
    print("  - '<'  enforces strict less than")
    print("  - '<=' allows equality")
    print("  - '>'  enforces strict greater than")
    print("  - '>=' allows equality")
    print("  - '='  enforces exact equality")

    return True


if __name__ == '__main__':
    success = test_operators()
    sys.exit(0 if success else 1)
