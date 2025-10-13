#!/usr/bin/env python3
"""
Comprehensive test of OR-Tools solver in cell.py
Tests various constraint types and hierarchical layouts
"""

from layout_automation.cell import Cell

def test_1_basic_constraints():
    """Test 1: Basic positioning with fixed dimensions"""
    print("\n" + "="*60)
    print("TEST 1: Basic Constraints")
    print("="*60)

    m1 = Cell('m1', 'metal1')
    m2 = Cell('m2', 'metal1')
    m3 = Cell('m3', 'metal2')

    top = Cell('top', m1, m2, m3)

    # Fixed dimensions
    top.constrain(m1, 'x2-x1=20, y2-y1=15, x1=0, y1=0')
    top.constrain(m2, 'x2-x1=25, y2-y1=15')
    top.constrain(m3, 'x2-x1=30, y2-y1=20')

    # Relative positioning
    top.constrain(m2, 'sx1>ox2+5, sy1=oy1', m1)
    top.constrain(m3, 'sx1=ox1, sy1>oy2+10', m1)

    result = top.solver(fix_leaf_positions=False)

    if result:
        print("✓ Solver succeeded!")
        print(f"  m1: {m1.pos_list} (width={m1.pos_list[2]-m1.pos_list[0]}, height={m1.pos_list[3]-m1.pos_list[1]})")
        print(f"  m2: {m2.pos_list} (width={m2.pos_list[2]-m2.pos_list[0]}, height={m2.pos_list[3]-m2.pos_list[1]})")
        print(f"  m3: {m3.pos_list} (width={m3.pos_list[2]-m3.pos_list[0]}, height={m3.pos_list[3]-m3.pos_list[1]})")
        print(f"  top: {top.pos_list}")

        # Verify constraints
        assert m1.pos_list[2] - m1.pos_list[0] == 20, "m1 width should be 20"
        assert m2.pos_list[0] >= m1.pos_list[2] + 5, "m2 should be 5+ units right of m1"
        assert m3.pos_list[1] >= m1.pos_list[3] + 10, "m3 should be 10+ units above m1"
        print("✓ All constraints verified!")
        return True
    else:
        print("✗ Solver failed!")
        return False

def test_2_hierarchical_layout():
    """Test 2: Hierarchical cell layout"""
    print("\n" + "="*60)
    print("TEST 2: Hierarchical Layout")
    print("="*60)

    # Create leaf cells
    poly1 = Cell('poly1', 'poly')
    diff1 = Cell('diff1', 'diff')
    poly2 = Cell('poly2', 'poly')
    diff2 = Cell('diff2', 'diff')

    # Create sub-cells (transistors)
    transistor1 = Cell('transistor1', poly1, diff1)
    transistor2 = Cell('transistor2', poly2, diff2)

    # Create top cell
    circuit = Cell('circuit', transistor1, transistor2)

    # Constraints within transistor1 - poly and diff positioned relative to each other
    transistor1.constrain(poly1, 'x2-x1=10, y2-y1=50')
    transistor1.constrain(diff1, 'x2-x1=30, y2-y1=20')
    transistor1.constrain(diff1, 'sy1=oy1+15, sx1=ox1', poly1)  # diff centered on poly

    # Constraints within transistor2 - same as transistor1
    transistor2.constrain(poly2, 'x2-x1=10, y2-y1=50')
    transistor2.constrain(diff2, 'x2-x1=30, y2-y1=20')
    transistor2.constrain(diff2, 'sy1=oy1+15, sx1=ox1', poly2)  # diff centered on poly

    # Position transistors relative to each other in circuit
    circuit.constrain(transistor2, 'sx1>=ox2+20', transistor1)  # Space between transistors
    circuit.constrain(transistor2, 'sy1=oy1', transistor1)  # Aligned vertically

    result = circuit.solver(fix_leaf_positions=False)

    if result:
        print("✓ Solver succeeded!")
        print(f"  transistor1: {transistor1.pos_list}")
        print(f"    - poly1: {poly1.pos_list}")
        print(f"    - diff1: {diff1.pos_list}")
        print(f"  transistor2: {transistor2.pos_list}")
        print(f"    - poly2: {poly2.pos_list}")
        print(f"    - diff2: {diff2.pos_list}")
        print(f"  circuit: {circuit.pos_list}")

        # Verify hierarchy
        assert transistor1.pos_list[0] <= poly1.pos_list[0], "Parent should encompass child (x1)"
        assert transistor1.pos_list[2] >= poly1.pos_list[2], "Parent should encompass child (x2)"
        assert transistor2.pos_list[0] >= transistor1.pos_list[2] + 20, "transistor2 should be 20+ units right"
        print("✓ All constraints verified!")
        return True
    else:
        print("✗ Solver failed!")
        return False

def test_3_alignment_constraints():
    """Test 3: Alignment constraints"""
    print("\n" + "="*60)
    print("TEST 3: Alignment Constraints")
    print("="*60)

    # Create cells to align
    r1 = Cell('r1', 'metal1')
    r2 = Cell('r2', 'metal1')
    r3 = Cell('r3', 'metal1')

    layout = Cell('layout', r1, r2, r3)

    # All have same width but different heights
    layout.constrain(r1, 'x2-x1=40, y2-y1=20, x1=0, y1=0')
    layout.constrain(r2, 'x2-x1=40, y2-y1=30')
    layout.constrain(r3, 'x2-x1=40, y2-y1=25')

    # Stack vertically with spacing, aligned on left edge
    layout.constrain(r2, 'sx1=ox1, sy1=oy2+5', r1)
    layout.constrain(r3, 'sx1=ox1, sy1=oy2+5', r2)

    result = layout.solver(fix_leaf_positions=False)

    if result:
        print("✓ Solver succeeded!")
        print(f"  r1: {r1.pos_list}")
        print(f"  r2: {r2.pos_list}")
        print(f"  r3: {r3.pos_list}")
        print(f"  layout: {layout.pos_list}")

        # Verify alignment
        assert r1.pos_list[0] == r2.pos_list[0] == r3.pos_list[0], "All should be left-aligned"
        assert r2.pos_list[1] == r1.pos_list[3] + 5, "r2 should be 5 units above r1"
        assert r3.pos_list[1] == r2.pos_list[3] + 5, "r3 should be 5 units above r2"
        print("✓ All constraints verified!")
        return True
    else:
        print("✗ Solver failed!")
        return False

def test_4_inequality_constraints():
    """Test 4: Inequality constraints (>=, <=)"""
    print("\n" + "="*60)
    print("TEST 4: Inequality Constraints")
    print("="*60)

    a = Cell('a', 'metal1')
    b = Cell('b', 'metal2')

    top = Cell('top', a, b)

    # a has minimum dimensions
    top.constrain(a, 'x2-x1>=20, y2-y1>=15, x1=0, y1=0')

    # b must be at least as wide as a, positioned to the right
    top.constrain(b, 'sx2-sx1>=ox2-ox1', a)  # b.width >= a.width
    top.constrain(b, 'sy2-sy1=10')  # b has fixed height
    top.constrain(b, 'sx1>=ox2+3', a)  # b is at least 3 units right of a
    top.constrain(b, 'sy1=oy1', a)  # b aligned with a vertically

    result = top.solver(fix_leaf_positions=False)

    if result:
        print("✓ Solver succeeded!")
        a_width = a.pos_list[2] - a.pos_list[0]
        a_height = a.pos_list[3] - a.pos_list[1]
        b_width = b.pos_list[2] - b.pos_list[0]
        b_height = b.pos_list[3] - b.pos_list[1]

        print(f"  a: {a.pos_list} (w={a_width}, h={a_height})")
        print(f"  b: {b.pos_list} (w={b_width}, h={b_height})")
        print(f"  top: {top.pos_list}")

        # Verify constraints
        assert a_width >= 20, "a width should be >= 20"
        assert a_height >= 15, "a height should be >= 15"
        assert b_width >= a_width, "b width should be >= a width"
        assert b.pos_list[0] >= a.pos_list[2] + 3, "b should be >= 3 units right of a"
        print("✓ All constraints verified!")
        return True
    else:
        print("✗ Solver failed!")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OR-TOOLS COMPREHENSIVE VALIDATION TEST SUITE")
    print("="*60)

    results = []
    results.append(("Basic Constraints", test_1_basic_constraints()))
    results.append(("Hierarchical Layout", test_2_hierarchical_layout()))
    results.append(("Alignment Constraints", test_3_alignment_constraints()))
    results.append(("Inequality Constraints", test_4_inequality_constraints()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "PASS ✓" if passed else "FAIL ✗"
        print(f"{name:.<40} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! OR-Tools solver is working perfectly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    exit(main())
