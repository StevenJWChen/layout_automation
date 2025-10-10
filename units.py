#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit system for layout coordinates

Supports microns (um), nanometers (nm), and conversion to integer grid
"""

from typing import Union


class Unit:
    """
    Unit system for layout coordinates

    Internally stores values in database units (DBU)
    Default: 1 DBU = 1 nm
    """

    # Database unit in meters
    DBU_IN_METERS = 1e-9  # 1 nm

    @staticmethod
    def um(value: float) -> int:
        """
        Convert microns to database units

        Args:
            value: Value in microns

        Returns:
            Integer value in database units (nm)
        """
        return int(round(value * 1000))  # 1 um = 1000 nm

    @staticmethod
    def nm(value: float) -> int:
        """
        Convert nanometers to database units

        Args:
            value: Value in nanometers

        Returns:
            Integer value in database units (nm)
        """
        return int(round(value))

    @staticmethod
    def to_um(dbu_value: int) -> float:
        """
        Convert database units to microns

        Args:
            dbu_value: Value in database units (nm)

        Returns:
            Float value in microns
        """
        return dbu_value / 1000.0

    @staticmethod
    def to_nm(dbu_value: int) -> float:
        """
        Convert database units to nanometers

        Args:
            dbu_value: Value in database units (nm)

        Returns:
            Float value in nanometers
        """
        return float(dbu_value)


# Convenience functions
def um(value: float) -> int:
    """Convert microns to integer DBU (nanometers)"""
    return Unit.um(value)


def nm(value: float) -> int:
    """Convert nanometers to integer DBU"""
    return Unit.nm(value)


def to_um(dbu: int) -> float:
    """Convert DBU to microns"""
    return Unit.to_um(dbu)


def to_nm(dbu: int) -> float:
    """Convert DBU to nanometers"""
    return Unit.to_nm(dbu)


# Examples of usage:
if __name__ == "__main__":
    print("Unit System Examples")
    print("=" * 50)

    # Convert from microns
    print(f"1.5 um = {um(1.5)} nm (DBU)")
    print(f"0.15 um = {um(0.15)} nm (DBU)")
    print(f"2.72 um = {um(2.72)} nm (DBU)")

    # Convert from nanometers
    print(f"\n150 nm = {nm(150)} nm (DBU)")
    print(f"265 nm = {nm(265)} nm (DBU)")

    # Convert back
    print(f"\n2720 DBU = {to_um(2720)} um")
    print(f"150 DBU = {to_um(150)} um")

    # SkyWater inverter dimensions
    print("\n" + "=" * 50)
    print("SkyWater Inverter Dimensions in DBU:")
    print(f"  NMOS width: 0.65um = {um(0.65)} nm")
    print(f"  PMOS width: 1.0um = {um(1.0)} nm")
    print(f"  Gate length: 0.15um = {um(0.15)} nm")
    print(f"  Cell height: 2.72um = {um(2.72)} nm")
    print(f"  Cell width: 1.38um = {um(1.38)} nm")
