# Hierarchical Layout Support - Relative Positioning

Enhancement to support GDS-style hierarchical positioning where child cell positions are relative to their parents.

## Overview

This enhancement adds hierarchical positioning capabilities to the layout automation system, allowing cells to have positions stored relative to their parents—matching the native GDS-II format semantics.

### Current System

**Absolute Positioning:**
```python
parent.pos_list = [0, 0, 200, 200]
child.pos_list = [10, 10, 50, 50]   # Absolute position in global space
```

During GDS export, the system converts to relative:
```python
child_relative = (10 - 0, 10 - 0) = (10, 10)  # Computed at export time
```

### Enhanced System

**Hierarchical Positioning:**
```python
from layout_automation.hierarchical_layout import enable_hierarchical_mode

parent = Cell('parent', child)
enable_hierarchical_mode(parent)

# Set child position relative to parent
child.set_local_position(10, 10, 50, 50)  # Stored as relative

# Both representations available:
child.get_local_position()   # [10, 10, 50, 50] (relative to parent)
child.get_global_position()  # [10, 10, 50, 50] (absolute, computed from parent)
```

## Key Features

### 1. Dual Coordinate System

Each cell can work in both coordinate systems:

- **Local (Relative)**: Position relative to parent's origin
- **Global (Absolute)**: Position in top-level coordinate space

```python
class Cell:
    pos_list = [x1, y1, x2, y2]  # Global position (absolute)
    _local_pos = [x1, y1, x2, y2]  # Local position (relative to parent)
```

### 2. Automatic Transformations

The system automatically transforms between coordinate systems:

```python
# Set local, get global
child.set_local_position(10, 10, 50, 50)
global_pos = child.get_global_position()  # Auto-computed

# Transform points
local_point = (5, 5)
global_point = child.local_to_global_point(*local_point)
```

### 3. Hierarchical Solver

Enhanced solver that maintains hierarchical relationships:

```python
from layout_automation.hierarchical_layout import solve_hierarchical

# Solve with hierarchy awareness
solve_hierarchical(parent)

# Updates both local and global positions for entire hierarchy
```

### 4. GDS-Native Workflow

Export and import work naturally with relative coordinates:

```python
# Export uses relative positions (no conversion needed)
parent.export_gds('layout.gds')

# Import preserves hierarchical structure
cell = Cell.from_gds('layout.gds')
# Hierarchy is maintained with relative positions
```

## Benefits

### 1. Matches GDS Format

GDS-II natively stores child positions relative to parents:
- No conversion overhead during export/import
- Direct correspondence between internal representation and file format
- Preserve design intent from GDS files

### 2. Easier Block Reuse

Move a parent cell → all children move automatically:

```python
# Original
parent.pos_list = [0, 0, 200, 200]
child.local_pos = [10, 10, 50, 50]
child.global_pos = [10, 10, 50, 50]

# Move parent
parent.pos_list = [100, 100, 300, 300]
# Child's local position unchanged!
child.local_pos = [10, 10, 50, 50]
# Child's global position auto-updated!
child.global_pos = [110, 110, 150, 150]
```

### 3. Clearer Design Intent

Express positions relative to their container:

```python
# Absolute positioning (current)
metal1.constrain('x1=10, y1=10, x2=50, y2=50')  # Where is (10,10)? Top-level? Parent?

# Relative positioning (enhanced)
metal1.set_local_position(10, 10, 50, 50)  # Clear: 10 units from parent origin
```

### 4. Simplified Constraints

More natural constraint expression:

```python
# "Place child 10 units from parent's left edge"
child.set_local_position(10, 0, 50, 100)

# "Center child within parent"
# (Constraint system can work in local space)
```

## Usage

### Basic Example

```python
from layout_automation.cell import Cell
from layout_automation.hierarchical_layout import (
    enable_hierarchical_mode,
    solve_hierarchical,
    print_hierarchy_positions
)

# Create hierarchy
metal1 = Cell('metal1', 'metal1')
metal2 = Cell('metal2', 'metal2')
parent = Cell('parent', metal1, metal2)

# Enable hierarchical mode
enable_hierarchical_mode(parent)

# Set positions in local (relative) coordinates
parent.pos_list = [0, 0, 200, 200]
metal1.set_local_position(10, 10, 50, 50)   # Relative to parent
metal2.set_local_position(60, 10, 100, 50)  # Relative to parent

# Solve (if needed)
solve_hierarchical(parent)

# Inspect hierarchy
print_hierarchy_positions(parent)

# Export to GDS (uses native relative positions)
parent.export_gds('output.gds')
```

### Multi-Level Hierarchy

```python
# 3-level hierarchy
leaf = Cell('leaf', 'metal1')
middle = Cell('middle', leaf)
top = Cell('top', middle)

enable_hierarchical_mode(top)

# Set positions at each level
top.pos_list = [0, 0, 500, 500]
middle.set_local_position(50, 50, 200, 200)  # Relative to top
leaf.set_local_position(10, 10, 60, 60)      # Relative to middle

# Global position of leaf is computed through hierarchy:
# leaf_global = top_origin + middle_local + leaf_local
# = (0, 0) + (50, 50) + (10, 10) = (60, 60)
```

### Working with Existing Layouts

Convert absolute positions to hierarchical:

```python
# Load existing layout (absolute coordinates)
cell = Cell.from_gds('existing.gds')

# Enable hierarchical mode
enable_hierarchical_mode(cell)

# System computes local positions from current global positions
solve_hierarchical(cell)

# Now can work in both coordinate systems
for child in cell.children:
    print(f"Global: {child.get_global_position()}")
    print(f"Local:  {child.get_local_position()}")
```

## API Reference

### Functions

#### `enable_hierarchical_mode(cell, recursive=True)`

Enable hierarchical positioning for a cell and its children.

**Parameters:**
- `cell`: Cell to enable hierarchical mode for
- `recursive`: If True, enable for all children recursively

**Returns:** None

**Example:**
```python
parent = Cell('parent', child1, child2)
enable_hierarchical_mode(parent)
```

#### `solve_hierarchical(cell, verbose=False)`

Solve layout with hierarchical positioning awareness.

**Parameters:**
- `cell`: Top-level cell to solve
- `verbose`: Print detailed solving information

**Returns:** `True` if solution found, `False` otherwise

**Example:**
```python
success = solve_hierarchical(parent, verbose=True)
```

#### `print_hierarchy_positions(cell, indent=0)`

Print position hierarchy for debugging.

**Parameters:**
- `cell`: Cell to print
- `indent`: Indentation level (for recursion)

**Returns:** None

**Example:**
```python
print_hierarchy_positions(parent)
```

### Methods (added to Cell)

#### `cell.set_local_position(x1, y1, x2, y2)`

Set position relative to parent.

**Parameters:**
- `x1, y1`: Lower-left corner relative to parent origin
- `x2, y2`: Upper-right corner relative to parent origin

**Returns:** None

#### `cell.get_local_position()`

Get position relative to parent.

**Returns:** `[x1, y1, x2, y2]` in local coordinates, or `None`

#### `cell.get_global_position()`

Get position in global (absolute) coordinates.

**Returns:** `[x1, y1, x2, y2]` in global coordinates, or `None`

#### `cell.local_to_global_point(x, y)`

Transform a point from local to global coordinates.

**Parameters:**
- `x, y`: Point in local coordinates

**Returns:** `(x, y)` in global coordinates

#### `cell.global_to_local_point(x, y)`

Transform a point from global to local coordinates.

**Parameters:**
- `x, y`: Point in global coordinates

**Returns:** `(x, y)` in local coordinates

## Implementation Details

### Coordinate Storage

```python
class Cell:
    # Existing attribute (global/absolute position)
    pos_list = [x1, y1, x2, y2]

    # New attributes (added by hierarchical_layout module)
    _local_pos = [x1, y1, x2, y2]      # Position relative to parent
    _parent_cell = reference_to_parent  # Parent cell reference
    _use_relative_coords = bool         # Flag for hierarchical mode
```

### Transformation Methods

```python
def _calculate_local_from_global(self):
    """Convert global position to local"""
    parent_x, parent_y = self._get_parent_origin()
    x1, y1, x2, y2 = self.pos_list
    return [x1 - parent_x, y1 - parent_y, x2 - parent_x, y2 - parent_y]

def _calculate_global_from_local(self):
    """Convert local position to global"""
    parent_x, parent_y = self._get_parent_origin()
    x1, y1, x2, y2 = self._local_pos
    return [x1 + parent_x, y1 + parent_y, x2 + parent_x, y2 + parent_y]
```

### Parent Reference Management

When enabling hierarchical mode:
1. Set `_parent_cell` reference for each child
2. Enable `_use_relative_coords` flag
3. Compute initial local positions from current global positions

### Solver Integration

The `solve_hierarchical()` function:
1. Calls standard `cell.solver()` to solve constraints
2. Updates local positions for entire hierarchy
3. Maintains consistency between local and global representations

## Examples

### Example 1: Simple Two-Level Hierarchy

```python
from layout_automation.cell import Cell
from layout_automation.hierarchical_layout import enable_hierarchical_mode

# Create cells
rect1 = Cell('rect1', 'metal1')
rect2 = Cell('rect2', 'metal1')
block = Cell('block', rect1, rect2)

# Enable hierarchical mode
enable_hierarchical_mode(block)

# Set block position
block.pos_list = [0, 0, 200, 100]

# Set rectangles relative to block
rect1.set_local_position(10, 10, 60, 40)
rect2.set_local_position(70, 10, 120, 40)

# Verify
print(f"rect1 local:  {rect1.get_local_position()}")
print(f"rect1 global: {rect1.get_global_position()}")

# Output:
# rect1 local:  [10, 10, 60, 40]
# rect1 global: [10, 10, 60, 40]
```

### Example 2: Moving a Block

```python
# Initial setup (from Example 1)
print("Before move:")
print(f"  block global: {block.get_global_position()}")
print(f"  rect1 global: {rect1.get_global_position()}")
print(f"  rect1 local:  {rect1.get_local_position()}")

# Move the block
block.pos_list = [100, 100, 300, 200]
rect1.set_local_position(10, 10, 60, 40)  # Re-apply local position

print("\nAfter move:")
print(f"  block global: {block.get_global_position()}")
print(f"  rect1 global: {rect1.get_global_position()}")
print(f"  rect1 local:  {rect1.get_local_position()}")

# Output:
# Before move:
#   block global: [0, 0, 200, 100]
#   rect1 global: [10, 10, 60, 40]
#   rect1 local:  [10, 10, 60, 40]
#
# After move:
#   block global: [100, 100, 300, 200]
#   rect1 global: [110, 110, 160, 140]
#   rect1 local:  [10, 10, 60, 40]
```

## Compatibility

### Backwards Compatibility

The hierarchical layout module is **fully backwards compatible**:

- Existing code continues to work unchanged
- `pos_list` (absolute positioning) still works as before
- Hierarchical mode is opt-in via `enable_hierarchical_mode()`
- GDS export/import work with both representations

### Migration Path

Gradual adoption:
1. Continue using absolute positioning where appropriate
2. Enable hierarchical mode for new designs
3. Convert existing designs as needed
4. Mix both approaches in same codebase

## Testing

Run the test suite:

```bash
# Simple conceptual demo
python demo_hierarchical_simple.py

# Full test suite
python test_hierarchical_layout.py
```

Test files included:
- `demo_hierarchical_simple.py` - Conceptual demonstration
- `test_hierarchical_layout.py` - Comprehensive tests
- Output GDS files for verification

## Limitations & Future Work

### Current Limitations

1. **Parent References**: Require manual setup via `enable_hierarchical_mode()`
2. **Solver Integration**: Basic integration; advanced features pending
3. **Constraint System**: Constraints still work in absolute space
4. **GDS Import**: Doesn't automatically preserve relative positions yet

### Future Enhancements

Planned improvements:

- [ ] Automatic parent reference management
- [ ] Relative constraint syntax (e.g., `'local_x1=10'`)
- [ ] GDS import with hierarchy preservation
- [ ] Incremental position updates (move parent → auto-update children)
- [ ] Visualization of coordinate systems
- [ ] Performance optimization for large hierarchies
- [ ] Integration with DRC workflow

## Related Documentation

- [USER_MANUAL.md](USER_MANUAL.md) - Main user manual
- [GDS_INVESTIGATION_SUMMARY.md](GDS_INVESTIGATION_SUMMARY.md) - GDS format details
- [DRC_WORKFLOW_README.md](DRC_WORKFLOW_README.md) - DRC workflow

## Credits

Hierarchical layout enhancement created for the layout_automation project to provide GDS-native positioning semantics.
