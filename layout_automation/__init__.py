"""
Layout Automation Library
=========================

A constraint-based IC layout automation toolkit supporting:
- Hierarchical cell-based design
- Constraint-based positioning and sizing
- GDS-II file import/export
- SkyWater PDK integration
- DRC (Design Rule Check) and LVS (Layout vs Schematic) verification
"""

from .cell import Cell as ZCell
from .gds_cell import Cell as GDSCell, Polygon, CellInstance
from .units import Unit
from .technology import Technology
from .contact import Contact, ViaStack
from .mosfet import MOSFET
from .integer_optimizer import smart_integer_rounding
from .array_gen import ArrayGenerator

# Import submodules that users can access
from . import drc
from . import lvs
from . import sky130_drc_rules
from . import skywater_layer_map
from . import layout_from_schematic

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "ZCell",
    "GDSCell",
    "Polygon",
    "CellInstance",

    # Units
    "Unit",

    # Technology
    "Technology",

    # Primitives
    "Contact",
    "ViaStack",
    "MOSFET",

    # Utilities
    "smart_integer_rounding",
    "ArrayGenerator",

    # Submodules
    "drc",
    "lvs",
    "sky130_drc_rules",
    "skywater_layer_map",
    "layout_from_schematic",
]
