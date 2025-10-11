#!/usr/bin/env python3
"""Regenerate AND3 visualization with better settings"""

import gdstk
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection

# Read the GDS
lib = gdstk.read_gds('sky130_and3_replica.gds')

print("="*70)
print("AND3 GDS Structure")
print("="*70)

print(f"\nCells in GDS: {len(lib.cells)}")
for cell in lib.cells:
    print(f"  - {cell.name}: {len(cell.polygons)} polygons, {len(cell.references)} refs")

# Find top cell (the one with references)
top_cell = None
for cell in lib.cells:
    if len(cell.references) > 0:
        top_cell = cell
        break

if top_cell is None:
    print("\nNo top cell found with references, using first cell")
    top_cell = lib.cells[0]

print(f"\nTop cell: {top_cell.name}")
print(f"  References: {len(top_cell.references)}")

# Get all cells referenced
if top_cell.references:
    print(f"\n  Referenced cells:")
    for ref in top_cell.references:
        print(f"    - {ref.cell.name} at origin {ref.origin}")

# Layer color mapping
layer_colors = {
    65: '#90EE90',  # diff - light green
    66: '#FF6B6B',  # poly - red
    67: '#9370DB',  # li1 - purple
    64: '#D2691E',  # pwell/nwell - brown
    93: '#FFB6C1',  # nsdm - light pink
    94: '#87CEEB',  # psdm - light blue
}

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

# --- Plot 1: Flattened view (all polygons) ---
print("\nGenerating flattened view...")

all_polys = []
# Get polygons from top cell
for poly in top_cell.polygons:
    all_polys.append(('top', poly))

# Get polygons from referenced cells (with offset)
for ref in top_cell.references:
    origin = ref.origin
    for poly in ref.cell.polygons:
        # Create a copy with offset
        points = poly.points + origin
        new_poly = gdstk.Polygon(points, layer=poly.layer, datatype=poly.datatype)
        all_polys.append((ref.cell.name, new_poly))

print(f"Total polygons to draw: {len(all_polys)}")

# Draw flattened view
for cell_name, poly in all_polys:
    color = layer_colors.get(poly.layer, '#CCCCCC')
    pts = poly.points
    if len(pts) > 0:
        polygon = patches.Polygon(pts, closed=True,
                                 edgecolor='black', facecolor=color,
                                 alpha=0.6, linewidth=0.5)
        ax1.add_patch(polygon)

ax1.set_aspect('equal')
ax1.autoscale()
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('X (μm)')
ax1.set_ylabel('Y (μm)')
ax1.set_title('AND3 Layout - Flattened View (All Layers)')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#90EE90', edgecolor='black', label='diff (65)'),
    Patch(facecolor='#FF6B6B', edgecolor='black', label='poly (66)'),
    Patch(facecolor='#9370DB', edgecolor='black', label='li1 (67)'),
    Patch(facecolor='#D2691E', edgecolor='black', label='well (64)'),
]
ax1.legend(handles=legend_elements, loc='upper right')

# --- Plot 2: Hierarchy view (show cell boundaries) ---
print("Generating hierarchy view...")

# Draw cell boundaries
for ref in top_cell.references:
    bbox = ref.cell.bounding_box()
    if bbox:
        (x1, y1), (x2, y2) = bbox
        origin = ref.origin
        # Offset bbox by origin
        rect = patches.Rectangle((x1 + origin[0], y1 + origin[1]),
                                 x2 - x1, y2 - y1,
                                 linewidth=2, edgecolor='red',
                                 facecolor='none', linestyle='--')
        ax2.add_patch(rect)
        # Add label
        ax2.text(x1 + origin[0], y2 + origin[1] + 0.1,
                ref.cell.name, fontsize=8, color='red')

# Draw diff regions in each cell
for ref in top_cell.references:
    origin = ref.origin
    for poly in ref.cell.polygons:
        if poly.layer == 65:  # diff only for clarity
            color = layer_colors.get(poly.layer, '#CCCCCC')
            pts = poly.points + origin
            polygon = patches.Polygon(pts, closed=True,
                                     edgecolor='black', facecolor=color,
                                     alpha=0.8, linewidth=1)
            ax2.add_patch(polygon)

ax2.set_aspect('equal')
ax2.autoscale()
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('X (μm)')
ax2.set_ylabel('Y (μm)')
ax2.set_title('AND3 Layout - Hierarchy View (Cell Boundaries + Diff)')

plt.tight_layout()
plt.savefig('sky130_and3_replica_fixed.png', dpi=150, bbox_inches='tight')
print(f"\nSaved improved visualization to: sky130_and3_replica_fixed.png")
plt.close()

# Also create a simple schematic-style view
print("\nGenerating schematic-style transistor map...")
fig, ax = plt.subplots(figsize=(12, 8))

# Count transistor types
nmos_nand = []
pmos_nand = []
nmos_inv = []
pmos_inv = []

for cell in lib.cells:
    if 'NMOS_NAND' in cell.name:
        nmos_nand.append(cell.name)
    elif 'PMOS_NAND' in cell.name:
        pmos_nand.append(cell.name)
    elif 'NMOS_INV' in cell.name:
        nmos_inv.append(cell.name)
    elif 'PMOS_INV' in cell.name:
        pmos_inv.append(cell.name)

# Draw transistor blocks
y_pos = 5
x_start = 1

# NAND3 PMOS (parallel)
ax.text(x_start - 0.5, y_pos, 'NAND3 PMOS\n(parallel)', fontsize=10, ha='right')
for i, name in enumerate(pmos_nand):
    x = x_start + i * 2
    rect = patches.Rectangle((x, y_pos - 0.3), 1.5, 0.6,
                             facecolor='#FFB6C1', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(x + 0.75, y_pos, name.split('_')[-1], ha='center', va='center', fontsize=9)
    ax.text(x + 0.75, y_pos - 0.7, 'W=0.42μm', ha='center', fontsize=7)

# Intermediate node
y_pos -= 1.5
ax.plot([x_start, x_start + 6], [y_pos, y_pos], 'k-', linewidth=2)
ax.text(x_start + 3, y_pos + 0.2, 'NAND3_out', ha='center', fontsize=9, style='italic')

# NAND3 NMOS (series)
y_pos -= 1
ax.text(x_start - 0.5, y_pos, 'NAND3 NMOS\n(series)', fontsize=10, ha='right')
for i, name in enumerate(nmos_nand):
    y = y_pos - i * 1.2
    rect = patches.Rectangle((x_start + 2, y - 0.3), 1.5, 0.6,
                             facecolor='#90EE90', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(x_start + 2.75, y, name.split('_')[-1], ha='center', va='center', fontsize=9)
    ax.text(x_start + 4, y, 'W=0.42μm', ha='left', fontsize=7)

# Inverter stage
y_pos = 3
x_inv = x_start + 8

ax.text(x_inv - 0.5, y_pos + 1, 'INVERTER', fontsize=10, ha='right', weight='bold')

# Inv PMOS
rect = patches.Rectangle((x_inv, y_pos), 1.5, 0.8,
                         facecolor='#FFB6C1', edgecolor='black', linewidth=2)
ax.add_patch(rect)
ax.text(x_inv + 0.75, y_pos + 0.4, 'PMOS', ha='center', va='center', fontsize=9)
ax.text(x_inv + 0.75, y_pos - 0.5, 'W=1.0μm', ha='center', fontsize=7)

# Inv NMOS
y_pos -= 2
rect = patches.Rectangle((x_inv, y_pos), 1.5, 0.8,
                         facecolor='#90EE90', edgecolor='black', linewidth=2)
ax.add_patch(rect)
ax.text(x_inv + 0.75, y_pos + 0.4, 'NMOS', ha='center', va='center', fontsize=9)
ax.text(x_inv + 0.75, y_pos - 0.5, 'W=0.65μm', ha='center', fontsize=7)

# Output
ax.text(x_inv + 2, 2, 'X (output)', fontsize=11, weight='bold')

# Inputs
ax.text(x_start + 1, 6, 'A, B, C\n(inputs)', fontsize=11, weight='bold', ha='center')

ax.set_xlim(-1, 12)
ax.set_ylim(-2, 7)
ax.axis('off')
ax.set_title('AND3 Gate - Transistor Schematic', fontsize=14, weight='bold')

plt.tight_layout()
plt.savefig('sky130_and3_schematic.png', dpi=150, bbox_inches='tight')
print(f"Saved schematic view to: sky130_and3_schematic.png")
plt.close()

print("\n" + "="*70)
print("Visualization complete!")
print("="*70)
print("\nGenerated files:")
print("  1. sky130_and3_replica_fixed.png - Detailed layout view")
print("  2. sky130_and3_schematic.png - Transistor schematic diagram")
