#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout Generation from Schematic

Automatically generates physical layout from a schematic netlist.

Flow:
1. Read schematic netlist (devices and connectivity)
2. Generate transistor layouts
3. Place transistors based on topology
4. Route connections (power, ground, signals)
5. Return complete Cell with layout

This implements automatic place-and-route from netlist.
"""

from typing import Dict, List, Tuple, Optional
from .lvs import Netlist, Device
from .mosfet import MOSFET
from .gds_cell import Cell, CellInstance, Polygon
from .technology import Technology, create_sky130_tech
from .units import nm, um, to_um


class LayoutGenerator:
    """
    Automatic layout generator from schematic netlist

    Takes a Netlist and generates a physical Cell layout
    """

    def __init__(self, netlist: Netlist, technology: Technology):
        """
        Initialize layout generator

        Args:
            netlist: Schematic netlist to implement
            technology: Technology object (e.g., SKY130)
        """
        self.netlist = netlist
        self.tech = technology
        self.cell = Cell(f"{netlist.name}_layout")
        self.instances: Dict[str, CellInstance] = {}
        self.device_cells: Dict[str, Cell] = {}

    def generate(self) -> Cell:
        """
        Generate complete layout from netlist

        Returns:
            Cell with complete layout
        """
        print(f"\n{'='*70}")
        print(f"GENERATING LAYOUT FROM SCHEMATIC: {self.netlist.name}")
        print(f"{'='*70}")

        # Step 1: Analyze netlist topology
        print("\n1. Analyzing circuit topology...")
        topology = self._analyze_topology()

        # Step 2: Generate transistor cells
        print("\n2. Generating transistor layouts...")
        self._generate_transistor_cells()

        # Step 3: Place transistors
        print("\n3. Placing transistors...")
        self._place_transistors(topology)

        # Step 4: Route connections
        print("\n4. Routing connections...")
        self._route_connections(topology)

        # Step 5: Add power distribution
        print("\n5. Adding power distribution...")
        self._add_power_distribution(topology)

        # Step 6: Solve constraints
        print("\n6. Solving layout constraints...")
        if not self.cell.solver():
            print("   ✗ Layout solving failed!")
            return None
        print("   ✓ Layout solved successfully")

        # Print summary
        self._print_summary()

        return self.cell

    def _analyze_topology(self) -> Dict:
        """
        Analyze circuit topology to determine placement strategy

        Returns:
            Dictionary with topology information
        """
        topology = {
            'nmos_devices': [],
            'pmos_devices': [],
            'nmos_series': [],  # Series-connected NMOS
            'pmos_parallel': [],  # Parallel-connected PMOS
            'nets': set(),
            'inputs': set(),
            'outputs': set(),
            'power_nets': {'VDD', 'GND', 'vdd', 'gnd', 'VSS', 'vss'}
        }

        # Categorize devices
        for dev_name, device in self.netlist.devices.items():
            if device.device_type == 'nmos':
                topology['nmos_devices'].append(device)
            elif device.device_type == 'pmos':
                topology['pmos_devices'].append(device)

        # Find series NMOS chains (for NAND gates, etc.)
        topology['nmos_series'] = self._find_series_chain(topology['nmos_devices'])

        # Find parallel PMOS (for NAND gates, etc.)
        topology['pmos_parallel'] = self._find_parallel_devices(topology['pmos_devices'])

        # Identify signal nets
        for net_name in self.netlist.nets.keys():
            if net_name not in topology['power_nets']:
                topology['nets'].add(net_name)

        # Identify inputs and outputs (heuristic: connected to few devices)
        for net_name in topology['nets']:
            net = self.netlist.nets[net_name]
            # If connected to gates only, likely an input
            if all(term == 'g' for _, term in net.connections):
                topology['inputs'].add(net_name)
            # If connected to drains, could be output
            elif any(term == 'd' for _, term in net.connections):
                if len(net.connections) <= 2:  # Not many connections
                    topology['outputs'].add(net_name)

        print(f"   NMOS devices: {len(topology['nmos_devices'])}")
        print(f"   PMOS devices: {len(topology['pmos_devices'])}")
        print(f"   Series NMOS chains: {len(topology['nmos_series'])}")
        print(f"   Parallel PMOS groups: {len(topology['pmos_parallel'])}")
        print(f"   Inputs: {topology['inputs']}")
        print(f"   Outputs: {topology['outputs']}")

        return topology

    def _find_series_chain(self, devices: List[Device]) -> List[List[Device]]:
        """Find series-connected devices (drain-to-source chains)"""
        chains = []
        used = set()

        for start_dev in devices:
            if start_dev.name in used:
                continue

            # Build chain starting from this device
            chain = [start_dev]
            used.add(start_dev.name)

            # Look for device whose source connects to this drain
            current = start_dev
            while True:
                drain_net = current.terminals.get('d')
                if not drain_net:
                    break

                # Find device with source on this net
                next_dev = None
                for dev in devices:
                    if dev.name not in used and dev.terminals.get('s') == drain_net:
                        next_dev = dev
                        break

                if next_dev:
                    chain.append(next_dev)
                    used.add(next_dev.name)
                    current = next_dev
                else:
                    break

            if len(chain) > 1:
                chains.append(chain)

        return chains

    def _find_parallel_devices(self, devices: List[Device]) -> List[List[Device]]:
        """Find parallel-connected devices (same source and drain nets)"""
        groups = []
        used = set()

        for dev1 in devices:
            if dev1.name in used:
                continue

            group = [dev1]
            used.add(dev1.name)

            # Find other devices with same source and drain
            s_net = dev1.terminals.get('s')
            d_net = dev1.terminals.get('d')

            for dev2 in devices:
                if dev2.name not in used:
                    if (dev2.terminals.get('s') == s_net and
                        dev2.terminals.get('d') == d_net):
                        group.append(dev2)
                        used.add(dev2.name)

            if len(group) > 1:
                groups.append(group)

        return groups

    def _generate_transistor_cells(self):
        """Generate physical layout for each transistor"""
        for dev_name, device in self.netlist.devices.items():
            if device.device_type not in ['nmos', 'pmos']:
                continue

            # Get device parameters
            width = device.parameters.get('W', 0.42e-6)
            length = device.parameters.get('L', 0.15e-6)

            # Create MOSFET (use device_type directly, MOSFET accepts nmos/pmos)
            mosfet = MOSFET(
                name=dev_name,
                device_type=device.device_type,  # nmos or pmos
                width=int(width),  # Convert to int (DBU)
                length=int(length),
                technology=self.tech
            )

            # Generate cell
            cell = mosfet.generate()
            self.device_cells[dev_name] = cell

            # Create instance
            instance = CellInstance(f"{dev_name}_inst", cell)
            self.instances[dev_name] = instance
            self.cell.add_instance(instance)

            print(f"   Generated {dev_name}: {device.device_type}, "
                  f"W={width*1e6:.2f}μm, L={length*1e6:.2f}μm")

    def _place_transistors(self, topology: Dict):
        """
        Place transistors based on topology

        Strategy:
        - NMOS in series: stack vertically
        - PMOS in parallel: place horizontally
        - Inverters: NMOS below, PMOS above
        """
        nmos_y = nm(500)  # Starting Y for NMOS
        pmos_y = nm(3800)  # Starting Y for PMOS
        spacing_x = nm(1000)  # Horizontal spacing
        spacing_y = nm(800)   # Vertical spacing

        # Place series NMOS chains (stack vertically)
        current_x = nm(500)
        for chain in topology['nmos_series']:
            y_pos = nmos_y
            for device in chain:
                inst = self.instances[device.name]
                self.cell.constrain(inst, f'x1={current_x}, y1={y_pos}')
                y_pos += spacing_y
                print(f"   Placed {device.name} at ({to_um(current_x):.2f}, {to_um(y_pos-spacing_y):.2f}) μm")
            current_x += spacing_x

        # Place standalone NMOS (not in series)
        placed = set()
        for chain in topology['nmos_series']:
            placed.update(dev.name for dev in chain)

        for device in topology['nmos_devices']:
            if device.name not in placed:
                inst = self.instances[device.name]
                self.cell.constrain(inst, f'x1={current_x}, y1={nmos_y}')
                print(f"   Placed {device.name} at ({to_um(current_x):.2f}, {to_um(nmos_y):.2f}) μm")
                current_x += spacing_x

        # Place parallel PMOS groups (horizontal)
        current_x = nm(500)
        for group in topology['pmos_parallel']:
            x_pos = current_x
            for device in group:
                inst = self.instances[device.name]
                self.cell.constrain(inst, f'x1={x_pos}, y1={pmos_y}')
                print(f"   Placed {device.name} at ({to_um(x_pos):.2f}, {to_um(pmos_y):.2f}) μm")
                x_pos += spacing_x
            current_x = x_pos + spacing_x

        # Place standalone PMOS
        placed = set()
        for group in topology['pmos_parallel']:
            placed.update(dev.name for dev in group)

        for device in topology['pmos_devices']:
            if device.name not in placed:
                inst = self.instances[device.name]
                self.cell.constrain(inst, f'x1={current_x}, y1={pmos_y}')
                print(f"   Placed {device.name} at ({to_um(current_x):.2f}, {to_um(pmos_y):.2f}) μm")
                current_x += spacing_x

    def _route_connections(self, topology: Dict):
        """Route signal connections"""
        # Route inputs (vertical stripes)
        x_pos = nm(200)
        for input_net in sorted(topology['inputs']):
            route = Polygon(f'route_input_{input_net}', 'li1')
            route.pos_list = [x_pos, nm(400), x_pos + nm(100), nm(4500)]
            self.cell.add_polygon(route)
            print(f"   Routed input {input_net} at X={to_um(x_pos):.2f} μm")
            x_pos += nm(150)

        # Route outputs (vertical stripes on right)
        x_pos = nm(4500)
        for output_net in sorted(topology['outputs']):
            route = Polygon(f'route_output_{output_net}', 'li1')
            route.pos_list = [x_pos, nm(500), x_pos + nm(150), nm(4500)]
            self.cell.add_polygon(route)
            print(f"   Routed output {output_net} at X={to_um(x_pos):.2f} μm")
            x_pos += nm(200)

        # Route intermediate nets (horizontal connections)
        internal_nets = topology['nets'] - topology['inputs'] - topology['outputs']
        y_pos = nm(2900)
        for net in internal_nets:
            if net not in topology['power_nets']:
                route = Polygon(f'route_internal_{net}', 'li1')
                route.pos_list = [nm(500), y_pos, nm(3500), y_pos + nm(150)]
                self.cell.add_polygon(route)
                print(f"   Routed internal net {net} at Y={to_um(y_pos):.2f} μm")
                y_pos += nm(200)

    def _add_power_distribution(self, topology: Dict):
        """Add VDD and GND power rails"""
        # VDD rail (top)
        vdd_rail = Polygon('rail_VDD', 'met1')
        vdd_rail.pos_list = [nm(100), nm(5000), nm(5000), nm(5300)]
        self.cell.add_polygon(vdd_rail)
        print(f"   Added VDD rail at Y={to_um(nm(5000)):.2f} μm")

        # GND rail (bottom)
        gnd_rail = Polygon('rail_GND', 'met1')
        gnd_rail.pos_list = [nm(100), nm(100), nm(5000), nm(400)]
        self.cell.add_polygon(gnd_rail)
        print(f"   Added GND rail at Y={to_um(nm(100)):.2f} μm")

    def _print_summary(self):
        """Print layout generation summary"""
        all_x = []
        all_y = []

        for inst in self.cell.instances:
            if inst.pos_list[0] is not None:
                all_x.extend([inst.pos_list[0], inst.pos_list[2]])
                all_y.extend([inst.pos_list[1], inst.pos_list[3]])

        for poly in self.cell.polygons:
            if poly.pos_list and all(v is not None for v in poly.pos_list):
                all_x.extend([poly.pos_list[0], poly.pos_list[2]])
                all_y.extend([poly.pos_list[1], poly.pos_list[3]])

        width = max(all_x) - min(all_x)
        height = max(all_y) - min(all_y)

        print(f"\n{'='*70}")
        print("LAYOUT GENERATION SUMMARY")
        print(f"{'='*70}")
        print(f"Cell name: {self.cell.name}")
        print(f"Devices: {len(self.instances)}")
        print(f"Routing polygons: {len(self.cell.polygons)}")
        print(f"Dimensions: {to_um(width):.3f} × {to_um(height):.3f} μm")
        print(f"Area: {to_um(width) * to_um(height):.3f} μm²")


# Example usage
if __name__ == "__main__":
    from lvs import create_and3_schematic_netlist

    print("="*70)
    print("LAYOUT GENERATION FROM SCHEMATIC - DEMO")
    print("="*70)

    # Create schematic
    schematic = create_and3_schematic_netlist()
    schematic.print_summary()

    # Generate layout
    tech = create_sky130_tech()
    generator = LayoutGenerator(schematic, tech)
    layout_cell = generator.generate()

    if layout_cell:
        # Export
        layout_cell.export_gds('generated_from_schematic.gds', technology=tech)
        print(f"\n✅ Layout generated and exported to: generated_from_schematic.gds")
    else:
        print(f"\n✗ Layout generation failed")
