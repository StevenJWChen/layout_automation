#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkyWater Netlist Extractor

Wrapper around netlist extractor with SkyWater layer mapping
"""

from .netlist_extractor_improved import ImprovedNetlistExtractor, GeometricShape
from layout_automation.skywater_layer_map import get_layer_name
from layout_automation.lvs import Netlist, Device, Net
from typing import List, Dict
from layout_automation.units import to_um


class SkyWaterExtractor(ImprovedNetlistExtractor):
    """
    Netlist extractor with SkyWater layer mapping
    """

    def _flatten_layout(self):
        """Flatten layout and apply layer name mapping"""
        print("\n1. Flattening layout hierarchy...")

        # Get all shapes
        all_shapes = self._get_all_shapes(self.cell, 0, 0)

        # Apply layer mapping and group by layer NAME
        for shape in all_shapes:
            # Get layer name from GDS layer/datatype
            if isinstance(shape.layer, tuple):
                gds_layer, gds_datatype = shape.layer
                layer_name = get_layer_name(gds_layer, gds_datatype)
            elif isinstance(shape.layer, str):
                # Handle "layerXX" format from GDS import
                if shape.layer.startswith('layer'):
                    try:
                        layer_num = int(shape.layer[5:])
                        # Try common datatypes
                        layer_name = None
                        for datatype in [20, 44, 14, 16, 59]:
                            name = get_layer_name(layer_num, datatype)
                            if not name.startswith('layer'):
                                layer_name = name
                                break
                        if layer_name is None:
                            layer_name = shape.layer
                    except:
                        layer_name = shape.layer
                else:
                    layer_name = shape.layer
            else:
                layer_name = f"layer{shape.layer}"

            # Create new shape with layer name
            mapped_shape = GeometricShape(
                name=shape.name,
                layer=layer_name,  # Use mapped name
                x1=shape.x1,
                y1=shape.y1,
                x2=shape.x2,
                y2=shape.y2
            )

            if layer_name not in self.shapes:
                self.shapes[layer_name] = []
            self.shapes[layer_name].append(mapped_shape)

        # Print summary
        for layer, shapes in sorted(self.shapes.items()):
            print(f"   {layer}: {len(shapes)} shapes")


def extract_skywater_netlist(cell, tech):
    """
    Extract netlist from SkyWater cell with proper layer mapping

    Args:
        cell: Cell to extract from
        tech: Technology object

    Returns:
        Extracted netlist
    """
    extractor = SkyWaterExtractor(cell, tech)
    netlist = extractor.extract()
    return netlist


if __name__ == "__main__":
    print("SkyWater Netlist Extractor")
    print("="*70)
    print("\nUse: netlist = extract_skywater_netlist(cell, tech)")
