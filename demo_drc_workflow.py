#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple DRC Workflow Demonstration

This demonstrates the DRC workflow with a simple example that creates
a layout, intentionally introduces violations, and shows how to detect them.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile
from layout_automation.drc_checker import DRCChecker
from layout_automation.drc_fixer import DRCFixer


def demo_drc_detection():
    """Demonstrate DRC violation detection"""
    print("\n" + "=" * 80)
    print("DRC Workflow Demonstration - Violation Detection")
    print("=" * 80)

    print("\n[Step 1] Creating test layout with intentional violations...")

    # Create metal1 rectangles with violations
    # According to FreePDK45: metal1 minWidth=0.065, minSpacing=0.065

    # Violation 1: Width too small (0.04 < 0.065)
    m1_narrow = Cell('metal1_narrow', 'metal1')
    m1_narrow.pos_list = [0, 0, 0.04, 0.5]  # Width = 0.04 (VIOLATION)

    # Violation 2: Two rectangles too close (spacing 0.05 < 0.065)
    m1_left = Cell('metal1_left', 'metal1')
    m1_left.pos_list = [1.0, 0, 1.1, 0.3]  # Width = 0.1 (OK)

    m1_right = Cell('metal1_right', 'metal1')
    m1_right.pos_list = [1.15, 0, 1.25, 0.3]  # Spacing = 0.05 (VIOLATION)

    # Valid rectangle for comparison
    m1_ok = Cell('metal1_ok', 'metal1')
    m1_ok.pos_list = [0, 1.0, 0.2, 1.2]  # OK

    # Create parent
    layout = Cell('demo_layout', m1_narrow, m1_left, m1_right, m1_ok)
    layout.pos_list = [0, 0, 2, 2]

    print("✓ Created layout with 2 intentional violations")
    print(f"  - metal1_narrow: width {0.04} < {0.065} (minWidth violation)")
    print(f"  - metal1_left/right: spacing {0.05} < {0.065} (minSpacing violation)")

    # Export to GDS
    print("\n[Step 2] Exporting to GDS...")
    layout.export_gds('demo_violations.gds')
    print("✓ Exported to demo_violations.gds")

    # Load DRC rules
    print("\n[Step 3] Loading DRC rules from FreePDK45.tf...")
    tech = TechFile()
    tech.parse_virtuoso_tech_file('FreePDK45.tf')
    print(f"✓ Loaded {len(tech.drc_rules.rules)} DRC rules")

    # Check for violations
    print("\n[Step 4] Running DRC check...")
    checker = DRCChecker(tech.drc_rules)
    violations = checker.check_layout(layout)

    print(f"\n{'=' * 80}")
    print("DRC Check Results")
    print(f"{'=' * 80}")
    checker.print_violations()

    # Export report
    checker.export_violations_report('demo_violations_report.txt')
    print("\n✓ Exported detailed report to demo_violations_report.txt")

    # Show DRC rule details
    print(f"\n{'=' * 80}")
    print("Relevant DRC Rules (FreePDK45)")
    print(f"{'=' * 80}")
    print(f"  metal1 minWidth:   {tech.drc_rules.get_min_width('metal1')} µm")
    print(f"  metal1 minSpacing: {tech.drc_rules.get_min_spacing('metal1')} µm")
    print(f"  poly minWidth:     {tech.drc_rules.get_min_width('poly')} µm")
    print(f"  poly minSpacing:   {tech.drc_rules.get_min_spacing('poly')} µm")

    return len(violations) > 0


def demo_drc_fix():
    """Demonstrate DRC violation fixing"""
    print("\n" + "=" * 80)
    print("DRC Workflow Demonstration - Auto-Fix")
    print("=" * 80)

    print("\n[Step 1] Creating layout with width violation...")

    # Simple width violation that can be fixed
    m1 = Cell('metal1_rect', 'metal1')
    m1.pos_list = [0, 0, 0.04, 0.5]  # Width 0.04 < 0.065 (VIOLATION)

    layout = Cell('fix_demo', m1)
    layout.pos_list = [0, 0, 1, 1]

    # Load DRC rules
    tech = TechFile()
    tech.parse_virtuoso_tech_file('FreePDK45.tf')

    # Check violations
    print("\n[Step 2] Checking for violations...")
    checker = DRCChecker(tech.drc_rules)
    violations = checker.check_layout(layout)

    print(f"Found {len(violations)} violation(s):")
    for v in violations:
        print(f"  - {v.message}")

    # Fix violations
    print("\n[Step 3] Attempting auto-fix...")
    fixer = DRCFixer(tech.drc_rules)
    fixed, unfixed = fixer.fix_violations(layout, violations)

    # Re-check
    print("\n[Step 4] Re-checking after fix...")
    violations_after = checker.check_layout(layout)

    if len(violations_after) == 0:
        print("✓ All violations fixed!")
    else:
        print(f"✗ {len(violations_after)} violation(s) remain")

    # Export fixed layout
    print("\n[Step 5] Exporting fixed layout...")
    layout.export_gds('demo_fixed.gds')
    print("✓ Exported to demo_fixed.gds")

    return len(violations_after) < len(violations)


def main():
    """Run demonstrations"""
    print("=" * 80)
    print("DRC Workflow - Simple Demonstration")
    print("=" * 80)
    print("\nThis demo shows how to:")
    print("  1. Create layouts with DRC violations")
    print("  2. Load DRC rules from technology files")
    print("  3. Detect violations automatically")
    print("  4. Auto-fix violations when possible")
    print("  5. Generate violation reports")

    # Demo 1: Detection
    demo_drc_detection()

    # Demo 2: Fixing
    demo_drc_fix()

    print("\n" + "=" * 80)
    print("Demonstration Complete")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - demo_violations.gds - Layout with violations")
    print("  - demo_violations_report.txt - Detailed violation report")
    print("  - demo_fixed.gds - Fixed layout")
    print("\nTo use the full workflow on your GDS files:")
    print("  python drc_workflow.py input.gds FreePDK45.tf output_fixed.gds")


if __name__ == '__main__':
    main()
