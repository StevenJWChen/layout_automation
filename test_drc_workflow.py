#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test for DRC workflow

This test creates a layout with intentional DRC violations,
then runs the DRC workflow to detect and fix them.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile
from layout_automation.drc_checker import DRCChecker
from layout_automation.drc_fixer import DRCFixer


def create_test_layout_with_violations():
    """
    Create a test layout with intentional DRC violations

    According to FreePDK45.tf:
    - metal1 minWidth: 0.065
    - metal1 minSpacing: 0.065
    - poly minWidth: 0.05
    - poly minSpacing: 0.075
    """
    print("Creating test layout with intentional DRC violations...")

    # Violation 1: Metal1 rectangle with width < 0.065 (too narrow)
    metal1_narrow = Cell('metal1_narrow', 'metal1')
    metal1_narrow.pos_list = [0, 0, 0.04, 0.5]  # Width 0.04 < 0.065 (VIOLATION)

    # Violation 2: Metal1 rectangle with correct width
    metal1_ok = Cell('metal1_ok', 'metal1')
    metal1_ok.pos_list = [0, 1.0, 0.2, 1.2]  # OK

    # Violation 3: Two metal1 rectangles too close (spacing violation)
    metal1_left = Cell('metal1_left', 'metal1')
    metal1_left.pos_list = [1.0, 0, 1.1, 0.3]  # OK width

    metal1_right = Cell('metal1_right', 'metal1')
    metal1_right.pos_list = [1.15, 0, 1.25, 0.3]  # Spacing = 0.05 < 0.065 (VIOLATION)

    # Violation 4: Poly with width < 0.05 (too narrow)
    poly_narrow = Cell('poly_narrow', 'poly')
    poly_narrow.pos_list = [2.0, 0, 2.03, 0.5]  # Width 0.03 < 0.05 (VIOLATION)

    # Violation 5: Two poly rectangles too close
    poly_bottom = Cell('poly_bottom', 'poly')
    poly_bottom.pos_list = [3.0, 0, 3.1, 0.1]  # OK width

    poly_top = Cell('poly_top', 'poly')
    poly_top.pos_list = [3.0, 0.15, 3.1, 0.25]  # Spacing = 0.05 < 0.075 (VIOLATION)

    # Create parent cell with all violating elements
    parent = Cell('test_layout_violations',
                  metal1_narrow, metal1_ok,
                  metal1_left, metal1_right,
                  poly_narrow, poly_bottom, poly_top)

    parent.pos_list = [0, 0, 4, 2]

    print("✓ Test layout created with fixed positions")

    return parent


def test_drc_workflow_complete():
    """Test the complete DRC workflow"""
    print("\n" + "=" * 80)
    print("DRC Workflow Complete Test")
    print("=" * 80)

    # Step 1: Create test layout with violations
    print("\n[Step 1] Creating test layout with violations...")
    cell = create_test_layout_with_violations()

    # Step 2: Export to GDS
    print("\n[Step 2] Exporting test layout to GDS...")
    gds_file = 'test_violations.gds'
    tech_file_path = 'FreePDK45.tf'

    # Load tech file
    tech = TechFile()
    tech.parse_virtuoso_tech_file(tech_file_path)

    cell.export_gds(gds_file)
    print(f"✓ Exported to {gds_file}")

    # Step 3: Run DRC check
    print("\n[Step 3] Running DRC check on original layout...")
    checker = DRCChecker(tech.drc_rules)
    violations = checker.check_layout(cell)

    print(f"\n{'=' * 80}")
    print(f"Initial DRC Check Results")
    print(f"{'=' * 80}")
    checker.print_violations()

    expected_violations = 5  # We created 5 intentional violations
    print(f"\nExpected {expected_violations} violations, found {len(violations)}")

    if len(violations) == 0:
        print("✗ Test FAILED: No violations detected (should have found violations)")
        return False

    # Export violation report
    checker.export_violations_report('test_violations_initial.txt')

    # Step 4: Auto-fix violations
    print("\n[Step 4] Attempting to auto-fix violations...")
    fixer = DRCFixer(tech.drc_rules)
    fixed_count, unfixed_count = fixer.fix_violations(cell, violations)

    # Step 5: Re-check after fixes
    print("\n[Step 5] Re-checking DRC after auto-fix...")
    checker2 = DRCChecker(tech.drc_rules)
    violations_after = checker2.check_layout(cell)

    print(f"\n{'=' * 80}")
    print(f"Final DRC Check Results")
    print(f"{'=' * 80}")
    checker2.print_violations()

    # Export final report
    checker2.export_violations_report('test_violations_final.txt')

    # Step 6: Export fixed GDS
    print("\n[Step 6] Exporting fixed layout to GDS...")
    fixed_gds_file = 'test_violations_fixed.gds'
    cell.export_gds(fixed_gds_file)
    print(f"✓ Exported fixed layout to {fixed_gds_file}")

    # Step 7: Verify results
    print("\n[Step 7] Verifying results...")
    print(f"  Initial violations: {len(violations)}")
    print(f"  Violations after fix: {len(violations_after)}")
    print(f"  Fixed: {len(violations) - len(violations_after)}")
    print(f"  Remaining: {len(violations_after)}")

    improvement = 0
    if len(violations) > 0:
        improvement = 100 * (len(violations) - len(violations_after)) / len(violations)
        print(f"  Improvement: {improvement:.1f}%")

    # Test passes if we reduced violations
    if len(violations_after) < len(violations):
        print(f"\n✓ Test PASSED: DRC violations reduced from {len(violations)} to {len(violations_after)}")
        return True
    else:
        print(f"\n✗ Test FAILED: No improvement in DRC violations")
        return False


def test_drc_checker_only():
    """Test just the DRC checker on a simple layout"""
    print("\n" + "=" * 80)
    print("DRC Checker Unit Test")
    print("=" * 80)

    # Create a simple layout with one known violation
    print("\nCreating simple test layout...")

    # Metal1 rectangle with width 0.04 < 0.065 (violation)
    metal1 = Cell('metal1_test', 'metal1')
    metal1.pos_list = [0, 0, 0.04, 0.5]  # Width = 0.04 (violation)

    parent = Cell('simple_test', metal1)
    parent.pos_list = [0, 0, 1, 1]

    # Load DRC rules
    tech = TechFile()
    tech.parse_virtuoso_tech_file('FreePDK45.tf')

    # Check for violations
    checker = DRCChecker(tech.drc_rules)
    violations = checker.check_layout(parent)

    print(f"\nExpected: 1 width violation")
    print(f"Found: {len(violations)} violation(s)")

    checker.print_violations()

    if len(violations) >= 1:
        print("\n✓ Test PASSED: Width violation detected")
        return True
    else:
        print("\n✗ Test FAILED: Width violation not detected")
        return False


def test_drc_rules_parsing():
    """Test DRC rules parsing from tech file"""
    print("\n" + "=" * 80)
    print("DRC Rules Parsing Test")
    print("=" * 80)

    tech = TechFile()
    tech.parse_virtuoso_tech_file('FreePDK45.tf')

    print(f"\nParsed {len(tech.drc_rules.rules)} DRC rules")

    # Check for specific rules
    metal1_width = tech.drc_rules.get_min_width('metal1')
    metal1_spacing = tech.drc_rules.get_min_spacing('metal1')
    poly_width = tech.drc_rules.get_min_width('poly')

    print(f"\nKey rules:")
    print(f"  metal1 minWidth: {metal1_width}")
    print(f"  metal1 minSpacing: {metal1_spacing}")
    print(f"  poly minWidth: {poly_width}")

    tech.drc_rules.print_summary()

    # Verify expected values
    if metal1_width == 0.065 and metal1_spacing == 0.065 and poly_width == 0.05:
        print("\n✓ Test PASSED: DRC rules parsed correctly")
        return True
    else:
        print("\n✗ Test FAILED: DRC rules not parsed correctly")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("DRC Workflow Test Suite")
    print("=" * 80)

    results = []

    # Test 1: DRC rules parsing
    results.append(("DRC Rules Parsing", test_drc_rules_parsing()))

    # Test 2: DRC checker only
    results.append(("DRC Checker Unit Test", test_drc_checker_only()))

    # Test 3: Complete workflow
    results.append(("Complete DRC Workflow", test_drc_workflow_complete()))

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

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
