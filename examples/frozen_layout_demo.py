#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frozen Layout Feature Demonstration

This example demonstrates how to create standard cells with fixed layouts,
then reuse them as building blocks in larger designs.

Use Cases:
1. Standard cell libraries (inverters, NAND gates, etc.)
2. Parameterized blocks (repeated structures)
3. IP blocks with fixed internal routing
4. Memory cells and other repeated structures
"""

from layout_automation.gds_cell import Cell, Polygon, CellInstance
import matplotlib.pyplot as plt

print("="*70)
print("FROZEN LAYOUT FEATURE DEMONSTRATION")
print("="*70)
print()

# ==============================================================================
# STEP 1: Create a Standard Cell Library
# ==============================================================================

print("Step 1: Creating Standard Cell Library")
print("-" * 70)

def create_buffer_cell():
    """Create a simple buffer standard cell"""
    buffer = Cell('buffer_std')

    # Add polygons for transistors
    nmos1 = Polygon('nmos1', 'diff')
    nmos2 = Polygon('nmos2', 'diff')
    pmos1 = Polygon('pmos1', 'diff')
    pmos2 = Polygon('pmos2', 'diff')

    buffer.add_polygon([nmos1, nmos2, pmos1, pmos2])

    # Define sizes
    buffer.constrain(nmos1, 'x2-x1=30, y2-y1=15')
    buffer.constrain(nmos2, 'x2-x1=30, y2-y1=15')
    buffer.constrain(pmos1, 'x2-x1=30, y2-y1=15')
    buffer.constrain(pmos2, 'x2-x1=30, y2-y1=15')

    # Stack vertically
    buffer.constrain(nmos1, 'sy2+5=oy1', nmos2)
    buffer.constrain(nmos2, 'sy2+10=oy1', pmos1)
    buffer.constrain(pmos1, 'sy2+5=oy1', pmos2)

    # Align left edges
    buffer.constrain(nmos1, 'sx1=ox1', nmos2)
    buffer.constrain(nmos1, 'sx1=ox1', pmos1)
    buffer.constrain(nmos1, 'sx1=ox1', pmos2)

    return buffer


def create_and_gate_cell():
    """Create an AND gate standard cell"""
    and_gate = Cell('and_std')

    # Input stage (NAND)
    nand_n1 = Polygon('nand_n1', 'diff')
    nand_n2 = Polygon('nand_n2', 'diff')
    nand_p1 = Polygon('nand_p1', 'diff')
    nand_p2 = Polygon('nand_p2', 'diff')

    # Output stage (inverter)
    inv_n = Polygon('inv_n', 'diff')
    inv_p = Polygon('inv_p', 'diff')

    and_gate.add_polygon([nand_n1, nand_n2, nand_p1, nand_p2, inv_n, inv_p])

    # NAND stage sizing
    and_gate.constrain(nand_n1, 'x2-x1=20, y2-y1=12')
    and_gate.constrain(nand_n2, 'x2-x1=20, y2-y1=12')
    and_gate.constrain(nand_p1, 'x2-x1=20, y2-y1=12')
    and_gate.constrain(nand_p2, 'x2-x1=20, y2-y1=12')

    # Inverter sizing
    and_gate.constrain(inv_n, 'x2-x1=15, y2-y1=12')
    and_gate.constrain(inv_p, 'x2-x1=15, y2-y1=12')

    # Stack NAND transistors
    and_gate.constrain(nand_n1, 'sy2+3=oy1', nand_n2)
    and_gate.constrain(nand_n2, 'sy2+8=oy1', nand_p1)
    and_gate.constrain(nand_p1, 'sy2+3=oy1', nand_p2)

    # Position inverter to the right
    and_gate.constrain(nand_n1, 'sx2+10=ox1', inv_n)
    and_gate.constrain(inv_n, 'sy2+8=oy1', inv_p)

    # Align
    and_gate.constrain(nand_n1, 'sx1=ox1', nand_n2)
    and_gate.constrain(nand_n1, 'sx1=ox1', nand_p1)
    and_gate.constrain(nand_n1, 'sx1=ox1', nand_p2)
    and_gate.constrain(inv_n, 'sx1=ox1', inv_p)

    return and_gate


# Create standard cells
print("Creating BUFFER standard cell...")
buffer_cell = create_buffer_cell()
result = buffer_cell.solver()
if result:
    buffer_cell.freeze_layout()
    bbox = buffer_cell.get_bbox()
    print(f"  ✓ BUFFER created and frozen: {bbox}")
else:
    print("  ✗ BUFFER solver failed")

print("\nCreating AND gate standard cell...")
and_cell = create_and_gate_cell()
result = and_cell.solver()
if result:
    and_cell.freeze_layout()
    bbox = and_cell.get_bbox()
    print(f"  ✓ AND gate created and frozen: {bbox}")
else:
    print("  ✗ AND gate solver failed")

print()

# ==============================================================================
# STEP 2: Build a Circuit Using Standard Cells
# ==============================================================================

print("Step 2: Building Circuit from Standard Cells")
print("-" * 70)

# Create top-level design
circuit = Cell('signal_chain')

# Add buffer chain (3 buffers)
buf1 = CellInstance('buf1', buffer_cell)
buf2 = CellInstance('buf2', buffer_cell)
buf3 = CellInstance('buf3', buffer_cell)

# Add AND gates
and1 = CellInstance('and1', and_cell)
and2 = CellInstance('and2', and_cell)

circuit.add_instance([buf1, buf2, buf3, and1, and2])

# Constrain the circuit layout
# Buffer chain in a row
circuit.constrain(buf1, 'sx1=10, sy1=10')
circuit.constrain(buf1, 'sx2+15=ox1, sy1=oy1', buf2)
circuit.constrain(buf2, 'sx2+15=ox1, sy1=oy1', buf3)

# AND gates below the buffer chain
circuit.constrain(buf1, 'sx1=ox1, sy2+20=oy1', and1)
circuit.constrain(and1, 'sx2+15=ox1, sy1=oy1', and2)

print("Solving circuit layout (only instance positions)...")
result = circuit.solver()

if result:
    print(f"  ✓ Circuit solved successfully")
    print(f"  buf1: {buf1.pos_list}")
    print(f"  buf2: {buf2.pos_list}")
    print(f"  buf3: {buf3.pos_list}")
    print(f"  and1: {and1.pos_list}")
    print(f"  and2: {and2.pos_list}")

    # Calculate total area
    bbox = circuit.get_bbox()
    if bbox:
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        area = width * height
        print(f"\n  Circuit bounding box: {bbox}")
        print(f"  Total area: {area:.1f} square units")
else:
    print("  ✗ Circuit solver failed")

print()

# ==============================================================================
# STEP 3: Create Parametric Array
# ==============================================================================

print("Step 3: Creating Parametric Array of Standard Cells")
print("-" * 70)

# Create an array of 2x3 buffers
array = Cell('buffer_array_2x3')

# Create instances
buffer_instances = []
for row in range(2):
    for col in range(3):
        inst = CellInstance(f'buf_r{row}_c{col}', buffer_cell)
        buffer_instances.append((row, col, inst))
        array.add_instance(inst)

# Position in grid
spacing_x = 15
spacing_y = 20

for row, col, inst in buffer_instances:
    if row == 0 and col == 0:
        # Anchor first cell
        array.constrain(inst, 'sx1=5, sy1=5')
    elif col == 0:
        # First column: stack vertically
        prev_inst = buffer_instances[(row-1) * 3][2]
        array.constrain(prev_inst, f'sy2+{spacing_y}=oy1, sx1=ox1', inst)
    else:
        # Other columns: place to the right
        prev_inst = buffer_instances[row * 3 + col - 1][2]
        array.constrain(prev_inst, f'sx2+{spacing_x}=ox1, sy1=oy1', inst)

print(f"Solving {len(buffer_instances)} buffer array...")
result = array.solver()

if result:
    print(f"  ✓ Array solved successfully")
    print(f"  First buffer: {buffer_instances[0][2].pos_list}")
    print(f"  Last buffer:  {buffer_instances[-1][2].pos_list}")

    bbox = array.get_bbox()
    if bbox:
        print(f"  Array bounding box: {bbox}")
else:
    print("  ✗ Array solver failed")

print()

# ==============================================================================
# STEP 4: Hierarchical Design with Mixed Frozen/Unfrozen
# ==============================================================================

print("Step 4: Hierarchical Design with Mixed Cells")
print("-" * 70)

# Create a custom routing cell (not frozen)
routing = Cell('custom_routing')
route1 = Polygon('route1', 'metal1')
route2 = Polygon('route2', 'metal1')
via = Polygon('via', 'via')
routing.add_polygon([route1, route2, via])

# Define routing with constraints
routing.constrain(route1, 'x2-x1=50, y2-y1=3')
routing.constrain(route2, 'x2-x1=3, y2-y1=30')
routing.constrain(route1, 'sx2=ox1, sy1=oy1', via)  # Via at route1 end
routing.constrain(via, 'x2-x1=3, y2-y1=3')

# Create top design mixing frozen and unfrozen
mixed_design = Cell('mixed_design')

# Add frozen standard cell
std_inst = CellInstance('standard_buf', buffer_cell)

# Add unfrozen routing
route_inst = CellInstance('routing', routing)

mixed_design.add_instance([std_inst, route_inst])

# Position: routing connects to standard cell
mixed_design.constrain(std_inst, 'sx1=10, sy1=20')
mixed_design.constrain(std_inst, 'sx2+5=ox1, sy1=oy1', route_inst)

print("Solving mixed frozen/unfrozen design...")
result = mixed_design.solver()

if result:
    print(f"  ✓ Mixed design solved")
    print(f"  Standard cell: {std_inst.pos_list}")
    print(f"  Routing block: {route_inst.pos_list}")
    print(f"  route1 (unfrozen): {route1.pos_list}")
    print(f"  route2 (unfrozen): {route2.pos_list}")
else:
    print("  ✗ Mixed design solver failed")

print()

# ==============================================================================
# STEP 5: Visualizations
# ==============================================================================

print("Step 5: Generating Visualizations")
print("-" * 70)

# Visualize the circuit
fig1 = circuit.draw(solve_first=False, show=False)
plt.savefig('frozen_circuit.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Circuit visualization saved to frozen_circuit.png")

# Visualize the array
fig2 = array.draw(solve_first=False, show=False)
plt.savefig('frozen_array.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Array visualization saved to frozen_array.png")

# Visualize the mixed design
fig3 = mixed_design.draw(solve_first=False, show=False)
plt.savefig('frozen_mixed.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Mixed design visualization saved to frozen_mixed.png")

print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("="*70)
print("SUMMARY")
print("="*70)
print()
print("Frozen Layout Feature Benefits:")
print("  ✓ Create reusable standard cells")
print("  ✓ Build complex circuits from simple blocks")
print("  ✓ Maintain fixed internal layouts")
print("  ✓ Mix frozen and unfrozen cells in hierarchies")
print("  ✓ Significantly reduce constraint solving complexity")
print()
print("Applications:")
print("  • Standard cell libraries (logic gates)")
print("  • Parametric arrays (memory, registers)")
print("  • IP blocks with fixed routing")
print("  • Hierarchical design flows")
print()
print("Key Methods:")
print("  • cell.freeze_layout()     - Freeze after solving")
print("  • cell.unfreeze_layout()   - Allow re-solving")
print("  • cell.is_frozen()         - Check freeze status")
print("  • cell.get_bbox()          - Get bounding box")
print()
print("🎉 Frozen layout demonstration complete!")
print("="*70)
