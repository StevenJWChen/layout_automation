# Contact Array + Well Ring + MOS Transistor Example

## Overview

This example demonstrates a complete hierarchical IC layout workflow using the **solve-then-freeze** pattern:

1. **Contact Array**: Create a 3x3 array of contact squares
2. **Freeze**: Lock the contact array as a fixed layout block
3. **MOS Transistor**: Build NMOS with frozen contact arrays
4. **Well Ring**: Create a well ring structure
5. **Complete Device**: Assemble NMOS + well ring
6. **Device Array**: Create 2x2 array of complete frozen devices

## Key Concept: Solve → Freeze → Reuse

The workflow demonstrates hierarchical design:
```
Contact Array → FREEZE → Use in MOS
       ↓
    MOS + Contacts → FREEZE → Use in Device
       ↓
  Complete Device → FREEZE → Use in Array
```

## Files

### `contact_array_mos_simple.py`

**Recommended** - Working example with manual positioning:
- Creates contact array, MOS transistor, well ring
- Uses manual positioning (positions set directly)
- Demonstrates freeze_layout() at each hierarchy level
- Exports GDS and PNG visualizations
- **Status**: ✅ Fully functional

**Run**:
```bash
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate layout_py312
python examples/contact_array_mos_simple.py
```

### `contact_array_mos_demo.py`

Advanced example using constraint solver:
- Uses constraint-based positioning
- More flexible but requires working solver
- **Status**: ⚠️ SciPy solver has issues with complex constraints

## What Gets Created

### Hierarchy Structure

```
Level 1: Contact Array (3x3)
         └─ 9 contact squares (2x2 each, 3 spacing)
         └─ FROZEN at 12x12

Level 2: NMOS Transistor
         ├─ Diffusion layer (active area)
         ├─ Poly gate (crosses diffusion)
         ├─ Metal source (with frozen contact array)
         └─ Metal drain (with frozen contact array)
         └─ FROZEN at 34x24

Level 3: Complete Device
         ├─ Well ring (50x40 outer, 40x30 inner opening)
         └─ NMOS transistor (centered in well)
         └─ FROZEN at 50x40

Level 4: Device Array
         └─ 2x2 grid of frozen complete devices (110x90 total)
```

### Output Files

Generated in `demo_outputs/`:

**GDS Files** (industry-standard layout format):
- `contact_array_simple.gds` - Contact array only
- `nmos_with_contacts.gds` - NMOS with frozen contacts
- `well_ring.gds` - Well ring structure
- `complete_device.gds` - NMOS + well ring
- `device_array.gds` - 2x2 array of devices

**PNG Files** (visualizations):
- `contact_array_simple.png`
- `nmos_with_contacts.png`
- `well_ring.png`
- `complete_device.png`
- `device_array.png`

## Key Features Demonstrated

### 1. Contact Array

```python
# Create 3x3 contact array
contact_array = create_contact_array_manual('contact_array_3x3',
                                             rows=3, cols=3,
                                             contact_size=2,
                                             spacing=3)
# Positions set manually
# Result: 12x12 array
```

### 2. Freeze Layout

```python
# Freeze locks all positions
contact_array.freeze_layout()

# Check status
assert contact_array.is_frozen() == True

# Now can be reused without re-solving
```

### 3. Reuse Frozen Blocks

```python
# Create instances of frozen block
source_contacts = CellInstance('source_contacts', contact_array)
drain_contacts = CellInstance('drain_contacts', contact_array)

# Position instances
source_contacts.pos_list = [7, 16, 19, 28]
drain_contacts.pos_list = [27, 16, 39, 28]

# Both instances use same frozen contact pattern
```

### 4. Hierarchical Assembly

```python
# Freeze each level before using in next level
contact_array.freeze_layout()  # Level 1
nmos.freeze_layout()           # Level 2
complete_device.freeze_layout() # Level 3

# Create array of frozen devices (Level 4)
for i in range(4):
    inst = CellInstance(f'device_{i}', complete_device)
    device_array.add_instance(inst)
```

## Benefits of This Workflow

### ✅ Modularity
- Build complex designs from simple frozen blocks
- Each level is independent and reusable

### ✅ Performance
- Frozen blocks don't need re-solving
- Large arrays solve quickly

### ✅ Consistency
- Same contact pattern used everywhere
- No variation between instances

### ✅ IP Protection
- Internal structure is locked
- Can share frozen blocks without revealing internals

### ✅ Hierarchy
- Multiple levels of abstraction
- Bottom-up design methodology

## Design Details

### Contact Array
- **Size**: 3x3 grid (9 contacts)
- **Contact size**: 2x2 units
- **Spacing**: 3 units between contacts
- **Total dimensions**: 12x12 units
- **Layer**: contact

### NMOS Transistor
- **Diffusion**: 30x20 units (active area)
- **Poly gate**: 10x24 units (crosses diffusion)
- **Metal source**: 8x10 units (left side)
- **Metal drain**: 8x10 units (right side)
- **Contact arrays**: 12x12 (frozen, positioned over metal)
- **Total dimensions**: 34x24 units
- **Layers**: diff, poly, metal1, contact

### Well Ring
- **Outer dimensions**: 50x40 units
- **Inner opening**: 40x30 units
- **Ring width**: 5 units
- **Layer**: nwell
- **Purpose**: Isolation and biasing

### Complete Device
- **Well ring**: 50x40 (frozen)
- **NMOS**: Centered in well opening
- **Total dimensions**: 50x40 units

### Device Array
- **Grid**: 2x2 (4 devices)
- **Spacing**: 10 units between devices
- **Total dimensions**: 110x90 units

## Usage Patterns

### Pattern 1: Create Standard Building Block

```python
# 1. Create basic structure
block = create_contact_array_manual(...)

# 2. Set positions (manual or solved)
# (positions already set in this example)

# 3. Freeze for reuse
block.freeze_layout()

# 4. Export if needed
block.export_gds('standard_block.gds')
```

### Pattern 2: Build Higher-Level Structure

```python
# 1. Create instances of frozen blocks
inst1 = CellInstance('inst1', frozen_block)
inst2 = CellInstance('inst2', frozen_block)

# 2. Add to parent
parent.add_instance([inst1, inst2])

# 3. Position instances
inst1.pos_list = [x1, y1, x2, y2]
inst2.pos_list = [x3, y3, x4, y4]

# 4. Freeze parent for next level
parent.freeze_layout()
```

### Pattern 3: Create Arrays

```python
# 1. Freeze single device
device.freeze_layout()

# 2. Create multiple instances
for i in range(n):
    inst = CellInstance(f'dev{i}', device)
    array.add_instance(inst)
    # Position in grid
    inst.pos_list = calculate_grid_position(i)
```

## Customization

### Change Contact Array Size

```python
# 5x5 array instead of 3x3
contact_array = create_contact_array_manual('contact_array_5x5',
                                             rows=5, cols=5,
                                             contact_size=2,
                                             spacing=3)
# Result: 22x22 array
```

### Change Contact Size/Spacing

```python
# Larger contacts, wider spacing
contact_array = create_contact_array_manual('large_contacts',
                                             rows=3, cols=3,
                                             contact_size=4,   # 4x4 instead of 2x2
                                             spacing=6)         # 6 instead of 3
# Result: 24x24 array
```

### Adjust Well Ring

```python
# Larger well, thicker ring
well_ring = create_well_ring_manual(inner_width=60,
                                     inner_height=50,
                                     ring_width=8)
# Result: 76x66 outer dimensions
```

### Create Larger Array

```python
# 5x5 device array
for i in range(5):
    for j in range(5):
        inst = CellInstance(f'dev_r{i}_c{j}', complete_device)
        x = j * (device_width + spacing)
        y = i * (device_height + spacing)
        inst.pos_list = [x, y, x + device_width, y + device_height]
        device_array.add_instance(inst)
```

## Verification

### Check Frozen Status

```python
print(f"Contact array frozen: {contact_array.is_frozen()}")
print(f"NMOS frozen: {nmos.is_frozen()}")
print(f"Complete device frozen: {complete_device.is_frozen()}")
```

### Check Bounding Boxes

```python
print(f"Contact array bbox: {contact_array.get_bbox()}")
print(f"NMOS bbox: {nmos.get_bbox()}")
print(f"Complete device bbox: {complete_device.get_bbox()}")
print(f"Array bbox: {device_array.get_bbox()}")
```

### Verify Hierarchy

```python
print(f"NMOS has {len(nmos.instances)} instances")  # 2 (source + drain contacts)
print(f"Complete device has {len(complete_device.instances)} instances")  # 2 (well + nmos)
print(f"Array has {len(device_array.instances)} instances")  # 4 (2x2 grid)
```

## Integration with Existing Tools

### GDS Export for Tape-Out

All cells can be exported to industry-standard GDS format:
```python
device_array.export_gds('my_design.gds')
```

This GDS file can be used with:
- Cadence Virtuoso
- Mentor Graphics Calibre (DRC/LVS)
- Synopsys IC Compiler
- KLayout (viewer)
- Magic (open-source tool)

### Visualization

All cells can be visualized:
```python
fig = cell.draw(solve_first=False, show=True)
# Or save to file
plt.savefig('layout.png', dpi=150, bbox_inches='tight')
```

## Troubleshooting

### Issue: Frozen block won't freeze

**Symptom**: `ValueError: Cannot freeze layout: polygon has unsolved positions`

**Solution**: Ensure all positions are set before freezing:
```python
# Check positions
for poly in cell.polygons:
    if None in poly.pos_list:
        print(f"Polygon {poly.name} has None positions")

# Set positions manually if needed
poly.pos_list = [x1, y1, x2, y2]
```

### Issue: Instances not visible

**Symptom**: Instances don't appear in drawing or GDS

**Solution**: Ensure instance positions are set:
```python
# Must set instance bounding box
inst.pos_list = [x1, y1, x2, y2]
```

### Issue: Hierarchy not preserved in GDS

**Symptom**: GDS export flattens everything

**Solution**: Use gds_cell.Cell which preserves hierarchy:
```python
from layout_automation.gds_cell import Cell, Polygon, CellInstance
# Hierarchy is preserved in GDS export
```

## Related Examples

- `frozen_layout_demo.py` - Basic frozen layout feature
- `gds_import_export_demo.py` - GDS import/export
- `self_constrain_auto_add_demo.py` - Self-constraints and auto-add

## Documentation

- `FROZEN_LAYOUT_FEATURE.md` - Frozen layout documentation
- `GDS_IMPORT_EXPORT.md` - GDS format documentation
- `SELF_CONSTRAIN_AUTO_ADD_FEATURES.md` - New features

## Contact

For questions or issues:
- GitHub: https://github.com/StevenJWChen/layout_automation

---

**Author**: Layout Automation Team
**Date**: October 14, 2025
**Status**: ✅ Fully Functional
