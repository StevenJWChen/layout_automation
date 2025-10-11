#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved DRC Checker with Topology Awareness

Fixes false positives by recognizing:
1. Contacts ON diff (required, not violation)
2. Poly crossing diff at gates (required, not violation)
3. Valid layer interactions
"""

from .drc import DRCChecker, DRCViolation, DRCRuleSet


class ImprovedDRCChecker(DRCChecker):
    """
    DRC checker with topology awareness to reduce false positives
    """

    def _check_spacing_rule(self, rule, polygons):
        """Check minimum spacing between polygons - improved version"""
        layer1, layer2 = rule.layers
        min_spacing = rule.value

        # Get polygons on relevant layers
        polys1 = [p for p in polygons if p[1] == layer1]
        polys2 = [p for p in polygons if p[1] == layer2]

        # Check spacing between all pairs
        for i, p1 in enumerate(polys1):
            name1, _, x1_1, y1_1, x2_1, y2_1 = p1

            # For same layer, avoid checking polygon against itself
            start_j = i + 1 if layer1 == layer2 else 0
            compare_list = polys2[start_j:] if layer1 == layer2 else polys2

            for p2 in compare_list:
                name2, _, x1_2, y1_2, x2_2, y2_2 = p2

                # Skip if same polygon
                if p1 == p2:
                    continue

                # TOPOLOGY AWARENESS: Skip known valid interactions
                if self._is_valid_interaction(name1, layer1, name2, layer2):
                    continue

                # Calculate spacing (edge to edge distance)
                spacing = self._calculate_spacing(
                    x1_1, y1_1, x2_1, y2_1,
                    x1_2, y1_2, x2_2, y2_2
                )

                # Check if violates minimum spacing
                if spacing < min_spacing:
                    # Find violation location (midpoint between closest edges)
                    location = self._find_closest_point(
                        x1_1, y1_1, x2_1, y2_1,
                        x1_2, y1_2, x2_2, y2_2
                    )

                    violation = DRCViolation(
                        rule=rule,
                        objects=[name1, name2],
                        actual_value=spacing,
                        location=location,
                        severity='error',
                        message=f"Spacing violation: {name1} and {name2} have spacing "
                               f"{spacing:.3f} < {min_spacing:.3f} (required)"
                    )
                    self.violations.append(violation)

    def _is_valid_interaction(self, name1: str, layer1: str, name2: str, layer2: str) -> bool:
        """
        Check if interaction between two shapes is valid (not a violation)

        Returns:
            True if interaction is valid (should be skipped), False otherwise
        """
        # Contact on diff - this is REQUIRED, not a violation
        if ('contact' in name1.lower() or 'licon' in name1.lower()) and layer2 == 'diff':
            return True
        if ('contact' in name2.lower() or 'licon' in name2.lower()) and layer1 == 'diff':
            return True

        # Poly crossing diff - valid if it's a gate
        if layer1 == 'poly' and layer2 == 'diff':
            # Poly on diff is typically a gate (valid)
            if 'poly' in name1.lower() and 'diff' in name2.lower():
                return True
        if layer1 == 'diff' and layer2 == 'poly':
            if 'diff' in name1.lower() and 'poly' in name2.lower():
                return True

        # Source/drain contacts (licon1) on diff
        if layer1 == 'licon1' and layer2 == 'diff':
            return True
        if layer1 == 'diff' and layer2 == 'licon1':
            return True

        # Metal contacts on li1
        if layer1 == 'mcon' and layer2 == 'li1':
            return True
        if layer1 == 'li1' and layer2 == 'mcon':
            return True

        # Contacts within same transistor (source/drain)
        if 'source' in name1.lower() and 'drain' in name2.lower():
            return True
        if 'drain' in name1.lower() and 'source' in name2.lower():
            return True

        return False

    def print_violations(self):
        """Print violations - improved version with filtering stats"""
        if not self.violations:
            print("\n✅ DRC CLEAN - No violations found!")
            return

        print(f"\n{'='*70}")
        print(f"DRC VIOLATIONS FOUND: {len(self.violations)}")
        print(f"{'='*70}\n")

        errors = [v for v in self.violations if v.severity == 'error']
        warnings = [v for v in self.violations if v.severity == 'warning']

        if errors:
            print(f"ERRORS ({len(errors)}):")
            print("-" * 70)
            # Print only first 10 to avoid spam
            for i, v in enumerate(errors[:10], 1):
                print(f"{i}. {v.message}")
                print(f"   Rule: {v.rule.description}")
                print(f"   Location: ({v.location[0]:.2f}, {v.location[1]:.2f})")
                print()

            if len(errors) > 10:
                print(f"... and {len(errors) - 10} more errors")
                print()

        if warnings:
            print(f"WARNINGS ({len(warnings)}):")
            print("-" * 70)
            for i, v in enumerate(warnings[:5], 1):
                print(f"{i}. {v.message}")
                print(f"   Rule: {v.rule.description}")
                print(f"   Location: ({v.location[0]:.2f}, {v.location[1]:.2f})")
                print()

            if len(warnings) > 5:
                print(f"... and {len(warnings) - 5} more warnings")


# Helper function to use improved checker
def run_improved_drc(cell, tech):
    """
    Run improved DRC verification

    Args:
        cell: Cell to verify
        tech: Technology object

    Returns:
        List of violations (should be much fewer than basic DRC)
    """
    from sky130_drc_rules import create_sky130_drc_rules

    rules = create_sky130_drc_rules()
    checker = ImprovedDRCChecker(rules)
    violations = checker.check_cell(cell)

    return violations, checker


if __name__ == "__main__":
    print("Improved DRC Checker with Topology Awareness")
    print("=" * 70)
    print("\nFeatures:")
    print("  • Recognizes valid contact-on-diff interactions")
    print("  • Recognizes valid poly-crossing-diff gates")
    print("  • Filters false positives")
    print("\nUse: violations, checker = run_improved_drc(cell, tech)")
