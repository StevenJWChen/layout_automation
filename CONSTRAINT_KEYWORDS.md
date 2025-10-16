# Constraint Keywords - Quick Reference

Simple keyword replacement for more readable constraints.

## What Are Constraint Keywords?

Keywords are shorthand replacements for common constraint patterns. They get automatically expanded to full constraint syntax.

**Example:**
```python
# Instead of writing:
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

# You can write:
parent.constrain(child, 'center', parent)
```

## Complete Keyword List

### Center Keywords
| Keyword | Expands To | Meaning |
|---------|------------|---------|
| `center` | `sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2` | Center both X and Y |
| `xcenter` | `sx1+sx2=ox1+ox2` | Center horizontally |
| `ycenter` | `sy1+sy2=oy1+oy2` | Center vertically |

### Alignment Keywords
| Keyword | Expands To | Meaning |
|---------|------------|---------|
| `left` | `sx1=ox1` | Align left edges |
| `right` | `sx2=ox2` | Align right edges |
| `top` | `sy2=oy2` | Align top edges |
| `bottom` | `sy1=oy1` | Align bottom edges |

### Size Keywords
| Keyword | Expands To | Meaning |
|---------|------------|---------|
| `swidth` | `sx2-sx1` | Subject width |
| `sheight` | `sy2-sy1` | Subject height |
| `owidth` | `ox2-ox1` | Object width |
| `oheight` | `oy2-oy1` | Object height |
| `width` | `x2-x1` | Width (self-constraint) |
| `height` | `y2-y1` | Height (self-constraint) |

### Position Keywords
| Keyword | Expands To | Meaning |
|---------|------------|---------|
| `sx` | `sx1` | Subject X position |
| `sy` | `sy1` | Subject Y position |
| `ox` | `ox1` | Object X position |
| `oy` | `oy1` | Object Y position |

## Usage Examples

### Example 1: Center Child in Parent
```python
# Old way
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)

# New way
parent.constrain(child, 'center', parent)
```

### Example 2: Center X and Set Width
```python
# Old way
parent.constrain(child, 'sx1+sx2=ox1+ox2, sx2-sx1=10', parent)

# New way
parent.constrain(child, 'xcenter, swidth=10', parent)
```

### Example 3: Align Left and Match Height
```python
# Old way
parent.constrain(child2, 'sx1=ox1, sy2-sy1=oy2-oy1', child1)

# New way
parent.constrain(child2, 'left, sheight=oheight', child1)
```

### Example 4: Position to the Right with Spacing
```python
# Old way
parent.constrain(child2, 'sx1=ox2+10, sy1=oy1', child1)

# New way
parent.constrain(child2, 'sx=ox2+10, sy=oy', child1)
```

### Example 5: Set Fixed Size (Self-Constraint)
```python
# Old way
cell.constrain('x2-x1=100, y2-y1=50')

# New way
cell.constrain('width=100, height=50')
```

### Example 6: Match Size
```python
# Old way
parent.constrain(child2, 'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', child1)

# New way
parent.constrain(child2, 'swidth=owidth, sheight=oheight', child1)
```

## Combining Keywords

Keywords can be combined with commas and work with any operators:

```python
# Multiple keywords
parent.constrain(child, 'center, swidth=20', parent)
parent.constrain(child2, 'left, top, swidth=owidth', child1)

# Keywords with expressions
parent.constrain(child, 'xcenter, swidth=owidth+5', ref)
parent.constrain(child2, 'sx=ox2+10, sy=oy, swidth>=20', child1)

# Mix keywords and full syntax
parent.constrain(child, 'xcenter, sy1=oy2+5', ref)
```

## Print Reference Table

```python
from layout_automation.constraint_keywords import print_keyword_reference

# Display complete reference table with all keywords
print_keyword_reference()
```

## Complete Example

```python
from layout_automation.cell import Cell

# Create layout
layout = Cell('EXAMPLE')

# Create cells
base = Cell('base', 'diff')
left = Cell('left', 'metal1')
right = Cell('right', 'metal1')
center = Cell('center', 'poly')

layout.add_instance([base, left, right, center])

# Use keywords for all constraints
layout.constrain(base, 'x1=0, y1=0, width=100, height=40')
layout.constrain(left, 'sx=ox+5, sy=oy+5, swidth=25, sheight=30', base)
layout.constrain(right, 'right, bottom, swidth=25, sheight=30', base)
layout.constrain(center, 'xcenter, ycenter, swidth=10, sheight=50', base)

# Solve
layout.solver()
layout.export_gds('example.gds')
```

## Benefits

✅ **Shorter** - Less typing
✅ **Readable** - Clear intent
✅ **Less Error-Prone** - No manual coordinate calculations
✅ **Backwards Compatible** - Full syntax still works
✅ **Flexible** - Mix keywords and full syntax

## Implementation

Keywords are automatically expanded in the `constrain()` method:

```python
# Input
parent.constrain(child, 'center, swidth=10', parent)

# Automatically becomes
parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2, sx2-sx1=10', parent)
```

The expansion happens transparently - you don't need to do anything special!

## Testing

Run the test to see all keywords in action:

```bash
python examples/test_constraint_keywords.py
```

This will:
- Show keyword expansion examples
- Test each keyword category
- Generate example GDS files
- Compare old vs new syntax

## See Also

- `constraint_keywords.py` - Keyword definitions and expansion logic
- `test_constraint_keywords.py` - Comprehensive tests
- `CELL_FEATURES_GUIDE.md` - Complete Cell class documentation
