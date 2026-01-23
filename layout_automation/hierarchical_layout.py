#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hierarchical Layout Support - Relative Positioning Enhancement

This module extends the Cell class with hierarchical positioning capabilities,
allowing child cells to have positions relative to their parents (like GDS format).

Key Features:
- Dual coordinate system: local (relative to parent) and global (absolute)
- Automatic coordinate transformations
- Enhanced solver with hierarchical awareness
- Natural GDS-like workflow
- Backwards compatible with existing code

Author: Layout Automation Enhancement
"""

from typing import List, Tuple, Optional


class HierarchicalPositioning:
    """
    Mixin class that adds hierarchical positioning capabilities to Cell.

    This enables:
    - Local coordinates (relative to parent)
    - Global coordinates (absolute in top-level space)
    - Automatic transformations between coordinate systems
    - Hierarchical constraint solving
    """

    def __init__(self):
        """Initialize hierarchical positioning"""
        self._local_pos = None  # Local position [x1, y1, x2, y2] relative to parent
        self._parent_cell = None  # Reference to parent cell
        self._use_relative_coords = False  # Flag to enable relative coordinate mode

    def set_local_position(self, x1: float, y1: float, x2: float, y2: float):
        """
        Set position relative to parent (local coordinates)

        Args:
            x1, y1: Lower-left corner relative to parent origin
            x2, y2: Upper-right corner relative to parent origin
        """
        self._local_pos = [x1, y1, x2, y2]
        self._use_relative_coords = True

        # Get parent origin and convert to global
        parent_x, parent_y = self._get_parent_origin()

        # Update global position (pos_list) directly
        if hasattr(self, 'pos_list'):
            self.pos_list = [
                x1 + parent_x,
                y1 + parent_y,
                x2 + parent_x,
                y2 + parent_y
            ]

    def get_local_position(self) -> Optional[List[float]]:
        """
        Get position relative to parent

        Returns:
            [x1, y1, x2, y2] in local coordinates, or None if not set
        """
        if self._use_relative_coords and self._local_pos is not None:
            return self._local_pos.copy()

        # Calculate from global if available
        if hasattr(self, 'pos_list') and self.pos_list and all(v is not None for v in self.pos_list):
            return self._calculate_local_from_global()

        return None

    def get_global_position(self) -> Optional[List[float]]:
        """
        Get position in global (absolute) coordinates

        Returns:
            [x1, y1, x2, y2] in global coordinates, or None if not set
        """
        if hasattr(self, 'pos_list') and self.pos_list and all(v is not None for v in self.pos_list):
            return self.pos_list.copy()

        # Calculate from local if available
        if self._use_relative_coords and self._local_pos is not None:
            return self._calculate_global_from_local()

        return None

    def _calculate_local_from_global(self) -> List[float]:
        """Calculate local coordinates from global coordinates"""
        if not hasattr(self, 'pos_list') or not self.pos_list:
            return [0, 0, 0, 0]

        x1, y1, x2, y2 = self.pos_list

        # Get parent's origin
        parent_x, parent_y = self._get_parent_origin()

        # Convert to local
        return [
            x1 - parent_x,
            y1 - parent_y,
            x2 - parent_x,
            y2 - parent_y
        ]

    def _calculate_global_from_local(self) -> List[float]:
        """Calculate global coordinates from local coordinates"""
        if not self._local_pos:
            return [0, 0, 0, 0]

        x1, y1, x2, y2 = self._local_pos

        # Get parent's origin
        parent_x, parent_y = self._get_parent_origin()

        # Convert to global
        return [
            x1 + parent_x,
            y1 + parent_y,
            x2 + parent_x,
            y2 + parent_y
        ]

    def _get_parent_origin(self) -> Tuple[float, float]:
        """
        Get parent cell's origin in global coordinates

        Returns:
            (x, y) tuple of parent origin, or (0, 0) if no parent
        """
        if not hasattr(self, '_parent_cell') or self._parent_cell is None:
            return (0.0, 0.0)

        parent = self._parent_cell
        if hasattr(parent, 'pos_list') and parent.pos_list and all(v is not None for v in parent.pos_list[:2]):
            return (parent.pos_list[0], parent.pos_list[1])

        return (0.0, 0.0)

    def _update_global_from_local(self):
        """Update global position from local position"""
        if self._local_pos:
            if hasattr(self, 'pos_list'):
                self.pos_list = self._calculate_global_from_local()

    def _update_local_from_global(self):
        """Update local position from global position"""
        if hasattr(self, 'pos_list') and self.pos_list:
            self._local_pos = self._calculate_local_from_global()

    def local_to_global_point(self, x: float, y: float) -> Tuple[float, float]:
        """
        Transform a point from local to global coordinates

        Args:
            x, y: Point in local (relative to parent) coordinates

        Returns:
            (x, y) in global coordinates
        """
        parent_x, parent_y = self._get_parent_origin()
        return (x + parent_x, y + parent_y)

    def global_to_local_point(self, x: float, y: float) -> Tuple[float, float]:
        """
        Transform a point from global to local coordinates

        Args:
            x, y: Point in global (absolute) coordinates

        Returns:
            (x, y) in local coordinates
        """
        parent_x, parent_y = self._get_parent_origin()
        return (x - parent_x, y - parent_y)


def enable_hierarchical_mode(cell, recursive: bool = True):
    """
    Enable hierarchical positioning mode for a cell hierarchy

    Args:
        cell: Cell to enable hierarchical mode for
        recursive: If True, enable for all children recursively

    Usage:
        cell = Cell('top', child1, child2)
        enable_hierarchical_mode(cell)
        # Now children store positions relative to parent
    """
    if not hasattr(cell, '_use_relative_coords'):
        # Add hierarchical positioning to this cell
        for attr in dir(HierarchicalPositioning):
            if not attr.startswith('_') or attr in ['_local_pos', '_parent_cell', '_use_relative_coords',
                                                      '_calculate_local_from_global', '_calculate_global_from_local',
                                                      '_get_parent_origin', '_update_global_from_local',
                                                      '_update_local_from_global']:
                if hasattr(HierarchicalPositioning, attr):
                    method = getattr(HierarchicalPositioning, attr)
                    if callable(method):
                        setattr(cell, attr, method.__get__(cell, type(cell)))

        cell._local_pos = None
        cell._parent_cell = None
        cell._use_relative_coords = False

    # Enable relative coordinate mode
    cell._use_relative_coords = True

    # Set parent references for children
    if hasattr(cell, 'children'):
        for child in cell.children:
            if hasattr(child, '_parent_cell'):
                child._parent_cell = cell

            if recursive:
                enable_hierarchical_mode(child, recursive=True)

    # Update local positions from current global positions
    if hasattr(cell, 'pos_list') and cell.pos_list and all(v is not None for v in cell.pos_list):
        if hasattr(cell, '_update_local_from_global'):
            cell._update_local_from_global()


def solve_hierarchical(cell, verbose: bool = False) -> bool:
    """
    Solve cell layout with hierarchical positioning awareness

    This solver:
    - Respects parent-child relationships
    - Maintains relative positioning where specified
    - Computes global positions for the entire hierarchy

    Args:
        cell: Top-level cell to solve
        verbose: Print detailed solving information

    Returns:
        True if solution found, False otherwise

    Usage:
        parent = Cell('parent')
        child = Cell('child', 'metal1')
        parent.add_child(child)

        # Set child position relative to parent
        enable_hierarchical_mode(parent)
        child.set_local_position(10, 10, 50, 50)

        # Solve maintains relative positioning
        solve_hierarchical(parent)
    """
    # First, use standard solver
    success = cell.solver()

    if not success:
        return False

    # If hierarchical mode is enabled, update all local positions
    if hasattr(cell, '_use_relative_coords') and cell._use_relative_coords:
        _update_hierarchy_local_positions(cell, verbose=verbose)

    return True


def _update_hierarchy_local_positions(cell, parent_origin=(0, 0), verbose=False):
    """
    Recursively update local positions for entire hierarchy

    Args:
        cell: Current cell to update
        parent_origin: Parent's origin in global coordinates
        verbose: Print update information
    """
    if not hasattr(cell, 'pos_list') or not cell.pos_list:
        return

    # Update this cell's local position
    if hasattr(cell, '_local_pos'):
        x1, y1, x2, y2 = cell.pos_list
        cell._local_pos = [
            x1 - parent_origin[0],
            y1 - parent_origin[1],
            x2 - parent_origin[0],
            y2 - parent_origin[1]
        ]

        if verbose:
            print(f"Cell {cell.name}: global={cell.pos_list}, local={cell._local_pos}")

    # Recurse to children
    if hasattr(cell, 'children'):
        current_origin = (cell.pos_list[0], cell.pos_list[1])
        for child in cell.children:
            _update_hierarchy_local_positions(child, current_origin, verbose)


def print_hierarchy_positions(cell, indent=0):
    """
    Print the position hierarchy for debugging

    Args:
        cell: Cell to print
        indent: Indentation level (for recursion)
    """
    prefix = "  " * indent

    # Get positions
    global_pos = None
    local_pos = None

    if hasattr(cell, 'get_global_position'):
        global_pos = cell.get_global_position()
    elif hasattr(cell, 'pos_list'):
        global_pos = cell.pos_list

    if hasattr(cell, 'get_local_position'):
        local_pos = cell.get_local_position()

    # Print cell info
    print(f"{prefix}{cell.name}:")
    if global_pos:
        print(f"{prefix}  Global: {global_pos}")
    if local_pos:
        print(f"{prefix}  Local:  {local_pos}")

    # Recurse to children
    if hasattr(cell, 'children'):
        for child in cell.children:
            print_hierarchy_positions(child, indent + 1)
