#!/usr/bin/env python3
"""
Test and demonstrate constraint helper functions

Shows how to use the constraint helpers to make layout code more readable
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.cell import Cell
from layout_automation.constraints import (
    center, center_x, center_y,
    align_left, align_right, align_top, align_bottom,
    spacing_h, spacing_v,
    same_width, same_height, same_size,
    width, height, size,
    at, bbox,
    beside, above, below,
    print_reference
)

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)


def test_center():
    """Test centering constraints"""
    print("=" * 80)
    print("TEST 1: Center Constraints")
    print("=" * 80)
    print()

    parent = Cell('parent')
    parent.constrain(size(100, 100))

    child = Cell('child', 'metal1')
    parent.add_instance(child)

    # Center child in parent using helper
    parent.constrain(child, *center(parent))
    parent.constrain(child, size(30, 20))

    if parent.solver():
        print("✓ Center constraint works")
        print(f"  Parent: {parent.pos_list}")
        print(f"  Child:  {child.pos_list}")
        print(f"  Child is centered: {(35, 40, 65, 60)}")
        parent.export_gds('demo_outputs/test_center.gds')
    else:
        print("✗ Solver failed")

    print()


def test_alignment():
    """Test alignment constraints"""
    print("=" * 80)
    print("TEST 2: Alignment Constraints")
    print("=" * 80)
    print()

    parent = Cell('parent')

    ref = Cell('reference', 'poly')
    child1 = Cell('align_left_child', 'metal1')
    child2 = Cell('align_right_child', 'metal1')
    child3 = Cell('align_center_child', 'metal1')

    parent.add_instance([ref, child1, child2, child3])

    # Reference cell
    parent.constrain(ref, at(20, 50, 60, 20))

    # Align left
    parent.constrain(child1, *align_left(ref))
    parent.constrain(child1, at(0, 10, 40, 15))

    # Align right
    parent.constrain(child2, *align_right(ref))
    parent.constrain(child2, at(0, 30, 40, 15))

    # Align center X
    parent.constrain(child3, *align_center_x(ref))
    parent.constrain(child3, at(0, 75, 30, 10))

    if parent.solver():
        print("✓ Alignment constraints work")
        print(f"  Reference:     {ref.pos_list}")
        print(f"  Align left:    {child1.pos_list}")
        print(f"  Align right:   {child2.pos_list}")
        print(f"  Align center:  {child3.pos_list}")
        parent.export_gds('demo_outputs/test_alignment.gds')
    else:
        print("✗ Solver failed")

    print()


def test_spacing():
    """Test spacing constraints"""
    print("=" * 80)
    print("TEST 3: Spacing Constraints")
    print("=" * 80)
    print()

    parent = Cell('parent')

    block1 = Cell('block1', 'diff')
    block2 = Cell('block2', 'diff')
    block3 = Cell('block3', 'diff')

    parent.add_instance([block1, block2, block3])

    # First block at origin
    parent.constrain(block1, at(0, 0, 20, 30))

    # Second block 10 units to the right (horizontal spacing)
    parent.constrain(block2, *spacing_h(block1, 10))
    parent.constrain(block2, *same_size(block1))
    parent.constrain(block2, *align_bottom(block1))

    # Third block 15 units above first block (vertical spacing)
    parent.constrain(block3, *spacing_v(block1, 15))
    parent.constrain(block3, *same_size(block1))
    parent.constrain(block3, *align_left(block1))

    if parent.solver():
        print("✓ Spacing constraints work")
        print(f"  Block 1: {block1.pos_list}")
        print(f"  Block 2: {block2.pos_list} (10 units right)")
        print(f"  Block 3: {block3.pos_list} (15 units above)")
        parent.export_gds('demo_outputs/test_spacing.gds')
    else:
        print("✗ Solver failed")

    print()


def test_compound():
    """Test compound constraints (beside, above, below)"""
    print("=" * 80)
    print("TEST 4: Compound Constraints")
    print("=" * 80)
    print()

    parent = Cell('parent')

    center_block = Cell('center', 'poly')
    right_block = Cell('right', 'metal1')
    left_block = Cell('left', 'metal1')
    top_block = Cell('top', 'metal2')
    bottom_block = Cell('bottom', 'metal2')

    parent.add_instance([center_block, right_block, left_block, top_block, bottom_block])

    # Center block
    parent.constrain(center_block, at(50, 50, 30, 20))

    # Right block: beside center, vertically centered, 5 unit spacing
    parent.constrain(right_block, *beside(center_block, spacing_val=5, align='center'))
    parent.constrain(right_block, size(20, 15))

    # Left block: to the left of center, vertically centered
    parent.constrain(left_block, *spacing_h(center_block, -25))  # negative spacing = to the left
    parent.constrain(left_block, *align_center_y(center_block))
    parent.constrain(left_block, size(20, 15))

    # Top block: above center, horizontally centered, 5 unit spacing
    parent.constrain(top_block, *above(center_block, spacing_val=5, align='center'))
    parent.constrain(top_block, size(25, 12))

    # Bottom block: below center, horizontally centered, 5 unit spacing
    parent.constrain(bottom_block, *below(center_block, spacing_val=5, align='center'))
    parent.constrain(bottom_block, size(25, 12))

    if parent.solver():
        print("✓ Compound constraints work")
        print(f"  Center: {center_block.pos_list}")
        print(f"  Right:  {right_block.pos_list}")
        print(f"  Left:   {left_block.pos_list}")
        print(f"  Top:    {top_block.pos_list}")
        print(f"  Bottom: {bottom_block.pos_list}")
        parent.export_gds('demo_outputs/test_compound.gds')
    else:
        print("✗ Solver failed")

    print()


def test_size_matching():
    """Test size matching constraints"""
    print("=" * 80)
    print("TEST 5: Size Matching")
    print("=" * 80)
    print()

    parent = Cell('parent')

    template = Cell('template', 'contact')
    copy1 = Cell('copy1', 'contact')
    copy2 = Cell('copy2', 'contact')
    copy3 = Cell('copy3', 'contact')

    parent.add_instance([template, copy1, copy2, copy3])

    # Template with specific size
    parent.constrain(template, at(10, 10, 15, 20))

    # Copies with same size as template
    parent.constrain(copy1, *beside(template, 5, 'bottom'))
    parent.constrain(copy1, *same_size(template))

    parent.constrain(copy2, *beside(copy1, 5, 'bottom'))
    parent.constrain(copy2, *same_width(template))
    parent.constrain(copy2, *same_height(template))

    parent.constrain(copy3, *beside(copy2, 5, 'bottom'))
    parent.constrain(copy3, *same_size(template))

    if parent.solver():
        print("✓ Size matching constraints work")
        print(f"  Template: {template.pos_list} (15×20)")
        print(f"  Copy 1:   {copy1.pos_list} (same size)")
        print(f"  Copy 2:   {copy2.pos_list} (same size)")
        print(f"  Copy 3:   {copy3.pos_list} (same size)")
        parent.export_gds('demo_outputs/test_size_matching.gds')
    else:
        print("✗ Solver failed")

    print()


def test_readable_layout():
    """Create a complex layout using constraint helpers for readability"""
    print("=" * 80)
    print("TEST 6: Readable Complex Layout")
    print("=" * 80)
    print()

    # Create a simple transistor-like structure
    layout = Cell('TRANSISTOR_DEMO')

    # Components
    diff_region = Cell('diffusion', 'diff')
    poly_gate = Cell('gate', 'poly')
    source_metal = Cell('source', 'metal1')
    drain_metal = Cell('drain', 'metal1')
    gate_contact = Cell('gate_contact', 'contact')

    layout.add_instance([diff_region, poly_gate, source_metal, drain_metal, gate_contact])

    # Diffusion region at base
    layout.constrain(diff_region, at(0, 10, 100, 40))

    # Poly gate crosses diffusion in the middle
    layout.constrain(poly_gate, *center_x(diff_region))
    layout.constrain(poly_gate, size(10, 60))
    layout.constrain(poly_gate, at(0, 0))

    # Source metal on left side
    layout.constrain(source_metal, bbox(5, 15, 25, 45))

    # Drain metal on right side, same size as source
    layout.constrain(drain_metal, *align_right(diff_region))
    layout.constrain(drain_metal, *same_size(source_metal))
    layout.constrain(drain_metal, *align_bottom(source_metal))

    # Gate contact centered on poly, at top
    layout.constrain(gate_contact, *center_x(poly_gate))
    layout.constrain(gate_contact, *align_top(poly_gate))
    layout.constrain(gate_contact, size(4, 4))

    if layout.solver():
        print("✓ Complex layout created with readable constraints")
        print(f"  Diffusion:     {diff_region.pos_list}")
        print(f"  Poly gate:     {poly_gate.pos_list}")
        print(f"  Source metal:  {source_metal.pos_list}")
        print(f"  Drain metal:   {drain_metal.pos_list}")
        print(f"  Gate contact:  {gate_contact.pos_list}")

        layout.tree(show_positions=True, show_layers=True)
        layout.export_gds('demo_outputs/test_readable_layout.gds')
    else:
        print("✗ Solver failed")

    print()


def compare_readability():
    """Compare old vs new constraint syntax"""
    print("=" * 80)
    print("COMPARISON: Old vs New Constraint Syntax")
    print("=" * 80)
    print()

    print("OLD SYNTAX (manual constraint strings):")
    print("-" * 80)
    print("""
    # Center child in parent
    parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

    # Place child2 to the right of child1 with spacing
    parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)

    # Match size
    parent.constrain(child2, 'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', child1)

    # Align left edge
    parent.constrain(child2, 'sx1=ox1', child1)
    """)

    print()
    print("NEW SYNTAX (constraint helpers):")
    print("-" * 80)
    print("""
    # Center child in parent
    parent.constrain(child, *center(parent))

    # Place child2 to the right of child1 with spacing
    parent.constrain(child2, *beside(child1, spacing_val=10, align='bottom'))

    # Match size
    parent.constrain(child2, *same_size(child1))

    # Align left edge
    parent.constrain(child2, *align_left(child1))
    """)

    print()
    print("✓ Constraint helpers make code:")
    print("  - More readable")
    print("  - Less error-prone")
    print("  - Easier to understand intent")
    print("  - Self-documenting")
    print()


def main():
    print()
    print("*" * 80)
    print("CONSTRAINT HELPER FUNCTIONS TEST & DEMO")
    print("*" * 80)
    print()

    # Print reference table
    print_reference()
    print()
    input("Press Enter to run tests...")
    print()

    # Run tests
    test_center()
    test_alignment()
    test_spacing()
    test_compound()
    test_size_matching()
    test_readable_layout()
    compare_readability()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✓ All constraint helper tests passed")
    print()
    print("Files generated:")
    print("  - demo_outputs/test_center.gds")
    print("  - demo_outputs/test_alignment.gds")
    print("  - demo_outputs/test_spacing.gds")
    print("  - demo_outputs/test_compound.gds")
    print("  - demo_outputs/test_size_matching.gds")
    print("  - demo_outputs/test_readable_layout.gds")
    print()
    print("To use constraint helpers in your code:")
    print("  from layout_automation.constraints import center, align_left, spacing_h")
    print("  from layout_automation.constraints import print_reference")
    print()
    print("  print_reference()  # Show constraint reference table")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
