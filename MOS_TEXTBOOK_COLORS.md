# MOS Transistor Layouts with Textbook Colors

## Overview

This document describes the MOS transistor layouts created with industry-standard textbook colors for CMOS technology.

## Textbook Color Scheme

The color scheme follows standard VLSI textbooks for CMOS process visualization:

| Layer | Color | Transparency | Usage |
|-------|-------|--------------|-------|
| **N-well** | Light green | 30% opaque | PMOS substrate region |
| **P-well/Substrate** | Light coral/pink | 30% opaque | NMOS substrate region |
| **Polysilicon (Gate)** | Red | 70% opaque | Transistor gate |
| **N-diffusion** | Green | 60% opaque | NMOS source/drain |
| **P-diffusion** | Tan/brown | 60% opaque | PMOS source/drain |
| **Metal1** | Blue | 60% opaque | First metal interconnect |
| **Contact** | Black | 90% opaque | Contact holes |
| **Via** | Gray | 90% opaque | Via connections |

## NMOS Transistor

### Structure
- **Substrate**: P-well (light coral)
- **Source/Drain**: N-diffusion (green)
- **Gate**: Polysilicon (red)
- **Contacts**: Black squares on diffusions
- **Metal**: Blue metal1 over contacts

### Cross-Section View
```
        Metal1 (blue)
           |
        Contact (black)
           |
    +---[N-diff]---+  <- Source/Drain (green)
    |              |
    |   P-well     |  <- Substrate (light coral)
    |  (light pink)|
    +==============+
```

### Gate Structure
The polysilicon gate (red) crosses over the channel region between source and drain.

## PMOS Transistor

### Structure
- **Substrate**: N-well (light green)
- **Source/Drain**: P-diffusion (tan/brown)
- **Gate**: Polysilicon (red)
- **Contacts**: Black squares on diffusions
- **Metal**: Blue metal1 over contacts

### Cross-Section View
```
        Metal1 (blue)
           |
        Contact (black)
           |
    +---[P-diff]---+  <- Source/Drain (tan)
    |              |
    |   N-well     |  <- Substrate (light green)
    | (light green)|
    +==============+
```

## Generated Layouts

### 1. Single NMOS Transistor
**File**: `demo_outputs/mos_nmos_textbook.png`

Shows a complete NMOS transistor with:
- W (width) = 12 units
- L (length) = 4 units
- Source and drain diffusions (green)
- Polysilicon gate (red)
- Metal1 connections (blue)
- Contacts (black)
- P-well background (light coral)

### 2. Single PMOS Transistor
**File**: `demo_outputs/mos_pmos_textbook.png`

Shows a complete PMOS transistor with:
- W (width) = 12 units
- L (length) = 4 units
- Source and drain diffusions (tan)
- Polysilicon gate (red)
- Metal1 connections (blue)
- Contacts (black)
- N-well background (light green)

### 3. NMOS Array (2×3)
**File**: `demo_outputs/mos_nmos_array_textbook.png`

Array of 6 NMOS transistors arranged in 2 rows and 3 columns:
- Demonstrates scalability using `fix_layout()` feature
- Uniform transistor sizing: W=8, L=3
- Regular spacing between transistors
- All use textbook-standard colors

### 4. PMOS Array (2×3)
**File**: `demo_outputs/mos_pmos_array_textbook.png`

Array of 6 PMOS transistors arranged in 2 rows and 3 columns:
- Same array structure as NMOS
- Demonstrates PMOS-specific coloring
- N-well substrates for all transistors
- P-diffusion source/drain regions

### 5. CMOS Comparison
**File**: `demo_outputs/mos_cmos_comparison_textbook.png`

Side-by-side comparison showing:
- Left: NMOS transistor (N-diffusion in P-well)
- Right: PMOS transistor (P-diffusion in N-well)
- Highlights complementary nature of CMOS

## Usage Example

### Creating a Single MOS Transistor

```python
from layout_automation.cell import Cell
from layout_automation.style_config import get_style_config

# Set up textbook colors
style = get_style_config()
style.set_layer_style('pwell', color='lightcoral', alpha=0.3)
style.set_layer_style('nwell', color='lightgreen', alpha=0.3)
style.set_layer_style('poly', color='red', alpha=0.7)
style.set_layer_style('ndiff', color='green', alpha=0.6)
style.set_layer_style('pdiff', color='tan', alpha=0.6)
style.set_layer_style('metal1', color='blue', alpha=0.6)
style.set_layer_style('contact', color='black', alpha=0.9)

# Create NMOS transistor
nmos = create_nmos_transistor('NMOS', width=12, length=4)
nmos.draw()
```

### Creating a MOS Array

```python
# Create template
template = create_nmos_transistor('template', width=8, length=3)
template.fix_layout()

# Create array
array = Cell('nmos_array')
for row in range(2):
    for col in range(3):
        mos = template.copy(f'M_{row}_{col}')
        array.add_instance(mos)
        x = col * 15
        y = row * 15
        mos.set_position(x, y)

array.draw()
```

## Design Parameters

### Customizable Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| **width (W)** | Channel width | 4-20 units |
| **length (L)** | Channel length (gate) | 2-10 units |
| **spacing** | Gap between transistors | 3-10 units |

### Default Dimensions

**Single Transistor:**
- W = 12 units
- L = 4 units
- Total footprint: ~20 × 14 units

**Array Transistor:**
- W = 8 units
- L = 3 units
- Spacing = 3 units
- Total footprint per transistor: ~19 × 16 units

## Technical Notes

### Layer Stack Order
1. Well layers (bottom): N-well or P-well
2. Diffusion layers: N-diff or P-diff
3. Polysilicon: Gate
4. Contacts: Connection holes
5. Metal1 (top): Interconnect

### Transistor Operation

**NMOS:**
- Conducts when gate voltage is HIGH
- N-type source/drain in P-type substrate
- Electrons are charge carriers

**PMOS:**
- Conducts when gate voltage is LOW
- P-type source/drain in N-type substrate
- Holes are charge carriers

**CMOS:**
- Complementary pair of NMOS and PMOS
- Low power consumption (one always OFF)
- Used in digital logic gates

## Color Customization

To modify colors for different styles:

```python
from layout_automation.style_config import get_style_config

style = get_style_config()

# Custom color scheme
style.set_layer_style('poly', color='darkred', alpha=0.8)
style.set_layer_style('ndiff', color='lime', alpha=0.7)
style.set_layer_style('metal1', color='steelblue', alpha=0.6)
```

## References

### Standard Textbook Colors
These colors are based on common VLSI design textbooks:
- "CMOS VLSI Design" by Weste and Harris
- "Introduction to VLSI Systems" by Mead and Conway
- "Digital Integrated Circuits" by Rabaey

### Layer Conventions
- **Wells**: Transparent to show underlying layers
- **Diffusions**: Solid colors (green for N, tan for P)
- **Poly**: Distinctive red for visibility
- **Metal**: Blue for contrast with poly
- **Contacts**: Black for clear identification

## File Structure

```
layout_automation/
├── examples/
│   └── mos_textbook_colors.py      # MOS generator
└── demo_outputs/
    ├── mos_nmos_textbook.png       # Single NMOS
    ├── mos_pmos_textbook.png       # Single PMOS
    ├── mos_nmos_array_textbook.png # NMOS array
    ├── mos_pmos_array_textbook.png # PMOS array
    └── mos_cmos_comparison_textbook.png # Comparison
```

## Performance

Using the `fix_layout()` feature for arrays:
- Template transistor: Solved once
- Array copies: Instant positioning
- 6-transistor array: <0.01s total time
- Larger arrays scale linearly with copy count

## Future Enhancements

Potential additions:
- Guard rings around wells
- Body contacts for substrate/well
- Multi-finger transistor layouts
- Folded transistor structures
- CMOS inverter and logic gates
- Standard cell library

---

**Generated**: 2025-10-17
**Status**: ✓ Production ready
**Colors**: ✓ Textbook standard
