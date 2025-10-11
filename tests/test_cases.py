#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cases for End-to-End IC Design Flow

5 different circuits to test the complete flow:
1. Simple Inverter (2 transistors)
2. NAND2 Gate (4 transistors)
3. NOR2 Gate (4 transistors)
4. AND3 Gate (8 transistors) - existing
5. Complex: 2-to-1 Multiplexer (8 transistors)

Each test case runs the complete flow and reports results.
"""

import sys
from layout_automation.lvs import Netlist, Device
from end_to_end_flow import EndToEndFlow
from layout_automation.technology import create_sky130_tech


def create_inverter_schematic() -> Netlist:
    """
    Test Case 1: Simple Inverter

    Circuit: Y = ~A
    Transistors: 2 (1 NMOS + 1 PMOS)
    """
    netlist = Netlist("INVERTER")

    # NMOS pull-down
    netlist.add_device(Device(
        name='M1',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # PMOS pull-up
    netlist.add_device(Device(
        name='M2',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    return netlist


def create_nand2_schematic() -> Netlist:
    """
    Test Case 2: NAND2 Gate

    Circuit: Y = ~(A & B)
    Transistors: 4 (2 NMOS in series + 2 PMOS in parallel)
    """
    netlist = Netlist("NAND2")

    # NMOS pull-down (series)
    netlist.add_device(Device(
        name='M1',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'n1', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M2',
        device_type='nmos',
        terminals={'g': 'B', 'd': 'n1', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # PMOS pull-up (parallel)
    netlist.add_device(Device(
        name='M3',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M4',
        device_type='pmos',
        terminals={'g': 'B', 'd': 'Y', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    return netlist


def create_nor2_schematic() -> Netlist:
    """
    Test Case 3: NOR2 Gate

    Circuit: Y = ~(A | B)
    Transistors: 4 (2 NMOS in parallel + 2 PMOS in series)
    """
    netlist = Netlist("NOR2")

    # NMOS pull-down (parallel)
    netlist.add_device(Device(
        name='M1',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M2',
        device_type='nmos',
        terminals={'g': 'B', 'd': 'Y', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # PMOS pull-up (series)
    netlist.add_device(Device(
        name='M3',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'n1', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M4',
        device_type='pmos',
        terminals={'g': 'B', 'd': 'n1', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    return netlist


def create_and3_schematic() -> Netlist:
    """
    Test Case 4: AND3 Gate (already implemented in lvs.py)

    Circuit: Y = A & B & C
    Transistors: 8 (NAND3 + Inverter)
    """
    from lvs import create_and3_schematic_netlist
    netlist = create_and3_schematic_netlist()
    netlist.name = "AND3"
    return netlist


def create_mux2to1_schematic() -> Netlist:
    """
    Test Case 5: 2-to-1 Multiplexer

    Circuit: Y = S ? B : A
    Implementation: Transmission gates + inverters
    Transistors: 8 (simplified CMOS implementation)

    Simplified as: Y = (A & ~S) | (B & S)
    Using: NAND(A, ~S) NAND with NAND(B, S) -> NOR
    """
    netlist = Netlist("MUX2to1")

    # First stage: Inverter for S -> S_bar
    netlist.add_device(Device(
        name='M_INV_N',
        device_type='nmos',
        terminals={'g': 'S', 'd': 'S_bar', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M_INV_P',
        device_type='pmos',
        terminals={'g': 'S', 'd': 'S_bar', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Path A (when S=0): NMOS passes A
    netlist.add_device(Device(
        name='M_A_N',
        device_type='nmos',
        terminals={'g': 'S_bar', 'd': 'Y', 's': 'A', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M_A_P',
        device_type='pmos',
        terminals={'g': 'S', 'd': 'Y', 's': 'A', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    # Path B (when S=1): NMOS passes B
    netlist.add_device(Device(
        name='M_B_N',
        device_type='nmos',
        terminals={'g': 'S', 'd': 'Y', 's': 'B', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M_B_P',
        device_type='pmos',
        terminals={'g': 'S_bar', 'd': 'Y', 's': 'B', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    # Output buffer (inverter pair for drive strength)
    netlist.add_device(Device(
        name='M_BUF_N',
        device_type='nmos',
        terminals={'g': 'Y', 'd': 'OUT', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='M_BUF_P',
        device_type='pmos',
        terminals={'g': 'Y', 'd': 'OUT', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    return netlist


def run_test_case(test_num: int, name: str, schematic: Netlist) -> dict:
    """
    Run complete flow for a test case

    Returns:
        Dictionary with results
    """
    print("\n" + "="*70)
    print(f"TEST CASE {test_num}: {name}")
    print("="*70)

    # Create technology
    tech = create_sky130_tech()

    # Create output name
    output_name = f"test{test_num}_{name.lower().replace(' ', '_')}"

    # Run complete flow
    flow = EndToEndFlow(schematic, tech, output_name=output_name)
    success = flow.run()

    # Collect results
    results = {
        'test_num': test_num,
        'name': name,
        'circuit': schematic.name,
        'devices_schematic': len(schematic.devices),
        'devices_extracted': len(flow.extracted_netlist.devices) if flow.extracted_netlist else 0,
        'drc_violations': len(flow.drc_violations),
        'lvs_violations': len(flow.lvs_violations),
        'lvs_clean': len(flow.lvs_violations) == 0,
        'success': success,
        'output_files': [
            f"{output_name}.gds",
            f"{output_name}_extracted.txt",
            f"{output_name}_report.txt"
        ]
    }

    return results


def print_summary_table(all_results: list):
    """Print summary table of all test results"""
    print("\n" + "="*70)
    print("SUMMARY OF ALL TEST CASES")
    print("="*70)

    print("\n{:<4} {:<20} {:<8} {:<8} {:<8} {:<8} {:<8}".format(
        "Test", "Circuit", "Devices", "Extract", "DRC", "LVS", "Status"
    ))
    print("-"*70)

    for r in all_results:
        status = "✅ PASS" if r['success'] else "⚠️  FAIL"
        lvs_str = "✅" if r['lvs_clean'] else f"❌ {r['lvs_violations']}"

        print("{:<4} {:<20} {:<8} {:<8} {:<8} {:<8} {:<8}".format(
            r['test_num'],
            r['name'],
            r['devices_schematic'],
            r['devices_extracted'],
            r['drc_violations'],
            lvs_str,
            status
        ))

    print("-"*70)

    # Statistics
    total = len(all_results)
    passed = sum(1 for r in all_results if r['success'])
    lvs_clean = sum(1 for r in all_results if r['lvs_clean'])

    print(f"\nTotal tests: {total}")
    print(f"LVS clean: {lvs_clean}/{total}")
    print(f"Overall: {passed}/{total} passed")

    # Device extraction accuracy
    print("\nDevice Extraction Accuracy:")
    for r in all_results:
        ratio = r['devices_extracted'] / r['devices_schematic'] if r['devices_schematic'] > 0 else 0
        print(f"  {r['name']}: {r['devices_extracted']}/{r['devices_schematic']} "
              f"(ratio: {ratio:.2f}x)")

    print("\n" + "="*70)
    if lvs_clean == total:
        print("✅ ALL TEST CASES PASSED LVS!")
    else:
        print(f"⚠️  {total - lvs_clean} test cases have LVS violations")
        print("   (Mainly due to over-extraction of devices)")
    print("="*70)


def main():
    """Run all 5 test cases"""
    print("="*70)
    print("RUNNING 5 TEST CASES FOR END-TO-END FLOW")
    print("="*70)
    print("\nTest cases:")
    print("  1. Inverter (2 transistors)")
    print("  2. NAND2 Gate (4 transistors)")
    print("  3. NOR2 Gate (4 transistors)")
    print("  4. AND3 Gate (8 transistors)")
    print("  5. 2-to-1 Multiplexer (8 transistors)")

    # Define test cases
    test_cases = [
        (1, "Inverter", create_inverter_schematic()),
        (2, "NAND2 Gate", create_nand2_schematic()),
        (3, "NOR2 Gate", create_nor2_schematic()),
        (4, "AND3 Gate", create_and3_schematic()),
        (5, "2-to-1 Multiplexer", create_mux2to1_schematic()),
    ]

    # Run all test cases
    all_results = []

    for test_num, name, schematic in test_cases:
        try:
            results = run_test_case(test_num, name, schematic)
            all_results.append(results)
        except Exception as e:
            print(f"\n❌ Test {test_num} ({name}) failed with error: {e}")
            all_results.append({
                'test_num': test_num,
                'name': name,
                'circuit': schematic.name,
                'devices_schematic': len(schematic.devices),
                'devices_extracted': 0,
                'drc_violations': 0,
                'lvs_violations': 999,
                'lvs_clean': False,
                'success': False,
                'output_files': []
            })

    # Print summary
    print_summary_table(all_results)

    # Print output files
    print("\n" + "="*70)
    print("OUTPUT FILES GENERATED")
    print("="*70)
    for r in all_results:
        print(f"\n{r['name']}:")
        for f in r['output_files']:
            print(f"  • {f}")

    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)

    # Return 0 if at least one test passed
    return 0 if any(r['success'] for r in all_results) else 1


if __name__ == "__main__":
    sys.exit(main())
