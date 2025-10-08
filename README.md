# Layout Automation

A Python library for constraint-based hierarchical layout automation using SciPy optimization. Define spatial relationships between layout elements using simple constraint expressions, and let the solver automatically compute optimal positions.

⚠️ **IMPORTANT**: This tool provides constraint solving and layout automation. Users are responsible for providing correct constraints and validating results for physical/electrical correctness. See [TOOL_VALIDATION.md](TOOL_VALIDATION.md) for details.

## Features

- **Constraint-based positioning**: Define spatial relationships using intuitive constraint expressions
- **Hierarchical cell structure**: Build complex layouts from reusable cell components
- **Two programming models**:
  - `cell.py`: Simplified hierarchical cell model with layer-based leaf cells
  - `gds_cell.py`: GDS-II compliant model with polygons and cell instances
- **Automatic constraint solving**: Uses SciPy optimization (SLSQP method) to satisfy all constraints
- **Visualization**: Built-in matplotlib-based layout visualization
- **GDS export/import**: Full support for GDS-II file format (gds_cell.py only)

## Installation

### Requirements

```bash
pip install scipy numpy matplotlib gdstk
```

### Dependencies

- Python 3.7+
- scipy: Constraint solving via optimization
- numpy: Numerical computations
- matplotlib: Layout visualization
- gdstk: GDS-II file I/O (optional, only for gds_cell.py)

## Quick Start

### Using cell.py (Simple Hierarchical Model)

```python
from cell import Cell

# Create leaf cells (representing layout layers)
inst1 = Cell('inst1', 'metal1')
inst2 = Cell('inst2', 'metal2')
inst3 = Cell('inst3', 'metal3')

# Create container cell with children
cell_inst1 = Cell('cell_inst1', inst1, inst2, inst3)

# Add constraints between cells
# 's' prefix refers to first cell, 'o' prefix refers to second cell
# x1, y1 = lower-left corner; x2, y2 = upper-right corner
cell_inst1.constrain(inst1, 'sx1<ox2+3, sy2+5<oy1', inst2)
cell_inst1.constrain(inst1, 'sx1=ox1-1', inst3)

# Create copies for reuse
t_inst1 = cell_inst1.copy()
t_inst2 = cell_inst1.copy()

# Create top-level cell
tt_inst = Cell('tt_inst', t_inst1, t_inst2)
tt_inst.constrain(t_inst1, 'sx2+5<ox1', t_inst2)

# Solve and visualize
tt_inst.draw()  # Automatically solves constraints and displays layout
```

### Using gds_cell.py (GDS-II Compatible Model)

```python
from gds_cell import Cell, Polygon, CellInstance

# Create a base cell with polygons
base_cell = Cell('base_cell')
poly1 = Polygon('poly1', 'metal1')
poly2 = Polygon('poly2', 'metal2')
base_cell.add_polygon([poly1, poly2])

# Add constraints between polygons
base_cell.constrain(poly1, 'sx2+3<ox1, sy2+5<oy1', poly2)

# Create top-level cell with instances
top_cell = Cell('top_cell')
inst1 = CellInstance('inst1', base_cell)
inst2 = CellInstance('inst2', base_cell)
top_cell.add_instance([inst1, inst2])

# Constrain instances
top_cell.constrain(inst1, 'sx2+5<ox1', inst2)

# Solve and export to GDS
top_cell.draw()
top_cell.export_gds('output.gds')
```

## Constraint Syntax

Constraints define spatial relationships between two objects using simple expressions:

### Syntax Format

```
constrain(obj1, constraint_string, obj2)
```

- `obj1`: First object (referenced as `s` in constraint string)
- `obj2`: Second object (referenced as `o` in constraint string)
- `constraint_string`: One or more constraints separated by commas

### Variable Names

- `sx1, sy1, sx2, sy2`: Coordinates of first object (s = self)
- `ox1, oy1, ox2, oy2`: Coordinates of second object (o = other)
- `x1, y1`: Lower-left corner
- `x2, y2`: Upper-right corner

### Operators

- `<`: Less than
- `>`: Greater than
- `<=`: Less than or equal
- `>=`: Greater than or equal
- `=`: Equal

### Examples

```python
# inst1 must be left of inst2 with 3 unit spacing
cell.constrain(inst1, 'sx2+3<ox1', inst2)

# inst1 and inst2 aligned vertically
cell.constrain(inst1, 'sy1=oy1', inst2)

# inst1 must be 5 units below inst2
cell.constrain(inst1, 'sy2+5<oy1', inst2)

# Multiple constraints
cell.constrain(inst1, 'sx2<ox1, sy1=oy1, sx2-sx1=20', inst2)
```

## API Reference

### Cell Class (cell.py)

#### Constructor

```python
Cell(name: str, *args)
```

- `name`: Cell instance name
- `*args`: Variable arguments - can be:
  - Other Cell instances (children)
  - A string (layer name, makes this a leaf cell)
  - Lists of Cell instances

#### Methods

- **`add_instance(instances)`**: Add child cell instance(s)
- **`constrain(cell1, constraint_str, cell2)`**: Add spatial constraint
- **`solver(fix_leaf_positions=True)`**: Solve constraints, returns bool
- **`draw(solve_first=True, ax=None, show=True)`**: Visualize layout
- **`copy()`**: Create deep copy with fresh constraint variables

#### Attributes

- **`pos_list`**: `[x1, y1, x2, y2]` - Position after solving
- **`children`**: List of child Cell instances
- **`is_leaf`**: Boolean, True if this is a layer cell
- **`layer_name`**: Layer name string (for leaf cells)

### Cell Class (gds_cell.py)

#### Constructor

```python
Cell(name: str)
```

#### Methods

- **`add_polygon(polygon)`**: Add Polygon or list of Polygons
- **`add_instance(instance)`**: Add CellInstance or list of CellInstances
- **`constrain(obj1, constraint_str, obj2)`**: Add spatial constraint
- **`solver(fix_polygon_size=True)`**: Solve constraints, returns bool
- **`draw(solve_first=True, ax=None, show=True)`**: Visualize layout
- **`export_gds(filename, unit=1e-6, precision=1e-9)`**: Export to GDS file
- **`import_gds(filename, top_cell_name=None)`**: Import from GDS file

### Polygon Class

```python
Polygon(name: str, layer: str)
```

- **`pos_list`**: `[x1, y1, x2, y2]` - Position after solving

### CellInstance Class

```python
CellInstance(name: str, cell: Cell)
```

- **`cell`**: Reference to master cell
- **`pos_list`**: `[x1, y1, x2, y2]` - Instance position after solving

## How It Works

### Constraint Solving with SciPy

The library uses SciPy's Sequential Least Squares Programming (SLSQP) optimizer to solve the constraint system:

1. **Variable Setup**: Each cell/polygon/instance gets 4 variables: `x1, y1, x2, y2`
2. **Constraint Translation**: User constraints are parsed into linear inequality/equality constraints
3. **Automatic Constraints**: System adds geometric constraints (`x2 > x1`, `y2 > y1`, parent bounds, etc.)
4. **Optimization**: Minimizes total area while satisfying all constraints
5. **Solution Extraction**: Extracts solved positions from optimization result

### Constraint Types

- **User constraints**: Defined via `constrain()` method
- **Geometric constraints**: Ensure valid rectangles (`x2 > x1`, `y2 > y1`)
- **Size constraints**: Minimum sizes for leaf cells/polygons
- **Hierarchical constraints**: Parents must encompass children

## Examples

### Example 1: Simple Metal Stack

```python
from cell import Cell

# Create metal layers
m1 = Cell('m1', 'metal1')
m2 = Cell('m2', 'metal2')
m3 = Cell('m3', 'metal3')

# Stack them vertically
stack = Cell('stack', m1, m2, m3)
stack.constrain(m1, 'sx2<ox1+5', m2)  # m1 left of m2
stack.constrain(m2, 'sx2<ox1+5', m3)  # m2 left of m3
stack.constrain(m1, 'sy1=oy1, sy2=oy2', m2)  # Same height
stack.constrain(m2, 'sy1=oy1, sy2=oy2', m3)  # Same height

stack.draw()
```

### Example 2: Reusable Cell Pattern

```python
from cell import Cell

# Create a basic cell
def create_basic_cell():
    p1 = Cell('p1', 'poly')
    m1 = Cell('m1', 'metal1')
    basic = Cell('basic', p1, m1)
    basic.constrain(p1, 'sx1=ox1, sx2=ox2, sy2+2<oy1', m1)
    return basic

# Create array of instances
basic1 = create_basic_cell()
basic2 = basic1.copy()
basic3 = basic1.copy()

array = Cell('array', basic1, basic2, basic3)
array.constrain(basic1, 'sx2+10<ox1', basic2)
array.constrain(basic2, 'sx2+10<ox1', basic3)

array.draw()
```

### Example 3: GDS Export

```python
from gds_cell import Cell, Polygon, CellInstance

# Create library cell
lib_cell = Cell('transistor')
gate = Polygon('gate', 'poly')
source = Polygon('source', 'diff')
drain = Polygon('drain', 'diff')
lib_cell.add_polygon([gate, source, drain])

lib_cell.constrain(source, 'sx2<ox1', gate)
lib_cell.constrain(gate, 'sx2<ox1', drain)

# Use in design
top = Cell('top')
t1 = CellInstance('t1', lib_cell)
t2 = CellInstance('t2', lib_cell)
top.add_instance([t1, t2])
top.constrain(t1, 'sx2+20<ox1', t2)

# Export to GDS
top.solver()
top.export_gds('design.gds')
```

## Testing

Run the included test files:

```bash
python test_cell.py
python test_gds_cell.py
```

## Implementation Notes

### Why SciPy?

Originally implemented with Z3 SMT solver, the library was refactored to use SciPy for several reasons:

- **Broader compatibility**: SciPy is more commonly installed in scientific Python environments
- **Simpler dependencies**: No need for specialized SMT solver binaries
- **Performance**: For geometric constraint problems, optimization often performs well
- **Maintained API**: Complete refactor with no API changes

### Limitations

- **Linear constraints only**: Constraint expressions must be linear combinations of variables
- **Local optima**: SLSQP may find local rather than global optima
- **Numerical precision**: Floating-point arithmetic may introduce small errors
- **Constraint feasibility**: No automatic diagnosis of infeasible constraint systems

### Tips for Best Results

1. **Provide good initial guesses**: The solver uses heuristic initial positions
2. **Avoid over-constraining**: Too many constraints may be infeasible
3. **Check solver return value**: Always check if `solver()` returns `True`
4. **Use appropriate spacing**: Add small gaps (e.g., `+3`) in spacing constraints
5. **Test incrementally**: Build and test complex hierarchies step by step

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Author

Steven Chen

## Acknowledgments

Built with SciPy, NumPy, Matplotlib, and gdstk.
