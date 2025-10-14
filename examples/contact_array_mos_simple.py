#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contact Array + MOS Transistor Example (Simplified)

This example demonstrates the solve-then-freeze workflow:
1. Create contact array with manually set positions
2. Freeze the contact array
3. Use frozen contact array in MOS transistor design
4. Build complete device with well ring

Key Concept: Solve → Freeze → Reuse as Fixed Layout
"""

import os
from layout_automation.gds_cell import Cell, Polygon, CellInstance

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("=" * 80)
print("CONTACT ARRAY + MOS TRANSISTOR EXAMPLE (Simplified)")
print("=" * 80)
print()
print("Demonstrating: Create → Solve/Position → Freeze → Reuse")
print()

# ==============================================================================
# STEP 1: Create Contact Array with Manual Positioning
# ==============================================================================

print("STEP 1: Create Contact Array")
print("-" * 80)
print()

def create_contact_array_manual(name, rows, cols, contact_size=2, spacing=3):
    """
    Create a contact array with manually set positions
    """
    array = Cell(name)

    contacts = []
    pitch_x = contact_size + spacing
    pitch_y = contact_size + spacing

    for i in range(rows):
        for j in range(cols):
            contact = Polygon(f'cont_{i}_{j}', 'contact')

            # Manually set positions
            x1 = j * pitch_x
            y1 = i * pitch_y
            contact.pos_list = [x1, y1, x1 + contact_size, y1 + contact_size]

            array.add_polygon(contact)
            contacts.append(contact)

    return array

# Create 2x2 contact array (smaller to fit in metal regions)
print("Creating 2x2 contact array (2x2 contacts, 2 spacing)...")
contact_array = create_contact_array_manual('contact_array_2x2', rows=2, cols=2,
                                            contact_size=2, spacing=2)

print(f"  Contact array has {len(contact_array.polygons)} contacts")

# Get bounding box
bbox = contact_array.get_bbox()
print(f"  Bounding box: {bbox}")
print(f"  Dimensions: {bbox[2] - bbox[0]} x {bbox[3] - bbox[1]}")
print()

# Visualize
fig = contact_array.draw(solve_first=False, show=False)
import matplotlib.pyplot as plt
plt.savefig('demo_outputs/contact_array_simple.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved visualization to demo_outputs/contact_array_simple.png")
print()

# Export to GDS
contact_array.export_gds('demo_outputs/contact_array_simple.gds')
print("✓ Exported to demo_outputs/contact_array_simple.gds")
print()

# ==============================================================================
# STEP 2: Freeze Contact Array
# ==============================================================================

print("STEP 2: Freeze Contact Array for Reuse")
print("-" * 80)
print()

# Freeze the array - locks all polygon positions
contact_array.freeze_layout()

print(f"✓ Contact array frozen")
print(f"  Is frozen: {contact_array.is_frozen()}")
print(f"  Frozen bbox: {contact_array._frozen_bbox}")
print()
print("  Benefits:")
print("  • Internal contact positions are locked")
print("  • Can be reused multiple times without re-solving")
print("  • Acts as a fixed IP block")
print()

# ==============================================================================
# STEP 3: Create MOS Transistor Structure
# ==============================================================================

print("STEP 3: Create MOS Transistor with Manual Positioning")
print("-" * 80)
print()

def create_nmos_manual():
    """Create NMOS transistor with manually positioned elements"""
    nmos = Cell('NMOS_transistor')

    # Create layers
    nmos_diff = Polygon('nmos_diff', 'diff')
    poly_gate = Polygon('poly_gate', 'poly')
    metal_source = Polygon('metal_source', 'metal1')
    metal_drain = Polygon('metal_drain', 'metal1')

    # Manually position (all coordinates explicit)
    # Diffusion region (30x20)
    nmos_diff.pos_list = [0, 5, 30, 25]

    # Poly gate crosses diffusion (8x26)
    poly_gate.pos_list = [11, 3, 19, 29]

    # Metal source on left (larger to accommodate contacts: 8x12)
    metal_source.pos_list = [1, 10, 9, 22]

    # Metal drain on right (larger to accommodate contacts: 8x12)
    metal_drain.pos_list = [21, 10, 29, 22]

    nmos.add_polygon([nmos_diff, poly_gate, metal_source, metal_drain])

    return nmos

print("Creating NMOS transistor...")
nmos = create_nmos_manual()
print(f"  NMOS has {len(nmos.polygons)} polygon layers")
print(f"  Bounding box: {nmos.get_bbox()}")
print()

# Add frozen contact arrays
print("Adding frozen contact arrays to source/drain...")
source_contacts = CellInstance('source_contacts', contact_array)
drain_contacts = CellInstance('drain_contacts', contact_array)

# Manually position contact arrays over metal regions (2x2 array = 6x6 total)
# Center in metal regions (metal is 8x12, contacts are 6x6)
source_contacts.pos_list = [2, 13, 8, 19]  # Over source metal (centered)
drain_contacts.pos_list = [22, 13, 28, 19]  # Over drain metal (centered)

nmos.add_instance([source_contacts, drain_contacts])

print(f"  Source contacts positioned at: {source_contacts.pos_list}")
print(f"  Drain contacts positioned at: {drain_contacts.pos_list}")
print()

bbox = nmos.get_bbox()
print(f"✓ NMOS transistor complete")
print(f"  Total bounding box: {bbox}")
print(f"  Dimensions: {bbox[2] - bbox[0]} x {bbox[3] - bbox[1]}")
print()

# Visualize
fig = nmos.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/nmos_with_contacts.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved visualization to demo_outputs/nmos_with_contacts.png")
print()

# Export
nmos.export_gds('demo_outputs/nmos_with_contacts.gds')
print("✓ Exported to demo_outputs/nmos_with_contacts.gds")
print()

# ==============================================================================
# STEP 4: Create Well Ring
# ==============================================================================

print("STEP 4: Create Well Ring")
print("-" * 80)
print()

def create_well_ring_manual(inner_width=40, inner_height=40, ring_width=5):
    """Create well ring with manual positioning"""
    ring = Cell('well_ring')

    # Create 4 sides
    left = Polygon('left', 'nwell')
    right = Polygon('right', 'nwell')
    bottom = Polygon('bottom', 'nwell')
    top = Polygon('top', 'nwell')

    # Manually position
    # Left side
    left.pos_list = [0, 0, ring_width, inner_height + 2*ring_width]

    # Right side
    right.pos_list = [ring_width + inner_width, 0,
                     2*ring_width + inner_width, inner_height + 2*ring_width]

    # Bottom side
    bottom.pos_list = [ring_width, 0, ring_width + inner_width, ring_width]

    # Top side
    top.pos_list = [ring_width, ring_width + inner_height,
                   ring_width + inner_width, 2*ring_width + inner_height]

    ring.add_polygon([left, right, bottom, top])
    return ring

print("Creating well ring (40x40 opening, 5 width)...")
well_ring = create_well_ring_manual(inner_width=40, inner_height=40, ring_width=5)

bbox = well_ring.get_bbox()
print(f"  Well ring bbox: {bbox}")
print(f"  Outer dimensions: {bbox[2] - bbox[0]} x {bbox[3] - bbox[1]}")
print()

# Freeze well ring
well_ring.freeze_layout()
print(f"✓ Well ring frozen: {well_ring.is_frozen()}")
print()

# Visualize
fig = well_ring.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/well_ring.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved visualization to demo_outputs/well_ring.png")
print()

# ==============================================================================
# STEP 5: Create Complete Device (NMOS + Well Ring)
# ==============================================================================

print("STEP 5: Assemble Complete Device")
print("-" * 80)
print()

# Freeze NMOS
print("Freezing NMOS transistor...")
nmos.freeze_layout()
print(f"✓ NMOS frozen: {nmos.is_frozen()}")
print()

print("Creating complete device...")
complete_device = Cell('complete_nmos_with_well')

# Create instances
nmos_inst = CellInstance('nmos', nmos)
well_inst = CellInstance('well', well_ring)

# Position manually (both are frozen)
# Well is 50x50, NMOS bbox is (0,3) to (30,29) = 30x26
well_inst.pos_list = [0, 0, 50, 50]  # Well at origin
nmos_inst.pos_list = [10, 12, 40, 38]  # NMOS centered in well (5 units padding on each side)

complete_device.add_instance([well_inst, nmos_inst])

bbox = complete_device.get_bbox()
print(f"✓ Complete device assembled")
print(f"  Bounding box: {bbox}")
print(f"  Dimensions: {bbox[2] - bbox[0]} x {bbox[3] - bbox[1]}")
print()

# Visualize
fig = complete_device.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/complete_device.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved visualization to demo_outputs/complete_device.png")
print()

# Export
complete_device.export_gds('demo_outputs/complete_device.gds')
print("✓ Exported to demo_outputs/complete_device.gds")
print()

# ==============================================================================
# STEP 6: Create Device Array
# ==============================================================================

print("STEP 6: Create 2x2 Device Array")
print("-" * 80)
print()

# Freeze complete device
complete_device.freeze_layout()
print(f"✓ Complete device frozen: {complete_device.is_frozen()}")
print()

print("Creating 2x2 array of frozen devices...")
device_array = Cell('device_array_2x2')

# Create 4 instances
devices = []
spacing = 10
device_width = 50
device_height = 50

for i in range(2):
    for j in range(2):
        inst = CellInstance(f'device_r{i}_c{j}', complete_device)

        # Position in grid
        x = j * (device_width + spacing)
        y = i * (device_height + spacing)
        inst.pos_list = [x, y, x + device_width, y + device_height]

        devices.append(inst)
        device_array.add_instance(inst)

bbox = device_array.get_bbox()
print(f"✓ Device array created")
print(f"  Array bbox: {bbox}")
print(f"  Array dimensions: {bbox[2] - bbox[0]} x {bbox[3] - bbox[1]}")
print()

# Visualize
fig = device_array.draw(solve_first=False, show=False)
plt.savefig('demo_outputs/device_array.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Saved visualization to demo_outputs/device_array.png")
print()

# Export
device_array.export_gds('demo_outputs/device_array.gds')
print("✓ Exported to demo_outputs/device_array.gds")
print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("=" * 80)
print("SUMMARY - Hierarchical Frozen Layout Workflow")
print("=" * 80)
print()
print("✅ Complete Hierarchy Built:")
print()
print("  Level 1: Contact Array (2x2)")
print("           └─ 4 contact squares (2x2 each, 2 spacing)")
print("           └─ Total size: 6x6 → FROZEN")
print()
print("  Level 2: NMOS Transistor")
print("           ├─ Diffusion layer (30x20)")
print("           ├─ Poly gate (8x26)")
print("           ├─ Metal source (8x12, with centered contacts)")
print("           └─ Metal drain (8x12, with centered contacts)")
print("           └─ Total size: 30x26 → FROZEN")
print()
print("  Level 3: Complete Device")
print("           ├─ Well ring (50x50 outer, 40x40 inner)")
print("           └─ NMOS transistor (centered with 5-unit padding)")
print("           └─ Total size: 50x50 → FROZEN")
print()
print("  Level 4: Device Array (2x2)")
print("           └─ 4 instances of frozen devices (10-unit spacing)")
print("           └─ Total size: 110x110")
print()
print("🎯 Key Workflow Steps:")
print()
print("  1. CREATE: Design basic building block (contact array)")
print("  2. POSITION: Set all coordinates (manual or solved)")
print("  3. FREEZE: Lock positions with freeze_layout()")
print("  4. REUSE: Use frozen block in higher-level designs")
print("  5. REPEAT: Build hierarchy of frozen blocks")
print()
print("💡 Benefits:")
print()
print("  • Modularity: Build complex from simple frozen blocks")
print("  • Performance: Frozen blocks don't need re-solving")
print("  • Consistency: Same pattern reused everywhere")
print("  • Hierarchy: Multiple levels of frozen abstractions")
print("  • IP Protection: Internal structure is locked")
print()
print("📁 Files Generated:")
print()
print("  • demo_outputs/contact_array_simple.{gds,png}")
print("  • demo_outputs/nmos_with_contacts.{gds,png}")
print("  • demo_outputs/well_ring.{gds,png}")
print("  • demo_outputs/complete_device.{gds,png}")
print("  • demo_outputs/device_array.{gds,png}")
print()
print("🎉 Contact Array → MOS → Well Ring → Device Array Complete!")
print("=" * 80)
