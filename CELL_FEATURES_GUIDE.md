# Cell Class Features Guide

## Overview

The `Cell` class in `layout_automation/cell.py` provides constraint-based layout automation with the following key features:

1. **Frozen Layout** - Lock cell structure while allowing positioning
2. **Minimum Size Constraint** - All cells are at least 1×1 unit
3. **GDS Import/Export** - Read/write GDS-II format
4. **Relative Position Constraints** - Position sub-cells relative to each other or parent

---

## 1. Frozen Layout Feature

### What is Freezing?

Freezing a cell locks its internal structure (size and child positions) while still allowing the cell itself to be positioned by a parent cell.

### Why Use Frozen Layouts?

- **Reusability**: Create a block once, reuse many times
- **Performance**: Frozen blocks don't need re-solving
- **IP Protection**: Internal structure is locked
- **Modularity**: Build complex designs from frozen building blocks

### API

```python
# Freeze a cell
cell.freeze_layout()  # Returns self for chaining

# Check if frozen
if cell.is_frozen():
    print("Cell is frozen")

# Unfreeze if needed
cell.unfreeze_layout()

# Get bounding box (cached for frozen cells)
bbox = cell.get_bbox()  # Returns (x1, y1, x2, y2) or None
```

### Example: Frozen Cell Can Be Constrained by Parent

```python
from layout_automation.cell import Cell

# Step 1: Create a reusable block
block = Cell('reusable_block')
metal = Cell('metal', 'metal1')
poly = Cell('poly', 'poly')

block.add_instance([metal, poly])
block.constrain(metal, 'x1=0, y1=0, x2=20, y2=20')
block.constrain(poly, 'x1=5, y1=5, x2=15, y2=15')

# Step 2: Solve and freeze
block.solver()
block.freeze_layout()  # Internal structure is now locked
# Block bbox: (0, 0, 20, 20) with 20×20 size

# Step 3: Use frozen block in top cell
top = Cell('top_cell')

# Create multiple instances
block1 = block.copy()
block2 = block.copy()

top.add_instance([block1, block2])

# Step 4: Constrain frozen blocks' positions
# The SIZE is frozen (20×20) but POSITION can be constrained
top.constrain(block1, 'x1=10, y1=10, x2=30, y2=30')  # Must maintain 20×20 size
top.constrain(block2, 'sx1=ox2+50, sy1=oy1, sx2-sx1=20, sy2-sy1=20', block1)

# Step 5: Solve top cell
top.solver()
# block1 will be at (10, 10, 30, 30) - size preserved!
# block2 will be 50 units to the right
```

### Important Notes

- Frozen cells maintain their **size** (width and height)
- Frozen cells can still be **positioned** by parent constraints
- The solver adds constraint: `x2 - x1 == frozen_width` and `y2 - y1 == frozen_height`
- Internal children of frozen cells are also frozen recursively

---

## 2. Minimum Size Constraint

### What It Does

All cells must be at least **1×1 unit** in size. The solver enforces:
- `x2 >= x1 + 1`
- `y2 >= y1 + 1`

### Why 1 Unit Minimum?

- Prevents degenerate (zero-area) cells
- Ensures all rectangles are visible
- Maintains valid GDS output
- Provides reasonable default for constraint solving

### Example

```python
from layout_automation.cell import Cell

cell = Cell('tiny_cell', 'metal1')

# Try to make a 1×1 cell (minimum size)
cell.constrain('x1=0, y1=0, x2-x1=1, y2-y1=1')

cell.solver()
print(cell.pos_list)  # [0, 0, 1, 1] - exactly 1×1

# Try to make smaller (will fail or be adjusted to minimum)
cell2 = Cell('another_cell', 'poly')
cell2.constrain('x1=0, y1=0, x2=0, y2=0')  # Try 0×0
cell2.solver()
print(cell2.pos_list)  # Will be at least [0, 0, 1, 1]
```

---

## 3. Center Constraint Syntax

### How to Center a Child in Parent

To center a child cell within its parent, use the constraint:

```python
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)
```

### Mathematical Explanation

For X-axis centering:
```
sx1 + sx2 = ox1 + ox2
(child.x1 + child.x2) = (parent.x1 + parent.x2)
2 * child_center_x = 2 * parent_center_x
child_center_x = parent_center_x
```

The same logic applies to Y-axis with `sy1+sy2=oy1+oy2`.

### Example: Center Child in Parent

```python
from layout_automation.cell import Cell

# Create parent with 100×100 size
parent = Cell('parent')
parent.constrain('x1=0, y1=0, x2=100, y2=100')

# Create child with 30×40 size
child = Cell('child', 'metal1')

# Set child size
parent.constrain(child, 'sx2-sx1=30, sy2-sy1=40')

# Center child in parent
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

# Solve
parent.solver()

# Result:
# Parent: (0, 0, 100, 100) - center at (50, 50)
# Child:  (35, 30, 65, 70) - center at (50, 50)
# Child is centered!
```

### Centering Only on One Axis

```python
# Center only horizontally
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1=10', parent)

# Center only vertically
parent.constrain(child, 'sx1=10, sy1+sy2=oy1+oy2', parent)
```

---

## 4. Relative Position Constraints

### Constraint Types

The `constrain()` method supports three modes:

#### Mode 1: Self-Constraint
```python
cell.constrain('x2-x1=100, y2-y1=50')
```

#### Mode 2: Absolute Positioning of Child
```python
parent.constrain(child, 'x1=10, y1=20, x2=50, y2=60')
```

#### Mode 3: Relative Positioning Between Children
```python
parent.constrain(child1, 'sx2+spacing=ox1', child2)
# child1's right edge + spacing = child2's left edge
```

### Prefix System

- **`s` prefix**: Refers to the **first** cell (subject) - e.g., `sx1`, `sy2`
- **`o` prefix**: Refers to the **second** cell (object) - e.g., `ox1`, `oy2`
- **No prefix** or **`x`/`y` prefix**: Refers to the cell itself in self-constraints

### Common Patterns

#### Horizontal Spacing
```python
# Place child2 to the right of child1 with 10-unit gap
parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)
```

#### Vertical Stacking
```python
# Place child2 below child1 with 5-unit gap
parent.constrain(child2, 'sx1=ox1, sy1=oy2+5', child1)
```

#### Alignment
```python
# Align left edges
parent.constrain(child2, 'sx1=ox1', child1)

# Align right edges
parent.constrain(child2, 'sx2=ox2', child1)

# Align centers (X-axis)
parent.constrain(child2, 'sx1+sx2=ox1+ox2', child1)
```

#### Size Matching
```python
# Same width as another cell
parent.constrain(child2, 'sx2-sx1=ox2-ox1', child1)

# Same height
parent.constrain(child2, 'sy2-sy1=oy2-oy1', child1)
```

---

## 5. GDS Import/Export

### Export to GDS

```python
from layout_automation.cell import Cell

cell = Cell('my_layout')
# ... build your layout ...

# Export with default layer mapping
cell.export_gds('output.gds')

# Export with custom layer mapping
custom_layers = {
    'metal1': (10, 0),
    'poly': (20, 0),
    'diff': (30, 0),
}
cell.export_gds('output.gds', layer_map=custom_layers)
```

### Import from GDS

```python
from layout_automation.cell import Cell

# Import top cell automatically
cell = Cell.from_gds('input.gds')

# Import specific cell by name
cell = Cell.from_gds('input.gds', cell_name='INVERTER')

# Import with custom layer mapping
custom_layers = {
    (10, 0): 'metal1',
    (20, 0): 'poly',
    (30, 0): 'diff',
}
cell = Cell.from_gds('input.gds', layer_map=custom_layers)
```

### Default Layer Mappings

**Export** (layer name → GDS layer):
```python
{
    'metal1': (1, 0),
    'metal2': (2, 0),
    'metal3': (3, 0),
    'metal4': (4, 0),
    'poly': (5, 0),
    'diff': (6, 0),
    'pdiff': (7, 0),
    'nwell': (8, 0),
    'contact': (9, 0),
}
```

**Import** (GDS layer → layer name):
```python
{
    (1, 0): 'metal1',
    (2, 0): 'metal2',
    (3, 0): 'metal3',
    (4, 0): 'metal4',
    (5, 0): 'poly',
    (6, 0): 'diff',
    (7, 0): 'pdiff',
    (8, 0): 'nwell',
    (9, 0): 'contact',
}
```

---

## Complete Example: Hierarchical Layout with All Features

```python
from layout_automation.cell import Cell

# Create a reusable contact array
contact_array = Cell('contact_2x2')
for i in range(2):
    for j in range(2):
        contact = Cell(f'c_{i}_{j}', 'contact')
        contact_array.constrain(contact, f'x1={j*4}, y1={i*4}, x2={j*4+2}, y2={i*4+2}')

# Solve and freeze
contact_array.solver()
contact_array.freeze_layout()  # Now it's a frozen 6×6 block

# Create transistor using frozen contacts
transistor = Cell('NMOS')
diff = Cell('diff', 'diff')
poly = Cell('gate', 'poly')

transistor.add_instance([diff, poly])
transistor.constrain(diff, 'x1=0, y1=5, x2=30, y2=25')
transistor.constrain(poly, 'x1=11, y1=0, x2=19, y2=30')

# Add frozen contact arrays (maintain 6×6 size)
src_contacts = contact_array.copy()
drn_contacts = contact_array.copy()

transistor.add_instance([src_contacts, drn_contacts])
# Position contacts at source and drain regions
transistor.constrain(src_contacts, 'x1=2, y1=12, x2=8, y2=18')
transistor.constrain(drn_contacts, 'x1=22, y1=12, x2=28, y2=18')

# Freeze the transistor
transistor.solver()
transistor.freeze_layout()

# Build top-level cell with centered transistor array
top = Cell('TOP')
trans1 = transistor.copy()
trans2 = transistor.copy()

top.add_instance([trans1, trans2])

# Position transistors with spacing
top.constrain(trans1, 'x1=0, y1=0, x2=30, y2=30')  # Fixed size from freeze
top.constrain(trans2, 'sx1=ox2+20, sy1=oy1, sx2-sx1=30, sy2-sy1=30', trans1)

# Solve and export
top.solver()
top.export_gds('hierarchical_layout.gds')

print(f"✓ Layout created with frozen contact arrays and transistors")
print(f"  Contact array: 6×6 (frozen)")
print(f"  Transistor: 30×30 (frozen)")
print(f"  Top cell: contains 2 transistors with 20-unit spacing")
```

---

## Summary

### Question 1: Can frozen cells be constrained by top cell?

**Answer: YES** ✓

Frozen cells maintain their **size** but can be **positioned** by parent constraints. The solver fixes `width = x2 - x1` and `height = y2 - y1` to the frozen values, but allows `x1`, `y1`, `x2`, `y2` to move together.

### Question 2: Does `sx1+sx2=ox1+ox2` center the child?

**Answer: YES** ✓

This constraint means:
- `child.x1 + child.x2 = parent.x1 + parent.x2`
- Which simplifies to: `child_center_x = parent_center_x`
- Combined with `sy1+sy2=oy1+oy2`, the child is centered in both dimensions

---

## See Also

- `examples/verify_freeze_and_center.py` - Verification examples
- `examples/test_cell_features.py` - Comprehensive feature tests
- `layout_automation/gds_cell.py` - Alternative cell implementation
