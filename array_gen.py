#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Array Generator Utility

Provides convenient functions for creating arrays of cell instances
with automatic constraint generation for common patterns.
"""

from typing import List, Union, Optional
from gds_cell import Cell, CellInstance


class ArrayGenerator:
    """
    Generator for creating arrays of cell instances
    """

    @staticmethod
    def create_1d_array(parent_cell: Cell,
                       base_cell: Cell,
                       count: int,
                       spacing: float,
                       direction: str = 'horizontal',
                       prefix: str = "inst") -> List[CellInstance]:
        """
        Create a 1D array of cell instances

        Args:
            parent_cell: Cell to add instances to
            base_cell: Cell to instantiate
            count: Number of instances
            spacing: Spacing between instances (edge-to-edge)
            direction: 'horizontal' or 'vertical'
            prefix: Prefix for instance names

        Returns:
            List of created CellInstance objects
        """
        if count < 1:
            raise ValueError("count must be at least 1")

        instances = []

        # Create instances
        for i in range(count):
            inst = CellInstance(f"{prefix}_{i}", base_cell)
            instances.append(inst)
            parent_cell.add_instance(inst)

        # Add constraints between adjacent instances
        for i in range(count - 1):
            if direction == 'horizontal':
                # Place next instance to the right
                parent_cell.constrain(
                    instances[i],
                    f'sx2+{spacing}<ox1',
                    instances[i + 1]
                )
                # Align vertically
                parent_cell.constrain(
                    instances[i],
                    'sy1=oy1',
                    instances[i + 1]
                )
            elif direction == 'vertical':
                # Place next instance above
                parent_cell.constrain(
                    instances[i],
                    f'sy2+{spacing}<oy1',
                    instances[i + 1]
                )
                # Align horizontally
                parent_cell.constrain(
                    instances[i],
                    'sx1=ox1',
                    instances[i + 1]
                )
            else:
                raise ValueError("direction must be 'horizontal' or 'vertical'")

        return instances

    @staticmethod
    def create_2d_array(parent_cell: Cell,
                       base_cell: Cell,
                       rows: int,
                       cols: int,
                       spacing_x: float,
                       spacing_y: float,
                       prefix: str = "inst") -> List[List[CellInstance]]:
        """
        Create a 2D array of cell instances

        Args:
            parent_cell: Cell to add instances to
            base_cell: Cell to instantiate
            rows: Number of rows
            cols: Number of columns
            spacing_x: Horizontal spacing between instances
            spacing_y: Vertical spacing between instances
            prefix: Prefix for instance names

        Returns:
            2D list of CellInstance objects [row][col]
        """
        if rows < 1 or cols < 1:
            raise ValueError("rows and cols must be at least 1")

        instances = []

        # Create instances in row-major order
        for row in range(rows):
            row_instances = []
            for col in range(cols):
                inst = CellInstance(f"{prefix}_r{row}_c{col}", base_cell)
                row_instances.append(inst)
                parent_cell.add_instance(inst)
            instances.append(row_instances)

        # Add horizontal constraints (within rows)
        for row in range(rows):
            for col in range(cols - 1):
                parent_cell.constrain(
                    instances[row][col],
                    f'sx2+{spacing_x}<ox1',
                    instances[row][col + 1]
                )
                parent_cell.constrain(
                    instances[row][col],
                    'sy1=oy1',
                    instances[row][col + 1]
                )

        # Add vertical constraints (between rows)
        for row in range(rows - 1):
            for col in range(cols):
                parent_cell.constrain(
                    instances[row][col],
                    f'sy2+{spacing_y}<oy1',
                    instances[row + 1][col]
                )
                parent_cell.constrain(
                    instances[row][col],
                    'sx1=ox1',
                    instances[row + 1][col]
                )

        return instances

    @staticmethod
    def create_symmetric_pair(parent_cell: Cell,
                             base_cell: Cell,
                             axis: str = 'y',
                             spacing: float = 10.0,
                             prefix: str = "inst") -> tuple[CellInstance, CellInstance]:
        """
        Create a symmetric pair of instances

        Args:
            parent_cell: Cell to add instances to
            base_cell: Cell to instantiate
            axis: 'x' or 'y' - axis of symmetry
            spacing: Spacing between instances
            prefix: Prefix for instance names

        Returns:
            Tuple of (inst1, inst2)
        """
        inst1 = CellInstance(f"{prefix}_1", base_cell)
        inst2 = CellInstance(f"{prefix}_2", base_cell)

        parent_cell.add_instance([inst1, inst2])

        # Use the built-in symmetry constraint
        parent_cell.add_symmetry(inst1, inst2, axis=axis)

        # Add spacing
        if axis == 'y':
            parent_cell.constrain(inst1, f'sx2+{spacing}<ox1', inst2)
        else:
            parent_cell.constrain(inst1, f'sy2+{spacing}<oy1', inst2)

        return inst1, inst2

    @staticmethod
    def create_interleaved_array(parent_cell: Cell,
                                 cell_a: Cell,
                                 cell_b: Cell,
                                 count: int,
                                 spacing: float,
                                 direction: str = 'horizontal',
                                 prefix_a: str = "inst_a",
                                 prefix_b: str = "inst_b") -> tuple[List[CellInstance], List[CellInstance]]:
        """
        Create interleaved array alternating between two cell types

        Args:
            parent_cell: Cell to add instances to
            cell_a: First cell type
            cell_b: Second cell type
            count: Total number of instances (will be rounded to even number)
            spacing: Spacing between instances
            direction: 'horizontal' or 'vertical'
            prefix_a: Prefix for cell_a instances
            prefix_b: Prefix for cell_b instances

        Returns:
            Tuple of (instances_a, instances_b)
        """
        if count < 2:
            raise ValueError("count must be at least 2")

        # Round to even number
        count = (count // 2) * 2

        instances_a = []
        instances_b = []
        all_instances = []

        # Create alternating instances
        for i in range(count):
            if i % 2 == 0:
                inst = CellInstance(f"{prefix_a}_{i//2}", cell_a)
                instances_a.append(inst)
            else:
                inst = CellInstance(f"{prefix_b}_{i//2}", cell_b)
                instances_b.append(inst)

            all_instances.append(inst)
            parent_cell.add_instance(inst)

        # Add constraints between adjacent instances
        for i in range(len(all_instances) - 1):
            if direction == 'horizontal':
                parent_cell.constrain(
                    all_instances[i],
                    f'sx2+{spacing}<ox1',
                    all_instances[i + 1]
                )
                parent_cell.constrain(
                    all_instances[i],
                    'sy1=oy1',
                    all_instances[i + 1]
                )
            elif direction == 'vertical':
                parent_cell.constrain(
                    all_instances[i],
                    f'sy2+{spacing}<oy1',
                    all_instances[i + 1]
                )
                parent_cell.constrain(
                    all_instances[i],
                    'sx1=ox1',
                    all_instances[i + 1]
                )
            else:
                raise ValueError("direction must be 'horizontal' or 'vertical'")

        return instances_a, instances_b

    @staticmethod
    def create_ring_array(parent_cell: Cell,
                         base_cell: Cell,
                         count: int,
                         radius: float,
                         prefix: str = "inst") -> List[CellInstance]:
        """
        Create instances arranged in a ring (approximation using constraints)

        Note: This creates a rectangular approximation of a ring layout.
        True circular placement would require angular positioning.

        Args:
            parent_cell: Cell to add instances to
            base_cell: Cell to instantiate
            count: Number of instances
            radius: Approximate radius (affects spacing)
            prefix: Prefix for instance names

        Returns:
            List of CellInstance objects
        """
        if count < 4:
            raise ValueError("count must be at least 4 for ring")

        instances = []

        # Create instances
        for i in range(count):
            inst = CellInstance(f"{prefix}_{i}", base_cell)
            instances.append(inst)
            parent_cell.add_instance(inst)

        # Arrange in square ring pattern
        # Calculate instances per side
        per_side = count // 4
        remainder = count % 4

        sides = [per_side] * 4
        for i in range(remainder):
            sides[i] += 1

        idx = 0

        # Bottom side (left to right)
        for i in range(sides[0] - 1):
            parent_cell.constrain(
                instances[idx],
                f'sx2+{radius/sides[0]}<ox1',
                instances[idx + 1]
            )
            parent_cell.constrain(instances[idx], 'sy1=oy1', instances[idx + 1])
            idx += 1
        idx += 1

        # Right side (bottom to top)
        for i in range(sides[1] - 1):
            parent_cell.constrain(
                instances[idx],
                f'sy2+{radius/sides[1]}<oy1',
                instances[idx + 1]
            )
            parent_cell.constrain(instances[idx], 'sx1=ox1', instances[idx + 1])
            idx += 1
        idx += 1

        # Top side (right to left)
        for i in range(sides[2] - 1):
            parent_cell.constrain(
                instances[idx],
                f'sx1-{radius/sides[2]}>ox2',
                instances[idx + 1]
            )
            parent_cell.constrain(instances[idx], 'sy1=oy1', instances[idx + 1])
            idx += 1
        idx += 1

        # Left side (top to bottom)
        for i in range(sides[3] - 1):
            parent_cell.constrain(
                instances[idx],
                f'sy1-{radius/sides[3]}>oy2',
                instances[idx + 1]
            )
            parent_cell.constrain(instances[idx], 'sx1=ox1', instances[idx + 1])
            idx += 1

        return instances


# Convenience functions for quick array creation

def create_row(parent_cell: Cell, base_cell: Cell, count: int,
              spacing: float = 10.0) -> List[CellInstance]:
    """
    Quick function to create a horizontal row

    Args:
        parent_cell: Parent cell
        base_cell: Cell to instantiate
        count: Number of instances
        spacing: Spacing between instances

    Returns:
        List of instances
    """
    gen = ArrayGenerator()
    return gen.create_1d_array(parent_cell, base_cell, count, spacing, 'horizontal')


def create_column(parent_cell: Cell, base_cell: Cell, count: int,
                 spacing: float = 10.0) -> List[CellInstance]:
    """
    Quick function to create a vertical column

    Args:
        parent_cell: Parent cell
        base_cell: Cell to instantiate
        count: Number of instances
        spacing: Spacing between instances

    Returns:
        List of instances
    """
    gen = ArrayGenerator()
    return gen.create_1d_array(parent_cell, base_cell, count, spacing, 'vertical')


def create_grid(parent_cell: Cell, base_cell: Cell, rows: int, cols: int,
               spacing_x: float = 10.0, spacing_y: float = 10.0) -> List[List[CellInstance]]:
    """
    Quick function to create a 2D grid

    Args:
        parent_cell: Parent cell
        base_cell: Cell to instantiate
        rows: Number of rows
        cols: Number of columns
        spacing_x: Horizontal spacing
        spacing_y: Vertical spacing

    Returns:
        2D list of instances [row][col]
    """
    gen = ArrayGenerator()
    return gen.create_2d_array(parent_cell, base_cell, rows, cols,
                               spacing_x, spacing_y)
