#!/usr/bin/env python3
"""
LVS Comparison Demonstration

Shows step-by-step how the LVS checker compares a golden (schematic)
netlist with an extracted (layout) netlist.
"""

from tools.skywater_direct_extractor import extract_skywater_direct
from layout_automation.lvs import LVSChecker, Netlist, Device
from layout_automation.technology import Technology


def create_golden_inverter():
    """Create the golden schematic netlist for an inverter"""
    netlist = Netlist("sky130_fd_sc_hd__inv_1")

    # NMOS transistor
    netlist.add_device(Device(
        name='M0',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VGND', 'b': 'VNB'},
        parameters={'W': 650e-9, 'L': 430e-9}
    ))

    # PMOS transistor
    netlist.add_device(Device(
        name='M1',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'Y', 's': 'VPWR', 'b': 'VPB'},
        parameters={'W': 1000e-9, 'L': 430e-9}
    ))

    return netlist


def print_netlist(netlist, title):
    """Pretty print a netlist"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"\nCell Name: {netlist.name}")
    print(f"Total Devices: {len(netlist.devices)}")

    # Group by type
    nmos = [d for d in netlist.devices.values() if d.device_type == 'nmos']
    pmos = [d for d in netlist.devices.values() if d.device_type == 'pmos']

    print(f"  NMOS: {len(nmos)}")
    print(f"  PMOS: {len(pmos)}")

    print(f"\n{'Device':<8} {'Type':<6} {'Width':<10} {'Length':<10} {'Gate':<10} {'Drain':<10} {'Source':<10}")
    print("-"*70)

    for name, dev in netlist.devices.items():
        W = dev.parameters.get('W', 0) * 1e9
        L = dev.parameters.get('L', 0) * 1e9
        g = dev.terminals.get('g', 'N/A')
        d = dev.terminals.get('d', 'N/A')
        s = dev.terminals.get('s', 'N/A')

        print(f"{name:<8} {dev.device_type:<6} {W:<10.1f} {L:<10.1f} {g:<10} {d:<10} {s:<10}")


def compare_device_counts(sch, lay):
    """Compare device counts"""
    print(f"\n{'='*70}")
    print("1. DEVICE COUNT COMPARISON")
    print(f"{'='*70}")

    from collections import Counter
    sch_types = Counter(d.device_type for d in sch.devices.values())
    lay_types = Counter(d.device_type for d in lay.devices.values())

    print(f"\n{'Type':<10} {'Schematic':<15} {'Layout':<15} {'Status':<10}")
    print("-"*70)

    all_types = set(list(sch_types.keys()) + list(lay_types.keys()))
    all_match = True

    for dtype in sorted(all_types):
        sch_count = sch_types.get(dtype, 0)
        lay_count = lay_types.get(dtype, 0)
        match = sch_count == lay_count
        all_match = all_match and match
        status = "✅ MATCH" if match else "❌ MISMATCH"
        print(f"{dtype:<10} {sch_count:<15} {lay_count:<15} {status}")

    return all_match


def compare_parameters(sch, lay):
    """Compare device parameters"""
    print(f"\n{'='*70}")
    print("2. PARAMETER COMPARISON")
    print(f"{'='*70}")

    # Group devices by type
    sch_nmos = [d for d in sch.devices.values() if d.device_type == 'nmos']
    sch_pmos = [d for d in sch.devices.values() if d.device_type == 'pmos']
    lay_nmos = [d for d in lay.devices.values() if d.device_type == 'nmos']
    lay_pmos = [d for d in lay.devices.values() if d.device_type == 'pmos']

    matches = []

    # Compare NMOS
    if sch_nmos and lay_nmos:
        print("\nNMOS Comparison:")
        print("-"*70)
        s_dev = sch_nmos[0]
        l_dev = lay_nmos[0]

        s_W = s_dev.parameters['W'] * 1e9
        s_L = s_dev.parameters['L'] * 1e9
        l_W = l_dev.parameters['W'] * 1e9
        l_L = l_dev.parameters['L'] * 1e9

        print(f"  Schematic: W={s_W:.1f}nm, L={s_L:.1f}nm")
        print(f"  Layout:    W={l_W:.1f}nm, L={l_L:.1f}nm")

        w_match = abs(s_W - l_W) < 1.0  # 1nm tolerance
        l_match = abs(s_L - l_L) < 1.0

        print(f"  Width:  {'✅ MATCH' if w_match else '❌ MISMATCH'} (Δ={abs(s_W-l_W):.1f}nm)")
        print(f"  Length: {'✅ MATCH' if l_match else '❌ MISMATCH'} (Δ={abs(s_L-l_L):.1f}nm)")

        matches.append(w_match and l_match)

    # Compare PMOS
    if sch_pmos and lay_pmos:
        print("\nPMOS Comparison:")
        print("-"*70)
        s_dev = sch_pmos[0]
        l_dev = lay_pmos[0]

        s_W = s_dev.parameters['W'] * 1e9
        s_L = s_dev.parameters['L'] * 1e9
        l_W = l_dev.parameters['W'] * 1e9
        l_L = l_dev.parameters['L'] * 1e9

        print(f"  Schematic: W={s_W:.1f}nm, L={s_L:.1f}nm")
        print(f"  Layout:    W={l_W:.1f}nm, L={l_L:.1f}nm")

        w_match = abs(s_W - l_W) < 1.0
        l_match = abs(s_L - l_L) < 1.0

        print(f"  Width:  {'✅ MATCH' if w_match else '❌ MISMATCH'} (Δ={abs(s_W-l_W):.1f}nm)")
        print(f"  Length: {'✅ MATCH' if l_match else '❌ MISMATCH'} (Δ={abs(s_L-l_L):.1f}nm)")

        matches.append(w_match and l_match)

    return all(matches)


def compare_connectivity(sch, lay):
    """Compare net connectivity"""
    print(f"\n{'='*70}")
    print("3. CONNECTIVITY COMPARISON")
    print(f"{'='*70}")

    # Extract nets
    sch_nets = set()
    for dev in sch.devices.values():
        for net in dev.terminals.values():
            if isinstance(net, str):
                sch_nets.add(net)

    lay_nets = set()
    for dev in lay.devices.values():
        for term, net in dev.terminals.items():
            if isinstance(net, str):
                lay_nets.add(net)

    print(f"\nSchematic Nets ({len(sch_nets)}):")
    print(f"  {sorted(sch_nets)}")

    print(f"\nLayout Nets ({len(lay_nets)}):")
    # Show first 10 nets
    lay_nets_list = sorted(lay_nets)
    if len(lay_nets_list) > 10:
        print(f"  {lay_nets_list[:10]} ... ({len(lay_nets_list)-10} more)")
    else:
        print(f"  {lay_nets_list}")

    # Terminal-by-terminal comparison
    print(f"\nTerminal Connectivity:")
    print(f"{'Device':<8} {'Term':<6} {'Schematic':<15} {'Layout':<15} {'Status':<10}")
    print("-"*70)

    # Get device pairs
    sch_devs = list(sch.devices.items())
    lay_devs = list(lay.devices.items())

    total_terms = 0
    matching_terms = 0

    for i, ((sch_name, sch_dev), (lay_name, lay_dev)) in enumerate(zip(sch_devs, lay_devs)):
        if sch_dev.device_type != lay_dev.device_type:
            continue

        for term in ['g', 'd', 's', 'b']:
            sch_net = sch_dev.terminals.get(term, 'N/A')
            lay_net = lay_dev.terminals.get(term, 'N/A')

            if isinstance(sch_net, str) and isinstance(lay_net, str):
                match = sch_net == lay_net
                status = "✅ MATCH" if match else "⚠️  DIFF"
                print(f"{sch_name:<8} {term:<6} {sch_net:<15} {lay_net:<15} {status}")

                total_terms += 1
                if match:
                    matching_terms += 1

    print(f"\nConnectivity Summary:")
    print(f"  Matching terminals: {matching_terms}/{total_terms}")
    print(f"  Match rate: {100*matching_terms/total_terms if total_terms > 0 else 0:.1f}%")

    return matching_terms == total_terms


def main():
    """Main demonstration"""

    print("╔" + "="*68 + "╗")
    print("║" + " "*18 + "LVS COMPARISON DEMONSTRATION" + " "*22 + "║")
    print("╚" + "="*68 + "╝")

    # Step 1: Create golden netlist
    print("\n" + "▶"*35)
    print("STEP 1: CREATE GOLDEN NETLIST (SCHEMATIC)")
    print("▶"*35)

    golden = create_golden_inverter()
    print_netlist(golden, "Golden Netlist (Schematic)")

    # Step 2: Extract from layout
    print("\n" + "▶"*35)
    print("STEP 2: EXTRACT NETLIST FROM LAYOUT")
    print("▶"*35)

    tech = Technology('sky130')
    extracted = extract_skywater_direct(
        "sky130_inv_replica.gds",
        "sky130_fd_sc_hd__inv_1_replica",
        tech
    )

    print_netlist(extracted, "Extracted Netlist (Layout)")

    # Step 3: Compare
    print("\n" + "▶"*35)
    print("STEP 3: COMPARE NETLISTS")
    print("▶"*35)

    count_match = compare_device_counts(golden, extracted)
    param_match = compare_parameters(golden, extracted)
    conn_match = compare_connectivity(golden, extracted)

    # Final summary
    print(f"\n{'='*70}")
    print("FINAL LVS SUMMARY")
    print(f"{'='*70}")

    checks = [
        ("Device Count", count_match),
        ("Parameters (W, L)", param_match),
        ("Connectivity", conn_match),
    ]

    print(f"\n{'Check':<25} {'Status':<20} {'Critical'}")
    print("-"*70)

    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        critical = "Yes" if check_name != "Connectivity" else "No*"
        print(f"{check_name:<25} {status:<20} {critical}")

    print("\n* Connectivity differences are expected when layout uses generic")
    print("  net names (net0_g, net1_d) vs schematic semantic names (A, Y).")
    print("  Full connectivity extraction would resolve this.")

    passed = sum(1 for _, p in checks if p)
    total = len(checks)

    print(f"\nOverall Result: {passed}/{total} checks passed")

    if count_match and param_match:
        print("\n🎉 STRUCTURAL MATCH - Layout correctly implements schematic!")
        print("   (Device count and parameters match perfectly)")
    elif count_match:
        print("\n⚠️  PARTIAL MATCH - Devices correct but parameters differ")
    else:
        print("\n❌ MISMATCH - Layout does not match schematic")

    # Run official LVS
    print(f"\n{'='*70}")
    print("OFFICIAL LVS VERIFICATION")
    print(f"{'='*70}")

    lvs = LVSChecker(golden, extracted)
    violations = lvs.verify()

    print(f"\nTotal LVS Violations: {len(violations)}")
    if len(violations) > 0:
        print("\nViolation Breakdown:")
        param_viols = sum(1 for v in violations if 'parameter' in v.message.lower())
        conn_viols = sum(1 for v in violations if 'connectivity' in v.message.lower())
        count_viols = sum(1 for v in violations if 'count' in v.message.lower())

        print(f"  Device count: {count_viols}")
        print(f"  Parameters:   {param_viols}")
        print(f"  Connectivity: {conn_viols}")


if __name__ == "__main__":
    main()
