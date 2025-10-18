#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technology file parser for Virtuoso and other formats

Handles:
- Layer name to GDS layer/datatype mapping
- Display colors from tech files
- Layer purpose definitions
- Stream (GDS) layer numbers
"""

import re
from typing import Dict, Tuple, Optional
from layout_automation.style_config import get_style_config


class LayerMapping:
    """Layer mapping information"""

    def __init__(self, name: str, purpose: str = 'drawing',
                 gds_layer: int = 0, gds_datatype: int = 0,
                 color: Optional[str] = None):
        """
        Initialize layer mapping

        Args:
            name: Layer name (e.g., 'metal1', 'poly')
            purpose: Layer purpose (e.g., 'drawing', 'pin', 'label')
            gds_layer: GDS layer number
            gds_datatype: GDS datatype number
            color: Display color (optional)
        """
        self.name = name
        self.purpose = purpose
        self.gds_layer = gds_layer
        self.gds_datatype = gds_datatype
        self.color = color

    def __repr__(self):
        return (f"LayerMapping(name='{self.name}', purpose='{self.purpose}', "
                f"gds_layer={self.gds_layer}, gds_datatype={self.gds_datatype}, "
                f"color='{self.color}')")


class TechFile:
    """Technology file parser and manager"""

    def __init__(self):
        """Initialize empty tech file"""
        self.layers: Dict[Tuple[str, str], LayerMapping] = {}  # (name, purpose) -> LayerMapping
        self.gds_to_layer: Dict[Tuple[int, int], LayerMapping] = {}  # (gds_layer, gds_datatype) -> LayerMapping
        self.tech_name = "unknown"

    def add_layer(self, mapping: LayerMapping):
        """Add a layer mapping"""
        key = (mapping.name, mapping.purpose)
        self.layers[key] = mapping

        gds_key = (mapping.gds_layer, mapping.gds_datatype)
        self.gds_to_layer[gds_key] = mapping

    def get_layer(self, name: str, purpose: str = 'drawing') -> Optional[LayerMapping]:
        """Get layer mapping by name and purpose"""
        return self.layers.get((name, purpose))

    def get_layer_by_gds(self, gds_layer: int, gds_datatype: int = 0) -> Optional[LayerMapping]:
        """Get layer mapping by GDS layer/datatype"""
        return self.gds_to_layer.get((gds_layer, gds_datatype))

    def get_gds_layer(self, name: str, purpose: str = 'drawing') -> Tuple[int, int]:
        """Get GDS layer/datatype for a layer name"""
        mapping = self.get_layer(name, purpose)
        if mapping:
            return (mapping.gds_layer, mapping.gds_datatype)
        return (0, 0)

    def apply_colors_to_style(self):
        """Apply tech file colors to the style configuration"""
        style = get_style_config()

        for (name, purpose), mapping in self.layers.items():
            if purpose == 'drawing' and mapping.color:
                style.set_layer_style(name, color=mapping.color)

    def parse_virtuoso_tech_file(self, filepath: str):
        """
        Parse a Cadence Virtuoso technology file

        Args:
            filepath: Path to technology file
        """
        print(f"Parsing Virtuoso tech file: {filepath}")

        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Warning: Tech file not found: {filepath}")
            return

        # Parse layerDefinitions section
        self._parse_layer_definitions(content)

        # Parse streamLayers section
        self._parse_stream_layers(content)

        # Parse display resources (colors)
        self._parse_display_resources(content)

        print(f"✓ Loaded {len(self.layers)} layer mappings")

    def _parse_layer_definitions(self, content: str):
        """Parse layerDefinitions section"""
        # Find layerDefinitions section using balanced parentheses
        layer_section = self._extract_balanced_section(content, 'layerDefinitions')
        if not layer_section:
            return

        # Find techLayerPurposePriorities section
        priorities_section = self._extract_balanced_section(layer_section, 'techLayerPurposePriorities')
        if priorities_section:
            # Parse individual entries: "layerName" "purpose" number
            # Can be on same line or separate lines
            layer_pattern = r'"([^"]+)"\s+"([^"]+)"\s+(\d+)'

            for match in re.finditer(layer_pattern, priorities_section):
                name = match.group(1)
                purpose = match.group(2)
                priority = int(match.group(3))

                # Create mapping (GDS numbers will be filled in later)
                mapping = LayerMapping(name, purpose, gds_layer=0, gds_datatype=0)
                self.add_layer(mapping)
        else:
            # Try old format: techLayerPurposePriorities("layerName" "purpose" number)
            layer_pattern = r'techLayerPurposePriorities\(\s*"([^"]+)"\s+"([^"]+)"\s+(\d+)\s*\)'

            for match in re.finditer(layer_pattern, layer_section):
                name = match.group(1)
                purpose = match.group(2)
                priority = int(match.group(3))

                # Create mapping (GDS numbers will be filled in later)
                mapping = LayerMapping(name, purpose, gds_layer=0, gds_datatype=0)
                self.add_layer(mapping)

    def _extract_balanced_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a section with balanced parentheses"""
        # Find the section start
        pattern = rf'{section_name}\s*\('
        match = re.search(pattern, content)
        if not match:
            return None

        # Find balanced closing paren
        start = match.end() - 1  # Position of opening paren
        paren_count = 0
        pos = start

        while pos < len(content):
            if content[pos] == '(':
                paren_count += 1
            elif content[pos] == ')':
                paren_count -= 1
                if paren_count == 0:
                    # Found the matching closing paren
                    return content[start+1:pos]
            pos += 1

        return None

    def _parse_stream_layers(self, content: str):
        """Parse streamLayers section for GDS layer numbers"""
        # Find streamLayers section using balanced parentheses
        stream_section = self._extract_balanced_section(content, 'streamLayers')
        if not stream_section:
            return

        # Parse layer/datatype mappings
        # Format: ("layerName" "purpose" layerNumber datatype)
        stream_pattern = r'\(\s*"([^"]+)"\s+"([^"]+)"\s+(\d+)\s+(\d+)\s*\)'

        for match in re.finditer(stream_pattern, stream_section):
            name = match.group(1)
            purpose = match.group(2)
            gds_layer = int(match.group(3))
            gds_datatype = int(match.group(4))

            # Update existing mapping or create new one
            key = (name, purpose)
            if key in self.layers:
                mapping = self.layers[key]
                mapping.gds_layer = gds_layer
                mapping.gds_datatype = gds_datatype
                # Update GDS lookup
                gds_key = (gds_layer, gds_datatype)
                self.gds_to_layer[gds_key] = mapping
            else:
                mapping = LayerMapping(name, purpose, gds_layer, gds_datatype)
                self.add_layer(mapping)

    def _parse_display_resources(self, content: str):
        """Parse display section for layer colors"""
        # Find display section using balanced parentheses
        display_section = self._extract_balanced_section(content, 'drDefineDisplay')
        if not display_section:
            return

        # Parse color definitions
        # Format: techLayerProperties("layerName" "purpose" ... color "colorName" ...)
        color_pattern = r'techLayerProperties\(\s*"([^"]+)"\s+"([^"]+)"[^)]*color\s+"([^"]+)"'

        for match in re.finditer(color_pattern, display_section):
            name = match.group(1)
            purpose = match.group(2)
            color = match.group(3)

            # Convert Virtuoso color names to matplotlib colors
            matplotlib_color = self._convert_color(color)

            key = (name, purpose)
            if key in self.layers:
                self.layers[key].color = matplotlib_color

    def _convert_color(self, virtuoso_color: str) -> str:
        """Convert Virtuoso color name to matplotlib color"""
        # Common Virtuoso to matplotlib color mappings
        color_map = {
            'red': 'red',
            'green': 'green',
            'blue': 'blue',
            'yellow': 'yellow',
            'cyan': 'cyan',
            'magenta': 'magenta',
            'white': 'white',
            'black': 'black',
            'orange': 'orange',
            'purple': 'purple',
            'pink': 'pink',
            'brown': 'brown',
            'tan': 'tan',
            'lime': 'lime',
            'navy': 'navy',
            'maroon': 'maroon',
            'olive': 'olive',
            'silver': 'silver',
            'gray': 'gray',
            'gold': 'gold',
        }

        return color_map.get(virtuoso_color.lower(), virtuoso_color)

    def create_generic_tech(self, tech_name: str = 'generic'):
        """Create a generic technology with common layers"""
        self.tech_name = tech_name

        # Common CMOS layers with standard GDS numbers
        layers = [
            LayerMapping('nwell', 'drawing', 1, 0, 'lightgreen'),
            LayerMapping('pwell', 'drawing', 2, 0, 'lightcoral'),
            LayerMapping('diff', 'drawing', 3, 0, 'brown'),
            LayerMapping('ndiff', 'drawing', 3, 0, 'green'),
            LayerMapping('pdiff', 'drawing', 4, 0, 'tan'),
            LayerMapping('poly', 'drawing', 10, 0, 'red'),
            LayerMapping('contact', 'drawing', 20, 0, 'black'),
            LayerMapping('metal1', 'drawing', 30, 0, 'blue'),
            LayerMapping('via1', 'drawing', 40, 0, 'gray'),
            LayerMapping('metal2', 'drawing', 50, 0, 'red'),
            LayerMapping('via2', 'drawing', 60, 0, 'gray'),
            LayerMapping('metal3', 'drawing', 70, 0, 'green'),
            LayerMapping('via3', 'drawing', 80, 0, 'gray'),
            LayerMapping('metal4', 'drawing', 90, 0, 'orange'),
            LayerMapping('via4', 'drawing', 100, 0, 'gray'),
            LayerMapping('metal5', 'drawing', 110, 0, 'cyan'),
            LayerMapping('via5', 'drawing', 120, 0, 'gray'),
            LayerMapping('metal6', 'drawing', 130, 0, 'magenta'),
        ]

        for layer in layers:
            self.add_layer(layer)

        print(f"✓ Created generic tech '{tech_name}' with {len(layers)} layers")

    def export_layer_map(self, filepath: str):
        """Export layer mapping to a simple text file"""
        with open(filepath, 'w') as f:
            f.write(f"# Technology: {self.tech_name}\n")
            f.write("# Format: LayerName Purpose GDS_Layer GDS_Datatype Color\n\n")

            for (name, purpose), mapping in sorted(self.layers.items()):
                color = mapping.color or 'default'
                f.write(f"{name:15} {purpose:10} {mapping.gds_layer:3} {mapping.gds_datatype:2} {color}\n")

        print(f"✓ Exported layer map to {filepath}")

    def print_summary(self):
        """Print a summary of the technology file"""
        print(f"\nTechnology: {self.tech_name}")
        print(f"Total layers: {len(self.layers)}")
        print("\nLayer Mappings:")
        print(f"{'Layer':15} {'Purpose':10} {'GDS Layer':10} {'GDS Type':10} {'Color':15}")
        print("-" * 70)

        for (name, purpose), mapping in sorted(self.layers.items()):
            color = mapping.color or '-'
            print(f"{name:15} {purpose:10} {mapping.gds_layer:<10} {mapping.gds_datatype:<10} {color:15}")


# Global technology file instance
_global_tech_file = None


def get_tech_file() -> TechFile:
    """Get the global technology file instance"""
    global _global_tech_file
    if _global_tech_file is None:
        _global_tech_file = TechFile()
        _global_tech_file.create_generic_tech()
    return _global_tech_file


def set_tech_file(tech: TechFile):
    """Set the global technology file"""
    global _global_tech_file
    _global_tech_file = tech


def load_tech_file(filepath: str):
    """Load a technology file"""
    tech = TechFile()
    tech.parse_virtuoso_tech_file(filepath)
    set_tech_file(tech)
    return tech
