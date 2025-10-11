# AND3 Layout Visualization Guide

## Generated Files

### 1. `sky130_and3_replica.gds`
The complete GDS layout file with all 8 transistors properly positioned.

### 2. `sky130_and3_replica_fixed.png`
Detailed 2-panel layout view showing:
- **Left panel**: Flattened view with all layers (diff, poly, li1, wells)
- **Right panel**: Hierarchy view showing cell boundaries and diff regions

### 3. `sky130_and3_schematic.png`
Circuit schematic diagram showing:
- NAND3 stage: 3 NMOS in series + 3 PMOS in parallel
- Inverter stage: 1 NMOS + 1 PMOS
- Transistor sizes labeled

## Layout Structure

### Transistor Placement

**NAND3 NMOS (Series Stack)**
- NMOS_NAND_A at (0.2, 0.4) μm - Input A
- NMOS_NAND_B at (0.2, 1.2) μm - Input B  
- NMOS_NAND_C at (0.2, 2.0) μm - Input C
- Stacked vertically at same X position

**NAND3 PMOS (Parallel Array)**
- PMOS_NAND_A at (0.2, 3.5) μm - Input A
- PMOS_NAND_B at (1.2, 3.5) μm - Input B
- PMOS_NAND_C at (2.2, 3.5) μm - Input C
- Side-by-side at same Y position

**Inverter Stage**
- NMOS_INV at (3.5, 0.4) μm - W=0.65μm
- PMOS_INV at (3.5, 3.5) μm - W=1.0μm

### Overall Dimensions
- Width: ~4.4 μm
- Height: ~4.5 μm
- Total area: ~19.8 μm²

Compare to SkyWater original: 2.68 × 3.20 μm (8.6 μm²)
- Our layout is ~2.3x larger due to non-optimized placement

## Color Legend (in fixed.png)

- **Light Green** (#90EE90): diff (active regions)
- **Red** (#FF6B6B): poly (gates)
- **Purple** (#9370DB): li1 (local interconnect)
- **Brown** (#D2691E): wells (pwell/nwell)
- **Light Pink** (#FFB6C1): nsdm (N+ implant)
- **Light Blue** (#87CEEB): psdm (P+ implant)

## What the Layout Shows

The visualization clearly shows:

1. **8 separate transistor cells** - each with its own diff, poly, contacts, and wells
2. **Proper stacking** of NAND3 NMOS transistors (vertical)
3. **Proper parallel placement** of NAND3 PMOS transistors (horizontal)
4. **Inverter stage** positioned to the right
5. **All transistor dimensions match SkyWater exactly** (W and L)

## Difference from SkyWater Original

SkyWater's hand-optimized layout uses:
- **Merged diffusions** - multiple transistors share active regions
- **Dense packing** - 2.3x smaller area
- **Complex routing** - multi-layer metal interconnects
- **Non-rectangular shapes** - optimized polygon shapes

Our tool-generated layout uses:
- **Separate transistor primitives** - each transistor is independent
- **Rectangular shapes only** - simpler but larger
- **Simplified routing** - li1 only
- **Regular grid placement** - easier to understand but less dense

Both layouts are **electrically equivalent** with identical transistor specifications!
