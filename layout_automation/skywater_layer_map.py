#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkyWater SKY130 Layer Mapping

Maps GDS layer numbers to layer names for proper extraction
"""

# SkyWater SKY130 Layer Map
# Format: (gds_layer, gds_datatype): layer_name
SKYWATER_LAYER_MAP = {
    # Active layers
    (64, 20): 'nwell',
    (64, 44): 'pwell',
    (65, 20): 'diff',      # Active diffusion
    (65, 44): 'tap',       # Substrate/well tap

    # Poly
    (66, 20): 'poly',      # Polysilicon (alternate)
    (66, 44): 'licon1',    # Local interconnect contact (alternate)
    (67, 20): 'poly',      # Polysilicon gate
    (67, 44): 'poly',      # Polysilicon (drawing)

    # Local interconnect
    (67, 14): 'licon1',    # Local interconnect contact
    (68, 20): 'li1',       # Local interconnect metal

    # Metal stack
    (69, 20): 'mcon',      # Metal contact (li1 to met1)
    (70, 20): 'met1',      # Metal 1
    (71, 20): 'via',       # Via (met1 to met2)
    (72, 20): 'met2',      # Metal 2
    (73, 20): 'via2',      # Via2 (met2 to met3)
    (74, 20): 'met3',      # Metal 3
    (75, 20): 'via3',      # Via3 (met3 to met4)
    (76, 20): 'met4',      # Metal 4
    (77, 20): 'via4',      # Via4 (met4 to met5)
    (78, 20): 'met5',      # Metal 5

    # Implants
    (93, 44): 'nsdm',      # N+ source/drain implant
    (94, 20): 'psdm',      # P+ source/drain implant

    # HVI (high voltage)
    (75, 20): 'hvtp',      # HV PMOS threshold adjust
    (78, 44): 'hvtr',      # HV resistor

    # Other
    (95, 20): 'npc',       # Nitride poly cut
    (64, 59): 'pwde',      # Deep nwell (extended pwell)
    (122, 16): 'nsm',      # N+ source/drain marker
    (125, 44): 'capm',     # MiM capacitor
}

def get_layer_name(gds_layer, gds_datatype):
    """
    Get layer name from GDS layer/datatype

    Args:
        gds_layer: GDS layer number
        gds_datatype: GDS datatype number

    Returns:
        Layer name string, or f"layer{gds_layer}" if not found
    """
    key = (gds_layer, gds_datatype)
    return SKYWATER_LAYER_MAP.get(key, f"layer{gds_layer}")


def get_all_layer_names():
    """Get set of all known layer names"""
    return set(SKYWATER_LAYER_MAP.values())


def print_layer_map():
    """Print the layer mapping for reference"""
    print("SkyWater SKY130 Layer Map")
    print("="*70)
    print(f"{'GDS Layer':<15} {'Datatype':<10} {'Layer Name':<15}")
    print("-"*70)

    for (layer, datatype), name in sorted(SKYWATER_LAYER_MAP.items()):
        print(f"{layer:<15} {datatype:<10} {name:<15}")

    print("="*70)
    print(f"Total: {len(SKYWATER_LAYER_MAP)} layer mappings")


if __name__ == "__main__":
    print_layer_map()
