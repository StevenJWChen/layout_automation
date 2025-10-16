# Layout Automation - Cell.py Module

A constraint-based IC layout automation toolkit focused on hierarchical cell-based design.

## Core Components

### layout_automation/
- **cell.py** - Main Cell class with constraint-based positioning and sizing
- **constraint_keywords.py** - Constraint keyword expansion utilities
- **__init__.py** - Module initialization

## Structure

```
layout_automation/
├── layout_automation/
│   ├── __init__.py
│   ├── cell.py
│   └── constraint_keywords.py
├── tests/                    # 21 test files
└── examples/                 # 43 example files
```

## Installation

```bash
# Add to Python path
export PYTHONPATH=/path/to/layout_automation:$PYTHONPATH

# Or install in development mode
pip install -e .
```

## Known Issues

### OR-Tools Segfault on Python 3.13

The `cell.py` module imports OR-Tools for constraint solving, which is known to have compatibility issues with Python 3.13:

**Problem**: OR-Tools causes a segmentation fault when imported on Python 3.13.5

**Symptoms**:
- Python crashes/hangs when importing layout_automation.cell
- Tests fail to run

**Workarounds**:
1. **Use Python 3.11 or 3.12** (recommended)
   ```bash
   # Install pyenv if needed
   brew install pyenv

   # Install Python 3.12
   pyenv install 3.12.0
   pyenv local 3.12.0
   ```

2. **Disable OR-Tools** (limited functionality)
   - Cell creation and hierarchy will work
   - Constraint solving (.solver() method) will not work

## Usage

### Basic Example

```python
from layout_automation.cell import Cell

# Create leaf cells (rectangles)
metal1 = Cell('metal1_rect', 'metal1')
metal2 = Cell('metal2_rect', 'metal2')

# Create hierarchical cell
parent = Cell('parent', metal1, metal2)

# Add constraints
parent.constrain(metal1, 'sx2+10<ox1', metal2)  # metal1 left of metal2

# Solve constraints (requires working OR-Tools)
if parent.solver():
    print(f"metal1 position: {metal1.pos_list}")
    print(f"metal2 position: {metal2.pos_list}")

    # Visualize
    parent.draw()
```

### Constraint Keywords

```python
from layout_automation.constraint_keywords import expand_constraint_keywords

# Use readable constraint helpers
parent.constrain(metal1, 'right_of', metal2, spacing=10)
parent.constrain(metal1, 'above', metal2, spacing=5)
parent.constrain(metal1, 'align_left', metal2)
```

## Features

- Hierarchical cell-based design
- Constraint-based positioning and sizing
- Copy and instance cells
- Freeze layouts to fix positions
- GDS import/export (requires additional modules)
- Constraint keyword expansion for readable code

## Testing

```bash
# Run a specific test (with Python 3.12 or earlier)
python3 tests/test_cell.py

# Run all tests
python3 -m pytest tests/
```

## Examples

See the `examples/` directory for 43 working examples including:
- `inverter_demo.py` - CMOS inverter layout
- `and2_gate_demo.py` - AND gate layout
- `frozen_layout_demo.py` - Frozen layout features
- `gds_import_export_demo.py` - GDS workflows
- `test_cell_features.py` - Cell feature demonstrations

## Documentation

- Cell class supports hierarchical instances
- Constraints use a DSL: `sx2+10<ox1` means "self.x2 + 10 < other.x1"
- Position list format: `[x1, y1, x2, y2]`
- Leaf cells have a layer name (e.g., 'metal1')
- Non-leaf cells contain child Cell instances

## License

See LICENSE file for details.
