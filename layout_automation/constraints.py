"""
Constraint Helper Functions

This module provides easy-to-use functions for common constraint patterns,
making constraints more readable and reducing errors.

Usage:
    from layout_automation.constraints import center, align_left, spacing, same_width

    parent.constrain(child, center(parent))
    parent.constrain(child2, align_left(child1))
    parent.constrain(child2, spacing(child1, 10))
"""

# ==============================================================================
# CENTER CONSTRAINTS
# ==============================================================================

def center(ref_cell):
    """
    Center child in reference cell (both X and Y)

    Args:
        ref_cell: Reference cell to center relative to

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child, *center(parent))
        # Equivalent to: parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', parent)
    """
    return ('sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', ref_cell)


def center_x(ref_cell):
    """
    Center child horizontally (X-axis only)

    Args:
        ref_cell: Reference cell to center relative to

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child, *center_x(parent))
        # Equivalent to: parent.constrain(child, 'sx1+sx2=ox1+ox2', parent)
    """
    return ('sx1+sx2=ox1+ox2', ref_cell)


def center_y(ref_cell):
    """
    Center child vertically (Y-axis only)

    Args:
        ref_cell: Reference cell to center relative to

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child, *center_y(parent))
        # Equivalent to: parent.constrain(child, 'sy1+sy2=oy1+oy2', parent)
    """
    return ('sy1+sy2=oy1+oy2', ref_cell)


# ==============================================================================
# ALIGNMENT CONSTRAINTS
# ==============================================================================

def align_left(ref_cell):
    """
    Align left edges

    Args:
        ref_cell: Reference cell to align with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *align_left(child1))
        # Equivalent to: parent.constrain(child2, 'sx1=ox1', child1)
    """
    return ('sx1=ox1', ref_cell)


def align_right(ref_cell):
    """
    Align right edges

    Args:
        ref_cell: Reference cell to align with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *align_right(child1))
        # Equivalent to: parent.constrain(child2, 'sx2=ox2', child1)
    """
    return ('sx2=ox2', ref_cell)


def align_top(ref_cell):
    """
    Align top edges

    Args:
        ref_cell: Reference cell to align with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *align_top(child1))
        # Equivalent to: parent.constrain(child2, 'sy2=oy2', child1)
    """
    return ('sy2=oy2', ref_cell)


def align_bottom(ref_cell):
    """
    Align bottom edges

    Args:
        ref_cell: Reference cell to align with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *align_bottom(child1))
        # Equivalent to: parent.constrain(child2, 'sy1=oy1', child1)
    """
    return ('sy1=oy1', ref_cell)


def align_center_x(ref_cell):
    """
    Align horizontal centers (X-axis)

    Args:
        ref_cell: Reference cell to align with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *align_center_x(child1))
        # Equivalent to: parent.constrain(child2, 'sx1+sx2=ox1+ox2', child1)
    """
    return ('sx1+sx2=ox1+ox2', ref_cell)


def align_center_y(ref_cell):
    """
    Align vertical centers (Y-axis)

    Args:
        ref_cell: Reference cell to align with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *align_center_y(child1))
        # Equivalent to: parent.constrain(child2, 'sy1+sy2=oy1+oy2', child1)
    """
    return ('sy1+sy2=oy1+oy2', ref_cell)


# ==============================================================================
# SPACING CONSTRAINTS
# ==============================================================================

def spacing(ref_cell, distance, direction='right'):
    """
    Place cell at specified distance from reference cell

    Args:
        ref_cell: Reference cell to space from
        distance: Distance between cells
        direction: 'right', 'left', 'above', 'below'

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *spacing(child1, 10, 'right'))
        # Places child2 10 units to the right of child1
    """
    directions = {
        'right': f'sx1=ox2+{distance}',
        'left': f'sx2=ox1-{distance}',
        'above': f'sy1=oy2+{distance}',
        'below': f'sy2=oy1-{distance}',
    }

    if direction not in directions:
        raise ValueError(f"Direction must be one of: {list(directions.keys())}")

    return (directions[direction], ref_cell)


def spacing_h(ref_cell, distance):
    """
    Horizontal spacing (place to the right)

    Args:
        ref_cell: Reference cell to space from
        distance: Distance between cells

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *spacing_h(child1, 10))
        # Equivalent to: parent.constrain(child2, 'sx1=ox2+10', child1)
    """
    return (f'sx1=ox2+{distance}', ref_cell)


def spacing_v(ref_cell, distance):
    """
    Vertical spacing (place above)

    Args:
        ref_cell: Reference cell to space from
        distance: Distance between cells

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *spacing_v(child1, 10))
        # Equivalent to: parent.constrain(child2, 'sy1=oy2+10', child1)
    """
    return (f'sy1=oy2+{distance}', ref_cell)


# ==============================================================================
# SIZE CONSTRAINTS
# ==============================================================================

def same_width(ref_cell):
    """
    Match width of reference cell

    Args:
        ref_cell: Reference cell to match width with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *same_width(child1))
        # Equivalent to: parent.constrain(child2, 'sx2-sx1=ox2-ox1', child1)
    """
    return ('sx2-sx1=ox2-ox1', ref_cell)


def same_height(ref_cell):
    """
    Match height of reference cell

    Args:
        ref_cell: Reference cell to match height with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *same_height(child1))
        # Equivalent to: parent.constrain(child2, 'sy2-sy1=oy2-oy1', child1)
    """
    return ('sy2-sy1=oy2-oy1', ref_cell)


def same_size(ref_cell):
    """
    Match both width and height of reference cell

    Args:
        ref_cell: Reference cell to match size with

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *same_size(child1))
        # Equivalent to: parent.constrain(child2, 'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', child1)
    """
    return ('sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', ref_cell)


def width(w):
    """
    Set fixed width

    Args:
        w: Width value

    Returns:
        str: Constraint string for self-constraint

    Example:
        cell.constrain(*width(100))
        # Equivalent to: cell.constrain('x2-x1=100')
    """
    return f'x2-x1={w}'


def height(h):
    """
    Set fixed height

    Args:
        h: Height value

    Returns:
        str: Constraint string for self-constraint

    Example:
        cell.constrain(*height(50))
        # Equivalent to: cell.constrain('y2-y1=50')
    """
    return f'y2-y1={h}'


def size(w, h):
    """
    Set fixed width and height

    Args:
        w: Width value
        h: Height value

    Returns:
        str: Constraint string for self-constraint

    Example:
        cell.constrain(*size(100, 50))
        # Equivalent to: cell.constrain('x2-x1=100, y2-y1=50')
    """
    return f'x2-x1={w}, y2-y1={h}'


# ==============================================================================
# POSITION CONSTRAINTS
# ==============================================================================

def at(x, y, w=None, h=None):
    """
    Position cell at absolute coordinates

    Args:
        x: X coordinate (x1)
        y: Y coordinate (y1)
        w: Optional width (if None, only position is set)
        h: Optional height (if None, only position is set)

    Returns:
        str: Constraint string

    Example:
        parent.constrain(child, *at(10, 20, 50, 30))
        # Equivalent to: parent.constrain(child, 'x1=10, y1=20, x2=60, y2=50')

        parent.constrain(child, *at(10, 20))
        # Equivalent to: parent.constrain(child, 'x1=10, y1=20')
    """
    if w is not None and h is not None:
        return f'x1={x}, y1={y}, x2={x+w}, y2={y+h}'
    else:
        return f'x1={x}, y1={y}'


def bbox(x1, y1, x2, y2):
    """
    Set bounding box explicitly

    Args:
        x1, y1, x2, y2: Bounding box coordinates

    Returns:
        str: Constraint string

    Example:
        parent.constrain(child, *bbox(0, 0, 100, 50))
        # Equivalent to: parent.constrain(child, 'x1=0, y1=0, x2=100, y2=50')
    """
    return f'x1={x1}, y1={y1}, x2={x2}, y2={y2}'


# ==============================================================================
# COMPOUND CONSTRAINTS (COMBINE MULTIPLE)
# ==============================================================================

def beside(ref_cell, spacing_val=0, align='bottom'):
    """
    Place cell beside (to the right of) reference cell with alignment

    Args:
        ref_cell: Reference cell to place beside
        spacing_val: Spacing between cells (default 0)
        align: 'top', 'bottom', or 'center' (default 'bottom')

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *beside(child1, 10, 'center'))
        # Places child2 to the right of child1 with 10 units spacing, centered vertically
    """
    constraints = [f'sx1=ox2+{spacing_val}']

    if align == 'bottom':
        constraints.append('sy1=oy1')
    elif align == 'top':
        constraints.append('sy2=oy2')
    elif align == 'center':
        constraints.append('sy1+sy2=oy1+oy2')
    else:
        raise ValueError("align must be 'top', 'bottom', or 'center'")

    return (', '.join(constraints), ref_cell)


def above(ref_cell, spacing_val=0, align='left'):
    """
    Place cell above reference cell with alignment

    Args:
        ref_cell: Reference cell to place above
        spacing_val: Spacing between cells (default 0)
        align: 'left', 'right', or 'center' (default 'left')

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *above(child1, 10, 'center'))
        # Places child2 above child1 with 10 units spacing, centered horizontally
    """
    constraints = [f'sy1=oy2+{spacing_val}']

    if align == 'left':
        constraints.append('sx1=ox1')
    elif align == 'right':
        constraints.append('sx2=ox2')
    elif align == 'center':
        constraints.append('sx1+sx2=ox1+ox2')
    else:
        raise ValueError("align must be 'left', 'right', or 'center'")

    return (', '.join(constraints), ref_cell)


def below(ref_cell, spacing_val=0, align='left'):
    """
    Place cell below reference cell with alignment

    Args:
        ref_cell: Reference cell to place below
        spacing_val: Spacing between cells (default 0)
        align: 'left', 'right', or 'center' (default 'left')

    Returns:
        tuple: (constraint_string, ref_cell)

    Example:
        parent.constrain(child2, *below(child1, 10, 'center'))
        # Places child2 below child1 with 10 units spacing, centered horizontally
    """
    constraints = [f'sy2=oy1-{spacing_val}']

    if align == 'left':
        constraints.append('sx1=ox1')
    elif align == 'right':
        constraints.append('sx2=ox2')
    elif align == 'center':
        constraints.append('sx1+sx2=ox1+ox2')
    else:
        raise ValueError("align must be 'left', 'right', or 'center'")

    return (', '.join(constraints), ref_cell)


# ==============================================================================
# CONSTRAINT REFERENCE TABLE
# ==============================================================================

CONSTRAINT_REFERENCE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     CONSTRAINT HELPER REFERENCE TABLE                      ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ CENTER CONSTRAINTS                                                          │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ center(ref)              │ Center in both X and Y                          │
│ center_x(ref)            │ Center horizontally (X only)                    │
│ center_y(ref)            │ Center vertically (Y only)                      │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ALIGNMENT CONSTRAINTS                                                       │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ align_left(ref)          │ Align left edges: sx1=ox1                       │
│ align_right(ref)         │ Align right edges: sx2=ox2                      │
│ align_top(ref)           │ Align top edges: sy2=oy2                        │
│ align_bottom(ref)        │ Align bottom edges: sy1=oy1                     │
│ align_center_x(ref)      │ Align horizontal centers: sx1+sx2=ox1+ox2       │
│ align_center_y(ref)      │ Align vertical centers: sy1+sy2=oy1+oy2         │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SPACING CONSTRAINTS                                                         │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ spacing(ref, d, 'right') │ Place d units to the right: sx1=ox2+d          │
│ spacing(ref, d, 'left')  │ Place d units to the left: sx2=ox1-d           │
│ spacing(ref, d, 'above') │ Place d units above: sy1=oy2+d                  │
│ spacing(ref, d, 'below') │ Place d units below: sy2=oy1-d                  │
│ spacing_h(ref, d)        │ Horizontal spacing: sx1=ox2+d                   │
│ spacing_v(ref, d)        │ Vertical spacing: sy1=oy2+d                     │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SIZE CONSTRAINTS                                                            │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ same_width(ref)          │ Match width: sx2-sx1=ox2-ox1                    │
│ same_height(ref)         │ Match height: sy2-sy1=oy2-oy1                   │
│ same_size(ref)           │ Match both width and height                     │
│ width(w)                 │ Set fixed width: x2-x1=w                        │
│ height(h)                │ Set fixed height: y2-y1=h                       │
│ size(w, h)               │ Set fixed size: x2-x1=w, y2-y1=h                │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ POSITION CONSTRAINTS                                                        │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ at(x, y)                 │ Position at (x,y): x1=x, y1=y                   │
│ at(x, y, w, h)           │ Position and size: x1=x, y1=y, x2=x+w, y2=y+h  │
│ bbox(x1, y1, x2, y2)     │ Set bounding box explicitly                     │
└──────────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ COMPOUND CONSTRAINTS (combine spacing + alignment)                         │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ beside(ref, d, 'center') │ Place to right with spacing, centered           │
│ above(ref, d, 'center')  │ Place above with spacing, centered              │
│ below(ref, d, 'center')  │ Place below with spacing, centered              │
└──────────────────────────┴──────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════╗
║                           USAGE EXAMPLES                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

Example 1: Center a child in parent
    parent.constrain(child, *center(parent))

Example 2: Place child2 to the right of child1 with 10 unit spacing
    parent.constrain(child2, *spacing_h(child1, 10))

Example 3: Align left edges and match height
    parent.constrain(child2, *align_left(child1))
    parent.constrain(child2, *same_height(child1))

Example 4: Position at (10, 20) with size 100×50
    parent.constrain(child, at(10, 20, 100, 50))

Example 5: Place child2 beside child1 with vertical centering
    parent.constrain(child2, *beside(child1, spacing_val=10, align='center'))

Example 6: Set fixed width
    cell.constrain(width(100))

╔════════════════════════════════════════════════════════════════════════════╗
║                      RAW CONSTRAINT REFERENCE                              ║
╚════════════════════════════════════════════════════════════════════════════╝

Center X:        sx1+sx2=ox1+ox2        (child center X = ref center X)
Center Y:        sy1+sy2=oy1+oy2        (child center Y = ref center Y)
Width:           sx2-sx1=W              (child width = W)
Height:          sy2-sy1=H              (child height = H)
Same width:      sx2-sx1=ox2-ox1        (child width = ref width)
Same height:     sy2-sy1=oy2-oy1        (child height = ref height)
Right of:        sx1=ox2+D              (child left = ref right + D)
Above:           sy1=oy2+D              (child bottom = ref top + D)
Align left:      sx1=ox1                (child left = ref left)
Align bottom:    sy1=oy1                (child bottom = ref bottom)
"""


def print_reference():
    """Print the constraint reference table"""
    print(CONSTRAINT_REFERENCE)


# ==============================================================================
# CONVENIENCE: Import all helpers
# ==============================================================================

__all__ = [
    # Center
    'center', 'center_x', 'center_y',
    # Align
    'align_left', 'align_right', 'align_top', 'align_bottom',
    'align_center_x', 'align_center_y',
    # Spacing
    'spacing', 'spacing_h', 'spacing_v',
    # Size
    'same_width', 'same_height', 'same_size',
    'width', 'height', 'size',
    # Position
    'at', 'bbox',
    # Compound
    'beside', 'above', 'below',
    # Reference
    'print_reference', 'CONSTRAINT_REFERENCE',
]
