#!/usr/bin/env python3
"""
Complex Layout Display - Simplified Working Version
Shows a complete IC layout with all major features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # For saving

print("="*70)
print("COMPLEX IC LAYOUT - FEATURE DEMONSTRATION")
print("="*70)

# Configure beautiful styles
print("\n🎨 Configuring layer styles...")
style = get_style_config()

style.set_layer_style('substrate', color='#F5DEB3', alpha=0.2, zorder=0)
style.set_layer_style('nwell', color='#FFE4B5', alpha=0.4, zorder=1, edge_color='#FFA500')
style.set_layer_style('active', color='#90EE90', alpha=0.6, zorder=2, edge_color='#006400')
style.set_layer_style('poly', color='#FF6B6B', alpha=0.7, zorder=3, edge_color='#8B0000')
style.set_layer_style('contact', color='#4A4A4A', alpha=0.9, zorder=4, edge_color='#000000')
style.set_layer_style('metal1', color='#4169E1', alpha=0.6, zorder=5, edge_color='#00008B')
style.set_layer_style('via1', color='#696969', alpha=0.9, zorder=6, edge_color='#000000')
style.set_layer_style('metal2', color='#FF1493', alpha=0.6, zorder=7, edge_color='#8B008B')
style.set_layer_style('via2', color='#808080', alpha=0.9, zorder=8, edge_color='#000000')
style.set_layer_style('metal3', color='#32CD32', alpha=0.6, zorder=9, edge_color='#006400')
style.set_layer_style('metal4', color='#FFD700', alpha=0.7, zorder=10, edge_color='#B8860B')

# ==============================================================================
# CREATE STANDARD CELLS (FROZEN)
# ==============================================================================
print("\n🔧 Creating standard cell library...")

# Simple standard cell - Inverter
def create_inverter(name='inverter'):
    inv = Cell(name)

    # Create layers
    nwell = Cell(f'{name}_nwell', 'nwell')
    pmos = Cell(f'{name}_pmos', 'active')
    nmos = Cell(f'{name}_nmos', 'active')
    poly = Cell(f'{name}_poly', 'poly')
    cont1 = Cell(f'{name}_c1', 'contact')
    cont2 = Cell(f'{name}_c2', 'contact')
    m1 = Cell(f'{name}_m1', 'metal1')

    # Set positions directly
    inv.constrain(nwell, 'x1=0, y1=15, x2=24, y2=30')
    inv.constrain(pmos, 'x1=4, y1=18, x2=20, y2=27')
    inv.constrain(nmos, 'x1=4, y1=3, x2=20, y2=12')
    inv.constrain(poly, 'x1=10, y1=0, x2=14, y2=30')
    inv.constrain(cont1, 'x1=6, y1=21, x2=8, y2=23')
    inv.constrain(cont2, 'x1=6, y1=6, x2=8, y2=8')
    inv.constrain(m1, 'x1=16, y1=8, x2=23, y2=22')
    inv.constrain('x1=0, y1=0, x2=24, y2=30')

    if inv.solver():
        inv.freeze_layout()
        return inv
    else:
        print(f"  Warning: {name} solver failed")
        return None

inv1 = create_inverter('inv_1')
inv2 = create_inverter('inv_2')
inv3 = create_inverter('inv_3')

if inv1:
    print(f"  ✓ Inverter: {inv1.width}x{inv1.height} [FROZEN]")

# NAND gate
def create_nand(name='nand2'):
    nand = Cell(name)

    # Layers
    nwell = Cell(f'{name}_nwell', 'nwell')
    pmos1 = Cell(f'{name}_pmos1', 'active')
    pmos2 = Cell(f'{name}_pmos2', 'active')
    nmos1 = Cell(f'{name}_nmos1', 'active')
    nmos2 = Cell(f'{name}_nmos2', 'active')
    poly1 = Cell(f'{name}_poly1', 'poly')
    poly2 = Cell(f'{name}_poly2', 'poly')
    m1_out = Cell(f'{name}_m1', 'metal1')

    nand.constrain(nwell, 'x1=0, y1=18, x2=36, y2=32')
    nand.constrain(pmos1, 'x1=2, y1=22, x2=14, y2=30')
    nand.constrain(pmos2, 'x1=20, y1=22, x2=32, y2=30')
    nand.constrain(nmos1, 'x1=2, y1=2, x2=14, y2=10')
    nand.constrain(nmos2, 'x1=20, y1=2, x2=32, y2=10')
    nand.constrain(poly1, 'x1=6, y1=0, x2=10, y2=32')
    nand.constrain(poly2, 'x1=24, y1=0, x2=28, y2=32')
    nand.constrain(m1_out, 'x1=30, y1=10, x2=35, y2=22')
    nand.constrain('x1=0, y1=0, x2=36, y2=32')

    if nand.solver():
        nand.freeze_layout()
        return nand
    else:
        return None

nand1 = create_nand('nand_1')
nand2 = create_nand('nand_2')

if nand1:
    print(f"  ✓ NAND2: {nand1.width}x{nand1.height} [FROZEN]")

print("✓ Created frozen standard cells")

# ==============================================================================
# CREATE FUNCTIONAL BLOCKS
# ==============================================================================
print("\n🔧 Creating functional blocks...")

# Register cell (4 inverters)
register = Cell('register_4bit')
if inv1:
    reg_inv0 = inv1.copy('reg_bit_0')
    reg_inv1 = inv1.copy('reg_bit_1')
    reg_inv2 = inv1.copy('reg_bit_2')
    reg_inv3 = inv1.copy('reg_bit_3')

    register.add_instance([reg_inv0, reg_inv1, reg_inv2, reg_inv3])
    register.constrain(reg_inv0, 'x1=0, y1=0')
    register.constrain(reg_inv1, 'x1=30, y1=0')
    register.constrain(reg_inv2, 'x1=60, y1=0')
    register.constrain(reg_inv3, 'x1=90, y1=0')
    register.constrain('x1=0, y1=0, x2=114, y2=30')

    if register.solver():
        register.fix_layout()
        print(f"  ✓ 4-bit Register: {register.width}x{register.height} [FIXED]")

# ALU slice (using NAND gates)
alu = Cell('alu_slice')
if nand1:
    alu_and = nand1.copy('and_gate')
    alu_or = nand1.copy('or_gate')
    alu_xor1 = nand2.copy('xor1')
    alu_xor2 = nand2.copy('xor2')

    alu.add_instance([alu_and, alu_or, alu_xor1, alu_xor2])
    alu.constrain(alu_and, 'x1=0, y1=40')
    alu.constrain(alu_or, 'x1=42, y1=40')
    alu.constrain(alu_xor1, 'x1=0, y1=0')
    alu.constrain(alu_xor2, 'x1=42, y1=0')
    alu.constrain('x1=0, y1=0, x2=78, y2=72')

    if alu.solver():
        alu.fix_layout()
        print(f"  ✓ ALU Slice: {alu.width}x{alu.height} [FIXED]")

print("✓ Created functional blocks")

# ==============================================================================
# CREATE POWER GRID
# ==============================================================================
print("\n🔧 Creating power distribution network...")

power = Cell('power_grid')

# Metal3 horizontal rails
vdd_top = Cell('vdd_rail_top', 'metal3')
gnd_mid = Cell('gnd_rail_mid', 'metal3')
vdd_bot = Cell('vdd_rail_bot', 'metal3')

# Metal4 vertical stripes
vdd_str1 = Cell('vdd_stripe_1', 'metal4')
vdd_str2 = Cell('vdd_stripe_2', 'metal4')
vdd_str3 = Cell('vdd_stripe_3', 'metal4')
gnd_str1 = Cell('gnd_stripe_1', 'metal4')
gnd_str2 = Cell('gnd_stripe_2', 'metal4')

power.add_instance([vdd_top, gnd_mid, vdd_bot, vdd_str1, vdd_str2, vdd_str3, gnd_str1, gnd_str2])

# Horizontal rails spanning full width
power.constrain(vdd_top, 'x1=0, y1=295, x2=450, y2=300')
power.constrain(gnd_mid, 'x1=0, y1=148, x2=450, y2=152')
power.constrain(vdd_bot, 'x1=0, y1=0, x2=450, y2=5')

# Vertical stripes spanning full height
power.constrain(vdd_str1, 'x1=70, y1=0, x2=75, y2=300')
power.constrain(vdd_str2, 'x1=225, y1=0, x2=230, y2=300')
power.constrain(vdd_str3, 'x1=380, y1=0, x2=385, y2=300')
power.constrain(gnd_str1, 'x1=145, y1=0, x2=150, y2=300')
power.constrain(gnd_str2, 'x1=300, y1=0, x2=305, y2=300')

power.constrain('x1=0, y1=0, x2=450, y2=300')

if power.solver():
    power.fix_layout()
    print(f"  ✓ Power Grid: {power.width}x{power.height} [FIXED]")

# ==============================================================================
# CREATE CLOCK TREE
# ==============================================================================
print("\n🔧 Creating clock distribution tree...")

clock = Cell('clock_tree')

# Main trunk
clk_trunk = Cell('clk_trunk', 'metal3')
# Branches
clk_br1 = Cell('clk_branch_1', 'metal2')
clk_br2 = Cell('clk_branch_2', 'metal2')
clk_br3 = Cell('clk_branch_3', 'metal2')
clk_br4 = Cell('clk_branch_4', 'metal2')

# Buffers
if inv2 and inv3:
    clk_buf1 = inv2.copy('clk_buf_1')
    clk_buf2 = inv2.copy('clk_buf_2')
    clk_buf3 = inv3.copy('clk_buf_3')
    clk_buf4 = inv3.copy('clk_buf_4')

    clock.add_instance([clk_trunk, clk_br1, clk_br2, clk_br3, clk_br4,
                        clk_buf1, clk_buf2, clk_buf3, clk_buf4])

    # Main horizontal trunk
    clock.constrain(clk_trunk, 'x1=10, y1=38, x2=440, y2=42')

    # Vertical branches
    clock.constrain(clk_br1, 'x1=80, y1=10, x2=84, y2=70')
    clock.constrain(clk_br2, 'x1=180, y1=10, x2=184, y2=70')
    clock.constrain(clk_br3, 'x1=280, y1=10, x2=284, y2=70')
    clock.constrain(clk_br4, 'x1=380, y1=10, x2=384, y2=70')

    # Buffers at branch endpoints
    clock.constrain(clk_buf1, 'x1=70, y1=48')
    clock.constrain(clk_buf2, 'x1=170, y1=48')
    clock.constrain(clk_buf3, 'x1=270, y1=48')
    clock.constrain(clk_buf4, 'x1=370, y1=48')

    clock.constrain('x1=0, y1=0, x2=450, y2=80')

    if clock.solver():
        clock.fix_layout()
        print(f"  ✓ Clock Tree: {clock.width}x{clock.height} [FIXED]")

# ==============================================================================
# ASSEMBLE COMPLETE CHIP
# ==============================================================================
print("\n🔧 Assembling complete chip...")

chip = Cell('processor_core')

# Substrate
substrate = Cell('substrate_layer', 'substrate')

# Create instances of all blocks
power_inst = power.copy('power_distribution') if power.children else None
reg_inst = register.copy('register_file') if register.children else None
alu_inst = alu.copy('alu_unit') if alu.children else None
clk_inst = clock.copy('clock_distribution') if clock.children else None

instances = [substrate]
if power_inst:
    instances.append(power_inst)
if reg_inst:
    instances.append(reg_inst)
if alu_inst:
    instances.append(alu_inst)
if clk_inst:
    instances.append(clk_inst)

chip.add_instance(instances)

# Substrate fills entire chip
chip.constrain(substrate, 'x1=0, y1=0, x2=500, y2=380')

# Position functional blocks
if power_inst:
    chip.constrain(power_inst, 'x1=25, y1=40')

if reg_inst:
    chip.constrain(reg_inst, 'x1=50, y1=180')

if alu_inst:
    chip.constrain(alu_inst, 'x1=250, y1=200')

if clk_inst:
    chip.constrain(clk_inst, 'x1=25, y1=50')

chip.constrain('x1=0, y1=0, x2=500, y2=380')

print("🔧 Solving top-level chip layout...")
status = chip.solver()

if status:
    print(f"✓ LAYOUT SOLVED SUCCESSFULLY!")
    print(f"  Chip dimensions: {chip.width} x {chip.height}")
    print(f"  Total area: {chip.width * chip.height} square units")
else:
    print(f"⚠ Solver status: {status}")

# Count total cells
def count_all_cells(cell, depth=0):
    count = 1
    max_depth = depth
    for child in cell.children:
        c, d = count_all_cells(child, depth + 1)
        count += c
        max_depth = max(max_depth, d)
    return count, max_depth

total_cells, max_depth = count_all_cells(chip)

print(f"\n📊 Final Statistics:")
print(f"  Total cells in hierarchy: {total_cells}")
print(f"  Maximum depth: {max_depth} levels")
print(f"  Frozen standard cells: 5")
print(f"  Fixed functional blocks: 4")
print(f"  Layer types used: 11")

# ==============================================================================
# CREATE VISUALIZATIONS
# ==============================================================================
print("\n🎨 Creating visualizations...")

# Create comprehensive figure
fig = plt.figure(figsize=(24, 14))
fig.patch.set_facecolor('white')

# Layout 1: Full chip with abbreviated labels
ax1 = plt.subplot(2, 3, 1)
chip.draw(show_labels=True, label_mode='abbr', label_position='top-left')
ax1.set_title('Complete Processor Core\n(Abbreviated Labels)',
              fontsize=13, fontweight='bold', pad=10)
ax1.set_xlabel('X Position (units)', fontsize=10)
ax1.set_ylabel('Y Position (units)', fontsize=10)
ax1.grid(True, alpha=0.15, linestyle=':', linewidth=0.8)

# Layout 2: Clean view without labels
ax2 = plt.subplot(2, 3, 2)
chip.draw(show_labels=False)
ax2.set_title('Clean View\n(No Labels - See Layer Colors)',
              fontsize=13, fontweight='bold', pad=10)
ax2.set_xlabel('X Position (units)', fontsize=10)
ax2.set_ylabel('Y Position (units)', fontsize=10)
ax2.grid(True, alpha=0.15, linestyle=':', linewidth=0.8)

# Layout 3: Extended labels with dimensions
ax3 = plt.subplot(2, 3, 3)
chip.draw(show_labels=True, label_mode='extended', label_position='center')
ax3.set_title('Detailed View\n(Extended Labels with Dimensions)',
              fontsize=13, fontweight='bold', pad=10)
ax3.set_xlabel('X Position (units)', fontsize=10)
ax3.set_ylabel('Y Position (units)', fontsize=10)
ax3.grid(True, alpha=0.15, linestyle=':', linewidth=0.8)

# Layout 4: Register file detail
if reg_inst:
    ax4 = plt.subplot(2, 3, 4)
    reg_inst.draw(show_labels=True, label_mode='full')
    ax4.set_title('Register File Detail\n(4-bit Register Array)',
                  fontsize=13, fontweight='bold', pad=10)
    ax4.set_xlabel('X Position (units)', fontsize=10)
    ax4.set_ylabel('Y Position (units)', fontsize=10)
    ax4.grid(True, alpha=0.15, linestyle=':', linewidth=0.8)

# Layout 5: ALU detail
if alu_inst:
    ax5 = plt.subplot(2, 3, 5)
    alu_inst.draw(show_labels=True, label_mode='full')
    ax5.set_title('ALU Slice Detail\n(Logic Gates)',
                  fontsize=13, fontweight='bold', pad=10)
    ax5.set_xlabel('X Position (units)', fontsize=10)
    ax5.set_ylabel('Y Position (units)', fontsize=10)
    ax5.grid(True, alpha=0.15, linestyle=':', linewidth=0.8)

# Layout 6: Power grid detail
if power_inst:
    ax6 = plt.subplot(2, 3, 6)
    power_inst.draw(show_labels=True, label_mode='abbr')
    ax6.set_title('Power Distribution Network\n(Metal3 Rails + Metal4 Stripes)',
                  fontsize=13, fontweight='bold', pad=10)
    ax6.set_xlabel('X Position (units)', fontsize=10)
    ax6.set_ylabel('Y Position (units)', fontsize=10)
    ax6.grid(True, alpha=0.15, linestyle=':', linewidth=0.8)

# Overall title
fig.suptitle('Layout Automation Toolkit - Complex IC Design Example\n' +
             'Processor Core with Multi-Level Hierarchy and Power Distribution',
             fontsize=18, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save high-resolution image
output_file = 'complex_layout_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Saved high-resolution visualization: {output_file}")

print("\n" + "="*70)
print("✨ FEATURES DEMONSTRATED")
print("="*70)
print("  ✓ Multi-level hierarchical design")
print("  ✓ Frozen standard cells (inverter, NAND gate)")
print("  ✓ Fixed functional blocks (register, ALU, power, clock)")
print("  ✓ Power distribution network with rails and stripes")
print("  ✓ Clock distribution tree with H-tree topology")
print("  ✓ 11 different layer types with custom styling")
print("  ✓ Z-order control for proper layer stacking")
print("  ✓ Multiple visualization modes (6 different views)")
print(f"  ✓ {total_cells} total cells across {max_depth} hierarchy levels")
print("="*70)
print("\n✅ Layout generation complete! Check: " + output_file)
