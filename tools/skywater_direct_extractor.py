#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct SkyWater Extractor

Reads GDS directly with gdstk and extracts netlist
Bypasses the Cell class to avoid coordinate issues
"""

import gdstk
from layout_automation.skywater_layer_map import get_layer_name
from .netlist_extractor_improved import GeometricShape
from layout_automation.lvs import Netlist, Device
from typing import List, Dict, Set
from layout_automation.units import to_um


class DirectSkyWaterExtractor:
    """Extract netlist directly from GDS using gdstk"""

    def __init__(self, gds_file, cell_name, technology):
        """
        Initialize extractor

        Args:
            gds_file: Path to GDS file
            cell_name: Name of cell to extract
            technology: Technology object
        """
        self.gds_file = gds_file
        self.cell_name = cell_name
        self.tech = technology
        self.shapes: Dict[str, List[GeometricShape]] = {}
        self.transistors: List[Dict] = []
        self.net_counter = 0

    def extract(self) -> Netlist:
        """
        Extract netlist from GDS

        Returns:
            Netlist with extracted devices
        """
        print(f"\n{'='*70}")
        print(f"EXTRACTING NETLIST FROM SKYWATER CELL")
        print(f"{'='*70}")

        # Read GDS
        library = gdstk.read_gds(self.gds_file)
        gds_cell = [c for c in library.cells if c.name == self.cell_name][0]

        # Step 1: Flatten and extract shapes
        print("\n1. Extracting shapes from GDS...")
        all_polygons = gds_cell.get_polygons(depth=None)  # Flatten hierarchy

        for polygon in all_polygons:
            layer = polygon.layer
            datatype = polygon.datatype
            points = polygon.points

            # Map to layer name
            layer_name = get_layer_name(layer, datatype)

            # Get bounding box (gdstk returns coordinates in microns)
            # Convert to nanometers by multiplying by 1000
            xs = [p[0] * 1000 for p in points]
            ys = [p[1] * 1000 for p in points]
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)

            # Create shape
            shape = GeometricShape(
                name=f"{layer_name}_{len(self.shapes.get(layer_name, []))}",
                layer=layer_name,
                x1=x1, y1=y1, x2=x2, y2=y2
            )

            if layer_name not in self.shapes:
                self.shapes[layer_name] = []
            self.shapes[layer_name].append(shape)

        # Print summary
        for layer, shapes in sorted(self.shapes.items()):
            print(f"   {layer}: {len(shapes)} shapes")

        # Step 2: Extract transistors
        print("\n2. Extracting transistors...")
        self._extract_transistors()

        # Step 3: Build netlist
        print("\n3. Building netlist...")
        netlist = Netlist(f"{self.cell_name}_extracted")

        for trans in self.transistors:
            device = Device(
                name=trans['name'],
                device_type=trans['type'],
                terminals=trans,
                parameters={'W': trans['W'], 'L': trans['L']}
            )
            netlist.add_device(device)

        print(f"\n{'='*70}")
        print(f"EXTRACTION SUMMARY")
        print(f"{'='*70}")
        print(f"Transistors extracted: {len(self.transistors)}")

        # Show devices
        nmos_count = sum(1 for t in self.transistors if t['type'] == 'nmos')
        pmos_count = sum(1 for t in self.transistors if t['type'] == 'pmos')
        print(f"  NMOS: {nmos_count}")
        print(f"  PMOS: {pmos_count}")

        return netlist

    def _extract_transistors(self):
        """Extract transistors from diff-poly overlaps"""
        diff_shapes = self.shapes.get('diff', [])
        poly_shapes = self.shapes.get('poly', [])
        nwell_shapes = self.shapes.get('nwell', [])
        nsdm_shapes = self.shapes.get('nsdm', [])  # N+ implant (for NMOS)
        psdm_shapes = self.shapes.get('psdm', [])  # P+ implant (for PMOS)
        contact_shapes = self.shapes.get('licon1', [])

        print(f"   Available: {len(diff_shapes)} diff, {len(poly_shapes)} poly, "
              f"{len(nwell_shapes)} nwell, {len(contact_shapes)} contacts")
        print(f"   Implants: {len(nsdm_shapes)} nsdm (N+), {len(psdm_shapes)} psdm (P+)")


        transistor_id = 0
        seen_locations = set()  # Deduplicate
        total_overlaps = 0
        filtered_overlaps = 0

        for diff in diff_shapes:
            for poly in poly_shapes:
                if diff.overlaps(poly):
                    total_overlaps += 1
                    # Check if near contact (skip if too close)
                    near_contact, min_dist = self._is_near_contact(diff, poly, contact_shapes, threshold=200)
                    if near_contact:
                        filtered_overlaps += 1
                        continue

                    # Calculate center for deduplication
                    center_x = (diff.x1 + diff.x2 + poly.x1 + poly.x2) / 4
                    center_y = (diff.y1 + diff.y2 + poly.y1 + poly.y2) / 4
                    # Use 200nm grid for deduplication (coarse enough to catch nearby duplicates)
                    location_key = (round(center_x / 200) * 200, round(center_y / 200) * 200)

                    if location_key in seen_locations:
                        continue

                    seen_locations.add(location_key)

                    # Determine type (nmos or pmos) using implant layers
                    # Use center of overlap region to determine which implant dominates
                    overlap_center_y = (max(diff.y1, poly.y1) + min(diff.y2, poly.y2)) / 2

                    # Check if center is in nsdm or psdm
                    device_type = 'nmos'  # Default
                    in_nsdm = any(nsdm.y1 <= overlap_center_y <= nsdm.y2 for nsdm in nsdm_shapes)
                    in_psdm = any(psdm.y1 <= overlap_center_y <= psdm.y2 for psdm in psdm_shapes)

                    # If only in psdm, it's PMOS
                    if in_psdm and not in_nsdm:
                        device_type = 'pmos'
                    # If only in nsdm, it's NMOS
                    elif in_nsdm and not in_psdm:
                        device_type = 'nmos'
                    # If in both (overlap region), use Y coordinate
                    # Based on subcell placement: PMOS at low Y (offset +35nm), NMOS at high Y (offset +400nm)
                    # Threshold around 700nm separates the two regions
                    elif in_nsdm and in_psdm:
                        device_type = 'nmos' if overlap_center_y > 700 else 'pmos'

                    # Calculate W and L
                    poly_is_vertical = poly.height() > poly.width()
                    if poly_is_vertical:
                        gate_length = poly.width()
                        gate_width = diff.height()
                    else:
                        gate_length = poly.height()
                        gate_width = diff.width()

                    # Sanity check
                    if gate_length < 50 or gate_length > 500:
                        continue

                    transistor = {
                        'id': transistor_id,
                        'type': device_type,
                        'name': f'M{transistor_id}',
                        'W': gate_width * 1e-9,  # Convert nm to meters
                        'L': gate_length * 1e-9,  # Convert nm to meters
                        'g': f'net{transistor_id}_g',
                        'd': f'net{transistor_id}_d',
                        's': f'net{transistor_id}_s',
                        'b': 'VGND' if device_type == 'nmos' else 'VPWR'
                    }

                    self.transistors.append(transistor)
                    transistor_id += 1

                    print(f"   Found {device_type.upper()}: "
                          f"W={to_um(gate_width):.3f}μm, L={to_um(gate_length):.3f}μm "
                          f"at ({to_um(center_x):.3f}, {to_um(center_y):.3f})")

        print(f"   Total overlaps: {total_overlaps}, Filtered: {filtered_overlaps}, Extracted: {transistor_id}")

    def _is_near_contact(self, diff, poly, contacts, threshold=200):
        """Check if overlap is near a contact (not a gate)"""
        overlap_x = (max(diff.x1, poly.x1) + min(diff.x2, poly.x2)) / 2
        overlap_y = (max(diff.y1, poly.y1) + min(diff.y2, poly.y2)) / 2

        min_dist = float('inf')
        for contact in contacts:
            contact_x = (contact.x1 + contact.x2) / 2
            contact_y = (contact.y1 + contact.y2) / 2
            dist = ((overlap_x - contact_x)**2 + (overlap_y - contact_y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
            if dist < threshold:
                return True, dist
        return False, min_dist


def extract_skywater_direct(gds_file, cell_name, tech):
    """
    Extract netlist from SkyWater GDS directly

    Args:
        gds_file: Path to GDS file
        cell_name: Cell name
        tech: Technology

    Returns:
        Extracted netlist
    """
    extractor = DirectSkyWaterExtractor(gds_file, cell_name, tech)
    return extractor.extract()


if __name__ == "__main__":
    from technology import Technology

    tech = Technology('sky130')
    netlist = extract_skywater_direct(
        "sky130_inv_replica.gds",
        "sky130_fd_sc_hd__inv_1_replica",
        tech
    )

    print(f"\n✅ Extracted {len(netlist.devices)} devices")
