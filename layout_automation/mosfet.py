#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOSFET transistor primitive for layout automation

Generates parametric MOSFET layouts with configurable W, L, and fingers
"""

from typing import Tuple, Optional, List
from .gds_cell import Cell, Polygon
from .technology import Technology
from .contact import Contact
from .units import um, nm, to_um


class MOSFET:
    """
    MOSFET transistor primitive (PCell)

    Generates layout for NMOS or PMOS transistor with:
    - Configurable width (W) and length (L)
    - Multi-finger support for current distribution
    - Automatic contact generation
    - Source, drain, and gate terminals

    Attributes:
        name: Transistor identifier
        device_type: 'nfet' or 'pfet'
        width: Channel width in DBU (total for all fingers)
        length: Channel length (gate length) in DBU
        fingers: Number of parallel fingers
        technology: Technology object
        cell: Generated cell containing transistor layout
    """

    def __init__(self, name: str, device_type: str, width: int, length: int,
                 technology: Technology, fingers: int = 1):
        """
        Initialize MOSFET primitive

        Args:
            name: Transistor identifier
            device_type: 'nfet' or 'pfet' (or 'nmos'/'pmos')
            width: Total channel width in DBU
            length: Channel length in DBU
            technology: Technology object
            fingers: Number of parallel fingers (default 1)
        """
        self.name = name
        self.device_type = device_type.lower()
        if self.device_type in ['nmos', 'nfet_01v8']:
            self.device_type = 'nfet'
        elif self.device_type in ['pmos', 'pfet_01v8_hvt']:
            self.device_type = 'pfet'

        self.width = width
        self.length = length
        self.fingers = fingers
        self.technology = technology
        self.cell = None

        # Calculate per-finger width
        self.finger_width = width // fingers

    def generate(self) -> Cell:
        """
        Generate MOSFET layout

        Creates:
        1. Active area (diff)
        2. Polysilicon gates
        3. Well (nwell for PMOS, pwell for NMOS)
        4. Implant layers (nsdm for NMOS, psdm for PMOS)
        5. Contacts to source/drain

        Returns:
            Cell containing transistor layout
        """
        self.cell = Cell(self.name)

        # Get design rules (matching SkyWater layout dimensions)
        # Poly (gate) dimensions - SkyWater uses much wider poly for DRC
        poly_drawn_width = nm(430)  # Actual drawn width (not just L)
        poly_extension = nm(130)  # Extension beyond active area

        # Contact and spacing rules
        diff_contact_spacing = nm(55)  # Space from gate edge to contact edge
        contact_size = nm(170)

        # Diff (active) dimensions
        diff_width = nm(670)  # SkyWater standard diff width

        # Calculate dimensions
        # For each finger: gate + spacing on each side
        finger_pitch = poly_drawn_width + 2 * diff_contact_spacing + contact_size
        total_width = self.fingers * finger_pitch + contact_size

        # Y dimensions
        diff_height = self.finger_width
        poly_height = diff_height + 2 * poly_extension

        # Generate active area (diff)
        diff_x1 = 0
        diff_y1 = poly_extension
        diff_x2 = diff_width
        diff_y2 = diff_y1 + diff_height

        diff = Polygon(f'{self.name}_diff', 'diff')
        diff.pos_list = [diff_x1, diff_y1, diff_x2, diff_y2]
        self.cell.add_polygon(diff)

        # Generate poly gates
        for i in range(self.fingers):
            gate_x1 = contact_size + i * finger_pitch
            gate_y1 = 0
            gate_x2 = gate_x1 + poly_drawn_width
            gate_y2 = gate_y1 + poly_height

            poly = Polygon(f'{self.name}_poly_{i}', 'poly')
            poly.pos_list = [gate_x1, gate_y1, gate_x2, gate_y2]
            self.cell.add_polygon(poly)

        # Generate well layer
        well_layer = 'nwell' if self.device_type == 'pfet' else 'pwell'
        well_extension = nm(180)  # Well extends beyond active

        well_x1 = diff_x1 - well_extension
        well_y1 = diff_y1 - well_extension
        well_x2 = diff_x2 + well_extension
        well_y2 = diff_y2 + well_extension

        well = Polygon(f'{self.name}_well', well_layer)
        well.pos_list = [well_x1, well_y1, well_x2, well_y2]
        self.cell.add_polygon(well)

        # Generate implant layer
        implant_layer = 'psdm' if self.device_type == 'pfet' else 'nsdm'
        implant_extension = nm(125)

        implant_x1 = diff_x1 - implant_extension
        implant_y1 = diff_y1 - implant_extension
        implant_x2 = diff_x2 + implant_extension
        implant_y2 = diff_y2 + implant_extension

        implant = Polygon(f'{self.name}_implant', implant_layer)
        implant.pos_list = [implant_x1, implant_y1, implant_x2, implant_y2]
        self.cell.add_polygon(implant)

        # Generate contacts to source/drain regions
        contact_y = (diff_y1 + diff_y2) // 2

        # First source contact (left side)
        source_x = contact_size // 2
        source_contact = Contact(
            f'{self.name}_source_0',
            'diff', 'li1',
            (source_x, contact_y),
            self.technology
        )
        source_contact.generate(self.cell)

        # Drain and source contacts between gates
        for i in range(self.fingers):
            drain_x = contact_size + i * finger_pitch + poly_drawn_width + diff_contact_spacing + contact_size // 2

            drain_contact = Contact(
                f'{self.name}_drain_{i}',
                'diff', 'li1',
                (drain_x, contact_y),
                self.technology
            )
            drain_contact.generate(self.cell)

            # Add source contact for next finger (except after last finger)
            if i < self.fingers - 1:
                next_source_x = drain_x + contact_size // 2 + diff_contact_spacing + poly_drawn_width + diff_contact_spacing + contact_size // 2
                source_contact = Contact(
                    f'{self.name}_source_{i+1}',
                    'diff', 'li1',
                    (next_source_x, contact_y),
                    self.technology
                )
                source_contact.generate(self.cell)

        return self.cell

    def get_terminals(self) -> dict:
        """
        Get terminal positions for connectivity

        Returns:
            Dictionary with 'gate', 'source', 'drain' positions
        """
        if self.cell is None:
            self.generate()

        # Extract terminal positions from generated layout
        # Gate: center of first poly
        gate_poly = [p for p in self.cell.polygons if 'poly' in p.name][0]
        gate_x = (gate_poly.pos_list[0] + gate_poly.pos_list[2]) // 2
        gate_y = (gate_poly.pos_list[1] + gate_poly.pos_list[3]) // 2

        # Source: left contact
        source_polys = [p for p in self.cell.polygons if 'source_0_top' in p.name]
        if source_polys:
            source_x = (source_polys[0].pos_list[0] + source_polys[0].pos_list[2]) // 2
            source_y = (source_polys[0].pos_list[1] + source_polys[0].pos_list[3]) // 2
        else:
            source_x, source_y = 0, 0

        # Drain: first drain contact
        drain_polys = [p for p in self.cell.polygons if 'drain_0_top' in p.name]
        if drain_polys:
            drain_x = (drain_polys[0].pos_list[0] + drain_polys[0].pos_list[2]) // 2
            drain_y = (drain_polys[0].pos_list[1] + drain_polys[0].pos_list[3]) // 2
        else:
            drain_x, drain_y = 0, 0

        return {
            'gate': (gate_x, gate_y),
            'source': (source_x, source_y),
            'drain': (drain_x, drain_y)
        }

    def __repr__(self):
        return f"MOSFET({self.device_type}, W={to_um(self.width):.3f}um, L={to_um(self.length):.3f}um, fingers={self.fingers})"


# Example usage and testing
if __name__ == "__main__":
    from technology import create_sky130_tech
    import matplotlib.pyplot as plt

    print("MOSFET Primitive Generator Example")
    print("=" * 70)

    # Create technology
    tech = create_sky130_tech()

    # Example 1: NMOS from SkyWater inverter
    print("\n1. NMOS (W=0.65um, L=0.15um) - SkyWater inv_1 spec")
    nmos = MOSFET('NMOS1', 'nfet_01v8', width=um(0.65), length=um(0.15), technology=tech)
    nmos_cell = nmos.generate()
    print(f"   {nmos}")
    print(f"   Generated {len(nmos_cell.polygons)} polygons")
    terminals = nmos.get_terminals()
    print(f"   Terminals: gate={terminals['gate']}, source={terminals['source']}, drain={terminals['drain']}")

    # Example 2: PMOS from SkyWater inverter
    print("\n2. PMOS (W=1.0um, L=0.15um) - SkyWater inv_1 spec")
    pmos = MOSFET('PMOS1', 'pfet_01v8_hvt', width=um(1.0), length=um(0.15), technology=tech)
    pmos_cell = pmos.generate()
    print(f"   {pmos}")
    print(f"   Generated {len(pmos_cell.polygons)} polygons")

    # Example 3: Multi-finger NMOS
    print("\n3. Multi-finger NMOS (W=2.0um, L=0.15um, fingers=4)")
    nmos_mf = MOSFET('NMOS_MF', 'nfet', width=um(2.0), length=um(0.15), technology=tech, fingers=4)
    nmos_mf_cell = nmos_mf.generate()
    print(f"   {nmos_mf}")
    print(f"   Generated {len(nmos_mf_cell.polygons)} polygons")
    print(f"   Finger width: {to_um(nmos_mf.finger_width):.3f}um each")

    # Export to GDS
    print("\nExporting NMOS to GDS...")
    nmos_cell.export_gds("nmos_test.gds")

    print("\nExporting PMOS to GDS...")
    pmos_cell.export_gds("pmos_test.gds")

    print("\nMOSFET primitive ready!")
    print("\nUsage:")
    print("  nmos = MOSFET('M1', 'nfet', width=um(0.65), length=um(0.15), tech)")
    print("  cell = nmos.generate()")
    print("  terminals = nmos.get_terminals()")
