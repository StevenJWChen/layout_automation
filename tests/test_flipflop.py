#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Case: D Flip-Flop
Complete end-to-end verification flow
"""

from layout_automation.lvs import Netlist, Device
from layout_automation.layout_from_schematic import LayoutGenerator
from layout_automation.drc_improved import run_improved_drc
from tools.netlist_extractor_improved import extract_improved_netlist
from layout_automation.lvs import LVSChecker
from layout_automation.technology import Technology
from layout_automation.units import to_um


def create_dff_schematic() -> Netlist:
    """
    D Flip-Flop (positive edge-triggered)

    Architecture: Master-Slave with transmission gates
    - Master latch (active when CLK=0)
    - Slave latch (active when CLK=1)
    - Clock inverter
    - Output buffer

    Total: ~20 transistors
    """
    netlist = Netlist("DFF")

    # Clock inverter
    netlist.add_device(Device(
        name='M_CLK_INV_N',
        device_type='nmos',
        terminals={'g': 'CLK', 'd': 'CLK_B', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_CLK_INV_P',
        device_type='pmos',
        terminals={'g': 'CLK', 'd': 'CLK_B', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Master latch - input transmission gate (passes when CLK=0)
    netlist.add_device(Device(
        name='M_MASTER_TG_N',
        device_type='nmos',
        terminals={'g': 'CLK_B', 'd': 'D', 's': 'MASTER', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_MASTER_TG_P',
        device_type='pmos',
        terminals={'g': 'CLK', 'd': 'D', 's': 'MASTER', 'b': 'VDD'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Master latch - inverter (storage element)
    netlist.add_device(Device(
        name='M_MASTER_INV1_N',
        device_type='nmos',
        terminals={'g': 'MASTER', 'd': 'MASTER_B', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_MASTER_INV1_P',
        device_type='pmos',
        terminals={'g': 'MASTER', 'd': 'MASTER_B', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Master latch - feedback inverter (weak keeper)
    netlist.add_device(Device(
        name='M_MASTER_INV2_N',
        device_type='nmos',
        terminals={'g': 'MASTER_B', 'd': 'MASTER', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.30e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_MASTER_INV2_P',
        device_type='pmos',
        terminals={'g': 'MASTER_B', 'd': 'MASTER', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    # Slave latch - input transmission gate (passes when CLK=1)
    netlist.add_device(Device(
        name='M_SLAVE_TG_N',
        device_type='nmos',
        terminals={'g': 'CLK', 'd': 'MASTER_B', 's': 'SLAVE', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_SLAVE_TG_P',
        device_type='pmos',
        terminals={'g': 'CLK_B', 'd': 'MASTER_B', 's': 'SLAVE', 'b': 'VDD'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Slave latch - inverter (storage element)
    netlist.add_device(Device(
        name='M_SLAVE_INV1_N',
        device_type='nmos',
        terminals={'g': 'SLAVE', 'd': 'SLAVE_B', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_SLAVE_INV1_P',
        device_type='pmos',
        terminals={'g': 'SLAVE', 'd': 'SLAVE_B', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Slave latch - feedback inverter (weak keeper)
    netlist.add_device(Device(
        name='M_SLAVE_INV2_N',
        device_type='nmos',
        terminals={'g': 'SLAVE_B', 'd': 'SLAVE', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.30e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_SLAVE_INV2_P',
        device_type='pmos',
        terminals={'g': 'SLAVE_B', 'd': 'SLAVE', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    # Output buffer
    netlist.add_device(Device(
        name='M_OUT_N',
        device_type='nmos',
        terminals={'g': 'SLAVE_B', 'd': 'Q', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))
    netlist.add_device(Device(
        name='M_OUT_P',
        device_type='pmos',
        terminals={'g': 'SLAVE_B', 'd': 'Q', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.00e-6, 'L': 0.15e-6}
    ))

    return netlist


def main():
    """Run complete verification flow for D flip-flop"""

    print("="*70)
    print("D FLIP-FLOP - COMPLETE VERIFICATION FLOW")
    print("="*70)
    print("\nArchitecture: Master-Slave with Transmission Gates")
    print("  • Master latch (2 TG + 2 inverters)")
    print("  • Slave latch (2 TG + 2 inverters)")
    print("  • Clock inverter + Output buffer")
    print("  • Total: 16 transistors\n")

    # Initialize
    tech = Technology('sky130')
    schematic = create_dff_schematic()

    print(f"Schematic created: {schematic.name}")
    print(f"  Devices: {len(schematic.devices)}")

    # Count device types
    nmos_count = sum(1 for d in schematic.devices.values() if d.device_type == 'nmos')
    pmos_count = sum(1 for d in schematic.devices.values() if d.device_type == 'pmos')
    print(f"  NMOS: {nmos_count}, PMOS: {pmos_count}")

    # List all devices
    print("\nDevice List:")
    for i, (name, dev) in enumerate(schematic.devices.items(), 1):
        w = dev.parameters.get('W', 0)
        l = dev.parameters.get('L', 0)
        print(f"  {i:2d}. {dev.name:20s} {dev.device_type:4s} "
              f"W={w*1e6:.2f}μm L={l*1e6:.2f}μm")

    # ==================================================================
    # STEP 1: GENERATE LAYOUT
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 1: GENERATE LAYOUT FROM NETLIST")
    print("="*70)

    try:
        generator = LayoutGenerator(schematic, tech)
        layout_cell = generator.generate()

        # Export GDS
        gds_file = "dff_test.gds"
        layout_cell.export_gds(gds_file)

        print(f"✅ Layout generated successfully")
        print(f"   Cell name: {layout_cell.name}")
        print(f"   Exported to: {gds_file}")

        # Count polygons
        total_polys = len(layout_cell.polygons)
        total_instances = len(layout_cell.instances)
        print(f"   Polygons: {total_polys}")
        print(f"   Instances: {total_instances}")

    except Exception as e:
        print(f"❌ Layout generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==================================================================
    # STEP 2: RUN DRC VERIFICATION
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 2: RUN DRC VERIFICATION (IMPROVED)")
    print("="*70)

    try:
        violations, checker = run_improved_drc(layout_cell, tech)

        print(f"\nDRC Results:")
        print(f"  Total violations: {len(violations)}")

        if len(violations) == 0:
            print("  ✅ DRC CLEAN - No violations!")
        else:
            print(f"  ❌ DRC FAILED - {len(violations)} violations")

            # Categorize violations
            width_viol = sum(1 for v in violations if 'Width' in v.message)
            spacing_viol = sum(1 for v in violations if 'Spacing' in v.message)
            area_viol = sum(1 for v in violations if 'Area' in v.message)

            print(f"\n  Breakdown:")
            print(f"    Width violations: {width_viol}")
            print(f"    Spacing violations: {spacing_viol}")
            print(f"    Area violations: {area_viol}")

            # Show first 10 violations
            print(f"\n  First 10 violations:")
            for i, v in enumerate(violations[:10], 1):
                print(f"    {i:2d}. {v.message}")

            if len(violations) > 10:
                print(f"    ... and {len(violations) - 10} more")

        # Save violations to file
        violations_file = "dff_drc_violations.txt"
        with open(violations_file, 'w') as f:
            f.write(f"DRC Violations for {layout_cell.name}\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total violations: {len(violations)}\n\n")
            for i, v in enumerate(violations, 1):
                f.write(f"{i}. {v.message}\n")
                f.write(f"   Rule: {v.rule.description}\n")
                f.write(f"   Location: ({v.location[0]:.2f}, {v.location[1]:.2f})\n\n")

        print(f"\n  Saved detailed violations to: {violations_file}")

    except Exception as e:
        print(f"❌ DRC check failed: {e}")
        import traceback
        traceback.print_exc()

    # ==================================================================
    # STEP 3: EXTRACT NETLIST FROM LAYOUT
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 3: EXTRACT NETLIST FROM LAYOUT (IMPROVED)")
    print("="*70)

    try:
        extracted_netlist = extract_improved_netlist(layout_cell, tech)

        print(f"\nExtraction Results:")
        print(f"  Devices extracted: {len(extracted_netlist.devices)}")
        print(f"  Devices expected: {len(schematic.devices)}")

        # Count extracted device types
        extracted_nmos = sum(1 for d in extracted_netlist.devices.values() if d.device_type == 'nmos')
        extracted_pmos = sum(1 for d in extracted_netlist.devices.values() if d.device_type == 'pmos')

        print(f"  Extracted NMOS: {extracted_nmos} (expected {nmos_count})")
        print(f"  Extracted PMOS: {extracted_pmos} (expected {pmos_count})")

        # Check accuracy
        if len(extracted_netlist.devices) == len(schematic.devices):
            print("  ✅ Device count matches!")
        else:
            ratio = len(extracted_netlist.devices) / len(schematic.devices)
            print(f"  ❌ Device count mismatch (ratio: {ratio:.2f}x)")

        # Save extracted netlist
        netlist_file = "dff_extracted.txt"
        with open(netlist_file, 'w') as f:
            f.write(f"Extracted Netlist: {extracted_netlist.name}\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total Devices: {len(extracted_netlist.devices)}\n")
            f.write(f"  NMOS: {extracted_nmos}\n")
            f.write(f"  PMOS: {extracted_pmos}\n\n")

            f.write("Device List:\n")
            f.write("-"*70 + "\n")
            for i, (name, dev) in enumerate(extracted_netlist.devices.items(), 1):
                w = dev.parameters.get('W', 0)
                l = dev.parameters.get('L', 0)
                f.write(f"{i:2d}. {dev.name}\n")
                f.write(f"    Type: {dev.device_type}\n")
                f.write(f"    W={w:.0f}nm, L={l:.0f}nm\n")
                f.write(f"    Terminals: {dev.terminals}\n\n")

        print(f"\n  Saved extracted netlist to: {netlist_file}")

    except Exception as e:
        print(f"❌ Netlist extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==================================================================
    # STEP 4: COMPARE WITH ORIGINAL NETLIST (LVS)
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 4: COMPARE WITH ORIGINAL NETLIST (LVS)")
    print("="*70)

    try:
        lvs_checker = LVSChecker(schematic, extracted_netlist)
        lvs_violations = lvs_checker.verify()

        print(f"\nLVS Results:")
        print(f"  Total violations: {len(lvs_violations)}")

        if len(lvs_violations) == 0:
            print("  ✅ LVS PASSED - Netlists match!")
        else:
            print(f"  ❌ LVS FAILED - {len(lvs_violations)} violations")

            # Categorize violations
            count_viol = sum(1 for v in lvs_violations if 'count' in v.message.lower())
            param_viol = sum(1 for v in lvs_violations if 'parameter' in v.message.lower())
            conn_viol = sum(1 for v in lvs_violations if 'connectivity' in v.message.lower())

            print(f"\n  Breakdown:")
            print(f"    Device count violations: {count_viol}")
            print(f"    Parameter violations: {param_viol}")
            print(f"    Connectivity violations: {conn_viol}")

            # Show first 15 violations
            print(f"\n  First 15 violations:")
            for i, v in enumerate(lvs_violations[:15], 1):
                print(f"    {i:2d}. {v.message}")

            if len(lvs_violations) > 15:
                print(f"    ... and {len(lvs_violations) - 15} more")

        # Save LVS report
        lvs_file = "dff_lvs_report.txt"
        with open(lvs_file, 'w') as f:
            f.write(f"LVS Report for {layout_cell.name}\n")
            f.write("="*70 + "\n\n")
            f.write(f"Schematic: {schematic.name} ({len(schematic.devices)} devices)\n")
            f.write(f"Layout:    {extracted_netlist.name} ({len(extracted_netlist.devices)} devices)\n\n")
            f.write(f"Total violations: {len(lvs_violations)}\n\n")

            if len(lvs_violations) == 0:
                f.write("✅ LVS CLEAN - Netlists match!\n")
            else:
                f.write("Violations:\n")
                f.write("-"*70 + "\n")
                for i, v in enumerate(lvs_violations, 1):
                    f.write(f"{i}. {v.message}\n")
                    f.write(f"   Severity: {v.severity}\n\n")

        print(f"\n  Saved LVS report to: {lvs_file}")

    except Exception as e:
        print(f"❌ LVS verification failed: {e}")
        import traceback
        traceback.print_exc()

    # ==================================================================
    # FINAL SUMMARY
    # ==================================================================
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    step1_pass = True  # Layout was generated
    step2_pass = len(violations) == 0 if 'violations' in locals() else False
    step3_pass = (len(extracted_netlist.devices) == len(schematic.devices)) if 'extracted_netlist' in locals() else False
    step4_pass = (len(lvs_violations) == 0) if 'lvs_violations' in locals() else False

    print(f"\n  Step 1 - Layout Generation:    {'✅ PASS' if step1_pass else '❌ FAIL'}")
    print(f"  Step 2 - DRC Verification:     {'✅ PASS' if step2_pass else '❌ FAIL'}")
    print(f"  Step 3 - Netlist Extraction:   {'✅ PASS' if step3_pass else '❌ FAIL'}")
    print(f"  Step 4 - LVS Comparison:       {'✅ PASS' if step4_pass else '❌ FAIL'}")

    all_pass = step1_pass and step2_pass and step3_pass and step4_pass

    print(f"\n  Overall Result: {'✅ ALL STEPS PASSED' if all_pass else '⚠️  SOME STEPS FAILED'}")

    print("\n" + "="*70)
    print("Files Generated:")
    print("  • dff_test.gds - Layout file")
    print("  • dff_drc_violations.txt - DRC violations")
    print("  • dff_extracted.txt - Extracted netlist")
    print("  • dff_lvs_report.txt - LVS comparison")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
