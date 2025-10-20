# Edge Distance Keywords

## Overview

Edge distance keywords provide an intuitive way to express relationships between cell edges in constraint-based layouts. These keywords represent the **distance** (difference) between edges of two cells.

## New Keywords Added

### Horizontal Edge Keywords

| Keyword | Expansion | Description |
|---------|-----------|-------------|
| `ll_edge` | `sx1-ox1` | Distance from subject's **left** to object's **left** |
| `lr_edge` | `sx1-ox2` | Distance from subject's **left** to object's **right** |
| `rl_edge` | `sx2-ox1` | Distance from subject's **right** to object's **left** |
| `rr_edge` | `sx2-ox2` | Distance from subject's **right** to object's **right** |

### Vertical Edge Keywords

| Keyword | Expansion | Description |
|---------|-----------|-------------|
| `bb_edge` | `sy1-oy1` | Distance from subject's **bottom** to object's **bottom** |
| `bt_edge` | `sy1-oy2` | Distance from subject's **bottom** to object's **top** |
| `tb_edge` | `sy2-oy1` | Distance from subject's **top** to object's **bottom** |
| `tt_edge` | `sy2-oy2` | Distance from subject's **top** to object's **top** |

## Understanding Edge Distances

Edge keywords represent the **distance** between edges:
- **Positive value**: Subject edge is to the right/above object edge
- **Zero**: Edges are aligned
- **Negative value**: Subject edge is to the left/below object edge (overlap!)

###Formula

```
{edge}_edge = subject_edge_position - object_edge_position
```

## Primary Use Cases

### 1. **Edge Alignment** ⭐⭐⭐

The most intuitive use of edge keywords is for alignment:

```python
# Left edges aligned
parent.constrain(child2, 'll_edge=0', child1)
# Equivalent to: sx1=ox1

# Right edges aligned
parent.constrain(child2, 'rr_edge=0', child1)
# Equivalent to: sx2=ox2

# Bottom edges aligned
parent.constrain(child2, 'bb_edge=0', child1)
# Equivalent to: sy1=oy1

# Top edges aligned
parent.constrain(child2, 'tt_edge=0', child1)
# Equivalent to: sy2=oy2
```

### 2. **Overlap Detection** ⭐⭐⭐

Detect if cells overlap using inequality constraints:

```python
# Check horizontal overlap
# If lr_edge < 0, child2's left is inside child1 (overlap!)
parent.constrain(child2, 'lr_edge<0', child1)

# Check vertical overlap
# If tb_edge < 0, child2's top is inside child1 (overlap!)
parent.constrain(child2, 'tb_edge<0', child1)
```

### 3. **Complex Edge Relationships** ⭐⭐

Express precise edge-to-edge distances:

```python
# Subject's right edge is exactly 100 units from object's left
parent.constrain(child2, 'rl_edge=100', child1)

# Subject spans from object's left to 20 units past object's right
parent.constrain(child2, 'll_edge=0, rr_edge=20', child1)
```

## Examples

### Example 1: Left-Aligned Column

```python
from layout_automation import Cell

parent = Cell('parent')
box1 = Cell('box1', 'metal1')
box2 = Cell('box2', 'metal2')
box3 = Cell('box3', 'poly')

# Stack vertically with left alignment
parent.constrain(box1, 'x1=0, y1=0, x2=40, y2=20')
parent.constrain(box2, 'll_edge=0, sy1=oy2+5, swidth=30, sheight=15', box1)
parent.constrain(box3, 'll_edge=0, sy1=oy2+5, swidth=25, sheight=12', box2)

parent.solver()
# Result: All boxes have the same x1 (left-aligned)
```

### Example 2: Right-Aligned Column

```python
# Stack vertically with right alignment
parent.constrain(box1, 'x1=10, y1=0, x2=50, y2=20')
parent.constrain(box2, 'rr_edge=0, sy1=oy2+5, swidth=30, sheight=15', box1)
parent.constrain(box3, 'rr_edge=0, sy1=oy2+5, swidth=25, sheight=12', box2)

parent.solver()
# Result: All boxes have the same x2 (right-aligned)
```

### Example 3: Overlap Detection

```python
parent = Cell('parent')
cell1 = Cell('cell1', 'metal1')
cell2 = Cell('cell2', 'metal2')

parent.constrain(cell1, 'x1=0, y1=0, x2=40, y2=20')
parent.constrain(cell2, 'x1=30, y1=5, x2=60, y2=25')

parent.solver()

# Check for overlap
lr_dist = cell2.x1 - cell1.x2  # lr_edge value
if lr_dist < 0:
    print(f"Overlap detected! Cells overlap by {-lr_dist} units")
else:
    print(f"No overlap. Gap of {lr_dist} units")
```

### Example 4: Bottom-Aligned Row

```python
# Horizontal row with bottom alignment
parent.constrain(box1, 'x1=0, y1=0, x2=30, y2=20')
parent.constrain(box2, 'sx1=ox2+5, bb_edge=0, swidth=25, sheight=20', box1)
parent.constrain(box3, 'sx1=ox2+5, bb_edge=0, swidth=20, sheight=20', box2)

parent.solver()
# Result: All boxes have the same y1 (bottom-aligned)
```

## Comparison with Traditional Syntax

| Task | Traditional | With Edge Keywords | Notes |
|------|-------------|-------------------|-------|
| Left align | `sx1=ox1` | `ll_edge=0` | Both work, `ll_edge` more explicit |
| Right align | `sx2=ox2` | `rr_edge=0` | Both work, `rr_edge` more explicit |
| Overlap check | `sx1-ox2<0` | `lr_edge<0` | `lr_edge` much clearer! |
| Complex distance | `sx2-ox1=100` | `rl_edge=100` | `rl_edge` shows intent better |

## When to Use Edge Keywords

### ✅ Best For:
- **Alignment**: `ll_edge=0`, `rr_edge=0`, `bb_edge=0`, `tt_edge=0`
- **Overlap detection**: `lr_edge<0`, `tb_edge<0`
- **Complex edge relationships**: When you need precise edge-to-edge distances
- **Readability**: When edge distance semantics make intent clearer

### ⚠️ Consider Traditional Syntax For:
- **Simple positioning**: `sx1=ox2+10` is often clearer than `rl_edge=swidth+10`
- **One-sided constraints**: When you only care about one edge
- **Self-constraints**: Edge keywords need two objects

## Value Semantics

### Positive Values
```python
'll_edge=10'  # Subject's left is 10 units RIGHT of object's left
'tt_edge=5'   # Subject's top is 5 units ABOVE object's top
```

### Zero Values (Alignment)
```python
'll_edge=0'   # Left edges aligned
'rr_edge=0'   # Right edges aligned
'bb_edge=0'   # Bottom edges aligned
'tt_edge=0'   # Top edges aligned
```

### Negative Values (Overlap)
```python
'lr_edge=-5'  # Subject's left is 5 units INSIDE object (overlap)
'tb_edge=-3'  # Subject's top is 3 units BELOW object's bottom (overlap)
```

## Visual Reference

```
Horizontal Edge Keywords:

    Object:    [ox1]--------[ox2]

    Subject:   [sx1]--------[sx2]

    ll_edge = sx1 - ox1
    lr_edge = sx1 - ox2  (negative if subject inside object)
    rl_edge = sx2 - ox1
    rr_edge = sx2 - ox2
```

```
Vertical Edge Keywords:

            [oy2/sy2] ---- (top)
                |
                |
            [oy1/sy1] ---- (bottom)

    bb_edge = sy1 - oy1
    bt_edge = sy1 - oy2
    tb_edge = sy2 - oy1
    tt_edge = sy2 - oy2
```

## Common Patterns

### Pattern 1: Align and Stack Vertically
```python
# Left-aligned vertical stack
parent.constrain(box1, 'x1=0, y1=0, width=40, height=20')
parent.constrain(box2, 'll_edge=0, sy1=oy2+gap', box1)
parent.constrain(box3, 'll_edge=0, sy1=oy2+gap', box2)
```

### Pattern 2: Align and Arrange Horizontally
```python
# Bottom-aligned horizontal row
parent.constrain(box1, 'x1=0, y1=0, width=30, height=20')
parent.constrain(box2, 'sx1=ox2+gap, bb_edge=0', box1)
parent.constrain(box3, 'sx1=ox2+gap, bb_edge=0', box2)
```

### Pattern 3: Centered with Edge Constraints
```python
# Horizontally centered, top-aligned
parent.constrain(child, 'xcenter, tt_edge=0', parent)
```

## Tips

1. **Alignment is intuitive**: `ll_edge=0` clearly means "left edges aligned"
2. **Overlap detection**: Negative values indicate overlap
3. **Combine freely**: Mix edge keywords with other constraint keywords
4. **Choose clarity**: Use edge keywords when they make intent clearer

## See Also

- **Full keyword reference**: Run `print_keyword_reference()` from `constraint_keywords`
- **Test file**: `test_edge_keywords_simple.py`
- **Examples**: `example_edge_keywords.py`
- **Visual demo**: `demo_outputs/example_edge_keywords.png`

## Summary

Edge distance keywords make alignment and overlap detection more intuitive:
- 8 new keywords: `ll_edge`, `lr_edge`, `rl_edge`, `rr_edge`, `bb_edge`, `bt_edge`, `tb_edge`, `tt_edge`
- Perfect for alignment (=0), overlap detection (<0), and edge relationships
- Fully compatible with existing constraint system
- Use when they make your intent clearer!
