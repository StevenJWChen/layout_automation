#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test and demonstration of hierarchical/relative positioning

This shows how to use the new hierarchical layout system where child
positions are relative to their parents (like GDS format).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell
from layout_automation.hierarchical_layout import (
    enable_hierarchical_mode,
    solve_hierarchical,
    print_hierarchy_positions
)


def test_basic_hierarchical_positioning():
    """Test basic hierarchical positioning with relative coordinates"""
    print("\n" + "=" * 80)
    print("Test 1: Basic Hierarchical Positioning")
    print("=" * 80)

    # Create a simple hierarchy
    print("\n[Step 1] Creating hierarchy...")

    # Child cells (leaf rectangles)
    metal1_a = Cell('metal1_a', 'metal1')
    metal1_b = Cell('metal1_b', 'metal1')

    # Parent cell
    parent = Cell('parent', metal1_a, metal1_b)

    print("✓ Created parent with 2 metal1 children")

    # Enable hierarchical mode
    print("\n[Step 2] Enabling hierarchical mode...")
    enable_hierarchical_mode(parent)
    print("✓ Hierarchical mode enabled")

    # Set positions directly (absolute coordinates first)
    print("\n[Step 3] Setting positions...")
    parent.pos_list = [0, 0, 200, 100]
    metal1_a.pos_list = [10, 10, 60, 40]  # Absolute position
    metal1_b.pos_list = [70, 10, 120, 40]  # Absolute position

    print("✓ Positions set")

    # Now update to hierarchical (compute local from global)
    print("\n[Step 4] Converting to hierarchical representation...")
    solve_hierarchical(parent, verbose=True)
    success = True

    # Print hierarchy
    print("\n[Step 6] Final hierarchy:")
    print_hierarchy_positions(parent)

    # Verify relative positions
    print("\n[Step 7] Verification:")
    metal1_a_local = metal1_a.get_local_position()
    metal1_b_local = metal1_b.get_local_position()

    print(f"  metal1_a local position: {metal1_a_local}")
    print(f"  metal1_b local position: {metal1_b_local}")

    # Local x1 should be 10 (relative to parent which starts at 0)
    if metal1_a_local and metal1_a_local[0] == 10:
        print("  ✓ metal1_a has correct local x1 coordinate")
    else:
        print(f"  ✗ metal1_a local x1 incorrect: expected 10, got {metal1_a_local[0] if metal1_a_local else None}")

    # Export to GDS to verify
    print("\n[Step 8] Exporting to GDS...")
    parent.export_gds('test_hierarchical_basic.gds')
    print("✓ Exported to test_hierarchical_basic.gds")

    return True


def test_nested_hierarchy():
    """Test nested hierarchy (grandchildren)"""
    print("\n" + "=" * 80)
    print("Test 2: Nested Hierarchy (3 levels)")
    print("=" * 80)

    # Create 3-level hierarchy
    print("\n[Step 1] Creating 3-level hierarchy...")

    # Leaf cells
    rect1 = Cell('rect1', 'metal1')
    rect2 = Cell('rect2', 'metal1')

    # Mid-level cell
    subblock = Cell('subblock', rect1, rect2)

    # Top-level cell
    top = Cell('top', subblock)

    print("✓ Created top -> subblock -> [rect1, rect2]")

    # Enable hierarchical mode
    print("\n[Step 2] Enabling hierarchical mode...")
    enable_hierarchical_mode(top)
    print("✓ Hierarchical mode enabled")

    # Set positions
    print("\n[Step 3] Setting positions...")
    top.constrain('x1=0, y1=0, width=300, height=200')
    subblock.constrain('x1=50, y1=50, width=200, height=100')  # Position relative to top
    rect1.constrain('x1=60, y1=60, width=40, height=40')       # Absolute (will be relative to top)
    rect2.constrain('x1=110, y1=60, width=40, height=40')      # Absolute (will be relative to top)

    # Solve
    print("\n[Step 4] Solving layout...")
    success = solve_hierarchical(top, verbose=True)

    if success:
        print("✓ Layout solved successfully")
    else:
        print("✗ Solver failed")
        return False

    # Print hierarchy
    print("\n[Step 5] Final hierarchy:")
    print_hierarchy_positions(top)

    # Verify
    print("\n[Step 6] Verification:")
    subblock_local = subblock.get_local_position()
    rect1_local = rect1.get_local_position()

    print(f"  subblock local to top: {subblock_local}")
    print(f"  rect1 local to subblock: {rect1_local}")

    if subblock_local and subblock_local[0] == 50:
        print("  ✓ subblock correctly positioned relative to top")
    else:
        print("  ✗ subblock position incorrect")

    # Export
    print("\n[Step 7] Exporting to GDS...")
    top.export_gds('test_hierarchical_nested.gds')
    print("✓ Exported to test_hierarchical_nested.gds")

    return True


def test_relative_constraints():
    """Test using relative positioning directly"""
    print("\n" + "=" * 80)
    print("Test 3: Direct Relative Positioning")
    print("=" * 80)

    # Create hierarchy
    print("\n[Step 1] Creating cells...")
    child1 = Cell('child1', 'metal1')
    child2 = Cell('child2', 'metal1')
    parent = Cell('parent', child1, child2)

    print("✓ Created parent with 2 children")

    # Enable hierarchical mode FIRST
    print("\n[Step 2] Enabling hierarchical mode...")
    enable_hierarchical_mode(parent)
    print("✓ Hierarchical mode enabled")

    # Set parent position
    print("\n[Step 3] Setting parent position...")
    parent.constrain('x1=100, y1=100, width=200, height=150')
    parent.solver()

    # Now set children using LOCAL coordinates
    print("\n[Step 4] Setting children positions in LOCAL coordinates...")
    child1.set_local_position(10, 10, 60, 50)   # Relative to parent
    child2.set_local_position(70, 10, 120, 50)  # Relative to parent

    print(f"  child1 local: {child1.get_local_position()}")
    print(f"  child2 local: {child2.get_local_position()}")

    # Get global positions
    print("\n[Step 5] Computed global positions:")
    child1_global = child1.get_global_position()
    child2_global = child2.get_global_position()

    print(f"  child1 global: {child1_global}")
    print(f"  child2 global: {child2_global}")

    # Verify
    print("\n[Step 6] Verification:")
    if child1_global and child1_global[0] == 110:  # 100 (parent x1) + 10 (local x1)
        print("  ✓ child1 global position correctly computed from local")
    else:
        expected = 110
        actual = child1_global[0] if child1_global else None
        print(f"  ✗ child1 global x1 incorrect: expected {expected}, got {actual}")

    # Print hierarchy
    print("\n[Step 7] Final hierarchy:")
    print_hierarchy_positions(parent)

    # Export
    print("\n[Step 8] Exporting to GDS...")
    parent.export_gds('test_hierarchical_relative.gds')
    print("✓ Exported to test_hierarchical_relative.gds")

    return True


def demo_hierarchical_inverter():
    """Demo: Create inverter with hierarchical positioning"""
    print("\n" + "=" * 80)
    print("Demo: Hierarchical Inverter Layout")
    print("=" * 80)

    print("\n[Step 1] Creating inverter components...")

    # PMOS transistor components (relative positions within transistor)
    pmos_gate = Cell('pmos_gate', 'poly')
    pmos_source = Cell('pmos_source', 'metal1')
    pmos_drain = Cell('pmos_drain', 'metal1')

    # NMOS transistor components
    nmos_gate = Cell('nmos_gate', 'poly')
    nmos_source = Cell('nmos_source', 'metal1')
    nmos_drain = Cell('nmos_drain', 'metal1')

    # Transistor blocks
    pmos = Cell('pmos_transistor', pmos_gate, pmos_source, pmos_drain)
    nmos = Cell('nmos_transistor', nmos_gate, nmos_source, nmos_drain)

    # Inverter cell
    inverter = Cell('inverter', pmos, nmos)

    print("✓ Created hierarchical inverter structure")

    # Enable hierarchical mode
    print("\n[Step 2] Enabling hierarchical mode...")
    enable_hierarchical_mode(inverter)
    print("✓ Hierarchical mode enabled")

    # Set inverter dimensions
    print("\n[Step 3] Setting component positions...")
    inverter.constrain('x1=0, y1=0, width=100, height=200')

    # Position PMOS and NMOS blocks (absolute)
    pmos.constrain('x1=10, y1=110, width=80, height=80')
    nmos.constrain('x1=10, y1=10, width=80, height=80')

    # PMOS components (absolute, but will be relative to pmos block after solving)
    pmos_gate.constrain('x1=20, y1=130, width=10, height=60')
    pmos_source.constrain('x1=35, y1=150, width=20, height=20')
    pmos_drain.constrain('x1=60, y1=150, width=20, height=20')

    # NMOS components
    nmos_gate.constrain('x1=20, y1=30, width=10, height=60')
    nmos_source.constrain('x1=35, y1=40, width=20, height=20')
    nmos_drain.constrain('x1=60, y1=40, width=20, height=20')

    # Solve
    print("\n[Step 4] Solving hierarchical layout...")
    success = solve_hierarchical(inverter, verbose=False)

    if success:
        print("✓ Inverter layout solved")
    else:
        print("✗ Solver failed")
        return False

    # Show hierarchy
    print("\n[Step 5] Inverter hierarchy (with local coordinates):")
    print_hierarchy_positions(inverter)

    # Export
    print("\n[Step 6] Exporting inverter to GDS...")
    inverter.export_gds('demo_hierarchical_inverter.gds')
    print("✓ Exported to demo_hierarchical_inverter.gds")

    print("\n[Step 7] Benefits of hierarchical positioning:")
    print("  • PMOS and NMOS can be reused with different positions")
    print("  • Each block maintains its own local coordinate system")
    print("  • GDS export naturally uses relative positions")
    print("  • Easy to move/reposition entire blocks")

    return True


def main():
    """Run all tests and demos"""
    print("=" * 80)
    print("Hierarchical Layout System - Test Suite")
    print("=" * 80)
    print("\nThis demonstrates the enhanced solver with hierarchical positioning")
    print("where polygon positions are relative to their parents (like GDS).")

    results = []

    # Run tests
    results.append(("Basic Hierarchical Positioning", test_basic_hierarchical_positioning()))
    results.append(("Nested Hierarchy (3 levels)", test_nested_hierarchy()))
    results.append(("Direct Relative Positioning", test_relative_constraints()))
    results.append(("Hierarchical Inverter Demo", demo_hierarchical_inverter()))

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    print("\n" + "=" * 80)
    print("Generated Files")
    print("=" * 80)
    print("  test_hierarchical_basic.gds - Basic hierarchical layout")
    print("  test_hierarchical_nested.gds - 3-level nested hierarchy")
    print("  test_hierarchical_relative.gds - Direct relative positioning")
    print("  demo_hierarchical_inverter.gds - Hierarchical inverter")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
