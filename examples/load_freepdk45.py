#!/usr/bin/env python3
"""
Example: Loading FreePDK45 technology file

This example demonstrates how to load and use the FreePDK45 technology file
with the updated parser that supports the .tf format.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from layout_automation.tech_file import TechFile, load_tech_file

def main():
    # Method 1: Using the convenience function
    print("Loading FreePDK45.tf using load_tech_file()...")
    tech = load_tech_file('../FreePDK45.tf')

    # Load DRF file for accurate layer colors
    print("\nLoading SantanaDisplay.drf for layer colors...")
    tech.parse_drf_file('../SantanaDisplay.drf')

    # Method 2: Create a TechFile instance directly
    # tech = TechFile()
    # tech.parse_virtuoso_tech_file('FreePDK45.tf')
    # tech.parse_drf_file('SantanaDisplay.drf')

    print("\nQuerying layer information:")
    print("-" * 60)

    # Get layer information
    layers = ['metal1', 'metal2', 'poly', 'active', 'contact']

    for layer_name in layers:
        layer = tech.get_layer(layer_name, 'drawing')
        if layer:
            color_str = layer.color or 'default'
            print(f"{layer_name:10} -> GDS {layer.gds_layer:2}/{layer.gds_datatype} "
                  f"(color: {color_str})")

    # Look up layer by GDS number
    print("\nReverse lookup (GDS layer -> name):")
    print("-" * 60)

    gds_layers = [(11, 0), (13, 0), (9, 0), (1, 0), (10, 0)]

    for gds_layer, gds_datatype in gds_layers:
        layer = tech.get_layer_by_gds(gds_layer, gds_datatype)
        if layer:
            print(f"GDS {gds_layer:2}/{gds_datatype} -> {layer.name} "
                  f"({layer.purpose})")

    # Export layer map for reference
    print("\nExporting layer map...")
    tech.export_layer_map('freepdk45_layer_map.txt')

if __name__ == '__main__':
    main()
