#!/usr/bin/env python3
"""
Constraint Helper Functions

Provides convenient functions for common constraint patterns,
including proper centering (without left/bottom bias).
"""

def constrain_xcenter(parent, child, ref_obj):
    """
    Center child's X coordinate relative to ref_obj (exact centering)

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)

    Example:
        parent = Cell('parent')
        child = Cell('child', 'metal1')
        parent.constrain('width=100, height=100')
        parent.constrain(child, 'swidth=30, sheight=40')
        constrain_xcenter(parent, child, parent)
    """
    parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)


def constrain_ycenter(parent, child, ref_obj):
    """
    Center child's Y coordinate relative to ref_obj (exact centering)

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)

    Example:
        parent = Cell('parent')
        child = Cell('child', 'metal1')
        parent.constrain('width=100, height=100')
        parent.constrain(child, 'swidth=30, sheight=40')
        constrain_ycenter(parent, child, parent)
    """
    parent.constrain(child, 'sy1+sy2=oy1+oy2', ref_obj)


def constrain_center(parent, child, ref_obj):
    """
    Center child both X and Y relative to ref_obj (exact centering)

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)

    Example:
        parent = Cell('parent')
        child = Cell('child', 'metal1')
        parent.constrain('width=100, height=100')
        parent.constrain(child, 'swidth=30, sheight=40')
        constrain_center(parent, child, parent)

    Note: This is equivalent to:
        parent.constrain(child, 'center', parent)
    """
    parent.constrain(child, 'sx1+sx2=ox1+ox2, sy1+sy2=oy1+oy2', ref_obj)


def constrain_align_left(parent, child, ref_obj):
    """
    Align child's left edge with ref_obj's left edge

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)

    Example:
        parent.constrain(child, 'left', ref_obj)
    """
    parent.constrain(child, 'sx1=ox1', ref_obj)


def constrain_align_right(parent, child, ref_obj):
    """
    Align child's right edge with ref_obj's right edge

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
    """
    parent.constrain(child, 'sx2=ox2', ref_obj)


def constrain_align_bottom(parent, child, ref_obj):
    """
    Align child's bottom edge with ref_obj's bottom edge

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
    """
    parent.constrain(child, 'sy1=oy1', ref_obj)


def constrain_align_top(parent, child, ref_obj):
    """
    Align child's top edge with ref_obj's top edge

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
    """
    parent.constrain(child, 'sy2=oy2', ref_obj)


def constrain_match_width(parent, child, ref_obj):
    """
    Make child's width match ref_obj's width

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
    """
    parent.constrain(child, 'sx2-sx1=ox2-ox1', ref_obj)


def constrain_match_height(parent, child, ref_obj):
    """
    Make child's height match ref_obj's height

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
    """
    parent.constrain(child, 'sy2-sy1=oy2-oy1', ref_obj)


def constrain_match_size(parent, child, ref_obj):
    """
    Make child's size match ref_obj's size (both width and height)

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object (usually parent or another child)
    """
    parent.constrain(child, 'sx2-sx1=ox2-ox1, sy2-sy1=oy2-oy1', ref_obj)


def constrain_spacing_x(parent, child1, child2, spacing):
    """
    Position child2 to the right of child1 with specified spacing

    Args:
        parent: Parent cell containing the constraint
        child1: Left child
        child2: Right child (positioned relative to child1)
        spacing: Horizontal spacing between children

    Example:
        # Place child2 10 units to the right of child1
        constrain_spacing_x(parent, child1, child2, spacing=10)
    """
    parent.constrain(child2, f'sx1=ox2+{spacing}', child1)


def constrain_spacing_y(parent, child1, child2, spacing):
    """
    Position child2 above child1 with specified spacing

    Args:
        parent: Parent cell containing the constraint
        child1: Bottom child
        child2: Top child (positioned relative to child1)
        spacing: Vertical spacing between children

    Example:
        # Place child2 5 units above child1
        constrain_spacing_y(parent, child1, child2, spacing=5)
    """
    parent.constrain(child2, f'sy1=oy2+{spacing}', child1)


# Advanced: Tolerance functions (use with caution - see XCENTER_TOLERANCE_SOLUTION.md)

def constrain_xcenter_with_tolerance_AVOID(parent, child, ref_obj, tolerance):
    """
    AVOID: This causes left/bottom bias!

    Use constrain_xcenter() instead for true centering.

    This function is provided for educational purposes only.
    It demonstrates why tolerance constraints don't work for centering.

    Due to the solver's objective function (minimizing coordinates),
    this will always place the child at the LEFT edge of the tolerance range.

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object
        tolerance: Tolerance in layout units (±T)

    See: XCENTER_TOLERANCE_SOLUTION.md for explanation
    """
    tolerance_sum = tolerance * 2
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)
    print("WARNING: constrain_xcenter_with_tolerance_AVOID will cause left bias!")
    print("         Use constrain_xcenter() instead for exact centering.")


def constrain_xcenter_exact_with_fallback(parent, child, ref_obj, tolerance):
    """
    Center exactly, with tolerance as fallback (if exact is impossible)

    This adds both exact equality AND tolerance inequalities.
    OR-Tools will satisfy the equality if possible.

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object
        tolerance: Fallback tolerance (only used if exact centering conflicts)

    Example:
        # Try to center exactly, but allow ±5 units if needed
        constrain_xcenter_exact_with_fallback(parent, child, parent, tolerance=5)

    Note: In most cases, just use constrain_xcenter() instead.
    """
    tolerance_sum = tolerance * 2

    # Primary: exact centering (OR-Tools will try this first)
    parent.constrain(child, 'sx1+sx2=ox1+ox2', ref_obj)

    # Fallback: tolerance range (only if exact is impossible)
    parent.constrain(child, f'sx1+sx2>=ox1+ox2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sx1+sx2<=ox1+ox2+{tolerance_sum}', ref_obj)


def constrain_ycenter_exact_with_fallback(parent, child, ref_obj, tolerance):
    """
    Center exactly in Y, with tolerance as fallback

    Args:
        parent: Parent cell containing the constraint
        child: Child cell to constrain
        ref_obj: Reference object
        tolerance: Fallback tolerance (only used if exact centering conflicts)
    """
    tolerance_sum = tolerance * 2

    # Primary: exact centering
    parent.constrain(child, 'sy1+sy2=oy1+oy2', ref_obj)

    # Fallback: tolerance range
    parent.constrain(child, f'sy1+sy2>=oy1+oy2-{tolerance_sum}', ref_obj)
    parent.constrain(child, f'sy1+sy2<=oy1+oy2+{tolerance_sum}', ref_obj)


# Export all helper functions
__all__ = [
    'constrain_xcenter',
    'constrain_ycenter',
    'constrain_center',
    'constrain_align_left',
    'constrain_align_right',
    'constrain_align_bottom',
    'constrain_align_top',
    'constrain_match_width',
    'constrain_match_height',
    'constrain_match_size',
    'constrain_spacing_x',
    'constrain_spacing_y',
    'constrain_xcenter_with_tolerance_AVOID',
    'constrain_xcenter_exact_with_fallback',
    'constrain_ycenter_exact_with_fallback',
]
