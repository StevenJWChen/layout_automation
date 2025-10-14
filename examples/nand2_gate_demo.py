#!/usr/bin/env python3
"""
CMOS NAND2 Gate Demo with Frozen Contact Arrays

This example demonstrates creating a 2-input NAND gate using:
- Frozen contact arrays for consistent via patterns
- 2 PMOS transistors in parallel at top (pull-up path)
- 2 NMOS transistors in series at bottom (pull-down path)
- Metal-to-poly contacts for gate connections
- Power rails (VDD/GND)
- Input/output routing

Circuit structure (like inverter, PMOS on top):
         VDD
          |
    PMOS_A | PMOS_B (parallel - either can pull up)
          |
    A,B---+---OUT
          |
    NMOS_A—NMOS_B (series - both must be on to pull down)
          |
         GND

Truth table (NAND logic):
    A  B  OUT
    0  0   1
    0  1   1
    1  0   1
    1  1   0
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout_automation.gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt


def create_contact_array_manual(name, rows, cols, contact_size=2, spacing=2):
    """Create a contact array with manual positioning"""
    array = Cell(name)
    pitch_x = contact_size + spacing
    pitch_y = contact_size + spacing

    for i in range(rows):
        for j in range(cols):
            contact = Polygon(f'cont_{i}_{j}', 'contact')
            x1 = j * pitch_x
            y1 = i * pitch_y
            contact.pos_list = [x1, y1, x1 + contact_size, y1 + contact_size]
            array.add_polygon(contact)

    return array


def create_nmos():
    """Create NMOS transistor with source/drain contacts"""
    nmos = Cell('NMOS')

    # Diffusion region (active area)
    diff = Polygon('diff', 'diff')
    diff.pos_list = [0, 5, 30, 25]  # 30x20 diffusion

    # Poly gate (crosses diffusion)
    poly = Polygon('poly', 'poly')
    poly.pos_list = [11, 3, 19, 29]  # 8x26 poly gate

    # Metal regions for source and drain
    metal_src = Polygon('metal_src', 'metal1')
    metal_drn = Polygon('metal_drn', 'metal1')
    metal_src.pos_list = [1, 10, 9, 22]   # 8x12 metal
    metal_drn.pos_list = [21, 10, 29, 22]  # 8x12 metal

    nmos.add_polygon([diff, poly, metal_src, metal_drn])

    # Add frozen contact arrays (centered in metal regions)
    src_contacts = CellInstance('src_contacts', contact_array)
    drn_contacts = CellInstance('drn_contacts', contact_array)
    src_contacts.pos_list = [2, 13, 8, 19]   # 6x6 centered in 8x12
    drn_contacts.pos_list = [22, 13, 28, 19]  # 6x6 centered in 8x12

    nmos.add_instance([src_contacts, drn_contacts])
    nmos.freeze_layout()
    return nmos


def create_pmos():
    """Create PMOS transistor (symmetric with NMOS)"""
    pmos = Cell('PMOS')

    # Use pdiff layer for p-type diffusion
    diff = Polygon('diff', 'pdiff')
    diff.pos_list = [0, 5, 30, 25]

    poly = Polygon('poly', 'poly')
    poly.pos_list = [11, 3, 19, 29]

    metal_src = Polygon('metal_src', 'metal1')
    metal_drn = Polygon('metal_drn', 'metal1')
    metal_src.pos_list = [1, 10, 9, 22]
    metal_drn.pos_list = [21, 10, 29, 22]

    pmos.add_polygon([diff, poly, metal_src, metal_drn])

    src_contacts = CellInstance('src_contacts', contact_array)
    drn_contacts = CellInstance('drn_contacts', contact_array)
    src_contacts.pos_list = [2, 13, 8, 19]
    drn_contacts.pos_list = [22, 13, 28, 19]

    pmos.add_instance([src_contacts, drn_contacts])
    pmos.freeze_layout()
    return pmos


def create_nand2_gate(nmos, pmos):
    """
    Create NAND2 gate using frozen NMOS and PMOS transistors

    Layout structure (vertical, like inverter):
    - VDD rail (top)
    - PMOS_A and PMOS_B in parallel (both sources to VDD, drains to OUT)
    - OUTPUT node (drains of both PMOS, drain of top NMOS)
    - NMOS_A and NMOS_B in series (A's drain to B's source)
    - GND rail (bottom)
    """
    nand2 = Cell('NAND2')

    # Position transistors vertically (PMOS at top, NMOS at bottom)
    # PMOS transistors in parallel (top section)
    pmos_a_inst = CellInstance('PMOS_A', pmos)
    pmos_b_inst = CellInstance('PMOS_B', pmos)

    # NMOS transistors in series (bottom section)
    nmos_a_inst = CellInstance('NMOS_A', nmos)
    nmos_b_inst = CellInstance('NMOS_B', nmos)

    # Vertical positions (bottom to top: GND -> NMOS_B -> NMOS_A -> PMOS_A & PMOS_B -> VDD)
    # Place NMOS transistors in series
    nmos_b_inst.pos_list = [0, 5, 30, 34]      # Bottom NMOS (y: 5-34)
    nmos_a_inst.pos_list = [0, 44, 30, 73]     # Top NMOS (y: 44-73, 10 unit spacing)

    # Place PMOS transistors in parallel (side by side, then shifted up)
    # Actually, let's stack them vertically for simplicity like the inverter pattern
    pmos_a_inst.pos_list = [0, 83, 30, 112]    # Bottom PMOS (y: 83-112, 10 unit spacing)
    pmos_b_inst.pos_list = [0, 122, 30, 151]   # Top PMOS (y: 122-151, 10 unit spacing)

    nand2.add_instance([nmos_b_inst, nmos_a_inst, pmos_a_inst, pmos_b_inst])

    # Power rails
    vdd_rail = Polygon('VDD', 'metal1')
    gnd_rail = Polygon('GND', 'metal1')
    vdd_rail.pos_list = [0, 151, 30, 156]  # Top rail (width=5)
    gnd_rail.pos_list = [0, 0, 30, 5]      # Bottom rail (width=5)

    # NMOS series connection: NMOS_B drain to NMOS_A source (internal node)
    nmos_series = Polygon('nmos_series', 'metal1')
    nmos_series.pos_list = [21, 27, 29, 51]  # Connects drain of NMOS_B to source of NMOS_A

    # NMOS_B source to GND
    nmos_gnd = Polygon('nmos_gnd', 'metal1')
    nmos_gnd.pos_list = [1, 0, 9, 18]  # NMOS_B source to GND

    # PMOS parallel: both sources to VDD
    pmos_vdd_a = Polygon('pmos_vdd_a', 'metal1')
    pmos_vdd_a.pos_list = [1, 93, 9, 156]  # PMOS_A source to VDD
    pmos_vdd_b = Polygon('pmos_vdd_b', 'metal1')
    pmos_vdd_b.pos_list = [1, 132, 9, 156]  # PMOS_B source to VDD

    # Output connection: both PMOS drains + NMOS_A drain
    output_metal = Polygon('OUTPUT', 'metal1')
    output_metal.pos_list = [21, 66, 29, 119]  # Connects NMOS_A drain to both PMOS drains

    # Input A connection with metal-to-poly contacts
    # Input A connects to PMOS_A and NMOS_A gates
    input_a_poly = Polygon('INPUT_A', 'poly')
    input_a_poly.pos_list = [11, 44, 19, 112]  # Spans NMOS_A and PMOS_A gates

    # Add metal stub and contact for Input A (essential for external connection)
    input_a_metal = Polygon('INPUT_A_metal', 'metal1')
    input_a_metal.pos_list = [11, 75, 19, 85]  # Metal region over poly

    # Contact array for metal-to-poly connection at Input A
    input_a_contact = CellInstance('input_a_contact', contact_array)
    input_a_contact.pos_list = [12, 77, 18, 83]  # Centered on metal/poly overlap

    # Input B connection with metal-to-poly contacts
    # Input B connects to PMOS_B and NMOS_B gates
    input_b_poly_nmos = Polygon('INPUT_B_nmos', 'poly')
    input_b_poly_nmos.pos_list = [11, 5, 19, 34]  # NMOS_B gate

    input_b_poly_pmos = Polygon('INPUT_B_pmos', 'poly')
    input_b_poly_pmos.pos_list = [11, 122, 19, 151]  # PMOS_B gate

    # Add metal stub and contact for Input B at NMOS_B
    input_b_metal_nmos = Polygon('INPUT_B_metal_nmos', 'metal1')
    input_b_metal_nmos.pos_list = [11, 15, 19, 25]  # Metal over NMOS_B poly

    input_b_contact_nmos = CellInstance('input_b_contact_nmos', contact_array)
    input_b_contact_nmos.pos_list = [12, 17, 18, 23]  # Metal-to-poly contact

    # Add metal stub and contact for Input B at PMOS_B
    input_b_metal_pmos = Polygon('INPUT_B_metal_pmos', 'metal1')
    input_b_metal_pmos.pos_list = [11, 132, 19, 142]  # Metal over PMOS_B poly

    input_b_contact_pmos = CellInstance('input_b_contact_pmos', contact_array)
    input_b_contact_pmos.pos_list = [12, 134, 18, 140]  # Metal-to-poly contact

    # Vertical metal to connect Input B at both transistors
    input_b_metal_vertical = Polygon('INPUT_B_vertical', 'metal1')
    input_b_metal_vertical.pos_list = [13, 15, 17, 142]  # Vertical metal connecting both B inputs

    nand2.add_polygon([
        vdd_rail, gnd_rail,
        input_a_poly, input_a_metal,
        input_b_poly_nmos, input_b_poly_pmos,
        input_b_metal_nmos, input_b_metal_pmos, input_b_metal_vertical,
        nmos_series, pmos_vdd_a, pmos_vdd_b, nmos_gnd,
        output_metal
    ])

    nand2.add_instance([
        input_a_contact,
        input_b_contact_nmos,
        input_b_contact_pmos
    ])

    return nand2


if __name__ == "__main__":
    print("Creating NAND2 Gate Demo...")

    # Step 1: Create and freeze contact array (2x2)
    print("\n1. Creating contact array (2x2)...")
    contact_array = create_contact_array_manual('contact_array', rows=2, cols=2,
                                                 contact_size=2, spacing=2)
    contact_array.freeze_layout()
    print(f"   Contact array frozen with {len(contact_array.polygons)} contacts")

    # Step 2: Create and freeze NMOS/PMOS transistors
    print("\n2. Creating NMOS and PMOS transistors...")
    nmos = create_nmos()
    pmos = create_pmos()
    print(f"   NMOS frozen with bbox: {nmos.get_bbox()}")
    print(f"   PMOS frozen with bbox: {pmos.get_bbox()}")

    # Step 3: Create NAND2 gate
    print("\n3. Creating NAND2 gate...")
    nand2 = create_nand2_gate(nmos, pmos)
    print(f"   NAND2 gate created with bbox: {nand2.get_bbox()}")

    # Step 4: Create top-level layout
    print("\n4. Creating top-level layout...")
    layout = Cell('LAYOUT')
    nand2_inst = CellInstance('nand2_gate', nand2)
    nand2_inst.pos_list = [0, 0, 30, 156]
    layout.add_instance(nand2_inst)

    # Step 5: Export to GDS
    print("\n5. Exporting to GDS...")
    os.makedirs('demo_outputs', exist_ok=True)
    layout.export_gds('demo_outputs/nand2_gate.gds')
    print("   Saved to: demo_outputs/nand2_gate.gds")

    # Step 6: Generate visualization
    print("\n6. Generating visualization...")
    fig = layout.draw(solve_first=False, show=False)
    plt.title('Layout: NAND2 Gate')
    plt.savefig('demo_outputs/nand2_gate.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   Saved to: demo_outputs/nand2_gate.png")

    # Also visualize just the NAND2 gate cell
    fig2 = nand2.draw(solve_first=False, show=False)
    plt.title('NAND2 Gate Detail')
    plt.savefig('demo_outputs/nand2_gate_detail.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   Saved to: demo_outputs/nand2_gate_detail.png")

    print("\n✓ NAND2 gate demo complete!")
    print("\nCircuit structure:")
    print("  - 2 PMOS in parallel at top (pull-up path)")
    print("  - 2 NMOS in series at bottom (pull-down path)")
    print("  - Input A: controls PMOS_A and NMOS_A (with metal-to-poly contacts)")
    print("  - Input B: controls PMOS_B and NMOS_B (with metal-to-poly contacts)")
    print("  - Output: LOW only when both A=1 AND B=1 (NAND logic)")
    print("\nKey feature: Metal-to-poly contacts for gate connections!")
    print("\nFiles generated:")
    print("  - demo_outputs/nand2_gate.gds")
    print("  - demo_outputs/nand2_gate.png")
    print("  - demo_outputs/nand2_gate_detail.png")
