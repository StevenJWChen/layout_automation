# GDS Import/Export Developer Guide
## Layout Automation Toolkit - Internal Documentation

**Version:** 1.0
**Date:** January 5, 2026
**Audience:** Developers, Contributors, Maintainers

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Implementation Details](#implementation-details)
3. [Data Structures](#data-structures)
4. [Algorithm Design](#algorithm-design)
5. [Testing Strategy](#testing-strategy)
6. [Bug Fixes Deep Dive](#bug-fixes-deep-dive)
7. [Performance Considerations](#performance-considerations)
8. [Contributing Guidelines](#contributing-guidelines)
9. [Future Enhancements](#future-enhancements)

---

## Architecture Overview

### System Components

```
Layout Automation Toolkit
├── Cell Class (cell.py)
│   ├── Position Management
│   ├── Hierarchy Management
│   ├── GDS Export (_convert_to_gds)
│   └── GDS Import (_from_gds_cell)
│
├── Technology File (tech.py)
│   └── Layer Mapping
│
└── External Libraries
    └── gdstk (GDS-II manipulation)
```

### Design Principles

1. **Absolute Coordinates in Python** - All position management uses absolute coordinates
2. **Relative Coordinates in GDS** - Conversion happens during export/import
3. **Object Identity** - Using `id(cell)` for tracking, not names
4. **Lazy Evaluation** - GDS conversion only when needed
5. **Immutable Hierarchy** - Once exported, hierarchy is frozen

---

## Implementation Details

### Cell Class (layout_automation/cell.py)

The `Cell` class is the core data structure representing layout elements.

#### Key Attributes

```python
class Cell:
    name: str              # Cell name (not unique!)
    layer_name: str        # Layer name (e.g., 'metal1')
    pos_list: List[float]  # [x1, y1, x2, y2] in absolute coordinates
    children: List[Cell]   # Child cells in hierarchy
    is_leaf: bool         # True if this is a leaf cell
```

#### Position System

**Invariant:** `pos_list` always contains absolute coordinates relative to the top-level origin (0, 0).

```python
# Example hierarchy
top.pos_list = [0, 0, 1000, 1000]      # Origin at (0, 0)
mid.pos_list = [100, 100, 400, 400]    # Origin at (100, 100)
leaf.pos_list = [150, 150, 250, 250]   # Origin at (150, 150)

# Relative to parent:
# mid relative to top: (100, 100)
# leaf relative to mid: (50, 50)  # NOT (150, 150)!
```

This design decision simplifies position management in Python while requiring coordinate transformation during GDS export.

---

## GDS Export Implementation

### Method Signature

```python
def _convert_to_gds(self, lib: 'gdstk.Library',
                    gds_cells_dict: Dict,
                    layer_map: Dict,
                    gds_name_counter: Dict = None) -> 'gdstk.Cell'
```

### Parameters Deep Dive

**`gds_cells_dict: Dict`**
- **Key:** `id(cell)` - Python object ID (unique per object)
- **Value:** `gdstk.Cell` - Corresponding GDS cell
- **Purpose:** Enables cell reuse detection and prevents infinite recursion

**`gds_name_counter: Dict`**
- **Key:** Cell name string
- **Value:** Integer counter
- **Purpose:** Generate unique GDS names (rect, rect_1, rect_2)

### Algorithm Flow

```python
def _convert_to_gds(self, lib, gds_cells_dict, layer_map, gds_name_counter=None):
    # 1. Initialize name counter (only on first call)
    if gds_name_counter is None:
        gds_name_counter = {}

    # 2. Check if already converted (cell reuse)
    cell_id = id(self)
    if cell_id in gds_cells_dict:
        return gds_cells_dict[cell_id]  # Reuse existing

    # 3. Generate unique GDS name
    gds_cell_name = self.name
    if gds_cell_name in gds_name_counter:
        gds_name_counter[gds_cell_name] += 1
        gds_cell_name = f"{self.name}_{gds_name_counter[gds_cell_name]}"
    else:
        gds_name_counter[gds_cell_name] = 0

    # 4. Create GDS cell and register it
    gds_cell = lib.new_cell(gds_cell_name)
    gds_cells_dict[cell_id] = gds_cell

    # 5. Calculate parent origin for relative positioning
    parent_x1 = self.pos_list[0] if all(v is not None for v in self.pos_list) else 0
    parent_y1 = self.pos_list[1] if all(v is not None for v in self.pos_list) else 0

    # 6. Process children recursively
    for child in self.children:
        if child.is_leaf:
            # Leaf cell: create geometry
            child_gds = create_leaf_cell(child, lib, gds_cells_dict, layer_map, gds_name_counter)
        else:
            # Non-leaf: recurse
            child_gds = child._convert_to_gds(lib, gds_cells_dict, layer_map, gds_name_counter)

        # 7. Create reference with RELATIVE position
        x1, y1, _, _ = child.pos_list
        ref = gdstk.Reference(child_gds, origin=(x1 - parent_x1, y1 - parent_y1))
        gds_cell.add(ref)

    return gds_cell
```

### Coordinate Transformation

**Critical Code Section (cell.py:1806-1855)**

```python
# Get parent's origin
parent_x1 = self.pos_list[0] if all(v is not None for v in self.pos_list) else 0
parent_y1 = self.pos_list[1] if all(v is not None for v in self.pos_list) else 0

# Child absolute position
x1, y1, _, _ = child.pos_list

# Create reference with relative offset
ref = gdstk.Reference(child_gds_cell, origin=(x1 - parent_x1, y1 - parent_y1))
```

**Why this works:**
- Parent at (100, 100), child at (150, 150)
- GDS reference: `(150 - 100, 150 - 100)` = `(50, 50)`
- When GDS reader places parent at (100, 100), child appears at (100 + 50, 100 + 50) = (150, 150) ✓

---

## GDS Import Implementation

### Method Signature

```python
@classmethod
def from_gds(cls, filename: str,
             cell_name: Optional[str] = None,
             layer_map: Optional[Dict[Tuple[int, int], str]] = None,
             use_tech_file: bool = True) -> 'Cell'
```

### Import Process

```python
def _from_gds_cell(cls, gds_cell, layer_map, parent_origin=(0, 0)):
    # 1. Create cell
    cell = cls(name=gds_cell.name)

    # 2. Process polygons (leaf geometry)
    for polygon in gds_cell.polygons:
        layer_name = layer_map.get((polygon.layer, polygon.datatype), 'unknown')
        # Create leaf cell from polygon
        leaf = create_leaf_from_polygon(polygon, layer_name, parent_origin)
        cell.add_instance(leaf)

    # 3. Process cell references (hierarchy)
    for ref in gds_cell.references:
        # Get reference origin (relative to parent)
        ref_origin = ref.origin if ref.origin else (0, 0)

        # Calculate absolute position
        abs_x = parent_origin[0] + ref_origin[0]
        abs_y = parent_origin[1] + ref_origin[1]

        # Recursively import child
        child = cls._from_gds_cell(ref.cell, layer_map, parent_origin=(abs_x, abs_y))

        # Set child's absolute position
        child.pos_list = [abs_x, abs_y, ...]

        cell.add_instance(child)

    return cell
```

**Key Point:** Import converts relative GDS coordinates back to absolute Python coordinates.

---

## Data Structures

### Cell Tracking Dictionaries

#### gds_cells_dict

```python
{
    140234567891234: <gdstk.Cell 'rect'>,      # First 'rect' cell
    140234567892345: <gdstk.Cell 'rect_1'>,    # Second 'rect' cell
    140234567893456: <gdstk.Cell 'block'>,     # Block cell
}
```

**Key insight:** Using object ID as key allows multiple cells with same name.

#### gds_name_counter

```python
{
    'rect': 2,      # Seen 'rect' 3 times (0, 1, 2)
    'block': 0,     # Seen 'block' 1 time (0)
    'top': 1,       # Seen 'top' 2 times (0, 1)
}
```

**Naming pattern:**
- First occurrence: Use original name
- Second occurrence: Append `_1`
- Third occurrence: Append `_2`
- etc.

### Layer Mapping

#### Export (Python → GDS)

```python
layer_map: Dict[str, Tuple[int, int]] = {
    'metal1': (30, 0),   # layer 30, datatype 0
    'metal2': (50, 0),   # layer 50, datatype 0
    'via1': (60, 0),
}
```

#### Import (GDS → Python)

```python
layer_map: Dict[Tuple[int, int], str] = {
    (30, 0): 'metal1',   # Reverse mapping
    (50, 0): 'metal2',
    (60, 0): 'via1',
}
```

---

## Algorithm Design

### Cell Reuse Detection

**Problem:** How to detect when the same cell is used multiple times?

**Solution:** Use Python object identity (`id()`).

```python
# Same object, different references
shared = Cell('rect', 'metal1')
block1.add_instance(shared)
block2.add_instance(shared)

# id(shared) is identical in both cases
# → gds_cells_dict[id(shared)] already exists
# → Return existing GDS cell, don't create new one
```

**Benefits:**
- Zero overhead (O(1) dictionary lookup)
- Perfect accuracy (object identity is unique)
- No content comparison needed

### Name Collision Resolution

**Problem:** Different cells can have the same name.

**Solution:** Append counter suffix.

```python
# First 'rect' → 'rect'
# Second 'rect' → 'rect_1'
# Third 'rect' → 'rect_2'
```

**Algorithm:**

```python
if name in gds_name_counter:
    # Name collision
    gds_name_counter[name] += 1
    unique_name = f"{name}_{gds_name_counter[name]}"
else:
    # First occurrence
    gds_name_counter[name] = 0
    unique_name = name
```

**Time complexity:** O(1) per cell

### Hierarchical Traversal

**Algorithm:** Depth-first search (DFS)

```python
def traverse(cell):
    visit(cell)
    for child in cell.children:
        traverse(child)
```

**Properties:**
- Ensures parents are created before children
- Natural recursion matches GDS hierarchy
- Stack depth = maximum hierarchy depth

**Space complexity:** O(h) where h = hierarchy depth

---

## Testing Strategy

### Test Coverage Matrix

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| `test_gds_hierarchy_absolute.py` | Hierarchical positioning | Position accuracy |
| `test_gds_name_collision.py` | Name collision handling | Name uniqueness |
| `test_gds_cell_reuse.py` | Cell reuse detection | Reuse vs collision |
| `test_gds_top_cell.py` | Cell name 'top' | Edge case |

### Test Methodology

#### 1. Position Accuracy Tests

```python
# Create hierarchy with known positions
top.pos_list = [0, 0, 1000, 1000]
child.pos_list = [100, 100, 300, 300]

# Export and reimport
top.to_gds('test.gds')
imported = Cell.from_gds('test.gds')

# Verify positions match exactly
assert imported.children[0].pos_list == [100, 100, 300, 300]
```

**Success criteria:** Zero position shift (< 0.001 nm tolerance)

#### 2. Name Collision Tests

```python
# Create cells with identical names but different content
rect1 = Cell('rect', 'metal1')  # 100x100
rect2 = Cell('rect', 'metal2')  # 200x200

# Export
top.to_gds('test.gds')

# Import and verify both cells exist
lib = gdstk.read_gds('test.gds')
names = [cell.name for cell in lib.cells]
assert 'rect' in names
assert 'rect_1' in names

# Verify content preserved
rect_cell = next(c for c in lib.cells if c.name == 'rect')
rect1_cell = next(c for c in lib.cells if c.name == 'rect_1')
# Check geometries differ
```

**Success criteria:** All cells preserved with unique names

#### 3. Cell Reuse Tests

```python
# Same object used twice
shared = Cell('rect', 'metal1')
block1.add_instance(shared)
block2.add_instance(shared)

# Export
top.to_gds('test.gds')

# Verify only one GDS cell created
lib = gdstk.read_gds('test.gds')
rect_cells = [c for c in lib.cells if c.name == 'rect']
assert len(rect_cells) == 1  # Only one definition

# Verify multiple references
refs = sum(len(c.references) for c in lib.cells)
# Should have 2 references to same cell
```

**Success criteria:** One cell definition, multiple references

---

## Bug Fixes Deep Dive

### Bug #1: Hierarchical Position Shift

**Timeline:**
1. User reports: "polygon shift after gds in"
2. Initial hypothesis: Rounding errors
3. User corrects: "shift is not because of rounding"
4. Deep investigation reveals: Absolute vs relative coordinate issue

**Root Cause Analysis:**

```python
# BROKEN CODE (before fix):
def _convert_to_gds(self, lib, gds_cells_dict, layer_map):
    # ...
    for child in self.children:
        x1, y1, x2, y2 = child.pos_list
        # BUG: Using absolute position as reference origin!
        ref = gdstk.Reference(child_gds, origin=(x1, y1))
        gds_cell.add(ref)
```

**Why it broke:**

```
Parent at (100, 100)
Child at (150, 150)

GDS export:
- Parent cell created
- Child reference at origin (150, 150)  ← WRONG!

GDS import:
- Parent placed at (100, 100)
- Child reference says origin (150, 150)
- Child appears at (100 + 150, 100 + 150) = (250, 250)  ← SHIFTED!
```

**Fix:**

```python
# FIXED CODE:
parent_x1 = self.pos_list[0]
parent_y1 = self.pos_list[1]

for child in self.children:
    x1, y1, x2, y2 = child.pos_list
    # Use RELATIVE position
    ref = gdstk.Reference(child_gds, origin=(x1 - parent_x1, y1 - parent_y1))
    gds_cell.add(ref)
```

**Verification:**

```
Parent at (100, 100)
Child at (150, 150)

GDS export:
- Parent cell created at some position
- Child reference at origin (150 - 100, 150 - 100) = (50, 50)  ✓

GDS import:
- Parent placed at (100, 100)
- Child reference says origin (50, 50)
- Child appears at (100 + 50, 100 + 50) = (150, 150)  ✓ CORRECT!
```

**Impact:** Fixes ALL hierarchical position shifts

**Code location:** `layout_automation/cell.py:1806-1855`

---

### Bug #2: Cell Name Collision Data Loss

**User Report:** "if you have the same cell name in different cell, it will be over write. Please don't use cell name as index in anywhere"

**Root Cause Analysis:**

```python
# BROKEN CODE (before fix):
def _convert_to_gds(self, lib, gds_cells_dict, layer_map):
    # BUG: Using name as dictionary key!
    if self.name in gds_cells_dict:
        return gds_cells_dict[self.name]

    gds_cell = lib.new_cell(self.name)
    gds_cells_dict[self.name] = gds_cell  # ← OVERWRITES previous cell with same name!
```

**Why it broke:**

```python
rect1 = Cell('rect', 'metal1')  # 100x100, id=12345
rect2 = Cell('rect', 'metal2')  # 200x200, id=67890

# First conversion:
gds_cells_dict['rect'] = <GDS cell with 100x100 geometry>

# Second conversion:
gds_cells_dict['rect'] = <GDS cell with 200x200 geometry>  # OVERWRITES!

# Result: First cell LOST!
```

**Fix:**

```python
# FIXED CODE:
def _convert_to_gds(self, lib, gds_cells_dict, layer_map, gds_name_counter):
    # Use object ID as key
    cell_id = id(self)

    if cell_id in gds_cells_dict:
        return gds_cells_dict[cell_id]

    # Generate unique name
    gds_cell_name = self.name
    if gds_cell_name in gds_name_counter:
        gds_name_counter[gds_cell_name] += 1
        gds_cell_name = f"{self.name}_{gds_name_counter[gds_cell_name]}"
    else:
        gds_name_counter[gds_cell_name] = 0

    gds_cell = lib.new_cell(gds_cell_name)
    gds_cells_dict[cell_id] = gds_cell  # Key by ID, not name!
```

**Verification:**

```python
rect1 = Cell('rect', 'metal1')  # id=12345
rect2 = Cell('rect', 'metal2')  # id=67890

# First conversion:
gds_cells_dict[12345] = <GDS cell 'rect' with 100x100>
gds_name_counter['rect'] = 0

# Second conversion:
gds_cells_dict[67890] = <GDS cell 'rect_1' with 200x200>
gds_name_counter['rect'] = 1

# Result: Both cells preserved! ✓
```

**Impact:** Prevents data loss in all name collision scenarios

**Code location:** `layout_automation/cell.py:1786-1804`

---

## Performance Considerations

### Time Complexity

**Export:**
- Cell traversal: O(n) where n = number of cells
- Dictionary lookup: O(1) per cell
- Total: **O(n)**

**Import:**
- GDS parsing: O(n)
- Cell creation: O(n)
- Total: **O(n)**

### Space Complexity

**Export:**
- `gds_cells_dict`: O(n) - one entry per unique cell
- `gds_name_counter`: O(u) where u = number of unique names
- Recursion stack: O(h) where h = hierarchy depth
- Total: **O(n + h)**

**Import:**
- Similar to export: **O(n + h)**

### Optimization Opportunities

1. **Memoization:** Already implemented via `gds_cells_dict`
2. **Lazy evaluation:** Could defer GDS conversion until needed
3. **Parallel processing:** Could process independent subtrees in parallel
4. **Streaming:** For very large designs, could stream GDS output

### Memory Usage

Typical IC block with 10,000 cells:
- `gds_cells_dict`: ~800 KB (80 bytes × 10,000)
- `gds_name_counter`: ~10 KB (typical case)
- Recursion stack: ~1 KB (depth ~10-20)
- **Total overhead: ~1 MB**

Very reasonable for modern systems.

---

## Contributing Guidelines

### Code Style

Follow PEP 8 with these additions:

```python
# Type hints required
def function_name(param: str, optional: Optional[int] = None) -> bool:
    """Docstring required for all public functions"""
    pass

# Descriptive variable names
gds_cells_dict  # Good
d  # Bad

# Comments for complex logic
# Calculate relative position for GDS reference
rel_x = child_x - parent_x
```

### Testing Requirements

**All changes must include:**
1. Unit tests
2. Integration tests
3. Documentation updates
4. Changelog entry

**Test coverage target:** ≥ 90%

### Pull Request Process

1. Create feature branch: `git checkout -b feature/description`
2. Make changes with tests
3. Run test suite: `pytest test_*.py`
4. Update documentation
5. Submit PR with description
6. Address review comments
7. Merge when approved

### Bug Report Template

```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Create cell with...
2. Export to GDS...
3. Observe incorrect...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Code Sample:**
```python
# Minimal reproducible example
```

**Environment:**
- Python version:
- gdstk version:
- OS:
```

---

## Future Enhancements

### Planned Features

#### 1. Content-Based Cell Deduplication

**Goal:** Detect cells with identical content even if different objects

```python
def get_cell_signature(cell):
    """Generate hash of cell content"""
    content = (
        cell.layer_name,
        tuple(cell.pos_list),
        tuple(id(child) for child in cell.children)
    )
    return hash(content)

# Use signature to detect identical cells
if signature in signature_dict:
    return signature_dict[signature]  # Reuse
```

**Benefit:** Smaller GDS files, better performance

#### 2. Incremental GDS Export

**Goal:** Only export changed cells

```python
def to_gds_incremental(self, filename, previous_state):
    """Only export cells that changed since previous_state"""
    changed_cells = detect_changes(self, previous_state)
    export_cells(changed_cells, filename)
```

**Benefit:** Faster export for large designs with small changes

#### 3. GDS Validation

**Goal:** Verify GDS correctness before writing

```python
def validate_gds(self):
    """Check for common GDS errors"""
    errors = []

    # Check for infinite recursion
    if has_circular_reference(self):
        errors.append("Circular reference detected")

    # Check for missing positions
    if any(v is None for v in self.pos_list):
        errors.append("Incomplete position data")

    return errors
```

**Benefit:** Catch errors before export

#### 4. Parallel Export

**Goal:** Export independent subtrees in parallel

```python
from concurrent.futures import ThreadPoolExecutor

def to_gds_parallel(self, filename):
    """Export using multiple threads"""
    independent_subtrees = find_independent_subtrees(self)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(export_subtree, tree)
            for tree in independent_subtrees
        ]
        results = [f.result() for f in futures]

    merge_gds_files(results, filename)
```

**Benefit:** Faster export for large, flat hierarchies

### Research Directions

1. **Machine Learning for Layout Optimization**
   - Predict optimal cell placement
   - Auto-detect reusable patterns

2. **GDS Compression**
   - Custom compression for IC layouts
   - Exploit pattern repetition

3. **Cloud-Based GDS Processing**
   - Distribute export/import across servers
   - Handle designs too large for single machine

---

## API Reference

### Core Methods

#### Cell._convert_to_gds()

```python
def _convert_to_gds(
    self,
    lib: gdstk.Library,
    gds_cells_dict: Dict[int, gdstk.Cell],
    layer_map: Dict[str, Tuple[int, int]],
    gds_name_counter: Optional[Dict[str, int]] = None
) -> gdstk.Cell
```

**Purpose:** Convert cell hierarchy to GDS format (internal method)

**Parameters:**
- `lib`: GDS library to add cells to
- `gds_cells_dict`: Tracking dict (key=id(cell), value=gds_cell)
- `layer_map`: Python layer names → (GDS layer, datatype)
- `gds_name_counter`: Name usage counter for unique naming

**Returns:** `gdstk.Cell` representing this cell

**Side Effects:**
- Modifies `gds_cells_dict`
- Modifies `gds_name_counter`
- Adds cells to `lib`

**Complexity:** O(n) where n = number of cells in subtree

**Example:**
```python
import gdstk
lib = gdstk.Library()
gds_cells_dict = {}
layer_map = {'metal1': (30, 0)}
gds_cell = cell._convert_to_gds(lib, gds_cells_dict, layer_map)
```

#### Cell._from_gds_cell()

```python
@classmethod
def _from_gds_cell(
    cls,
    gds_cell: gdstk.Cell,
    layer_map: Dict[Tuple[int, int], str],
    parent_origin: Tuple[float, float] = (0, 0)
) -> Cell
```

**Purpose:** Import cell from GDS (internal method)

**Parameters:**
- `gds_cell`: GDS cell to import
- `layer_map`: (GDS layer, datatype) → Python layer name
- `parent_origin`: Parent's absolute origin for coordinate calculation

**Returns:** `Cell` object with hierarchy

**Complexity:** O(n) where n = number of cells in subtree

---

## Appendix

### Glossary

- **Absolute coordinates:** Position relative to top-level origin (0, 0)
- **Relative coordinates:** Position relative to parent cell origin
- **Cell reuse:** Same object instance used multiple times
- **Name collision:** Different objects with identical names
- **GDS-II:** Industry standard IC layout file format
- **gdstk:** Python library for GDS manipulation
- **Hierarchy:** Parent-child relationship structure
- **Layer mapping:** Translation between logical and physical layers

### References

1. **GDS-II Format Specification**
   - SEMI Standard P39-0309
   - http://www.artwork.com/gdsii/gdsii/index.htm

2. **gdstk Documentation**
   - https://heitzmann.github.io/gdstk/

3. **FreePDK45**
   - https://eda.ncsu.edu/freepdk/freepdk45/

### Version History

- **1.0** (January 2026)
  - Initial release
  - Fixed hierarchical position shift
  - Fixed cell name collision
  - Comprehensive test coverage

---

**End of Developer Guide**
