# FreePDK45 Technology File Parser Update

## Summary

The technology file parser (`layout_automation/tech_file.py`) has been updated to support the FreePDK45.tf file format. The parser now handles multiple Virtuoso technology file formats, including the newer FreePDK45 format.

## Changes Made

### 1. **Layer Definition Parsing** (`_parse_layer_definitions`)
   - Added support for FreePDK45 format: `( layerName purpose )` without quotes
   - Maintains backward compatibility with quoted format: `"layerName" "purpose" number`
   - Automatically detects which format is used

### 2. **GDS Layer Number Extraction** (`_parse_layer_rules`)
   - New method to parse the `layerRules/functions` section
   - Extracts GDS layer numbers from the `maskNumber` field
   - Format: `( layerName "function" maskNumber )`
   - Updates all layer purposes with the correct GDS layer number

### 3. **Layer Color Assignment** (`_parse_display_resources`)
   - Enhanced to support `techDisplays` section (FreePDK45 format)
   - Added `_get_default_layer_color()` method with standard CMOS layer colors:
     - Wells: nwell (lightgreen), pwell (lightcoral)
     - Active: brown
     - Poly: red
     - Metals: blue, red, green, orange, cyan, magenta, purple, yellow, pink, lime
     - Vias/Contacts: black/gray
     - Implants: lightgreen (n), lightcoral (p)
   - Maintains backward compatibility with `drDefineDisplay` section

### 4. **Unicode Encoding Fix**
   - Replaced Unicode checkmarks (✓) with [OK] for Windows compatibility
   - Fixes `UnicodeEncodeError` on Windows systems with cp950 encoding

## Technology File Sections Parsed

The parser now handles the following FreePDK45.tf sections:

1. **layerDefinitions**
   - `techLayerPurposePriorities`: Layer names and purposes
   - `techDisplays`: Display properties and color assignments

2. **layerRules**
   - `functions`: Layer types and GDS layer numbers (maskNumber)

3. **Legacy sections** (backward compatible):
   - `streamLayers`: GDS layer/datatype mappings
   - `drDefineDisplay`: Color definitions

## Usage Example

```python
from layout_automation.tech_file import load_tech_file

# Load FreePDK45 technology file
tech = load_tech_file('FreePDK45.tf')

# Query layer information
metal1 = tech.get_layer('metal1', 'drawing')
print(f"Metal1: GDS {metal1.gds_layer}/{metal1.gds_datatype}, Color: {metal1.color}")

# Reverse lookup by GDS number
layer = tech.get_layer_by_gds(11, 0)
print(f"GDS 11/0 is: {layer.name}")

# Export layer map
tech.export_layer_map('freepdk45_layers.txt')
```

## Test Results

Successfully parsed FreePDK45.tf with:
- **297 layer mappings** extracted
- **GDS layer numbers** correctly assigned:
  - active: 1
  - poly: 9
  - contact: 10
  - metal1: 11
  - via1: 12
  - metal2: 13
  - ... (up to metal10: 29)
- **Colors** assigned to all major layers

## Files Modified

1. `layout_automation/tech_file.py` - Updated parser implementation
2. `test_freepdk45.py` - Test script (new)
3. `examples/load_freepdk45.py` - Usage example (new)

## Backward Compatibility

All changes maintain backward compatibility with existing technology file formats. The parser automatically detects and handles:
- Quoted vs. unquoted layer names
- Different GDS layer number sources (streamLayers vs. layerRules)
- Different color definition formats (drDefineDisplay vs. techDisplays)

## Next Steps

The parser is ready to use with FreePDK45.tf. You can now:
1. Load the technology file in your layout automation tools
2. Query layer information by name or GDS number
3. Use the color assignments for visualization
4. Export layer maps for documentation
