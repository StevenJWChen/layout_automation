# freeze_layout() vs fix_layout() - Analysis

## TL;DR

**NO, you should keep BOTH methods.** They serve different purposes:

- **`freeze_layout()`**: Treat cell as a **black box** (like an IP block you can't modify)
- **`fix_layout()`**: **Preserve internal structure** while allowing repositioning

## Detailed Comparison

| Feature | `freeze_layout()` | `fix_layout()` |
|---------|-------------------|----------------|
| **Purpose** | Lock cell as immutable black box | Preserve relationships, allow repositioning |
| **Children positions** | NOT updated when parent moves | Automatically updated when parent moves |
| **Solver behavior** | Children excluded from solver | Children excluded from solver |
| **Size constraint** | Fixed: `x2-x1 = frozen_width` | Fixed: `x2-x1 = max_offset` |
| **Internal structure** | Hidden (black box) | Accessible via `_fixed_offsets` |
| **Use case** | Reusable IP blocks | Repositionable sub-layouts |
| **After repositioning** | Children positions unchanged | Children automatically update |

## Key Difference

### freeze_layout() - Black Box Model

```python
block = Cell('ip_block')
# ... create complex layout ...
block.solver()
block.freeze_layout()  # Lock it as-is

# Use in parent
parent.constrain(block, 'x1=100, y1=50')
parent.solver()

# Result: Only block's bbox moves, children positions stay at original coords
# Children are NOT accessible/updated - treated as opaque black box
```

**When frozen**:
- `_frozen = True`
- `_frozen_bbox` stores the bounding box
- Children are **excluded** from solver (`_get_all_cells()` returns only parent)
- Children positions are **NOT updated** when parent moves

### fix_layout() - Repositionable Structure

```python
block = Cell('block')
# ... create complex layout ...
block.solver()
block.fix_layout()  # Preserve structure

# Use in parent
parent.constrain(block, 'x1=100, y1=50')
parent.solver()

# Result: Block AND all children move together maintaining relationships
# All internal polygons automatically update via stored offsets
```

**When fixed**:
- `_fixed = True`
- `_fixed_offsets` stores relative positions of all children
- Children are **excluded** from solver (`_get_all_cells()` returns only parent)
- Children positions **ARE updated** via `update_fixed_positions()` after solving

## Implementation Differences

### In Solver (`solver()` method)

Both behave similarly during solving:

```python
# Line 562-563: Both excluded from child traversal
if self._frozen or self._fixed:
    return cells  # Don't include children in solver

# Line 583-584: Both skip parent bound updates
if cell._fixed or cell._frozen:
    continue

# Line 652-653: Both skip bounding constraints
if not cell.is_leaf and len(cell.children) > 0 and not cell._frozen and not cell._fixed:
    # Add parent-child bounding constraints
```

### After Solving

**Key difference**:

```python
# Line 530: Only fix_layout updates children positions
self._update_all_fixed_positions()

# This calls update_fixed_positions() which:
def update_fixed_positions(self):
    if not self._fixed or len(self._fixed_offsets) == 0:
        return  # frozen cells don't have _fixed_offsets

    # Update children based on new parent position
    for child in self.children:
        if child.name in self._fixed_offsets:
            dx1, dy1, dx2, dy2 = self._fixed_offsets[child.name]
            child.pos_list = [
                px1 + dx1,
                py1 + dy1,
                px1 + dx2,
                py1 + dy2
            ]
```

**`freeze_layout()` does NOT update children** - they remain at original positions.

## Size Constraints

Both add fixed size constraints, but differently:

### freeze_layout():
```python
# Line 448-449
if cell._frozen and cell._frozen_bbox is not None:
    x1_f, y1_f, x2_f, y2_f = cell._frozen_bbox
    width = x2_f - x1_f
    height = y2_f - y1_f
    model.Add(x2_var - x1_var == width)
    model.Add(y2_var - y1_var == height)
```

### fix_layout():
```python
# Line 457-460
elif cell._fixed and len(cell._fixed_offsets) > 0:
    max_x_offset = max(offset[2] for offset in cell._fixed_offsets.values())
    max_y_offset = max(offset[3] for offset in cell._fixed_offsets.values())
    model.Add(x2_var - x1_var == max_x_offset)
    model.Add(y2_var - y1_var == max_y_offset)
```

## Use Cases

### Use `freeze_layout()` when:

1. **IP block reuse** - You have a complex cell you want to use as-is
2. **Performance optimization** - Exclude children from solver for speed
3. **Black box abstraction** - Don't care about internal structure
4. **Static placement** - Children positions never need to update

**Example**: Standard cell library, pre-designed analog blocks

### Use `fix_layout()` when:

1. **Repositionable layouts** - Need to move entire structure as unit
2. **GDS import** - Imported layouts that need repositioning
3. **Hierarchical design** - Sub-layouts that maintain internal relationships
4. **Manual positioning** - Using `set_position()` to place blocks

**Example**: Imported GDS blocks, hierarchical floorplanning

## Can One Replace the Other?

**NO**, because:

1. **Different behavior after repositioning**:
   - `freeze`: Children stay at original coordinates
   - `fix`: Children update with parent

2. **Different storage**:
   - `freeze`: `_frozen_bbox` (just 4 numbers)
   - `fix`: `_fixed_offsets` (dictionary of all children's offsets)

3. **Different semantics**:
   - `freeze`: "This is immutable"
   - `fix`: "This is repositionable but maintains structure"

## Memory & Performance

### freeze_layout():
- **Memory**: ~32 bytes (one tuple for bbox)
- **Computation**: None after initial freeze
- **Solver variables**: Only parent (4 variables)

### fix_layout():
- **Memory**: ~32 bytes × number of children (dictionary of offsets)
- **Computation**: `update_fixed_positions()` after each solve
- **Solver variables**: Only parent (4 variables)

Both are efficient, but `freeze` is slightly lighter.

## Recommendation

**Keep both methods** because:

1. ✅ They serve **different purposes**
2. ✅ They have **different semantics** (black box vs. repositionable)
3. ✅ They enable **different use cases**
4. ✅ The implementation is **clean and minimal**
5. ✅ Users may need **both behaviors** in the same design

### Potential Improvement

Consider adding a warning/error if user tries to do incompatible operations:

```python
def freeze_layout(self):
    if self._fixed:
        raise RuntimeError(f"Cell '{self.name}' is already fixed. Use unfix_layout() first.")
    # ... rest of implementation

def fix_layout(self):
    if self._frozen:
        raise RuntimeError(f"Cell '{self.name}' is already frozen. Use unfreeze_layout() first.")
    # ... rest of implementation
```

## Conclusion

**KEEP BOTH METHODS!**

They are:
- Complementary, not redundant
- Serving different use cases
- Both necessary for a complete layout system

The only potential issue is user confusion about which to use, which can be addressed with better documentation.
