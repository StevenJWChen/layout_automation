"""
Layout Automation Library
=========================

A constraint-based IC layout automation toolkit supporting:
- Hierarchical cell-based design
- Constraint-based positioning and sizing using OR-Tools
- Constraint keyword expansion for readable layout code
"""

# Import the Cell class
try:
    from .cell import Cell
    HAS_CELL = True
except (ImportError, OSError, Exception) as e:
    Cell = None
    HAS_CELL = False
    import warnings
    warnings.warn(f"Could not import Cell class: {e}")

# Import constraint keyword utilities
try:
    from .constraint_keywords import expand_constraint_keywords
    HAS_CONSTRAINT_KEYWORDS = True
except (ImportError, Exception) as e:
    expand_constraint_keywords = None
    HAS_CONSTRAINT_KEYWORDS = False
    import warnings
    warnings.warn(f"Could not import constraint_keywords: {e}")

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "Cell",

    # Utilities
    "expand_constraint_keywords",

    # Flags
    "HAS_CELL",
    "HAS_CONSTRAINT_KEYWORDS",
]
