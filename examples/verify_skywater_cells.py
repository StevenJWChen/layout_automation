#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify SkyWater Standard Cells

Runs DRC and LVS verification on actual SkyWater SKY130 standard cells
to validate our verification tools against production-quality layouts.
"""

import gdstk
from pathlib import Path
from layout_automation.drc_improved import run_improved_drc
from tools.skywater_direct_extractor import extract_skywater_direct
from layout_automation.lvs import LVSChecker, Netlist, Device
from layout_automation.technology import Technology
from layout_automation.units import to_um
import sys


def load_skywater_cell(gds_file, cell_name=None):
    """
    Load a SkyWater standard cell from GDS

    Args:
        gds_file: Path to GDS file
        cell_name: Name of cell to load (None = top cell)

    Returns:
        Cell object that can be used for DRC/extraction
    """
    from gds_cell import Cell as GDSCell

    print(f"Loading SkyWater cell: {gds_file}")

    # Read GDS
    library = gdstk.read_gds(gds_file)

    # Find the cell
    if cell_name:
        gds_cell = [c for c in library.cells if c.name == cell_name]
        if not gds_cell:
            print(f"Error: Cell '{cell_name}' not found")
            return None
        gds_cell = gds_cell[0]
    else:
        top_cells = library.top_level()
        if not top_cells:
            gds_cell = library.cells[0]
        else:
            gds_cell = top_cells[0]

    print(f"  Cell: {gds_cell.name}")

    # Import using the Cell's import_gds method
    cell = GDSCell(gds_cell.name)

    # Import from the library - this handles the conversion properly
    try:
        cell.import_gds(gds_file, top_cell_name=gds_cell.name)
        print(f"  Imported successfully")
    except Exception as e:
        print(f"  Warning: Direct import failed ({e}), using fallback")
        # Fallback: just store the gdstk cell for extraction
        cell._gdstk_cell = gds_cell
        cell._gdstk_library = library

    return cell


def create_inv_1_schematic():
    """
    Create schematic for sky130_fd_sc_hd__inv_1

    Standard inverter (based on extracted layout):
    - 1 NMOS (W=650nm, L=430nm)
    - 1 PMOS (W=1000nm, L=430nm)
    """
    netlist = Netlist("sky130_fd_sc_hd__inv_1")

    # NMOS pull-down
    netlist.add_device(Device(
        name='M0',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 430e-9}
    ))

    # PMOS pull-up
    netlist.add_device(Device(
        name='M1',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 430e-9}
    ))

    return netlist


def create_nand2_1_schematic():
    """
    Create schematic for sky130_fd_sc_hd__nand2_1

    2-input NAND:
    - 2 NMOS in series
    - 2 PMOS in parallel
    """
    netlist = Netlist("sky130_fd_sc_hd__nand2_1")

    # NMOS series (bottom to top)
    netlist.add_device(Device(
        name='M0',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'a_27_47#', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 150e-9}
    ))

    netlist.add_device(Device(
        name='M1',
        device_type='nmos',
        terminals={'g': 'B', 'd': 'a_27_47#', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 150e-9}
    ))

    # PMOS parallel
    netlist.add_device(Device(
        name='M2',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 150e-9}
    ))

    netlist.add_device(Device(
        name='M3',
        device_type='pmos',
        terminals={'g': 'B', 'd': 'Y', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 150e-9}
    ))

    return netlist


def create_and3_1_schematic():
    """
    Create schematic for sky130_fd_sc_hd__and3_1

    3-input AND (NAND3 + inverter):
    - NAND3 (6 transistors: 3 NMOS series, 3 PMOS parallel)
    - Inverter (2 transistors)
    Total: 8 transistors
    """
    netlist = Netlist("sky130_fd_sc_hd__and3_1")

    # NAND3 stage - NMOS in series
    netlist.add_device(Device(
        name='M0',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'nand_out', 's': 'n1', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 430e-9}
    ))

    netlist.add_device(Device(
        name='M1',
        device_type='nmos',
        terminals={'g': 'B', 'd': 'n1', 's': 'n2', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 430e-9}
    ))

    netlist.add_device(Device(
        name='M2',
        device_type='nmos',
        terminals={'g': 'C', 'd': 'n2', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 430e-9}
    ))

    # NAND3 stage - PMOS in parallel
    netlist.add_device(Device(
        name='M3',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'nand_out', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 430e-9}
    ))

    netlist.add_device(Device(
        name='M4',
        device_type='pmos',
        terminals={'g': 'B', 'd': 'nand_out', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 430e-9}
    ))

    netlist.add_device(Device(
        name='M5',
        device_type='pmos',
        terminals={'g': 'C', 'd': 'nand_out', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 430e-9}
    ))

    # Inverter stage
    netlist.add_device(Device(
        name='M6',
        device_type='nmos',
        terminals={'g': 'nand_out', 'd': 'X', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 430e-9}
    ))

    netlist.add_device(Device(
        name='M7',
        device_type='pmos',
        terminals={'g': 'nand_out', 'd': 'X', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 430e-9}
    ))

    return netlist


def create_and2_1_schematic():
    """
    Create schematic for sky130_fd_sc_hd__and2_1

    2-input AND (NAND + inverter):
    - NAND2 (4 transistors)
    - Inverter (2 transistors)
    Total: 6 transistors
    """
    netlist = Netlist("sky130_fd_sc_hd__and2_1")

    # NAND2 stage
    netlist.add_device(Device(
        name='M0',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'nand_out', 's': 'a_27_47#', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 150e-9}
    ))

    netlist.add_device(Device(
        name='M1',
        device_type='nmos',
        terminals={'g': 'B', 'd': 'a_27_47#', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 150e-9}
    ))

    netlist.add_device(Device(
        name='M2',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'nand_out', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 150e-9}
    ))

    netlist.add_device(Device(
        name='M3',
        device_type='pmos',
        terminals={'g': 'B', 'd': 'nand_out', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 150e-9}
    ))

    # Inverter stage
    netlist.add_device(Device(
        name='M4',
        device_type='nmos',
        terminals={'g': 'nand_out', 'd': 'X', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 150e-9}
    ))

    netlist.add_device(Device(
        name='M5',
        device_type='pmos',
        terminals={'g': 'nand_out', 'd': 'X', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 150e-9}
    ))

    return netlist


def verify_skywater_cell(gds_file, schematic, cell_name=None, description=""):
    """
    Complete verification of a SkyWater standard cell

    Args:
        gds_file: Path to GDS file
        schematic: Schematic netlist
        cell_name: Cell name to verify
        description: Cell description

    Returns:
        dict with verification results
    """
    print("\n" + "="*70)
    print(f"VERIFYING SKYWATER CELL: {description}")
    print("="*70)

    results = {
        'name': schematic.name,
        'description': description,
        'load_ok': False,
        'drc_pass': False,
        'drc_violations': 0,
        'extraction_ok': False,
        'extracted_count': 0,
        'expected_count': len(schematic.devices),
        'lvs_pass': False,
        'lvs_violations': 0
    }

    # Load cell
    tech = Technology('sky130')
    cell = load_skywater_cell(gds_file, cell_name)

    if not cell:
        print("❌ Failed to load cell")
        return results

    results['load_ok'] = True

    # Step 1: Run DRC
    print("\n" + "-"*70)
    print("STEP 1: DRC Verification")
    print("-"*70)

    try:
        violations, checker = run_improved_drc(cell, tech)
        results['drc_violations'] = len(violations)

        if len(violations) == 0:
            results['drc_pass'] = True
            print(f"✅ DRC CLEAN - No violations!")
        else:
            print(f"⚠️  DRC: {len(violations)} violations")

            # Categorize
            width_viol = sum(1 for v in violations if 'Width' in v.message)
            spacing_viol = sum(1 for v in violations if 'Spacing' in v.message)
            area_viol = sum(1 for v in violations if 'Area' in v.message)

            print(f"   Width: {width_viol}, Spacing: {spacing_viol}, Area: {area_viol}")

            # Show first 5
            for i, v in enumerate(violations[:5], 1):
                print(f"   {i}. {v.message[:70]}")
            if len(violations) > 5:
                print(f"   ... and {len(violations) - 5} more")

    except Exception as e:
        print(f"❌ DRC failed with error: {e}")
        import traceback
        traceback.print_exc()

    # Step 2: Extract netlist
    print("\n" + "-"*70)
    print("STEP 2: Netlist Extraction")
    print("-"*70)

    try:
        extracted = extract_skywater_direct(gds_file, cell_name, tech)
        results['extracted_count'] = len(extracted.devices)
        results['extraction_ok'] = True

        print(f"Extracted: {len(extracted.devices)} devices")
        print(f"Expected:  {len(schematic.devices)} devices")

        if len(extracted.devices) == len(schematic.devices):
            print("✅ Device count matches!")
        else:
            ratio = len(extracted.devices) / len(schematic.devices) if len(schematic.devices) > 0 else 0
            print(f"⚠️  Count mismatch (ratio: {ratio:.2f}x)")

        # Show device types
        ext_nmos = sum(1 for d in extracted.devices.values() if d.device_type == 'nmos')
        ext_pmos = sum(1 for d in extracted.devices.values() if d.device_type == 'pmos')
        sch_nmos = sum(1 for d in schematic.devices.values() if d.device_type == 'nmos')
        sch_pmos = sum(1 for d in schematic.devices.values() if d.device_type == 'pmos')

        print(f"   Extracted: {ext_nmos} NMOS, {ext_pmos} PMOS")
        print(f"   Expected:  {sch_nmos} NMOS, {sch_pmos} PMOS")

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return results

    # Step 3: Run LVS
    print("\n" + "-"*70)
    print("STEP 3: LVS Verification")
    print("-"*70)

    try:
        lvs_checker = LVSChecker(schematic, extracted)
        lvs_violations = lvs_checker.verify()
        results['lvs_violations'] = len(lvs_violations)

        if len(lvs_violations) == 0:
            results['lvs_pass'] = True
            print("✅ LVS PASSED - Netlists match!")
        else:
            print(f"⚠️  LVS: {len(lvs_violations)} violations")

            # Show first 10
            for i, v in enumerate(lvs_violations[:10], 1):
                print(f"   {i}. {v.message[:70]}")
            if len(lvs_violations) > 10:
                print(f"   ... and {len(lvs_violations) - 10} more")

    except Exception as e:
        print(f"❌ LVS failed: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "-"*70)
    print("SUMMARY")
    print("-"*70)
    load_msg = '✅ PASS' if results['load_ok'] else '❌ FAIL'
    drc_msg = '✅ PASS' if results['drc_pass'] else f'⚠️  {results["drc_violations"]} violations'
    ext_msg = '✅ PASS' if results['extraction_ok'] and results['extracted_count'] == results['expected_count'] else f'⚠️  {results["extracted_count"]}/{results["expected_count"]} devices'
    lvs_msg = '✅ PASS' if results['lvs_pass'] else f'⚠️  {results["lvs_violations"]} violations'
    print(f"  Cell Load:      {load_msg}")
    print(f"  DRC:            {drc_msg}")
    print(f"  Extraction:     {ext_msg}")
    print(f"  LVS:            {lvs_msg}")

    return results


def main():
    """Test verification tools on SkyWater standard cells"""

    print("="*70)
    print("SKYWATER STANDARD CELL VERIFICATION")
    print("="*70)
    print("\nTesting DRC and LVS tools on production-quality SkyWater cells")
    print()

    # Find SkyWater cell GDS files
    test_cells = []

    # Check for existing SkyWater replicas
    skywater_files = [
        ('sky130_inv_replica.gds', 'sky130_fd_sc_hd__inv_1_replica', create_inv_1_schematic(), "Inverter (1x drive)"),
        ('sky130_and3_replica.gds', 'sky130_fd_sc_hd__and3_1_replica', create_and3_1_schematic(), "3-input AND (NAND3 + INV)"),
        ('sky130_and3_with_routing.gds', 'sky130_and3_routed', create_and3_1_schematic(), "3-input AND with routing"),
    ]

    all_results = []

    # Test each cell
    for gds_file, cell_name, schematic, description in skywater_files:
        if not Path(gds_file).exists():
            print(f"\n⚠️  Skipping {description}: {gds_file} not found")
            continue

        results = verify_skywater_cell(gds_file, schematic, cell_name, description)
        all_results.append(results)

    # Final summary
    if all_results:
        print("\n\n" + "="*70)
        print("FINAL SUMMARY - SKYWATER CELLS")
        print("="*70)

        print(f"\n{'Cell':<30} {'Load':<8} {'DRC':<10} {'Extract':<12} {'LVS':<10}")
        print("-"*70)

        for r in all_results:
            load_status = "✅" if r['load_ok'] else "❌"
            drc_status = "✅" if r['drc_pass'] else f"⚠️ {r['drc_violations']}v"
            ext_status = "✅" if r['extraction_ok'] and r['extracted_count'] == r['expected_count'] else f"⚠️ {r['extracted_count']}/{r['expected_count']}"
            lvs_status = "✅" if r['lvs_pass'] else f"⚠️ {r['lvs_violations']}v"

            print(f"{r['description']:<30} {load_status:<8} {drc_status:<10} {ext_status:<12} {lvs_status:<10}")

        # Statistics
        total = len(all_results)
        drc_pass = sum(1 for r in all_results if r['drc_pass'])
        ext_pass = sum(1 for r in all_results if r['extraction_ok'] and r['extracted_count'] == r['expected_count'])
        lvs_pass = sum(1 for r in all_results if r['lvs_pass'])

        print("\n" + "="*70)
        print(f"Results: {total} cell(s) tested")
        print(f"  DRC Clean:     {drc_pass}/{total}")
        print(f"  Extraction OK: {ext_pass}/{total}")
        print(f"  LVS Clean:     {lvs_pass}/{total}")
        print("="*70)

    else:
        print("\n⚠️  No SkyWater cells found to test")
        print("\nExpected files:")
        print("  • sky130_inv_replica.gds - Inverter")
        print("\nTo create test cells, run the replication scripts first.")


if __name__ == "__main__":
    main()
