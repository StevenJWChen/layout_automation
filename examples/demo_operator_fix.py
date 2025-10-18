"""
Demonstration of the operator fix

This shows the difference between strict (< and >) and non-strict (<= and >=) operators.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
import matplotlib.pyplot as plt


def demo_operator_fix():
    """Demonstrate that strict inequalities work correctly"""

    print("="*70)
    print("DEMONSTRATION: Strict vs Non-Strict Inequality Operators")
    print("="*70)

    # Create two cells with different constraints
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

    # Cell 1: Using >= (non-strict)
    print("\n1. Using '>=' (non-strict): x1 >= 10")
    cell1 = Cell('cell1')
    r1a = Cell('r1a', 'metal1')
    r1b = Cell('r1b', 'poly')
    cell1.add_instance([r1a, r1b])
    cell1.constrain(r1a, 'x1>=10, x2-x1=8, y2-y1=8')
    cell1.constrain(r1b, 'sx1=ox2+2, sy1=oy1, sx2-sx1=8, sy2-sy1=8', r1a)
    cell1.constrain(r1a, 'sx1=x1, sy1=y1')
    cell1.draw(ax=ax1, show=False)
    ax1.set_title('Using ">=" (allows x1=10)', fontsize=14, fontweight='bold')
    ax1.axvline(x=10, color='red', linestyle='--', linewidth=2, label='x=10 boundary')
    ax1.legend()
    print(f"   r1a position: x1 = {r1a.pos_list[0]}")
    print(f"   ✓ x1 = 10 is ALLOWED with '>='")

    # Cell 2: Using > (strict)
    print("\n2. Using '>' (strict): x1 > 10")
    cell2 = Cell('cell2')
    r2a = Cell('r2a', 'metal1')
    r2b = Cell('r2b', 'poly')
    cell2.add_instance([r2a, r2b])
    cell2.constrain(r2a, 'x1>10, x2-x1=8, y2-y1=8')
    cell2.constrain(r2b, 'sx1=ox2+2, sy1=oy1, sx2-sx1=8, sy2-sy1=8', r2a)
    cell2.constrain(r2a, 'sx1=x1, sy1=y1')
    cell2.draw(ax=ax2, show=False)
    ax2.set_title('Using ">" (forces x1>10)', fontsize=14, fontweight='bold')
    ax2.axvline(x=10, color='red', linestyle='--', linewidth=2, label='x=10 boundary')
    ax2.legend()
    print(f"   r2a position: x1 = {r2a.pos_list[0]}")
    print(f"   ✓ x1 = 11 (must be STRICTLY greater than 10)")

    plt.suptitle('Operator Fix Demonstration: Strict vs Non-Strict Inequalities',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig('demo_outputs/operator_fix_demo.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved demonstration to demo_outputs/operator_fix_demo.png")
    plt.close()

    print("\n" + "="*70)
    print("SUMMARY:")
    print("  - With '>=': x1 = 10 (equality allowed)")
    print("  - With '>':  x1 = 11 (strictly greater, no equality)")
    print("="*70)


if __name__ == '__main__':
    demo_operator_fix()
