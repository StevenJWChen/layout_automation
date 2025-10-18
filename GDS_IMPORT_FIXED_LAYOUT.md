# GDS Import with Fixed Layout Feature

## Overview

When importing GDS files, the imported cells are now automatically set as **fixed layouts**. This means:

1. **Imported cells have their bounding box set** to match the GDS boundary
2. **Cells are automatically fixed** using `fix_layout()`
3. **Internal structure is preserved** and cannot be resized
4. **Cells can be repositioned** to any location using constraints
5. **All internal elements move together** when the cell is repositioned

## Key Features

### 1. Bounding Box from GDS
The imported cell's `pos_list` is set to the exact bounding box of all shapes in the GDS file:

```python
imported = Cell.from_gds('design.gds', use_tech_file=True)
bounds = imported.get_bounds()  # Returns actual GDS boundary
# Example: (10, 20, 50, 45)
```

### 2. Fixed Layout Behavior
The imported cell is automatically fixed, meaning:
- Internal structure is locked
- Children positions are stored as relative offsets
- Cell can only be translated (repositioned)
- Cannot be resized or have internal elements modified

```python
imported._fixed  # True
imported.children  # All children have positions set
```

### 3. Repositioning Capability
You can reposition the imported cell anywhere using constraints:

```python
top = Cell('top_level')
imported_copy = imported.copy('my_block')
top.add_instance([imported_copy])

# Reposition to (100, 200)
top.constrain(imported_copy, 'x1=100, y1=200')
top.solver()

# All internal shapes move together
new_bounds = imported_copy.get_bounds()  # (100, 200, 140, 225)
```

## Implementation Details

### GDS Import Process

When `Cell.from_gds()` is called:

1. **Read GDS file** using gdstk
2. **For each polygon:**
   - Extract bounding box from polygon
   - Convert coordinates to integers (for solver compatibility)
   - Create leaf cell with position set
3. **Calculate cell bounding box:**
   - Find min/max of all child positions
   - Set cell's `pos_list` to bounding box
4. **Fix the layout:**
   - Call `fix_layout()` on the cell
   - Store relative offsets for all children
   - Mark cell as fixed

### Code Example

```python
@classmethod
def _from_gds_cell(cls, gds_cell, layer_map: Dict) -> 'Cell':
    """Convert GDS cell to Cell object with fixed layout"""
    cell = cls(gds_cell.name)

    # Process polygons
    for polygon in gds_cell.polygons:
        # ... extract layer and bbox ...
        leaf = cls(f'{name}_{layer}_{i}', layer_name)
        # Convert to int for solver
        leaf.pos_list = [int(round(x1)), int(round(y1)),
                        int(round(x2)), int(round(y2))]
        cell.children.append(leaf)

    # Calculate bounding box
    if cell.children:
        x1_vals, y1_vals, x2_vals, y2_vals = [], [], [], []
        for child in cell.children:
            x1_vals.append(child.pos_list[0])
            # ... collect all coordinates ...

        cell.pos_list = [
            int(round(min(x1_vals))),
            int(round(min(y1_vals))),
            int(round(max(x2_vals))),
            int(round(max(y2_vals)))
        ]

    # Fix the layout
    cell.fix_layout()

    return cell
```

## Usage Examples

### Example 1: Basic Import and Repositioning

```python
from layout_automation.cell import Cell

# Import GDS (automatically fixed)
block = Cell.from_gds('block.gds', use_tech_file=True)
print(f"Imported bounds: {block.get_bounds()}")
print(f"Is fixed: {block._fixed}")  # True

# Use in new layout
chip = Cell('chip')
b1 = block.copy('block_1')
b2 = block.copy('block_2')

chip.add_instance([b1, b2])

# Position blocks
chip.constrain(b1, 'x1=0, y1=0')
chip.constrain(b2, 'sx1=ox2+10, y1=0', b1)

chip.solver()

# Blocks positioned correctly with all internals intact
print(f"Block 1: {b1.get_bounds()}")
print(f"Block 2: {b2.get_bounds()}")
```

### Example 2: Array of Imported Blocks

```python
# Import standard cell
stdcell = Cell.from_gds('inv.gds', use_tech_file=True)

# Create array
array = Cell('cell_array')

for row in range(3):
    for col in range(5):
        cell = stdcell.copy(f'inv_{row}_{col}')
        array.add_instance([cell])

        x = col * 100
        y = row * 50
        array.constrain(cell, f'x1={x}, y1={y}')

array.solver()
# 15 cells positioned in a 3x5 grid
```

### Example 3: Hierarchical Layout with Imported Blocks

```python
# Import multiple GDS files
nand = Cell.from_gds('nand.gds', use_tech_file=True)
nor = Cell.from_gds('nor.gds', use_tech_file=True)
inv = Cell.from_gds('inv.gds', use_tech_file=True)

# Build logic circuit
circuit = Cell('logic_circuit')

n1 = nand.copy('nand1')
n2 = nor.copy('nor1')
i1 = inv.copy('inv1')

circuit.add_instance([n1, n2, i1])

# Position with constraints
circuit.constrain(n1, 'x1=0, y1=0')
circuit.constrain(n2, 'sx1=ox2+20, y1=0', n1)
circuit.constrain(i1, 'sx1=ox2+20, sy1=oy1', n2)

circuit.solver()

# Export complete circuit
circuit.export_gds('circuit.gds', use_tech_file=True)
```

## Benefits

### 1. Correct Bounding Box
The imported cell has the exact bounding box from the GDS file, making it easy to:
- Calculate spacing between blocks
- Align blocks precisely
- Determine chip dimensions

### 2. Reusable Blocks
Fixed imported cells can be copied and repositioned multiple times:
- Efficient for standard cell libraries
- Perfect for block-based design
- Supports hierarchical composition

### 3. Preserved Fidelity
Internal structure is locked, ensuring:
- No accidental modification of imported designs
- Exact shapes are preserved from GDS
- Relative positions maintained

### 4. Constraint-Based Placement
Use full power of constraint solver:
- Relative positioning
- Alignment constraints
- Spacing rules
- Hierarchical constraints

## Verification

### Test Case: Round-Trip with Repositioning

```python
# Create original layout
orig = Cell('original')
r1 = Cell('r1', 'metal1')
orig.add_instance([r1])
orig.constrain(r1, 'x1=10, y1=20, x2=30, y2=40')
orig.solver()

orig_bounds = orig.get_bounds()  # (10, 20, 30, 40)

# Export to GDS
orig.export_gds('test.gds', use_tech_file=True)

# Import back
imported = Cell.from_gds('test.gds', use_tech_file=True)

# Verify bounds match
assert imported.get_bounds() == orig_bounds  # ✓

# Verify it's fixed
assert imported._fixed == True  # ✓

# Reposition
top = Cell('top')
imp_copy = imported.copy('copy1')
top.add_instance([imp_copy])
top.constrain(imp_copy, 'x1=100, y1=200')
top.solver()

# Verify repositioning
new_bounds = imp_copy.get_bounds()  # (100, 200, 120, 220)
offset_x = new_bounds[0] - orig_bounds[0]  # 90
offset_y = new_bounds[1] - orig_bounds[1]  # 180

assert offset_x == 90  # ✓
assert offset_y == 180  # ✓
```

## Comparison: Before vs After

### Before (Old Behavior)
```python
imported = Cell.from_gds('block.gds')
imported._fixed  # False
imported.get_bounds()  # None or inconsistent

# Repositioning would require manual offset calculation
# Internal structure could be accidentally modified
```

### After (New Behavior)
```python
imported = Cell.from_gds('block.gds', use_tech_file=True)
imported._fixed  # True
imported.get_bounds()  # Exact GDS boundary: (x1, y1, x2, y2)

# Repositioning is automatic via constraints
top.constrain(imported_copy, 'x1=100, y1=200')
top.solver()  # All internals update automatically
```

## Technical Notes

### Coordinate Conversion
GDS coordinates are converted to integers to ensure solver compatibility:
- `gdstk` returns floating point coordinates
- Solver requires integer values for constraints
- Values are rounded to nearest integer

### Memory Efficiency
Fixed layouts store offsets once, not full position data:
- Original: N cells × 4 coordinates = 4N values
- Fixed: 1 bounding box + N offsets = (4 + 4N) values
- Minimal overhead for repositioning capability

### Performance
Repositioning is O(1) operation:
- Solver only updates parent position
- Children update via stored offsets
- No constraint re-solving needed for internals

## Future Enhancements

Potential improvements:
- Option to import without fixing (for editing)
- Selective fixing (only certain cells)
- Preservation of cell references in GDS hierarchy
- Support for GDS transformations (rotation, mirroring)

---

**Date:** 2025-10-18
**Status:** ✓ Implemented and Tested
**Demo:** `examples/demo_virtuoso_minimal.py`
