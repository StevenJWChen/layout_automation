#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDS Import/Export Feature Demonstration

This example demonstrates how to:
1. Export cells to GDS format
2. Import GDS as fixed (frozen) layouts
3. Import GDS as constraint-capable (unfrozen) layouts
4. Build designs mixing imported and new cells
5. Create standard cell libraries from GDS files

Use Cases:
- Import existing GDS layouts as IP blocks
- Convert GDS to constraint-based format for editing
- Build libraries of standard cells from GDS files
- Integrate legacy designs into new workflows
"""

import os
from layout_automation.gds_cell import Cell, Polygon, CellInstance

# Create output directory
os.makedirs('demo_outputs', exist_ok=True)

print("="*70)
print("GDS IMPORT/EXPORT DEMONSTRATION")
print("="*70)
print()

# ==============================================================================
# STEP 1: Create and Export Standard Cells
# ==============================================================================

print("Step 1: Creating and Exporting Standard Cells")
print("-" * 70)

def create_buffer():
    """Create a simple buffer cell"""
    buffer = Cell('BUF_X1')
    nmos = Polygon('nmos', 'diff')
    pmos = Polygon('pmos', 'diff')
    poly = Polygon('poly', 'poly')

    buffer.add_polygon([nmos, pmos, poly])

    # Size constraints
    buffer.constrain(nmos, 'x2-x1=40, y2-y1=20')
    buffer.constrain(pmos, 'x2-x1=40, y2-y1=20')
    buffer.constrain(poly, 'x2-x1=5, y2-y1=50')

    # Position constraints
    buffer.constrain(nmos, 'sy2+10=oy1', pmos)  # Stack vertically
    buffer.constrain(nmos, 'sx1=ox1', pmos)     # Align left
    buffer.constrain(nmos, 'sx1=ox1', poly)     # Align with poly

    return buffer


def create_inverter():
    """Create a simple inverter cell"""
    inv = Cell('INV_X1')
    nmos = Polygon('nmos', 'diff')
    pmos = Polygon('pmos', 'diff')
    poly = Polygon('poly', 'poly')

    inv.add_polygon([nmos, pmos, poly])

    # Size constraints
    inv.constrain(nmos, 'x2-x1=30, y2-y1=15')
    inv.constrain(pmos, 'x2-x1=30, y2-y1=15')
    inv.constrain(poly, 'x2-x1=4, y2-y1=40')

    # Position
    inv.constrain(nmos, 'sy2+10=oy1', pmos)
    inv.constrain(nmos, 'sx1=ox1', pmos)
    inv.constrain(nmos, 'sx1+13=ox1', poly)

    return inv


# Create cells
print("Creating standard cells...")
buffer = create_buffer()
buffer_result = buffer.solver()

inverter = create_inverter()
inverter_result = inverter.solver()

if buffer_result:
    print(f"  ✓ BUF_X1 created, bbox: {buffer.get_bbox()}")
    buffer.export_gds('demo_outputs/BUF_X1.gds')
    print(f"    Exported to demo_outputs/BUF_X1.gds")
else:
    print(f"  ✗ BUF_X1 solver failed")

if inverter_result:
    print(f"  ✓ INV_X1 created, bbox: {inverter.get_bbox()}")
    inverter.export_gds('demo_outputs/INV_X1.gds')
    print(f"    Exported to demo_outputs/INV_X1.gds")
else:
    print(f"  ✗ INV_X1 solver failed")

print()

# ==============================================================================
# STEP 2: Import GDS as Frozen (Fixed) Standard Cells
# ==============================================================================

print("Step 2: Importing GDS as Frozen Standard Cells")
print("-" * 70)

# Import buffer as frozen standard cell
if os.path.exists('demo_outputs/BUF_X1.gds'):
    buf_frozen = Cell.from_gds('demo_outputs/BUF_X1.gds', freeze_imported=True)
    print(f"✓ Imported BUF_X1 as frozen standard cell")
    print(f"  Cell name: {buf_frozen.name}")
    print(f"  Is frozen: {buf_frozen.is_frozen()}")
    print(f"  Bbox: {buf_frozen.get_bbox()}")
    print(f"  Polygons: {len(buf_frozen.polygons)}")
else:
    print("✗ BUF_X1.gds not found")
    buf_frozen = None

# Import inverter as frozen standard cell
if os.path.exists('demo_outputs/INV_X1.gds'):
    inv_frozen = Cell.from_gds('demo_outputs/INV_X1.gds', freeze_imported=True)
    print(f"\n✓ Imported INV_X1 as frozen standard cell")
    print(f"  Cell name: {inv_frozen.name}")
    print(f"  Is frozen: {inv_frozen.is_frozen()}")
    print(f"  Bbox: {inv_frozen.get_bbox()}")
    print(f"  Polygons: {len(inv_frozen.polygons)}")
else:
    print("✗ INV_X1.gds not found")
    inv_frozen = None

print()

# ==============================================================================
# STEP 3: Build Circuit from Imported Standard Cells
# ==============================================================================

print("Step 3: Building Circuit from Imported Standard Cells")
print("-" * 70)

if buf_frozen and inv_frozen:
    # Create signal chain: INV -> BUF -> BUF -> INV
    signal_chain = Cell('signal_chain')

    # Create instances
    inv1 = CellInstance('inv1', inv_frozen)
    buf1 = CellInstance('buf1', buf_frozen)
    buf2 = CellInstance('buf2', buf_frozen)
    inv2 = CellInstance('inv2', inv_frozen)

    signal_chain.add_instance([inv1, buf1, buf2, inv2])

    # Position in a chain
    signal_chain.constrain(inv1, 'sx1=10, sy1=10')
    signal_chain.constrain(inv1, 'sx2+20=ox1, sy1=oy1', buf1)
    signal_chain.constrain(buf1, 'sx2+20=ox1, sy1=oy1', buf2)
    signal_chain.constrain(buf2, 'sx2+20=ox1, sy1=oy1', inv2)

    print("Solving signal chain...")
    result = signal_chain.solver()

    if result:
        print(f"✓ Signal chain solved")
        print(f"  inv1: {inv1.pos_list}")
        print(f"  buf1: {buf1.pos_list}")
        print(f"  buf2: {buf2.pos_list}")
        print(f"  inv2: {inv2.pos_list}")

        # Export the circuit
        signal_chain.export_gds('demo_outputs/signal_chain.gds')
        print(f"✓ Exported to demo_outputs/signal_chain.gds")

        # Visualize
        fig = signal_chain.draw(solve_first=False, show=False)
        import matplotlib.pyplot as plt
        plt.savefig('demo_outputs/signal_chain.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Visualization saved to demo_outputs/signal_chain.png")
    else:
        print("✗ Signal chain solver failed")
else:
    print("⚠ Skipping circuit - standard cells not available")

print()

# ==============================================================================
# STEP 4: Import GDS as Unfrozen for Editing
# ==============================================================================

print("Step 4: Importing GDS as Unfrozen for Editing")
print("-" * 70)

# Export a cell first
custom = Cell('custom_block')
c1 = Polygon('c1', 'metal1')
c2 = Polygon('c2', 'metal1')
custom.add_polygon([c1, c2])
custom.constrain(c1, 'x2-x1=50, y2-y1=30, x1=10, y1=10')
custom.constrain(c2, 'x2-x1=20, y2-y1=20, x1=70, y1=15')
custom.solver()
custom.export_gds('demo_outputs/custom_block.gds')
print(f"Created and exported custom_block.gds")

# Import as unfrozen
custom_unfrozen = Cell.from_gds('demo_outputs/custom_block.gds', freeze_imported=False)
print(f"✓ Imported custom_block as unfrozen")
print(f"  Is frozen: {custom_unfrozen.is_frozen()}")
print(f"  Polygons: {len(custom_unfrozen.polygons)}")

# Can add new constraints and re-solve
print("\nAdding new polygon to imported (unfrozen) cell...")
new_poly = Polygon('new', 'metal2')
custom_unfrozen.add_polygon(new_poly)
custom_unfrozen.constrain(new_poly, 'x2-x1=15, y2-y1=15, x1=40, y1=25')
result = custom_unfrozen.solver()
print(f"  Re-solved with new polygon: {result}")

if result:
    custom_unfrozen.export_gds('demo_outputs/custom_modified.gds')
    print(f"  ✓ Exported modified version to demo_outputs/custom_modified.gds")

print()

# ==============================================================================
# STEP 5: Create Standard Cell Library
# ==============================================================================

print("Step 5: Creating Standard Cell Library from GDS")
print("-" * 70)

# Library dictionary
std_cell_lib = {}

# Import all standard cells from GDS
gds_files = ['BUF_X1.gds', 'INV_X1.gds']

for gds_file in gds_files:
    path = os.path.join('demo_outputs', gds_file)
    if os.path.exists(path):
        cell = Cell.from_gds(path, freeze_imported=True)
        std_cell_lib[cell.name] = cell
        print(f"  ✓ {cell.name}: {cell.get_bbox()}")

print(f"\n✓ Standard cell library created with {len(std_cell_lib)} cells")

# Use library to build a design
if len(std_cell_lib) > 0:
    print("\nBuilding design from library...")
    lib_circuit = Cell('lib_circuit')

    # Create 2x2 grid of alternating cells
    cell_types = list(std_cell_lib.values())
    instances = []

    for row in range(2):
        for col in range(2):
            cell_type = cell_types[(row + col) % len(cell_types)]
            inst = CellInstance(f'cell_r{row}_c{col}', cell_type)
            instances.append((row, col, inst))
            lib_circuit.add_instance(inst)

    # Position in grid
    spacing_x = 25
    spacing_y = 20

    for row, col, inst in instances:
        if row == 0 and col == 0:
            lib_circuit.constrain(inst, 'sx1=5, sy1=5')
        elif col == 0:
            prev = instances[(row-1) * 2][2]
            lib_circuit.constrain(prev, f'sy2+{spacing_y}=oy1, sx1=ox1', inst)
        else:
            prev = instances[row * 2 + col - 1][2]
            lib_circuit.constrain(prev, f'sx2+{spacing_x}=ox1, sy1=oy1', inst)

    result = lib_circuit.solver()
    if result:
        print(f"  ✓ Library circuit solved ({len(instances)} cells)")
        lib_circuit.export_gds('demo_outputs/lib_circuit.gds')
        print(f"  ✓ Exported to demo_outputs/lib_circuit.gds")
    else:
        print("  ✗ Library circuit solver failed")

print()

# ==============================================================================
# STEP 6: Compare Frozen vs Unfrozen Performance
# ==============================================================================

print("Step 6: Performance Comparison - Frozen vs Unfrozen")
print("-" * 70)

import time

if buf_frozen:
    # Array size
    n = 4  # 4x4 = 16 cells

    # Create array with frozen cells
    print(f"Creating {n}x{n} array with frozen cells...")
    array_frozen = Cell('array_frozen')
    insts_frozen = []

    for i in range(n*n):
        inst = CellInstance(f'buf{i}', buf_frozen)
        insts_frozen.append(inst)
        array_frozen.add_instance(inst)

    # Simple row layout
    for i, inst in enumerate(insts_frozen):
        if i == 0:
            array_frozen.constrain(inst, 'sx1=5, sy1=5')
        else:
            array_frozen.constrain(insts_frozen[i-1], 'sx2+10=ox1, sy1=oy1', inst)

    start = time.time()
    result_frozen = array_frozen.solver()
    time_frozen = time.time() - start

    print(f"  Frozen array solve time: {time_frozen:.3f}s")
    print(f"  Result: {result_frozen}")

    # Create array with unfrozen cells (slower)
    if os.path.exists('demo_outputs/BUF_X1.gds'):
        print(f"\nCreating {n}x{n} array with unfrozen cells...")
        buf_unfrozen = Cell.from_gds('demo_outputs/BUF_X1.gds', freeze_imported=False)

        array_unfrozen = Cell('array_unfrozen')
        insts_unfrozen = []

        for i in range(n*n):
            inst = CellInstance(f'buf{i}', buf_unfrozen)
            insts_unfrozen.append(inst)
            array_unfrozen.add_instance(inst)

        for i, inst in enumerate(insts_unfrozen):
            if i == 0:
                array_unfrozen.constrain(inst, 'sx1=5, sy1=5')
            else:
                array_unfrozen.constrain(insts_unfrozen[i-1], 'sx2+10=ox1, sy1=oy1', inst)

        start = time.time()
        result_unfrozen = array_unfrozen.solver()
        time_unfrozen = time.time() - start

        print(f"  Unfrozen array solve time: {time_unfrozen:.3f}s")
        print(f"  Result: {result_unfrozen}")

        if time_frozen > 0:
            speedup = time_unfrozen / time_frozen
            print(f"\n  ⚡ Speedup with frozen cells: {speedup:.1f}x")

print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("="*70)
print("SUMMARY")
print("="*70)
print()
print("✓ Standard cells created and exported to GDS")
print("✓ GDS files imported as frozen (fixed) layouts")
print("✓ GDS files imported as unfrozen (editable) layouts")
print("✓ Circuits built from imported standard cells")
print("✓ Standard cell library created from GDS files")
print("✓ Performance benefit demonstrated")
print()
print("Key Features:")
print("  • Export any cell to GDS format")
print("  • Import GDS as frozen (for reuse) or unfrozen (for editing)")
print("  • Cell.from_gds() - convenient class method")
print("  • Automatic freezing of subcells in hierarchies")
print("  • Mix imported and newly created cells")
print()
print("Files generated in demo_outputs/:")
print("  • BUF_X1.gds - Buffer standard cell")
print("  • INV_X1.gds - Inverter standard cell")
print("  • signal_chain.gds - Circuit from imported cells")
print("  • custom_block.gds - Original custom cell")
print("  • custom_modified.gds - Modified imported cell")
print("  • lib_circuit.gds - Design from cell library")
print("  • signal_chain.png - Visualization")
print()
print("🎉 GDS import/export demonstration complete!")
print("="*70)
