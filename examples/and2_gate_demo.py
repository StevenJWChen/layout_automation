#!/usr/bin/env python3
"""
CMOS AND2 Gate Demo with Frozen Contact Arrays

This example demonstrates creating a 2-input AND gate using:
- Frozen contact arrays for consistent via patterns
- 2 NMOS transistors in series (pull-down path)
- 2 PMOS transistors in parallel (pull-up path)
- Power rails (VDD/GND)
- Input/output routing

Circuit structure:
         VDD
          |
    PMOS_A | PMOS_B (parallel - both connect VDD to output)
          |
    A,B---+---OUT
          |
    NMOS_A—NMOS_B (series - both must be on to pull down)
          |
         GND

Truth table:
    A  B  OUT
    0  0   0
    0  1   0
    1  0   0
    1  1   1
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


def create_and2_gate(nmos, pmos):
    """
    Create AND2 gate using frozen NMOS and PMOS transistors

    Layout structure (vertical):
    - VDD rail (top)
    - PMOS_A (parallel to VDD)
    - PMOS_B (parallel to VDD)
    - OUTPUT node (drains of all transistors)
    - NMOS_A (series)
    - NMOS_B (series)
    - GND rail (bottom)
    """
    and2 = Cell('AND2')

    # Position transistors vertically
    # NMOS transistors in series (bottom section)
    nmos_b_inst = CellInstance('NMOS_B', nmos)  # Bottom NMOS
    nmos_a_inst = CellInstance('NMOS_A', nmos)  # Top NMOS

    # PMOS transistors in parallel (top section)
    pmos_a_inst = CellInstance('PMOS_A', pmos)  # Bottom PMOS
    pmos_b_inst = CellInstance('PMOS_B', pmos)  # Top PMOS

    # Vertical positions (with spacing between transistors)
    # Bottom to top: GND -> NMOS_B -> NMOS_A -> PMOS_A -> PMOS_B -> VDD
    nmos_b_inst.pos_list = [0, 5, 30, 34]      # y: 5-34
    nmos_a_inst.pos_list = [0, 44, 30, 73]     # y: 44-73 (10 unit spacing)
    pmos_a_inst.pos_list = [0, 83, 30, 112]    # y: 83-112 (10 unit spacing)
    pmos_b_inst.pos_list = [0, 122, 30, 151]   # y: 122-151 (10 unit spacing)

    and2.add_instance([nmos_b_inst, nmos_a_inst, pmos_a_inst, pmos_b_inst])

    # Power rails
    vdd_rail = Polygon('VDD', 'metal1')
    gnd_rail = Polygon('GND', 'metal1')
    vdd_rail.pos_list = [0, 151, 30, 156]  # Top rail (width=5)
    gnd_rail.pos_list = [0, 0, 30, 5]      # Bottom rail (width=5)

    # Input A connection (poly) - connects NMOS_A and PMOS_A gates
    input_a_poly = Polygon('INPUT_A', 'poly')
    input_a_poly.pos_list = [11, 44, 19, 112]  # Spans NMOS_A and PMOS_A

    # Input B connection (poly) - connects NMOS_B and PMOS_B gates
    input_b_poly = Polygon('INPUT_B', 'poly')
    input_b_poly.pos_list = [11, 5, 19, 34]    # NMOS_B gate
    input_b_poly_2 = Polygon('INPUT_B_2', 'poly')
    input_b_poly_2.pos_list = [11, 122, 19, 151]  # PMOS_B gate

    # Series connection between NMOS transistors (metal1)
    # NMOS_B drain to NMOS_A source
    nmos_series = Polygon('nmos_series', 'metal1')
    nmos_series.pos_list = [21, 27, 29, 51]  # Connects drain of NMOS_B to source of NMOS_A

    # Parallel PMOS sources to VDD
    pmos_vdd_a = Polygon('pmos_vdd_a', 'metal1')
    pmos_vdd_a.pos_list = [1, 93, 9, 156]  # PMOS_A source to VDD
    pmos_vdd_b = Polygon('pmos_vdd_b', 'metal1')
    pmos_vdd_b.pos_list = [1, 132, 9, 156]  # PMOS_B source to VDD

    # NMOS_B source to GND
    nmos_gnd = Polygon('nmos_gnd', 'metal1')
    nmos_gnd.pos_list = [1, 0, 9, 18]  # NMOS_B source to GND

    # Output connection (drains of NMOS_A and both PMOS)
    output_metal = Polygon('OUTPUT', 'metal1')
    output_metal.pos_list = [21, 66, 29, 119]  # Connects NMOS_A drain to PMOS_A,B drains

    and2.add_polygon([
        vdd_rail, gnd_rail,
        input_a_poly, input_b_poly, input_b_poly_2,
        nmos_series, pmos_vdd_a, pmos_vdd_b, nmos_gnd,
        output_metal
    ])

    return and2


if __name__ == "__main__":
    print("Creating AND2 Gate Demo...")

    # Step 1: Create and freeze contact array (2x2)
    print("\n1. Creating contact array (2x2)...")
    contact_array = create_contact_array_manual('contact_array', rows=2, cols=2,
                                                 contact_size=2, spacing=2)
    contact_array.freeze_layout()
    print(f"   Contact array frozen at {len(contact_array.polygons)} contacts")

    # Step 2: Create and freeze NMOS/PMOS transistors
    print("\n2. Creating NMOS and PMOS transistors...")
    nmos = create_nmos()
    pmos = create_pmos()
    print(f"   NMOS frozen with bbox: {nmos.get_bbox()}")
    print(f"   PMOS frozen with bbox: {pmos.get_bbox()}")

    # Step 3: Create AND2 gate
    print("\n3. Creating AND2 gate...")
    and2 = create_and2_gate(nmos, pmos)
    print(f"   AND2 gate created with bbox: {and2.get_bbox()}")

    # Step 4: Create top-level layout
    print("\n4. Creating top-level layout...")
    layout = Cell('LAYOUT')
    and2_inst = CellInstance('and2_gate', and2)
    and2_inst.pos_list = [0, 0, 30, 156]
    layout.add_instance(and2_inst)

    # Step 5: Export to GDS
    print("\n5. Exporting to GDS...")
    os.makedirs('demo_outputs', exist_ok=True)
    layout.export_gds('demo_outputs/and2_gate.gds')
    print("   Saved to: demo_outputs/and2_gate.gds")

    # Step 6: Generate visualization
    print("\n6. Generating visualization...")
    fig = layout.draw(solve_first=False, show=False)
    plt.title('Layout: AND2 Gate')
    plt.savefig('demo_outputs/and2_gate.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   Saved to: demo_outputs/and2_gate.png")

    # Also visualize just the AND2 gate cell
    fig2 = and2.draw(solve_first=False, show=False)
    plt.title('AND2 Gate Detail')
    plt.savefig('demo_outputs/and2_gate_detail.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   Saved to: demo_outputs/and2_gate_detail.png")

    print("\n✓ AND2 gate demo complete!")
    print("\nCircuit structure:")
    print("  - 2 NMOS in series (pull-down path)")
    print("  - 2 PMOS in parallel (pull-up path)")
    print("  - Input A: controls NMOS_A and PMOS_A")
    print("  - Input B: controls NMOS_B and PMOS_B")
    print("  - Output: HIGH only when both A=1 AND B=1")
    print("\nFiles generated:")
    print("  - demo_outputs/and2_gate.gds")
    print("  - demo_outputs/and2_gate.png")
    print("  - demo_outputs/and2_gate_detail.png")
