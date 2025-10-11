# GDS Constraint Tool - Quick Reference

## 🚀 Quick Start

```bash
# 1. Convert GDS → Constraints
python tools/gds_to_constraints.py input.gds output.yaml

# 2. Edit output.yaml in any text editor
#    Change width, height, x1, y1, x2, y2 values

# 3. Regenerate GDS
python tools/gds_to_constraints.py --regenerate output.yaml modified.gds
```

## 📝 Command Line

```bash
# Convert to YAML (recommended)
python tools/gds_to_constraints.py layout.gds constraints.yaml [cell_name]

# Convert to JSON
python tools/gds_to_constraints.py layout.gds constraints.json

# Regenerate GDS
python tools/gds_to_constraints.py --regenerate constraints.yaml output.gds
```

## 🐍 Python API

### Convert

```python
from tools.gds_to_constraints import convert_gds_to_constraints

convert_gds_to_constraints(
    'input.gds',
    'output.yaml',
    cell_name='my_cell',     # Optional
    layer_map={67: 'metal1'} # Optional
)
```

### Modify

```python
from tools.gds_to_constraints import GDSToConstraints

converter = GDSToConstraints('input.gds')
constraints = converter.extract_constraints()

# Modify
for poly in constraints.polygons:
    poly.width *= 1.5  # Make 50% wider
    poly.x2 = poly.x1 + poly.width

converter.export_to_yaml('modified.yaml', constraints)
```

### Regenerate

```python
from tools.gds_to_constraints import regenerate_gds_from_constraints

regenerate_gds_from_constraints('modified.yaml', 'output.gds')
```

## 📄 YAML Format

```yaml
cell_name: my_cell
dimensions:
  width: 100.0
  height: 50.0
polygons:
  - name: metal1_1
    layer: metal1
    layer_num: 67
    datatype: 0
    position:
      x1: 0.0    # ← Edit
      y1: 0.0    # ← Edit
      x2: 20.0   # ← Edit
      y2: 10.0   # ← Edit
    size:
      width: 20.0   # ← Or edit
      height: 10.0  # ← Or edit
```

## 🔧 Common Tasks

### Scale entire design by 1.2x

```python
import yaml
with open('constraints.yaml') as f:
    data = yaml.safe_load(f)

for poly in data['polygons']:
    for key in ['x1', 'y1', 'x2', 'y2']:
        poly['position'][key] *= 1.2
    for key in ['width', 'height']:
        poly['size'][key] *= 1.2

with open('scaled.yaml', 'w') as f:
    yaml.dump(data, f)
```

### Make specific layer wider

```python
import yaml
with open('constraints.yaml') as f:
    data = yaml.safe_load(f)

for poly in data['polygons']:
    if poly['layer'] == 'metal1':
        increase = poly['size']['width'] * 0.2
        poly['size']['width'] += increase
        poly['position']['x2'] += increase

with open('wider.yaml', 'w') as f:
    yaml.dump(data, f)
```

### Move all polygons

```python
import yaml
with open('constraints.yaml') as f:
    data = yaml.safe_load(f)

shift_x, shift_y = 100, 50

for poly in data['polygons']:
    poly['position']['x1'] += shift_x
    poly['position']['x2'] += shift_x
    poly['position']['y1'] += shift_y
    poly['position']['y2'] += shift_y

with open('moved.yaml', 'w') as f:
    yaml.dump(data, f)
```

## 📚 Full Documentation

See `GDS_CONSTRAINT_TOOL.md` for complete documentation.

## 💡 Tips

✓ Always backup original GDS
✓ Use YAML for human editing
✓ Use JSON for programmatic processing
✓ Verify results with `gds_to_png`
✓ Track constraint files in version control
