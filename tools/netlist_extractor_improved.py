#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Geometric Netlist Extraction

Fixes over-extraction by:
1. Filtering contact regions (not real transistors)
2. Identifying gate regions vs source/drain overlaps
3. Proper transistor counting
"""

from .netlist_extractor import NetlistExtractor, GeometricShape
from layout_automation.lvs import Netlist, Device
from layout_automation.units import to_um


class ImprovedNetlistExtractor(NetlistExtractor):
    """
    Improved extractor that filters false transistor detections
    """

    def _extract_transistors(self):
        """Extract transistors - improved to filter contacts"""
        diff_shapes = self.shapes.get('diff', [])
        poly_shapes = self.shapes.get('poly', [])
        nwell_shapes = self.shapes.get('nwell', [])
        pwell_shapes = self.shapes.get('pwell', [])
        contact_shapes = self.shapes.get('licon1', [])

        transistor_id = 0
        seen_locations = set()  # Track transistor locations to avoid duplicates

        # Find diff-poly overlaps (these are gates)
        for diff in diff_shapes:
            for poly in poly_shapes:
                if diff.overlaps(poly):
                    # Check if this is near a contact (likely not a gate)
                    if self._is_near_contact(diff, poly, contact_shapes):
                        continue  # Skip - this is a contact region, not a gate

                    # Calculate center position for deduplication
                    center_x = (diff.x1 + diff.x2 + poly.x1 + poly.x2) / 4
                    center_y = (diff.y1 + diff.y2 + poly.y1 + poly.y2) / 4
                    location_key = (round(center_x / 100) * 100, round(center_y / 100) * 100)

                    # Skip if we've already found a transistor at this location
                    if location_key in seen_locations:
                        continue

                    seen_locations.add(location_key)

                    # Determine type from well
                    device_type = 'nmos'  # Default
                    for nwell in nwell_shapes:
                        if diff.overlaps(nwell):
                            device_type = 'pmos'
                            break

                    # Calculate gate dimensions
                    # Length = poly width in crossing direction
                    # Width = diff dimension in channel direction

                    # Determine orientation
                    poly_is_vertical = poly.height() > poly.width()

                    if poly_is_vertical:
                        # Vertical poly -> horizontal channel
                        gate_length = poly.width()
                        gate_width = diff.height()
                    else:
                        # Horizontal poly -> vertical channel
                        gate_length = poly.height()
                        gate_width = diff.width()

                    # Sanity check - gate length should be reasonable (0.15um = 150nm typical)
                    if gate_length < 50 or gate_length > 500:
                        continue  # Skip unreasonable dimensions

                    transistor = {
                        'id': transistor_id,
                        'type': device_type,
                        'name': f'M{transistor_id}',
                        'W': gate_width,
                        'L': gate_length,
                        'diff': diff,
                        'poly': poly,
                        'gate_net': None,
                        'source_net': None,
                        'drain_net': None,
                        'bulk_net': 'GND' if device_type == 'nmos' else 'VDD'
                    }

                    self.transistors.append(transistor)
                    transistor_id += 1

                    print(f"   Found {device_type.upper()} transistor: "
                          f"W={to_um(gate_width):.3f}μm, L={to_um(gate_length):.3f}μm "
                          f"at ({to_um(center_x):.2f}, {to_um(center_y):.2f})")

    def _is_near_contact(self, diff: GeometricShape, poly: GeometricShape,
                        contacts: list, threshold: float = 200) -> bool:
        """
        Check if diff-poly overlap is near a contact (likely not a gate)

        Args:
            diff: Diffusion shape
            poly: Poly shape
            contacts: List of contact shapes
            threshold: Distance threshold in nm (default 200nm)

        Returns:
            True if near contact (not a gate), False otherwise
        """
        # Calculate overlap region center
        overlap_x = (max(diff.x1, poly.x1) + min(diff.x2, poly.x2)) / 2
        overlap_y = (max(diff.y1, poly.y1) + min(diff.y2, poly.y2)) / 2

        # Check if any contact is very close
        for contact in contacts:
            contact_x = (contact.x1 + contact.x2) / 2
            contact_y = (contact.y1 + contact.y2) / 2

            dist_x = abs(overlap_x - contact_x)
            dist_y = abs(overlap_y - contact_y)
            dist = (dist_x**2 + dist_y**2)**0.5

            if dist < threshold:
                return True  # Near contact, probably not a gate

        return False


# Helper function
def extract_improved_netlist(cell, tech):
    """
    Extract netlist with improved filtering

    Args:
        cell: Cell to extract from
        tech: Technology object

    Returns:
        Extracted netlist (should have correct device count)
    """
    extractor = ImprovedNetlistExtractor(cell, tech)
    netlist = extractor.extract()
    return netlist


if __name__ == "__main__":
    print("Improved Netlist Extractor")
    print("=" * 70)
    print("\nImprovements:")
    print("  • Filters contact regions (not transistors)")
    print("  • Deduplicates transistor locations")
    print("  • Better gate dimension calculation")
    print("\nUse: netlist = extract_improved_netlist(cell, tech)")
