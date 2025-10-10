#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technology file support for layout automation

Defines process-specific layers, rules, and device parameters
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from units import um, nm, to_um


@dataclass
class Layer:
    """Layer definition"""
    name: str
    gds_layer: int
    gds_datatype: int = 0
    color: str = 'gray'
    fill: str = 'none'
    thickness_nm: Optional[int] = None  # Physical thickness


class Technology:
    """
    Technology definition for a specific process node

    Contains:
    - Layer definitions
    - Design rules
    - Device parameters
    """

    def __init__(self, name: str):
        """
        Initialize technology

        Args:
            name: Technology name (e.g., 'sky130', 'tsmc28')
        """
        self.name = name
        self.layers: Dict[str, Layer] = {}
        self.min_width: Dict[str, int] = {}
        self.min_spacing: Dict[str, int] = {}
        self.grid: int = 1  # Manufacturing grid in nm

    def add_layer(self, name: str, gds_layer: int, gds_datatype: int = 0,
                  color: str = 'gray', thickness_nm: Optional[int] = None):
        """Add layer definition"""
        self.layers[name] = Layer(
            name=name,
            gds_layer=gds_layer,
            gds_datatype=gds_datatype,
            color=color,
            thickness_nm=thickness_nm
        )

    def add_min_width(self, layer: str, width_nm: int):
        """Add minimum width rule"""
        self.min_width[layer] = width_nm

    def add_min_spacing(self, layer: str, spacing_nm: int):
        """Add minimum spacing rule"""
        self.min_spacing[layer] = spacing_nm

    def get_layer(self, name: str) -> Layer:
        """Get layer by name"""
        if name not in self.layers:
            raise ValueError(f"Layer '{name}' not defined in technology '{self.name}'")
        return self.layers[name]

    def get_gds_layer(self, name: str) -> Tuple[int, int]:
        """Get GDS layer/datatype for a layer name"""
        layer = self.get_layer(name)
        return (layer.gds_layer, layer.gds_datatype)


# Pre-defined technology: SkyWater SKY130
def create_sky130_tech() -> Technology:
    """
    Create SkyWater SKY130 technology definition

    Based on https://skywater-pdk.readthedocs.io/
    """
    tech = Technology('sky130')

    # Manufacturing grid
    tech.grid = 5  # 5nm grid

    # Layer definitions (from SkyWater PDK)
    tech.add_layer('nwell', 64, 20, 'tan', um(0.2))
    tech.add_layer('pwell', 64, 16, 'brown', um(0.2))
    tech.add_layer('diff', 65, 20, 'green', um(0.15))  # Active area
    tech.add_layer('tap', 65, 44, 'lightgreen')  # Substrate tap
    tech.add_layer('nsdm', 93, 44, 'red')  # N+ source/drain implant
    tech.add_layer('psdm', 94, 20, 'blue')  # P+ source/drain implant
    tech.add_layer('poly', 66, 20, 'red', um(0.18))  # Polysilicon
    tech.add_layer('licon1', 66, 44, 'purple')  # Local interconnect contact
    tech.add_layer('li1', 67, 20, 'purple', um(0.1))  # Local interconnect
    tech.add_layer('mcon', 67, 44, 'blue')  # Metal contact
    tech.add_layer('met1', 68, 20, 'blue', um(0.36))  # Metal 1
    tech.add_layer('via', 68, 44, 'cyan')  # Via 1
    tech.add_layer('met2', 69, 20, 'cyan', um(0.36))  # Metal 2
    tech.add_layer('via2', 69, 44, 'magenta')  # Via 2
    tech.add_layer('met3', 70, 20, 'magenta', um(0.845))  # Metal 3
    tech.add_layer('via3', 70, 44, 'yellow')  # Via 3
    tech.add_layer('met4', 71, 20, 'yellow', um(0.845))  # Metal 4
    tech.add_layer('via4', 71, 44, 'orange')  # Via 4
    tech.add_layer('met5', 72, 20, 'orange', um(1.26))  # Metal 5

    # Design rules (simplified - see PDK for complete rules)
    tech.add_min_width('poly', nm(150))
    tech.add_min_width('diff', nm(150))
    tech.add_min_width('li1', nm(170))
    tech.add_min_width('met1', nm(140))
    tech.add_min_width('met2', nm(140))

    tech.add_min_spacing('poly', nm(210))
    tech.add_min_spacing('diff', nm(250))
    tech.add_min_spacing('li1', nm(170))
    tech.add_min_spacing('met1', nm(140))
    tech.add_min_spacing('met2', nm(140))

    return tech


# Example usage
if __name__ == "__main__":
    print("Technology System Example")
    print("=" * 70)

    # Create SkyWater technology
    tech = create_sky130_tech()

    print(f"\nTechnology: {tech.name}")
    print(f"Manufacturing grid: {tech.grid} nm")

    print(f"\nLayers defined: {len(tech.layers)}")
    for name, layer in list(tech.layers.items())[:10]:
        thickness = f"{to_um(layer.thickness_nm):.2f} um" if layer.thickness_nm else "N/A"
        print(f"  {name:10s}: GDS {layer.gds_layer:3d}/{layer.gds_datatype} "
              f"thickness={thickness}")

    print(f"\nDesign Rules:")
    print(f"  Minimum widths:")
    for layer, width in tech.min_width.items():
        print(f"    {layer:10s}: {width} nm ({width/1000:.3f} um)")

    print(f"\n  Minimum spacings:")
    for layer, spacing in tech.min_spacing.items():
        print(f"    {layer:10s}: {spacing} nm ({spacing/1000:.3f} um)")

    # Test layer lookup
    print(f"\nLayer Lookup Example:")
    poly = tech.get_layer('poly')
    print(f"  poly: GDS layer/datatype = {tech.get_gds_layer('poly')}")
    print(f"  poly: color = {poly.color}")
    print(f"  poly: thickness = {poly.thickness_nm} nm")

    print(f"\nSkyWater Inverter in this technology:")
    print(f"  NMOS W={um(0.65)} nm, L={um(0.15)} nm")
    print(f"  PMOS W={um(1.0)} nm, L={um(0.15)} nm")
    print(f"  Uses layers: poly({tech.get_gds_layer('poly')}), "
          f"diff({tech.get_gds_layer('diff')}), "
          f"met1({tech.get_gds_layer('met1')})")
