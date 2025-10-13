#!/usr/bin/env python3
"""
Quick test script to verify OR-Tools solver integration in cell.py
"""

from layout_automation.cell import Cell

def test_basic_layout():
    """Test basic constraint solving with OR-Tools"""
    print("Testing basic OR-Tools solver integration...")

    # Create leaf cells (layer rectangles)
    m1 = Cell('m1', 'metal1')
    m2 = Cell('m2', 'metal1')
    m3 = Cell('m3', 'metal2')

    # Create container cell
    top = Cell('top', m1, m2, m3)

    # Add some constraints
    top.constrain(m1, 'x2-x1=20')  # Width = 20
    top.constrain(m1, 'y2-y1=15')  # Height = 15
    top.constrain(m1, 'x1=0, y1=0')  # Position at origin

    top.constrain(m2, 'x2-x1=25')
    top.constrain(m2, 'y2-y1=15')
    top.constrain(m2, 'sx1>ox2+5', m1)  # m2 is 5 units to the right of m1
    top.constrain(m2, 'sy1=oy1', m1)  # m2 aligned with m1 in Y

    top.constrain(m3, 'x2-x1=30')
    top.constrain(m3, 'y2-y1=20')
    top.constrain(m3, 'sx1=ox1', m1)  # m3 aligned with m1 in X
    top.constrain(m3, 'sy1>oy2+10', m1)  # m3 is 10 units above m1

    # Solve
    print("Running solver...")
    result = top.solver(fix_leaf_positions=False, integer_positions=True)

    if result:
        print("✓ Solver succeeded!")
        print(f"\nCell positions:")
        print(f"  m1: {m1.pos_list}")
        print(f"  m2: {m2.pos_list}")
        print(f"  m3: {m3.pos_list}")
        print(f"  top: {top.pos_list}")

        # Verify some constraints
        assert m1.pos_list[2] - m1.pos_list[0] == 20, "m1 width should be 20"
        assert m1.pos_list[3] - m1.pos_list[1] == 15, "m1 height should be 15"
        assert m2.pos_list[0] >= m1.pos_list[2] + 5, "m2 should be 5+ units to the right of m1"
        assert m3.pos_list[1] >= m1.pos_list[3] + 10, "m3 should be 10+ units above m1"

        print("\n✓ All constraint checks passed!")
        return True
    else:
        print("✗ Solver failed!")
        return False

if __name__ == '__main__':
    success = test_basic_layout()
    exit(0 if success else 1)
