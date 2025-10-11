#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout vs Schematic (LVS) Verification

Provides verification that a layout matches its schematic by:
- Extracting netlist from layout (connectivity)
- Comparing with reference schematic netlist
- Verifying device parameters match (W, L for transistors)
- Checking all nets are properly connected
"""

from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict
import math


@dataclass
class Device:
    """
    Transistor or other device in circuit

    Attributes:
        name: Device name (e.g., 'M1', 'M2')
        device_type: Type ('nmos', 'pmos', 'resistor', 'capacitor')
        terminals: Dictionary mapping terminal name to net name
        parameters: Dictionary of device parameters (W, L, etc.)
    """
    name: str
    device_type: str
    terminals: Dict[str, str]  # e.g., {'g': 'A', 'd': 'X', 's': 'GND', 'b': 'GND'}
    parameters: Dict[str, float]  # e.g., {'W': 0.42, 'L': 0.15}


@dataclass
class Net:
    """
    Electrical net (connection)

    Attributes:
        name: Net name (e.g., 'VDD', 'GND', 'A', 'X')
        connections: List of (device_name, terminal) tuples connected to this net
    """
    name: str
    connections: List[Tuple[str, str]]


class Netlist:
    """
    Circuit netlist (schematic or extracted from layout)
    """

    def __init__(self, name: str = "circuit"):
        """
        Initialize netlist

        Args:
            name: Circuit name
        """
        self.name = name
        self.devices: Dict[str, Device] = {}  # device_name -> Device
        self.nets: Dict[str, Net] = {}  # net_name -> Net

    def add_device(self, device: Device):
        """Add a device to the netlist"""
        self.devices[device.name] = device

        # Update nets
        for terminal, net_name in device.terminals.items():
            if net_name not in self.nets:
                self.nets[net_name] = Net(net_name, [])
            self.nets[net_name].connections.append((device.name, terminal))

    def add_net(self, net: Net):
        """Add a net to the netlist"""
        self.nets[net.name] = net

    def get_device(self, name: str) -> Optional[Device]:
        """Get device by name"""
        return self.devices.get(name)

    def get_net(self, name: str) -> Optional[Net]:
        """Get net by name"""
        return self.nets.get(name)

    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """Get all devices of a specific type"""
        return [d for d in self.devices.values() if d.device_type == device_type]

    def print_summary(self):
        """Print netlist summary"""
        print(f"\nNetlist: {self.name}")
        print("=" * 70)
        print(f"Devices: {len(self.devices)}")

        device_counts = defaultdict(int)
        for device in self.devices.values():
            device_counts[device.device_type] += 1

        for dtype, count in sorted(device_counts.items()):
            print(f"  {dtype}: {count}")

        print(f"\nNets: {len(self.nets)}")
        for net_name, net in sorted(self.nets.items()):
            print(f"  {net_name}: {len(net.connections)} connections")


@dataclass
class LVSViolation:
    """
    LVS verification violation

    Attributes:
        violation_type: Type of violation ('device_count', 'device_parameter',
                       'connectivity', 'missing_device', 'extra_device')
        severity: 'error' or 'warning'
        message: Detailed violation message
        schematic_ref: Reference to schematic object (if applicable)
        layout_ref: Reference to layout object (if applicable)
    """
    violation_type: str
    severity: str
    message: str
    schematic_ref: Optional[str] = None
    layout_ref: Optional[str] = None


class LVSChecker:
    """
    Layout vs Schematic checker - verifies layout matches schematic
    """

    def __init__(self, schematic: Netlist, layout: Netlist,
                 parameter_tolerance: float = 0.01):
        """
        Initialize LVS checker

        Args:
            schematic: Reference schematic netlist
            layout: Extracted layout netlist
            parameter_tolerance: Tolerance for parameter matching (relative, e.g., 0.01 = 1%)
        """
        self.schematic = schematic
        self.layout = layout
        self.parameter_tolerance = parameter_tolerance
        self.violations: List[LVSViolation] = []

    def verify(self) -> List[LVSViolation]:
        """
        Run complete LVS verification

        Returns:
            List of LVSViolation objects
        """
        self.violations = []

        print("\nRunning LVS Verification...")
        print("=" * 70)

        # 1. Check device counts
        print("\n1. Checking device counts...")
        self._check_device_counts()

        # 2. Check device parameters
        print("2. Checking device parameters...")
        self._check_device_parameters()

        # 3. Check connectivity
        print("3. Checking connectivity...")
        self._check_connectivity()

        return self.violations

    def _check_device_counts(self):
        """Check that layout has same number and types of devices as schematic"""
        # Count devices by type in schematic
        sch_counts = defaultdict(int)
        for device in self.schematic.devices.values():
            sch_counts[device.device_type] += 1

        # Count devices by type in layout
        lay_counts = defaultdict(int)
        for device in self.layout.devices.values():
            lay_counts[device.device_type] += 1

        # Compare counts
        all_types = set(sch_counts.keys()) | set(lay_counts.keys())

        for device_type in all_types:
            sch_count = sch_counts.get(device_type, 0)
            lay_count = lay_counts.get(device_type, 0)

            if sch_count != lay_count:
                violation = LVSViolation(
                    violation_type='device_count',
                    severity='error',
                    message=f"Device count mismatch for {device_type}: "
                           f"schematic has {sch_count}, layout has {lay_count}",
                    schematic_ref=f"{device_type}_count={sch_count}",
                    layout_ref=f"{device_type}_count={lay_count}"
                )
                self.violations.append(violation)
                print(f"   ✗ {violation.message}")
            else:
                print(f"   ✓ {device_type}: {sch_count} devices match")

    def _check_device_parameters(self):
        """Check that device parameters (W, L, etc.) match"""
        # Try to match devices by name or topology
        matched_devices = self._match_devices()

        for sch_name, lay_name in matched_devices.items():
            sch_dev = self.schematic.get_device(sch_name)
            lay_dev = self.layout.get_device(lay_name)

            if not sch_dev or not lay_dev:
                continue

            # Check each parameter
            for param, sch_value in sch_dev.parameters.items():
                if param not in lay_dev.parameters:
                    violation = LVSViolation(
                        violation_type='device_parameter',
                        severity='error',
                        message=f"Device {sch_name} missing parameter {param} in layout",
                        schematic_ref=f"{sch_name}.{param}={sch_value}",
                        layout_ref=f"{lay_name}.{param}=missing"
                    )
                    self.violations.append(violation)
                    print(f"   ✗ {violation.message}")
                    continue

                lay_value = lay_dev.parameters[param]

                # Check if values match within tolerance
                if sch_value == 0:
                    if abs(lay_value) > self.parameter_tolerance:
                        mismatch = True
                    else:
                        mismatch = False
                else:
                    relative_error = abs(lay_value - sch_value) / abs(sch_value)
                    mismatch = relative_error > self.parameter_tolerance

                if mismatch:
                    violation = LVSViolation(
                        violation_type='device_parameter',
                        severity='error',
                        message=f"Device {sch_name} parameter {param} mismatch: "
                               f"schematic={sch_value:.6f}, layout={lay_value:.6f}",
                        schematic_ref=f"{sch_name}.{param}={sch_value}",
                        layout_ref=f"{lay_name}.{param}={lay_value}"
                    )
                    self.violations.append(violation)
                    print(f"   ✗ {violation.message}")
                else:
                    print(f"   ✓ {sch_name}.{param} matches ({sch_value:.6f})")

    def _check_connectivity(self):
        """Check that device connectivity matches"""
        matched_devices = self._match_devices()

        for sch_name, lay_name in matched_devices.items():
            sch_dev = self.schematic.get_device(sch_name)
            lay_dev = self.layout.get_device(lay_name)

            if not sch_dev or not lay_dev:
                continue

            # Check each terminal connection
            for terminal, sch_net in sch_dev.terminals.items():
                if terminal not in lay_dev.terminals:
                    violation = LVSViolation(
                        violation_type='connectivity',
                        severity='error',
                        message=f"Device {sch_name} terminal {terminal} not found in layout",
                        schematic_ref=f"{sch_name}.{terminal}={sch_net}",
                        layout_ref=f"{lay_name}.{terminal}=missing"
                    )
                    self.violations.append(violation)
                    print(f"   ✗ {violation.message}")
                    continue

                lay_net = lay_dev.terminals[terminal]

                # For now, simple name matching
                # (Real LVS would do topological net matching)
                if sch_net != lay_net:
                    violation = LVSViolation(
                        violation_type='connectivity',
                        severity='warning',
                        message=f"Device {sch_name} terminal {terminal} connectivity mismatch: "
                               f"schematic net '{sch_net}', layout net '{lay_net}'",
                        schematic_ref=f"{sch_name}.{terminal}={sch_net}",
                        layout_ref=f"{lay_name}.{terminal}={lay_net}"
                    )
                    self.violations.append(violation)
                    print(f"   ⚠ {violation.message}")
                else:
                    print(f"   ✓ {sch_name}.{terminal} → {sch_net}")

    def _match_devices(self) -> Dict[str, str]:
        """
        Match devices between schematic and layout

        Returns:
            Dictionary mapping schematic device names to layout device names
        """
        # For now, use simple name-based matching
        # Real LVS would use topological matching algorithms

        matched = {}

        # Try exact name matching first
        for sch_name in self.schematic.devices.keys():
            if sch_name in self.layout.devices:
                matched[sch_name] = sch_name

        return matched

    def print_violations(self):
        """Print all violations in human-readable format"""
        if not self.violations:
            print("\n" + "=" * 70)
            print("✓ LVS CLEAN - Layout matches schematic!")
            print("=" * 70)
            return

        print(f"\n{'='*70}")
        print(f"LVS VIOLATIONS FOUND: {len(self.violations)}")
        print(f"{'='*70}\n")

        errors = [v for v in self.violations if v.severity == 'error']
        warnings = [v for v in self.violations if v.severity == 'warning']

        if errors:
            print(f"ERRORS ({len(errors)}):")
            print("-" * 70)
            for i, v in enumerate(errors, 1):
                print(f"{i}. [{v.violation_type}] {v.message}")
                if v.schematic_ref:
                    print(f"   Schematic: {v.schematic_ref}")
                if v.layout_ref:
                    print(f"   Layout:    {v.layout_ref}")
                print()

        if warnings:
            print(f"WARNINGS ({len(warnings)}):")
            print("-" * 70)
            for i, v in enumerate(warnings, 1):
                print(f"{i}. [{v.violation_type}] {v.message}")
                if v.schematic_ref:
                    print(f"   Schematic: {v.schematic_ref}")
                if v.layout_ref:
                    print(f"   Layout:    {v.layout_ref}")
                print()

        print("=" * 70)
        if errors:
            print("❌ LVS FAILED - Errors must be fixed")
        else:
            print("⚠ LVS PASSED WITH WARNINGS - Review warnings")
        print("=" * 70)


def create_and3_schematic_netlist() -> Netlist:
    """
    Create reference schematic netlist for AND3 gate

    Circuit: X = A & B & C
    Implementation: NAND3 + Inverter

    NAND3:
      - 3 NMOS in series (A, B, C) from nand_out to GND
      - 3 PMOS in parallel (A, B, C) from VDD to nand_out

    Inverter:
      - 1 NMOS from X to GND (gate = nand_out)
      - 1 PMOS from VDD to X (gate = nand_out)

    Returns:
        Netlist with AND3 schematic
    """
    netlist = Netlist("AND3_schematic")

    # NAND3 NMOS devices (series stack: A->B->C from nand_out to GND)
    netlist.add_device(Device(
        name='NMOS_A',
        device_type='nmos',
        terminals={'g': 'A', 'd': 'nand_out', 's': 'n1', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='NMOS_B',
        device_type='nmos',
        terminals={'g': 'B', 'd': 'n1', 's': 'n2', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='NMOS_C',
        device_type='nmos',
        terminals={'g': 'C', 'd': 'n2', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    # NAND3 PMOS devices (parallel: all drains to nand_out, all sources to VDD)
    netlist.add_device(Device(
        name='PMOS_A',
        device_type='pmos',
        terminals={'g': 'A', 'd': 'nand_out', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='PMOS_B',
        device_type='pmos',
        terminals={'g': 'B', 'd': 'nand_out', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    netlist.add_device(Device(
        name='PMOS_C',
        device_type='pmos',
        terminals={'g': 'C', 'd': 'nand_out', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 0.42e-6, 'L': 0.15e-6}
    ))

    # Inverter NMOS
    netlist.add_device(Device(
        name='NMOS_INV',
        device_type='nmos',
        terminals={'g': 'nand_out', 'd': 'X', 's': 'GND', 'b': 'GND'},
        parameters={'W': 0.65e-6, 'L': 0.15e-6}
    ))

    # Inverter PMOS
    netlist.add_device(Device(
        name='PMOS_INV',
        device_type='pmos',
        terminals={'g': 'nand_out', 'd': 'X', 's': 'VDD', 'b': 'VDD'},
        parameters={'W': 1.0e-6, 'L': 0.15e-6}
    ))

    return netlist


def extract_netlist_from_layout(cell) -> Netlist:
    """
    Extract netlist from a Cell layout

    This is a simplified extractor that looks at MOSFET instances
    Real extraction would analyze polygon connectivity

    Args:
        cell: Cell object from gds_cell.py

    Returns:
        Netlist extracted from layout
    """
    netlist = Netlist(f"{cell.name}_extracted")

    # Extract devices from cell instances
    for instance in cell.instances:
        inst_name = instance.name.replace('_inst', '')
        cell_name = instance.cell.name

        # Determine device type
        if 'NMOS' in cell_name or 'nmos' in cell_name or 'nfet' in cell_name:
            device_type = 'nmos'
        elif 'PMOS' in cell_name or 'pmos' in cell_name or 'pfet' in cell_name:
            device_type = 'pmos'
        else:
            continue

        # Extract W and L from the MOSFET cell
        # This would need to parse the actual geometry
        # For now, use naming convention or metadata

        # Placeholder - real extraction would measure geometry
        # We'll assume the layout tool preserves the MOSFET object
        parameters = {'W': 0.0, 'L': 0.0}  # Would be extracted from geometry

        # Placeholder terminals - real extraction would trace connectivity
        terminals = {
            'g': 'unknown',
            'd': 'unknown',
            's': 'unknown',
            'b': 'unknown'
        }

        device = Device(
            name=inst_name,
            device_type=device_type,
            terminals=terminals,
            parameters=parameters
        )

        netlist.add_device(device)

    return netlist


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("LVS (Layout vs Schematic) Verification Example")
    print("=" * 70)

    # Create schematic netlist for AND3
    schematic = create_and3_schematic_netlist()
    schematic.print_summary()

    # Create a dummy layout netlist (would normally be extracted from GDS)
    layout = Netlist("AND3_layout")

    # Add same devices as schematic (perfect match case)
    for device in schematic.devices.values():
        layout.add_device(Device(
            name=device.name,
            device_type=device.device_type,
            terminals=dict(device.terminals),
            parameters=dict(device.parameters)
        ))

    layout.print_summary()

    # Run LVS
    lvs = LVSChecker(schematic, layout)
    violations = lvs.verify()
    lvs.print_violations()

    print("\n" + "=" * 70)
    print("LVS verification complete")
    print("=" * 70)
