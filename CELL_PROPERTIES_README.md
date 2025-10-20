# Cell Position Properties

## Overview

The `Cell` class now provides convenient read-only properties for accessing position information, making code more readable and intuitive.

## Available Properties

All properties return `None` if the cell has not been positioned yet (i.e., before `solver()` is called).

### Coordinate Properties

- **`cell.x1`** - Left x-coordinate (bottom-left corner)
- **`cell.y1`** - Bottom y-coordinate (bottom-left corner)
- **`cell.x2`** - Right x-coordinate (top-right corner)
- **`cell.y2`** - Top y-coordinate (top-right corner)

### Dimension Properties

- **`cell.width`** - Width of the cell (x2 - x1)
- **`cell.height`** - Height of the cell (y2 - y1)

### Center Properties

- **`cell.cx`** - Center x-coordinate ((x1 + x2) / 2)
- **`cell.cy`** - Center y-coordinate ((y1 + y2) / 2)

## Usage Examples

### Basic Usage

```python
from layout_automation import Cell

# Create and solve layout
parent = Cell('parent')
box = Cell('box', 'metal1')
parent.constrain(box, 'x1=10, y1=20, x2=60, y2=70')
parent.solver()

# Access properties
print(f"Box position: ({box.x1}, {box.y1}) to ({box.x2}, {box.y2})")
print(f"Box size: {box.width} x {box.height}")
print(f"Box center: ({box.cx}, {box.cy})")
```

Output:
```
Box position: (10, 20) to (60, 70)
Box size: 50 x 50
Box center: (35.0, 45.0)
```

### Before vs After

**OLD WAY** (accessing pos_list directly):
```python
# Less readable
left_edge = box.pos_list[0]
width = box.pos_list[2] - box.pos_list[0]
center_x = (box.pos_list[0] + box.pos_list[2]) / 2
```

**NEW WAY** (using properties):
```python
# More readable and intuitive
left_edge = box.x1
width = box.width
center_x = box.cx
```

### Practical Examples

#### 1. Calculate spacing between cells
```python
spacing = box2.x1 - box1.x2
print(f"Spacing: {spacing} units")
```

#### 2. Check alignment
```python
if box1.y1 == box2.y1:
    print(f"Boxes are bottom-aligned at y={box1.y1}")
```

#### 3. Calculate area
```python
area = box.width * box.height
print(f"Area: {area}")
```

#### 4. Find dimensions
```python
print(f"{cell.name}: {cell.width}x{cell.height} at ({cell.x1}, {cell.y1})")
```

#### 5. Work with centers
```python
# Distance between centers
import math
distance = math.sqrt((box2.cx - box1.cx)**2 + (box2.cy - box1.cy)**2)
```

## Benefits

1. **More Readable**: `cell.width` is clearer than `cell.pos_list[2] - cell.pos_list[0]`
2. **Less Error-Prone**: No need to remember indices or calculate differences
3. **Intuitive**: Properties have self-documenting names
4. **Consistent**: All properties return `None` when not positioned
5. **Pythonic**: Uses standard Python property decorators

## Compatibility

These properties are fully compatible with:
- Regular cells
- Frozen cells (`freeze_layout()`)
- Fixed cells (`fix_layout()`)
- Imported GDS cells
- All existing constraint features

The underlying `pos_list` attribute is still available for direct access when needed.

## Testing

See the following test files for comprehensive examples:
- `test_cell_properties.py` - Comprehensive property tests
- `test_width_height_properties.py` - Basic width/height tests
- `example_cell_properties.py` - Practical usage examples
