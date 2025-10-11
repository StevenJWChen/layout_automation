# Module Structure Guide

This document explains the new modular structure of the Layout Automation toolkit.

## Directory Structure

```
layout_automation/
├── layout_automation/          # Core library (importable package)
│   ├── __init__.py            # Package exports
│   ├── cell.py                # Original Cell class (Z3-based)
│   ├── gds_cell.py            # GDS-style Cell class (scipy-based)
│   ├── units.py               # Unit system (DBU, microns, etc.)
│   ├── technology.py          # Technology definitions (SkyWater, etc.)
│   ├── contact.py             # Contact/via generator
│   ├── mosfet.py              # MOSFET primitive generator
│   ├── integer_optimizer.py  # Smart rounding for integer coordinates
│   ├── array_gen.py           # Array/grid generators
│   ├── drc.py                 # Design Rule Checker
│   ├── drc_improved.py        # Topology-aware DRC
│   ├── lvs.py                 # Layout vs Schematic checker
│   ├── sky130_drc_rules.py    # SkyWater SKY130 DRC rules
│   ├── skywater_layer_map.py  # SkyWater layer mapping
│   └── layout_from_schematic.py  # Auto place-and-route
│
├── tools/                     # Utilities and tools
│   ├── __init__.py
│   ├── gds_to_png.py          # GDS to PNG converter
│   ├── netlist_extractor.py   # Geometric netlist extraction
│   ├── netlist_extractor_improved.py  # Improved extraction
│   ├── skywater_extractor.py  # SkyWater-specific extractor
│   ├── skywater_direct_extractor.py   # Direct GDS extraction
│   └── end_to_end_flow.py     # Complete design flow
│
├── examples/                  # Example designs and demos
│   ├── __init__.py
│   ├── inverter_*.py          # Inverter examples
│   ├── replicate_skywater_*.py  # SkyWater cell replication
│   ├── analyze_*.py           # Analysis scripts
│   ├── debug_*.py             # Debug utilities
│   └── verify_*.py            # Verification scripts
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_*.py              # Unit tests
│   └── test_cases.py          # Test case library
│
├── setup.py                   # Package installation
└── MODULE_GUIDE.md            # This file
```

## Installation

### Development Mode (Recommended)
```bash
# Install in editable mode with development dependencies
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Regular Installation
```bash
pip install .
```

## Usage Examples

### 1. Basic Cell Creation

```python
from layout_automation import GDSCell, Polygon

# Create a cell with polygons
cell = GDSCell('my_cell')
poly1 = Polygon('rect1', 'metal1')
poly2 = Polygon('rect2', 'metal1')
cell.add_polygon([poly1, poly2])

# Add constraints
cell.constrain(poly1, 'sx2+5<ox1', poly2)  # poly2 is 5um right of poly1

# Solve and export
if cell.solver():
    cell.export_gds('output.gds')
```

### 2. Creating a MOSFET

```python
from layout_automation import MOSFET, Technology
from layout_automation.units import um

# Create technology
tech = Technology.create_sky130()

# Create NMOS transistor
nmos = MOSFET(
    name='M1',
    device_type='nfet',
    width=um(0.65),
    length=um(0.15),
    technology=tech
)
nmos_cell = nmos.generate()
nmos_cell.export_gds('nmos.gds')
```

### 3. Using SkyWater PDK

```python
from layout_automation import Technology, MOSFET, Contact
from layout_automation.units import um, nm

# Load SkyWater SKY130 technology
tech = Technology.create_sky130()

# Access layer information
metal1 = tech.layers['metal1']
print(f"Metal1 GDS layer: {metal1.gds_layer}")

# Create contact
contact = Contact(
    layer1='diff',
    layer2='metal1',
    tech=tech
)
```

### 4. Design Rule Checking (DRC)

```python
from layout_automation import DRC, GDSCell
from layout_automation.sky130_drc_rules import create_sky130_drc_rules

# Create layout
cell = GDSCell('my_design')
# ... add polygons ...

# Run DRC
rules = create_sky130_drc_rules()
checker = DRC(rules)
violations = checker.check_cell(cell)

# Report violations
for v in violations:
    print(f"DRC Violation: {v.rule_name} - {v.description}")
```

### 5. Netlist Extraction

```python
from tools import NetlistExtractor
from layout_automation import GDSCell, Technology

# Load layout
cell = GDSCell('inverter')
cell.import_gds('inverter.gds', 'inverter')

# Extract netlist
tech = Technology.create_sky130()
extractor = NetlistExtractor(cell, tech)
netlist = extractor.extract()

# Print devices
for device in netlist.devices:
    print(f"{device.name}: {device.device_type} W={device.width} L={device.length}")
```

### 6. Layout vs Schematic (LVS)

```python
from layout_automation import LVS, Netlist
from tools import NetlistExtractor

# Create schematic netlist
schematic = Netlist('inverter_sch')
schematic.add_device(Device('M1', 'nfet', width=0.65, length=0.15))
schematic.add_device(Device('M2', 'pfet', width=1.3, length=0.15))

# Extract layout netlist
# ... (as shown above) ...

# Run LVS
lvs = LVS()
result = lvs.compare(schematic, layout_netlist)

if result.match:
    print("LVS PASS")
else:
    print(f"LVS FAIL: {result.errors}")
```

### 7. GDS to PNG Conversion

```python
from tools import gds_to_png

# Convert GDS to PNG
gds_to_png('input.gds', 'output.png', cell_name='top_cell')
```

Or from command line:
```bash
gds2png input.gds output.png
```

### 8. Complete End-to-End Flow

```python
from tools import EndToEndFlow
from layout_automation import Netlist, Device

# Define schematic
netlist = Netlist('and3')
netlist.add_device(Device('M1', 'nfet', width=0.65, length=0.15))
# ... add more devices ...

# Run complete flow: Layout → DRC → Extract → LVS
flow = EndToEndFlow(netlist)
result = flow.run()

if result.success:
    print("Design verified successfully!")
    result.layout_cell.export_gds('and3_final.gds')
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
python tests/test_gds_cell.py

# Run with coverage
pytest --cov=layout_automation tests/
```

## Running Examples

```bash
# Run an example
python examples/replicate_skywater_inv.py

# Run verification
python examples/verify_skywater_cells.py
```

## Import Conventions

### Core Library
All core functionality is in the `layout_automation` package:
```python
from layout_automation import (
    Cell,           # Original Z3-based cell
    GDSCell,        # GDS-style cell (recommended)
    Polygon,
    CellInstance,
    MOSFET,
    Contact,
    Technology,
    DRC,
    LVS,
)
```

### Tools
Import tools from the `tools` package:
```python
from tools import (
    gds_to_png,
    NetlistExtractor,
    SkyWaterExtractor,
    EndToEndFlow,
)
```

### Test Utilities
Import test utilities from the `tests` package:
```python
from tests.test_cases import (
    create_inverter_schematic,
    create_nand2_schematic,
)
```

## API Documentation

See individual module docstrings for detailed API documentation:
- `layout_automation/__init__.py` - Main package exports
- Each module has comprehensive docstrings explaining classes and functions

## Migration from Old Structure

If you have old code that imports from the root directory:

**Old:**
```python
from gds_cell import Cell, Polygon
from mosfet import MOSFET
from technology import Technology
```

**New:**
```python
from layout_automation.gds_cell import GDSCell as Cell, Polygon
from layout_automation.mosfet import MOSFET
from layout_automation.technology import Technology
```

## Contributing

When adding new features:
1. Core library code → `layout_automation/`
2. Utility tools → `tools/`
3. Examples → `examples/`
4. Tests → `tests/`

Always update the appropriate `__init__.py` to export public APIs.
