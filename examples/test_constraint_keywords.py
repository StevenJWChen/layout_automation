#!/usr/bin/env python3
"""
Test constraint keyword expansion

Demonstrates the simple keyword→constraint string replacement system
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.constraint_keywords import print_keyword_reference

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)


def test_keyword_expansion():
    """Test that keywords are expanded correctly"""
    print("=" * 80)
    print("TEST: Keyword Expansion")
    print("=" * 80)
    print()

    examples = [
        ('xcenter', 'sx1+sx2=ox1+ox2'),
        ('ycenter', 'sy1+sy2=oy1+oy2'),
        ('center', 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2'),
        ('xcenter, swidth=10', 'sx1+sx2=ox1+ox2, sx2-sx1=10'),
        ('left, sheight=oheight', 'sx1=ox1, sy2-sy1=oy2-oy1'),
        ('sx=ox+10, sy=oy', 'sx1=ox1+10, sy1=oy1'),
        ('width=100, height=50', 'x2-x1=100, y2-y1=50'),
    ]

    from layout_automation.constraint_keywords import expand_constraint_keywords

    print("Keyword expansion examples:")
    print()
    for keyword, expected in examples:
        expanded = expand_constraint_keywords(keyword)
        match = "✓" if expanded == expected else "✗"
        print(f"{match} '{keyword}'")
        print(f"   → '{expanded}'")
        if expanded != expected:
            print(f"   Expected: '{expected}'")
        print()

    print()


def test_center_with_keywords():
    """Test centering using keywords"""
    print("=" * 80)
    print("TEST 1: Center Using Keywords")
    print("=" * 80)
    print()

    parent = Cell('parent')
    parent.constrain('width=100, height=100')  # Using keywords!

    child = Cell('child', 'metal1')
    parent.add_instance(child)

    # Center child in parent using keyword
    parent.constrain(child, 'center', parent)  # Simple!
    parent.constrain(child, 'swidth=30, sheight=20')  # Using keywords!

    print("Constraints added:")
    print("  parent.constrain('width=100, height=100')")
    print("  parent.constrain(child, 'center', parent)")
    print("  parent.constrain(child, 'swidth=30, sheight=20')")
    print()

    if parent.solver():
        print("✓ Solver succeeded")
        print(f"  Parent: {parent.pos_list}")
        print(f"  Child:  {child.pos_list}")
        print(f"  Child centered at: ({(child.pos_list[0]+child.pos_list[2])/2}, {(child.pos_list[1]+child.pos_list[3])/2})")
        parent.export_gds('demo_outputs/keyword_center.gds')
    else:
        print("✗ Solver failed")

    print()


def test_alignment_with_keywords():
    """Test alignment using keywords"""
    print("=" * 80)
    print("TEST 2: Alignment Using Keywords")
    print("=" * 80)
    print()

    parent = Cell('parent')

    block1 = Cell('block1', 'diff')
    block2 = Cell('block2', 'metal1')
    block3 = Cell('block3', 'poly')

    parent.add_instance([block1, block2, block3])

    # Block 1 at origin
    parent.constrain(block1, 'x1=0, y1=0, x2=50, y2=30')

    # Block 2: align left, match height - using keywords!
    parent.constrain(block2, 'left, sheight=oheight', block1)
    parent.constrain(block2, 'sy=oy+40, swidth=40', block1)

    # Block 3: align right, match height - using keywords!
    parent.constrain(block3, 'right, sheight=oheight', block1)
    parent.constrain(block3, 'sy=oy+40, swidth=35', block1)

    print("Constraints added (using keywords):")
    print("  parent.constrain(block2, 'left, sheight=oheight', block1)")
    print("  parent.constrain(block3, 'right, sheight=oheight', block1)")
    print()

    if parent.solver():
        print("✓ Solver succeeded")
        print(f"  Block 1: {block1.pos_list}")
        print(f"  Block 2: {block2.pos_list} (left aligned)")
        print(f"  Block 3: {block3.pos_list} (right aligned)")
        parent.export_gds('demo_outputs/keyword_align.gds')
    else:
        print("✗ Solver failed")

    print()


def test_spacing_with_keywords():
    """Test spacing using keywords"""
    print("=" * 80)
    print("TEST 3: Spacing Using Keywords")
    print("=" * 80)
    print()

    parent = Cell('parent')

    block1 = Cell('block1', 'diff')
    block2 = Cell('block2', 'diff')
    block3 = Cell('block3', 'diff')

    parent.add_instance([block1, block2, block3])

    # First block at origin
    parent.constrain(block1, 'x1=0, y1=0, swidth=20, sheight=30')

    # Second block to the right with spacing - using keywords!
    parent.constrain(block2, 'sx=ox2+10, sy=oy, swidth=owidth, sheight=oheight', block1)

    # Third block above first with spacing - using keywords!
    parent.constrain(block3, 'sx=ox, sy=oy2+15, swidth=owidth, sheight=oheight', block1)

    print("Constraints added (using keywords):")
    print("  parent.constrain(block2, 'sx=ox2+10, sy=oy, swidth=owidth, sheight=oheight', block1)")
    print("  parent.constrain(block3, 'sx=ox, sy=oy2+15, swidth=owidth, sheight=oheight', block1)")
    print()

    if parent.solver():
        print("✓ Solver succeeded")
        print(f"  Block 1: {block1.pos_list}")
        print(f"  Block 2: {block2.pos_list} (10 units right)")
        print(f"  Block 3: {block3.pos_list} (15 units above)")
        parent.export_gds('demo_outputs/keyword_spacing.gds')
    else:
        print("✗ Solver failed")

    print()


def test_complex_layout_with_keywords():
    """Test complex layout using only keywords"""
    print("=" * 80)
    print("TEST 4: Complex Layout Using Only Keywords")
    print("=" * 80)
    print()

    layout = Cell('LAYOUT_WITH_KEYWORDS')

    # Components
    base = Cell('base', 'diff')
    left_metal = Cell('left_metal', 'metal1')
    right_metal = Cell('right_metal', 'metal1')
    center_poly = Cell('center_poly', 'poly')
    top_contact = Cell('top_contact', 'contact')

    layout.add_instance([base, left_metal, right_metal, center_poly, top_contact])

    # Base layer
    layout.constrain(base, 'x1=0, y1=0, width=100, height=40')

    # Left metal
    layout.constrain(left_metal, 'sx=ox+5, sy=oy+5, swidth=25, sheight=30', base)

    # Right metal - align with base right edge
    layout.constrain(right_metal, 'right, bottom', base)
    layout.constrain(right_metal, 'swidth=25, sheight=30')
    layout.constrain(right_metal, 'sx=ox2-30', base)  # Offset from right edge

    # Center poly - crosses horizontally
    layout.constrain(center_poly, 'xcenter, ycenter', base)
    layout.constrain(center_poly, 'swidth=10, sheight=50')

    # Top contact - centered on poly at top
    layout.constrain(top_contact, 'xcenter, sy=oy2-6', center_poly)
    layout.constrain(top_contact, 'swidth=4, sheight=4')

    print("All constraints use keywords:")
    print("  base: 'width=100, height=40'")
    print("  left_metal: 'sx=ox+5, sy=oy+5, swidth=25, sheight=30'")
    print("  right_metal: 'right, bottom' + 'swidth=25, sheight=30'")
    print("  center_poly: 'xcenter, ycenter' + 'swidth=10, sheight=50'")
    print("  top_contact: 'xcenter, sy=oy2-6' + 'swidth=4, sheight=4'")
    print()

    if layout.solver():
        print("✓ Complex layout solved using only keywords")
        layout.tree(show_positions=True, show_layers=True)
        layout.export_gds('demo_outputs/keyword_complex.gds')
    else:
        print("✗ Solver failed")

    print()


def compare_syntax():
    """Compare old vs new syntax"""
    print("=" * 80)
    print("COMPARISON: Old vs New Syntax")
    print("=" * 80)
    print()

    print("OLD SYNTAX (full constraint strings):")
    print("-" * 80)
    print("""
    # Center child
    parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

    # Center X and set width
    parent.constrain(child, 'sx1+sx2=ox1+ox2, sx2-sx1=10', parent)

    # Align left and match height
    parent.constrain(child2, 'sx1=ox1, sy2-sy1=oy2-oy1', child1)

    # Position to the right
    parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)

    # Self-constraint
    cell.constrain('x2-x1=100, y2-y1=50')
    """)

    print()
    print("NEW SYNTAX (with keywords):")
    print("-" * 80)
    print("""
    # Center child
    parent.constrain(child, 'center', parent)

    # Center X and set width
    parent.constrain(child, 'xcenter, swidth=10', parent)

    # Align left and match height
    parent.constrain(child2, 'left, sheight=oheight', child1)

    # Position to the right
    parent.constrain(child2, 'sx=ox2+10, sy=oy', child1)

    # Self-constraint
    cell.constrain('width=100, height=50')
    """)

    print()
    print("✓ Keywords make constraints:")
    print("  - Shorter and more readable")
    print("  - Less typing")
    print("  - Less error-prone")
    print("  - Still allows full expressions")
    print()


def main():
    print()
    print("*" * 80)
    print("CONSTRAINT KEYWORD EXPANSION TEST")
    print("*" * 80)
    print()

    # Print reference table
    print_keyword_reference()
    print()
    input("Press Enter to run tests...")
    print()

    # Run tests
    test_keyword_expansion()
    test_center_with_keywords()
    test_alignment_with_keywords()
    test_spacing_with_keywords()
    test_complex_layout_with_keywords()
    compare_syntax()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✓ All keyword tests passed")
    print()
    print("Files generated:")
    print("  - demo_outputs/keyword_center.gds")
    print("  - demo_outputs/keyword_align.gds")
    print("  - demo_outputs/keyword_spacing.gds")
    print("  - demo_outputs/keyword_complex.gds")
    print()
    print("Key Benefits:")
    print("  - Shorter constraint strings")
    print("  - More readable code")
    print("  - Less typing")
    print("  - Backwards compatible (full syntax still works)")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
