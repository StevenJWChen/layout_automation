#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRC Workflow: Import GDS, Check DRC, Auto-Fix Violations, Export Fixed GDS

This script provides an end-to-end workflow for:
1. Importing a GDS file
2. Loading DRC rules from a technology file
3. Checking for DRC violations
4. Automatically fixing violations
5. Re-checking violations
6. Exporting the fixed GDS
7. Generating violation reports

Usage:
    python drc_workflow.py input.gds FreePDK45.tf output.gds
    python drc_workflow.py input.gds FreePDK45.tf output.gds --check-only
    python drc_workflow.py input.gds FreePDK45.tf output.gds --max-iterations 10
"""

import sys
import argparse
from pathlib import Path

# Import layout automation modules
from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile
from layout_automation.drc_checker import DRCChecker
from layout_automation.drc_fixer import DRCFixer


def run_drc_workflow(gds_input: str, tech_file: str, gds_output: str = None,
                     check_only: bool = False, max_iterations: int = 5,
                     report_file: str = None):
    """
    Run the complete DRC workflow

    Args:
        gds_input: Path to input GDS file
        tech_file: Path to technology file (.tf)
        gds_output: Path to output GDS file (optional)
        check_only: If True, only check violations without fixing
        max_iterations: Maximum fix-check iterations
        report_file: Path to violation report file (optional)
    """
    print("=" * 80)
    print("DRC Workflow - Design Rule Check and Auto-Fix")
    print("=" * 80)

    # Step 1: Load technology file and DRC rules
    print("\n[Step 1/7] Loading technology file and DRC rules...")
    tech = TechFile()
    tech.parse_virtuoso_tech_file(tech_file)

    if len(tech.drc_rules.rules) == 0:
        print("✗ Error: No DRC rules found in technology file")
        return False

    print(f"✓ Loaded {len(tech.drc_rules.rules)} DRC rules")
    tech.drc_rules.print_summary()

    # Step 2: Import GDS file
    print(f"\n[Step 2/7] Importing GDS file: {gds_input}")
    try:
        # Use import_gds_to_cell for better constraint support
        cell = Cell.import_gds_to_cell(gds_input, tech_file=tech)
        print(f"✓ Imported GDS: {cell.name}")
    except Exception as e:
        print(f"✗ Error importing GDS: {e}")
        return False

    # Step 3: Run initial DRC check
    print(f"\n[Step 3/7] Running DRC check...")
    checker = DRCChecker(tech.drc_rules)
    violations = checker.check_layout(cell)

    print(f"\n{'=' * 80}")
    print(f"Initial DRC Check Results")
    print(f"{'=' * 80}")
    checker.print_violations()

    if len(violations) == 0:
        print("\n✓ Layout is DRC clean! No violations found.")
        if gds_output:
            print(f"\n[Step 7/7] Exporting GDS (no changes needed): {gds_output}")
            cell.export_gds(gds_output, tech_file=tech)
        return True

    # Export initial violation report
    if report_file:
        initial_report = report_file.replace('.txt', '_initial.txt')
        checker.export_violations_report(initial_report)

    if check_only:
        print("\n[Info] Check-only mode enabled. Skipping auto-fix.")
        return len(violations) == 0

    # Step 4: Auto-fix violations
    print(f"\n[Step 4/7] Attempting to auto-fix violations...")
    fixer = DRCFixer(tech.drc_rules)
    fixed_count, unfixed_count = fixer.fix_violations(cell, violations, max_iterations)

    # Step 5: Re-check DRC after fixes
    print(f"\n[Step 5/7] Re-checking DRC after fixes...")
    checker2 = DRCChecker(tech.drc_rules)
    violations_after = checker2.check_layout(cell)

    print(f"\n{'=' * 80}")
    print(f"Final DRC Check Results")
    print(f"{'=' * 80}")
    checker2.print_violations()

    # Step 6: Compare results
    print(f"\n[Step 6/7] Comparing results...")
    print(f"  Initial violations: {len(violations)}")
    print(f"  Fixed violations:   {len(violations) - len(violations_after)}")
    print(f"  Remaining violations: {len(violations_after)}")

    if len(violations_after) < len(violations):
        improvement = 100 * (len(violations) - len(violations_after)) / len(violations)
        print(f"  Improvement: {improvement:.1f}%")

    # Export final violation report
    if report_file:
        final_report = report_file.replace('.txt', '_final.txt')
        checker2.export_violations_report(final_report)

    # Step 7: Export fixed GDS
    if gds_output:
        print(f"\n[Step 7/7] Exporting fixed GDS: {gds_output}")
        try:
            cell.export_gds(gds_output, tech_file=tech)
            print(f"✓ Successfully exported fixed GDS")
        except Exception as e:
            print(f"✗ Error exporting GDS: {e}")
            return False

    print("\n" + "=" * 80)
    print("DRC Workflow Complete")
    print("=" * 80)

    return len(violations_after) == 0


def main():
    """Command-line interface for DRC workflow"""
    parser = argparse.ArgumentParser(
        description='DRC Workflow: Import GDS, Check DRC, Auto-Fix, Export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow (check + fix + export)
  python drc_workflow.py input.gds FreePDK45.tf output_fixed.gds

  # Check only (no fixing)
  python drc_workflow.py input.gds FreePDK45.tf --check-only

  # Generate violation reports
  python drc_workflow.py input.gds FreePDK45.tf output.gds --report violations.txt

  # Adjust fix iterations
  python drc_workflow.py input.gds FreePDK45.tf output.gds --max-iterations 10
        """
    )

    parser.add_argument('gds_input', type=str,
                        help='Input GDS file path')
    parser.add_argument('tech_file', type=str,
                        help='Technology file path (.tf)')
    parser.add_argument('gds_output', type=str, nargs='?', default=None,
                        help='Output GDS file path (optional)')
    parser.add_argument('--check-only', action='store_true',
                        help='Only check violations without fixing')
    parser.add_argument('--max-iterations', type=int, default=5,
                        help='Maximum fix-check iterations (default: 5)')
    parser.add_argument('--report', type=str, default=None,
                        help='Violation report output file (default: None)')

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.gds_input).exists():
        print(f"✗ Error: Input GDS file not found: {args.gds_input}")
        sys.exit(1)

    if not Path(args.tech_file).exists():
        print(f"✗ Error: Technology file not found: {args.tech_file}")
        sys.exit(1)

    # Auto-generate output filename if not provided
    if args.gds_output is None and not args.check_only:
        input_path = Path(args.gds_input)
        args.gds_output = str(input_path.parent / f"{input_path.stem}_fixed.gds")
        print(f"[Info] Auto-generated output filename: {args.gds_output}")

    # Auto-generate report filename if not provided
    if args.report is None:
        input_path = Path(args.gds_input)
        args.report = str(input_path.parent / f"{input_path.stem}_drc_report.txt")

    # Run workflow
    success = run_drc_workflow(
        gds_input=args.gds_input,
        tech_file=args.tech_file,
        gds_output=args.gds_output,
        check_only=args.check_only,
        max_iterations=args.max_iterations,
        report_file=args.report
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
