#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Improved Flow with Step-by-Step Checks

Tests each case to ensure:
1. Layout generation works ✓
2. DRC passes cleanly (0 violations)
3. Extraction matches original netlist
4. LVS passes cleanly
"""

import sys
from pathlib import Path

# Import all necessary modules
from tests.test_cases import (
    create_inverter_schematic,
    create_nand2_schematic,
    create_nor2_schematic,
    create_and3_schematic,
    create_mux2to1_schematic
)
from layout_automation.layout_from_schematic import LayoutGenerator
from layout_automation.drc_improved import run_improved_drc
from tools.netlist_extractor_improved import extract_improved_netlist
from layout_automation.lvs import LVSChecker
from layout_automation.technology import Technology
from layout_automation.units import to_um


def verify_single_case(case_name: str, schematic_netlist, tech):
    """
    Verify a single test case step-by-step

    Returns:
        dict with results for each step
    """
    print(f"\n{'='*70}")
    print(f"TEST CASE: {case_name}")
    print(f"{'='*70}\n")

    results = {
        'name': case_name,
        'layout_generated': False,
        'drc_passed': False,
        'drc_violations': 0,
        'extraction_correct': False,
        'extracted_count': 0,
        'expected_count': 0,
        'lvs_passed': False,
        'lvs_violations': 0
    }

    # Step 1: Generate Layout
    print("Step 1: Generating Layout from Netlist...")
    print("-" * 70)

    try:
        generator = LayoutGenerator(schematic_netlist, tech)
        layout_cell = generator.generate()

        # Save layout
        gds_file = f"{case_name}_improved.gds"
        layout_cell.export_gds(gds_file)

        results['layout_generated'] = True
        print(f"✅ Layout generated successfully: {gds_file}")
        print(f"   Area: {to_um(layout_cell.bbox()[2]):.3f} × {to_um(layout_cell.bbox()[3]):.3f} μm")

    except Exception as e:
        print(f"❌ Layout generation failed: {e}")
        return results

    # Step 2: Run Improved DRC
    print("\nStep 2: Running Improved DRC (Topology-Aware)...")
    print("-" * 70)

    try:
        violations, checker = run_improved_drc(layout_cell, tech)
        results['drc_violations'] = len(violations)

        if len(violations) == 0:
            results['drc_passed'] = True
            print("✅ DRC PASSED - No violations found!")
        else:
            print(f"❌ DRC FAILED - {len(violations)} violations found:")
            # Show first 5 violations
            for i, v in enumerate(violations[:5], 1):
                print(f"   {i}. {v.message}")
            if len(violations) > 5:
                print(f"   ... and {len(violations) - 5} more")

    except Exception as e:
        print(f"❌ DRC check failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    # Step 3: Extract Netlist with Improved Extractor
    print("\nStep 3: Extracting Netlist from Layout (Contact-Filtered)...")
    print("-" * 70)

    try:
        extracted_netlist = extract_improved_netlist(layout_cell, tech)

        # Save extracted netlist
        netlist_file = f"{case_name}_improved_extracted.txt"
        with open(netlist_file, 'w') as f:
            f.write(f"Extracted Netlist: {extracted_netlist.name}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Devices: {len(extracted_netlist.devices)}\n\n")
            for dev in extracted_netlist.devices:
                f.write(f"{dev.name}:\n")
                f.write(f"  Type: {dev.device_type}\n")
                f.write(f"  Parameters: {dev.parameters}\n")
                f.write(f"  Terminals: {dev.terminals}\n\n")

        results['extracted_count'] = len(extracted_netlist.devices)
        results['expected_count'] = len(schematic_netlist.devices)

        if results['extracted_count'] == results['expected_count']:
            results['extraction_correct'] = True
            print(f"✅ Extraction correct: {results['extracted_count']} devices "
                  f"(expected {results['expected_count']})")
        else:
            print(f"❌ Extraction mismatch: {results['extracted_count']} devices "
                  f"(expected {results['expected_count']})")
            print(f"   Ratio: {results['extracted_count'] / results['expected_count']:.1f}x")

        # Show device breakdown
        nmos_count = sum(1 for d in extracted_netlist.devices if d.device_type == 'nmos')
        pmos_count = sum(1 for d in extracted_netlist.devices if d.device_type == 'pmos')
        print(f"   Extracted: {nmos_count} NMOS, {pmos_count} PMOS")

        expected_nmos = sum(1 for d in schematic_netlist.devices if d.device_type == 'nmos')
        expected_pmos = sum(1 for d in schematic_netlist.devices if d.device_type == 'pmos')
        print(f"   Expected:  {expected_nmos} NMOS, {expected_pmos} PMOS")

    except Exception as e:
        print(f"❌ Netlist extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    # Step 4: Run LVS
    print("\nStep 4: Running LVS Comparison...")
    print("-" * 70)

    try:
        lvs_checker = LVSChecker(schematic_netlist, extracted_netlist)
        lvs_violations = lvs_checker.verify()
        results['lvs_violations'] = len(lvs_violations)

        if len(lvs_violations) == 0:
            results['lvs_passed'] = True
            print("✅ LVS PASSED - Netlists match!")
        else:
            print(f"❌ LVS FAILED - {len(lvs_violations)} violations:")
            for v in lvs_violations:
                print(f"   • {v.message}")

    except Exception as e:
        print(f"❌ LVS comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    # Summary
    print(f"\n{'-'*70}")
    print(f"Summary for {case_name}:")
    layout_msg = '✅ PASS' if results['layout_generated'] else '❌ FAIL'
    drc_msg = '✅ PASS' if results['drc_passed'] else f'❌ FAIL ({results["drc_violations"]} violations)'
    extract_msg = '✅ PASS' if results['extraction_correct'] else f'❌ FAIL ({results["extracted_count"]}/{results["expected_count"]} devices)'
    lvs_msg = '✅ PASS' if results['lvs_passed'] else f'❌ FAIL ({results["lvs_violations"]} violations)'
    print(f"  Layout Generation: {layout_msg}")
    print(f"  DRC Check:         {drc_msg}")
    print(f"  Extraction:        {extract_msg}")
    print(f"  LVS Verification:  {lvs_msg}")

    all_passed = (results['layout_generated'] and results['drc_passed'] and
                  results['extraction_correct'] and results['lvs_passed'])
    print(f"\n  Overall: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}")
    print(f"{'-'*70}")

    return results


def main():
    """Run all 5 test cases with improved flow"""
    print("="*70)
    print("IMPROVED VERIFICATION FLOW")
    print("="*70)
    print("\nTesting 5 cases with:")
    print("  • Topology-aware DRC (recognizes valid constructs)")
    print("  • Contact-filtered extraction (avoids over-counting)")
    print("  • Full LVS verification")
    print()

    # Initialize technology
    tech = Technology('sky130')

    # Define test cases
    test_cases = [
        ("test1_inverter", create_inverter_schematic()),
        ("test2_nand2", create_nand2_schematic()),
        ("test3_nor2", create_nor2_schematic()),
        ("test4_and3", create_and3_schematic()),
        ("test5_2-to-1_multiplexer", create_mux2to1_schematic()),
    ]

    # Run all tests
    all_results = []
    for case_name, schematic in test_cases:
        results = verify_single_case(case_name, schematic, tech)
        all_results.append(results)

    # Final Summary
    print("\n\n" + "="*70)
    print("FINAL SUMMARY - ALL TEST CASES")
    print("="*70 + "\n")

    print(f"{'Test Case':<30} {'Layout':<8} {'DRC':<8} {'Extract':<10} {'LVS':<8} {'Overall':<10}")
    print("-"*70)

    for r in all_results:
        layout_status = "✅ PASS" if r['layout_generated'] else "❌ FAIL"
        drc_status = "✅ PASS" if r['drc_passed'] else f"❌ {r['drc_violations']}v"
        extract_status = "✅ PASS" if r['extraction_correct'] else f"❌ {r['extracted_count']}/{r['expected_count']}"
        lvs_status = "✅ PASS" if r['lvs_passed'] else f"❌ {r['lvs_violations']}v"

        all_passed = (r['layout_generated'] and r['drc_passed'] and
                     r['extraction_correct'] and r['lvs_passed'])
        overall_status = "✅ PASS" if all_passed else "❌ FAIL"

        print(f"{r['name']:<30} {layout_status:<8} {drc_status:<8} {extract_status:<10} {lvs_status:<8} {overall_status:<10}")

    # Statistics
    total_passed = sum(1 for r in all_results if (
        r['layout_generated'] and r['drc_passed'] and
        r['extraction_correct'] and r['lvs_passed']
    ))

    print("\n" + "="*70)
    print(f"RESULT: {total_passed}/5 test cases passed all checks")

    if total_passed == 5:
        print("🎉 SUCCESS - All test cases verified!")
    else:
        print(f"⚠️  {5 - total_passed} test case(s) still have issues")

    print("="*70)

    return all_results


if __name__ == "__main__":
    main()
