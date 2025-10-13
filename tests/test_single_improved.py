#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test single case with improved flow"""

from tests.test_cases import create_inverter_schematic
from layout_automation.layout_from_schematic import LayoutGenerator
from layout_automation.drc_improved import run_improved_drc
from tools.netlist_extractor_improved import extract_improved_netlist
from layout_automation.lvs import LVSChecker
from layout_automation.technology import Technology
from layout_automation.units import to_um

# Initialize
tech = Technology('sky130')
schematic = create_inverter_schematic()

print("="*70)
print("TEST: Inverter with Improved Flow")
print("="*70)

# Step 1: Generate layout
print("\n1. Generating layout...")
generator = LayoutGenerator(schematic, tech)
layout_cell = generator.generate()
layout_cell.export_gds("inverter_improved.gds")
print(f"✅ Layout generated and exported to inverter_improved.gds")

# Step 2: Run improved DRC
print("\n2. Running improved DRC...")
violations, checker = run_improved_drc(layout_cell, tech)
print(f"{'✅ DRC PASSED' if len(violations) == 0 else f'❌ {len(violations)} violations'}")
if len(violations) > 0:
    for i, v in enumerate(violations[:5], 1):
        print(f"   {i}. {v.message}")

# Step 3: Extract with improved extractor
print("\n3. Extracting netlist (improved)...")
extracted = extract_improved_netlist(layout_cell, tech)
print(f"Extracted: {len(extracted.devices)} devices (expected {len(schematic.devices)})")
if len(extracted.devices) == len(schematic.devices):
    print("✅ Device count matches!")
else:
    print(f"❌ Mismatch: {len(extracted.devices)} vs {len(schematic.devices)}")

# Step 4: Run LVS
print("\n4. Running LVS...")
lvs_checker = LVSChecker(schematic, extracted)
lvs_violations = lvs_checker.verify()
if len(lvs_violations) == 0:
    print("✅ LVS PASSED!")
else:
    print(f"❌ LVS failed: {len(lvs_violations)} violations")
    for v in lvs_violations:
        print(f"   • {v.message}")

print("\n" + "="*70)
