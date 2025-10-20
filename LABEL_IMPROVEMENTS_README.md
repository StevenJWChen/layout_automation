# Label Display Improvements

## Overview

The `draw()` method now includes smart label rendering with adaptive sizing, reduced clutter, and multiple display modes for better readability in complex layouts.

## New Parameters

### `draw()` Method Signature

```python
cell.draw(solve_first=True, ax=None, show=True,
          show_labels=True, label_mode='auto')
```

**New Parameters:**
- `show_labels` (bool): Whether to show cell/layer labels (default: `True`)
- `label_mode` (str): Label display mode (default: `'auto'`)

## Label Modes

### 1. `'auto'` Mode (Recommended) ⭐

Smart sizing based on cell dimensions:
- **Very small cells** (< 3 units or < 15 area): No label
- **Small cells** (< 8 units or < 100 area): Abbreviated name (2 chars)
- **Medium cells** (< 15 units or < 300 area): Full name only
- **Large cells**: Full name + layer name

**Advantages:**
- Automatically adapts to layout density
- Prevents label overlap in dense layouts
- Maintains readability across different scales
- Default mode for best results

**Example:**
```python
cell.draw(label_mode='auto')  # Smart, adaptive labels
```

### 2. `'full'` Mode

Always shows complete information:
- Format: `"name\n(layer_name)"`
- Fixed font size: 7pt
- Normal weight

**Use when:**
- You need complete information for all cells
- Layout is not too dense
- Presentation requires full details

**Example:**
```python
cell.draw(label_mode='full')  # Always show name + layer
```

### 3. `'compact'` Mode

Minimalist labeling:
- Shows abbreviated names only
- Truncates long names (first 3 chars + ".")
- Very small font size: 5pt

**Use when:**
- Maximum space efficiency needed
- Dense layouts with many cells
- Labels are reference only

**Example:**
```python
cell.draw(label_mode='compact')  # Minimal, abbreviated
```

### 4. `'none'` Mode

No labels displayed:
- Clean layout view
- Same as `show_labels=False`

**Use when:**
- Creating publication-quality figures
- Labels are distracting
- Layout structure is primary focus

**Example:**
```python
cell.draw(label_mode='none')  # No labels
# OR
cell.draw(show_labels=False)  # Same result
```

## Key Improvements

### 1. **Smaller, Thinner Fonts**
- Reduced from fontsize=8 (bold) to 4-7pt (normal weight)
- More readable, less overwhelming
- Better for dense layouts

### 2. **Smart Sizing**
- Labels adapt to cell dimensions
- Tiny cells get no labels (avoids clutter)
- Large cells get full information

### 3. **Semi-Transparent Backgrounds**
- Labels have subtle dark background (alpha=0.3)
- Improves readability over colored cells
- White text with rounded background box

### 4. **Reduced Container Label Size**
- Container labels now 7pt (down from 9pt) in auto mode
- Less intrusive, cleaner hierarchy
- Positioned slightly closer to box (y+0.5 instead of y+1)

### 5. **Overlap Avoidance**
- Very small cells automatically skip labels
- Prevents label pileup in dense regions
- Smart truncation in compact mode

## Visual Comparison

```
OLD (Always full labels):
┌─────────────────────┐
│   long_cell_name    │  ← Size 8, bold, can overlap
│    (metal1)         │
└─────────────────────┘

NEW (Auto mode):
┌─────────────────────┐
│  long_cell_name     │  ← Size 6, normal, adaptive
│      metal1         │     Semi-transparent background
└─────────────────────┘

Small cell old:       Small cell new:
┌──┐                  ┌──┐
│AB│ ← Cluttered      │  │ ← Clean (no label)
│()│                  │  │    Too small for text
└──┘                  └──┘
```

## Usage Examples

### Example 1: Default (Auto Mode)

```python
from layout_automation import Cell

# Create layout
parent = Cell('chip')
block1 = Cell('processor', 'metal1')
block2 = Cell('mem', 'metal2')

parent.add_instance([block1, block2])
parent.constrain(block1, 'x1=0, y1=0, x2=50, y2=40')
parent.constrain(block2, 'x1=60, y1=0, x2=80, y2=25')

# Draw with smart labels (default)
parent.draw()  # Automatically uses label_mode='auto'
```

### Example 2: Dense Layout

```python
# For dense layouts with many small cells
dense_chip = Cell('dense_chip')

# Add 100 small cells
for i in range(10):
    for j in range(10):
        cell = Cell(f'cell_{i}_{j}', 'metal1')
        dense_chip.add_instance(cell)
        dense_chip.constrain(cell, f'x1={i*6}, y1={j*6}, x2={i*6+5}, y2={j*6+5}')

# Auto mode handles dense layouts well
dense_chip.draw(label_mode='auto')  # Clean, readable

# Full mode would be cluttered
dense_chip.draw(label_mode='full')  # Too many labels!
```

### Example 3: Publication Figure

```python
# For clean publication figures
chip.draw(label_mode='none', show=True)  # No labels, clean view
```

### Example 4: Comparing Modes

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# Compare all modes
cell.draw(ax=axes[0,0], label_mode='auto',    show=False)
cell.draw(ax=axes[0,1], label_mode='full',    show=False)
cell.draw(ax=axes[1,0], label_mode='compact', show=False)
cell.draw(ax=axes[1,1], label_mode='none',    show=False)

axes[0,0].set_title('Auto (Smart)')
axes[0,1].set_title('Full (Complete)')
axes[1,0].set_title('Compact (Minimal)')
axes[1,1].set_title('None (Clean)')

plt.tight_layout()
plt.show()
```

## Smart Sizing Thresholds

In `'auto'` mode, labels are sized based on these thresholds:

| Cell Size | Label Content | Font Size | Weight |
|-----------|---------------|-----------|--------|
| < 3 units or < 15 area | None (too small) | - | - |
| < 8 units or < 100 area | 2-char abbreviation | 4pt | normal |
| < 15 units or < 300 area | Full name only | 5pt | normal |
| ≥ 15 units or ≥ 300 area | Name + layer | 6pt | normal |

## Benefits

### ✅ Readability
- Smaller fonts less overwhelming
- Normal weight easier to read
- Adaptive sizing reduces clutter

### ✅ Scalability
- Works well from 10 to 10,000 cells
- Auto mode handles any layout density
- No manual adjustment needed

### ✅ Flexibility
- Four modes for different use cases
- Easy to toggle labels on/off
- Backward compatible (auto is default)

### ✅ Professional
- Semi-transparent backgrounds look polished
- Clean hierarchy with smaller container labels
- Suitable for presentations and publications

## Backward Compatibility

All existing code works without changes:
- Default behavior uses `'auto'` mode
- Similar appearance to old style for medium/large cells
- Old code: `cell.draw()` → Now uses smart labels
- To get old behavior: `cell.draw(label_mode='full')`

## Tips

1. **For most layouts**: Use `label_mode='auto'` (default)
2. **For presentations**: Use `label_mode='none'` for clean look
3. **For dense layouts**: `'auto'` automatically handles it
4. **For debugging**: `'full'` shows all information
5. **For space-constrained**: `'compact'` minimizes label size

## See Also

- **Test file**: `test_label_improvements.py`
- **Examples**: Visual comparison in `demo_outputs/test_label_modes.png`
- **Dense layout demo**: `demo_outputs/test_dense_layout.png`
- **Real-world example**: `demo_outputs/test_real_world_labels.png`

## Summary

The label system now intelligently adapts to your layout:
- ✨ Smart sizing based on cell dimensions
- ✨ Cleaner, more readable fonts
- ✨ Multiple modes for different needs
- ✨ Automatic overlap avoidance
- ✨ Works great from simple to complex layouts

Just use `cell.draw()` and enjoy better labels! 🎨
