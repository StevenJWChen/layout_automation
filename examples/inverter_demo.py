#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CMOS Inverter Example with Contact Arrays

This example demonstrates creating a complete CMOS inverter:
1. Contact array (reusable, frozen)
2. NMOS transistor with contacts
3. PMOS transistor with contacts
4. CMOS inverter combining NMOS + PMOS
5. Power rails (VDD, GND)
6. Input/output routing

Circuit:
       VDD
        |
       PMOS (pull-up)
        |
    IN--+--OUT
        |
       NMOS (pull-down)
        |
       GND
"""

import os
from layout_automation.gds_cell import Cell, Polygon, CellInstance

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("=" * 80)
print("CMOS INVERTER EXAMPLE")
print("=" * 80)
print()

# ==============================================================================
# STEP 1: Create Reusable Contact Array
# ==============================================================================

print("STEP 1: Create Contact Array (2x2)")
print("-" * 80)

def create_contact_array(name='contact_array', rows=2, cols=2, size=2, spacing=2):
    """Create contact array with manual positioning"""
    array = Cell(name)
    pitch_x = size + spacing
    pitch_y = size + spacing

    for i in range(rows):
        for j in range(cols):
            contact = Polygon(f'cont_{i}_{j}', 'contact')
            x1 = j * pitch_x
            y1 = i * pitch_y
            contact.pos_list = [x1, y1, x1 + size, y1 + size]
            array.add_polygon(contact)

    return array

contact_array = create_contact_array()
contact_array.freeze_layout()

print(f"✓ Contact array created and frozen")
print(f"  Size: 6x6, Bbox: {contact_array.get_bbox()}")
print()

# ==============================================================================
# STEP 2: Create NMOS Transistor
# ==============================================================================

print("STEP 2: Create NMOS Transistor")
print("-" * 80)

def create_nmos():
    """Create NMOS transistor with source/drain contacts"""
    nmos = Cell('NMOS')

    # Create layers
    diff = Polygon('diff', 'diff')
    poly = Polygon('poly', 'poly')
    metal_src = Polygon('metal_src', 'metal1')
    metal_drn = Polygon('metal_drn', 'metal1')

    # Position layers
    diff.pos_list = [0, 5, 30, 25]      # 30x20 diffusion
    poly.pos_list = [11, 3, 19, 29]     # 8x26 poly gate
    metal_src.pos_list = [1, 10, 9, 22] # 8x12 source metal
    metal_drn.pos_list = [21, 10, 29, 22] # 8x12 drain metal

    nmos.add_polygon([diff, poly, metal_src, metal_drn])

    # Add contact arrays (frozen)
    src_contacts = CellInstance('src_contacts', contact_array)
    drn_contacts = CellInstance('drn_contacts', contact_array)

    # Position contacts (centered in metal)
    src_contacts.pos_list = [2, 13, 8, 19]
    drn_contacts.pos_list = [22, 13, 28, 19]

    nmos.add_instance([src_contacts, drn_contacts])

    return nmos

nmos = create_nmos()
nmos.freeze_layout()

print(f"✓ NMOS created and frozen")
print(f"  Bbox: {nmos.get_bbox()}")
print()

# Visualize NMOS
fig = nmos.draw(solve_first=False, show=False)
import matplotlib.pyplot as plt
plt.savefig('demo_outputs/inverter_nmos.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved NMOS to demo_outputs/inverter_nmos.png")
print()

# ==============================================================================
# STEP 3: Create PMOS Transistor
# ==============================================================================

print("STEP 3: Create PMOS Transistor")
print("-" * 80)

def create_pmos():
    """Create PMOS transistor with source/drain contacts"""
    pmos = Cell('PMOS')

    # Create layers
    diff = Polygon('diff', 'pdiff')     # PMOS diffusion
    poly = Polygon('poly', 'poly')
    metal_src = Polygon('metal_src', 'metal1')
    metal_drn = Polygon('metal_drn', 'metal1')

    # Position layers (same as NMOS for symmetry)
    diff.pos_list = [0, 5, 30, 25]      # 30x20 diffusion
    poly.pos_list = [11, 3, 19, 29]     # 8x26 poly gate
    metal_src.pos_list = [1, 10, 9, 22] # 8x12 source metal
    metal_drn.pos_list = [21, 10, 29, 22] # 8x12 drain metal

    pmos.add_polygon([diff, poly, metal_src, metal_drn])

    # Add contact arrays (frozen, same as NMOS)
    src_contacts = CellInstance('src_contacts', contact_array)
    drn_contacts = CellInstance('drn_contacts', contact_array)

    src_contacts.pos_list = [2, 13, 8, 19]
    drn_contacts.pos_list = [22, 13, 28, 19]

    pmos.add_instance([src_contacts, drn_contacts])

    return pmos

pmos = create_pmos()
pmos.freeze_layout()

print(f"✓ PMOS created and frozen")
print(f"  Bbox: {pmos.get_bbox()}")
print()

# Visualize PMOS
fig = pmos.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/inverter_pmos.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved PMOS to demo_outputs/inverter_pmos.png")
print()

# ==============================================================================
# STEP 4: Create CMOS Inverter
# ==============================================================================

print("STEP 4: Create CMOS Inverter")
print("-" * 80)

inverter = Cell('INVERTER')

# Create instances of NMOS and PMOS
nmos_inst = CellInstance('NMOS_inst', nmos)
pmos_inst = CellInstance('PMOS_inst', pmos)

# Position transistors vertically
# PMOS on top, NMOS on bottom
spacing = 10

# NMOS at bottom
nmos_inst.pos_list = [0, 0, 30, 29]

# PMOS on top (with spacing)
pmos_inst.pos_list = [0, 29 + spacing, 30, 29 + spacing + 29]

inverter.add_instance([nmos_inst, pmos_inst])

print("✓ Transistors positioned:")
print(f"  NMOS: {nmos_inst.pos_list}")
print(f"  PMOS: {pmos_inst.pos_list}")
print()

# Add power rails
print("Adding power rails...")
vdd_rail = Polygon('VDD', 'metal1')
gnd_rail = Polygon('GND', 'metal1')

# VDD at top (above PMOS source)
vdd_rail.pos_list = [0, 68, 30, 73]

# GND at bottom (below NMOS source)
gnd_rail.pos_list = [0, -5, 30, 0]

inverter.add_polygon([vdd_rail, gnd_rail])

print(f"  VDD rail: {vdd_rail.pos_list}")
print(f"  GND rail: {gnd_rail.pos_list}")
print()

# Add input connection (poly gates)
print("Adding input connection...")
input_poly = Polygon('INPUT', 'poly')

# Connect both gates vertically
# NMOS gate is at x=11-19, y=3-29
# PMOS gate is at x=11-19, y=42-68
input_poly.pos_list = [11, 3, 19, 68]

inverter.add_polygon(input_poly)

print(f"  Input poly: {input_poly.pos_list}")
print()

# Add output connection (drain metals)
print("Adding output connection...")
output_metal = Polygon('OUTPUT', 'metal1')

# Connect NMOS drain to PMOS drain
# NMOS drain: (21, 10) to (29, 22)
# PMOS drain: (21, 49) to (29, 61)
output_metal.pos_list = [21, 10, 29, 61]

inverter.add_polygon(output_metal)

print(f"  Output metal: {output_metal.pos_list}")
print()

# Add connection from PMOS source to VDD
pmos_vdd_connect = Polygon('PMOS_VDD', 'metal1')
pmos_vdd_connect.pos_list = [1, 49, 9, 68]

inverter.add_polygon(pmos_vdd_connect)

# Add connection from NMOS source to GND
nmos_gnd_connect = Polygon('NMOS_GND', 'metal1')
nmos_gnd_connect.pos_list = [1, 0, 9, 22]

inverter.add_polygon(nmos_gnd_connect)

print("✓ Power connections added")
print()

# Get final bbox
bbox = inverter.get_bbox()
print(f"✓ CMOS Inverter complete")
print(f"  Bbox: {bbox}")
print(f"  Dimensions: {bbox[2]-bbox[0]} x {bbox[3]-bbox[1]}")
print()

# ==============================================================================
# STEP 5: Visualize and Export
# ==============================================================================

print("STEP 5: Visualize and Export")
print("-" * 80)

# Visualize complete inverter
fig = inverter.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/inverter_complete.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved complete inverter to demo_outputs/inverter_complete.png")

# Export to GDS
inverter.export_gds('demo_outputs/inverter.gds')
print("✓ Exported to demo_outputs/inverter.gds")
print()

# Freeze inverter for reuse
inverter.freeze_layout()
print(f"✓ Inverter frozen: {inverter.is_frozen()}")
print()

# ==============================================================================
# STEP 6: Create Inverter Array
# ==============================================================================

print("STEP 6: Create Inverter Chain (3 inverters)")
print("-" * 80)

inv_chain = Cell('INVERTER_CHAIN')

# Create 3 inverter instances
inv1 = CellInstance('INV1', inverter)
inv2 = CellInstance('INV2', inverter)
inv3 = CellInstance('INV3', inverter)

# Position in a row
spacing_x = 15
inv_width = 30
inv_height = 73

inv1.pos_list = [0, 0, inv_width, inv_height]
inv2.pos_list = [inv_width + spacing_x, 0,
                 2*inv_width + spacing_x, inv_height]
inv3.pos_list = [2*(inv_width + spacing_x), 0,
                 3*inv_width + 2*spacing_x, inv_height]

inv_chain.add_instance([inv1, inv2, inv3])

# Add interconnects between inverters
inter1 = Polygon('INTER1', 'metal1')
inter2 = Polygon('INTER2', 'metal1')

# Connect INV1 output to INV2 input (at poly level)
inter1.pos_list = [21, 35, 45+15, 40]

# Connect INV2 output to INV3 input
inter2.pos_list = [21+45+15, 35, 90+30, 40]

inv_chain.add_polygon([inter1, inter2])

bbox = inv_chain.get_bbox()
print(f"✓ Inverter chain created")
print(f"  Bbox: {bbox}")
print(f"  Dimensions: {bbox[2]-bbox[0]} x {bbox[3]-bbox[1]}")
print()

# Visualize chain
fig = inv_chain.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/inverter_chain.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved inverter chain to demo_outputs/inverter_chain.png")

# Export chain
inv_chain.export_gds('demo_outputs/inverter_chain.gds')
print("✓ Exported to demo_outputs/inverter_chain.gds")
print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("✅ Complete CMOS Inverter Created:")
print()
print("  Components:")
print("  ├─ Contact Array (2x2, 6x6) → FROZEN")
print("  ├─ NMOS Transistor (30x29)")
print("  │  ├─ Diffusion (30x20)")
print("  │  ├─ Poly gate (8x26)")
print("  │  ├─ Source metal + contacts")
print("  │  └─ Drain metal + contacts")
print("  ├─ PMOS Transistor (30x29)")
print("  │  ├─ P-type diffusion (30x20)")
print("  │  ├─ Poly gate (8x26)")
print("  │  ├─ Source metal + contacts")
print("  │  └─ Drain metal + contacts")
print("  └─ Complete Inverter (30x73)")
print("     ├─ PMOS (pull-up to VDD)")
print("     ├─ NMOS (pull-down to GND)")
print("     ├─ VDD rail (top)")
print("     ├─ GND rail (bottom)")
print("     ├─ Input (poly gates)")
print("     └─ Output (drain connection)")
print()
print("🔌 Circuit Function:")
print()
print("       VDD")
print("        |")
print("      [PMOS]")
print("        |")
print("   IN---+---OUT")
print("        |")
print("      [NMOS]")
print("        |")
print("       GND")
print()
print("  • IN=0 → PMOS ON, NMOS OFF → OUT=1 (VDD)")
print("  • IN=1 → PMOS OFF, NMOS ON → OUT=0 (GND)")
print()
print("📁 Files Generated:")
print()
print("  • demo_outputs/inverter_nmos.png - NMOS layout")
print("  • demo_outputs/inverter_pmos.png - PMOS layout")
print("  • demo_outputs/inverter_complete.png - Complete inverter")
print("  • demo_outputs/inverter.gds - Inverter GDS")
print("  • demo_outputs/inverter_chain.png - 3 inverters in chain")
print("  • demo_outputs/inverter_chain.gds - Chain GDS")
print()
print("🎯 Key Features:")
print()
print("  • Reusable frozen contact arrays")
print("  • Symmetric NMOS/PMOS design")
print("  • Proper VDD/GND power rails")
print("  • Input/output routing")
print("  • Inverter chain demonstration")
print("  • Ready for DRC/LVS verification")
print()
print("🎉 CMOS Inverter Example Complete!")
print("=" * 80)
