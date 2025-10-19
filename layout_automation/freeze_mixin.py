#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Freeze Layout Mixin

Provides freeze_layout() functionality for treating cells as immutable black boxes.
This is separate from fix_layout() which preserves internal structure for repositioning.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from layout_automation.cell import Cell


class FreezeMixin:
    """
    Mixin class providing freeze_layout functionality.

    When a cell is frozen:
    - Internal structure is LOCKED (size and child positions fixed)
    - Can be used as fixed layout in parent cells
    - Only the cell's position can be changed by parent constraints
    - Solver fixes size: x2-x1=frozen_width, y2-y1=frozen_height
    - Efficiently reusable as fixed IP block
    - Bounding box is cached for fast access
    - Children are excluded from solver (treated as black box)

    This is different from fix_layout():
    - freeze: treats cell as black box, internal structure locked
    - fix: allows repositioning while updating all internal elements
    """

    def _init_freeze_attributes(self):
        """Initialize freeze-related attributes. Called from Cell.__init__()"""
        self._frozen = False  # Track if layout is frozen
        self._frozen_bbox = None  # Cache bbox when frozen

    def freeze_layout(self) -> 'Cell':
        """
        Freeze the current layout as a fixed block

        When frozen:
        - Internal structure is LOCKED (size and child positions fixed)
        - Can be used as fixed layout in parent cells
        - Only the cell's position can be changed by parent constraints
        - Solver fixes size: x2-x1=frozen_width, y2-y1=frozen_height
        - Efficiently reusable as fixed IP block
        - Bounding box is cached for fast access

        Returns:
            Self for method chaining

        Example:
            >>> block = Cell('ip_block')
            >>> # ... create complex layout ...
            >>> block.solver()
            >>> block.freeze_layout()  # Lock as immutable IP block
            >>>
            >>> parent.constrain(block, 'x1=100, y1=50')
            >>> parent.solver()
            >>> # block bbox moves, but children positions unchanged
        """
        if self._frozen:
            return self  # Already frozen

        # Solve if not yet solved
        if any(v is None for v in self.pos_list):
            if not self.solver():
                raise RuntimeError(f"Cannot freeze cell '{self.name}': solver failed")

        # Mark as frozen
        self._frozen = True

        # Cache the bounding box
        self._frozen_bbox = tuple(self.pos_list)

        # Recursively freeze all children
        for child in self.children:
            if not child.is_leaf:
                child.freeze_layout()

        print(f"✓ Cell '{self.name}' frozen with bbox {self._frozen_bbox}")
        return self

    def unfreeze_layout(self) -> 'Cell':
        """
        Unfreeze the layout, allowing modifications again

        Returns:
            Self for method chaining
        """
        self._frozen = False
        self._frozen_bbox = None

        # Recursively unfreeze all children
        for child in self.children:
            if not child.is_leaf:
                child.unfreeze_layout()

        return self

    def is_frozen(self) -> bool:
        """
        Check if this cell's layout is frozen

        Returns:
            True if frozen, False otherwise
        """
        return self._frozen

    def _get_frozen_bbox(self):
        """
        Get the frozen bounding box if cell is frozen

        Returns:
            Tuple of (x1, y1, x2, y2) if frozen, None otherwise
        """
        if self._frozen and self._frozen_bbox is not None:
            return self._frozen_bbox
        return None

    def _apply_frozen_size_constraint(self, model, var_objects, x1_var, y1_var, x2_var, y2_var):
        """
        Apply frozen size constraints to OR-Tools model

        Args:
            model: OR-Tools CP model
            var_objects: Dictionary of variable objects
            x1_var, y1_var, x2_var, y2_var: OR-Tools variables for this cell

        Returns:
            True if constraints were applied, False if not frozen
        """
        if self._frozen and self._frozen_bbox is not None:
            x1_f, y1_f, x2_f, y2_f = self._frozen_bbox
            width = x2_f - x1_f
            height = y2_f - y1_f

            # Fix the size (but allow position to vary)
            model.Add(x2_var - x1_var == width)
            model.Add(y2_var - y1_var == height)
            return True

        return False

    def _is_frozen_or_fixed(self):
        """
        Check if cell is frozen OR fixed (used in multiple places)

        Returns:
            True if frozen or fixed, False otherwise
        """
        return self._frozen or getattr(self, '_fixed', False)

    def _get_frozen_status_str(self) -> str:
        """
        Get frozen status string for __repr__

        Returns:
            " [FROZEN]" if frozen, empty string otherwise
        """
        return " [FROZEN]" if self._frozen else ""


# Export the mixin
__all__ = ['FreezeMixin']
