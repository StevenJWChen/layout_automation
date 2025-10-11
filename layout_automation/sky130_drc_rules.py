#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkyWater SKY130 DRC Rules

Design rules from SkyWater SKY130 PDK
Reference: https://skywater-pdk.readthedocs.io/en/main/rules.html
"""

from .drc import DRCRuleSet
from .units import nm


def create_sky130_drc_rules() -> DRCRuleSet:
    """
    Create comprehensive DRC rule set for SkyWater SKY130 process

    Returns:
        DRCRuleSet with SKY130 design rules
    """
    rules = DRCRuleSet("skywater_sky130")

    # =========================================================================
    # DIFFUSION (Active) RULES
    # =========================================================================

    # diff.1: Minimum width
    rules.add_width_rule('diff', nm(150),
                        "diff.1: Minimum diffusion width = 0.15um")

    # diff.2: Minimum spacing
    rules.add_spacing_rule('diff', 'diff', nm(270),
                          "diff.2: Minimum diffusion spacing = 0.27um")

    # diff.3: Minimum area
    rules.add_area_rule('diff', nm(150) * nm(150),
                       "diff.3: Minimum diffusion area = 0.0225 um²")

    # =========================================================================
    # POLY (Polysilicon) RULES
    # =========================================================================

    # poly.1: Minimum width
    rules.add_width_rule('poly', nm(150),
                        "poly.1: Minimum poly width = 0.15um")

    # poly.2: Minimum spacing over diff
    rules.add_spacing_rule('poly', 'poly', nm(210),
                          "poly.2: Minimum poly spacing = 0.21um")

    # poly.3: Minimum gate extension beyond diff
    # (This would be an extension rule - using overlap as approximation)
    rules.add_overlap_rule('poly', 'diff', nm(130),
                          "poly.3: Poly must extend 0.13um beyond diff")

    # =========================================================================
    # CONTACT (licon1) RULES
    # =========================================================================

    # licon.1: Exact contact size
    rules.add_width_rule('licon1', nm(170),
                        "licon.1: Contact size = 0.17um x 0.17um")

    # licon.2: Minimum spacing
    rules.add_spacing_rule('licon1', 'licon1', nm(170),
                          "licon.2: Minimum contact spacing = 0.17um")

    # licon.5: Contact must be enclosed by li1
    rules.add_enclosure_rule('li1', 'licon1', nm(0),
                            "licon.5: li1 must enclose contact")

    # licon.6: Contact must be enclosed by diff or poly
    rules.add_enclosure_rule('diff', 'licon1', nm(40),
                            "licon.6: diff must enclose contact by 0.04um")

    # =========================================================================
    # LOCAL INTERCONNECT (li1) RULES
    # =========================================================================

    # li.1: Minimum width
    rules.add_width_rule('li1', nm(170),
                        "li.1: Minimum li1 width = 0.17um")

    # li.2: Minimum spacing
    rules.add_spacing_rule('li1', 'li1', nm(170),
                          "li.2: Minimum li1 spacing = 0.17um")

    # li.3: Minimum area
    rules.add_area_rule('li1', nm(561),
                       "li.3: Minimum li1 area = 0.0561 um²")

    # =========================================================================
    # METAL CONTACT (mcon) RULES
    # =========================================================================

    # mcon.1: Exact via size
    rules.add_width_rule('mcon', nm(170),
                        "mcon.1: Metal contact size = 0.17um x 0.17um")

    # mcon.2: Minimum spacing
    rules.add_spacing_rule('mcon', 'mcon', nm(190),
                          "mcon.2: Minimum mcon spacing = 0.19um")

    # mcon.4: Contact must be enclosed by li1
    rules.add_enclosure_rule('li1', 'mcon', nm(0),
                            "mcon.4: li1 must enclose mcon")

    # mcon.5: Contact must be enclosed by met1
    rules.add_enclosure_rule('met1', 'mcon', nm(30),
                            "mcon.5: met1 must enclose mcon by 0.03um")

    # =========================================================================
    # METAL1 (met1) RULES
    # =========================================================================

    # met1.1: Minimum width
    rules.add_width_rule('met1', nm(140),
                        "met1.1: Minimum met1 width = 0.14um")

    # met1.2: Minimum spacing
    rules.add_spacing_rule('met1', 'met1', nm(140),
                          "met1.2: Minimum met1 spacing = 0.14um")

    # met1.3: Minimum area
    rules.add_area_rule('met1', nm(830),
                       "met1.3: Minimum met1 area = 0.083 um²")

    # =========================================================================
    # METAL2 (met2) RULES
    # =========================================================================

    # met2.1: Minimum width
    rules.add_width_rule('met2', nm(140),
                        "met2.1: Minimum met2 width = 0.14um")

    # met2.2: Minimum spacing
    rules.add_spacing_rule('met2', 'met2', nm(140),
                          "met2.2: Minimum met2 spacing = 0.14um")

    # met2.3: Minimum area
    rules.add_area_rule('met2', nm(1480),
                       "met2.3: Minimum met2 area = 0.148 um²")

    # =========================================================================
    # WELL RULES
    # =========================================================================

    # nwell.1: Minimum width
    rules.add_width_rule('nwell', nm(840),
                        "nwell.1: Minimum nwell width = 0.84um")

    # nwell.2: Minimum spacing
    rules.add_spacing_rule('nwell', 'nwell', nm(1270),
                          "nwell.2: Minimum nwell spacing = 1.27um")

    # pwell.1: Minimum width (same as nwell)
    rules.add_width_rule('pwell', nm(840),
                        "pwell.1: Minimum pwell width = 0.84um")

    # =========================================================================
    # IMPLANT RULES
    # =========================================================================

    # nsdm.1: Minimum width (N+ source/drain implant)
    rules.add_width_rule('nsdm', nm(380),
                        "nsdm.1: Minimum nsdm width = 0.38um")

    # nsdm.2: Minimum spacing
    rules.add_spacing_rule('nsdm', 'nsdm', nm(380),
                          "nsdm.2: Minimum nsdm spacing = 0.38um")

    # psdm.1: Minimum width (P+ source/drain implant)
    rules.add_width_rule('psdm', nm(380),
                        "psdm.1: Minimum psdm width = 0.38um")

    # psdm.2: Minimum spacing
    rules.add_spacing_rule('psdm', 'psdm', nm(380),
                          "psdm.2: Minimum psdm spacing = 0.38um")

    # =========================================================================
    # CROSS-LAYER RULES
    # =========================================================================

    # diff.4: Minimum spacing between diff and poly (not over diff)
    rules.add_spacing_rule('diff', 'poly', nm(75),
                          "diff.4: Minimum diff to poly spacing = 0.075um")

    # poly.9: Poly must not cross diff unless forming a gate
    # (This would require special topology checking - omitted for now)

    return rules


if __name__ == "__main__":
    print("=" * 70)
    print("SkyWater SKY130 DRC Rules")
    print("=" * 70)

    rules = create_sky130_drc_rules()

    print(f"\nTotal rules defined: {len(rules.rules)}")
    print("\nRules by type:")

    from collections import defaultdict
    rules_by_type = defaultdict(int)
    for rule in rules.rules:
        rules_by_type[rule.rule_type] += 1

    for rule_type, count in sorted(rules_by_type.items()):
        print(f"  {rule_type}: {count}")

    print("\nSample rules:")
    print("-" * 70)
    for i, rule in enumerate(rules.rules[:10], 1):
        print(f"{i}. {rule.name}: {rule.description}")
        print(f"   Value: {rule.value} nm")
        print()

    print("=" * 70)
    print("Use these rules with DRCChecker to verify layouts")
    print("=" * 70)
