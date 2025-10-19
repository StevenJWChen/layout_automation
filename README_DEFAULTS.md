# Project Defaults and Quick Reference

This document contains default settings and quick reference for the layout_automation project.

## User Configuration

### Git Settings
- **Name**: StevenJWChen
- **Email**: jwchenb@gmail.com
- **Remote Type**: SSH
- **Remote URL**: git@github.com:StevenJWChen/layout_automation.git
- **SSH Key**: `~/.ssh/id_ed25519_github`

### Git Commands
```bash
# Already configured globally:
git config --global user.name "StevenJWChen"
git config --global user.email "jwchenb@gmail.com"

# Standard workflow:
git add .
git commit -m "Your commit message"
git push origin main
```

## Technology Files

### Default Files
- **Tech File**: `FreePDK45.tf` (297 layers, GDS mappings)
- **DRF File**: `SantanaDisplay.drf` (36 colors, 333 packets)

### Loading Tech Files
```python
from layout_automation.tech_file import TechFile, set_tech_file

# Standard loading sequence:
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')
set_tech_file(tech)
tech.apply_colors_to_style()
```

## Common Layer Mappings (FreePDK45)

| Layer   | GDS Layer | Color   | Hex Color |
|---------|-----------|---------|-----------|
| active  | 1         | green   | #00cc66   |
| poly    | 9         | red     | #ff0000   |
| contact | 10        | white   | #ffffff   |
| metal1  | 11        | blue    | #0000ff   |
| via1    | 12        | gray    | varies    |
| metal2  | 13        | magenta | #ff00ff   |
| via2    | 14        | gray    | varies    |
| metal3  | 15        | cyan    | #00ffff   |

## Quick Commands

### Run Demo
```bash
python my_demo.py
# Outputs to: demo_outputs/
```

### Load Tech File Example
```bash
python examples/load_freepdk45.py
```

### Test Suite
```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest tests/test_tech_file.py
```

## Project Structure

```
layout_automation/
├── FreePDK45.tf                    # Technology file
├── SantanaDisplay.drf              # Display resource file
├── my_demo.py                      # Main demo script
├── layout_automation/
│   ├── tech_file.py               # Tech file parser
│   ├── cell.py                    # Cell class
│   └── style_config.py            # Style configuration
├── examples/
│   └── load_freepdk45.py          # Tech file usage example
├── demo_outputs/                   # Demo output files
└── docs/                          # Documentation
```

## SSH Configuration

SSH is already configured in `~/.ssh/config`:
```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes
```

Public key fingerprint: `SHA256:b863f37plQEGFgO3zkNhWlNusGdMMjpWp9vmQIyV7g4`

## Environment

- **OS**: Windows (with cp950 encoding)
- **Unicode**: Use [OK]/[DIFF] instead of ✓/✗
- **Python Path**: Auto-configured in scripts

## Documentation Files

Quick reference to documentation:
- `FREEPDK45_PARSER_UPDATE.md` - Tech file parser details
- `DRF_COLOR_PARSER.md` - DRF color parser guide
- `TECH_FILE_PARSER_COMPLETE.md` - Complete parser reference
- `MY_DEMO_REVISION.md` - Demo script documentation

## Default Workflow

### Creating New Layouts
```python
from layout_automation.cell import Cell
from layout_automation.tech_file import TechFile, set_tech_file

# 1. Load technology
tech = TechFile()
tech.parse_virtuoso_tech_file('FreePDK45.tf')
tech.parse_drf_file('SantanaDisplay.drf')
set_tech_file(tech)

# 2. Create layout
cell = Cell('my_design')
# ... add instances and constraints

# 3. Export
cell.export_gds('output.gds', use_tech_file=True)
```

### Git Workflow
```bash
# 1. Make changes
# ... edit files

# 2. Stage and commit
git add .
git commit -m "description of changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. Push
git push origin main
```

## Notes

- All Unicode characters replaced with ASCII equivalents for Windows compatibility
- SSH authentication is preferred over HTTPS
- Tech files should be loaded before creating layouts for proper color rendering
- GDS export requires tech file for correct layer numbers
