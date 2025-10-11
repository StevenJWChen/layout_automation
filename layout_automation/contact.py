#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contact and Via generator for layout automation

Generates contacts/vias between different layers following technology rules
"""

from typing import Tuple, Optional, List
from .gds_cell import Cell, Polygon
from .technology import Technology
from .units import um, nm


class Contact:
    """
    Contact/via generator between two layers

    Generates the contact geometry including:
    - Contact/via cut itself
    - Enclosure rectangles on top and bottom layers

    Attributes:
        name: Contact identifier
        bottom_layer: Lower layer name (e.g., 'diff', 'li1')
        top_layer: Upper layer name (e.g., 'li1', 'met1')
        contact_layer: Contact/via layer name
        position: (x, y) center position
        technology: Technology object with design rules
        size: (width, height) of contact array
        rows: Number of contact rows
        cols: Number of contact columns
    """

    def __init__(self, name: str, bottom_layer: str, top_layer: str,
                 position: Tuple[int, int], technology: Technology,
                 rows: int = 1, cols: int = 1):
        """
        Initialize contact generator

        Args:
            name: Contact identifier
            bottom_layer: Name of bottom layer (e.g., 'diff', 'li1')
            top_layer: Name of top layer (e.g., 'li1', 'met1')
            position: (x, y) center position in DBU
            technology: Technology object
            rows: Number of contact rows (for contact arrays)
            cols: Number of contact columns (for contact arrays)
        """
        self.name = name
        self.bottom_layer = bottom_layer
        self.top_layer = top_layer
        self.position = position
        self.technology = technology
        self.rows = rows
        self.cols = cols

        # Determine contact layer from layer pair
        self.contact_layer = self._get_contact_layer(bottom_layer, top_layer)

    def _get_contact_layer(self, bottom: str, top: str) -> str:
        """
        Determine contact layer name from bottom/top layer pair

        Args:
            bottom: Bottom layer name
            top: Top layer name

        Returns:
            Contact layer name
        """
        # Common contact layer mappings for SkyWater SKY130
        contact_map = {
            ('diff', 'li1'): 'licon1',
            ('poly', 'li1'): 'licon1',
            ('tap', 'li1'): 'licon1',
            ('li1', 'met1'): 'mcon',
            ('met1', 'met2'): 'via',
            ('met2', 'met3'): 'via2',
            ('met3', 'met4'): 'via3',
            ('met4', 'met5'): 'via4',
        }

        key = (bottom, top)
        if key in contact_map:
            return contact_map[key]
        else:
            # Generic naming: contact_{bottom}_{top}
            return f'contact_{bottom}_{top}'

    def generate(self, cell: Cell) -> List[Polygon]:
        """
        Generate contact polygons and add to cell

        Creates:
        1. Contact/via cuts (single or array)
        2. Enclosure rectangles on bottom layer
        3. Enclosure rectangles on top layer

        Args:
            cell: Cell to add contact polygons to

        Returns:
            List of generated Polygon objects
        """
        polygons = []

        # Get design rules (use defaults if not in technology)
        contact_size = self._get_contact_size()
        contact_spacing = self._get_contact_spacing()
        bottom_enclosure = self._get_enclosure(self.bottom_layer)
        top_enclosure = self._get_enclosure(self.top_layer)

        # Generate contact array
        cx, cy = self.position

        # Calculate array dimensions
        array_width = self.cols * contact_size + (self.cols - 1) * contact_spacing
        array_height = self.rows * contact_size + (self.rows - 1) * contact_spacing

        # Generate individual contact cuts
        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate contact position (centered array)
                offset_x = col * (contact_size + contact_spacing) - array_width // 2
                offset_y = row * (contact_size + contact_spacing) - array_height // 2

                cut_x1 = cx + offset_x
                cut_y1 = cy + offset_y
                cut_x2 = cut_x1 + contact_size
                cut_y2 = cut_y1 + contact_size

                # Create contact cut polygon
                cut = Polygon(f'{self.name}_cut_{row}_{col}', self.contact_layer)
                cut.pos_list = [cut_x1, cut_y1, cut_x2, cut_y2]
                polygons.append(cut)

        # Generate bottom layer enclosure
        bottom_x1 = cx - array_width // 2 - bottom_enclosure
        bottom_y1 = cy - array_height // 2 - bottom_enclosure
        bottom_x2 = cx + array_width // 2 + array_width % 2 + bottom_enclosure
        bottom_y2 = cy + array_height // 2 + array_height % 2 + bottom_enclosure

        bottom_poly = Polygon(f'{self.name}_bottom', self.bottom_layer)
        bottom_poly.pos_list = [bottom_x1, bottom_y1, bottom_x2, bottom_y2]
        polygons.append(bottom_poly)

        # Generate top layer enclosure
        top_x1 = cx - array_width // 2 - top_enclosure
        top_y1 = cy - array_height // 2 - top_enclosure
        top_x2 = cx + array_width // 2 + array_width % 2 + top_enclosure
        top_y2 = cy + array_height // 2 + array_height % 2 + top_enclosure

        top_poly = Polygon(f'{self.name}_top', self.top_layer)
        top_poly.pos_list = [top_x1, top_y1, top_x2, top_y2]
        polygons.append(top_poly)

        # Add all polygons to cell
        cell.add_polygon(polygons)

        return polygons

    def _get_contact_size(self) -> int:
        """Get contact cut size from technology (DBU)"""
        # Default contact sizes for common layers (in nm)
        defaults = {
            'licon1': nm(170),  # Local interconnect contact
            'mcon': nm(170),    # Metal contact
            'via': nm(150),     # Via 1
            'via2': nm(200),    # Via 2
            'via3': nm(200),    # Via 3
            'via4': nm(800),    # Via 4
        }

        return defaults.get(self.contact_layer, nm(170))

    def _get_contact_spacing(self) -> int:
        """Get minimum contact spacing from technology (DBU)"""
        # Default contact spacing (in nm)
        defaults = {
            'licon1': nm(170),
            'mcon': nm(190),
            'via': nm(170),
            'via2': nm(200),
            'via3': nm(200),
            'via4': nm(800),
        }

        return defaults.get(self.contact_layer, nm(170))

    def _get_enclosure(self, layer: str) -> int:
        """Get contact enclosure rule for a layer (DBU)"""
        # Default enclosures for common layers (in nm)
        defaults = {
            'diff': nm(60),
            'poly': nm(80),
            'tap': nm(60),
            'li1': nm(80),
            'met1': nm(30),
            'met2': nm(40),
            'met3': nm(60),
            'met4': nm(60),
            'met5': nm(60),
        }

        return defaults.get(layer, nm(60))


class ViaStack:
    """
    Via stack generator for connecting across multiple metal layers

    Creates a stack of vias to connect from one metal layer to another,
    automatically inserting all necessary intermediate vias.

    Example:
        # Connect met1 to met3 (requires via + via2)
        stack = ViaStack('via_stack', 'met1', 'met3', (500, 500), tech)
        stack.generate(cell)
    """

    def __init__(self, name: str, bottom_layer: str, top_layer: str,
                 position: Tuple[int, int], technology: Technology,
                 rows: int = 1, cols: int = 1):
        """
        Initialize via stack generator

        Args:
            name: Via stack identifier
            bottom_layer: Starting metal layer
            top_layer: Ending metal layer
            position: (x, y) center position
            technology: Technology object
            rows: Number of via rows
            cols: Number of via columns
        """
        self.name = name
        self.bottom_layer = bottom_layer
        self.top_layer = top_layer
        self.position = position
        self.technology = technology
        self.rows = rows
        self.cols = cols

    def generate(self, cell: Cell) -> List[Contact]:
        """
        Generate via stack and add to cell

        Returns:
            List of Contact objects created
        """
        # Define metal layer stack
        metal_stack = ['li1', 'met1', 'met2', 'met3', 'met4', 'met5']

        # Find bottom and top indices
        try:
            bottom_idx = metal_stack.index(self.bottom_layer)
            top_idx = metal_stack.index(self.top_layer)
        except ValueError:
            raise ValueError(f"Invalid metal layers: {self.bottom_layer}, {self.top_layer}")

        if bottom_idx >= top_idx:
            raise ValueError(f"Bottom layer must be below top layer")

        # Generate vias for each layer transition
        contacts = []
        for i in range(bottom_idx, top_idx):
            layer_bottom = metal_stack[i]
            layer_top = metal_stack[i + 1]

            contact = Contact(
                f'{self.name}_via{i}',
                layer_bottom,
                layer_top,
                self.position,
                self.technology,
                rows=self.rows,
                cols=self.cols
            )
            contact.generate(cell)
            contacts.append(contact)

        return contacts


# Example usage and testing
if __name__ == "__main__":
    from technology import create_sky130_tech

    print("Contact/Via Generator Example")
    print("=" * 70)

    # Create technology
    tech = create_sky130_tech()

    # Create test cell
    cell = Cell("contact_test")

    # Example 1: Single contact from diff to li1
    print("\n1. Single contact (diff → li1)")
    contact1 = Contact('cont1', 'diff', 'li1', (um(1), um(1)), tech)
    polys1 = contact1.generate(cell)
    print(f"   Generated {len(polys1)} polygons:")
    for p in polys1:
        print(f"     {p.name}: {p.layer}, pos={p.pos_list}")

    # Example 2: Contact array from li1 to met1
    print("\n2. Contact array 2x2 (li1 → met1)")
    contact2 = Contact('cont2', 'li1', 'met1', (um(3), um(1)), tech, rows=2, cols=2)
    polys2 = contact2.generate(cell)
    print(f"   Generated {len(polys2)} polygons (4 cuts + 2 enclosures)")

    # Example 3: Via stack from met1 to met3
    print("\n3. Via stack (met1 → met3)")
    via_stack = ViaStack('stack1', 'met1', 'met3', (um(5), um(1)), tech)
    contacts = via_stack.generate(cell)
    print(f"   Generated {len(contacts)} via levels:")
    for c in contacts:
        print(f"     {c.name}: {c.bottom_layer} → {c.top_layer}")

    print(f"\n   Total polygons in cell: {len(cell.polygons)}")

    # Export to GDS
    print("\nExporting to GDS...")
    cell.export_gds("contact_test.gds")

    print("\nContact generator ready!")
    print("Usage:")
    print("  contact = Contact('name', 'bottom_layer', 'top_layer', (x, y), tech)")
    print("  contact.generate(cell)")
